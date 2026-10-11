# Test plan

| ID | Level | Intent | Covers | How | Status |
|---|---|---|---|---|---|
| TP-01 | Unit | Lifecycle transition table and guards | BR-01, BR-03, INV-01..03 | tests/unit/test_placement_lifecycle.py (6 tests) | VERIFIED |
| TP-02 | Unit | Rule evaluators and configuration-only rule change | BR-01, BR-08, QS-07 | tests/unit/test_readiness_rules.py (5 tests) | VERIFIED |
| TP-03 | Unit | Adapters translate payloads and failures; program aliases | AD-05, QS-05 | tests/unit/test_reference_and_adapters.py (7 cases) | VERIFIED |
| TP-04 | Integration | Activation slice end to end through the API | QS-08, BR-01, BR-02 | tests/integration/test_activation_endpoint.py (8 tests) | VERIFIED |
| TP-05 | Integration | Concurrency, atomicity, repetition, correlation, machine-readable codes | QS-09, QS-04, BR-12, INV-04, INV-05, INV-07 | tests/integration/test_concurrency_and_atomicity.py (5 tests) | VERIFIED |
| TP-06 | Integration | Outbox: failed channel, retry, crash, payload content | QS-06, BR-11 | test_outbox.py (1) + test_traceability_evidence.py (3: payload, crash, FAILED after 5) | VERIFIED |
| TP-07 | Integration | Access: unrelated user, wrong role, supervisor relationship, projection | QS-02, QS-01 (partial), BR-09, BR-10 | activation tests + test_traceability_evidence.py (401, 403 host organization, student projection; workplace supervisor at policy level, EU-05) | VERIFIED (slice only) |
| TP-08 | Architecture | Dependency rules, purity of domain, mocks only through M-11, audit append-only | ADR-001, ADR-007, ADR-006 | tests/architecture/test_module_boundaries.py (5 tests) | VERIFIED |
| TP-09 | Data | Seed keeps raw files intact and loads every placement | EU-03, INV-08 | test_traceability_evidence.py (2 tests); scripts/validate_data.py (run locally) | VERIFIED |
| TP-10 | Mutation check | Do the tests detect real defects? Six defects were injected one at a time into a copy of the code (no conditional update, directory failure lets the gate pass, projection leaks evidence, student may activate, forbidden import, worker commits once per run) and each made at least one test fail | Test quality | docs/evaluation-2/validation/mutation_check.py and mutation_output.txt | EXECUTED (6 of 6 detected); script is repeatable, not part of CI |
| TP-11 | Contract | Mock service contracts against the adapters | ADR-007 | Adapter tests use the real mock classes and failure ids; no consumer-driven contract tool | PARTIAL |
| TP-12 | Acceptance | Eligibility, employer decision, academic approval, hours, evaluation, closure scenarios | QS-01, QS-03, QS-05, BR-05, BR-06 | Planned with the modules of Evaluation 3 | NOT EXECUTED - modules not built |
| TP-13 | Non-functional | Load at the seasonal peak (QS performance is a non-driver) | DA-01 | Not planned unless DA-01 is contradicted | NOT EXECUTED - by decision |
| TP-14 | Environment | Same suite against PostgreSQL; true parallel concurrency | DA-03, QS-09 | Run docker-compose profile with two real connections | NOT EXECUTED - no PostgreSQL in the authoring environment |
| TP-15 | Security | Authentication, rate limiting, dependency scan | T-01, T-10 | Needs real authentication first | NOT EXECUTED - not designed |

## What the tests do not prove

- The concurrency test interleaves two sessions deterministically on SQLite. It proves the conditional update logic, not behavior under true parallel load on PostgreSQL (TP-14).
- The rollback test proves that nothing is committed when a handler fails; it does not distinguish an explicit rollback from the session being discarded.
- The outbox is at-least-once towards the channel; a crash between send and commit can repeat one message.
- Only the activation slice exists in code (M-03, M-04, M-06, M-07, M-08, M-09, M-11). The four business modules M-01, M-02, M-05 and M-10, the closure gate and the web client are designed, not implemented or tested.
- No performance, security-scanning or accessibility testing has been run.
- The CI workflow (.github/workflows/ci.yml) exists but has not run on a remote, and no pull-request review was exercised: the team worked on one local repository.
- The architecture test reads import statements only. It does not see dynamic imports, imports made inside the routers (api.py, the composition points) or coupling through shared database tables.
- QS-02 with a real workplace-supervisor identity is verified at policy level only, because the identity mock has none (EU-05).
