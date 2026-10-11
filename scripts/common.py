from pathlib import Path

from horizon.config import get_settings
from horizon.infrastructure.importers import CsvImporter, ImportResult, JsonImporter

SUPPORTED_SUFFIXES = {".csv", ".json"}


def discover_data_files(data_root: Path) -> list[Path]:
    files: list[Path] = []
    for directory_name in ("raw", "reference", "events"):
        directory = data_root / directory_name
        if not directory.exists():
            continue
        files.extend(
            path
            for path in directory.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        )
    return sorted(files)


def import_path(path: Path) -> ImportResult:
    if path.suffix.lower() == ".csv":
        return CsvImporter().import_file(path)
    if path.suffix.lower() == ".json":
        return JsonImporter().import_file(path)
    raise ValueError(f"Unsupported data file: {path}")


def data_root() -> Path:
    return get_settings().data_root
