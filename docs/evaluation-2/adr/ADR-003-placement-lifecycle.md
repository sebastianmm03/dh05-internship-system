# ADR-003 - Explicit placement lifecycle with gated transitions

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-01, AD-03

## Context

Today activation and start are merged (OB-07), completion is judged only by hours (OB-11), and the exports mix states with consequences ('Blocked', 'Activation pending'). The lifecycle has few states but two critical guards.

## Decision

The Placement aggregate has an explicit transition table: PENDING_ACTIVATION -> ACTIVE -> COMPLETION_PENDING -> COMPLETED -> CLOSED, plus ACTIVE <-> ON_HOLD, CLOSED with result INTERRUPTED from ACTIVE, ON_HOLD or COMPLETION_PENDING, and CANCELLED from PENDING_ACTIVATION. Two transitions have guards: activation requires the readiness gate; completion requires the closure gate (accepted hours, final evaluations without hold, academic signoff). The real start date is an attribute recorded after activation, not a state. 'Blocked' is derived from the gate, not stored. Activation is written with a conditional update on the status that was read (ADR-010), and the other commands are designed to reuse it. The 'result INTERRUPTED' attribute and the closure gate are designed; the code today implements the transition table and the activation gate.

## Alternatives

State pattern (one class per state); status as free text as in the exports; a BPM engine.

## Rationale

A transition table is the simplest structure that makes illegal transitions impossible and testable. The State pattern adds one class per state while the behavior per state is still small.

## Consequences

Any new state requires updating the table and its tests. If behavior per state grows (for example per placement type), we revisit the State pattern.

## Verification

tests/unit/test_placement_lifecycle.py (6); activation tests (8). Closure gate: DESIGNED only.

## Reconsideration / supersession

When states start to carry different behavior, or when CL-011 (which changes during a placement need a new approval, still open from Evaluation 1) defines changes that restart the academic review.

## Trace links

AD-01; QS-08; BR-01, BR-03, BR-04, BR-06; V-04; lifecycle figure
