# Domain and data

## Entities

| Entity | Module | Status | Key attributes | Notes |
|---|---|---|---|---|
| Placement | M-03 | IMPLEMENTED | placement_id (PK), source_application_id, student_id, organization_id, placement_type, program_code, approved_start_date, approved_end_date, required_total_hours, status, workplace_supervisor_id, faculty_supervisor_id, activated_at, actual_start_date | Aggregate root of the lifecycle. Source: placements.csv; 'Blocked' is not stored. |
| ReadinessCondition | M-04 | IMPLEMENTED | check_id (PK), placement_id, requirement_type, required, status, completed_at, evidence_reference, valid_until | Checklist row. Source: readiness_checklist.csv. valid_until is the expiry used by the gate (null for every seeded row: the export has no such column). |
| AuditEntry | M-08 | IMPLEMENTED | id (PK), occurred_at, actor_id, action, resource_type, resource_id, previous_value, new_value, reason, correlation_id | Append-only. Written in the same transaction as the change. |
| OutboxMessage | M-09 | IMPLEMENTED | id (PK), created_at, event_name, recipient_id, payload, status, attempts, last_error, correlation_id | PENDING, SENT or FAILED (after 5 attempts). |
| RuleSet (file) | M-06 | IMPLEMENTED | version, readiness rules by placement type and program | config/rules/readiness.json, lookup TYPE@PROGRAM, TYPE, default. |
| Opportunity | M-01 | DESIGNED | opportunity_id, organization_id, title, placement_type, eligible_programs, work_modality, dates, minimum_credits, minimum_average, status | Source: internship_opportunities.csv. |
| Application | M-02 | DESIGNED | application_id, student_id, opportunity_id, application_status, eligibility_status, employer_decision, academic_approval, current_version | Three separate results (BR-05). Source: applications.csv. |
| EligibilityDecision | M-02 | DESIGNED | review_id, application_id, outcome, criteria_summary, source_data_timestamp, rule_version | Source: eligibility_reviews.csv; rule_version is new. |
| WorkPlan (version) | M-03 | DESIGNED | work_plan_id, placement_id, version_label, approved_at, approved_by, current_version | New record per version, never overwritten. Source: work_plans.csv. |
| HourEntry | M-05 | DESIGNED | hour_entry_id, placement_id, work_date, reported_hours, confirmed_hours, accepted_hours, statuses | Three levels of hours. Source: hour_entries.csv. |
| Evaluation | M-05 | DESIGNED | evaluation_id, placement_id, evaluation_type, student_visible_feedback, restricted_comments, visibility_classification | Mixed visibility in one record. Source: evaluations.csv. |
| Incident | M-05 | DESIGNED | incident_id, placement_id, category, severity, visibility, status | Visibility drives the projection. Source: placement_incidents.csv. |
| StudentProfile (snapshot) | M-11 / M-02 | IMPLEMENTED (port) | student_id, program_code, enrollment_status, completed_credits, academic_average, academic_standing, read_at | Not stored as master data; owned by the Student Information Service. |
| AgreementSummary (snapshot) | M-11 / M-04 | IMPLEMENTED (port) | organization_id, active, agreement_status, agreement_valid_until, read_at | Owned by the Employer Directory. Transient value returned by the port; not persisted. |

## Data dictionary

| Field | Meaning and rule |
|---|---|
| placements.status | One of the seven lifecycle states. Today only the activate command writes it, through the transition table and conditional update; the other commands are DESIGNED to reuse the same path (ADR-010). |
| placements.activated_at | Instant of the activation commit (UTC). Null before activation. |
| placements.actual_start_date | Real first working day, recorded after activation; never a status. |
| placements.program_code | Normalized through academic_programs.known_aliases (SWE becomes BSC-SWE). |
| readiness_conditions.valid_until | Expiry of the evidence; a COMPLETE row past this date blocks. The exported checklist has no such column, so the seed leaves it null; only synthetic test rows set it. |
| readiness_conditions.evidence_reference | Reference to a document kept elsewhere; null in projections for RESTRICTED requirements. |
| audit_entries.previous_value / new_value | JSON snapshots of the changed fields; a refusal stores the blocking list. |
| audit_entries.reason | Free text. Gate decisions name the rule version ('readiness gate readiness-v1' on refusal, 'readiness gate readiness-v1 passed' on success); ACCESS_DENIED entries hold the attempted action (for example placement.activate). |
| audit_entries.correlation_id | Same value as the event, the outbox messages and the API response. |
| outbox_messages.payload | Only placement_id and template; no personal or restricted data. |
| outbox_messages.attempts / status | Incremented on each failed delivery; FAILED at 5. |

## Invariants

| ID | Invariant | Enforced in | Status | Verified by |
|---|---|---|---|---|
| INV-01 | A placement status is always one of the seven lifecycle states and changes only through the transition table. | Placement._move, TRANSITIONS | VERIFIED | tests/unit/test_placement_lifecycle.py |
| INV-02 | ACTIVE can be reached only by 'activate' with a passed gate result. | Placement.activate | VERIFIED | test_activation_needs_a_passed_gate, test_active_cannot_be_reached_by_other_commands |
| INV-03 | A start date exists only on a placement that was activated. | Placement.register_start | VERIFIED | test_start_date_only_after_activation |
| INV-04 | Each state change is stored only if the stored status still equals the status read (conditional update). | SqlPlacementRepository.save | VERIFIED | test_two_concurrent_activations_only_one_commits |
| INV-05 | State change, audit entry and outbox messages of one command commit together or not at all. | ActivatePlacement.execute | VERIFIED | test_failure_in_the_middle_rolls_everything_back |
| INV-06 | Audit entries can only be appended and read. | AuditRecorder public interface | VERIFIED | test_audit_history_can_only_be_appended_and_read |
| INV-07 | One correlation id links the audit entry, the event and the outbox messages of a command. | new_correlation_id | VERIFIED | test_one_correlation_id_links_audit_entry_and_notifications |
| INV-08 | The seed never modifies the raw data-pack files. | seed_placements | VERIFIED | test_seed_never_modifies_the_raw_files |

## Data ownership

| Information | Authority | What DH-05 keeps | Evidence |
|---|---|---|---|
| Student identity and academic profile | Student Information Service | Nothing stored today; the eligibility decision (M-02, designed) will record the values it used and their read_at time | ASM-002, SIS contract |
| Organization identity and agreement summary | Employer Directory Service | Organization reference only; the agreement is read at each gate evaluation and not stored (a refusal records the status that blocked) | ASM-003, directory contract |
| User identity and institutional role | Identity service | User id in audit entries and relationships | ASM-001, US-027 |
| Opportunities and reviews | DH-05 (M-01) | Master data | CL-002, US-003 |
| Applications, eligibility, employer decision, academic approval | DH-05 (M-02) | Master data; decisions append-only | CL-003, US-011 |
| Placement, lifecycle, work-plan versions, supervisors | DH-05 (M-03) | Master data; versions append-only | CL-014, CL-015, CL-019 |
| Readiness conditions and evidence references | DH-05 (M-04) | Master data; documents stay in the document system (simulated reference) | CL-007, document_types.csv |
| Hours, progress, incidents, evaluations, signoff | DH-05 (M-05) | Master data; reviews append-only | CL-017, CL-018 |
| Rule configuration and reference data | DH-05 (M-06) | Versioned configuration | CL-004, CL-020 |
| Audit history | DH-05 (M-08) | Append-only | OB-12, US-026 |

## Data lifecycle

| Data | Rule |
|---|---|
| Placements | Never deleted; CANCELLED and CLOSED remain for program validation. |
| Audit entries | Append and read only through the application; a database administrator could still change rows (AR-05). |
| Outbox messages | SENT and FAILED are kept for diagnosis; an archive policy is not defined yet (BL-12). |
| Rule versions | Old versions stay in Git so every stored version label can be explained. |
| Personal data | Only synthetic data in the course (C-02). Real retention rules must be defined before a pilot. |
| Raw data pack | Never modified (INV-08); every transformation is written to data/generated/transformation_log.md. |
| Schema changes | create_all builds the schema today; versioned migrations are needed before shared data exists (BL-13). |
