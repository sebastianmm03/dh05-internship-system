"""QS-09 (concurrent activation), QS-04 (history written with the change) and ADR-010.

These tests attack the design, not the happy path: two commands that read the same
status, a failure in the middle of the transaction, and a command that is repeated.
"""

from datetime import UTC, datetime

import pytest

from horizon.infrastructure.database import SessionLocal
from horizon.mocks.dh05_services import MockEmployerDirectoryService
from horizon.modules.access.policy import AccessPolicy
from horizon.modules.audit.recorder import AuditEntryModel
from horizon.modules.integrations.adapters import EmployerDirectoryAdapter
from horizon.modules.notifications.outbox import OutboxMessageModel, on_placement_activated
from horizon.modules.placements.domain import StaleState
from horizon.modules.placements.repository import PlacementModel
from horizon.modules.placements.service import ActivatePlacement
from horizon.modules.readiness.gate import ReadinessGate
from horizon.modules.rules.evaluators import RuleConfiguration
from horizon.shared.events import EventDispatcher
from tests.conftest import ROOT, TODAY, as_user
from tests.integration.test_activation_endpoint import add_ready_placement

COORDINATOR = as_user("EXP-COORD-001")


def _actor():
    from horizon.modules.integrations.adapters import IdentityAdapter

    access = AccessPolicy(ROOT / "data")
    return access, access.actor_for(IdentityAdapter(ROOT / "data").resolve("EXP-COORD-001"))


def _use_case(session, gate=None, dispatcher=None) -> tuple[ActivatePlacement, object]:
    access, actor = _actor()
    directory = EmployerDirectoryAdapter(MockEmployerDirectoryService(ROOT / "mocks", None))
    real_gate = ReadinessGate(
        session, RuleConfiguration(ROOT / "config" / "rules" / "readiness.json"), directory
    )
    if dispatcher is None:
        dispatcher = EventDispatcher()
        dispatcher.subscribe("PlacementActivated", on_placement_activated)
    use_case = ActivatePlacement(
        session,
        gate or real_gate,
        access,
        lambda: TODAY,
        lambda: datetime.now(UTC),
        dispatcher=dispatcher,
    )
    return use_case, actor


class _GateWithCompetitor:
    """Lets a second command run to completion between our read and our write."""

    def __init__(self, real_gate, competitor) -> None:
        self._real, self._competitor = real_gate, competitor

    def evaluate(self, facts, today):
        result = self._real.evaluate(facts, today)
        self._competitor()
        return result

    def checklist(self, placement_id):
        return self._real.checklist(placement_id)


def test_two_concurrent_activations_only_one_commits(session) -> None:
    add_ready_placement(session)

    def competing_command() -> None:
        with SessionLocal() as other:
            other_case, actor = _use_case(other)
            other_case.execute("PLC-9001", actor)

    directory = EmployerDirectoryAdapter(MockEmployerDirectoryService(ROOT / "mocks", None))
    real_gate = ReadinessGate(
        session, RuleConfiguration(ROOT / "config" / "rules" / "readiness.json"), directory
    )
    loser, actor = _use_case(session, gate=_GateWithCompetitor(real_gate, competing_command))

    with pytest.raises(StaleState):
        loser.execute("PLC-9001", actor)

    with SessionLocal() as check:
        assert check.get(PlacementModel, "PLC-9001").status == "ACTIVE"
        activated = check.query(AuditEntryModel).filter_by(action="PLACEMENT_ACTIVATED").count()
        assert activated == 1  # the losing command left no success record
        assert check.query(OutboxMessageModel).count() == 3  # one set of notifications only


def test_failure_in_the_middle_rolls_everything_back(session) -> None:
    add_ready_placement(session)
    dispatcher = EventDispatcher()

    def broken_handler(event, db) -> None:
        on_placement_activated(event, db)  # writes the outbox rows ...
        raise RuntimeError("simulated failure before commit")  # ... then the command fails

    dispatcher.subscribe("PlacementActivated", broken_handler)
    use_case, actor = _use_case(session, dispatcher=dispatcher)

    with pytest.raises(RuntimeError):
        use_case.execute("PLC-9001", actor)

    with SessionLocal() as check:
        assert check.get(PlacementModel, "PLC-9001").status == "PENDING_ACTIVATION"
        assert check.query(AuditEntryModel).filter_by(action="PLACEMENT_ACTIVATED").count() == 0
        assert check.query(OutboxMessageModel).count() == 0


def test_repeating_the_command_adds_no_second_set_of_side_effects(client, session) -> None:
    add_ready_placement(session)

    first = client.post("/placements/PLC-9001/activation", headers=COORDINATOR)
    second = client.post("/placements/PLC-9001/activation", headers=COORDINATOR)

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["code"] == "ILLEGAL_TRANSITION"
    session.expire_all()
    assert session.query(AuditEntryModel).filter_by(action="PLACEMENT_ACTIVATED").count() == 1
    assert session.query(OutboxMessageModel).count() == 3


def test_one_correlation_id_links_audit_entry_and_notifications(client, session) -> None:
    add_ready_placement(session)

    response = client.post("/placements/PLC-9001/activation", headers=COORDINATOR)

    correlation_id = response.json()["correlation_id"]
    session.expire_all()
    audit = session.query(AuditEntryModel).filter_by(action="PLACEMENT_ACTIVATED").one()
    assert audit.correlation_id == correlation_id
    messages = session.query(OutboxMessageModel).all()
    assert len(messages) == 3
    assert {m.correlation_id for m in messages} == {correlation_id}


def test_refusal_and_denial_carry_machine_readable_codes(client, session) -> None:
    refused = client.post("/placements/PLC-2002/activation", headers=COORDINATOR)
    assert refused.json()["code"] == "ACTIVATION_BLOCKED"
    entry = session.query(AuditEntryModel).filter_by(action="ACTIVATION_REFUSED").one()
    assert entry.correlation_id == refused.json()["correlation_id"]

    denied = client.post("/placements/PLC-2002/activation", headers=as_user("HU-STU-5001"))
    assert denied.status_code == 403
    denial = session.query(AuditEntryModel).filter_by(action="ACCESS_DENIED").one()
    assert denial.correlation_id is not None
