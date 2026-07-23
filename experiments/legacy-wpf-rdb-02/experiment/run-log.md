# 実行ログ EXP-LWR-002

| Seq | 現在位置 | Action | 結果 | 証跡・備考 |
|---:|---|---|---|---|
| 001 | 選定前 | 第二実験で変更する変数を固定 | 同じTraggo/commitでRDBだけPostgreSQLへ変更 | `candidate-selection.md` |
| 002 | 環境準備 | PostgreSQL配布経路を確認 | PostgreSQL公式Windowsページが案内するEDB zipを採用 | `source-lock.json` |
| 003 | MIG-00 | Charter、profile、rolesを受入してGateを実行 | PASS、MIG-10 / STEP-011へadvance | `bomdd/migration/gates/MIG-00-result.json` |
| 004 | MIG-10 / STEP-011 | PostgreSQL 16.14をlocalhost:55432で起動しTraggoを接続 | `unknown authentication response: 10`でschema生成前に停止 | `bomdd/migration/evidence/EX-DB-001-auth-observation.md` |
| 005 | MIG-10 / STEP-011 | 旧driver互換認証をownerだけに限定し、既存schemaを依存順で再構成 | 元UIが起動し、代表tag/time spanを作成。validatorはSCRAM/read-only、本番相当DBへCONNECT不可 | `bomdd/migration/evidence/EX-DB-001-auth-resolution.md` |
| 006 | MIG-10 / STEP-013 | custom dumpを空のrestore-control DBへ復元 | users/tag/time spanとschema/constraint/indexが一致 | `bomdd/migration/evidence/postgresql-restore-observation.md` |
| 007 | ART-DB-BASELINE受入 | Version 1.2凍結GateへPostgreSQL manifestを入力 | schema 1.1を未対応として停止。`INT-201`を記録 | `intervention-log.md` |
| 008 | INT-201 | PostgreSQL専用templateとlive read-only validatorだけを中央/凍結工具へ追加 | 正常受入PASS。credential不足、代表値差、本番相当DB誤指定をすべてRed | `bomdd/migration/evidence/postgresql-gate-validation.md` |
| 009 | MIG-10 Gate | 4成果物、3承認、例外seal、blockerを検査しadvance | PASS、MIG-20 / STEP-021へ移動 | `bomdd/migration/gates/MIG-10-result.json` |
| 010 | 退行検査 | 中央selftestと第一実験MIG-00/MIG-10を再検査 | すべてPASS | `experiment-result.md` |
| 011 | handoff | MIG-20の現在不足とfuture artifactを分離して出力 | 再開Actionが一つに確定 | `bomdd/migration/handoffs/handoff-20260719T120837Z.md` |
| 012 | 終了処理 | 実験用PostgreSQLを`pg_ctl -m fast stop`で停止 | `server stopped` | runtimeはGit管理外のまま保持 |
