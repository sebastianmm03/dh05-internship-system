"""Application services of M-03 Placements.

ActivatePlacement is the first vertical slice (US-014, US-016; DH05-SC-01, DH05-SC-02).
Everything happens in one transaction: access check, gate, transition, audit, event.
"""

import uuid
from collections.abc import Callable
from dataclasses import asdict
from datetime import date, datetime

from sqlalchemy.orm import Session

from horizon.modules.access.policy import AccessDenied, AccessPolicy, Actor, PlacementRelations
from horizon.modules.audit.recorder import AuditRecorder
from horizon.modules.placements.domain import ActivationBlocked, Placement, PlacementStatus
from horizon.modules.placements.repository import SqlPlacementRepository
from horizon.modules.readiness.gate import PlacementFacts, ReadinessGate
from horizon.shared.events import DomainEvent, EventDispatcher


class PlacementNotFound(Exception):
    pass


def facts_of(placement: Placement) -> PlacementFacts:
    return PlacementFacts(
        placement_id=placement.placement_id,
        organization_id=placement.organization_id,
        placement_type=placement.placement_type,
        program_code=placement.program_code,
        workplace_supervisor_id=placement.workplace_supervisor_id,
        faculty_supervisor_id=placement.faculty_supervisor_id,
    )


def relations_of(placement: Placement) -> PlacementRelations:
    return PlacementRelations(
        student_id=placement.student_id,
        organization_id=placement.organization_id,
        workplace_supervisor_id=placement.workplace_supervisor_id,
        faculty_supervisor_id=placement.faculty_supervisor_id,
    )


def new_correlation_id() -> str:
    """One id per command; it links the audit entries, the event and the outbox messages."""
    return uuid.uuid4().hex


class _PlacementUseCase:
    def __init__(
        self,
        session: Session,
        gate: ReadinessGate,
        access: AccessPolicy,
        today: Callable[[], date],
        now: Callable[[], datetime],
    ) -> None:
        self._session = session
        self._gate = gate
        self._access = access
        self._today = today
        self._now = now
        self._placements = SqlPlacementRepository(session)
        self._audit = AuditRecorder(session)

    def _load_and_check(
        self, placement_id: str, actor: Actor, action: str, correlation_id: str
    ) -> tuple[Placement, str]:
        placement = self._placements.get(placement_id)
        if placement is None:
            raise PlacementNotFound(placement_id)
        try:
            audience = self._access.check(actor, action, relations_of(placement))
        except AccessDenied:
            self._audit.record(
                actor_id=actor.user_id,
                action="ACCESS_DENIED",
                resource_type="placement",
                resource_id=placement_id,
                reason=action,
                correlation_id=correlation_id,
            )
            self._session.commit()
            raise
        return placement, audience


class ActivatePlacement(_PlacementUseCase):
    def __init__(self, *args, dispatcher: EventDispatcher, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._dispatcher = dispatcher

    def execute(self, placement_id: str, actor: Actor) -> dict:
        correlation_id = new_correlation_id()
        placement, _ = self._load_and_check(
            placement_id, actor, "placement.activate", correlation_id
        )
        previous = placement.status.value
        result = self._gate.evaluate(facts_of(placement), self._today())
        try:
            placement.activate(result.passed, result.blocking, self._now())
        except ActivationBlocked as blocked:
            self._audit.record(
                actor_id=actor.user_id,
                action="ACTIVATION_REFUSED",
                resource_type="placement",
                resource_id=placement_id,
                previous_value={"status": previous},
                new_value={"status": previous, "blocking": [asdict(b) for b in result.blocking]},
                reason=f"readiness gate {result.rule_version}",
                correlation_id=correlation_id,
            )
            self._session.commit()
            blocked.correlation_id = correlation_id
            raise
        # Everything below is one transaction: the state change, its audit entry and the outbox
        # messages are committed together or not at all (ADR-002, ADR-006, ADR-008).
        try:
            self._placements.save(placement, PlacementStatus(previous))
            self._audit.record(
                actor_id=actor.user_id,
                action="PLACEMENT_ACTIVATED",
                resource_type="placement",
                resource_id=placement_id,
                previous_value={"status": previous},
                new_value={
                    "status": placement.status.value,
                    "activated_at": placement.activated_at.isoformat(),
                },
                reason=f"readiness gate {result.rule_version} passed",
                correlation_id=correlation_id,
            )
            self._dispatcher.publish(
                DomainEvent(
                    "PlacementActivated",
                    {
                        "placement_id": placement.placement_id,
                        "student_id": placement.student_id,
                        "workplace_supervisor_id": placement.workplace_supervisor_id,
                        "faculty_supervisor_id": placement.faculty_supervisor_id,
                        "correlation_id": correlation_id,
                    },
                ),
                self._session,
            )
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return {
            "placement_id": placement_id,
            "status": placement.status.value,
            "rule_version": result.rule_version,
            "correlation_id": correlation_id,
        }


class ReadinessView(_PlacementUseCase):
    def execute(self, placement_id: str, actor: Actor) -> dict:
        placement, audience = self._load_and_check(
            placement_id, actor, "placement.readiness.read", new_correlation_id()
        )
        result = self._gate.evaluate(facts_of(placement), self._today())
        conditions = [
            self._access.project_condition(
                audience,
                {
                    "check_id": row.check_id,
                    "requirement_type": row.requirement_type,
                    "status": row.status,
                    "evidence_reference": row.evidence_reference,
                },
            )
            for row in self._gate.checklist(placement_id)
        ]
        return {
            "placement_id": placement_id,
            "status": placement.status.value,
            "audience": audience,
            "rule_version": result.rule_version,
            "ready": result.passed,
            "blocking": [asdict(b) for b in result.blocking],
            "conditions": conditions,
        }
