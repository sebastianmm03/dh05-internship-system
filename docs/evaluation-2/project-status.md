# Project status: risks, backlog, plan

## Status

| Concern | Design | Implementation | Validation |
|---|---|---|---|
| Activation gate, access, audit, outbox (slice) | Documented | Implemented | Verified (59 tests, 6/6 mutations) |
| Concurrency (conditional update) | ADR-010, SEQ-04 | Implemented | Verified on SQLite; PostgreSQL not executed |
| Module boundaries | V-03, V-DEV, dependency rules | Enforced by test | Verified |
| Opportunities, applications, eligibility | Modules, rules, contracts | Not implemented | Not executed |
| Hours, evaluations, incidents, closure gate | Modules, transitions, BR-06 | Not implemented | Not executed |
| Web client and UX | V-UX-01, V-UX-02 | Not implemented | Not executed |
| Pilot deployment, real identity, rate limits | V-05 target, T-01, T-10 | Not implemented | Not executed |

## Architecture risks

| ID | Risk | P | I | Mitigation / trigger | Owner role | Status |
|---|---|---|---|---|---|---|
| AR-01 | A module imports another module's internals and the boundaries decay. | M | H | Architecture test fails the test suite (and the CI build on GitHub); keep ALLOWED table in sync with the Module Design. | Architecture owner | Mitigated (TP-08) |
| AR-02 | The mock identity header reaches a real pilot as the only authentication. | M | H | No pilot before IdentityAdapter is replaced; decide with IT Services (identity integration is still an open question). | Architecture owner | Open |
| AR-03 | Readiness matrix (CL-020) differs from our union of observed conditions. | H | M | Rules are configuration; replace file and version. Ask the Legal Representative. | Backend owner | Open (EU-02) |
| AR-04 | PostgreSQL behaves differently from SQLite for conditional update or JSON columns. | L | M | Run the suite on PostgreSQL before Evaluation 3 (TP-14). | Quality owner | Open |
| AR-05 | Audit rows altered directly in the database. | L | H | Restrict database permissions in the shared environment; consider hash chaining only if an audit requires it. | Architecture owner | Open |
| AR-06 | No rate limiting or abuse protection. | L | L | Accepted at this load (DA-01); revisit with a real pilot. | Backend owner | Accepted |
| AR-07 | Team overload: four business modules (M-01, M-02, M-05, M-10), the closure gate and the web client remain for Evaluation 3. | H | H | Vertical slices in the order BL-01 to BL-05; stop adding scope. | Team | Open |
| AR-08 | CL-018 stays open and the access policy for restricted fields is wrong. | M | H | Deny by default; the policy lives in one module. | Backend owner | Open |

## Backlog

| ID | Item | Why now | Depends on | Stories | Owner role |
|---|---|---|---|---|---|
| BL-01 | Applications and eligibility slice (M-02 + M-06 rules + StudentInformationAdapter in use) | Second most important rule set; uses the SIS failure policy (QS-05) | - | US-005, US-007 | Backend owner |
| BL-02 | Academic approval and work plan versions; events complete readiness conditions | Feeds the gate with real data instead of seeded rows | BL-01 | US-010, US-011 | Backend owner |
| BL-03 | Hours in three levels and review | Next highest-risk data (disputes) | BL-02 | US-017, US-018, US-019 | Backend owner |
| BL-04 | Evaluations, incidents and restricted projections | QS-03; closes the privacy scenarios | BL-03 | US-020, US-022 | Backend owner |
| BL-05 | Closure gate and CompletionEvidencePort | BR-06 | BL-03, BL-04 | US-024, US-025 | Backend owner |
| BL-06 | Negative tests for invalid rule configuration and directory 404/409 on the activation path; a workplace-supervisor fixture identity for QS-02 end to end | Closes FM-03, FM-04, FM-14, EU-05 | - | - | Quality owner |
| BL-07 | Rule publication: who may change a rule version and how it is reviewed | T-06; CL-004, CL-020 | Client answer | - | Architecture owner |
| BL-08 | API versioning convention and error format ADR | Contract stability | - | - | Architecture owner |
| BL-09 | Run suite on PostgreSQL with parallel connections | TP-14, AR-04 | - | - | Quality owner |
| BL-10 | Web client technology decision | Evaluation 3 UI | BL-01 | - | Team |
| BL-11 | Add eventId and schemaVersion to domain events | Event contract before any extraction | - | - | Architecture owner |
| BL-12 | Outbox archive and retention policy | Data lifecycle | - | US-030 | Backend owner |
| BL-13 | Versioned schema migrations | create_all cannot change an existing schema | BL-09 | - | Backend owner |

## Plan

| When | Work | Responsible |
|---|---|---|
| By 2026-10-11 (Evaluation 2 delivery) | Submit the Evaluation 2 package (architecture document, ADRs, workbook and repository). Every member rehearses the trace of one requirement in both directions. | Sebastián Mercado, Juan Arbeláez, Cher Jiménez |
| 2026-10-12 to 2026-10-21 | Evaluation 3, first iteration: BL-01 applications and eligibility; BL-06 negative tests; BL-08 error format ADR; BL-09 suite on PostgreSQL. | Juan Arbeláez (backend), Cher Jiménez (quality), Sebastián Mercado (BL-08) |
| 2026-10-22 to 2026-10-31 | Evaluation 3, second iteration: BL-02 approvals and work plans; BL-03 hours; BL-10 web client decision. | Juan Arbeláez; team for BL-10, led by Sebastián Mercado |
| 2026-11-01 to 2026-11-08 | Evaluation 3, third iteration: BL-04 evaluations and incidents; BL-05 closure gate; demo of one placement end to end; update ADRs and views. | Juan Arbeláez, Cher Jiménez, Sebastián Mercado |
| 2026-11-08 (Evaluation 3) | Next architecture review point: does the structure survive execution? Every change goes to a new or superseding ADR. | Sebastián Mercado (architecture owner) |
| 2026-11-29 (Evaluation 4) | Final delivery: remaining backlog items, final evidence and project finished. | Sebastián Mercado, Juan Arbeláez, Cher Jiménez |

## Open questions

| CL | Unknown | How the design stays safe | ADR |
|---|---|---|---|
| CL-008 | Who may authorize an activation with a missing condition | The gate supports an exception only as a separate, audited command; not implemented until the role is confirmed. | ADR-003 |
| CL-017 | Who resolves disputed hours | The resolving role is a configuration value (default: experiential-learning coordinator, US-019). | ADR-004 |
| CL-018 | Who may read restricted comments and sensitive incidents | Deny by default except the office, the faculty supervisor of the placement and the author of the content (a workplace supervisor reads their own comments); policy lives only in M-07. | ADR-005 |
| CL-020 | Mandatory readiness conditions per placement type | Initial configuration from observed data (EU-02), versioned, replaceable without code. | ADR-004 |
| CL-004 | Exact eligibility rules per program | Rule types derived from eligibility_reviews.csv; parameters per program in configuration. | ADR-004 |
| CL-016 | Whether the reflection is mandatory to close | Completion requirement configurable per program. | ADR-004 |
| CL-001 | Placement types in the first release (ten defined, five used by opportunities, three by placements) | Placement types are reference data; rules are configured per type; the demo uses the types present in the scenarios. | ADR-004 |

Owners: architecture owner Sebastián Mercado, backend owner Juan Arbeláez, quality owner Cher Jiménez.
