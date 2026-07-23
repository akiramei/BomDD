# DB Schema Intent - <プロジェクト名>

この文書は DDL の写しではなく、DB/永続化の意図、制約、移行方針を BOM と PLM に読ませるためのテンプレートである。DB があるプロジェクトでは、DDL の前にこの文書を作る。

## 1. 永続化の目的

- DB を使う理由:
- 永続化する業務事実:
- 永続化しないものと理由:
- データ保持期間:
- 監査、復旧、移行の要否:

## 2. Entity

| ID | Entity | Purpose | Requirement refs | E-BOM | M-BOM | Control Plan |
|---|---|---|---|---|---|---|
| DB-ENT-001 | `<EntityName>` | <何を表すか> | REQ-xxx | E-PERSISTENCE-001 | M-PERSISTENCE-001 | CP-PERSISTENCE-001 |

## 3. Fields

| ID | Entity | Field | Type intent | Required | Constraints | Requirement refs |
|---|---|---|---|---|---|---|
| DB-FLD-001 | DB-ENT-001 | `id` | stable identifier | yes | unique, immutable | REQ-xxx |
| DB-FLD-002 | DB-ENT-001 | `created_at` | UTC timestamp | yes | literal-Z ISO-8601 | REQ-xxx |

## 4. Invariants

| ID | Invariant | Applies to | E-BOM | Control Plan |
|---|---|---|---|---|
| INV-DB-001 | <例 active booking は同じ room/time range で重複しない> | DB-ENT-001 | E-BOOKING-RULES-001 | CP-BOOKING-RULES-001 |

## 5. DDL / Migration refs

| ID | Kind | Path | Purpose | Related refs |
|---|---|---|---|---|
| DB-DDL-001 | ddl | `bomdd/db/ddl/initial.sql` | initial schema | DB-ENT-001 |
| DB-MIG-001 | migration-intent | `bomdd/db/migrations/001-<name>.md` | <何を変えるか> | REQ-xxx / E-xxx |

## 6. K-BOM candidates

| K-BOM candidate | Knowledge | Risk if implicit |
|---|---|---|
| K-DB-ENGINE-001 | <例 SQLite transaction / datetime / foreign key policy> | <工場ごとに分岐する危険> |

## 7. Acceptance intent

| CP candidate | What to verify | Depth | Fixture |
|---|---|---|---|
| CP-PERSISTENCE-001 | schema can store and retrieve required entity without loss | L3 | <acceptance harness> |
| CP-MIGRATION-001 | migration preserves existing fixture data | L3 | `bomdd/db/migrations/<fixture>` |

## 8. TraceLink

| TraceLink | From | Relation | To | Evidence |
|---|---|---|---|---|
| TL-DB-E-001 | DB-ENT-001 | satisfies | E-PERSISTENCE-001 | `bomdd/db/schema-intent.md` |
| TL-DB-M-001 | DB-ENT-001 | realizes | M-PERSISTENCE-001 | `bomdd/32-mbom.yaml` |
| TL-DB-CP-001 | DB-ENT-001 | verifies | CP-PERSISTENCE-001 | `bomdd/33-control-plan.yaml` |

## 9. Unresolved Questions

| ID | Question | Severity | Owner | Affected refs | Status |
|---|---|---|---|---|---|
| UQ-DB-001 | <例 既存データの migration 互換性をどこまで保証するか> | blocker / non-blocker | human / AI | DB-MIG-001 / CP-MIGRATION-001 | open |

## 10. PLM-ready checklist

- 全 Entity が `DB-ENT-*` ID を持つ。
- 全 Field が `DB-FLD-*` ID を持つ。
- Entity が REQ、E-BOM、M-BOM、Control Plan へ接続されている。
- DB エンジンや日時、transaction、migration convention は K-BOM 候補になっている。
- migration がある場合、移行専用 Control Plan がある。
