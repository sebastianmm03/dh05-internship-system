from fastapi import APIRouter

from horizon import __version__
from horizon.config import get_settings
from horizon.interfaces.api.schemas import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service="dh05-internship-system",
        version=__version__,
        project_code=settings.project_code,
    )
