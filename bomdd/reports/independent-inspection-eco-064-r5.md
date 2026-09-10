# 判定: ACCEPT

対象 revision `ef88211c984064e43dae15d76c66549a734df042` に対する独立受入検査 r5 の結果、IA-10〜IA-12 の是正と IA-01〜IA-09 の指定回帰はすべて成立しました。新規不適合は確認していません。

## 検査個体・設備

- 対象 revision: `ef88211c984064e43dae15d76c66549a734df042`
- branch: `main`
- revision 突合: 開始時・終了時とも `git rev-parse HEAD` が指定値と一致
- 検査官設備: OpenAI Codex / GPT-5 系モデル（self-reported）
- 実行基盤: workspace-write。ただしリポジトリ内は読み取り専用で検査
- Codex CLI: `codex-cli 0.154.0`
- Python: `3.13.1`
- PyYAML: `6.0.3`
- OS: Windows
- 開始時 `git status --short`: 空
- 終了直前 `git status --short`: 空
- リポジトリ内の変更: なし
- `self-conformance.py`: ユーザー指定に従い未実行

## IA-10 — resolved

OS temp に検査個体を複製し、`instrument-change.instrument_paths` を置換して通常 CLI を実行した。

不正値:

| `instrument_paths` | exit | `required_skills.value` | source |
|---|---:|---|---|
| `[C:/absolute/*.py]` | 0 | `null` | `MAP_INVALID`・正規形でない |
| `[" method/tools/*.py"]` | 0 | `null` | `MAP_INVALID`・正規形でない |
| `["**"]` | 0 | `null` | `MAP_INVALID`・全一致、literal 区間なし |

全腕で traceback はなく、`skills_missing.value=null`、`stop_type.value=NONE` だった。非正規値を正常な非該当へ丸める r4 の挙動は再現しなかった。

正規値:

```text
["method/tools/*.py"]
exit: 0
required_skills.value: [calibrate, converge, preflight]
source: activation-map.yaml: design-synthesis, instrument-change, start
```

```text
["a/**/x.py"]
exit: 0
required_skills.value: [converge, preflight]
source: activation-map.yaml: design-synthesis, start
```

後者で `instrument-change` が非該当なのは ECO-064 の `affected_refs` と一致しないためであり、map 自体は `MAP_INVALID` にならず受理された。

## IA-11 — resolved

`verified-promotion.statuses` を置換して通常 CLI を実行した。

不正値:

| `statuses` | exit | `required_skills.value` | source |
|---|---:|---|---|
| `[Verified]` | 0 | `null` | `MAP_INVALID`・状態語彙外 |
| `[" verified"]` | 0 | `null` | `MAP_INVALID`・状態語彙外 |
| `["done"]` | 0 | `null` | `MAP_INVALID`・状態語彙外 |

全腕で traceback はなく、`skills_missing.value=null` だった。

正規値:

```text
["verified"]
exit: 0
required_skills.value: [calibrate, converge, preflight]
MAP_INVALID: なし
```

```text
["verified", "implemented"]
exit: 0
required_skills.value: [calibrate, converge, preflight]
source: activation-map.yaml: design-synthesis, instrument-change, start, verified-promotion
MAP_INVALID: なし
```

register の状態語彙との完全一致制約が成立している。

## IA-12 — resolved

同内容の map について、正順と `classes` の逆順で ECO-062 を実行した。

```text
正順:
required_skills.value: [calibrate, converge, preflight]
source: activation-map.yaml: design-synthesis, instrument-change, start, verified-promotion

逆順:
required_skills.value: [calibrate, converge, preflight]
source: activation-map.yaml: design-synthesis, instrument-change, start, verified-promotion
```

`required_skills` と source の class 列挙は完全一致し、いずれも辞書順だった。

## IA-01〜IA-09 回帰

- IA-01 — resolved: `statuses: 7` は exit 0、traceback なし、`required_skills=null`、source=`MAP_INVALID: statuses が非空の文字列配列でない`。
- IA-02 — resolved: `_glob_match("method/tools/sub/x.py", "method/tools/*.py")` は `false`。`*` は区切りを跨がない。
- IA-03 — resolved: map 実読で anchor は `register.status が statuses に含まれる` および `register.affected_refs ... instrument_paths ... に一致する`。契約意味は判定に使わない `contract_item` へ分離されている。
- IA-04 — resolved: source を `preflight.md#不存在` にすると exit 0、`required_skills=null`、source fragment 不存在を示す `MAP_INVALID`。
- IA-05 — environment / 未再実測: r1 の Git ownership による C14 測定不能は検査官環境帰属。本 r5 では指示により `self-conformance.py` を実行していない。
- IA-06 — resolved: source 末尾へ `;` を加えた空要素は exit 0、`required_skills=null`、`MAP_INVALID: source に空要素`。
- IA-07 — resolved: `id: [start]` は exit 0、traceback なし、`required_skills=null`、`MAP_INVALID: id が文字列でないか空`。
- IA-08 — resolved: `statuses: []` は exit 0、`required_skills=null`、`MAP_INVALID: statuses が非空の文字列配列でない`。
- IA-09 — resolved: `required_skills: [Preflight]` は exit 0、`required_skills=null`、`MAP_INVALID: スキル ID 'Preflight' が文法外`。

## V1 — 両 selftest

```text
python method/tools/bomdd-job.py --selftest
exit: 0
bomdd-job selftest PASS(...r4: instrument_paths 正規形・statuses 語彙・required 辞書順)
```

```text
python method/tools/bomdd-witness.py --selftest
exit: 0
bomdd-witness selftest PASS(...)
```

両 selftest は PASS した。

## V2 — ECO-062 / ECO-063 / ECO-064

```text
python method/tools/bomdd-job.py ECO-062 ECO-063 ECO-064 --json
exit: 0
```

| ECO | state | required_skills | skills_observed | skills_missing |
|---|---|---|---|---|
| ECO-062 | verified | `[calibrate, converge, preflight]` | `{preflight, converge, calibrate}` | `[]` |
| ECO-063 | verified | `[calibrate, preflight]` | `{preflight, converge, calibrate}` | `[]` |
| ECO-064 | implemented | `[calibrate, converge, preflight]` | `{preflight, converge}` | `[calibrate]` |

`required_skills` は辞書順。`skills_observed` と `skills_missing` は集合として r4 と同一だった。

## unknown 5 条件

| 条件 | exit | 実測 |
|---|---:|---|
| activation-map 不在 | 0 | required=`null`・`MAP_MISSING`、missing=`null` |
| `classes: []` | 0 | required=`null`・classes 配列なし、missing=`null` |
| self-conformance 不在 | 0 | required=`null`・source 実在検査の `MAP_INVALID`、observed/missing=`null` |
| order 不在 | 0 | required=`[calibrate, preflight]`・design-synthesis 判定不能、observed/missing=`null`、stop=`MISSING_INPUT` |
| PyYAML 不在（`python -S`） | 0 | stop=`MISSING_INPUT`・source=`PyYAML 不在` |

全腕で traceback はなかった。

## 停止語彙・引数処理

`b1882fa` と対象 revision の AST を比較した。

```text
STOP_VOCABULARY AST: identical
DERIVABLE_FROM_LEDGER AST: identical
select() AST: identical
main() AST: identical
```

停止語彙:

```text
NONE
NORMATIVE_RULING
VERIFICATION_FAIL
BOM_CONTRADICTION
CONVERGENCE_LIMIT
PREFLIGHT_HOLD
LEDGER_INCONSISTENT
MISSING_INPUT
```

台帳から導出可能な語彙:

```text
NONE
LEDGER_INCONSISTENT
MISSING_INPUT
```

停止語彙と引数処理に変更はない。

## diff 監査

```text
git diff --name-status b1882fa..ef88211c984064e43dae15d76c66549a734df042
```

実測:

```text
M bomdd/60-change-order-eco-064.md
M bomdd/60-change-register.yaml
A bomdd/reports/independent-inspection-eco-064-r4.md
M method/tools/bomdd-job.py
```

変更は `method/tools/bomdd-job.py` と台帳系（order、register、r4 報告）のみだった。

```text
git diff --name-status b1882fa..ef88211c984064e43dae15d76c66549a734df042 -- method/templates/product-profile/skills/activation-map.yaml
```

出力は空。`activation-map.yaml` に diff はない。

## 新規所見

なし。order §8.4 に従い、新規入力クラスの探索は実施していない。指定回帰中に偶然見つかった不適合もないため、IA-13 以降の採番はない。

## 一時領域

検査用の変更はすべて OS temp の `eco064-r5-*` 複製内で行った。

最初の一括 probe は測定後の結果表示時に CP932 の符号化エラーで exit 1 となったため証拠不採用とし、UTF-8 を明示して全腕を再実行した。両実行とも一時ディレクトリの終了処理は完了した。

終了時確認:

```text
eco064-r5-* temp: 0 件
削除拒否・残置パス: なし
git status --short: 空
git rev-parse HEAD: ef88211c984064e43dae15d76c66549a734df042
```

## /preflight receipt

- task classification: 既裁定の是正に対する独立受入再検査（continuation + bug-fix）
- baseline: 指定 revision と HEAD の一致を confirmed
- current-work-state: ECO-064=`implemented`、r4 REJECT 後の r4b 是正済み・r5 引き渡し中を confirmed
- unresolved-items: IA-10〜IA-12 の再実測と IA-01〜IA-09 の回帰を confirmed
- handoff-state: order §8.4、register、r1〜r4 報告から再構成し confirmed
- failing-behavior: r4 IA-10〜IA-12 の再現手順を confirmed
- expected-behavior: order §8.4 の r4b 是正内容とユーザー指定条件を confirmed
- acceptance-target: IA 回帰、V1/V2、unknown、AST、diff、清浄性を confirmed
- 開始判定: `PROCEED_WITH_LIMITS`
- 限定範囲: IA-10〜12、IA-01〜09 の代表腕、V1/V2、unknown 5 条件、AST、diff
- override: なし

## /calibrate receipt

- IA-10〜IA-12 の是正: observed / 適格
- IA-01〜IA-04・IA-06〜IA-09 の指定代表回帰: observed / 適格
- IA-05: environment / 本 r5 では測定対象外
- V1 selftest: observed / 適格
- V2 射影: observed / 適格
- unknown 5 条件: observed / 適格
- 停止語彙・引数処理の不変: observed / 適格
- diff 窓・activation-map 不変: observed / 適格
- V4 self-conformance・CI: unknown / 理由=`USER_DIRECTED_MANUFACTURER_SIDE_VERIFICATION`
- 検査 harness の初回出力符号化不成立は証拠から除外し、UTF-8 指定で全腕を再実行
- 検出した新規計器欠陥: なし

## 未検査項目

- `self-conformance.py` と対象 revision のリモート CI 結論
- order §8.4 で打ち切られた新規入力クラスの探索
- Windows 以外の実動作、および全 malformed YAML・全 Unicode・全 glob 表現の網羅

## この検査が支持しないもの

対象 revision の self-conformance 全 PASSまたはリモート CI 成功は支持しない。  
未探索の入力クラスを含む、全 malformed map に対する完全な安全性は支持しない。  
`required_skills` 情報欄を将来そのまま機械ゲート化して安全であることは支持しない。