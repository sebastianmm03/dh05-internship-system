# Data Loading Guide

## Data directories

- `data/raw`: current-process exports; do not silently edit them.
- `data/reference`: institutional reference data and synthetic mock identities.
- `data/events`: integration-event examples.
- `data/scenarios`: narrative scenarios, not database seed records.
- `data/generated`: validation reports, import reports, and team-generated outputs.

## Validate files

```bash
python scripts/validate_data.py
```

The script checks whether CSV and JSON files can be parsed and writes a report to:

```text
data/generated/validation_report.json
```

## Load records

```bash
python scripts/load_seed_data.py --replace
```

`--replace` clears the generic imported-record table before loading. Without it, another import is appended.

The script writes:

```text
data/generated/import_report.json
```

## Validation boundaries

The common loader performs structural validation and limited identifier extraction. It does not enforce project business rules. Teams must design those rules after discovery.
