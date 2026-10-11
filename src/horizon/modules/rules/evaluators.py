"""M-06 Rule Configuration: readiness evaluators (Strategy) and their factory (Factory Method).

Each rule type is one small class with the same `evaluate` method. The gate does not
know which classes exist: it asks the factory to build them from the configuration
(ADR-004). Adding a condition is a configuration change; adding a new kind of rule is
a new class registered in RULE_TYPES, without touching the callers.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from horizon.shared.ports import (
    AgreementSummary,
    ExternalDataConflict,
    ExternalRecordNotFound,
    ExternalServiceUnavailable,
)


@dataclass(frozen=True)
class Condition:
    check_id: str
    requirement_type: str
    status: str
    evidence_reference: str | None = None
    valid_until: date | None = None


@dataclass(frozen=True)
class ReadinessContext:
    placement_id: str
    organization_id: str
    placement_type: str
    program_code: str | None
    workplace_supervisor_id: str | None
    faculty_supervisor_id: str | None
    conditions: dict[str, Condition]
    today: date
    agreement_lookup: Callable[[str], AgreementSummary]


@dataclass(frozen=True)
class Blocking:
    requirement: str
    check_id: str | None
    reason: str


class RequirementEvaluator(Protocol):
    def evaluate(self, context: ReadinessContext) -> list[Blocking]: ...


@dataclass
class RequirementComplete:
    """The checklist row exists, is COMPLETE and has not expired."""

    requirement: str

    def evaluate(self, context: ReadinessContext) -> list[Blocking]:
        condition = context.conditions.get(self.requirement)
        if condition is None:
            return [Blocking(self.requirement, None, "required condition is not registered")]
        if condition.status != "COMPLETE":
            return [Blocking(self.requirement, condition.check_id, f"status is {condition.status}")]
        if condition.valid_until and condition.valid_until < context.today:
            return [
                Blocking(
                    self.requirement, condition.check_id, f"expired on {condition.valid_until}"
                )
            ]
        return []


@dataclass
class AgreementValidInDirectory:
    """Asks the authoritative Employer Directory. If it cannot answer, the gate stays closed."""

    def evaluate(self, context: ReadinessContext) -> list[Blocking]:
        try:
            agreement = context.agreement_lookup(context.organization_id)
        except ExternalServiceUnavailable as error:
            return [Blocking("VALID_AGREEMENT", None, f"agreement could not be verified ({error})")]
        except ExternalDataConflict as error:
            return [
                Blocking(
                    "VALID_AGREEMENT", None, f"directory data in conflict ({error}), manual review"
                )
            ]
        except ExternalRecordNotFound as error:
            return [
                Blocking(
                    "VALID_AGREEMENT", None, f"organization unknown to the directory ({error})"
                )
            ]
        if not agreement.is_valid_on(context.today):
            return [
                Blocking(
                    "VALID_AGREEMENT",
                    None,
                    f"directory agreement {agreement.agreement_status}, "
                    f"valid until {agreement.agreement_valid_until}",
                )
            ]
        return []


@dataclass
class SupervisorsAssigned:
    def evaluate(self, context: ReadinessContext) -> list[Blocking]:
        missing = []
        if not context.workplace_supervisor_id:
            missing.append(Blocking("SUPERVISORS", None, "workplace supervisor not assigned"))
        if not context.faculty_supervisor_id:
            missing.append(Blocking("SUPERVISORS", None, "faculty supervisor not assigned"))
        return missing


RULE_TYPES: dict[str, Callable[..., RequirementEvaluator]] = {
    "REQUIREMENT_COMPLETE": RequirementComplete,
    "AGREEMENT_VALID_IN_DIRECTORY": AgreementValidInDirectory,
    "SUPERVISORS_ASSIGNED": SupervisorsAssigned,
}


class RuleEvaluatorFactory:
    def build(self, rule: dict[str, Any]) -> RequirementEvaluator:
        params = {k: v for k, v in rule.items() if k != "type"}
        try:
            return RULE_TYPES[rule["type"]](**params)
        except KeyError as error:
            raise ValueError(f"Unknown rule type in configuration: {rule.get('type')}") from error


@dataclass
class ReadinessRuleSet:
    version: str
    rules: list[dict[str, Any]] = field(default_factory=list)


class RuleConfiguration:
    """Versioned rule file. Lookup order: 'TYPE@PROGRAM', then 'TYPE', then 'default'."""

    def __init__(self, path: Path) -> None:
        with path.open(encoding="utf-8") as handle:
            self._document = json.load(handle)

    @property
    def version(self) -> str:
        return self._document["version"]

    def readiness_rules(self, placement_type: str, program_code: str | None) -> ReadinessRuleSet:
        readiness = self._document["readiness"]
        for key in (f"{placement_type}@{program_code}", placement_type, "default"):
            if key in readiness:
                return ReadinessRuleSet(version=self.version, rules=readiness[key])
        return ReadinessRuleSet(version=self.version, rules=[])
