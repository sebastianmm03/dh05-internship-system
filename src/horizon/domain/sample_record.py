from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class SampleRecord:
    """Generic imported source record used only by the starter shell."""

    id: int
    source_file: str
    source_identifier: str | None
    source_format: str
    payload: dict[str, Any]
    imported_at: datetime
