# 実験結果 EXP-LWR-002

判定: PASS  
完了日: 2026-07-19

## 結果

- 同一Traggo v0.8.3をPostgreSQL 16.14で起動し、代表データをcustom-format dumpへ固定した。
- 空の`traggo_restore_control`へ復元し、read-only validatorでschemaと代表値を再検査した。
- Version 1.2の停止点を`INT-201`として先に記録し、PostgreSQL fixture対応だけをVersion 1.3へ追加した。
- MIG-10 Gateは4成果物、3承認、解消済み例外seal、blockerゼロを確認してPASSし、MIG-20へadvanceした。
- handoffは現在のMIG-20不足とfuture artifactを分離し、再開ActionをSTEP-021一つに示した。
- 実験用PostgreSQLは検査完了後に停止した。

## 指標

| 指標 | 結果 |
|---|---|
| 手引き外介入 | 1件（INT-201） |
| 改善 | 1件（IMP-009） |
| dump | 23,495 bytes / `9b18cb620e0748cf7d103e50832f10aec184522b0eff13f563fc3f9ecef744d0` |
| restore | 空DBへ成功 |
| live checks | read-only/version/constraint/index/schema/canonical query PASS |
| 変異試験 | credential不足、代表値差、本番相当DB誤指定をRed |
| credential記録 | accepted成果物に0 |
| production相当DB | Gate後の代表値が基準線と一致 |
| 退行 | 中央selftest、第一実験MIG-00/MIG-10 PASS |

## 限界

- 第二実験の独立変数をRDB方式だけに保つため、WPF製品完成は評価していない。
- PostgreSQL一製品・一version・一operatorであり、MySQL/SQL Serverや複数作業者は未検証である。
- 旧Traggo driverのSCRAM非対応とschema生成順は製品固有例外であり、一般手順へ自動修復を追加していない。

## 後続作業

配布PDFのVersion 1.3再生成と全ページ検査は、独立した`IMP-010`として2026-07-20に完了した。
