# DH-05 Internship and Practicum — Release 1: Discovery Data Pack

This pack contains synthetic exports from Horizon University's current placement
environment. It is evidence for discovery and modeling, not a final application schema.

## Use with the Common Horizon Starter

Copy this pack's `data/` contents into the starter repository's `data/` directory,
or set `DATA_ROOT` to this pack's `data` directory.

Then run:

```bash
python scripts/validate_data.py
python scripts/load_seed_data.py --replace
```

## Student responsibilities

Teams should:

- distinguish opportunity, application, employer decision, academic approval, readiness,
  and active placement;
- inspect supervisor, work-plan, hours, evaluation, and incident history;
- preserve raw files and place transformations in `data/generated/`;
- identify external-user and field-level privacy boundaries;
- avoid treating the export structure as the required final domain model.

The pack intentionally contains incomplete activation conditions, expired agreements,
disputed hours, overdue evaluations, actual duties diverging from the approved plan,
legacy program codes, and incomplete closure evidence.
