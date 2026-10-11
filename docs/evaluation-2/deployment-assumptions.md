# Deployment assumptions

| Concern | Assumption |
|---|---|
| Runtime | Python 3.12, FastAPI, SQLAlchemy 2; versions recorded in docs/evaluation-2/validation/versions.txt. |
| Database | SQLite file by default; PostgreSQL 16 profile in docker-compose.yml, not yet exercised by the suite (TP-14). |
| Schema | Created by create_all at start-up; no migrations yet (BL-13). |
| Mocks | In-process classes reading mocks/*.json; failure injected with MOCK_EMPLOYER_FAILURE=EMP-503. |
| Identity | Header X-Mock-User-Id with MOCK_IDENTITY_ENABLED=true; development only (DA-04). |
| Worker | Run on demand with scripts/run_worker.py; a scheduler is a deployment decision for the pilot. |
| Data | DH-05 release-1 data pack; manifest hashes verified (placement_types.csv unchanged). |
| Reproducibility | pip install -e '.[dev]'; python scripts/seed_domain.py; pytest. The same commands run in CI (.github/workflows/ci.yml); run #1 on GitHub passed on 2026-10-11. |

## Signals

| Signal | Interpretation | Source | Status |
|---|---|---|---|
| Activation outcomes by code | Separates normal blocking from failures | Audit entries by action (ACTIVATION_REFUSED, PLACEMENT_ACTIVATED, ACCESS_DENIED); query by resource_id | Available through the audit table |
| Oldest PENDING outbox message | Delivery is not progressing | outbox_messages.created_at where status = PENDING | Available (query); no alert yet |
| FAILED messages | Human action needed | outbox_messages.status = FAILED with last_error | Available (query) |
| STATE_CHANGED rate | Real contention between coordinators | API responses with code STATE_CHANGED | DESIGNED (no metrics endpoint) |
| Directory failures | Activations blocked by an outage | Blocking reason 'could not be verified' in refusals | Available in audit new_value |
| Correlation | Follow one command end to end | correlation_id in audit, outbox and response | Available |
