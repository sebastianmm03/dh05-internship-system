"""M-07 Access: the only place where access is decided (ADR-005).

Access = role + relationship with the resource. Default is deny.
Relationship data comes from the DH-05 reference files (staff and organization
contacts) and from the placement itself (student, supervisors, organization).
"""

import csv
from dataclasses import dataclass
from pathlib import Path

from horizon.shared.ports import Identity

OFFICE_ROLES = {
    "EXPERIENTIAL_LEARNING_COORDINATOR",
    "PROGRAM_DIRECTOR",
    "AGREEMENTS_REPRESENTATIVE",
}

# Readiness requirements whose evidence is a RESTRICTED document type (document_types.csv).
RESTRICTED_REQUIREMENTS = {"VALID_AGREEMENT", "INSURANCE_REFERENCE", "CONFIDENTIALITY_FORM"}


class AccessDenied(Exception):
    def __init__(self, reveal: bool) -> None:
        super().__init__("Access denied")
        # reveal=False means the user has no relationship: answer as if the resource did not exist.
        self.reveal = reveal


@dataclass(frozen=True)
class PlacementRelations:
    """The relationships of a placement that access decisions need (M-03 builds it)."""

    student_id: str
    organization_id: str
    workplace_supervisor_id: str | None
    faculty_supervisor_id: str | None


@dataclass(frozen=True)
class Actor:
    user_id: str
    institutional_role: str
    staff_role: str | None = None
    organization_id: str | None = None


class AccessPolicy:
    def __init__(self, data_root: Path) -> None:
        self._staff_roles = self._read(
            data_root / "reference" / "staff.csv", "staff_id", "staff_role"
        )
        self._contact_orgs = self._read(
            data_root / "reference" / "organization_contacts.csv", "contact_id", "organization_id"
        )

    @staticmethod
    def _read(path: Path, key: str, value: str) -> dict[str, str]:
        with path.open(encoding="utf-8") as handle:
            return {
                row[key]: row[value]
                for row in csv.DictReader(handle)
                if row.get("active") != "false"
            }

    def actor_for(self, identity: Identity) -> Actor:
        return Actor(
            user_id=identity.user_id,
            institutional_role=identity.institutional_role,
            staff_role=self._staff_roles.get(identity.user_id),
            organization_id=self._contact_orgs.get(identity.user_id),
        )

    # -- relationship -------------------------------------------------------
    def audience(self, actor: Actor, placement: PlacementRelations) -> str | None:
        """Which audience the actor belongs to for this placement, or None if unrelated."""
        if actor.staff_role in OFFICE_ROLES:
            return "office"
        if actor.user_id == placement.faculty_supervisor_id:
            return "faculty"
        if actor.user_id == placement.workplace_supervisor_id:
            return "workplace_supervisor"
        if actor.user_id == placement.student_id:
            return "student"
        if actor.organization_id and actor.organization_id == placement.organization_id:
            return "host_organization"
        return None

    # -- decisions ----------------------------------------------------------
    def check(self, actor: Actor, action: str, placement: PlacementRelations) -> str:
        audience = self.audience(actor, placement)
        if audience is None:
            raise AccessDenied(reveal=False)
        allowed = {
            "placement.readiness.read": {
                "office",
                "faculty",
                "workplace_supervisor",
                "student",
                "host_organization",
            },
            "placement.activate": {"office"}
            if actor.staff_role == "EXPERIENTIAL_LEARNING_COORDINATOR"
            else set(),
        }
        if audience not in allowed.get(action, set()):
            raise AccessDenied(reveal=True)
        return audience

    # -- projections --------------------------------------------------------
    @staticmethod
    def project_condition(audience: str, condition: dict) -> dict:
        """Field-level privacy: only the office sees references to RESTRICTED evidence."""
        visible = dict(condition)
        if audience != "office" and condition["requirement_type"] in RESTRICTED_REQUIREMENTS:
            visible["evidence_reference"] = None
        return visible
