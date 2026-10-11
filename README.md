# DH-05 Internship and Practicum Management System

Software Design II - Universidad del Norte. Team: Sebastián Mercado, Cher Jiménez, Juan Arbeláez.

This is our project repository for Evaluation 2. We started from the Horizon starter that the
course gave us (ADR-000) and organized the code as a modular monolith (ADR-001): one application
with one module per business area.

For this evaluation we implemented one complete flow: **activating a placement** (user stories
US-014 and US-016). The system only lets the coordinator activate a placement when all the
required documents and approvals are ready, and it explains what is missing when they are not.
The other modules are designed in the documents and will be implemented in Evaluation 3.

## What you need

- Python 3.12 or newer
- Docker, only if you want to try the optional PostgreSQL setup

## How to run it

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |   macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env                 # Windows: copy .env.example .env

python scripts/validate_data.py      # checks the DH-05 data files
python scripts/load_seed_data.py --replace
python scripts/seed_domain.py        # loads the data into the database
uvicorn horizon.main:app --reload
```

Then open http://127.0.0.1:8000/docs. The services are simulated, so you choose the user with the
header `X-Mock-User-Id`. Some requests to try:

| Request | User | What should happen |
|---|---|---|
| `POST /placements/PLC-2002/activation` | `EXP-COORD-001` | 409: two conditions are pending (READY-004 and READY-006) |
| `POST /placements/PLC-2003/activation` | `EXP-COORD-001` | 409: lists all five missing or expired conditions |
| `POST /placements/PLC-2002/activation` | `HU-STU-5001` | 403: a student cannot activate, and the attempt is audited |
| `GET /placements/PLC-2002/readiness` | `ORG-C-001` | 200: the company sees the checklist without restricted data |
| `GET /placements/PLC-2003/readiness` | `ORG-C-001` | 404: the company has no relation with this placement |

Other options: `python scripts/run_worker.py` sends the pending notifications, and
`MOCK_EMPLOYER_FAILURE=EMP-503` in `.env` simulates the employer directory being down.

## Tests

```bash
python -m pytest -o addopts="" -v
ruff check . && ruff format --check .
python docs/evaluation-2/validation/mutation_check.py .
```

The last command breaks the code on purpose in a temporary copy (6 different defects) and checks
that our tests catch each one. The repository itself is not changed.

The same checks are set up in GitHub Actions (`.github/workflows/ci.yml`). At the time of this
delivery the workflow had not run yet.

## How the code is organized

```text
src/horizon/
  main.py              FastAPI application and routers
  modules/
    placements/        M-03  placement states and the activation command   <- implemented
    readiness/         M-04  checklist and readiness gate                  <- implemented
    rules/             M-06  rules read from config/rules (Strategy pattern)
    access/            M-07  who can see or do what
    audit/             M-08  history of changes (only new rows, never edited)
    notifications/     M-09  messages saved with the change and sent later (outbox)
    integrations/      M-11  connection to the simulated external services
    opportunities/, applications/, monitoring/, reporting/   designed for Evaluation 3
  shared/              interfaces of the external services and domain events
  infrastructure/      database, importers and data loading
config/rules/          readiness rules in JSON (they change without touching code)
data/                  DH-05 data pack (the original files are not modified)
mocks/                 contracts of the simulated services
docs/evaluation-2/     all the Evaluation 2 documents (index below)
```

Rules we agreed on as a team:

- A module uses another module only through its public functions, never through its tables.
- Permissions are checked only in `modules/access`.
- Every change of state saves an audit record in the same transaction.
- Rules for programs and placement types go in `config/rules`, not in the code.
- Only `modules/integrations` talks to the external services.

## Evaluation 2 documents

Reviewed version: 2026-10-11. We mark every item with its real status: **DESIGNED** (decided but no
code yet), **IMPLEMENTED** (there is code), **VERIFIED** (there is code and a test that we ran
checks it) and **NOT EXECUTED** (planned but not run). In the test plan, **EXECUTED** is used for a
check that was run but does not test a feature by itself, and **PARTIAL** for a test that covers
only part of what it targets.

| Document | Where |
|---|---|
| Architecture and design document (PDF) | `docs/evaluation-2/architecture-document.pdf` |
| Decision records ADR-000 to ADR-010 | `docs/evaluation-2/adr/` |
| Requirements, rules, scenarios and drivers | `docs/evaluation-2/requirements-and-drivers.md` |
| Diagrams (SVG and PNG) | `docs/evaluation-2/views/` |
| Domain, data, states, failures, interfaces and security | `docs/evaluation-2/design/` |
| Deployment assumptions | `docs/evaluation-2/deployment-assumptions.md` |
| Test plan, results and raw output | `docs/evaluation-2/validation/` |
| Traceability | `docs/evaluation-2/traceability.md` |
| Risks, backlog, plan and open questions | `docs/evaluation-2/project-status.md` |
| Submission manifest | `docs/evaluation-2/manifest.yaml` |

| What | Status | Evidence |
|---|---|---|
| Activation flow with permissions, audit and notifications | VERIFIED | `tests/integration/`, `tests/unit/` |
| Two coordinators activating at the same time: only one wins (ADR-010) | VERIFIED on SQLite; PostgreSQL NOT EXECUTED | `tests/integration/test_concurrency_and_atomicity.py` |
| Modules only use the modules they are allowed to | VERIFIED | `tests/architecture/test_module_boundaries.py` |
| The tests catch real defects | EXECUTED: 6 of 6 defects detected | `docs/evaluation-2/validation/mutation_output.txt` |
| Test and lint output on the review date | EXECUTED | `docs/evaluation-2/validation/pytest_output.txt`, `ruff_output.txt`, `versions.txt` |
| Opportunities, applications, monitoring, reporting, closure and web client | DESIGNED only | Evaluation 3 |
| PostgreSQL, load tests, real login | NOT EXECUTED | `docs/evaluation-2/validation/test-plan.md` (TP-13 to TP-15) |

The source digest in `manifest.yaml` identifies the exact version of the code we reviewed. It is
calculated with this command (on Windows, run it in Git Bash):

```bash
find src tests config -type f \( -name '*.py' -o -name '*.json' \) -not -path '*/__pycache__/*' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16
```
