# ADR-002 - One relational database with module-owned tables and transactional commands

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-01, AD-03

## Context

The activation command must read readiness, approvals and supervisors and change the status atomically, and the audit entry must never be lost when a change happens.

## Decision

Use one relational database (SQLite in local development, PostgreSQL in the shared environment through docker-compose). Each table belongs to exactly one module; other modules never query it directly. Each command runs in one transaction that includes the state change, the audit entry and the outbox message.

## Alternatives

One database per module: rejected because the gate needs state, audit and outbox in one local transaction. A document database: rejected because the data is relational (placements, conditions, supervisors) and integrity rules are easier to keep with transactions and keys.

## Rationale

Strong consistency with no distributed transaction. SQLite keeps the starter runnable; PostgreSQL is already prepared in the starter docker-compose.

## Consequences

Table ownership must be respected by convention and review. Reports read through read-only queries owned by the Reporting module.

## Verification

test_failure_in_the_middle_rolls_everything_back; test_two_concurrent_activations_only_one_commits. PostgreSQL run: NOT EXECUTED (TP-14).

## Reconsideration / supersession

If a module is extracted as a service (ADR-001 triggers).

## Trace links

AD-01, AD-03; QS-04, QS-09; INV-04, INV-05; V-02
