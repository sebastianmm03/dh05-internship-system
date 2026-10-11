from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from horizon.application.sample_service import SampleRecordService
from horizon.config import get_settings
from horizon.infrastructure.database import get_db_session
from horizon.infrastructure.repositories.sample_repository import (
    SqlAlchemySampleRecordRepository,
)
from horizon.mocks.identity_service import MockIdentityService


def get_sample_record_service(
    session: Session = Depends(get_db_session),
) -> SampleRecordService:
    repository = SqlAlchemySampleRecordRepository(session)
    return SampleRecordService(repository)


def get_current_mock_user(
    x_mock_user_id: str | None = Header(default=None, alias="X-Mock-User-Id"),
) -> dict:
    settings = get_settings()
    if not settings.mock_identity_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mock identity is disabled.",
        )
    if not x_mock_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Mock-User-Id header is required in development mode.",
        )

    user = MockIdentityService(settings.data_root).get_user(x_mock_user_id)
    if user is None or not user.get("active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown or inactive mock user.",
        )
    return user
