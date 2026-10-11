# Interfaces

## POST /placements/{placement_id}/activation

| Field | Value |
|---|---|
| Stories | US-014, US-016 |
| Caller | Experiential-learning coordinator (staff role EXPERIENTIAL_LEARNING_COORDINATOR) |
| Request | Header X-Mock-User-Id (required in development). No body. |
| Idempotency | Not idempotent by design: a second call after success returns 409 ILLEGAL_TRANSITION and adds no side effects (FM-10). |
| Versioning | No version prefix yet; breaking changes require a new ADR (BL-08). |

| Status | Body | Meaning |
|---|---|---|
| 200 | {placement_id, status: 'ACTIVE', rule_version, correlation_id} | Gate passed; state, audit and outbox committed. |
| 401 | {detail} | Header missing, user unknown or inactive. |
| 403 | {detail} | User related to the placement but not allowed to activate. Audited. |
| 404 | {detail} | Placement does not exist OR user has no relationship (indistinguishable). Audited only when the placement exists. |
| 409 | {code: ACTIVATION_BLOCKED, detail, blocking: [{requirement, check_id, reason}], correlation_id} | At least one rule blocks. Audited as ACTIVATION_REFUSED. |
| 409 | {code: STATE_CHANGED, detail} | Another command changed the placement first. Read it again. |
| 409 | {code: ILLEGAL_TRANSITION, detail} | Placement is not in PENDING_ACTIVATION. |
| 503 | {detail} | Identity provider disabled. |

## GET /placements/{placement_id}/readiness

| Field | Value |
|---|---|
| Stories | US-012 |
| Caller | Office, faculty supervisor, workplace supervisor, student, host organization (related users only) |
| Request | Header X-Mock-User-Id. |
| Idempotency | Safe read; the gate is evaluated at read time, so the result can change between calls. |
| Versioning | As above. |

| Status | Body | Meaning |
|---|---|---|
| 200 | {placement_id, status, audience, rule_version, ready, blocking[], conditions[{check_id, requirement_type, status, evidence_reference}]} | evidence_reference is null for RESTRICTED requirements outside the office. |
| 401 | {detail} | As above. |
| 404 | {detail} | Not found or no relationship. Denial audited when the placement exists. |
| 503 | {detail} | Identity provider disabled. |

## Errors

| Status | Code | Meaning | Recovery |
|---|---|---|---|
| 401 | - | Header missing, user unknown or inactive | Sign in again; do not retry automatically. |
| 403 | - | Related to the placement but not allowed to act | Do not retry; ask the office. |
| 404 | - | Placement missing or no relationship (indistinguishable on purpose) | Check the identifier; no retry. |
| 409 | ACTIVATION_BLOCKED | At least one rule blocks; the list is in the body | Complete the named conditions, then activate again. |
| 409 | STATE_CHANGED | Another command changed the placement first | Read the placement again; do not resend blindly. |
| 409 | ILLEGAL_TRANSITION | The placement is not in PENDING_ACTIVATION | Read the current status; nothing to do if already ACTIVE. |
| 503 | - | Identity provider disabled | Retry after the identity service is configured. |

## Event as published today

```json
{
  "name": "PlacementActivated",
  "occurred_at": "2026-09-24T14:05:00Z",
  "payload": {
    "placement_id": "PLC-9001",
    "student_id": "HU-STU-5002",
    "workplace_supervisor_id": "SUP-EXT-002",
    "faculty_supervisor_id": "FAC-SUP-101",
    "correlation_id": "<uuid hex, one per command>"
  }
}
```

The current event has no schema version and no event id. It never leaves the process, so this is acceptable today; before a module is extracted or an external consumer appears, add eventId and schemaVersion (BL-11).

## Event and outbox contracts

| Contract | Owner | Content | Guarantees |
|---|---|---|---|
| PlacementActivated | M-03 | payload: placement_id, student_id, workplace_supervisor_id, faculty_supervisor_id, correlation_id | Handlers run inside the command's transaction and may only write local rows. Order of handlers is not guaranteed. Delivery is in-process and at-most-once: a crash before commit means the event never happened. |
| Outbox message | M-09 | event_name, recipient_id, payload {placement_id, template}, status PENDING/SENT/FAILED, attempts, correlation_id | At-least-once towards the channel: a crash between send and commit may repeat one message; the receiver must tolerate a duplicate (documented limitation). |

## Ports

| Port | Failure contract |
|---|---|
| EmployerDirectoryPort.agreement(organization_id) -> AgreementSummary | Raises ExternalServiceUnavailable (503), ExternalDataConflict (409), ExternalRecordNotFound (404). Implemented by EmployerDirectoryAdapter (M-11). |
| StudentInformationPort.profile(student_id) -> StudentProfile | Same three exceptions. Carries read_at. Implemented by StudentInformationAdapter (M-11). |
| IdentityPort.resolve(user_id) -> Identity / None | None for unknown users. Implemented by IdentityAdapter reading mock_identities.json. |

## Planned endpoints

| Operation | Module | Caller | Stories |
|---|---|---|---|
| POST /opportunities | M-01 | Host organization contact | US-002 |
| POST /opportunities/{id}/review | M-01 | Experiential-learning coordinator | US-003 |
| GET /opportunities?program= | M-01 | Student | US-004 |
| POST /applications | M-02 | Student | US-005, US-007 |
| POST /applications/{id}/employer-decision | M-02 | Host organization contact | US-009 |
| POST /applications/{id}/academic-approval | M-02 | Academic program coordinator | US-011 |
| POST /placements/{id}/work-plans | M-03 | Academic program coordinator | US-010, US-021 |
| GET /placements/{id}/readiness | M-04 | Related users only: office, faculty supervisor, workplace supervisor, student, host organization (projection) | US-012 |
| POST /placements/{id}/activation | M-03 | Experiential-learning coordinator | US-014, US-016 |
| POST /placements/{id}/hours | M-05 | Student | US-017 |
| POST /hours/{id}/review | M-05 | Workplace supervisor | US-018 |
| POST /placements/{id}/closure | M-03 | Experiential-learning coordinator | US-025 |
| GET /placements/{id}/history | M-08 | Office, auditor | US-026 |
