"""M-04 Readiness & Documents: checklist storage and the readiness gate."""

from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from horizon.infrastructure.database import Base
from horizon.modules.rules.evaluators import (
    Blocking,
    Condition,
    ReadinessContext,
    RuleConfiguration,
    RuleEvaluatorFactory,
)
from horizon.shared.ports import EmployerDirectoryPort


class ReadinessConditionModel(Base):
    __tablename__ = "readiness_conditions"

    check_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    placement_id: Mapped[str] = mapped_column(String(32), index=True)
    requirement_type: Mapped[str] = mapped_column(String(64))
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evidence_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)


@dataclass(frozen=True)
class PlacementFacts:
    """What the gate needs to know about a placement; given by M-03 through the facade."""

    placement_id: str
    organization_id: str
    placement_type: str
    program_code: str | None
    workplace_supervisor_id: str | None
    faculty_supervisor_id: str | None


@dataclass(frozen=True)
class GateResult:
    rule_version: str
    blocking: list[Blocking]

    @property
    def passed(self) -> bool:
        return not self.blocking


class ReadinessGate:
    def __init__(
        self,
        session: Session,
        rules: RuleConfiguration,
        employer_directory: EmployerDirectoryPort,
        factory: RuleEvaluatorFactory | None = None,
    ) -> None:
        self._session = session
        self._rules = rules
        self._directory = employer_directory
        self._factory = factory or RuleEvaluatorFactory()

    def checklist(self, placement_id: str) -> list[ReadinessConditionModel]:
        statement = (
            select(ReadinessConditionModel)
            .where(ReadinessConditionModel.placement_id == placement_id)
            .order_by(ReadinessConditionModel.check_id)
        )
        return list(self._session.scalars(statement))

    def evaluate(self, facts: PlacementFacts, today: date) -> GateResult:
        conditions = {
            row.requirement_type: Condition(
                check_id=row.check_id,
                requirement_type=row.requirement_type,
                status=row.status,
                evidence_reference=row.evidence_reference,
                valid_until=row.valid_until,
            )
            for row in self.checklist(facts.placement_id)
            if row.required
        }
        context = ReadinessContext(
            placement_id=facts.placement_id,
            organization_id=facts.organization_id,
            placement_type=facts.placement_type,
            program_code=facts.program_code,
            workplace_supervisor_id=facts.workplace_supervisor_id,
            faculty_supervisor_id=facts.faculty_supervisor_id,
            conditions=conditions,
            today=today,
            agreement_lookup=self._directory.agreement,
        )
        rule_set = self._rules.readiness_rules(facts.placement_type, facts.program_code)
        blocking: list[Blocking] = []
        # Every rule is evaluated so that the office sees ALL missing conditions at once.
        for rule in rule_set.rules:
            blocking.extend(self._factory.build(rule).evaluate(context))
        return GateResult(rule_version=rule_set.version, blocking=blocking)
