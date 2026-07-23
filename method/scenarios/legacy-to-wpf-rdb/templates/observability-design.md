# Observability Design

| OBS ID | Signal/event | Fields and correlation | PII/secret handling | Destination/retention | Alert/SLO | Diagnostic runbook | Owner |
|---|---|---|---|---|---|---|---|
| OBS-001 | startup/version/config identity | | | | | | |
| OBS-002 | unhandled exception/crash dump | | | | | | |
| OBS-003 | DB query/transaction failure | | | | | | |
| OBS-004 | external integration failure | | | | | | |
| OBS-005 | UI hang/slow operation | | | | | | |
| OBS-006 | install/update/rollback | | | | | | |
| OBS-007 | security/audit event | | | | | | |

Every user-visible failure must produce a support-safe correlation ID. Logs and crash dumps must not contain credentials or unapproved customer data.

