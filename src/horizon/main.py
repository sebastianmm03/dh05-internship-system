import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from horizon import __version__
from horizon.config import get_settings
from horizon.infrastructure.database import create_database_schema
from horizon.interfaces.api.health import router as health_router
from horizon.interfaces.api.mock_services import router as mock_services_router
from horizon.interfaces.api.sample_records import router as sample_records_router
from horizon.modules.audit.recorder import AuditEntryModel  # noqa: F401  (table registration)
from horizon.modules.notifications.outbox import OutboxMessageModel  # noqa: F401
from horizon.modules.placements.api import router as placements_router

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    create_database_schema()
    yield


app = FastAPI(
    title="DH-05 Internship and Practicum Management System",
    version=__version__,
    description=(
        "Modular monolith built on the Horizon common starter (ADR-000, ADR-001). "
        "Evaluation 2 implementation foundation: activation gate slice."
    ),
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(sample_records_router)
app.include_router(mock_services_router)
app.include_router(placements_router)
