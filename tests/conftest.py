"""Test configuration: a throw-away SQLite database seeded from the DH-05 data pack."""

import os
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DB = Path(tempfile.gettempdir()) / "dh05_test.db"  # outside the repository
TEST_DB.unlink(missing_ok=True)  # always start from the current schema, never from an old file
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["DATA_ROOT"] = str(ROOT / "data")
os.environ["MOCKS_ROOT"] = str(ROOT / "mocks")
os.environ["RULES_ROOT"] = str(ROOT / "config" / "rules")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from horizon.infrastructure.database import SessionLocal, create_database_schema  # noqa: E402
from horizon.infrastructure.seed import seed_placements  # noqa: E402
from horizon.main import app  # noqa: E402
from horizon.modules.placements import api as placements_api  # noqa: E402

# Fixed "today" so that agreement validity does not change with the calendar.
TODAY = date(2026, 9, 24)


@pytest.fixture()
def session():
    create_database_schema()
    with SessionLocal() as s:
        from horizon.modules.audit.recorder import AuditEntryModel
        from horizon.modules.notifications.outbox import OutboxMessageModel

        s.query(AuditEntryModel).delete()
        s.query(OutboxMessageModel).delete()
        s.commit()
        seed_placements(s, ROOT / "data")
        yield s


@pytest.fixture()
def client(session):
    app.dependency_overrides[placements_api.get_today] = lambda: TODAY
    yield TestClient(app)
    app.dependency_overrides.clear()


def as_user(user_id: str) -> dict:
    return {"X-Mock-User-Id": user_id}
