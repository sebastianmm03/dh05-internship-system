from fastapi import APIRouter, Depends, HTTPException, Query, status

from horizon.application.sample_service import SampleRecordService
from horizon.interfaces.api.dependencies import get_current_mock_user, get_sample_record_service
from horizon.interfaces.api.schemas import SampleRecordResponse

router = APIRouter(prefix="/sample-records", tags=["starter records"])


@router.get("", response_model=list[SampleRecordResponse])
def list_sample_records(
    limit: int = Query(default=50, ge=1, le=200),
    source_file: str | None = None,
    service: SampleRecordService = Depends(get_sample_record_service),
    _current_user: dict = Depends(get_current_mock_user),
) -> list[SampleRecordResponse]:
    records = service.list_records(limit=limit, source_file=source_file)
    return [SampleRecordResponse.model_validate(record) for record in records]


@router.get("/{record_id}", response_model=SampleRecordResponse)
def get_sample_record(
    record_id: int,
    service: SampleRecordService = Depends(get_sample_record_service),
    _current_user: dict = Depends(get_current_mock_user),
) -> SampleRecordResponse:
    record = service.get_record(record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imported record not found.",
        )
    return SampleRecordResponse.model_validate(record)
