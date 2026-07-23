# PostgreSQL baseline DB observation

Observed: 2026-07-19  
Connection: `traggo_validator` → `traggo_restore_control` only  
Transaction default: read-only

## Server and safety

| Check | Result |
|---|---|
| server_version_num | `160014` |
| default_transaction_read_only | `on` |
| production DB CONNECT | denied |
| INSERT probe on restore-control | denied: read-only transaction |
| unvalidated constraints | 0 |
| invalid indexes | 0 |

## Canonical query results

```text
APPLICATION-TABLE-COUNTS
1|1|1|1|0|0|0|0|0|0

VISIBLE-USER
1|admin|true

VISIBLE-TAG
project|1|#e6b3b3

VISIBLE-SPAN
1|2026-07-19 20:41:05+09|2026-07-19 20:41:19+09|2026-07-20 05:41:05+09|2026-07-20 05:41:19+09|32400|1|

VISIBLE-TAG-VALUE
1|project|experiment
```

Result: restored database values match the UI-created baseline.

