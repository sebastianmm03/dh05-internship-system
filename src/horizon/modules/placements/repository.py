"""Repository for the Placement aggregate (P-05). One repository per aggregate, not per table."""

from datetime import date, datetime
from typing import Protocol

from sqlalchemy import Date, DateTime, Integer, String, update
from sqlalchemy.orm import Mapped, Session, mapped_column

from horizon.infrastructure.database import Base
from horizon.modules.placements.domain import Placement, PlacementStatus, StaleState


class PlacementModel(Base):
    __tablename__ = "placements"

    placement_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    source_application_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    student_id: Mapped[str] = mapped_column(String(32), index=True)
    organization_id: Mapped[str] = mapped_column(String(32), index=True)
    placement_type: Mapped[str] = mapped_column(String(64))
    program_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    approved_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    approved_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    required_total_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    faculty_supervisor_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    workplace_supervisor_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class PlacementRepository(Protocol):
    def get(self, placement_id: str) -> Placement | None: ...

    def save(self, placement: Placement, expected_status: PlacementStatus) -> None: ...


class SqlPlacementRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, placement_id: str) -> Placement | None:
        row = self._session.get(PlacementModel, placement_id)
        if row is None:
            return None
        return Placement(
            placement_id=row.placement_id,
            student_id=row.student_id,
            organization_id=row.organization_id,
            placement_type=row.placement_type,
            program_code=row.program_code,
            status=PlacementStatus(row.status),
            workplace_supervisor_id=row.workplace_supervisor_id,
            faculty_supervisor_id=row.faculty_supervisor_id,
            activated_at=row.activated_at,
            actual_start_date=row.actual_start_date,
        )

    def save(self, placement: Placement, expected_status: PlacementStatus) -> None:
        """Writes the changes only if the stored status is still the one the command read.

        This is a conditional update, also called compare-and-set (ADR-010): two commands
        that read the same status cannot both write. The caller (application service) owns
        the commit.
        """
        result = self._session.execute(
            update(PlacementModel)
            .where(
                PlacementModel.placement_id == placement.placement_id,
                PlacementModel.status == expected_status.value,
            )
            .values(
                status=placement.status.value,
                activated_at=placement.activated_at,
                actual_start_date=placement.actual_start_date,
            )
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            raise StaleState(placement.placement_id)
