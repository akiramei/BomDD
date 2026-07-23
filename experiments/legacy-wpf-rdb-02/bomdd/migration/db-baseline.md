# DB Baseline — PostgreSQL 16.14

状態: frozen candidate for MIG-10  
観測日時: 2026-07-19T11:41:19Z

## 1. 接続境界

| 用途 | Database | Role | 権限 |
|---|---|---|---|
| 原版のproduction相当 | `traggo_prod` | `traggo_owner` | schema owner / writer |
| Gate live検査 | `traggo_restore_control` | `traggo_validator` | CONNECT、USAGE、SELECT。default transaction read-only |

- host: `127.0.0.1`
- port: `55432`
- SSL: isolated localhost experimentのため`disable`
- credential: 成果物へ記録しない。実行時の`BOMDD_POSTGRES_PASSWORD`だけを使う
- validatorは`traggo_prod`へCONNECT不可

凍結原版のPostgreSQL driverはSCRAM認証応答を扱えないため、owner roleだけserver側でMD5 verifierを使う。validatorはSCRAM-SHA-256を使う。この互換設定は既存アプリの接続境界であり、移行先provider選定ではMIG-30の再確認対象とする。

## 2. Schema

実体tableは10件:

`users`, `tag_definitions`, `devices`, `time_spans`, `time_span_tags`, `user_settings`, `dashboards`, `dashboard_entries`, `dashboard_tag_filters`, `dashboard_ranges`

- schema-only dump: `bomdd/migration/evidence/baseline-schema-extracted.sql`
- file SHA-256: `24654ea7efb475000f295c1a1da2a294fa38db3453d3b689823b720401c6213c`
- `\\restrict` / `\\unrestrict`のrun固有行を除き、改行と行末空白を正規化したSHA-256: `eeaa4a0a9359c9083371a5e09e0fae7588704dd67cc8b57c186d0b9978e98fe6`
- unvalidated constraints: 0
- invalid indexes: 0

空DBで原版`AutoMigrate`を実行すると、`TagDefinition`が`User`より先に列挙されているためFK作成でtransactionが失敗する。既存RDB流用シナリオとして、凍結modelから依存順を固定した`baseline-schema.sql`をDB Custodianが適用し、原版が同じschemaを利用できることを確認した。移行先からschema生成は行わない。

## 3. Dump / restore

- format: PostgreSQL custom dump
- dump: `fixtures/baseline/traggo-postgresql.dump`
- SHA-256: `9b18cb620e0748cf7d103e50832f10aec184522b0eff13f563fc3f9ecef744d0`
- restore target: 空の`traggo_restore_control`
- restore owner: `traggo_owner`
- restore result: pass
- restore evidence: `bomdd/migration/evidence/postgresql-restore-observation.md`

## 4. Canonical values

| Query | Expected |
|---|---|
| application table counts | users=1, tag_definitions=1, time_spans=1, time_span_tags=1, devices=0, remaining=0 |
| visible tag | `project`, user 1, `#e6b3b3` |
| visible span | id 1, start `2026-07-19 20:41:05+09`, end `2026-07-19 20:41:19+09`, offset 32400, user 1 |
| visible tag value | time span 1, `project`, `experiment` |

詳細行は`baseline-db-observation.md`を正とする。

## 5. 禁止

- Gateから`traggo_prod`へ接続しない。
- manifestへpasswordまたは完全connection stringを書かない。
- restore-control DBを原版writerへ渡さない。
- dumpを上書きして同じfixture IDを使わない。
