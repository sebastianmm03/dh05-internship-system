"""First vertical slice: the activation gate (US-014, US-016; DH05-SC-01, DH05-SC-02; QS-08)."""

from horizon.main import app
from horizon.mocks.dh05_services import MockEmployerDirectoryService
from horizon.modules.audit.recorder import AuditEntryModel
from horizon.modules.integrations.adapters import EmployerDirectoryAdapter
from horizon.modules.notifications.outbox import OutboxMessageModel
from horizon.modules.placements import api as placements_api
from horizon.modules.placements.repository import PlacementModel
from horizon.modules.readiness.gate import ReadinessConditionModel
from tests.conftest import ROOT, as_user

COORDINATOR = as_user("EXP-COORD-001")


def blocking_ids(response) -> set:
    return {b["check_id"] for b in response.json()["blocking"] if b["check_id"]}


def add_ready_placement(session, placement_id="PLC-9001") -> None:
    """Synthetic test placement (not in the data pack) with every condition complete."""
    session.add(
        PlacementModel(
            placement_id=placement_id,
            student_id="HU-STU-5002",
            organization_id="ORG-001",
            placement_type="ACADEMIC_INTERNSHIP",
            program_code="BSC-CS",
            status="PENDING_ACTIVATION",
            workplace_supervisor_id="SUP-EXT-002",
            faculty_supervisor_id="FAC-SUP-101",
        )
    )
    for i, requirement in enumerate(["ACADEMIC_APPROVAL", "WORK_PLAN", "VALID_AGREEMENT"], 1):
        session.add(
            ReadinessConditionModel(
                check_id=f"TEST-{i}",
                placement_id=placement_id,
                requirement_type=requirement,
                required=True,
                status="COMPLETE",
            )
        )
    session.commit()


def test_sc01_selected_but_not_approved_cannot_be_activated(client, session) -> None:
    response = client.post("/placements/PLC-2002/activation", headers=COORDINATOR)

    assert response.status_code == 409
    assert {"READY-004", "READY-006"} <= blocking_ids(response)
    assert session.get(PlacementModel, "PLC-2002").status == "PENDING_ACTIVATION"
    audit = session.query(AuditEntryModel).filter_by(resource_id="PLC-2002").one()
    assert audit.action == "ACTIVATION_REFUSED"


def test_sc02_expired_agreement_and_missing_insurance_block(client, session) -> None:
    response = client.post("/placements/PLC-2003/activation", headers=COORDINATOR)

    assert response.status_code == 409
    blocking = {(b["requirement"], b["check_id"], b["reason"]) for b in response.json()["blocking"]}
    assert blocking == {
        ("ACADEMIC_APPROVAL", None, "required condition is not registered"),
        ("WORK_PLAN", None, "required condition is not registered"),
        ("VALID_AGREEMENT", "READY-007", "status is EXPIRED"),
        ("INSURANCE_REFERENCE", "READY-008", "status is MISSING"),
        ("VALID_AGREEMENT", None, "directory agreement EXPIRED, valid until 2026-07-31"),
    }
    assert session.query(OutboxMessageModel).count() == 0


def test_ready_placement_is_activated_audited_and_notified(client, session) -> None:
    add_ready_placement(session)

    response = client.post("/placements/PLC-9001/activation", headers=COORDINATOR)

    assert response.status_code == 200
    assert response.json()["status"] == "ACTIVE"
    session.expire_all()
    assert session.get(PlacementModel, "PLC-9001").activated_at is not None
    audit = session.query(AuditEntryModel).filter_by(resource_id="PLC-9001").one()
    assert audit.previous_value == {"status": "PENDING_ACTIVATION"}
    assert audit.new_value["status"] == "ACTIVE"
    assert session.query(OutboxMessageModel).count() == 3  # student + both supervisors


def test_directory_down_means_activation_refused(client, session) -> None:
    add_ready_placement(session)
    app.dependency_overrides[placements_api.get_employer_directory] = lambda: (
        EmployerDirectoryAdapter(
            MockEmployerDirectoryService(ROOT / "mocks", simulate_failure="EMP-503")
        )
    )

    response = client.post("/placements/PLC-9001/activation", headers=COORDINATOR)

    assert response.status_code == 409
    assert "could not be verified" in response.json()["blocking"][0]["reason"]
    session.expire_all()
    assert session.get(PlacementModel, "PLC-9001").status == "PENDING_ACTIVATION"


def test_student_cannot_activate_and_denial_is_audited(client, session) -> None:
    response = client.post("/placements/PLC-2002/activation", headers=as_user("HU-STU-5001"))

    assert response.status_code == 403
    denial = session.query(AuditEntryModel).filter_by(action="ACCESS_DENIED").one()
    assert denial.actor_id == "HU-STU-5001"


def test_unrelated_user_gets_not_found(client) -> None:
    # HU-STU-5003 has no relationship with PLC-2002: the placement is not revealed (QS-02).
    response = client.get("/placements/PLC-2002/readiness", headers=as_user("HU-STU-5003"))
    assert response.status_code == 404


def test_host_organization_sees_readiness_without_restricted_evidence(client) -> None:
    response = client.get("/placements/PLC-2002/readiness", headers=as_user("ORG-C-001"))

    assert response.status_code == 200
    body = response.json()
    assert body["audience"] == "host_organization"
    agreement = next(c for c in body["conditions"] if c["requirement_type"] == "VALID_AGREEMENT")
    assert agreement["evidence_reference"] is None  # RESTRICTED document (QS-01)
    office = client.get("/placements/PLC-2002/readiness", headers=COORDINATOR).json()
    agreement_office = next(
        c for c in office["conditions"] if c["requirement_type"] == "VALID_AGREEMENT"
    )
    assert agreement_office["evidence_reference"] == "AGR-ORG001-2026"


def test_other_organization_cannot_see_the_placement(client) -> None:
    response = client.get("/placements/PLC-2003/readiness", headers=as_user("ORG-C-001"))
    assert response.status_code == 404
