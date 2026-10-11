"""Reference data owned by M-06 (programs, placement types)."""

import csv
from pathlib import Path


def load_program_aliases(data_root: Path) -> dict[str, str]:
    """Maps every known alias (and the official code) to the official program code.

    Needed because students_current_export.csv still uses legacy codes, e.g. 'SWE' (EU-03).
    """
    aliases: dict[str, str] = {}
    with (data_root / "reference" / "academic_programs.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            code = row["program_code"]
            aliases[code.upper()] = code
            for alias in (row.get("known_aliases") or "").split("|"):
                if alias.strip():
                    aliases[alias.strip().upper()] = code
    return aliases


def normalize_program_code(raw_code: str, aliases: dict[str, str]) -> str | None:
    return aliases.get(raw_code.strip().upper())
