# 判定: REJECT

対象 revision `b1882fa0db27708169e8e02245b7ade79da57edd` に対する独立受入検査 r4 の結果、r3 所見 IA-09 は **resolved** です。一方、追加境界探索で IA-10〜IA-12 の新規不適合を確認したため、総合判定は REJECT です。

## 検査個体・設備

- 対象 revision: `b1882fa0db27708169e8e02245b7ade79da57edd`
- revision 突合: 開始時・終了時の `git rev-parse HEAD` が指定値と一致
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

## IA-09 — resolved

対象: `required_skills` の canonical skill ID 制約  
該当箇所: `method/tools/bomdd-job.py:85,111-129,537-542`

### コード読解

- 文法: `SKILL_ID_RE.fullmatch()` により `[a-z0-9][a-z0-9-]*`
- 実在判定: `skills_dir.iterdir()` から `{p.stem ...}` を作り、`s not in canonical` で大小文字込み比較
- Windows の大小文字非区別なファイル実在判定には依存していない
- `/`、`..`、拡張子付き ID は文法段階で拒否
- `seen_skills` により同一 class 内の重複を拒否

実ファイルから得た canonical stem には次が含まれます。

```text
bomdd-next
factory-delegate
preflight
```

### 直接 probe

| `required_skills` | `validate_map` |
|---|---|
| `[Preflight]` | 問題あり・文法外 |
| `[../README]` | 問題あり・文法外 |
| `[preflight, preflight]` | 問題あり・重複 |
| `[pre_flight]` | 問題あり・文法外 |
| `[-preflight]` | 問題あり・文法外 |
| `[preflight-]` | 問題あり・canonical file 不在 |
| `[PREFLIGHT]` | 問題あり・文法外 |
| `[preflight.md]` | 問題あり・文法外 |
| `[skills/preflight]` | 問題あり・文法外 |
| `[préflight]` | 問題あり・文法外 |
| `[プレフライト]` | 問題あり・文法外 |
| `[preflight]` | 問題なし |
| `[factory-delegate]` | 問題なし |
| `[bomdd-next]` | 問題なし |

### OS temp 複製での通常 CLI

`[Preflight]`:

```text
exit: 0
traceback: false
required_skills.value: null
required_skills.source: unknown(...MAP_INVALID...文法外...)
skills_missing.value: null
stop_type.value: NONE
```

`[../README]`:

```text
exit: 0
traceback: false
required_skills.value: null
required_skills.source: unknown(...MAP_INVALID...文法外...)
skills_missing.value: null
stop_type.value: NONE
```

`[preflight, preflight]`:

```text
exit: 0
traceback: false
required_skills.value: null
required_skills.source: unknown(...MAP_INVALID...required_skills に重複...)
skills_missing.value: null
stop_type.value: NONE
```

canonical ID は通常 CLI でも受理されました。

```text
[preflight]        → required=[preflight, converge, calibrate]
[factory-delegate] → required=[factory-delegate, converge, calibrate]
[bomdd-next]       → required=[bomdd-next, converge, calibrate]
```

IA-09 の是正は成立しています。

## 新規所見

### IA-10 — MEDIUM — `instrument_paths` が非正規パスを受理し、class を無言で無効化する

- evidence class: `validate_map()` 直接陰性対照、`_class_matches()`、OS temp 改変 map、通常 CLI
- 該当箇所: `method/tools/bomdd-job.py:88-89,135-136,193-212,225-231`
- 帰属: activation-map validator（製造物兼検査器）

`instrument_paths` は「非空の文字列配列」だけを確認し、リポジトリ相対パス、前後空白、pattern の有効範囲を検査しません。

直接 probe:

| 値 | validate | `method/tools/x.py` との match |
|---|---|---|
| `C:/absolute/*.py` | 問題なし | false |
| ` method/tools/*.py` | 問題なし | false |
| `method/tools/*.py ` | 問題なし | false |
| 空白のみ | 問題あり | None |
| `**` | 問題なし | true |
| `**` 対 `docs/x.md` | 問題なし | true |

OS temp の ECO-064 map で通常 CLI を実行すると、絶対パスまたは前後空白により `instrument-change` が無言で消えます。

```text
instrument_paths: [C:/absolute/*.py]
exit: 0 / traceback: false
required_skills.value: [preflight, converge]
required_skills.source: activation-map.yaml: start, design-synthesis
skills_missing.value: []
stop_type.value: NONE
```

先頭空白・末尾空白でも同じ結果でした。正規 map なら ECO-064 は `instrument-change` により `calibrate` を要求しますが、非正規値が MAP_INVALID にならず、要求を欠落させます。

`**` は実装上明示された glob 文法に含まれるため、それ自体を独立した文法違反とは判定しません。ただし単独指定で全 `affected_refs` に発火するため、scope 制約を validator が持たないことも確認しました。

再現手順:

1. temp 複製の `instrument-change.instrument_paths` を `[C:/absolute/*.py]` または前後空白付き pattern に置換。
2. `python method/tools/bomdd-job.py ECO-064 --json`
3. exit 0 のまま `calibrate` と `instrument-change` が required/source から消えることを確認。

### IA-11 — MEDIUM — `statuses` の大小文字・前後空白違いを受理し、verified class を無言で無効化する

- evidence class: `validate_map()` 直接陰性対照、`_class_matches()`、OS temp 改変 map、通常 CLI
- 該当箇所: `method/tools/bomdd-job.py:88-89,133-134,220-224`
- 帰属: activation-map validator（製造物兼検査器）

次の値はすべて validator を通過しますが、register の `verified` とは一致しません。

```text
statuses: [Verified]  → validate=[] / match=false
statuses: [" verified"] → validate=[] / match=false
statuses: ["verified "] → validate=[] / match=false
```

他の calibrate trigger を除いた OS temp の ECO-063 で通常 CLI を実行した結果:

```text
statuses: [Verified]
affected_refs: [docs/a.md]
exit: 0
traceback: false
required_skills.value: [preflight]
required_skills.source: activation-map.yaml: start
skills_missing.value: []
stop_type.value: NONE
```

正規値 `[verified]` なら `verified-promotion` が発火し、`calibrate` が required になります。値の typo が MAP_INVALID ではなく正常な非該当として扱われるため、要求を無言で欠落させます。

再現手順:

1. temp map の `verified-promotion.statuses` を `[Verified]` に置換。
2. 対象 register entry の他の calibrate trigger を外して通常 CLI を実行。
3. exit 0、MAP_INVALID なしで `calibrate` が required から消えることを確認。

### IA-12 — LOW — class 順序だけで `required_skills` の配列順が変わる

- evidence class: OS temp 改変 map、通常 CLI
- 該当箇所: `method/tools/bomdd-job.py:317-326,341-342`
- 帰属: job 射影の集約処理

同じ四つの class を同じ内容のまま逆順にした結果です。

```text
canonical class order:
required_skills.value: [preflight, converge, calibrate]
source classes: start, design-synthesis, verified-promotion, instrument-change
```

```text
reversed class order:
required_skills.value: [calibrate, converge, preflight]
source classes: instrument-change, verified-promotion, design-synthesis, start
```

required は実質的に class ごとの skill の集合和ですが、初出順で重複除去しているため、class の宣言順が出力順へ漏れます。class 間の優先順位や required 配列の順序意味は正本に定義されていません。意味的に等価な map の並べ替えで機械出力が変わるため、安定した射影になっていません。

再現手順:

1. temp map の `classes` を `reversed(classes)` にする。各 class の内容は変更しない。
2. `python method/tools/bomdd-job.py ECO-062 --json`
3. required の集合は同じまま配列順が変わることを確認。

## その他の境界探索

| 境界 | 実測結果 |
|---|---|
| `id` の大文字・前後空白・内部空白・`/` | validator は受理 |
| `anchor` の int/list/dict/null | すべて問題として列挙、例外なし |
| `contract_item` の int/list/dict/null | 受理、判定不変 |
| `limitation` の int/list/dict/null | 受理、判定不変 |
| `source` がディレクトリ | `is_file()` により問題として列挙 |
| `instrument_paths` が空白のみ | 問題として列挙、match=None |
| `instrument_paths: ["**"]` | 受理し、階層を問わず全参照に一致 |
| `statuses: [Verified]` | 受理するが `verified` に不一致 |
| class 逆順化 | required の集合は同じだが配列順が変化 |

`id` には canonical 文法が定義されておらず、現在は表示用 class ID と重複検出にのみ使われます。この検査では具体的な誤射影を再現できなかったため、新規 IA にはしていません。

`contract_item` は map 自身が「注記・検査しない」と宣言しており、r2 でも arbitrary object による ablation が意図的に採用されています。`limitation` も判定入力ではないため、型を受理することだけでは不適合としません。

## 回帰

### V1 — 両 selftest

```text
python method/tools/bomdd-job.py --selftest
exit: 0
bomdd-job selftest PASS(...r3: canonical skill ID〔文法+大小文字込み実在+重複拒否〕)
```

```text
python method/tools/bomdd-witness.py --selftest
exit: 0
bomdd-witness selftest PASS(...)
```

両 selftest は PASS しました。ただし IA-10〜IA-12 の入力クラスは検出しません。

### V2 — ECO-062 / ECO-063 / ECO-064

```text
python method/tools/bomdd-job.py ECO-062 ECO-063 ECO-064 --json
exit: 0
```

| ECO | state | required_skills | skills_observed | skills_missing | stop |
|---|---|---|---|---|---|
| ECO-062 | verified | preflight, converge, calibrate | preflight, converge, calibrate | `[]` | NONE |
| ECO-063 | verified | preflight, calibrate | preflight, converge, calibrate | `[]` | NONE |
| ECO-064 | implemented | preflight, converge, calibrate | preflight, converge | `[calibrate]` | NONE |

r3 の申告値と一致します。

### unknown 5 条件

| 条件 | exit | 実測 |
|---|---:|---|
| map 不在 | 0 | required=null・MAP_MISSING、missing=null |
| `classes: []` | 0 | required=null・classes 配列なし、missing=null |
| self-conformance 不在 | 0 | required=null・MAP_INVALID、observed/missing=null |
| order 不在 | 0 | required=`[preflight, calibrate]`、design-synthesis 判定不能、observed/missing=null、stop=MISSING_INPUT |
| PyYAML 不在（`python -S`） | 0 | stop=MISSING_INPUT・`PyYAML 不在` |

全腕で traceback はありません。UNKNOWN を PASS 値へ変換する経路は確認されませんでした。

### 停止語彙と引数処理

`d9fe305` と対象 revision の AST を比較しました。

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
select() signature AST: identical
引数解析・対象選択 prefix AST: identical
```

`select()` 全体には ECO-064 の map/self-conformance 読込と `project()` 引数追加があるため全関数比較は非同一です。比較対象を引数解析・対象選択までに限定すると同一でした。

実動作:

```text
--register 値なし → exit 0 / MISSING_INPUT
未知の --bogus    → exit 0 / MISSING_INPUT
--json のみ       → exit 0 / MISSING_INPUT
```

## diff 監査

```text
git diff --name-status eea1b4f..b1882fa0db27708169e8e02245b7ade79da57edd
```

実測:

```text
M bomdd/60-change-order-eco-064.md
M bomdd/60-change-register.yaml
A bomdd/reports/independent-inspection-eco-064-r3.md
M method/tools/bomdd-job.py
```

`method/tools/bomdd-job.py` と台帳系（order・register・r3 報告）のみです。

```text
git diff eea1b4f..b1882fa0db27708169e8e02245b7ade79da57edd \
  -- method/templates/product-profile/skills/activation-map.yaml
```

出力は空で、activation-map.yaml に r3b の diff はありません。

## 一時領域

採用証拠は、リポジトリを変更しない直接 probe または OS temp の `eco064-r4-*` 複製から取得しました。

最初の Unicode probe は Windows の既定出力符号化で終了したため不採用とし、UTF-8 を明示して再実行しました。別の広範囲コピーは観測窓内に結果を回収できなかったため不採用とし、小さい独立 probe へ分割しました。

終了直前の確認:

```text
eco064-r4-* temp: 0 件
削除拒否・残置パス: なし
git status --short: 空
```

## /preflight receipt

- task classification: 既存 revision に対する独立受入再検査（continuation + bug-fix）
- baseline: 指定 revision と HEAD の一致を confirmed
- current-work-state: ECO-064=`implemented`、r3 REJECT 後の r3b 是正済み・r4 引き渡し中を confirmed
- unresolved-items: IA-09 の再測定、追加境界探索、回帰、diff 監査を confirmed
- handoff-state: order §8.3 と r3 報告から再構成し confirmed
- failing-behavior: r3 IA-09 の三つの再現手順を confirmed
- expected-behavior: order §8.3 の r3b 是正内容とユーザー指定の受入条件を confirmed
- acceptance-target: 全指定 probe、回帰、diff、清浄性、temp cleanup を confirmed
- discovered prerequisites: Python・PyYAML・git 履歴・OS temp 書込を confirmed
- 開始判定: PROCEED
- override: なし

## /calibrate receipt

### 主張別判定

- IA-09 の是正: observed / 適格
- IA-10 `instrument_paths` の非正規値受理: observed / 適格
- IA-11 `statuses` の大小文字・空白違い受理: observed / 適格
- IA-12 class 順序による required 順序変化: observed / 条件付き適格（required 配列順の意味は正本に明記されていない）
- V1 selftest の PASS: observed / 条件付き適格（IA-10〜IA-12 を検出しない）
- V2 の 3 ECO 射影: observed / 適格
- unknown 5 条件: observed / 適格
- 停止語彙・引数処理の不変: observed / 適格
- diff 窓と activation-map 不変: observed / 適格
- V4 self-conformance・CI: unknown / 理由=`USER_DIRECTED_MANUFACTURER_SIDE_VERIFICATION`

### 検出した計器欠陥と帰属

- IA-10、IA-11: `validate_map` の入力値検査不足。製造物兼検査器へ帰属
- IA-12: job 射影の順序正規化不足。製造物へ帰属
- 独立検査 harness の採用証拠に影響する欠陥: なし。不成立だった初期二腕は証拠から除外して再実行

### battery

- Q1: asked
- Q2: asked
- Q3: asked
- Q4: asked
- Q5: asked
- Q6: asked
- Q7: asked
- Q8: NA（新規 gate なし）
- Q9: asked
- Q10: asked
- Q11: asked

### 検出力の限界

- Windows 以外の実動作は測定していない
- 全 status vocabulary、全 glob 表現、全 Unicode/YAML 型の組合せは網羅していない
- `source` の literal 実在と契約上の意味の一致は測定していない
- class ID と required 配列順に外部 consumer が依存しているかは測定していない

## 未検査項目

- `self-conformance.py` と対象 revision の CI 結論（ユーザー指定により製造者側 V4）
- Linux/macOS 上の大小文字・パス・glob 動作
- IA-01〜IA-08 の全直接再現（r2/r3 resolved を前提とし、今回は selftest 回帰のみ）
- 全 malformed YAML、全 status、全 glob、全 alias graph、資源上限の網羅

## この検査が支持しないもの

対象 revision の self-conformance 全 PASSまたはリモート CI 成功は支持しない。  
全 OS・全 malformed map に対する fail-closed 性は支持しない。  
現状の activation-map validator を追加の境界検査なしに gate 化して安全であることは支持しない。