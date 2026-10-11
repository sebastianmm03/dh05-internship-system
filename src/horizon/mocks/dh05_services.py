"""Development-only mocks that follow the DH-05 service contracts (mocks/ folder)."""

import json
from pathlib import Path
from typing import Any


class MockServiceError(Exception):
    """A documented failure of a simulated service (see failure-responses.json)."""

    def __init__(self, failure: dict[str, Any]) -> None:
        super().__init__(failure["message"])
        self.failure_id: str = failure["failure_id"]
        self.http_status: int = failure["http_status"]
        self.error: str = failure["error"]


class _ContractMock:
    folder = ""
    records_file = ""
    id_field = ""
    not_found_id = ""

    def __init__(self, mocks_root: Path, simulate_failure: str | None = None) -> None:
        self._root = mocks_root / self.folder
        self._simulate_failure = simulate_failure

    def _read(self, file_name: str) -> list[dict[str, Any]]:
        with (self._root / file_name).open("r", encoding="utf-8") as handle:
            return json.load(handle)["records"]

    def _failure(self, failure_id: str) -> MockServiceError:
        failure = next(
            f for f in self._read("failure-responses.json") if f["failure_id"] == failure_id
        )
        return MockServiceError(failure)

    def get(self, identifier: str) -> dict[str, Any]:
        if self._simulate_failure:
            raise self._failure(self._simulate_failure)
        record = next(
            (r for r in self._read(self.records_file) if r[self.id_field] == identifier), None
        )
        if record is None:
            raise self._failure(self.not_found_id)
        return record


class MockEmployerDirectoryService(_ContractMock):
    folder = "employer_directory_service"
    records_file = "organizations.json"
    id_field = "organization_id"
    not_found_id = "EMP-404"


class MockStudentInformationServiceDH05(_ContractMock):
    folder = "student_information_service"
    records_file = "students.json"
    id_field = "student_id"
    not_found_id = "SIS-404"
