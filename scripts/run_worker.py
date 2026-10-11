"""Worker process (same codebase): delivers pending outbox messages once (ADR-008).

Run it on a schedule or in a loop. The simulated channel only prints the message.
"""

import horizon.main  # noqa: F401
from horizon.infrastructure.database import SessionLocal, create_database_schema
from horizon.modules.notifications.outbox import deliver_pending


class PrintSender:
    def send(self, message) -> None:
        print(
            f"[notification] to={message.recipient_id} event={message.event_name} "
            f"payload={message.payload}"
        )


def main() -> int:
    create_database_schema()
    with SessionLocal() as session:
        print(deliver_pending(session, PrintSender()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
