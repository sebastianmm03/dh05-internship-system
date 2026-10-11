from pathlib import Path

from horizon.infrastructure.importers import CsvImporter, JsonImporter


def test_csv_importer_preserves_identifier(tmp_path: Path) -> None:
    path = tmp_path / "records.csv"
    path.write_text("request_id,status\nREQ-001,Open\n", encoding="utf-8")

    result = CsvImporter().import_file(path)

    assert result.records_read == 1
    assert result.accepted == 1
    assert result.items[0].source_identifier == "REQ-001"


def test_json_importer_reports_non_object_record(tmp_path: Path) -> None:
    path = tmp_path / "records.json"
    path.write_text('[{"event_id": "E-1"}, 42]', encoding="utf-8")

    result = JsonImporter().import_file(path)

    assert result.records_read == 2
    assert result.accepted == 1
    assert result.rejected == 1
