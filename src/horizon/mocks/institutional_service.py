from pathlib import Path
from typing import Any

from horizon.mocks.file_store import JsonCollectionStore


class MockStudentInformationService:
    def __init__(self, data_root: Path) -> None:
        self._store = JsonCollectionStore(
            data_root / "reference" / "mock_students.json",
            identifier_field="student_id",
        )

    def get_student(self, student_id: str) -> dict[str, Any] | None:
        return self._store.get(student_id)
