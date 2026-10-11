"""M-08 Audit History: append-only entries written in the same transaction (ADR-006)."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from horizon.infrastructure.database import Base


class AuditEntryModel(Base):
    __tablename__ = "audit_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    actor_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64), index=True)
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str] = mapped_column(String(64), index=True)
    previous_value: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)


class AuditRecorder:
    """Only adds entries. There is deliberately no update or delete method."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def record(
        self,
        *,
        actor_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        previous_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        reason: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        self._session.add(
            AuditEntryModel(
                actor_id=actor_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                previous_value=previous_value,
                new_value=new_value,
                reason=reason,
                correlation_id=correlation_id,
            )
        )

    def history(self, resource_id: str) -> list[AuditEntryModel]:
        statement = (
            select(AuditEntryModel)
            .where(AuditEntryModel.resource_id == resource_id)
            .order_by(AuditEntryModel.id)
        )
        return list(self._session.scalars(statement))
