# Security and privacy

## Access matrix

| Resource | Student | Host org. | Workplace sup. | Faculty sup. | Program coord. (DESIGNED) | Office |
|---|---|---|---|---|---|---|
| Published opportunity | Read if their program is eligible | Read/edit own organization's | - | Read | Read | Read/review |
| Application (status, documents APPLICATION) | Own applications | Candidates of own opportunities | - | - | Own program | All |
| Student academic profile (credits, average, standing) | Own | Never | Never | Own placements | Own program | All |
| Placement summary and readiness checklist | Own | Own organization, without RESTRICTED evidence | Assigned placements | Assigned placements | Own program | All |
| RESTRICTED documents (agreement, insurance, confidentiality) | Status only | Status only | - | Status only | Status only | Full |
| Hour entries | Own (all levels) | - | Assigned placements | Assigned placements | Own program | All |
| Evaluation - student-visible feedback and rating | Own | Own evaluations submitted | Own evaluations | Assigned placements | Own program | All |
| Evaluation - restricted comments | Never | Never (CL-018 open) | Own comments only | Assigned placements | Pending CL-018 (deny) | All |
| Incident with visibility STUDENT/PLACEMENT_TEAM | If reporter or placement member | - | Assigned placements | Assigned placements | Own program | All |
| Incident with visibility RESTRICTED or INTERNAL | Only if they reported it | Never | Never (CL-018 open) | Assigned placements | Pending CL-018 (deny) | All |
| Audit history | - | - | - | - | Own program (read) | All (read) |

## Trust boundaries

| ID | Boundary | Treatment |
|---|---|---|
| TB-1 | Browser / client -> API | Untrusted input crosses here. Identity is a header in development (DA-04); real authentication is not designed yet. |
| TB-2 | API -> institutional services (identity, student, employer) | Their answers are data, not truth about our rules; they may fail or be stale; adapters translate and fail closed where needed. |
| TB-3 | API -> database and rule files | Trusted zone; access only with the application credentials; rule files are reviewed in version control. |
| TB-4 | Worker -> notification channel | Messages leave the system; they must contain no restricted data. |

## Threats

| ID | Category | Threat | Boundary | Control | Status | Evidence |
|---|---|---|---|---|---|---|
| T-01 | Spoofing | A caller sends any X-Mock-User-Id and acts as a coordinator. | TB-1 | Development-only mechanism (DA-04). Production needs real authentication; ports isolate the change. Risk accepted for the course and NOT acceptable for a pilot. | DESIGNED (open risk AR-02) | ADR-007; technical-assumptions.md |
| T-02 | Information disclosure | Enumerating placement ids reveals which exist. | TB-1 | Unrelated users get 404, identical to a missing placement. | VERIFIED | test_unrelated_user_gets_not_found |
| T-03 | Information disclosure | Host organization or student reads RESTRICTED evidence references (agreement, insurance). | TB-1 | Audience projection removes evidence_reference outside the office. | VERIFIED | test_host_organization_sees_readiness_without_restricted_evidence |
| T-04 | Information disclosure | A notification carries restricted data to an external recipient. | TB-4 | Outbox payload contains only placement id and template. | VERIFIED | test_qs06_outbox_payload_has_no_restricted_data |
| T-05 | Tampering | Someone edits or deletes audit history. | TB-3 | No update/delete interface; application never exposes one. A database administrator could still alter rows: not prevented. | VERIFIED (interface) / open (DB-level) | test_audit_history_can_only_be_appended_and_read; AR-05 |
| T-06 | Tampering | A weaker rule version is published to let a placement start. | TB-3 | Rules are files in version control reviewed by the team; version is stored in each decision. No runtime admin screen yet. | DESIGNED | ADR-004; BL-07 |
| T-07 | Repudiation | A coordinator denies having activated a placement. | TB-1 | Audit entry with actor, time, previous and new value, rule version and correlation id. | VERIFIED | test_ready_placement_is_activated_audited_and_notified |
| T-08 | Elevation of privilege | A student or external user calls the activation endpoint. | TB-1 | Access policy allows only the coordinator staff role; denial is audited. | VERIFIED | test_student_cannot_activate_and_denial_is_audited |
| T-09 | Tampering / integrity | Two concurrent commands produce two success records or two sets of notifications. | TB-3 | Conditional update on status; single transaction. | VERIFIED (deterministic interleaving on SQLite) | test_two_concurrent_activations_only_one_commits |
| T-10 | Denial of service | A flood of requests exhausts the application or the directory. | TB-1, TB-2 | Not addressed: load is small (DA-01) and no rate limiting is designed. | NOT DESIGNED (accepted, AR-06) | - |
