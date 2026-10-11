from typing import Any

PREFERRED_IDENTIFIER_FIELDS = (
    "record_id",
    "request_id",
    "case_id",
    "work_order_id",
    "proposal_id",
    "project_id",
    "application_id",
    "placement_id",
    "event_id",
    "student_id",
    "user_id",
    "id",
)


def extract_identifier(payload: dict[str, Any]) -> str | None:
    for field_name in PREFERRED_IDENTIFIER_FIELDS:
        value = payload.get(field_name)
        if value not in (None, ""):
            return str(value)

    for field_name, value in payload.items():
        if field_name.lower().endswith("_id") and value not in (None, ""):
            return str(value)
    return None
