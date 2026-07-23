# Existing RDB Preservation Oracle

The preserved baseline fixture is never modified. Every run creates and tests a disposable copy.

| ID | Verification | Expected | Failure classification | Evidence |
|---|---|---|---|---|
| DBP-01 | Target starts against a disposable copy of the current DB | no schema/data loss | data-preservation miss | |
| DBP-02 | Read-only target scenario leaves DB unchanged | reconciliation exact | unintended write | |
| DBP-03 | Current-written fixture is read by target | semantic equality | compatibility miss | |
| DBP-04 | Target-written fixture is read by current | semantic equality or approved one-way ruling | compatibility miss | |
| DBP-05 | Failure inside transaction leaves no partial update | exact rollback | transaction miss | |
| DBP-06 | Retried operation does not duplicate business action | idempotent | duplicate effect | |
| DBP-07 | Key set, counts, critical values, history and invariants reconcile | declared tolerance | data-preservation miss | |
| DBP-08 | Backup restores into isolation and passes DBP-01..07 | all pass | rollback incapability | |

## Calibration

- Positive control result:
- Negative control/mutant:
- Expected failing rows:
- Actual failing rows:
- Acceptance Owner:
- DB Custodian:

