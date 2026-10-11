from typing import Protocol

from horizon.domain.sample_record import SampleRecord


class SampleRecordReader(Protocol):
    def list_records(
        self,
        *,
        limit: int,
        source_file: str | None = None,
    ) -> list[SampleRecord]: ...

    def get_record(self, record_id: int) -> SampleRecord | None: ...


class SampleRecordService:
    """Small application service that demonstrates a repository boundary."""

    def __init__(self, repository: SampleRecordReader) -> None:
        self._repository = repository

    def list_records(
        self,
        *,
        limit: int = 50,
        source_file: str | None = None,
    ) -> list[SampleRecord]:
        safe_limit = min(max(limit, 1), 200)
        return self._repository.list_records(limit=safe_limit, source_file=source_file)

    def get_record(self, record_id: int) -> SampleRecord | None:
        if record_id < 1:
            return None
        return self._repository.get_record(record_id)
