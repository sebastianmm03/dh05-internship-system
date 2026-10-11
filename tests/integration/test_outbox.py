"""QS-06: a failed notification never undoes the activation."""

from horizon.modules.notifications.outbox import OutboxMessageModel, deliver_pending
from horizon.modules.placements.repository import PlacementModel
from tests.conftest import as_user
from tests.integration.test_activation_endpoint import add_ready_placement


class BrokenChannel:
    def send(self, message) -> None:
        raise ConnectionError("simulated channel down")


class WorkingChannel:
    def __init__(self) -> None:
        self.sent = []

    def send(self, message) -> None:
        self.sent.append(message.recipient_id)


def test_failed_delivery_keeps_activation_and_retries(client, session) -> None:
    add_ready_placement(session)
    client.post("/placements/PLC-9001/activation", headers=as_user("EXP-COORD-001"))

    summary = deliver_pending(session, BrokenChannel())

    assert summary["retry"] == 3
    assert session.get(PlacementModel, "PLC-9001").status == "ACTIVE"
    assert all(m.status == "PENDING" and m.attempts == 1 for m in session.query(OutboxMessageModel))

    channel = WorkingChannel()
    assert deliver_pending(session, channel)["sent"] == 3
    assert "HU-STU-5002" in channel.sent
