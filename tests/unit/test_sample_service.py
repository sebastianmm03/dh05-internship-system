from datetime import UTC, datetime

from horizon.application.sample_service import SampleRecordService
from horizon.domain.sample_record import SampleRecord


class FakeRepository:
    def __init__(self) -> None:
        self.last_limit: int | None = None

    def list_records(self, *, limit: int, source_file: str | None = None) -> list[SampleRecord]:
        self.last_limit = limit
        return [
            SampleRecord(
                id=1,
                source_file=source_file or "sample.csv",
                source_identifier="SRC-001",
                source_format="csv",
                payload={"status": "Open"},
                imported_at=datetime.now(UTC),
            )
        ]

    def get_record(self, record_id: int) -> SampleRecord | None:
        return None


def test_service_caps_requested_limit() -> None:
    repository = FakeRepository()
    service = SampleRecordService(repository)

    records = service.list_records(limit=5_000)

    assert repository.last_limit == 200
    assert len(records) == 1


def test_service_rejects_non_positive_record_identifier() -> None:
    service = SampleRecordService(FakeRepository())

    assert service.get_record(0) is None
