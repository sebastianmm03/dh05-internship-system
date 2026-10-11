import json
from datetime import UTC, date, datetime
from pathlib import Path

from horizon.modules.rules.evaluators import (
    AgreementValidInDirectory,
    Condition,
    ReadinessContext,
    RequirementComplete,
    RuleConfiguration,
)
from horizon.shared.ports import AgreementSummary, ExternalServiceUnavailable

TODAY = date(2026, 9, 24)


def context(conditions, lookup=None) -> ReadinessContext:
    def ok(org):
        return AgreementSummary(org, True, "ACTIVE", date(2027, 12, 31), datetime.now(UTC))

    return ReadinessContext(
        "PLC-X",
        "ORG-001",
        "ACADEMIC_INTERNSHIP",
        "BSC-SWE",
        "SUP-EXT-002",
        "FAC-SUP-101",
        {c.requirement_type: c for c in conditions},
        TODAY,
        lookup or ok,
    )


def test_pending_condition_blocks() -> None:
    blocking = RequirementComplete("WORK_PLAN").evaluate(
        context([Condition("READY-006", "WORK_PLAN", "PENDING")])
    )
    assert blocking[0].check_id == "READY-006"


def test_expired_condition_blocks_even_if_marked_complete() -> None:
    blocking = RequirementComplete("VALID_AGREEMENT").evaluate(
        context(
            [Condition("READY-X", "VALID_AGREEMENT", "COMPLETE", valid_until=date(2026, 7, 31))]
        )
    )
    assert "expired" in blocking[0].reason


def test_missing_condition_blocks() -> None:
    blocking = RequirementComplete("INSURANCE_REFERENCE").evaluate(context([]))
    assert blocking[0].reason == "required condition is not registered"


def test_directory_unavailable_keeps_gate_closed() -> None:
    def down(_org):
        raise ExternalServiceUnavailable("EMP-503")

    blocking = AgreementValidInDirectory().evaluate(context([], lookup=down))
    assert "could not be verified" in blocking[0].reason


def test_rule_change_is_configuration_only(tmp_path: Path) -> None:
    """QS-07: a program adds CONFIDENTIALITY_FORM without any code change."""
    root = Path(__file__).resolve().parents[2]
    base = json.loads((root / "config/rules/readiness.json").read_text(encoding="utf-8"))
    base["version"] = "readiness-v2"
    base["readiness"]["PROFESSIONAL_PRACTICUM@BSC-BIO"] = base["readiness"][
        "PROFESSIONAL_PRACTICUM"
    ] + [{"type": "REQUIREMENT_COMPLETE", "requirement": "CONFIDENTIALITY_FORM"}]
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(base), encoding="utf-8")

    config = RuleConfiguration(path)
    bio = config.readiness_rules("PROFESSIONAL_PRACTICUM", "BSC-BIO")
    civil = config.readiness_rules("PROFESSIONAL_PRACTICUM", "BENG-CIV")

    assert bio.version == "readiness-v2"
    assert {"type": "REQUIREMENT_COMPLETE", "requirement": "CONFIDENTIALITY_FORM"} in bio.rules
    assert len(civil.rules) == len(bio.rules) - 1
