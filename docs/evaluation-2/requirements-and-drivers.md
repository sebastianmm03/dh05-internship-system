# Requirements, rules and drivers

## Significant requirements

| ID | Requirement | Stories | Significance | Status |
|---|---|---|---|---|
| CAP-01 | Controlled publication with four review results | US-001..US-004 | Opportunity lifecycle owned by M-01; review result audited. | DESIGNED |
| CAP-02 | Eligibility checked at application time | US-005..US-008 | Versioned rules (M-06) plus Student Information port with fail-soft policy (QS-05). | DESIGNED |
| CAP-03 | Three approvals kept apart | US-009..US-011 | Three separate fields and events; none implies another (BR-05). | DESIGNED |
| CAP-04 | Readiness gate before activation | US-012..US-016 | Gate + transition table + conditional update in one transaction (AD-01). | VERIFIED (slice) |
| CAP-05 | Verified hours and evidence | US-017..US-021 | Three levels of hours in M-05; dispute role configurable (CL-017). | DESIGNED |
| CAP-06 | Evidence-based closure and history | US-022..US-026 | Closure gate (BR-06) and append-only audit (ADR-006). | Audit VERIFIED; closure DESIGNED |
| US-027, US-028 | Identity and relationship-based access | US-027, US-028 | One access module, audience projections, deny by default (ADR-005). | VERIFIED (slice) |
| US-030 | Notifications that never undo a decision | US-030 | Transactional outbox and worker (ADR-008). | VERIFIED |

## Business rules

| ID | Rule | Source | Enforced in | Verification |
|---|---|---|---|---|
| BR-01 | A placement becomes ACTIVE only when every required readiness condition is COMPLETE and not expired, the agreement is valid in the Employer Directory, and both supervisors are assigned. | RFP section 7; OB-07; ASM-006; R-002 | M-03 + M-04 (ADR-003) | test_sc01_*, test_sc02_*, test_ready_placement_is_activated_*, tests/unit/test_readiness_rules.py |
| BR-02 | If the agreement cannot be verified because the directory fails, the activation is refused (fail closed). | ASM-003; R-005; QS-08 | M-04 AgreementValidInDirectory (ADR-007) | test_directory_down_means_activation_refused, test_directory_unavailable_keeps_gate_closed |
| BR-03 | Activation and the real start date are different facts: the start date is recorded after activation and is not a status. | OB-07 | M-03 Placement.register_start (ADR-003) | test_start_date_only_after_activation |
| BR-04 | 'Blocked' is not a lifecycle state; it is the result of evaluating the gate. | EU-03; R-008 | M-03 transition table, seed STATUS_MAP | test_active_cannot_be_reached_by_other_commands; transformation_log.md |
| BR-05 | Eligibility, employer decision and academic approval are three separate results; none implies another. | OB-05; CL-003 | M-02 (designed) | NOT EXECUTED - module planned for Evaluation 3 |
| BR-06 | A placement is completed only when the closure gate passes: accepted hours reach the required total, final evaluations are submitted without hold and the academic signoff exists. | OB-11; R-007; DH05-SC-05 | M-03 + M-05 (ADR-003) | NOT EXECUTED - designed; closure gate is Evaluation 3 |
| BR-07 | Every state-changing command and every denied access writes an audit entry; entries are never updated or deleted. | QR-03; OB-12; US-026 | M-08 (ADR-006) | test_audit_history_can_only_be_appended_and_read, audit assertions in activation tests |
| BR-08 | Every eligibility or readiness decision stores the version of the rules used; changing a rule never changes a past decision. | QR-05; F-24; QS-07 | M-06 (ADR-004) | test_rule_change_is_configuration_only, test_qs04_audit_reason_records_the_rule_version_used |
| BR-09 | Restricted evaluation comments and RESTRICTED/INTERNAL incidents are visible only to authorized roles; while CL-018 is open, access is denied by default. | QR-02; CL-018; R-004 | M-07 (ADR-005) | test_host_organization_sees_readiness_without_restricted_evidence (evidence references); evaluation/incident projections NOT EXECUTED (M-05 planned) |
| BR-10 | A user reaches a placement only through a relationship with it; without one, the answer is 'not found'. | QR-02; ASM-007 | M-07 (ADR-005) | test_unrelated_user_gets_not_found, test_other_organization_cannot_see_the_placement, test_qs02_* |
| BR-11 | A failed notification never cancels or reverts an approval, an activation or a closure. | QR-04; ASM-009 | M-09 outbox (ADR-008) | test_failed_delivery_keeps_activation_and_retries |
| BR-12 | Two commands on the same placement cannot both succeed from the same starting status. | Design rule found in review (QS-09) | M-03 repository conditional update (ADR-010) | test_two_concurrent_activations_only_one_commits |

## Design assumptions

| ID | Assumption | Source | How to validate | If false |
|---|---|---|---|---|
| DA-01 | Load stays between 600 and 900 placements per year with 8 to 12 office users. | RFP section 8; F-22 | Ask the office for last year's numbers (CL-005 follow-up). | ADR-001 revisit triggers: measure and reconsider the structure. |
| DA-02 | One institution, one time zone; all timestamps are stored in UTC. | Starter kit convention | Confirm no campus works in another country. | Add a time-zone attribute per campus; no structural change. |
| DA-03 | SQLite is enough for local development and the demo; PostgreSQL is the shared environment. | Starter docker-compose | Run the same tests against PostgreSQL (NOT EXECUTED, see TP-14). | Fix SQL differences; the repository isolates them. |
| DA-04 | The mock identity header is a development mechanism, never production security. | Starter technical assumptions | Decide with IT Services the real authentication before any real pilot. | Only IdentityAdapter changes (ADR-007). |
| DA-05 | One experiential-learning coordinator role is allowed to activate placements; other roles are not. | US-016; CL-008 open | Confirm with the office which staff roles may activate. | Change one entry of the access policy (M-07). |
| DA-06 | The Employer Directory answers the agreement question for the organization at the moment of activation; DH-05 does not cache the answer between requests. | ASM-003 | Contract test against the real service when it exists. | Add a snapshot with timestamp (already designed for verification evidence). |

## Quality scenarios

| ID | Attribute | Stimulus | Response | Measure |
|---|---|---|---|---|
| QS-01 | Privacy | Opens the candidate INT-APP-1001 (student HU-STU-5001) to take the hiring decision. | The system returns only the candidate projection approved for employers: name, program, the documents of that application classified as APPLICATION (CV, motivation letter) and the application status. Academic average, credits, standing, other applications of the student and RESTRICTED documents are never included. | 0 fields outside the employer projection in 100% of responses to external users. Verified by an automated test per external endpoint. |
| QS-02 | Relationship-based Authorization | Requests the evaluations and incidents of placement PLC-2001, which belongs to ORG-002 and is supervised by SUP-EXT-001. | The request is denied because the user has no relationship with PLC-2001, even though their role is correct. The response does not reveal whether the placement exists, and the attempt is written to the audit history. | 100% of requests without a relationship are denied; 100% of denials are recorded with actor, resource and time. |
| QS-03 | Field-level privacy | Opens the midterm evaluation EVAL-001 and the incident list of their own placement. | The student sees student_visible_feedback and the rating, but never restricted_comments. Incidents with visibility RESTRICTED or INTERNAL (for example INC-001 and INC-002 in the data pack) are shown only to the roles allowed for that visibility. While CL-018 is open, restricted fields are denied to everybody except the experiential-learning office, the faculty supervisor of the placement and the author of the content (a workplace supervisor reads their own comments); deny by default. | restricted_comments absent from 100% of student and external responses; tested for every audience in the access matrix. |
| QS-04 | Auditability | Investigates months later why hour entry HOUR-002 was reported as 10 hours and confirmed as 8, and which work plan version was approved for PLC-2001. | The history of the placement shows every change with actor, date and time, previous value, new value and reason. WP-001 is labeled v2, so the previous approved version and v2 both remain readable; nothing was overwritten. | 100% of state-changing commands write an audit entry in the same database transaction as the change. No application interface can update or delete an audit entry. The history of one placement is obtained with one query. |
| QS-05 | Reliability (integration failure) | Answers SIS-503 SERVICE_UNAVAILABLE (or SIS-409 STALE_ACADEMIC_PROFILE) while the eligibility of a new application is checked. | The application is saved. Its eligibility stays ELIGIBILITY_PENDING with the error code recorded, and the check is retried. A 409 answer sends the case to manual review. The system never decides eligibility without a source timestamp. | 0 applications lost; 0 eligibility decisions without source data and timestamp; the student sees the pending status and the reason. |
| QS-06 | Reliability (notification failure) | Fails when the system notifies the student and the supervisors that PLC-2001 was activated. | The activation stays committed. The notification is kept in the outbox with its failure and is retried; the failure is visible to the office. | 0 approvals, activations or closures rolled back because of a notification failure; every failed notification is retried or flagged. |
| QS-07 | Maintainability (rule change) | The BSc Biology program adds CONFIDENTIALITY_FORM as a readiness condition for PROFESSIONAL_PRACTICUM, and raises its minimum average, while applications are open. | The change is applied as a new version of the rule configuration. New evaluations use the new version; decisions already taken keep the version they were evaluated with. | No source-code change and no redeployment; 0 past decisions modified; the rule version is visible in every eligibility decision and readiness evaluation. |
| QS-08 | Integrity of the activation gate | Tries to activate PLC-2002 (academic approval and work plan pending) and PLC-2003 (agreement expired, insurance missing). | Both activations are refused and the system names the blocking conditions: READY-004 and READY-006 for PLC-2002; for PLC-2003, READY-007 (expired), READY-008 (missing), the directory's EXPIRED agreement for ORG-005 (valid until 2026-07-31), and ACADEMIC_APPROVAL and WORK_PLAN, which the configuration requires but its checklist does not contain (EU-02). If the agreement cannot be verified because the directory is down, the activation is also refused (fail closed). The attempt is recorded. | 100% of activations with a pending, blocked, expired or unverifiable required condition are refused; after the initial load there is no other path (import, API, script) that sets a placement to ACTIVE. The one exception is the one-time seed, which loads historic placements as exported (PLC-2001 is already ACTIVE in the data pack) and logs it in data/generated/transformation_log.md. |
| QS-09 | Consistency under concurrent commands | Both send the activation command for the same placement in PENDING_ACTIVATION at the same moment, and both read the same status before either writes. | Exactly one command writes ACTIVE. The other rolls back, receives 409 with code STATE_CHANGED and leaves no success audit entry and no notification. | For N concurrent commands on the same status, exactly 1 success audit entry and 1 set of notifications; N-1 receive STATE_CHANGED or ILLEGAL_TRANSITION. Verified by a deterministic interleaving on SQLite; true parallel run on PostgreSQL NOT EXECUTED (TP-14). |

## Drivers

| ID | Driver | Sources | Consequence | Decisions |
|---|---|---|---|---|
| AD-01 | Activation and closure gates that cannot be bypassed | RFP section 7, OB-07, OB-11, ASM-006, R-002, R-007, QS-08, QS-09 | Placement lifecycle changes happen only through commands of the Placements module, which evaluates the readiness gate or the closure gate in the same transaction. No other module, import or script writes the placement status. | ADR-001, ADR-002, ADR-003, ADR-010 |
| AD-02 | Access by relationship and by field | QR-01, QR-02, CL-009, CL-018, ASM-007, R-003, R-004, QS-01, QS-02, QS-03 | One Access module decides every request (deny by default) using role plus relationship with the opportunity or placement, and every response goes through an audience projection that removes the fields the user may not read. | ADR-005 |
| AD-03 | Complete history that nobody can rewrite | QR-03, OB-12, F-02, US-026, CL-019, QS-04, QS-09 | Every command writes an append-only audit entry in the same transaction. Work plans, eligibility decisions and hour reviews are stored as new records or versions, never overwritten. | ADR-002, ADR-006, ADR-010 |
| AD-04 | Rules that change by program and placement type | QR-05, RFP section 7, F-24, CL-004, CL-020, ASM-004, R-001, EU-01, EU-02, QS-07 | Rules are versioned configuration evaluated by small interchangeable evaluators (Strategy). Each decision stores the rule version used. | ADR-004 |
| AD-05 | Authoritative external services that may fail | QR-04, F-17, F-18, ASM-002, ASM-003, ASM-009, R-005, service contracts, QS-05, QS-06 | The core talks to ports, not to services. Adapters translate the contracts, record source timestamps and define the failure behavior of each call. Notifications leave through an outbox so that they never undo a business decision. | ADR-007, ADR-008 |

## Tensions

| Tension | Resolution | Accepted cost |
|---|---|---|
| Fresh agreement data vs. availability of the directory | Verify the agreement at activation and refuse when it cannot be verified | Activations stop while the directory is down (BR-02). |
| Immediate notification vs. reliable decision | Commit locally, deliver through the outbox | Messages arrive later and may repeat once. |
| Flexible rules vs. simple code | A small vocabulary of rule types configured per type and program | A rule that the vocabulary cannot express needs a new class (ADR-004 revisit). |
| Strong module isolation vs. one transaction | Modules in one process sharing one database, with table ownership | Isolation is enforced by tests, not by the network. |
| Rich history vs. minimum exposure | Audit everything, show history only to the office | External users cannot reconstruct decisions themselves. |
| Complete product vs. one semester | Implement the riskiest slice, design the rest and label it | Four business modules, the closure gate and the web client remain for Evaluation 3 (AR-07). |
