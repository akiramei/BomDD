[INFORM / COMPLETE]
REJECT IA-07 — `a3c95ee..c5ea61d` の差分に、指定された README と order 以外の r2 検査報告が含まれます。

- range: 是正確認＋回帰（指定項目 1〜4 のみ）
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol / r1・r2 と同系統の別セッション
- 対象 revision: `c5ea61d08250a4cabf4d19cbe5c205b1e7bff480`
- commit: 0
- リポ内ファイル書込み: 0
- 外部 API: 呼び出しなし
- `jev_qual_0*.py`: 実行なし
- human_action: none
- execution: COMPLETE — 指定範囲の判定を完了

開始時 `git status --short`:

```text
（出力なし）
```

終了時 `git status --short`:

```text
（出力なし）
```

| 項目 | 観測 | 判定 |
|---|---|---|
| 1 / IA-06 | README 冒頭に、旧3ファイルは SHA-256 の先頭16桁、`results-03b.jsonl` 以降は64桁との注記あり。全行解析結果は旧3ファイルが順に78/78、150/150、27/27で小文字16進16桁、03bが27/27で小文字16進64桁。JSON解析エラー・異なる桁数は0。 | **PASS（是正済み）** |
| 2 / 是正差分 | `git diff --stat a3c95ee c5ea61d...` は3ファイル・88 insertions。README（4行）とorder §5.2（8行）に加え、`independent-inspection-eco-080-r2.md`（76行）が追加されている。テンプレ・スクリプト・JSONL・register の差分は0だが、「README.md と order のみ」ではない。 | **FAIL（IA-07）** |
| 3 / §3不変 | `git diff --unified=0 0e50b2f c5ea61d... -- bomdd/60-change-order-eco-080.md` に§3のhunkなし。両revisionから抽出した§3は各8行、完全一致し、SHA-256も同じ `f4b54f795aba095505492844eed87cb8053106d2eedc873eb71ba2e2cd46fe90`。 | **PASS（退行なし）** |
| 4 / 窓 | `0e50b2f..c5ea61d` は12ファイル・674 insertions / 4 deletions。全12ファイルが指定allowed_paths内。範囲外パスは0。 | **PASS（退行なし）** |

## 較正 receipt

### 査定した主張と判定

- 「IA-06が是正された」: **observed × 適格**。README注記と対象revision内のJSONL全282行が整合。
- 「r2でPASSだった指定回帰範囲に退行がない」: **observed × 不適格**。§3と全体窓は適合したが、是正差分の限定条件にIA-07がある。
- 「対象revisionをACCEPTできる」: **observed × 不適格**。項目2のFAILにより受入根拠として使用不可。

### 計器欠陥

- 製品側の検査器欠陥: なし。
- 検査コマンド構築上の欠陥: 初回の `git rev-parse ...^{commit}` でPowerShellによる解釈を考慮せず、3件ともexit non-zeroとなった。revision式を引用符で囲んで再実行し、3 revisionすべてを解決した後に測定したため、判定への影響なし。

### battery

| 問い | 記録 |
|---|---|
| Q1 | asked — READMEの主張をJSONL全行および実diffと照合 |
| Q2 | NA — known-good/known-badによる検査器較正は今回の限定range外 |
| Q3 | asked — 4項目を個別判定し、一括PASSに丸めず |
| Q4 | asked — `git show <target>:<path>` から対象revisionのREADME・JSONLを直接入力 |
| Q5 | asked — JSON解析エラー、欠測、コマンド失敗をPASSに算入せず |
| Q6 | asked — 各コマンドの終了と出力を観測後に次の判定へ進行 |
| Q7 | NA — 常設検査器の変更・健全性主張は今回の対象外 |
| Q8 | NA — 予防ゲート・免除は指定range外 |
| Q9 | asked — 対象full SHAを解決し、対象revisionを明示して全データを取得 |
| Q10 | asked — 下記「検出力の限界」に記録 |
| Q11 | asked — 旧3ファイルと03bを別クラスに分けて全行集計 |

### 検出力の限界

- `state_sha256` は指定どおり桁数と小文字16進形式を測定した。各値を元のstateから再計算し、実際のSHA-256またはその接頭辞であることまでは測っていない。
- 外部API原応答との同一性は測っていない。
- 指定range外の新規境界探索、IA-01〜IA-05の再実行、Jev設備認定全体は判定していない。
- 項目2はブリーフの「README.md と orderのみ」を字義どおり適用した。r2報告を例外扱いできるとの明示はない。

## 範囲外の観察

- なし。