# ADR-009 - Do not adopt microservices, service mesh, serverless, low-code or RAG in this release

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-01 to AD-05, C-01, C-05

## Context

The course presented several technologies. Each was run through the decision filter: problem, driver, simpler alternative, benefit, cost, evidence.

## Decision

Not adopted now: microservices, service mesh, external broker, serverless functions, low-code platform, RAG assistant. Adopted instead: modular monolith, outbox, a worker process (run on demand today; scheduled reminders designed), custom UI over the API, rule text shown in the UI.

## Alternatives

Adopt any of them now.

## Rationale

None solves a problem that our drivers define, and each adds cost the team cannot absorb (C-01). AI may not decide eligibility or select candidates (RFP section 10, C-05).

## Consequences

We record the triggers under which each option becomes justified (Decision Filter sheet), so the decision can evolve with evidence.

## Verification

Not a testable decision; reviewed against the decision filter. Revisit triggers recorded in ADR-001.

## Reconsideration / supersession

Triggers listed in ADR-001 and in the Decision Filter sheet.

## Trace links

AD-01..AD-05; C-01, C-05; Decision Filter
