import argparse
import json
from datetime import UTC, datetime

from common import data_root, discover_data_files, import_path

from horizon.infrastructure.database import SessionLocal, create_database_schema
from horizon.infrastructure.repositories.sample_repository import (
    SqlAlchemySampleRecordRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load generic Horizon starter records.")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Clear previously imported generic records before loading.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = data_root()
    results = [import_path(path) for path in discover_data_files(root)]
    items = [item for result in results for item in result.items]

    create_database_schema()
    with SessionLocal() as session:
        repository = SqlAlchemySampleRecordRepository(session)
        if args.replace:
            repository.clear()
        inserted = repository.add_items(items)

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "replace_existing": args.replace,
        "files_processed": len(results),
        "records_read": sum(result.records_read for result in results),
        "records_inserted": inserted,
        "errors": sum(result.rejected for result in results),
        "warnings": sum(result.warnings for result in results),
        "files": [result.as_dict() for result in results],
    }

    output_dir = root / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "import_report.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("Import summary")
    print("--------------")
    print(f"Files processed: {report['files_processed']}")
    print(f"Records read: {report['records_read']}")
    print(f"Records inserted: {report['records_inserted']}")
    print(f"Errors: {report['errors']}")
    print(f"Warnings: {report['warnings']}")
    print(f"Report: {output_path}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
