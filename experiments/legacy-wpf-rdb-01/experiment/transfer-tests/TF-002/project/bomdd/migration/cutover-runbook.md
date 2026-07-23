# Production Cutover Runbook

## Frozen identification

- Target artifact/version/hash:
- Current system version:
- DB backup procedure/version:
- Scheduled window:
- Migration Owner:
- DB Custodian:
- Acceptance Owner:
- Rollback deadline:

## Go/No-Go prerequisites

| Check | Required evidence | Result | Approver |
|---|---|---|---|
| MIG-80 Gate Green | | | |
| Restore test passed | | | |
| Target package verified | | | |
| Monitoring ready | | | |
| Rollback personnel present | | | |

## Execution steps

| Order | Owner | Action/command | Expected result | Evidence | Timeout | Failure action |
|---:|---|---|---|---|---|---|
| 1 | | Announce start | | | | Stop |
| 2 | | Stop current writes | single writer confirmed | | | Rollback |
| 3 | | Create final backup | backup ID recorded | | | Stop |
| 4 | | Deploy target | expected hash | | | Rollback |
| 5 | | Start target | healthy | | | Rollback |
| 6 | | Run smoke | all pass | | | Rollback |
| 7 | | Run DB reconciliation | all pass | | | Rollback |
| 8 | | Record Go decision | signed | | | Rollback |

No unrecorded command may be introduced during production cutover. Record it as `EX-CUTOVER-003` before use.

