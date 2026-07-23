# Phased Customer Rollout Plan

## Cohort order

| Order | Cohort | Customers/devices/versions | Entry checks | Monitoring window | Exit checks | Stop trigger | Rollback window | Owner |
|---:|---|---|---|---|---|---|---|---|
| 1 | COHORT-CANARY | | | | | | | |

## Version coexistence

- Minimum/maximum supported client versions:
- DB compatibility across version skew:
- Offline client rejoin behavior:
- Configuration/user-profile migration and downgrade:
- Legacy installer/update suppression:
- Single-writer enforcement during each cohort:

## Fixed rule

Do not start the next cohort until the previous cohort has completed its monitoring window and exit checks. A schedule date alone never advances a cohort.

