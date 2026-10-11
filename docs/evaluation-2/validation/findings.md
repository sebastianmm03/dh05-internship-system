# Findings: expected versus observed

Executed on 2026-10-11. Raw output: pytest_output.txt, ruff_output.txt, mutation_output.txt; versions in versions.txt.

```yaml
test_id: 'TP-01 / tests/unit/test_placement_lifecycle.py (6 tests)'
status: 'PASSED'
claim: 'BR-01, BR-03, INV-01..03: the lifecycle only moves through the transition table; ACTIVE only through activate() with a passed gate.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'none'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'not applicable'
fixture:
  description: 'None: Placement objects built in memory'
  setup: 'Placement objects built in memory; no database.'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'not needed: objects are created inside each test'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: 'not applicable'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: 'Activation without a passed gate is refused; other commands cannot reach ACTIVE; closing from PENDING_ACTIVATION is illegal; start date only after activation; interrupted closure allowed from ON_HOLD.'
  observed: 'As expected (6 passed).'
limitations: ['Domain level only; persistence and API are covered by TP-04 and TP-05.']
related:
  requirements: 'US-014'
  qualities: 'QS-08'
  decisions: 'ADR-003'
```

```yaml
test_id: 'TP-02 / tests/unit/test_readiness_rules.py (5 tests)'
status: 'PASSED'
claim: 'BR-01, BR-02, BR-08, QS-07: pending, expired or missing conditions block; directory failure keeps the gate closed; a rule change is configuration only.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'none'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'not applicable'
fixture:
  description: 'In-memory conditions; temporary copy of config/rules/readiness.json'
  setup: 'Rule evaluators with in-memory conditions; a temporary copy of readiness.json for the configuration test.'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'not needed: each test builds its own conditions and a temporary rule file'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: 'not applicable'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: 'Each blocking case returns a blocking result; adding CONFIDENTIALITY_FORM for one program changes the result without code changes.'
  observed: 'As expected (5 passed).'
limitations: ['Readiness rules only; eligibility rule types are designed.']
related:
  requirements: 'US-012, US-014'
  qualities: 'QS-07, QS-08'
  decisions: 'ADR-004'
```

```yaml
test_id: 'TP-03 / tests/unit/test_reference_and_adapters.py (7 cases)'
status: 'PASSED'
claim: 'AD-05, QS-05, EU-03: adapters translate payloads and the three failures; the legacy program code is normalized.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'none'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'not applicable'
fixture:
  description: 'The mock service classes and their JSON contracts in mocks/'
  setup: 'The real mock service classes with their documented failure ids (SIS-404, SIS-409, SIS-503).'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'not needed: the mocks are read-only files'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: 'not applicable'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: 'Failures become port exceptions; read_at is recorded; SWE becomes BSC-SWE; expired agreements are not valid.'
  observed: 'As expected (7 passed).'
limitations: ['Mocks, not the real institutional services; no consumer-driven contract tool.']
related:
  requirements: 'US-012'
  qualities: 'QS-05'
  decisions: 'ADR-007'
```

```yaml
test_id: 'TP-04 / test_sc01_*, test_sc02_*, test_directory_down_*'
status: 'PASSED'
claim: 'QS-08, BR-01, BR-02: activation refused when a condition blocks or the directory is down.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'SQLite 3.43.1'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'create_all, no migrations (BL-13)'
fixture:
  description: 'DH-05 data pack seeded into a throw-away SQLite file for each test session (tests/conftest.py); fixed date 2026-09-24; synthetic PLC-9001 where stated'
  setup: 'Seeded data pack (PLC-2002, PLC-2003); synthetic PLC-9001 with EMP-503 injected.'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'tests/conftest.py recreates the SQLite database and reseeds the data pack for each test session'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: 'not applicable'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: '409 with READY-004 and READY-006; 409 with exactly five blocking results for PLC-2003 (READY-007 expired, READY-008 missing, directory agreement EXPIRED valid until 2026-07-31, ACADEMIC_APPROVAL and WORK_PLAN not registered); 409 ''could not be verified''; status unchanged.'
  observed: 'As expected.'
limitations: ['Mocked directory; the real service contract may differ.']
related:
  requirements: 'US-014, US-016'
  qualities: 'QS-08'
  decisions: 'ADR-003, ADR-004, ADR-007'
```

```yaml
test_id: 'TP-05 / test_failure_in_the_middle_rolls_everything_back'
status: 'PASSED'
claim: 'INV-05: state, audit and outbox commit together or not at all.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'SQLite 3.43.1'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'create_all, no migrations (BL-13)'
fixture:
  description: 'DH-05 data pack seeded into a throw-away SQLite file for each test session (tests/conftest.py); fixed date 2026-09-24; synthetic PLC-9001 where stated'
  setup: 'Event handler writes the outbox rows and then raises.'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'tests/conftest.py recreates the SQLite database and reseeds the data pack for each test session'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: 'not applicable'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: 'Status PENDING_ACTIVATION, no success audit entry, no outbox rows (checked from a new session).'
  observed: 'As expected.'
limitations: ['Shows nothing was committed; does not distinguish an explicit rollback from a discarded session.']
related:
  requirements: 'US-014'
  qualities: 'QS-04, QS-09'
  decisions: 'ADR-002, ADR-010'
```

```yaml
test_id: 'TP-05 / test_two_concurrent_activations_only_one_commits'
status: 'PASSED'
claim: 'QS-09, BR-12, ADR-010: two commands that read the same status cannot both commit.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'SQLite 3.43.1'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'create_all, no migrations (BL-13)'
fixture:
  description: 'DH-05 data pack seeded into a throw-away SQLite file for each test session (tests/conftest.py); fixed date 2026-09-24; synthetic PLC-9001 where stated'
  setup: 'PLC-9001 with every condition complete; two SQLAlchemy sessions on the same SQLite file; the second command runs to completion between the first command''s read and write.'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'tests/conftest.py recreates the SQLite database and reseeds the data pack for each test session'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: '2 SQLAlchemy sessions on the same SQLite file, deterministic interleaving'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: 'First writer commits ACTIVE; second raises StaleState; one PLACEMENT_ACTIVATED entry; three outbox rows.'
  observed: 'As expected (pytest output, docs/evaluation-2/validation/pytest_output.txt).'
limitations: ['Deterministic interleaving on SQLite, one trial; not parallel connections on PostgreSQL (TP-14).']
related:
  requirements: 'US-014'
  qualities: 'QS-04, QS-09'
  decisions: 'ADR-002, ADR-010'
```

```yaml
test_id: 'TP-06 / test_failed_delivery_keeps_activation_and_retries, test_qs06_*, test_outbox_message_is_failed_after_five_attempts'
status: 'PASSED'
claim: 'QS-06, BR-11, ADR-008: a failed notification never undoes an activation; messages are retried and marked FAILED after 5 attempts; no restricted data in payloads.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'SQLite 3.43.1'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'create_all, no migrations (BL-13)'
fixture:
  description: 'DH-05 data pack seeded into a throw-away SQLite file for each test session (tests/conftest.py); fixed date 2026-09-24; synthetic PLC-9001 where stated'
  setup: 'Activation of PLC-9001, then the worker run with a failing channel, with a crash in the middle and with five failures.'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'tests/conftest.py recreates the SQLite database and reseeds the data pack for each test session'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: 'not applicable'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: 'Placement stays ACTIVE; messages PENDING then FAILED at 5; sent messages are not resent after a crash; payload has only placement_id and template.'
  observed: 'As expected.'
limitations: ['At-least-once towards the channel: a crash between send and commit can repeat one message.']
related:
  requirements: 'US-030'
  qualities: 'QS-06'
  decisions: 'ADR-008'
```

```yaml
test_id: 'TP-07 / access tests in test_activation_endpoint.py and test_traceability_evidence.py'
status: 'PASSED'
claim: 'QS-01 (partial), QS-02, BR-09, BR-10, ADR-005: relationship-based access, 404 vs 403, audited denials, audience projections.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'SQLite 3.43.1'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'create_all, no migrations (BL-13)'
fixture:
  description: 'DH-05 data pack seeded into a throw-away SQLite file for each test session (tests/conftest.py); fixed date 2026-09-24; synthetic PLC-9001 where stated'
  setup: 'Seeded data pack; identities from mock_identities.json (student, host-organization contact, coordinator).'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'tests/conftest.py recreates the SQLite database and reseeds the data pack for each test session'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: 'not applicable'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: 'Unrelated user gets 404; related but not allowed gets 403; both audited when the placement exists; non-office audiences never see RESTRICTED evidence references; unknown identity gets 401.'
  observed: 'As expected.'
limitations: ['The identity mock has no workplace supervisors, so that case is verified at policy level only (EU-05).']
related:
  requirements: 'US-027, US-028'
  qualities: 'QS-01, QS-02'
  decisions: 'ADR-005'
```

```yaml
test_id: 'TP-08 / tests/architecture/test_module_boundaries.py (5 tests)'
status: 'PASSED'
claim: 'ADR-001, ADR-006, ADR-007: module dependencies follow the written rules; domain code is framework-free; only M-11 imports the mocks; audit is append-only.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'none'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'not applicable'
fixture:
  description: 'None: static reading of the source files'
  setup: 'Static reading of the import statements of src/horizon.'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'not needed: the test only reads source files'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: 'not applicable'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: 'No import outside the allowed table; planned modules hold only __init__.py; AuditRecorder exposes only record() and history().'
  observed: 'As expected; mutation M5 (forbidden import) made it fail as intended.'
limitations: ['Does not see dynamic imports, router wiring or coupling through shared tables.']
related:
  requirements: '-'
  qualities: '-'
  decisions: 'ADR-001, ADR-006, ADR-007'
```

```yaml
test_id: 'TP-09 / test_seed_never_modifies_the_raw_files, test_seed_loads_every_placement_of_the_pack_once'
status: 'PASSED'
claim: 'EU-03, INV-08: the seed never edits the raw exports and loads every placement once.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'SQLite 3.43.1'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'create_all, no migrations (BL-13)'
fixture:
  description: 'DH-05 data pack seeded into a throw-away SQLite file for each test session (tests/conftest.py); fixed date 2026-09-24; synthetic PLC-9001 where stated'
  setup: 'Hashes of data/raw before and after the seed; count of placements loaded.'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'tests/conftest.py recreates the SQLite database and reseeds the data pack for each test session'
execution:
  command: 'python -m pytest -o addopts="" -v (from the repository root)'
  independent_connections: 'not applicable'
  trials: '1 run; the tests are deterministic'
  raw_output: 'docs/evaluation-2/validation/pytest_output.txt'
assertions:
  expected: 'Raw files unchanged; every placement of placements.csv (four) is present after the seed; the primary key prevents duplicates.'
  observed: 'As expected.'
limitations: ['The seed is a one-time load, not a migration tool (BL-13).']
related:
  requirements: '-'
  qualities: '-'
  decisions: 'ADR-000'
```

```yaml
test_id: 'TP-10 / docs/evaluation-2/validation/mutation_check.py'
status: 'EXECUTED (6 of 6 injected defects detected)'
claim: 'The tests detect real defects in the design mechanisms.'
source_commit: '502188d4724d4a4279bc5d472c5d186052fadd26'  # same source digest as the executed copy
source_digest: 'f7281a5c6c9e7a50 (command: find src tests config -type f \( -name ''*.py'' -o -name ''*.json'' \) -not -path ''*/__pycache__/*'' | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-16)'
executed_at: '2026-10-11'
executor: 'Sebastián Mercado, 2026-10-11'
environment:
  operating_system: 'Windows 11 (10.0.26300)'
  runtime_version: 'Python 3.12.1'
  database_version: 'SQLite 3.43.1'
  extension_versions: 'none (no database extensions used)'
  resource_limits: 'none set'
  configuration_profile: 'default settings (.env.example)'
  schema_migration: 'create_all, no migrations (BL-13)'
fixture:
  description: 'A temporary copy of the repository for each injected defect'
  setup: 'Each defect injected alone into a copy of the repository; suite run with PYTHONPATH on the copy.'
  version: 'DH-05 data pack, release 1 (manifest.json unchanged)'
  seed: 'not applicable (fixed data pack, no random data)'
  reset_procedure: 'a fresh temporary copy of the repository for each injected defect'
execution:
  command: 'python docs/evaluation-2/validation/mutation_check.py .  (from the repository root; works on a copy)'
  independent_connections: 'not applicable'
  trials: '1 baseline run without defects + 1 run per defect (7 runs)'
  raw_output: 'docs/evaluation-2/validation/mutation_output.txt'
assertions:
  expected: 'At least one failing test per defect.'
  observed: 'M1..M6 all DETECTED (mutation_output.txt).'
limitations: ['Hand-picked defects, not a full mutation-testing tool.']
related:
  requirements: '-'
  qualities: '-'
  decisions: 'ADR-001, ADR-005, ADR-007, ADR-008, ADR-010'
```

```yaml
test_id: 'TP-14'
status: 'NOT_EXECUTED'
claim: 'The same suite passes against PostgreSQL with two real connections (conditional update under true parallelism).'
source_commit: null
executed_at: null
executor: null
environment:
  operating_system: null
  runtime_version: null
  database_version: 'PostgreSQL (docker-compose profile), planned'
  extension_versions: null
  resource_limits: null
  configuration_profile: null
  schema_migration: null
fixture:
  version: null
  seed: null
  reset_procedure: null
execution:
  command: null
  independent_connections: 2
  trials: null
  raw_output: null
assertions:
  expected: 'Exactly one of two concurrent activations commits; the other gets 409 STATE_CHANGED.'
  observed: null
limitations: ['Not run: no PostgreSQL in the environment used for Evaluation 2 (BL-09, AR-04).']
related:
  requirements: 'DA-03'
  qualities: 'QS-09'
  decisions: 'ADR-010'
```
