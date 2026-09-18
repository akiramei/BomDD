[INFORM / COMPLETE]
REJECT IA-06 — README に「第1回・第2回・第3回初版の `state_sha256` は16桁接頭辞」という注記がなく、是正が完了していません。

- range: 是正確認＋回帰（指定項目 1〜10 のみ）
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: `a3c95ee37fa1f96cc5772e32669d95e017f9841e`
- HEAD: 開始時・終了時とも対象 revision
- commit: 0
- 外部 API: 呼び出しなし
- リポ内ファイル書込み: 0
- smoke 一時生成先: `C:\Users\akira\AppData\Local\Temp\bomdd-eco080-r2-da503ea8872640cd8990e127f9daa19b\Smoke`（削除なし）

開始時 `git status --short`（exit 0）:

```text
（出力なし）
```

終了時 `git status --short`（exit 0）:

```text
（出力なし）
```

| 項目 | 観測 | 判定 |
|---|---|---|
| 1 / IA-01 | Pandoc 3.7.0.1、GFM 解析 exit 0。二部形の箇条書き後に空行があり、失敗5分類は独立した `Table` として解析された。 | PASS（是正済み） |
| 2 / IA-02 | `NEW_BODY["077"]` に `known-bad(実測): 実 map の 1 class から roles を外すと job selftest が FAIL(復元後 PASS)` が原文どおり存在。`temp map`・`一時 map` は0件。 | PASS（是正済み） |
| 3 / IA-03 | `build()` は `orig_section()` が返す原文見出しを newh0 に使用。`--list` exit 0で ECO-068=`## 3. 受入(製造時の候補)`、ECO-075=`## 3. 受入(候補)`。README §5 の定義とも一致。 | PASS（是正済み） |
| 4 / IA-04 | 9節をV項目単位で集計し、V項目45件・対応する `— 検査法:` 45件・欠落0。ECO-068 V1は折返し行に検査法を保持。 | PASS（是正済み） |
| 5 / IA-05 | テンプレに、UNMEASURABLEでは測定不能の原因と試みたコマンドを書き、PASSに数えないとの明記あり。 | PASS（是正済み） |
| 6 / IA-06 | `results-03b.jsonl` は27行、全27行が小文字16進64桁。一方、READMEには旧記録の短縮規則の注記なし。実データは `results.jsonl` 78/78、`results-02.jsonl` 150/150、`results-03.jsonl` 27/27が16桁であることを確認。order §5.1 が約束するREADME注記を満たさない。 | **FAIL（未是正）** |
| 7 / 自己適用 | `git diff --unified=0 0e50b2f..a3c95ee -- order` に§3のhunkなし。§4は別の「受入結果」行としてV1/V2を記録し、§3の条件行を書き換えていない。 | PASS（退行なし） |
| 8 / 第3回記録 | JSONL 27行、エラー0。orig=N9・planned 0・performed 9、new=N9・planned 9・performed 0、newh0=N9・planned 9・performed 0。README §6およびsummary-03bと一致。 | PASS（退行なし） |
| 9 / kit smoke | `bomdd-init.py` exit 0。生成された `bomdd/60-change-order.md` に二部形5行と、原因・試行コマンド・PASS非算入のUNMEASURABLE要件を確認。 | PASS（退行なし） |
| 10 / 窓 | 0e50b2f..対象revisionは11ファイル・586 insertions / 4 deletions。すべて指定allowed_paths内。変更されたorderはECO-080のみ。playbook、change-management.md、acceptance-evidence.md、既存orderに差分なし。 | PASS（退行なし） |

## 較正 receipt

### 査定した主張と判定

- 「IA-01〜IA-06がすべて是正された」: **observed × 不適格**。IA-01〜IA-05は是正済みだが、IA-06のREADME注記が欠落。
- 「r1でPASSだった範囲に退行がない」: **observed × 適格**。項目7〜10はすべてPASS。
- 「03bの記録数値がREADME・summaryと整合する」: **observed × 条件付き適格**。保存済みJSONL内の整合は成立するが、外部API原応答との同一性は検査禁止により未測定。

### 計器欠陥

- 製品側の検査器欠陥: なし。
- 検査コマンド構築時に正規表現の過剰エスケープと一時的なモジュール読込み失敗が各1回発生（exit 1）。いずれも書込み前で、単純化した独立コマンドを再実行してexit 0・同一対象の観測を完了したため、項目の測定成立性には影響なし。

### battery

| 問い | 記録 |
|---|---|
| Q1 | asked — README・テンプレ・スクリプト・記録の主張を実装と照合し、IA-06の未是正を検出 |
| Q2 | asked — orig/new/newh0の保存済み対照記録を確認。外部API再実行は範囲外 |
| Q3 | asked — IA-01〜IA-06を個別に測定し、一括PASSへ丸めなかった |
| Q4 | asked — `NEW_BODY`、`build()`、`--list`、JSONLを実入力経路として照合 |
| Q5 | asked — UNMEASURABLE規定、エラー件数、欠測を確認。UNKNOWNをPASSに算入せず |
| Q6 | asked — 本roundの各終了コードを直後に観測。過去API実行の時系列は未測定 |
| Q7 | asked — 保存済みorig対照は9/9 performed。API計器自体の再較正は未実施 |
| Q8 | NA — 予防ゲートと免除は指定range外 |
| Q9 | asked — HEADと対象full SHAを照合。03b fingerprintは27/27で完全な64桁 |
| Q10 | asked — 下記「検出力の限界」に記録 |
| Q11 | asked — orig/new/newh0を別クラスとして分離集計 |

### 検出力の限界

- 外部APIを再実行しておらず、JSONLが原応答を完全に保存しているかは測っていない。
- 第3回設計が結果受領前に固定された時系列は、成果物だけからは検証していない。
- GitHub上のMarkdown表示は未確認。表構造はPandoc GFMで測定した。
- 指定range外の新規境界探索、Jev設備認定全体、他の書き手への一般化は判定していない。

## 範囲外の観察

- なし。