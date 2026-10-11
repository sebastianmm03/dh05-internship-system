# ADR-008 - In-process domain events with a transactional outbox for side effects

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-05, QR-04, AD-03

## Context

One decision triggers several reactions: an activation must notify the student and both supervisors, update reminders and feed reports; an academic approval completes a readiness condition. A failed notification must never cancel the decision (ASM-009).

## Decision

Modules publish domain events (for example AcademicApprovalRecorded, WorkPlanApproved, PlacementActivated, HoursReviewed, PlacementClosed) through an in-process dispatcher (Observer). Handlers that change business data run in the same transaction. Handlers with external side effects (notifications; reminders are DESIGNED) only write to an outbox table; the worker process delivers them and retries failures.

## Alternatives

Call every reaction directly from the service; external message broker; serverless functions.

## Rationale

The service only announces what happened (open/closed), and side effects are isolated from the transaction. The outbox gives reliability without new infrastructure.

## Consequences

Delivery of notifications is eventual. The team must keep the event catalog (Interfaces sheet) up to date.

## Verification

tests/integration/test_outbox.py; test_qs06_worker_crash_*; test_qs06_outbox_payload_*.

## Reconsideration / supersession

If a module is extracted as a service, the same events move to a broker (ADR-001 triggers).

## Trace links

AD-05; QS-06; BR-11; FM-11, FM-12; T-04
