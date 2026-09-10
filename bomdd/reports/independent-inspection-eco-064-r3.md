# 判定: REJECT

対象 revision `eea1b4ffc21bc8be78b0f9458c300e3859ab3f81` に対する独立受入検査 r3 の結果、r2 の IA-06〜IA-08 はすべて解消を確認しました。一方、追加境界探索で `required_skills` の非正規識別子を受理する新規不適合 IA-09 を確認したため、総合判定は REJECT です。

## 検査個体・設備

- 対象 revision: `eea1b4ffc21bc8be78b0f9458c300e3859ab3f81`
- revision 突合: 指定値と開始時・終了時の `git rev-parse HEAD` が一致
- 検査官設備: OpenAI Codex / GPT-5 系モデル（self-reported）
- 実行基盤: workspace-write。リポジトリ内は読み取り専用で検査
- CLI: `codex-cli 0.154.0`
- Python: `3.13.1`
- PyYAML: `6.0.3`
- OS: Windows 11 `10.0.26200`
- 開始時 `git status --short`: 空
- 終了直前 `git status --short`: 空
- リポジトリ内の変更: なし
- `self-conformance.py`: ユーザー指定に従い未実行

## r2 所見の再検査

### IA-06 — resolved

対象: `source` の `;` 区切りに含まれる空要素  
該当箇所: `method/tools/bomdd-job.py:125-153`

`start.source` に中間・先頭・末尾の空要素を個別に注入しました。

```text
中間: valid ; ; valid
先頭: ; valid
末尾: valid ;
```

三腕すべてで直接 probe は例外なく次の問題を返しました。

```text
class 'start': source に空要素(; 区切り)がある
```

OS temp 複製で通常 CLI を実行した結果も三腕で一致しました。

```text
exit: 0
traceback: false
required_skills.value: null
required_skills.source: unknown(...MAP_INVALID...source に空要素...)
skills_missing.value: null
skills_missing.source: unknown(required が判定不能)
stop_type.value: NONE
```

IA-06 は解消しています。

### IA-07 — resolved

対象: 非文字列・unhashable な `id` と validator 自身の例外  
該当箇所: `method/tools/bomdd-job.py:97-109,157-175`

`id` の直接 probe:

| 値 | `validate_map` |
|---|---|
| `["start"]` | 問題あり、例外なし |
| `{"a": 1}` | 問題あり、例外なし |
| `None` | 問題あり、例外なし |
| `3` | 問題あり、例外なし |
| `""` | 問題あり、例外なし |

共通の問題は `id が文字列でないか空` でした。

OS temp 複製の map を `id: [start]` に変更して通常 CLI を実行しました。

```text
exit: 0
traceback: false
required_skills.value: null
required_skills.source: unknown(...MAP_INVALID...class[0]: id が文字列でないか空)
skills_missing.value: null
stop_type.value: NONE
```

`load_map` の最終防御は、`validate_map` を monkeypatch して意図的に `RuntimeError` を送出させて確認しました。

```text
classes: null
error: activation-map 不正(MAP_INVALID): validate_map が例外終了: RuntimeError
外部への例外伝播: なし
```

IA-07 は解消しています。

### IA-08 — resolved

対象: 空または空白要素を持つ trigger 配列  
該当箇所: `method/tools/bomdd-job.py:119-122,201-217`

直接 probe:

| 入力 | `validate_map` | `_class_matches` |
|---|---|---|
| `statuses: []` | 問題あり | `None` |
| `instrument_paths: []` | 問題あり | `None` |
| `statuses: [""]` | 問題あり | `None` |
| `statuses: [" "]` | 問題あり | `None` |

OS temp 複製で空配列 2 腕を通常 CLI に通した結果:

```text
statuses: []
exit: 0 / traceback: false
required_skills.value: null
source: unknown(...MAP_INVALID...statuses が非空の文字列配列でない)
stop_type.value: NONE
```

```text
instrument_paths: []
exit: 0 / traceback: false
required_skills.value: null
source: unknown(...MAP_INVALID...instrument_paths が非空の文字列配列でない)
stop_type.value: NONE
```

IA-08 は解消しています。

## 新規所見

### IA-09 — MEDIUM — `required_skills` が canonical skill ID に制限されない

- evidence class: `validate_map()` の直接陰性対照、OS temp の改変 map、通常 CLI
- 該当箇所: `method/tools/bomdd-job.py:110-115,310-312,323-328`
- 内容: `required_skills` は非空文字列と組み立てた `.md` パスの実在だけを検査します。大小文字の一致、パス区切り・`..` の禁止、skills ディレクトリ内への containment を検査しません。

#### 再現 1 — 大文字小文字違い

`start.required_skills` を次へ変更しました。

```yaml
required_skills: [Preflight]
```

Windows の大小文字を区別しないファイル実在判定により、直接 probe は問題を返しませんでした。通常 CLI:

```text
exit: 0
traceback: false
required_skills.value: [Preflight, converge, calibrate]
skills_observed.value: [preflight, converge]
skills_missing.value: [Preflight, calibrate]
stop_type.value: NONE
```

存在する canonical skill は `preflight` ですが、非 canonical な `Preflight` が採用され、観測済み receipt と一致せず偽の missing を生成します。Linux 等では同じ map が MAP_INVALID になり得るため、OS 間でも判定が不一致になります。

#### 再現 2 — skills/ 外への相対パス

指定された `../x` は対象ファイルが存在しないため MAP_INVALID になりました。

```text
required_skills: [../x]
→ スキル ../x が skills/ に実在しない
```

一方、実在する親ファイルを指す `../README` に置換すると validator を通過しました。

```yaml
required_skills: [../README]
```

通常 CLI:

```text
exit: 0
traceback: false
required_skills.value: [../README, converge, calibrate]
skills_observed.value: [preflight, converge]
skills_missing.value: [../README, calibrate]
stop_type.value: NONE
```

これは「スキル名が skills/ に実在する」という V3 の検査文と一致せず、skills/ 外の通常文書を skill ID として採用します。現時点では情報欄であり停止 gate ではありませんが、F1 の required/missing 射影を誤らせるため不適合です。

推奨される受入条件は、`required_skills` を canonical な skill ID 文法へ制限し、解決後パスが skills ディレクトリ直下の対応する `<id>.md` と完全一致することです。

## その他の境界探索

| 境界 | 実測結果 |
|---|---|
| `required_skills` の重複 | validator は受理。射影側は重複を除去するため出力上の故障なし |
| `required_skills: [Preflight]` | 受理して偽 missing。IA-09 |
| `required_skills: [../x]` | 対象不在により MAP_INVALID |
| `required_skills: [../README]` | skills/ 外の実在ファイルを受理。IA-09 |
| `anchor_kind: ALWAYS` | `anchor_kind 不正 'ALWAYS'` として拒否 |
| `source` 断片に `#` が二つ | 結合された断片が実在しないとして拒否 |
| YAML anchor/alias | `safe_load` 後に通常 map として受理。判定異常なし |
| `classes` が dict | 通常 CLI exit 0、`classes 配列なし`、MAP_INVALID |
| 1,000 class | `validate_map` 約 0.107 秒、通常 CLI 約 0.492 秒、exit 0、traceback なし |

1,000 class 腕は全 class が `always` で `preflight` を要求する有効 map としました。required skill は重複除去され `[preflight]`、問題件数は 0 でした。

## 回帰

### V1 — 両 selftest

```text
python method/tools/bomdd-job.py --selftest
exit: 0
bomdd-job selftest PASS(...r2: 空 source 要素・unhashable id・空配列= MAP_INVALID)
```

```text
python method/tools/bomdd-witness.py --selftest
exit: 0
bomdd-witness selftest PASS(...)
```

両 selftest は PASS しました。ただし IA-09 の大小文字・パス containment に対する陰性対照はありません。

### V2 — 3 ECO の導出

```text
python method/tools/bomdd-job.py ECO-062 ECO-063 ECO-064 --json
exit: 0
```

| ECO | state | required_skills | skills_observed | skills_missing | stop |
|---|---|---|---|---|---|
| ECO-062 | verified | preflight, converge, calibrate | preflight, converge, calibrate | `[]` | NONE |
| ECO-063 | verified | preflight, calibrate | preflight, converge, calibrate | `[]` | NONE |
| ECO-064 | implemented | preflight, converge, calibrate | preflight, converge | `[calibrate]` | NONE |

r2 の値と同一です。

### unknown 5 条件

| 条件 | exit | 実測 |
|---|---:|---|
| map 不在 | 0 | required=null・MAP_MISSING、missing=null |
| `classes: []` | 0 | required=null・`classes 配列なし`、missing=null |
| self-conformance 不在 | 0 | required=null・MAP_INVALID、observed/missing=null |
| order 不在 | 0 | required=`[preflight, calibrate]`、design-synthesis 判定不能、observed/missing=null、stop=MISSING_INPUT |
| PyYAML 不在（`python -S`） | 0 | stop=MISSING_INPUT・`PyYAML 不在` |

全腕で traceback はありません。欠測を PASS 値へ変換する経路は確認されませんでした。

### 停止語彙と引数処理

`d9fe305` と対象 revision の Python ソースを AST 解析し、定数値と `select()` の引数・選択処理を抽出比較しました。

```text
STOP_VOCABULARY:
NONE
NORMATIVE_RULING
VERIFICATION_FAIL
BOM_CONTRADICTION
CONVERGENCE_LIMIT
PREFLIGHT_HOLD
LEDGER_INCONSISTENT
MISSING_INPUT

DERIVABLE_FROM_LEDGER:
NONE
LEDGER_INCONSISTENT
MISSING_INPUT
```

```text
停止語彙 AST: identical
引数・対象選択 AST: identical
```

実動作:

```text
--register 値なし → exit 0 / MISSING_INPUT / traceback なし
未知の --bogus    → exit 0 / MISSING_INPUT / traceback なし
--json のみ       → exit 0 / MISSING_INPUT / traceback なし
```

## diff 監査

```text
git diff --name-status ee7c20a..eea1b4ffc21bc8be78b0f9458c300e3859ab3f81
```

実測:

```text
M bomdd/60-change-order-eco-064.md
M bomdd/60-change-register.yaml
A bomdd/reports/independent-inspection-eco-064-r2.md
M method/tools/bomdd-job.py
```

r2b の製造物 `method/tools/bomdd-job.py` と台帳系（order・register・r2 報告）のみです。

```text
git diff --name-only ee7c20a..eea1b4ffc21bc8be78b0f9458c300e3859ab3f81 \
  -- method/templates/product-profile/skills/activation-map.yaml
```

出力は空で、activation-map.yaml に r2b の diff はありません。

## 一時領域

すべての採用証拠は、OS temp の `eco064-r3-*` 複製またはリポジトリを変更しない直接 probe から取得しました。

最初の一括 probe は観測窓内に結果を回収できなかったため証拠不採用とし、独立した小さい probe に分割して再実行しました。一括 probe の temp 残置がないことを確認しています。

終了直前の確認:

```text
eco064-r3-* temp: 0 件
削除拒否・残置パス: なし
git status --short: 空
```

## /preflight receipt

- task classification: 既存 revision に対する独立受入再検査（continuation + bug-fix）
- baseline: 指定 revision と HEAD の一致を confirmed
- current-work-state: ECO-064=`implemented`、r2 REJECT 後の r2b 是正済み・r3 引き渡し中を confirmed
- unresolved-items: IA-06〜IA-08 の再測定と追加境界探索を confirmed
- handoff-state: order §8.2 と r2 報告から再構成し confirmed
- failing-behavior: r2 の IA-06〜IA-08 再現手順を confirmed
- expected-behavior: order §8.2 とユーザー指定の受入条件を confirmed
- acceptance-target: 全指定 probe、回帰、diff、清浄性確認を confirmed
- 開始判定: PROCEED
- override: なし

## /calibrate receipt

- IA-06〜IA-08 の是正: observed / 適格
- V1 selftest の PASS: observed / 条件付き適格（IA-09 の非正規 skill ID を検出しない）
- V2 の 3 ECO 射影: observed / 適格
- unknown 5 条件の exit 0・unknown/MISSING_INPUT 化: observed / 適格
- `required_skills` validator の canonical ID・containment: observed / 不適格（IA-09）
- 停止語彙・引数処理の不変: observed / 適格
- diff 窓と activation-map 不変: observed / 適格
- V4 self-conformance・CI: unknown / 理由=`USER_DIRECTED_MANUFACTURER_SIDE_VERIFICATION`
- 検出した計器欠陥: IA-09（map validator、製造物帰属）
- battery:
  - Q1〜Q7: asked
  - Q8: NA（新規 gate なし）
  - Q9〜Q11: asked
- 検出力の限界:
  - Windows 以外での実動作は未測定
  - 1,000 class を超える規模・YAML alias graph 全般の資源上限は未測定
  - `source` の literal 実在と契約意味の一致は検査していない

## 未検査項目

- `self-conformance.py` と対象 revision の CI 結論（ユーザー指定により製造者側 V4）
- Linux/macOS 上の大小文字・パス解決
- 全 YAML 型・全 Unicode/パス表現・全 alias graph の網羅
- r1 IA-01〜IA-04 の全直接再現（r2 resolved を前提とし、今回は selftest 回帰のみ）

## この検査が支持しないもの

対象 revision の self-conformance 全 PASSまたはリモート CI 成功は支持しない。  
全 OS・全 malformed YAML に対する fail-closed 性は支持しない。  
`required_skills` を現状の validator のまま gate 化して安全であることは支持しない。