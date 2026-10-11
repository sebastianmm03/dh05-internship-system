"""M-09 Notifications: transactional outbox (ADR-008).

The handler only writes a message in the same transaction as the decision.
The worker delivers later; a delivery failure never touches the decision.
"""

from datetime import UTC, datetime
from typing import Any, Protocol

from sqlalchemy import JSON, DateTime, Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from horizon.infrastructure.database import Base
from horizon.shared.events import DomainEvent

MAX_ATTEMPTS = 5


class OutboxMessageModel(Base):
    __tablename__ = "outbox_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    event_name: Mapped[str] = mapped_column(String(64))
    recipient_id: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="PENDING")  # PENDING, SENT, FAILED
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)


def on_placement_activated(event: DomainEvent, session: Session) -> None:
    for key in ("student_id", "workplace_supervisor_id", "faculty_supervisor_id"):
        recipient = event.payload.get(key)
        if recipient:
            session.add(
                OutboxMessageModel(
                    event_name=event.name,
                    recipient_id=recipient,
                    payload={
                        "placement_id": event.payload["placement_id"],
                        "template": "placement_activated",
                    },
                    correlation_id=event.payload.get("correlation_id"),
                )
            )


class NotificationSender(Protocol):
    def send(self, message: OutboxMessageModel) -> None: ...


def deliver_pending(session: Session, sender: NotificationSender) -> dict[str, int]:
    """Called by the worker process. Returns a small summary."""
    summary = {"sent": 0, "retry": 0, "failed": 0}
    pending = session.scalars(
        select(OutboxMessageModel).where(OutboxMessageModel.status == "PENDING")
    )
    for message in list(pending):
        try:
            sender.send(message)
            message.status = "SENT"
            summary["sent"] += 1
        except Exception as error:  # the channel is external: any failure is retried
            message.attempts += 1
            message.last_error = str(error)[:500]
            if message.attempts >= MAX_ATTEMPTS:
                message.status = "FAILED"
                summary["failed"] += 1
            else:
                summary["retry"] += 1
        session.commit()  # one commit per message: a crash never repeats an already sent one
    return summary
