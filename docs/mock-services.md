# Mock Services

## Identity service

Endpoint:

```http
GET /mock/identity/users/{user_id}
```

Development header:

```text
X-Mock-User-Id: HU-STU-1001
```

The service reads `data/reference/mock_users.json`.

## Student Information Service

Endpoint:

```http
GET /mock/institutional/students/{student_id}
```

Simulate unavailability:

```http
GET /mock/institutional/students/HU-STU-1001?simulate_failure=true
```

The service reads `data/reference/mock_students.json`.

## Ownership boundary

The mock Student Information Service is authoritative for the supplied student profile fields. A project system may cache or reference these values but should not silently become their authoritative source.
