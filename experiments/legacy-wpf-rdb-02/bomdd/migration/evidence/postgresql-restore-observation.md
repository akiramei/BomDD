# PostgreSQL restore-control observation

Date: 2026-07-19  
DB Custodian: Experiment Operator (Codex)

1. 原版writerを停止した。
2. `traggo_prod`をcustom format、`--no-owner --no-acl`でdumpした。
3. 空の`traggo_restore_control`を作成した。
4. `pg_restore --exit-on-error`で復元した。
5. validatorへUSAGE/SELECTだけを付与した。
6. validatorのdefault transactionをread-onlyにした。
7. production相当DBのPUBLIC CONNECTをrevokeし、validator接続が拒否されることを確認した。
8. restore-controlへのINSERTがread-only transactionとして拒否されることを確認した。
9. schema、constraint、index、canonical queryを再測定した。

Dump SHA-256: `9b18cb620e0748cf7d103e50832f10aec184522b0eff13f563fc3f9ecef744d0`  
Restore result: PASS

