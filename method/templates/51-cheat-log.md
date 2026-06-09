# Cheat Log — <プロジェクト名>

> ずる = BOM/工程から導けず、慣習・暗黙知・未文書の判断で埋めた箇所。失敗でなく**観測データ**。
> 分類 C1–C6 は [cheat-taxonomy.md](../cheat-taxonomy.md)。
> **side**: factory(製造側)/ **harness(検査器側)** を区別する(v1.2: C2 は検査器にも出る)。

### CHEAT-<LOOP>-001 [C2] <一行要約>
- side: factory | harness
- 発生段: ①要求 ②仕様 ③BOM設計 ④工程 ⑤製造 ⑥合否
- 手法が与えなかったもの:
- 代替した従来技術/判断:
- 重大度: blocker / friction / minor
- 差分帰属: unspecified_bom_residue / specified_contract_miss / exploratory_unspecified_surface / observer_*
- 想定される手法的修正(次ループで BOM/工程/検査器をどう直すか):
- ユーザー裁定(Phase 5): 仕様に昇格 / 探索のまま / 対象外
