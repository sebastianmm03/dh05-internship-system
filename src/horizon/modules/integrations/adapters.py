"""M-11 Integration Adapters (Adapter pattern, ADR-007).

They translate the payloads and error codes of the simulated services into the
types and exceptions of our ports. Nothing outside this file knows the contracts.
"""

import json
from datetime import UTC, date, datetime
from pathlib import Path

from horizon.mocks.dh05_services import (
    MockEmployerDirectoryService,
    MockServiceError,
    MockStudentInformationServiceDH05,
)
from horizon.shared.ports import (
    AgreementSummary,
    ExternalDataConflict,
    ExternalRecordNotFound,
    ExternalServiceUnavailable,
    Identity,
    StudentProfile,
)


def _translate(error: MockServiceError) -> Exception:
    if error.http_status == 404:
        return ExternalRecordNotFound(error.failure_id)
    if error.http_status == 409:
        return ExternalDataConflict(error.failure_id)
    return ExternalServiceUnavailable(error.failure_id)


class EmployerDirectoryAdapter:
    def __init__(self, service: MockEmployerDirectoryService) -> None:
        self._service = service

    def agreement(self, organization_id: str) -> AgreementSummary:
        try:
            record = self._service.get(organization_id)
        except MockServiceError as error:
            raise _translate(error) from error
        valid_until = record.get("agreement_valid_until")
        return AgreementSummary(
            organization_id=record["organization_id"],
            active=bool(record.get("active")),
            agreement_status=record.get("agreement_status") or "UNKNOWN",
            agreement_valid_until=date.fromisoformat(valid_until) if valid_until else None,
            read_at=datetime.now(UTC),
        )


class StudentInformationAdapter:
    def __init__(self, service: MockStudentInformationServiceDH05) -> None:
        self._service = service

    def profile(self, student_id: str) -> StudentProfile:
        try:
            record = self._service.get(student_id)
        except MockServiceError as error:
            raise _translate(error) from error
        return StudentProfile(
            student_id=record["student_id"],
            program_code=record["program_code"],
            enrollment_status=record["enrollment_status"],
            completed_credits=int(record["completed_credits"]),
            academic_average=float(record["academic_average"]),
            academic_standing=record["academic_standing"],
            read_at=datetime.now(UTC),
        )


class IdentityAdapter:
    """Reads the DH-05 file mock_identities.json (the starter expected mock_users.json, EU-04)."""

    def __init__(self, data_root: Path) -> None:
        self._path = data_root / "reference" / "mock_identities.json"

    def resolve(self, user_id: str) -> Identity | None:
        with self._path.open("r", encoding="utf-8") as handle:
            records = json.load(handle)
        record = next((r for r in records if r["user_id"] == user_id), None)
        if record is None:
            return None
        return Identity(
            user_id=record["user_id"],
            display_name=record["display_name"],
            institutional_role=record["institutional_role"],
            active=bool(record.get("active", False)),
        )
