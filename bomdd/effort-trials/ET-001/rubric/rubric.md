# ET-001 rubric(封印 — run 開始前に確定・以後不変)

- oracle: `method/tools/self-conformance.py` の `converge_verdict(text, eco_no)` @ `00a3190bc6fc1ed51a7d5c118ec09400206ee5c2`
  (sha256 `4eb445b08996ba08dea7254087943f80d3f982c9ee8dc9d60a57ed39c825bb7c`)
- 合否: 12 検体すべてで `Sxx: PASS|FAIL` の判定が期待と一致したとき **pass**、1 件でも不一致・欠落・
  形式違反があれば **fail**(閾値なし — 部分点は評価 receipt に持ち込まない)
- 症状語彙: 不一致の検体に対応する語(下表)+ `missing-verdict`(判定行なし)+ `format-violation`
  (同一検体に相反する判定行、または判定行の書式外)

| 検体 | eco_no | 期待 | 誤答時の症状語 | oracle 理由 |
|---|---|---|---|---|
| S01 | 60 | FAIL | `miss-hard-positive` | converge-required(open-gate)だが収束 receipt の見出し+本体ラベル(判定/起動経路/round/未収束事項/DoD ✔✘)が揃っていない — 平文の言及・フェンス内の様式例は receipt ではない |
| S02 | 60 | PASS | `miss-heading-label` | ok |
| S03 | 40 | PASS | `miss-legacy-rule` | ok |
| S04 | 60 | FAIL | `miss-new-rule-labels` | converge-required(open-gate,recommended-option)だが収束 receipt の見出し+本体ラベル(判定/起動経路/round/未収束事項/DoD ✔✘)が揃っていない — 平文の言及・フェンス内の様式例は receipt ではない |
| S05 | 60 | PASS | `miss-grounded-exemption` | ok |
| S06 | 60 | FAIL | `miss-fence-declaration` | converge-required(open-gate,recommended-option)だが収束 receipt の見出し+本体ラベル(判定/起動経路/round/未収束事項/DoD ✔✘)が揃っていない — 平文の言及・フェンス内の様式例は receipt ではない |
| S07 | 60 | FAIL | `miss-declared-required` | converge-required(declared:required)だが収束 receipt の見出し+本体ラベル(判定/起動経路/round/未収束事項/DoD ✔✘)が揃っていない — 平文の言及・フェンス内の様式例は receipt ではない |
| S08 | 60 | FAIL | `miss-fenced-hard-positive` | converge-required(adjudication-request)だが収束 receipt の見出し+本体ラベル(判定/起動経路/round/未収束事項/DoD ✔✘)が揃っていない — 平文の言及・フェンス内の様式例は receipt ではない |
| S09 | 60 | FAIL | `miss-conflict-precedence` | 根拠なき not-required 宣言(欠落: decided-by)だが hard-positive 実在: adjudication-target |
| S10 | 60 | FAIL | `miss-body-boundary` | converge-required(open-gate,recommended-option)だが収束 receipt の見出し+本体ラベル(判定/起動経路/round/未収束事項/DoD ✔✘)が揃っていない — 平文の言及・フェンス内の様式例は receipt ではない |
| S11 | 60 | FAIL | `miss-unclosed-fence` | converge-required(open-gate,recommended-option)だが収束 receipt の見出し+本体ラベル(判定/起動経路/round/未収束事項/DoD ✔✘)が揃っていない — 平文の言及・フェンス内の様式例は receipt ではない |
| S12 | 60 | PASS | `false-fail-control` | ok |
