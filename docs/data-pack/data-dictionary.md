# Data Dictionary

The fields describe supplied exports. They do not define the required final schema.

## Reference files

### `host_organizations.csv`

| Field | Meaning | Known limitation |
|---|---|---|
| organization_id | Host organization identifier | Does not define placement-specific authorization |
| agreement_status | Current agreement summary | Placement readiness may require more evidence |
| agreement_valid_until | Agreement expiration date | Expired agreement appears in an active opportunity |

### `internship_opportunities.csv`

| Field | Meaning | Known limitation |
|---|---|---|
| eligible_programs | Program codes allowed by the opportunity | Pipe-separated source value is not a final rule model |
| minimum_credits/minimum_average | Initial academic criteria | Program-specific conditions may add more rules |
| status | Opportunity lifecycle state | Does not determine application or placement status |

## Raw files

### `applications.csv`

| Field | Meaning | Known limitation |
|---|---|---|
| employer_decision | Employer selection outcome | Selection is not academic or administrative approval |
| academic_approval | Program decision on academic suitability | May still require administrative readiness |
| administrative_readiness | Readiness checklist summary | Detailed checks are stored separately |
| application_status | Current source label | Several parallel dimensions are collapsed into one label |

### `placements.csv`

| Field | Meaning | Known limitation |
|---|---|---|
| source_application_id | Application that led to the placement | Historical placements may reference unavailable applications |
| placement_status | Current placement lifecycle state | Activation, completion, and closure are distinct |
| approved_start/end_date | Approved baseline dates | Later changes require preserved history |
| supervisor IDs | Current supervisor references | Supervisor changes need history |

### `readiness_checklist.csv`

| Field | Meaning | Known limitation |
|---|---|---|
| requirement_type | Condition required before activation | Conditions vary by placement type and program |
| status | Current readiness outcome | Does not define all permitted transitions |
| evidence_reference | Link to supporting evidence | Evidence may live in an external document system |

### `hour_entries.csv`

| Field | Meaning | Known limitation |
|---|---|---|
| reported_hours | Student-entered hours | Not authoritative by itself |
| confirmed_hours | Workplace supervisor confirmation | May be disputed |
| accepted_hours | Hours accepted for academic completion | Requires institutional review in some cases |

### `evaluations.csv`

| Field | Meaning | Known limitation |
|---|---|---|
| student_visible_feedback | Feedback intended for the student | Must not expose restricted comments |
| restricted_comments | Internal or limited-access comments | Complete field-level policy is not supplied |
| status | Evaluation completion state | Overdue and alternative resolution require workflow |

### `placement_incidents.csv`

| Field | Meaning | Known limitation |
|---|---|---|
| incident_category | Type of concern | Incident categories may change |
| visibility | Intended access boundary | Sensitive reports require relationship-based authorization |
| incident_status | Current handling state | A placement may remain active while under review |
