from fastapi import APIRouter, HTTPException, Query, status

from horizon.config import get_settings
from horizon.mocks.dh05_services import (
    MockEmployerDirectoryService,
    MockServiceError,
    MockStudentInformationServiceDH05,
)
from horizon.mocks.identity_service import MockIdentityService

router = APIRouter(prefix="/mock", tags=["development mocks"])


@router.get("/identity/users/{user_id}")
def get_mock_identity(user_id: str) -> dict:
    settings = get_settings()
    if not settings.mock_identity_enabled:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Mock identity is disabled.")
    user = MockIdentityService(settings.data_root).get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Synthetic user not found.")
    return user


def _answer(service, identifier: str) -> dict:
    try:
        return service.get(identifier)
    except MockServiceError as error:
        raise HTTPException(
            error.http_status, {"error": error.error, "failure_id": error.failure_id}
        ) from error


@router.get("/student-information/students/{student_id}")
def get_mock_student(student_id: str, simulate_failure: str | None = Query(default=None)) -> dict:
    """DH-05 contract. simulate_failure accepts SIS-404, SIS-409 or SIS-503."""
    return _answer(
        MockStudentInformationServiceDH05(get_settings().mocks_root, simulate_failure), student_id
    )


@router.get("/employers/{organization_id}")
def get_mock_employer(
    organization_id: str, simulate_failure: str | None = Query(default=None)
) -> dict:
    """DH-05 contract. simulate_failure accepts EMP-404, EMP-409 or EMP-503."""
    return _answer(
        MockEmployerDirectoryService(get_settings().mocks_root, simulate_failure), organization_id
    )
