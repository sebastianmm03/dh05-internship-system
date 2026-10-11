import json
from pathlib import Path
from typing import Any

from horizon.infrastructure.importers.models import ImportedItem, ImportIssue, ImportResult
from horizon.infrastructure.importers.utils import extract_identifier


class JsonImporter:
    def import_file(self, path: Path) -> ImportResult:
        result = ImportResult(source_file=path.as_posix())
        try:
            with path.open("r", encoding="utf-8") as handle:
                document: Any = json.load(handle)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            result.issues.append(
                ImportIssue("error", path.as_posix(), f"Unable to parse JSON: {exc}")
            )
            return result

        records: list[Any]
        if isinstance(document, list):
            records = document
        elif isinstance(document, dict) and isinstance(document.get("records"), list):
            records = document["records"]
        elif isinstance(document, dict):
            records = [document]
        else:
            result.issues.append(
                ImportIssue(
                    "error",
                    path.as_posix(),
                    "JSON root must be an object, an array, or an object containing `records`.",
                )
            )
            return result

        for record_number, record in enumerate(records, start=1):
            result.records_read += 1
            if not isinstance(record, dict):
                result.issues.append(
                    ImportIssue(
                        "error",
                        path.as_posix(),
                        "JSON record must be an object.",
                        record_number,
                    )
                )
                continue

            identifier = extract_identifier(record)
            if identifier is None:
                result.issues.append(
                    ImportIssue(
                        "warning",
                        path.as_posix(),
                        "No source identifier could be inferred.",
                        record_number,
                    )
                )

            result.items.append(
                ImportedItem(
                    source_file=path.as_posix(),
                    source_identifier=identifier,
                    source_format="json",
                    payload=record,
                )
            )
        return result
