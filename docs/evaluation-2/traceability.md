# Traceability

## Requirement to tests

| Requirement | Rules | Drivers / ADRs | Design | Tests |
|---|---|---|---|---|
| CAP-04 Readiness gate | BR-01, BR-02, BR-03, BR-04, BR-12 | AD-01, AD-05; ADR-003, ADR-004, ADR-007, ADR-010 | V-04, V-TXN, SEQ-01..04, lifecycle; ActivatePlacement, ReadinessGate | TP-01, TP-02, TP-04, TP-05 |
| US-027, US-028 Access | BR-09, BR-10 | AD-02; ADR-005 | V-03, access matrix, threats T-02, T-03, T-08; AccessPolicy | TP-07 |
| CAP-06 History | BR-07, BR-08 | AD-03; ADR-006, ADR-010 | V-DATA, V-STATUS; AuditRecorder | TP-05, TP-08 (append-only), test_qs04_* |
| US-030 Notifications | BR-11 | AD-05; ADR-008 | SEQ-05, V-02; outbox, worker | TP-06 |
| CAP-02 Eligibility | BR-08 | AD-04, AD-05; ADR-004, ADR-007 | M-02, M-06, StudentInformationPort | TP-03 (adapter); TP-12 NOT EXECUTED |
| CAP-03 Three approvals | BR-05 | AD-03; ADR-006 | M-02, V-DOM | TP-12 NOT EXECUTED |
| CAP-05 Verified hours | BR-06 | AD-03, AD-04; ADR-004, ADR-006 | M-05, V-DOM | TP-12 NOT EXECUTED |
| CAP-06 Closure | BR-06 | AD-01; ADR-003 | lifecycle, closure gate | TP-12 NOT EXECUTED |
| CAP-01 Publication | - | ADR-001, ADR-006 | M-01 | TP-12 NOT EXECUTED |

## Driver to verification

| Driver | Scenarios | QR | Evidence | ADRs | Modules | Patterns | Views | Verification |
|---|---|---|---|---|---|---|---|---|
| AD-01 | QS-08, QS-09 | RFP s.7 constraint | OB-07, OB-11, ASM-006, R-002, R-007 | ADR-001, ADR-002, ADR-003, ADR-010 | M-03, M-04, M-05 | Facade (P-06) | V-03, V-04 | SC-05, SC-12; test_activation_endpoint.py (test_sc01_*, test_sc02_*, test_directory_down_*); test_concurrency_and_atomicity.py |
| AD-02 | QS-01, QS-02, QS-03 | QR-01, QR-02 | CL-009, CL-018, ASM-007, R-003, R-004 | ADR-005 | M-07 (used by all) | - | V-03 | SC-07, SC-08, SC-09; test_student_cannot_activate_*, test_unrelated_user_*, test_host_organization_sees_*, test_qs02_* |
| AD-03 | QS-04, QS-09 | QR-03 | OB-12, F-02, CL-019 | ADR-002, ADR-006, ADR-010 | M-08 (used by all) | - | V-03, V-04 | SC-10; audit assertions in test_activation_endpoint.py; test_one_correlation_id_*; test_qs04_* |
| AD-04 | QS-07 | QR-05 | F-24, CL-004, CL-020, ASM-004, R-001, EU-01, EU-02 | ADR-004 | M-06 | Strategy (P-01), Factory Method (P-02) | V-03, V-04 | SC-03, SC-05; tests/unit/test_readiness_rules.py::test_rule_change_is_configuration_only |
| AD-05 | QS-05, QS-06, QS-08 | QR-04 | F-17, F-18, ASM-002, ASM-003, ASM-009, R-005 | ADR-007, ADR-008 | M-09, M-11 | Adapter (P-03), Observer (P-04) | V-01, V-02, V-04 | SC-11; tests/unit/test_reference_and_adapters.py, tests/integration/test_outbox.py, test_qs06_* |

## Stories

| Story | Module | Driver | ADR | Component | SC |
|---|---|---|---|---|---|
| US-001 | M-01 | - | ADR-001 | OpportunityService | SC-01 |
| US-002 | M-01 | AD-04 | ADR-004 | OpportunityService | SC-01 |
| US-003 | M-01 | AD-03 | ADR-006 | OpportunityService, audit | SC-01 |
| US-004 | M-01 | AD-02 | ADR-005 | Search + projection | SC-02 |
| US-005 | M-02 | AD-05 | ADR-007 | ApplicationService | SC-02 |
| US-006 | M-02 | - | ADR-001 | ApplicationService | SC-02 |
| US-007 | M-02, M-06 | AD-04, AD-05 | ADR-004, ADR-007 | Strategy (P-01), Adapter (P-03) | SC-03 |
| US-008 | M-02 | AD-02 | ADR-005 | Projection | SC-02 |
| US-009 | M-02 | AD-03 | ADR-006 | ApplicationService, events | SC-04 |
| US-010 | M-03 | AD-03 | ADR-006 | WorkPlan versions | SC-04 |
| US-011 | M-02 | AD-01 | ADR-003 | Three decision records | SC-04 |
| US-012 | M-04, M-06 | AD-04 | ADR-004 | Readiness checklist, Strategy | SC-05 |
| US-013 | M-04 | AD-03 | ADR-006 | Evidence references | SC-05 |
| US-014 | M-03, M-04 | AD-01, AD-05 | ADR-003, ADR-007 | ActivationGate, EmployerDirectoryPort | SC-05 |
| US-015 | M-03 | AD-02, AD-03 | ADR-005, ADR-006 | Supervisor assignment (relationships) | SC-05 |
| US-016 | M-03 | AD-01 | ADR-003 | Lifecycle transition table | SC-05 |
| US-017 | M-05 | AD-03 | ADR-006 | HourEntry | SC-06 |
| US-018 | M-05 | AD-03 | ADR-006 | Hour review records | SC-06 |
| US-019 | M-05 | AD-03 | ADR-006 | Dispute resolution | SC-06 |
| US-020 | M-05, M-07 | AD-02 | ADR-005 | Incident visibility | SC-09 |
| US-021 | M-03 | AD-03 | ADR-006 | WorkPlan versions | SC-10 |
| US-022 | M-05, M-07 | AD-02 | ADR-005 | Evaluation projections | SC-07 |
| US-023 | M-05 | - | ADR-001 | Reflection record | SC-07 |
| US-024 | M-05, M-06 | AD-01, AD-04 | ADR-003, ADR-004 | Closure gate, Strategy | SC-12 |
| US-025 | M-03 | AD-01 | ADR-003 | Lifecycle transition table | SC-12 |
| US-026 | M-08 | AD-03 | ADR-006 | Append-only audit | SC-10 |
| US-027 | M-07, M-11 | AD-02, AD-05 | ADR-005, ADR-007 | IdentityAdapter | SC-11 |
| US-028 | M-07 | AD-02 | ADR-005 | Access policy + projections | SC-08, SC-09 |
| US-029 | M-10 | - | ADR-002 | Read-only queries | SC-02 |
| US-030 | M-09 | AD-05 | ADR-008 | Observer (P-04), outbox | SC-11 |

## Reverse traces

**Start from the worker (C-WORKER).** It exists because a failed notification must never cancel an activation (US-030, BR-11, QR-04, QS-06). ADR-008 chose a transactional outbox. The worker reads PENDING rows from C-DB, calls the channel and commits per message without ever touching a placement. It appears in V-02, V-05 and SEQ-05, and TP-06 challenges it. A worker without the outbox table or without the crash test would be a broken reverse trace.

**Start from the conditional update in SqlPlacementRepository.save.** It exists because two coordinators can act on the same placement (QS-09, BR-12). ADR-010 chose it over row locks. It is not an authorization mechanism and does not replace the gate; it only guarantees one winner. SEQ-04 shows it and test_two_concurrent_activations_only_one_commits verifies it on SQLite.
