# ADR-006 - Append-only audit history and versioned records

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-03, QR-03

## Context

Hours are disputed (HOUR-002), work plans are revised (WP-001 is v2) and decisions must be reconstructed (OB-12). Editing records in place loses the previous value.

## Decision

An Audit History module stores one entry per state-changing command: entry id, time, actor, action, resource, previous value, new value, reason and correlation id. Entries are written by the command in the same transaction and there is no update or delete operation. Work plans, eligibility decisions, hour reviews and readiness evidence are new records or versions linked to the previous one.

## Alternatives

Database triggers; logging to files; full event sourcing.

## Rationale

Explicit entries written by the application carry the business reason and the actor, which triggers do not know. Event sourcing would solve the same problem at a much higher complexity for this team.

## Consequences

Storage grows with every change, which is small at this volume. Reports of history are queries on one table. The application exposes no update or delete, but a database administrator could still alter rows: this is recorded as risk AR-05. One correlation id links the entries of a command (ADR-010).

## Verification

test_audit_history_can_only_be_appended_and_read; audit assertions in activation tests; test_one_correlation_id_links_audit_entry_and_notifications.

## Reconsideration / supersession

If an external audit store or legal retention policy is required.

## Trace links

AD-03; QS-04; BR-07; INV-06, INV-07; T-05, T-07
