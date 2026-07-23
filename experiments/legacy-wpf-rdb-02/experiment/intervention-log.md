# 手引き介入ログ EXP-LWR-002

手引き、template、`status`、`next`だけでは作業を一意に継続できない時点で、解決前に記録する。

| ID | Step | 観測 | 必要だった介入 | 分類 | 改善状態 |
|---|---|---|---|---|---|
| INT-201 | STEP-013 / ART-DB-BASELINE受入 | PostgreSQL dump、復元DB、canonical query証跡を用意しても、凍結Gateが `unexpected fixture manifest schema: bomdd-legacy-wpf-baseline-fixture/1.1` で停止した | 作業者がvalidator形式を設計せずに済むPostgreSQL専用templateと、復元検査DBをread-onlyで検査するGate実装を追加した | 方法欠落 | 完了。正常受入と3変異Redを確認 |
