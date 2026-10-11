from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    project_code: str


class SampleRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_file: str
    source_identifier: str | None
    source_format: str
    payload: dict[str, Any]
    imported_at: datetime
