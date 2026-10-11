"""Transformation from the raw data-pack exports to the domain tables (ASM-010, EU-03).

The raw files are never modified. Every decision taken here is written to the
transformation log so the team can defend it.
"""

import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from horizon.modules.placements.repository import PlacementModel
from horizon.modules.readiness.gate import ReadinessConditionModel
from horizon.modules.rules.reference import load_program_aliases, normalize_program_code

# 'Blocked' and 'Activation pending' are not states: blocking is derived from the gate (ADR-003).
STATUS_MAP = {
    "Activation pending": "PENDING_ACTIVATION",
    "Blocked": "PENDING_ACTIVATION",
    "ACTIVE": "ACTIVE",
    "Completion pending": "COMPLETION_PENDING",
}


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _dt(value: str) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def seed_placements(session: Session, data_root: Path) -> list[str]:
    log: list[str] = []
    aliases = load_program_aliases(data_root)
    students = {
        r["student_id"]: r for r in _rows(data_root / "raw" / "students_current_export.csv")
    }

    session.execute(delete(ReadinessConditionModel))
    session.execute(delete(PlacementModel))

    for row in _rows(data_root / "raw" / "placements.csv"):
        raw_program = students.get(row["student_id"], {}).get("program_code", "")
        program = normalize_program_code(raw_program, aliases) if raw_program else None
        status = STATUS_MAP.get(row["placement_status"])
        if status is None:
            log.append(
                f"- {row['placement_id']}: unknown status '{row['placement_status']}', skipped."
            )
            continue
        if status != row["placement_status"]:
            log.append(
                f"- {row['placement_id']}: status '{row['placement_status']}' mapped to {status}."
            )
        session.add(
            PlacementModel(
                placement_id=row["placement_id"],
                source_application_id=row["source_application_id"] or None,
                student_id=row["student_id"],
                organization_id=row["organization_id"],
                placement_type=row["placement_type"],
                program_code=program,
                approved_start_date=datetime.fromisoformat(row["approved_start_date"]).date()
                if row["approved_start_date"]
                else None,
                approved_end_date=datetime.fromisoformat(row["approved_end_date"]).date()
                if row["approved_end_date"]
                else None,
                required_total_hours=int(row["required_total_hours"])
                if row["required_total_hours"]
                else None,
                faculty_supervisor_id=row["faculty_supervisor_id"] or None,
                workplace_supervisor_id=row["workplace_supervisor_id"] or None,
                status=status,
                activated_at=_dt(row["activated_at"]),
            )
        )

    for row in _rows(data_root / "raw" / "readiness_checklist.csv"):
        session.add(
            ReadinessConditionModel(
                check_id=row["check_id"],
                placement_id=row["placement_id"],
                requirement_type=row["requirement_type"],
                required=row["required"].lower() == "true",
                status=row["status"],
                completed_at=_dt(row["completed_at"]),
                evidence_reference=row["evidence_reference"] or None,
            )
        )
    log.append(
        "- readiness_checklist.csv has no validity date column; "
        "expiry is taken from status EXPIRED "
        "and from the Employer Directory agreement date at activation."
    )
    applications = {r["application_id"]: r for r in _rows(data_root / "raw" / "applications.csv")}
    checklist = {
        (r["placement_id"], r["requirement_type"])
        for r in _rows(data_root / "raw" / "readiness_checklist.csv")
    }
    for row in _rows(data_root / "raw" / "placements.csv"):
        app = applications.get(row["source_application_id"])
        if (
            app
            and app["academic_approval"] == "APPROVED"
            and ((row["placement_id"], "ACADEMIC_APPROVAL") not in checklist)
        ):
            log.append(
                f"- {row['placement_id']}: {app['application_id']} says academic approval APPROVED "
                "but the checklist has no ACADEMIC_APPROVAL row. Not invented: the gate reports it "
                "as not registered until the AcademicApprovalRecorded event creates it."
            )
    for sid, student in students.items():
        normalized = normalize_program_code(student["program_code"], aliases)
        if normalized != student["program_code"]:
            log.append(
                f"- {sid}: legacy program code '{student['program_code']}' "
                f"normalized to {normalized}."
            )
    session.commit()
    return log
