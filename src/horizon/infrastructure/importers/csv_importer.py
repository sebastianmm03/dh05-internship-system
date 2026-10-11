import csv
from pathlib import Path

from horizon.infrastructure.importers.models import ImportedItem, ImportIssue, ImportResult
from horizon.infrastructure.importers.utils import extract_identifier


class CsvImporter:
    def import_file(self, path: Path) -> ImportResult:
        result = ImportResult(source_file=path.as_posix())
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                if not reader.fieldnames:
                    result.issues.append(
                        ImportIssue("error", path.as_posix(), "CSV file has no header row.")
                    )
                    return result

                duplicate_headers = {
                    name for name in reader.fieldnames if reader.fieldnames.count(name) > 1
                }
                if duplicate_headers:
                    result.issues.append(
                        ImportIssue(
                            "warning",
                            path.as_posix(),
                            f"Duplicate CSV headers detected: {sorted(duplicate_headers)}",
                        )
                    )

                for row_number, row in enumerate(reader, start=2):
                    result.records_read += 1
                    payload = {key: value for key, value in row.items() if key is not None}
                    if not any(value not in (None, "") for value in payload.values()):
                        result.issues.append(
                            ImportIssue(
                                "warning",
                                path.as_posix(),
                                "Blank CSV row skipped.",
                                row_number,
                            )
                        )
                        continue

                    identifier = extract_identifier(payload)
                    if identifier is None:
                        result.issues.append(
                            ImportIssue(
                                "warning",
                                path.as_posix(),
                                "No source identifier could be inferred.",
                                row_number,
                            )
                        )

                    result.items.append(
                        ImportedItem(
                            source_file=path.as_posix(),
                            source_identifier=identifier,
                            source_format="csv",
                            payload=payload,
                        )
                    )
        except (OSError, UnicodeError, csv.Error) as exc:
            result.issues.append(
                ImportIssue("error", path.as_posix(), f"Unable to parse CSV: {exc}")
            )
        return result
