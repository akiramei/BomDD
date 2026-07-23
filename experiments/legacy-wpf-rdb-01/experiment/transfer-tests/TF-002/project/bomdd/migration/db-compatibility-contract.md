# Existing RDB Compatibility Contract

## 1. Scope and writer policy

- Reused DB engine and version:
- Schema change allowed in initial migration: no
- Verification DB: anonymous disposable copy
- Production automated tests: forbidden
- Declared writer before cutover:
- Declared writer during cutover:
- Declared writer after cutover:
- Dual write: forbidden unless a separate approved design and Control Plan exist

## 2. Type and value semantics

| Contract ID | Entity/field | Current semantics | Target semantics | Equality/normalization rule | CP ref |
|---|---|---|---|---|---|
| DB-C-001 | | | | exact/normalized/tolerance | |

Cover NULL vs empty, collation, whitespace, timezone, date precision, decimal precision/scale, binary, enum/code values and generated keys.

## 3. Transaction and concurrency

| Contract ID | Use case | Transaction boundary | Isolation/lock | Timeout/retry | Idempotency | Failure rollback | CP ref |
|---|---|---|---|---|---|---|---|
| DB-TX-001 | | | | | | | |

## 4. Database-side behavior

| DB object | Trigger/procedure/view/default/generated behavior | Required side effect | Observation evidence | CP ref |
|---|---|---|---|---|
| | | | | |

## 5. Compatibility directions

| Test ID | Producer | Consumer | Fixture/action | Expected result | Required before | CP ref |
|---|---|---|---|---|---|---|
| DB-COMPAT-001 | current | target | current writes, target reads | semantic equality | MIG-60 | |
| DB-COMPAT-002 | target | current | target writes, current reads | semantic equality or approved one-way ruling | MIG-70 | |

## 6. Reconciliation

| Check ID | Scope | Method | Tolerance | Failure action | Evidence output |
|---|---|---|---|---|---|
| DB-REC-001 | row counts | | exact | Red/rollback | |
| DB-REC-002 | primary key set | | exact | Red/rollback | |
| DB-REC-003 | business invariant | | exact | Red/rollback | |
| DB-REC-004 | critical values/history | | exact or declared tolerance | Red/rollback | |

## 7. Approval

- DB Custodian:
- Specification Owner:
- Approved at:
- Evidence:

