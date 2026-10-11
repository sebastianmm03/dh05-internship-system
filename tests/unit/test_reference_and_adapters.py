from datetime import date
from pathlib import Path

import pytest

from horizon.mocks.dh05_services import (
    MockEmployerDirectoryService,
    MockStudentInformationServiceDH05,
)
from horizon.modules.integrations.adapters import (
    EmployerDirectoryAdapter,
    StudentInformationAdapter,
)
from horizon.modules.rules.reference import load_program_aliases, normalize_program_code
from horizon.shared.ports import (
    ExternalDataConflict,
    ExternalRecordNotFound,
    ExternalServiceUnavailable,
)

MOCKS = Path("mocks")


def test_legacy_program_code_is_normalized() -> None:
    aliases = load_program_aliases(Path("data"))
    assert normalize_program_code("SWE", aliases) == "BSC-SWE"  # HU-STU-5006 (EU-03)
    assert normalize_program_code("BA Psych", aliases) == "BA-PSY"


def test_expired_agreement_is_not_valid() -> None:
    agreement = EmployerDirectoryAdapter(MockEmployerDirectoryService(MOCKS)).agreement("ORG-005")
    assert agreement.is_valid_on(date(2026, 9, 24)) is False


def test_active_agreement_is_valid() -> None:
    agreement = EmployerDirectoryAdapter(MockEmployerDirectoryService(MOCKS)).agreement("ORG-001")
    assert agreement.is_valid_on(date(2026, 9, 24)) is True


@pytest.mark.parametrize(
    "failure,error",
    [
        ("SIS-503", ExternalServiceUnavailable),
        ("SIS-409", ExternalDataConflict),
        ("SIS-404", ExternalRecordNotFound),
    ],
)
def test_student_service_failures_are_translated(failure, error) -> None:
    adapter = StudentInformationAdapter(MockStudentInformationServiceDH05(MOCKS, failure))
    with pytest.raises(error):
        adapter.profile("HU-STU-5001")


def test_student_profile_is_read_with_timestamp() -> None:
    profile = StudentInformationAdapter(MockStudentInformationServiceDH05(MOCKS)).profile(
        "HU-STU-5001"
    )
    assert profile.program_code == "BSC-SWE"
    assert profile.read_at is not None
