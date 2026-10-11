# Definition of Done

A story is done when:

- [ ] The story's acceptance criteria (Given/When/Then) pass as automated tests, including at least one failure case (missing data, unauthorized user or failed dependency).
- [ ] Code merged into main through a pull request reviewed by another team member.
- [ ] CI is green: ruff and pytest.
- [ ] Access to the new endpoint is declared in the Access module and covered by at least one denial test.
- [ ] Every state change writes an audit entry (checked by test).
- [ ] Affected documents updated: ADR (new or superseded), module interfaces, traceability.
- [ ] No hard-coded program or placement-type rule; rules go to configuration.
- [ ] Demonstrable with the DH-05 data pack.
