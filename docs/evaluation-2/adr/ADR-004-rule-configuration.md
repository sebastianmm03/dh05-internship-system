# ADR-004 - Versioned rule configuration evaluated through Strategy

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-04, QR-05

## Context

Eligibility combines opportunity criteria (eligible programs, minimum credits, minimum average) with program rules; the observed reasons for ineligibility are enrollment status (ELIG-5005) and academic standing (ELIG-5006). Readiness conditions vary by placement type and program (CL-020, EU-02). Rules change between periods and the office has few technical people.

## Decision

Rules are data: a versioned configuration file (config/rules/readiness.json, version readiness-v1) lists which rules apply per placement type, optionally per program (lookup 'TYPE@PROGRAM', then 'TYPE', then 'default'), with their parameters. Each rule type is a small evaluator implementing one interface (Strategy); a factory builds the evaluators from the configuration. Implemented readiness rule types: REQUIREMENT_COMPLETE, AGREEMENT_VALID_IN_DIRECTORY and SUPERVISORS_ASSIGNED. Eligibility and completion rule types (PROGRAM_IN_LIST, MIN_CREDITS, MIN_AVERAGE, ENROLLMENT_ACTIVE, STANDING_ALLOWED, ACCEPTED_HOURS_AT_LEAST, EVALUATION_SUBMITTED) are DESIGNED. Every gate decision records the rule version in its audit reason ('readiness gate readiness-v1'); a refusal also stores each blocking rule result in the audit new_value. A dedicated rule_version column on decisions is DESIGNED.

## Alternatives

Hard-coded conditionals; an external rule engine (Drools-like); a full BPM tool.

## Rationale

Adding or changing a condition is a configuration change (QS-07). New rule types are new classes that do not modify the callers (open/closed). Storing the version answers auditability questions (AD-03).

## Consequences

Somebody must own rule governance (who may publish a new version): recorded as open question for CL-004 and CL-020. The first release edits configuration files reviewed by the team; an admin screen is a later backlog item.

## Verification

test_rule_change_is_configuration_only; test_qs04_audit_reason_records_the_rule_version_used. Eligibility rules: DESIGNED.

## Reconsideration / supersession

If rules need logic that cannot be expressed as a combination of rule types.

## Trace links

AD-04; QS-07; BR-08; EU-01, EU-02; V-04
