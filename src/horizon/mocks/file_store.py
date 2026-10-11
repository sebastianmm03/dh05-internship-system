import json
from pathlib import Path
from typing import Any


class JsonCollectionStore:
    """Read-only store for small synthetic mock-service datasets."""

    def __init__(self, path: Path, identifier_field: str) -> None:
        self._path = path
        self._identifier_field = identifier_field

    def get(self, identifier: str) -> dict[str, Any] | None:
        records = self._read_records()
        return next(
            (record for record in records if str(record.get(self._identifier_field)) == identifier),
            None,
        )

    def list_all(self) -> list[dict[str, Any]]:
        return self._read_records()

    def _read_records(self) -> list[dict[str, Any]]:
        with self._path.open("r", encoding="utf-8") as handle:
            document = json.load(handle)
        if not isinstance(document, list) or not all(isinstance(item, dict) for item in document):
            raise ValueError(f"Expected a JSON array of objects in {self._path}")
        return document
