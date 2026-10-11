"""M-03 Placements: the placement aggregate and its lifecycle (ADR-003).

The transition table is the only place that says which status can follow which.
ACTIVE can only be reached through `activate`, and only with a passed gate result.
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class PlacementStatus(StrEnum):
    PENDING_ACTIVATION = "PENDING_ACTIVATION"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETION_PENDING = "COMPLETION_PENDING"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


S = PlacementStatus
TRANSITIONS: dict[str, dict[PlacementStatus, PlacementStatus]] = {
    "activate": {S.PENDING_ACTIVATION: S.ACTIVE},
    "cancel": {S.PENDING_ACTIVATION: S.CANCELLED},
    "hold": {S.ACTIVE: S.ON_HOLD},
    "resume": {S.ON_HOLD: S.ACTIVE},
    "request_completion": {S.ACTIVE: S.COMPLETION_PENDING},
    "complete": {S.COMPLETION_PENDING: S.COMPLETED},
    "close": {S.COMPLETED: S.CLOSED},
    "close_interrupted": {S.ACTIVE: S.CLOSED, S.ON_HOLD: S.CLOSED, S.COMPLETION_PENDING: S.CLOSED},
}


class IllegalTransition(Exception):
    pass


class StaleState(Exception):
    """The placement changed between the moment it was read and the moment it was written."""


class ActivationBlocked(Exception):
    def __init__(self, blocking: list) -> None:
        super().__init__("Activation refused by the readiness gate")
        self.blocking = blocking
        self.correlation_id: str | None = None


@dataclass
class Placement:
    placement_id: str
    student_id: str
    organization_id: str
    placement_type: str
    program_code: str | None
    status: PlacementStatus
    workplace_supervisor_id: str | None = None
    faculty_supervisor_id: str | None = None
    activated_at: datetime | None = None
    actual_start_date: date | None = None

    def _move(self, command: str) -> PlacementStatus:
        allowed = TRANSITIONS[command]
        if self.status not in allowed:
            raise IllegalTransition(f"'{command}' is not allowed from {self.status}")
        self.status = allowed[self.status]
        return self.status

    def activate(self, gate_passed: bool, blocking: list, now: datetime) -> None:
        if self.status != PlacementStatus.PENDING_ACTIVATION:
            raise IllegalTransition(f"'activate' is not allowed from {self.status}")
        if not gate_passed:
            raise ActivationBlocked(blocking)
        self._move("activate")
        self.activated_at = now

    def register_start(self, start: date) -> None:
        if self.status != PlacementStatus.ACTIVE:
            raise IllegalTransition(
                "The real start date can only be registered on an active placement"
            )
        self.actual_start_date = start

    def apply(self, command: str) -> PlacementStatus:
        """Transitions without a gate (hold, resume, cancel...).

        Gated transitions (activate, complete) have their own method.
        """
        if command in ("activate", "complete"):
            raise IllegalTransition(f"'{command}' needs its gate")
        return self._move(command)
