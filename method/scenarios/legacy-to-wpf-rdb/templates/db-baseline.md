# Existing RDB Baseline

## Identification

| Item | Frozen value | Evidence |
|---|---|---|
| DB engine/version | | |
| Source snapshot time | | |
| Schema hash | | |
| Anonymous fixture ID | | |
| Backup ID | | |
| Restore test result | | |
| Machine-checked fixture closure | | `bomdd/migration/evidence/baseline-fixture-manifest.json` |

## Object counts

| Object type | Count | Inventory evidence |
|---|---:|---|
| table | | |
| view | | |
| trigger | | |
| stored procedure/function | | |
| index | | |
| sequence/identity generator | | |
| role/permission set | | |

## Safety declaration

- Production DB was not modified during inventory: yes / no
- Baseline fixture is preserved read-only: yes / no
- Working tests use a disposable copy: yes / no
- Current and target systems have one declared writer: yes / no

Before acceptance, copy `.templates/baseline-fixture-manifest.json` to `evidence/baseline-fixture-manifest.json`, replace every placeholder, and include it in the `ART-DB-BASELINE` acceptance evidence.
