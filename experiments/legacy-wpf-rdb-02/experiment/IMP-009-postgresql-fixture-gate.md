# IMP-009 — PostgreSQL fixtureを迷わず検査できるようにする

## 一件だけの問題

Version 1.2のGateはSQLite schema 1.0だけを受け付けた。作業者が正しいPostgreSQL dump、復元DB、schema、代表値を用意しても、`unexpected fixture manifest schema 1.1`で停止した。作業者自身にmanifest形式とclient-server検査方法を設計させる状態だった。

## 変更

- PostgreSQL専用`baseline-fixture-postgresql-manifest.json`を追加した。
- `database_engine`がSQLiteかPostgreSQLかでコピー元を一意に示した。
- Gateが固定hashの`psql`、`pg_dump`、`pg_restore`を使い、custom dump catalog、read-only、server major、constraint、index、live schema hash、canonical queryを復元検査DBで再検査するようにした。
- passwordはmanifestへ記録せず、`BOMDD_*`環境変数だけを許可した。
- 通常新規開発には配置せず、明示的に有効化した移行案件の`.templates`と凍結工具だけへ配布した。

## 前後比較

| 条件 | Version 1.2 | Version 1.3 |
|---|---|---|
| 正常PostgreSQL基準線 | 未対応schemaで停止 | MIG-10 PASS |
| credential未設定 | 検査不能 | 明示的Red |
| canonical値差 | 検査不能 | expected/actual付きRed |
| 本番相当DB誤指定 | 検査不能 | CONNECT権限拒否でRed |
| SQLite退行 | 基準 | 中央selftest、第一実験MIG-10ともPASS |

## 判定

有効。`INT-201`一件に対して変更を一件だけ行い、正常系と変異系で効果を分離して確認した。手引きはVersion 1.3とする。配布PDFはVersion 1.2のため、次の独立作業で再生成する。
