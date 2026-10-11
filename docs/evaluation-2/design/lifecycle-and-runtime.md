# Lifecycle, interactions and failure behavior

## Transitions

| From | To | Command | Actor | Guard | Side effects | Status |
|---|---|---|---|---|---|---|
| PENDING_ACTIVATION | ACTIVE | activate | Experiential-learning coordinator | Readiness gate passes; status still PENDING_ACTIVATION at write | activated_at, audit PLACEMENT_ACTIVATED, 3 outbox messages | VERIFIED |
| PENDING_ACTIVATION | (unchanged) | activate refused | Same | Gate blocks | audit ACTIVATION_REFUSED with blocking list | VERIFIED |
| PENDING_ACTIVATION | CANCELLED | cancel | Coordinator | Reason required | audit entry | Transition table only |
| ACTIVE | ON_HOLD | hold | Coordinator | Reason required | audit entry | Transition table only |
| ON_HOLD | ACTIVE | resume | Coordinator | Reason required | audit entry | Transition table only |
| ACTIVE | COMPLETION_PENDING | request_completion | Student / coordinator | End date reached or final evidence submitted | audit entry, reminders | Transition table only |
| COMPLETION_PENDING | COMPLETED | complete | Faculty supervisor | Closure gate | audit entry, notifications | DESIGNED |
| COMPLETED | CLOSED | close | Coordinator | Coordinator audit done | audit entry | Transition table only |
| ACTIVE / ON_HOLD / COMPLETION_PENDING | CLOSED | close_interrupted | Coordinator | Reason and result | audit entry | Transition table only |

## Critical interactions

| ID | Interaction | Drivers | Scenario | What it shows |
|---|---|---|---|---|
| SEQ-01 | Activation succeeds | AD-01, AD-03, AD-05 | QS-08 | Access, gate, directory, transition, audit, event and outbox in one transaction. |
| SEQ-02 | Activation refused by the gate | AD-01, AD-03 | QS-08 | Nothing changes except an ACTIVATION_REFUSED audit entry. |
| SEQ-03 | Employer Directory is down | AD-05, AD-01 | QS-08 | Gate stays closed (fail closed). |
| SEQ-04 | Two coordinators activate at the same time | AD-01, AD-03 | QS-09 | Conditional update: one wins, the other gets STATE_CHANGED. |
| SEQ-05 | Notification delivery and failure | AD-05 | QS-06 | Worker delivers after commit; failures are retried, never undo the decision. |

## Failure matrix

| ID | What fails | Detected in | Behavior | State afterwards | Who sees what | Verified by |
|---|---|---|---|---|---|---|
| FM-01 | Required condition PENDING, missing or expired | M-04 evaluator | Refuse: 409 ACTIVATION_BLOCKED with every blocking condition | Placement unchanged; ACTIVATION_REFUSED audit entry | Office sees the list and the correlation id | test_sc01_*, test_expired_condition_blocks_even_if_marked_complete |
| FM-02 | Employer Directory 503 / timeout | AgreementValidInDirectory | Fail closed: refuse, reason 'could not be verified' | Placement unchanged | Office sees the reason and can retry | test_directory_down_means_activation_refused |
| FM-03 | Employer Directory 409 (data conflict) | AgreementValidInDirectory | Refuse, reason 'directory data in conflict, manual review' | Placement unchanged | Office is told to review manually | NOT EXECUTED for the activation path (unit-tested in adapter only) |
| FM-04 | Employer Directory 404 (unknown organization) | AgreementValidInDirectory | Refuse, reason 'organization unknown to the directory' | Placement unchanged | Office | NOT EXECUTED for the activation path |
| FM-05 | Student Information 503 / 409 / 404 | StudentInformationAdapter | Translated to port exceptions; M-02 policy: pending + retry / manual review / business error | Application kept | Student sees pending and reason | Adapter translation VERIFIED (3 cases); M-02 policy DESIGNED |
| FM-06 | User without relationship | AccessPolicy | 404 as if the placement did not exist; ACCESS_DENIED audited when the placement exists (an unknown id leaves nothing to audit) | Nothing changes | Caller learns nothing | test_unrelated_user_gets_not_found, test_qs02_* |
| FM-07 | User with relationship but not allowed to act | AccessPolicy | 403; audit ACCESS_DENIED | Nothing changes | Caller knows the placement exists | test_student_cannot_activate_and_denial_is_audited, test_host_organization_cannot_activate_and_denial_is_audited |
| FM-08 | Another command changed the status first | SqlPlacementRepository.save | 409 STATE_CHANGED; rollback; no success audit, no messages | Winner's state stands | Loser is told to read again | test_two_concurrent_activations_only_one_commits (repository), test_api_answers_state_changed_when_another_command_wins (409 through the API) |
| FM-09 | Failure after the state change, before commit | ActivatePlacement.execute | Rollback of state, audit and outbox | Placement still PENDING_ACTIVATION | Caller gets an error; retry is safe | test_failure_in_the_middle_rolls_everything_back |
| FM-10 | Command repeated after success | Placement.activate | 409 ILLEGAL_TRANSITION; no second audit entry or messages | Unchanged | Caller learns it is already active | test_repeating_the_command_adds_no_second_set_of_side_effects |
| FM-11 | Notification channel fails | deliver_pending | Retry up to 5 attempts, then FAILED | Activation committed; message PENDING/FAILED | Failure visible in the outbox | test_failed_delivery_keeps_activation_and_retries, test_outbox_message_is_failed_after_five_attempts |
| FM-12 | Worker dies in the middle of a run | deliver_pending | Commit per message: sent messages stay SENT | Remaining messages PENDING | Next run continues | test_qs06_worker_crash_does_not_resend_what_was_already_sent |
| FM-13 | Identity provider disabled or user unknown | get_current_actor | 503 if disabled; 401 if missing, unknown or inactive | Nothing changes | Caller | test_mock_identity_disabled_answers_503, test_placements_endpoint_requires_a_known_identity |
| FM-14 | Rule configuration file missing or invalid | RuleConfiguration | Request fails with a server error; nothing is activated | Unchanged | Operator | NOT EXECUTED (no negative test yet; BL-06) |

## Use case UC-ACT

| Field | Value |
|---|---|
| Use case | UC-ACT  Activate a placement (US-014, US-016) |
| Primary actor | Experiential-learning coordinator (staff role EXPERIENTIAL_LEARNING_COORDINATOR). |
| Trigger | The coordinator selects Activate on a placement in PENDING_ACTIVATION. |
| Preconditions | Valid identity; the placement exists; the actor's staff role allows the action. |
| Main flow | Resolve identity, check access, read the placement, evaluate the gate under the current rule version, transition to ACTIVE, save with a conditional update, write the audit entry, publish PlacementActivated (outbox), commit, return status, rule version and correlation id. |
| Success guarantee | One committed ACTIVE status with activated_at, exactly one PLACEMENT_ACTIVATED audit entry and three outbox messages, all with the same correlation id. |
| Failure guarantee | No partial state: the placement stays PENDING_ACTIVATION, no success audit entry, no messages. |
| Alternatives | Gate blocks (409 ACTIVATION_BLOCKED, audited); directory down (blocks, fail closed); unrelated user (404, audited); related but not allowed (403, audited); concurrent command first (409 STATE_CHANGED); already active (409 ILLEGAL_TRANSITION); identity disabled (503). |
| Visible result | The office sees ACTIVE immediately; notifications may still be pending. |
| Status | IMPLEMENTED and VERIFIED by TP-04 and TP-05. |
