from datetime import UTC, datetime

import pytest

from horizon.modules.placements.domain import (
    ActivationBlocked,
    IllegalTransition,
    Placement,
    PlacementStatus,
)


def make(status=PlacementStatus.PENDING_ACTIVATION) -> Placement:
    return Placement("PLC-X", "HU-STU-5001", "ORG-001", "ACADEMIC_INTERNSHIP", "BSC-SWE", status)


def test_activation_needs_a_passed_gate() -> None:
    placement = make()
    with pytest.raises(ActivationBlocked):
        placement.activate(False, ["READY-004"], datetime.now(UTC))
    assert placement.status == PlacementStatus.PENDING_ACTIVATION


def test_activation_with_passed_gate_sets_active_and_date() -> None:
    placement = make()
    placement.activate(True, [], datetime(2027, 1, 14, tzinfo=UTC))
    assert placement.status == PlacementStatus.ACTIVE
    assert placement.activated_at is not None


def test_active_cannot_be_reached_by_other_commands() -> None:
    with pytest.raises(IllegalTransition):
        make().apply("activate")


def test_cannot_close_directly_from_pending_activation() -> None:
    with pytest.raises(IllegalTransition):
        make().apply("close")


def test_start_date_only_after_activation() -> None:
    with pytest.raises(IllegalTransition):
        make().register_start(datetime(2027, 1, 15).date())


def test_interrupted_closure_allowed_from_on_hold() -> None:
    placement = make(PlacementStatus.ON_HOLD)
    assert placement.apply("close_interrupted") == PlacementStatus.CLOSED
