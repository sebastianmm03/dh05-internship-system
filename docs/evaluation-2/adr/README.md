# Architecture decision register

| ID | Decision | Status | Drivers |
|---|---|---|---|
| ADR-000 | Adopt the Horizon common starter kit as technical baseline | Selected | C-01, C-03, C-06, AD-05 |
| ADR-001 | Use a modular monolith as architectural style | Selected | AD-01, AD-02, AD-03, AD-05, C-01, C-03 |
| ADR-002 | One relational database with module-owned tables and transactional commands | Selected | AD-01, AD-03 |
| ADR-003 | Explicit placement lifecycle with gated transitions | Selected | AD-01, AD-03 |
| ADR-004 | Versioned rule configuration evaluated through Strategy | Selected | AD-04, QR-05 |
| ADR-005 | Centralized relationship-based access with audience projections | Selected | AD-02, QR-01, QR-02 |
| ADR-006 | Append-only audit history and versioned records | Selected | AD-03, QR-03 |
| ADR-007 | Ports and adapters for identity, student information and employer directory | Selected | AD-05, QR-04, ASM-002, ASM-003 |
| ADR-008 | In-process domain events with a transactional outbox for side effects | Selected | AD-05, QR-04, AD-03 |
| ADR-009 | Do not adopt microservices, service mesh, serverless, low-code or RAG in this release | Selected | AD-01 to AD-05, C-01, C-05 |
| ADR-010 | Concurrent commands: conditional update on status and a correlation id per command | Selected | AD-01, AD-03 |

A later decision never rewrites an earlier one: it supersedes it with a new record.
