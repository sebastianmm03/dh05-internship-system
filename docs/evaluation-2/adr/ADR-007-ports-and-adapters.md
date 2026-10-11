# ADR-007 - Ports and adapters for identity, student information and employer directory

**Status:** Selected  
**Date and owner:** 2026-09-24, revised 2026-10-11, Sebastián Mercado (architecture owner)  
**Drivers:** AD-05, QR-04, ASM-002, ASM-003

## Context

The Student Information Service is authoritative for program, credits, average, standing and enrollment; the Employer Directory is authoritative for organization identity and agreement summary. Both are simulated and fail with 404, 409 and 503. The starter identity mock uses a different file name (EU-04).

## Decision

The core defines ports (StudentInformationPort, EmployerDirectoryPort, IdentityPort) in the shared kernel (horizon/shared/ports.py), so that any module can depend on a port without depending on M-11. Adapters, which live only in M-11, implement them for the mocks and translate their payloads into internal types, recording the source timestamp. Failure behavior is decided per use case: eligibility check -> keep the application as ELIGIBILITY_PENDING and retry (fail soft); 409 stale profile -> manual review; activation agreement check -> refuse the activation (fail closed); unknown organization or student (404) -> business error shown to the user. Values returned by a port (StudentProfile, AgreementSummary) are transient snapshots used for one decision; they are not stored as master data, and DH-05 never becomes the authoritative source.

## Alternatives

Call the mock endpoints directly from services; copy student and employer data into our tables as master data.

## Rationale

The contracts say the internship system must not become the authoritative academic-record or agreement repository. Ports keep the core testable with fake adapters and let the university replace the mocks later.

## Consequences

Each adapter needs contract tests and failure tests. Values read may be stale; the port values carry read_at, and recording it with each decision is DESIGNED.

## Verification

tests/unit/test_reference_and_adapters.py; test_directory_down_means_activation_refused; architecture test: mocks imported only by M-11 and composition points.

## Reconsideration / supersession

When real institutional services are integrated, or if a service adds events/webhooks.

## Trace links

AD-05; QS-05, QS-08; BR-02; FM-02..FM-05; TB-2
