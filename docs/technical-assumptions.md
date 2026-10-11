# Technical Assumptions

- The default environment is local development.
- SQLite is used only to make the starter immediately runnable.
- PostgreSQL is optional and does not imply that teams must select it.
- CSV and JSON files represent fictional current-system exports or integration messages.
- The generic `imported_records` table is temporary technical scaffolding, not the target domain schema.
- Development mock identity headers must never be treated as production security.
- External services may fail, return missing records, or provide stale data.
- All personal, institutional, and operational information is synthetic.
