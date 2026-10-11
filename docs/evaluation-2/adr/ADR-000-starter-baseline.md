# ADR-000 - Adopt the Horizon common starter kit as technical baseline

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** C-01, C-03, C-06, AD-05

## Context

The course supplies horizon-common-starter: a FastAPI application with environment configuration, a generic SQLAlchemy table (imported_records), CSV and JSON importers with validation reports, a mock identity service, a mock Student Information Service and unit, integration and importer tests. Its README states that it does not define the domain model, workflow, authorization, schema or architecture. We also received the DH-05 discovery data pack with two service contracts (Student Information, Employer Directory) and their failure responses.

## Decision

Keep: FastAPI, the configuration mechanism, the importers and validation scripts, the interfaces / application / domain / infrastructure split, the mock identity header and the test setup (pytest, ruff).
Modify: the identity mock reads the DH-05 file mock_identities.json; the Student Information mock follows the DH-05 contract route and returns the three documented failures; PROJECT_CODE becomes DH-05.
Add: an Employer Directory mock, the business modules of ADR-001, domain tables per module, the audit and outbox tables.
Replace: the generic imported_records table is kept only as a staging area for raw evidence; the domain lives in module-owned tables built by a documented transformation.

## Alternatives

(1) Start from an empty repository with another stack. (2) Use the starter unchanged and model the domain inside imported_records.

## Rationale

The starter already runs, is tested and matches the size of the team (C-01). Python and FastAPI are known to the team and simple to maintain (C-03). Starting from zero spends the first sprint on setup. Using imported_records as the domain would copy the export structure, which the data pack and ASM-010 forbid.

## Consequences

We inherit the starter conventions and must keep its tests passing. We own the transformation from raw exports to domain tables and must document it (data/generated/transformation_log.md). Python 3.12 is required on every team computer.

## Verification

Starter tests still pass (tests/importers, test_health_endpoint.py, test_sample_endpoint.py); the DH-05 files are used by the adapters.

## Reconsideration / supersession

If the chosen web technology for Evaluation 3 cannot consume a FastAPI backend, or if a requirement needs a capability the stack cannot offer.

## Trace links

C-01, C-03, C-06; EU-04; repository README
