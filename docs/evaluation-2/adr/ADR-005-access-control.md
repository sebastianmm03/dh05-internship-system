# ADR-005 - Centralized relationship-based access with audience projections

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-02, QR-01, QR-02

## Context

Roles are not enough: a workplace supervisor may see only their own placements, a host organization only its opportunities and candidates, and one evaluation mixes student-visible feedback with restricted comments. CL-018 (who may read restricted content) is still open.

## Decision

An Access module is the only place where access is decided. Application services call check(actor, action, placement relations) before any read or command. The decision uses the role of the user and their relationship with the resource (student of, contact of the organization, workplace supervisor of, faculty supervisor of, office staff with role EXPERIENTIAL_LEARNING_COORDINATOR, PROGRAM_DIRECTOR or AGREEMENTS_REPRESENTATIVE; 'coordinator of the program' is DESIGNED). Responses are built through audience projections (student, host organization, workplace supervisor, faculty, office) that include only the allowed fields. Default is deny; until CL-018 is closed, restricted fields stay limited to the office, the faculty supervisor of the placement and the author of the content (a workplace supervisor reads their own comments).

## Alternatives

Role checks in each endpoint; protection proxy around repositories; database row-level security.

## Rationale

One decision point is easier to test exhaustively (QS-02, QS-03) and to change when CL-018 is answered. Projections make field-level privacy explicit instead of relying on the UI to hide fields.

## Consequences

Every new endpoint must declare its action and projection; tests cover the access matrix. Relationship data (assignments, contacts) becomes critical and is audited.

## Verification

test_unrelated_user_gets_not_found; test_host_organization_sees_readiness_without_restricted_evidence; test_qs02_*. Evaluation/incident projections: DESIGNED.

## Reconsideration / supersession

When CL-018 is closed, or if the number of audiences grows beyond what projections can express simply.

## Trace links

AD-02; QS-01, QS-02, QS-03; BR-09, BR-10; T-02, T-03, T-08
