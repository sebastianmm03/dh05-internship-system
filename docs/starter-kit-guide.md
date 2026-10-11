# Starter Kit Guide

## Purpose

The common starter reduces environment setup work and demonstrates a small number of engineering practices. It is intentionally generic so that it can be used with all five Horizon University project tracks.

## What it demonstrates

- Application startup and routing.
- Configuration through environment variables.
- A generic repository and application-service boundary.
- Persistence of imported source records.
- CSV/JSON ingestion with visible errors and warnings.
- Simulated identity and institutional integrations.
- Basic automated tests.

## What it does not decide

The starter does not decide the final:

- Domain entities or aggregates.
- Workflow states and transitions.
- Authorization rules.
- Relational schema.
- Architecture style.
- User interface.
- Integration strategy.
- Reporting architecture.
- Change-request solution.

## Expected team action

1. Inspect the RFP and data pack.
2. Identify ambiguities and prepare stakeholder questions.
3. Decide which starter components are useful.
4. Record the decision in ADR-000.
5. Replace generic records with a justified domain model when appropriate.
6. Preserve raw source evidence and document transformations.
