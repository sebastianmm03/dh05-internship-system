from pathlib import Path
from typing import Any

from horizon.mocks.file_store import JsonCollectionStore


class MockIdentityService:
    def __init__(self, data_root: Path) -> None:
        self._store = JsonCollectionStore(
            data_root / "reference" / "mock_identities.json",
            identifier_field="user_id",
        )

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        return self._store.get(user_id)
