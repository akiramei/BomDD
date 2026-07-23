# MIG-10 artifact review

2026-07-19、Experiment Operator (Codex) が次を確認した。

- source lock、再現build、実行境界が `current-baseline.md` と `baseline-build.log` に一致する。
- PostgreSQL custom dump を空の復元検査DBへrestoreできる。
- 復元検査者はread-onlyで、本番相当DBへ接続できない。
- canonical query、schema hash、constraint、indexの観測値がDB基準線に一致する。
- login、populated list、alternate calendar viewの画像・DOM・DB証跡が観測索引に一致する。
- accepted evidenceにpasswordやraw runtime logを含めていない。
