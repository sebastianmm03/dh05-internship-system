# Dataset Notes

## Source interpretation

- `data/reference/` contains relatively stable placement references.
- `data/raw/` contains spreadsheet-like exports from several offices.
- `data/scenarios/` identifies situations to analyze; scenarios do not prescribe solutions.
- `mocks/` describes simulated authoritative student and employer services.

## Known limitations

The source data intentionally contains:

- one legacy program code;
- an employer-selected student without academic approval;
- an approved placement distinct from an active placement;
- an expired employer agreement;
- missing insurance evidence;
- incomplete work-plan approval;
- multiple applications for one student;
- rejected and ineligible applications retained historically;
- reported hours that differ from confirmed hours;
- an overdue employer evaluation;
- mixed student-visible and restricted evaluation comments;
- actual duties diverging from the approved work plan;
- a placement with nearly complete hours but incomplete academic closure evidence.

Preserve raw evidence and document any normalization, validation, and migration decisions.
