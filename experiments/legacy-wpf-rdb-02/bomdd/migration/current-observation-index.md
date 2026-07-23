# Current Observation Index — Traggo PostgreSQL

Source: Traggo v0.8.3 / commit `6321119c` / PostgreSQL 16.14  
Observed: 2026-07-19

| Observation ID | State | Surface | Screenshot | Semantic evidence | Claim |
|---|---|---|---|---|---|
| OBS-CURRENT-001 | empty | unauthenticated Login | `evidence/current-ui/OBS-PG-LOGIN-001.jpg` | `evidence/current-ui/OBS-PG-LOGIN-001.md` | Login form and source/version boundary are visible |
| OBS-CURRENT-002 | populated | Timesheet / List | `evidence/current-ui/OBS-PG-LIST-001.jpg` | `evidence/current-ui/OBS-PG-LIST-001.md`, `evidence/baseline-db-observation.md` | `project:experiment` and completed span are visible and backed by restored rows |
| OBS-CURRENT-003 | alternate-view | Timesheet / Calendar | `evidence/current-ui/OBS-PG-CALENDAR-001.jpg` | `evidence/current-ui/OBS-PG-CALENDAR-001.md`, `evidence/baseline-db-observation.md` | Calendar week and the recorded event state exist |

観測は原版UIから行った。DB主張はproduction相当DBではなく、同じdumpを復元したrestore-control DBのread-only queryで再確認する。
