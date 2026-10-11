# ADR-010 - Concurrent commands: conditional update on status and a correlation id per command

**Status:** Selected  
**Date and owner:** 2026-10-05, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-01, AD-03

## Context

Review of the first slice found a hole: two coordinators can read the same PENDING_ACTIVATION placement, both pass the gate and both write ACTIVE, leaving two success audit entries and two sets of notifications. ADR-002 gives a transaction, but a transaction alone does not stop a lost update. Also, the audit entry, the event and the outbox messages of one command had no common identifier, so QS-04 (reconstruct a decision) was harder than it should be.

## Decision

The repository saves a placement with an UPDATE ... WHERE status = <status that was read>. If no row changes, it raises StaleState and the command rolls back; the API answers 409 with code STATE_CHANGED. Every command generates one correlation id, written to its audit entries, carried by the domain event and copied to the outbox messages and to the API response. Error responses carry a machine-readable code (ACTIVATION_BLOCKED, STATE_CHANGED, ILLEGAL_TRANSITION).

## Alternatives

Pessimistic row lock (SELECT ... FOR UPDATE: not supported by SQLite and needs more care with the gate's external call); version column (optimistic locking with a counter: heavier schema change for the same effect here); a unique constraint on 'activation' records; do nothing and rely on the low load.

## Rationale

Conditional update on the status that the command already depends on needs no new column, is supported by both SQLite and PostgreSQL (tested on SQLite only, TP-14), and makes the lost update impossible instead of unlikely. The rule 'activate only from PENDING_ACTIVATION' already existed; this makes the database enforce it at write time.

## Consequences

Callers must handle 409 STATE_CHANGED. The gate's external call happens before the write, so the loser may have called the directory for nothing: acceptable. The same pattern must be reused by every status-changing command (hold, resume, complete, close). We tested it with a deterministic interleaving on SQLite, not with parallel connections on PostgreSQL (TP-14).

## Verification

test_two_concurrent_activations_only_one_commits; test_one_correlation_id_links_audit_entry_and_notifications; test_refusal_and_denial_carry_machine_readable_codes. Parallel PostgreSQL run: NOT EXECUTED.

## Reconsideration / supersession

If a command needs to change more than the status atomically (then use a version column), or if contention becomes frequent.

## Trace links

AD-01, AD-03; QS-09; BR-12; INV-04, INV-07; FM-08; T-09; SEQ-04
