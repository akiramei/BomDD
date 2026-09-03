# Change Order — ECO-059(effort 序数へ none / max を追加 — ET-002 の Luna none 腕を投影可能にする)

> 裁定: user 2026-09-04「EFFORT_ORDER に none/max を足す ECO を起票して製造まで進めて」。裁定が gate 1 を兼ねる。
> 変更は `method/tools/effort-calibration.py` の序数 1 行+陽性対照 2 腕。**skill 新設 0・本文変更 0**。

## 担当設備(equipment)

- 製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

- ET-002 の plan(`bomdd/effort-trial-runner/plan-ET-002.yaml`・EXP-20260903-04)は Luna none / medium / high +
  Sol medium の 4 腕。現行の `EFFORT_ORDER` は `low / medium / high / xhigh` のみで、`none` を含む対は
  `project` が `unordered-effort` を返し、Luna 内 3 腕の effort 感度が投影されない(実測: 序数外ラベルの
  腕= selftest known-bad 8 が `unordered-effort` を返すことを ECO-058 で確認済み)。
- GPT-5.6 系の effort 幅は `none / low / medium / high / xhigh / max`(user 提示の資料・未検証。codex exec
  `-c model_reasoning_effort=none` が応答することは 2026-09-03 に実測)。

## 1. 変更要求(製造対象)

1. `EFFORT_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3, "xhigh": 4, "max": 5}`。
2. selftest に **known-good 2 腕**を追加: (a) none fail / max pass → `supported`(low= none・high= max — 両端の
   序数と向き)(b) none pass / high fail → `unsupported`(序数追加が低/高の向きを壊していない)。
   known-bad 8(序数外 `turbo`)は据え置き。
3. docstring に序数を明記。**序数は要求した推論量の順序であり、到達 effort の順序ではない**(resolved= unknown)。

**採らない**: ET-002 の実施(別途・実タスク待ち)/ 序数の外部化(設定ファイル化)— 必要が実測されてから /
`unordered-effort` の挙動変更。

## 2. 影響なし予測(反証可能・製造前に凍結)

diff は effort-calibration.py 1 本+台帳系。ET-001 の記録(medium / high のみ)の投影結果は不変(序数の相対順が
変わらない)。self-conformance の判定不変(effort-calibration は組み込まれていない・C7/C13/C1 は触れない)。

## 3. 受入

- **V1**: `--selftest` PASS(known-good 3・known-bad 8)。**V2**: ET-001 の `project` が変更前後で同一の
  effort_sensitivity(unsupported ×2)を出す。**V3**: self-conformance 全 PASS。**V4**: CI 緑。**V5**: diff 窓。

## /preflight receipt(起動経路: 自発 — 既裁定の適用実装)

- 分類= 既裁定の適用実装(continuation)。baseline `7aac533`= **confirmed**(HEAD・origin/main 一致・作業木 clean)/
  次番 059= **confirmed**(register 末尾= 058)/ 変更対象の実在= **confirmed**(effort-calibration.py:71)。
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-04)

- diff 監査の窓: baseline `7aac533` → head は受入時に確定。
- 序数を 6 段へ・known-good 2 腕を追加・docstring 更新。
- **V1 実測**: `--selftest` **PASS(known-good 3・known-bad 8)** — known-good 2/3 は序数変更前は `unordered-effort` になる腕
  (変更で初めて通る= 変更固有の理由で赤くなる対照)。**V2 実測**: ET-001 の `project` は変更前(git stash)/後で同一
  (`effort_sensitive: unsupported` ×2)。実行器 `bomdd/effort-trial-runner` の selftest も PASS。
- **製造中の手順逸脱(自己捕捉)**: V2 の前後比較で `git stash` / `stash pop` を、self-conformance がバックグラウンドで
  走っている最中に実行した(作業木が数秒間 baseline に戻った)。その検査結果は信頼せず、staged tree で最終検査を
  やり直してから commit した(witness は最終検査のもの)。是正= 検査中は作業木を触らない。

### 較正 receipt(/calibrate 自己適用 — trigger 3: 検査器の変更直後。二軸)

- 査定した主張と判定:
  1. 「none / max を含む対が序数どおりに supported / unsupported へ分類される」— **observed / 適格**
     (known-good 2・3 が両端と向きを実測)。
  2. 「序数外ラベルは引き続き `unordered-effort`」— **observed / 適格**(known-bad 8 据え置き・PASS)。
  3. 「ET-002 で Luna none 腕の effort 感度が測れる」— **unknown(理由コード: 未実行)** — 本 ECO は投影可能性
     までで、感度の有無は ET-002 の観測。
- 検出した計器欠陥: 0 件(本変更は序数の拡張で、ECO-058 の文字列比較欠陥の再演はない — known-good 3 が向きを検査)。
- 検出力の限界: 序数は**要求値**の順序であり到達 effort は観測不能(限界 (2))。`none` が本当に推論ゼロかは
  本ツールでは測れない(reasoning tokens は receipt に残るが、序数の根拠にはしない)。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | docstring の序数とコードの一致 |
  | Q2 | asked | observed/適格 | 実測 | known-good 3・known-bad 8 |
  | Q3 | asked | observed/適格 | 実測 | known-good 2/3 は序数変更で初めて通る腕(変更前は unordered) |
  | Q4 | asked | observed/適格 | 実測 | selftest は本体 project を合成記録で実行 |
  | Q5 | asked | observed/適格 | 実測 | 序数外は率を出さず unordered-effort |
  | Q6 | asked | observed/適格 | 実測 | exit code 経由 |
  | Q7 | asked | observed/適格 | 実測 | --selftest が常設陽性対照 |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | 投影の tool_hash が変わる(序数変更が来歴に出る) |
  | Q10 | asked | observed/適格 | 読解 | 限界 (2) の再掲 |
  | Q11 | asked | observed/適格 | 実測 | 序数内/序数外をクラス別に |

## 5. CI 実測(V4)

- 対象 revision: `8427f24`(**origin/main と一致を確認**)
- run 識別子: 33774358682 — 結論: **PASS**(completed/success・headSha 照合済み)
- V3 = self-conformance 全 PASS を staged tree で観測してから push(pre-push hook + witness)。

## 6. クローズ

- diff 監査の窓: baseline `7aac533` → head `8427f24`(**窓閉鎖**)。窓内は effort-calibration.py+台帳系(order・register・
  improvements.md)のみ — 影響なし予測が的中(ET-001 投影不変・self-conformance 判定不変)。
- 受入: V1(selftest 3/8)/ V2(投影の前後同一)/ V3(全検査緑)/ V4(CI 緑)/ V5(窓)成立。較正 receipt は §4(行別 asked/NA つき)。
- このクローズが支持しないもの: ET-002 で Luna none 腕の effort 感度が測れること(未実行)/ `none` が到達側で推論ゼロであること
  (観測不能)/ 序数の外部化の要否(必要が実測されてから)。
