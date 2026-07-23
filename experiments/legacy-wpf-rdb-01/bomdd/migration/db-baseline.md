# Existing RDB Baseline

## Identification

| Item | Frozen value | Evidence |
|---|---|---|
| DB engine/version | SQLite; inspected using SQLite CLI 3.49.1 | `bomdd/migration/evidence/environment-inventory.md` |
| Source snapshot time | 2026-07-19T02:46:48Z after original app stopped | fixture file metadata and observation log |
| Schema hash | SHA-256 `b74799d39cabfc458d18beed7c92d1401bc4fafed04267e7701d01bf57d8d804` | normalized `sqlite_master` query; `baseline-schema.sql` |
| Anonymous fixture ID | `TRAGGO-BASELINE-001` | `fixtures/baseline/traggo.db` |
| Fixture/backup hash | SHA-256 `308b5feebc0eed2be1ac781698f20bee2fd771fbd61a298e8e5f4e1544237458` | `baseline-db-observation.md` |
| Restore test result | PASS: same hash, integrity ok, FK violations 0, canonical row count 1 | `baseline-db-observation.md` |
| Machine-checked fixture closure | fixture, restore copy, schema, observations and canonical query | `bomdd/migration/evidence/baseline-fixture-manifest.json` |

Fixture contains only synthetic experiment data. Password hash and generated device token are not extracted into text evidence.

## Object counts

| Object type | Count | Inventory evidence |
|---|---:|---|
| application table | 10 | `baseline-schema.sql` |
| application index | 7 | `baseline-schema.sql` |
| view | 0 | `sqlite_master` read-only query |
| trigger | 0 | `sqlite_master` read-only query |
| stored procedure/function | 0 | not supported as application objects in this SQLite fixture |
| AUTOINCREMENT declaration | 7 | `baseline-schema.sql` |
| role/permission set | 0 DB objects | file access is an OS deployment concern |

SQLite internal `sqlite_sequence` is not counted as an application table and must not be removed or recreated by the target.

## Backup and restore

1. Stop the only writer.
2. Copy `fixtures/baseline/traggo.db` to a new work directory.
3. Verify copied file SHA-256 before first use.
4. Run `PRAGMA integrity_check` and `PRAGMA foreign_key_check` read-only.
5. Connect the application only to the work copy.

Restore control `fixtures/restore-control/traggo.db` passed. The preserved fixture and restore control copy are evidence, not execution targets.

## Safety declaration

- Production DB was not modified during inventory: yes; no production DB exists in this experiment
- Baseline fixture is preserved read-only by procedure: yes
- Working tests use a disposable copy: yes
- Current and target systems have one declared writer: yes
