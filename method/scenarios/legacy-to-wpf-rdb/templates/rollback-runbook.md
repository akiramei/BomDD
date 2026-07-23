# Production Rollback Runbook

## Rollback triggers

| Trigger ID | Observable condition | Measurement/evidence | Decision owner |
|---|---|---|---|
| RB-001 | Target cannot start within declared timeout | | Migration Owner |
| RB-002 | DB reconciliation differs outside tolerance | | DB Custodian |
| RB-003 | Critical user journey fails smoke | | Acceptance Owner |
| RB-004 | Uncontrolled concurrent writers detected | | DB Custodian |
| RB-005 | Data corruption or partial transaction observed | | DB Custodian |

## Execution steps

| Order | Owner | Action/command | Expected result | Evidence | Timeout | Failure escalation |
|---:|---|---|---|---|---|---|
| 1 | | Stop target writes | no target writer | | | |
| 2 | | Preserve incident evidence | logs and DB snapshot retained | | | |
| 3 | | Restore declared DB point if required | DBP oracle passes | | | |
| 4 | | Re-enable current system | healthy | | | |
| 5 | | Run current-system smoke | pass | | | |
| 6 | | Reconcile DB | within tolerance | | | |
| 7 | | Announce rollback completion | signed | | | |

## Post-rollback

- Incident/CAPA ID:
- Evidence preserved at:
- New migration position:
- Resume STEP:
- Owner:

