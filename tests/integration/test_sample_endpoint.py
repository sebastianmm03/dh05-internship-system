from datetime import UTC, datetime

from fastapi.testclient import TestClient

from horizon.application.sample_service import SampleRecordService
from horizon.domain.sample_record import SampleRecord
from horizon.interfaces.api.dependencies import get_sample_record_service
from horizon.main import app


class FakeRepository:
    def list_records(self, *, limit: int, source_file: str | None = None) -> list[SampleRecord]:
        return [
            SampleRecord(
                id=1,
                source_file="data/raw/sample.csv",
                source_identifier="SRC-001",
                source_format="csv",
                payload={"status": "Open"},
                imported_at=datetime.now(UTC),
            )
        ]

    def get_record(self, record_id: int) -> SampleRecord | None:
        return None


def override_service() -> SampleRecordService:
    return SampleRecordService(FakeRepository())


def test_list_sample_records_requires_mock_identity() -> None:
    app.dependency_overrides[get_sample_record_service] = override_service
    client = TestClient(app)

    response = client.get("/sample-records")

    assert response.status_code == 401
    app.dependency_overrides.clear()


def test_list_sample_records_returns_records_for_active_mock_user() -> None:
    app.dependency_overrides[get_sample_record_service] = override_service
    client = TestClient(app)

    response = client.get(
        "/sample-records",
        headers={"X-Mock-User-Id": "HU-STU-5001"},
    )

    assert response.status_code == 200
    assert response.json()[0]["source_identifier"] == "SRC-001"
    app.dependency_overrides.clear()
