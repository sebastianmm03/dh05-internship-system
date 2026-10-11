from dataclasses import dataclass, field
from typing import Any, Literal

IssueSeverity = Literal["warning", "error"]


@dataclass(frozen=True, slots=True)
class ImportIssue:
    severity: IssueSeverity
    source_file: str
    message: str
    record_number: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "source_file": self.source_file,
            "message": self.message,
            "record_number": self.record_number,
        }


@dataclass(frozen=True, slots=True)
class ImportedItem:
    source_file: str
    source_identifier: str | None
    source_format: str
    payload: dict[str, Any]


@dataclass(slots=True)
class ImportResult:
    source_file: str
    records_read: int = 0
    items: list[ImportedItem] = field(default_factory=list)
    issues: list[ImportIssue] = field(default_factory=list)

    @property
    def accepted(self) -> int:
        return len(self.items)

    @property
    def rejected(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "records_read": self.records_read,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "warnings": self.warnings,
            "issues": [issue.as_dict() for issue in self.issues],
        }
