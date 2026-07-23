# EX-DB-001 authentication resolution

- 対象: `EX-DB-001-20260719T113339158094Z`
- 原因: Traggo v0.8.3 が使用する旧 PostgreSQL driver は SCRAM authentication response 10 を処理できなかった。
- 解決: `traggo_owner` の localhost IPv4 接続だけを MD5 認証に限定した。`traggo_validator` は SCRAM のまま維持した。
- 安全境界: `traggo_validator` は `default_transaction_read_only=on`、本番相当 `traggo_prod` への CONNECT 不可、復元検査用 `traggo_restore_control` の SELECT のみ許可した。
- schema: 既存RDB流用の前提に合わせ、Traggo model の外部キー依存順で既存schemaを再構成した。製品コードは変更していない。
- 確認: 元Web UIが HTTP 200 で起動し、login、tag、time span、calendar を観察した。
- 復元確認: custom-format dump を空の `traggo_restore_control` へ復元し、canonical query、未検証constraint、無効index、読取専用状態を確認した。
- 秘密情報: password は証跡へ記載していない。無視対象runtime logは受入証跡に含めない。

参照:

- `bomdd/migration/evidence/EX-DB-001-auth-observation.md`
- `bomdd/migration/evidence/baseline-schema.sql`
- `bomdd/migration/evidence/baseline-db-observation.md`
- `bomdd/migration/evidence/postgresql-restore-observation.md`
