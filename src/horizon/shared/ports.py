"""Ports owned by the core (ADR-007): the shared kernel defines them, M-11 implements them."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol


class ExternalServiceUnavailable(Exception):
    """The authoritative service could not answer (for example EMP-503 or SIS-503)."""


class ExternalRecordNotFound(Exception):
    """The authoritative service does not know the identifier (404)."""


class ExternalDataConflict(Exception):
    """The service answered but its data cannot be trusted (409)."""


@dataclass(frozen=True)
class AgreementSummary:
    organization_id: str
    active: bool
    agreement_status: str
    agreement_valid_until: date | None
    read_at: datetime

    def is_valid_on(self, day: date) -> bool:
        if not self.active:
            return False
        if self.agreement_status == "INTERNAL":
            return True  # university departments do not need an external agreement
        if self.agreement_status != "ACTIVE" or self.agreement_valid_until is None:
            return False
        return self.agreement_valid_until >= day


@dataclass(frozen=True)
class StudentProfile:
    student_id: str
    program_code: str
    enrollment_status: str
    completed_credits: int
    academic_average: float
    academic_standing: str
    read_at: datetime


@dataclass(frozen=True)
class Identity:
    user_id: str
    display_name: str
    institutional_role: str  # STUDENT, EMPLOYEE, EXTERNAL
    active: bool


class EmployerDirectoryPort(Protocol):
    def agreement(self, organization_id: str) -> AgreementSummary: ...


class StudentInformationPort(Protocol):
    def profile(self, student_id: str) -> StudentProfile: ...


class IdentityPort(Protocol):
    def resolve(self, user_id: str) -> Identity | None: ...
