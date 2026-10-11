"""Builds the DH-05 domain tables from the raw exports and writes the transformation log."""

from datetime import UTC, datetime

from common import data_root

import horizon.main  # noqa: F401  (registers every module table)
from horizon.infrastructure.database import SessionLocal, create_database_schema
from horizon.infrastructure.seed import seed_placements


def main() -> int:
    root = data_root()
    create_database_schema()
    with SessionLocal() as session:
        log = seed_placements(session, root)
    output = root / "generated" / "transformation_log.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "# Transformation log\n\n"
        f"Generated {datetime.now(UTC).isoformat()} by scripts/seed_domain.py.\n"
        "Raw files in data/raw and data/reference are not modified (ASM-010).\n\n"
        + "\n".join(log)
        + "\n",
        encoding="utf-8",
    )
    print("\n".join(log))
    print(f"Log: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
