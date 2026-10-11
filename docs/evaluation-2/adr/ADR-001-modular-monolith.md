# ADR-001 - Use a modular monolith as architectural style

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-01, AD-02, AD-03, AD-05, C-01, C-03

## Context

Eleven modules (M-01 to M-11) share one placement lifecycle. The most important driver (AD-01) needs the readiness conditions, the approvals and the placement status to be consistent at the moment of activation. Expected load is small (F-22). The team has three people and one semester.

## Decision

Build one deployable backend application organized in business modules with explicit public interfaces. Modules own their data and may only call other modules through those interfaces or react to their domain events. The same artifact runs as API process and as worker process (outbox and reminders).

## Alternatives

Layered monolith: gives the local transaction but does not stop every layer from talking to every other, so module boundaries decay. Microservices: would turn the activation gate into a distributed transaction or saga for 600-900 placements a year and a team of three. Low-code platform: does not fit relationship-based access, versioned rules or the simulated service contracts. Full comparison in the Alternatives sheet.

## Rationale

Local transactions protect the gates and the audit history. Module boundaries prevent the 'everything talks to everything' decay and let each team member own modules. One pipeline and one database fit C-01 and C-03.

## Consequences

Everything scales together, which is acceptable at this load. Module boundaries are a discipline: we enforce them with the dependency rules of the Module Design sheet and with an automated architecture test that reads the imports of the code and fails the test suite when a module reaches into another one outside the allowed table.

## Verification

tests/architecture/test_module_boundaries.py fails when a module imports another one outside the allowed table; one runnable artifact (API + worker).

## Reconsideration / supersession

Independent teams take ownership of modules; notification or reporting volume degrades the core; a module needs a different release cadence; a failure in one module must be isolated at runtime.

## Trace links

AD-01, AD-02, AD-03, AD-05; V-02, V-03; QS-08; TP-08
