import json
from datetime import UTC, datetime

from common import data_root, discover_data_files, import_path


def main() -> int:
    root = data_root()
    files = discover_data_files(root)
    results = [import_path(path) for path in files]

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "files_processed": len(results),
        "records_read": sum(result.records_read for result in results),
        "records_accepted": sum(result.accepted for result in results),
        "errors": sum(result.rejected for result in results),
        "warnings": sum(result.warnings for result in results),
        "files": [result.as_dict() for result in results],
    }

    output_dir = root / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "validation_report.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("Validation summary")
    print("------------------")
    print(f"Files processed: {report['files_processed']}")
    print(f"Records read: {report['records_read']}")
    print(f"Records accepted: {report['records_accepted']}")
    print(f"Errors: {report['errors']}")
    print(f"Warnings: {report['warnings']}")
    print(f"Report: {output_path}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
