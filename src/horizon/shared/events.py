"""In-process domain events (Observer, ADR-008).

Handlers receive the database session of the command, so anything they write
(for example an outbox message) is committed or rolled back together with it.
"""

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session


@dataclass(frozen=True)
class DomainEvent:
    name: str
    payload: dict[str, Any]
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


Handler = Callable[[DomainEvent, Session], None]


class EventDispatcher:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Handler) -> None:
        self._handlers[event_name].append(handler)

    def publish(self, event: DomainEvent, session: Session) -> None:
        for handler in self._handlers[event.name]:
            handler(event, session)
