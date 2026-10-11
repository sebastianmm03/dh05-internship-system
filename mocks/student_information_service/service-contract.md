# Simulated Student Information Service

The Student Information Service is authoritative for student identity, academic program,
enrollment status, completed credits, academic average, academic standing, and prior
placement participation.

Suggested operation:

```http
GET /mock/student-information/students/{student_id}
```

The internship system may preserve eligibility decisions and source timestamps, but it
should not become the authoritative academic-record system.
