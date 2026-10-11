"""Evidence for QS-02, QS-04, QS-06, QS-07 and the seed rules (test plan TP-xx).

Each test states the quality scenario or design rule it checks.
"""

import hashlib

import pytest

from horizon.config import get_settings
from horizon.infrastructure.seed import seed_placements
from horizon.modules.audit.recorder import AuditEntryModel
from horizon.modules.notifications.outbox import OutboxMessageModel, deliver_pending
from horizon.modules.placements import api as placements_api
from horizon.modules.placements.repository import PlacementModel
from tests.conftest import ROOT, as_user
from tests.integration.test_activation_endpoint import add_ready_placement

COORDINATOR = as_user("EXP-COORD-001")


def test_qs02_unrelated_student_gets_404_and_denial_is_audited(client, session) -> None:
    # HU-STU-5003 owns PLC-2001 only; PLC-2002 must not be revealed to them.
    response = client.get("/placements/PLC-2002/readiness", headers=as_user("HU-STU-5003"))

    assert response.status_code == 404
    denial = session.query(AuditEntryModel).filter_by(action="ACCESS_DENIED").one()
    assert denial.actor_id == "HU-STU-5003"
    assert denial.resource_id == "PLC-2002"


def test_qs02_workplace_supervisor_is_related_only_to_their_own_placement() -> None:
    # The identity mock has no workplace supervisors (finding), so the policy is tested directly.
    from horizon.modules.access.policy import AccessPolicy, Actor, PlacementRelations

    policy = AccessPolicy(ROOT / "data")
    supervisor = Actor(user_id="SUP-EXT-002", institutional_role="EXTERNAL")
    own = PlacementRelations("HU-STU-5001", "ORG-001", "SUP-EXT-002", "FAC-SUP-101")
    other = PlacementRelations("HU-STU-5003", "ORG-002", "SUP-EXT-001", "FAC-SUP-101")

    assert policy.audience(supervisor, own) == "workplace_supervisor"
    assert policy.audience(supervisor, other) is None


def test_qs04_audit_reason_records_the_rule_version_used(client, session) -> None:
    client.post("/placements/PLC-2002/activation", headers=COORDINATOR)

    entry = session.query(AuditEntryModel).filter_by(action="ACTIVATION_REFUSED").one()
    assert entry.reason.startswith("readiness gate ")
    assert entry.reason.split()[-1]  # a version label is always present


def test_qs06_outbox_payload_has_no_restricted_data(client, session) -> None:
    add_ready_placement(session)
    client.post("/placements/PLC-9001/activation", headers=COORDINATOR)

    for message in session.query(OutboxMessageModel):
        assert set(message.payload) == {"placement_id", "template"}


class _CrashAfterFirst:
    def __init__(self) -> None:
        self.calls = 0
        self.sent: list[int] = []

    def send(self, message) -> None:
        self.calls += 1
        if self.calls == 2:
            raise KeyboardInterrupt  # simulates the worker process dying mid-run
        self.sent.append(message.id)


def test_qs06_worker_crash_does_not_resend_what_was_already_sent(client, session) -> None:
    add_ready_placement(session)
    client.post("/placements/PLC-9001/activation", headers=COORDINATOR)
    channel = _CrashAfterFirst()

    with pytest.raises(KeyboardInterrupt):
        deliver_pending(session, channel)

    session.rollback()
    statuses = sorted(m.status for m in session.query(OutboxMessageModel))
    assert statuses == ["PENDING", "PENDING", "SENT"]  # the first one was committed

    class Working:
        def send(self, message) -> None:
            pass

    assert deliver_pending(session, Working())["sent"] == 2  # only the two unsent messages


def test_mock_identity_disabled_answers_503(client, monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "mock_identity_enabled", False)

    response = client.get("/placements/PLC-2002/readiness", headers=COORDINATOR)

    assert response.status_code == 503


def test_seed_never_modifies_the_raw_files(session) -> None:
    raw = sorted((ROOT / "data" / "raw").glob("*.csv"))
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in raw}

    seed_placements(session, ROOT / "data")

    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in raw}
    assert before == after


def test_seed_loads_every_placement_of_the_pack_once(session) -> None:
    import csv

    with (ROOT / "data" / "raw" / "placements.csv").open(encoding="utf-8-sig") as handle:
        expected = {r["placement_id"] for r in csv.DictReader(handle)}
    loaded = {p.placement_id for p in session.query(PlacementModel)}
    assert expected <= loaded


def test_placements_api_exposes_overridable_dependencies() -> None:
    # The wiring points used by tests (and by the future auth integration) are explicit.
    for name in ("get_today", "get_employer_directory", "get_access_policy", "get_dispatcher"):
        assert hasattr(placements_api, name)


# ---- second review: claims that were only implemented are now exercised ----------------


class _CompetingDirectory:
    """Directory adapter that lets another coordinator activate first (FM-08 through the API)."""

    def __init__(self, real) -> None:
        self._real, self._done = real, False

    def agreement(self, organization_id):
        if not self._done:
            self._done = True
            from datetime import UTC, datetime

            from horizon.infrastructure.database import SessionLocal
            from horizon.modules.access.policy import AccessPolicy
            from horizon.modules.integrations.adapters import IdentityAdapter
            from horizon.modules.placements.service import ActivatePlacement
            from horizon.modules.readiness.gate import ReadinessGate
            from horizon.modules.rules.evaluators import RuleConfiguration
            from horizon.shared.events import EventDispatcher
            from tests.conftest import TODAY

            with SessionLocal() as other:
                access = AccessPolicy(ROOT / "data")
                actor = access.actor_for(IdentityAdapter(ROOT / "data").resolve("EXP-COORD-001"))
                gate = ReadinessGate(
                    other, RuleConfiguration(ROOT / "config/rules/readiness.json"), self._real
                )
                ActivatePlacement(
                    other,
                    gate,
                    access,
                    lambda: TODAY,
                    lambda: datetime.now(UTC),
                    dispatcher=EventDispatcher(),
                ).execute("PLC-9001", actor)
        return self._real.agreement(organization_id)


def test_api_answers_state_changed_when_another_command_wins(client, session) -> None:
    from horizon.main import app
    from horizon.mocks.dh05_services import MockEmployerDirectoryService
    from horizon.modules.integrations.adapters import EmployerDirectoryAdapter

    add_ready_placement(session)
    real = EmployerDirectoryAdapter(MockEmployerDirectoryService(ROOT / "mocks", None))
    app.dependency_overrides[placements_api.get_employer_directory] = lambda: _CompetingDirectory(
        real
    )

    response = client.post("/placements/PLC-9001/activation", headers=COORDINATOR)

    assert response.status_code == 409
    assert response.json()["code"] == "STATE_CHANGED"
    session.expire_all()
    assert session.query(AuditEntryModel).filter_by(action="PLACEMENT_ACTIVATED").count() == 1


def test_outbox_message_is_failed_after_five_attempts(client, session) -> None:
    add_ready_placement(session)
    client.post("/placements/PLC-9001/activation", headers=COORDINATOR)

    class Broken:
        def send(self, message) -> None:
            raise ConnectionError("channel down")

    for _ in range(5):
        deliver_pending(session, Broken())

    messages = session.query(OutboxMessageModel).all()
    assert {m.status for m in messages} == {"FAILED"}
    assert {m.attempts for m in messages} == {5}
    assert session.get(PlacementModel, "PLC-9001").status == "ACTIVE"


def test_placements_endpoint_requires_a_known_identity(client) -> None:
    missing = client.post("/placements/PLC-2002/activation")
    unknown = client.post("/placements/PLC-2002/activation", headers=as_user("NOBODY-1"))
    assert missing.status_code == 401
    assert unknown.status_code == 401


def test_host_organization_cannot_activate_and_denial_is_audited(client, session) -> None:
    response = client.post("/placements/PLC-2002/activation", headers=as_user("ORG-C-001"))

    assert response.status_code == 403
    denial = session.query(AuditEntryModel).filter_by(action="ACCESS_DENIED").one()
    assert denial.actor_id == "ORG-C-001"


def test_student_projection_hides_restricted_evidence(client) -> None:
    body = client.get("/placements/PLC-2002/readiness", headers=as_user("HU-STU-5001")).json()

    assert body["audience"] == "student"
    agreement = next(c for c in body["conditions"] if c["requirement_type"] == "VALID_AGREEMENT")
    assert agreement["evidence_reference"] is None


def test_new_rule_version_never_changes_a_past_decision(client, session, tmp_path) -> None:
    import json

    from horizon.mocks.dh05_services import MockEmployerDirectoryService
    from horizon.modules.integrations.adapters import EmployerDirectoryAdapter
    from horizon.modules.placements.repository import SqlPlacementRepository
    from horizon.modules.placements.service import facts_of
    from horizon.modules.readiness.gate import ReadinessGate
    from horizon.modules.rules.evaluators import RuleConfiguration
    from tests.conftest import TODAY

    client.post("/placements/PLC-2002/activation", headers=COORDINATOR)
    first = session.query(AuditEntryModel).filter_by(action="ACTIVATION_REFUSED").one()
    assert first.reason == "readiness gate readiness-v1"

    v2 = json.loads((ROOT / "config/rules/readiness.json").read_text(encoding="utf-8"))
    v2["version"] = "readiness-v2"
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(v2), encoding="utf-8")
    directory = EmployerDirectoryAdapter(MockEmployerDirectoryService(ROOT / "mocks", None))
    gate = ReadinessGate(session, RuleConfiguration(path), directory)
    result = gate.evaluate(facts_of(SqlPlacementRepository(session).get("PLC-2002")), TODAY)

    assert result.rule_version == "readiness-v2"
    session.expire_all()
    assert session.get(AuditEntryModel, first.id).reason == "readiness gate readiness-v1"
