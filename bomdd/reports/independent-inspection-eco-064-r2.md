# 判定: REJECT

対象 revision `ee7c20abb45fdeac8649d14d6e1323c23675a2dd`（`main`）に対する独立受入検査 r2 の結果、r1 の IA-01〜IA-04 はすべて解消を確認しました。一方、fail-closed 検証に新たな不適合 3 件（IA-06〜IA-08）を確認したため、総合判定は REJECT です。

## 検査個体・設備

- 対象 revision: `ee7c20abb45fdeac8649d14d6e1323c23675a2dd`
- branch: `main`
- revision 突合: 指定値と `git rev-parse HEAD` が一致
- 検査官設備: OpenAI Codex / GPT-5 系モデル（self-reported）
- 実行基盤: workspace-write。ただしリポジトリ内は読み取り専用で検査
- CLI: `codex-cli 0.154.0`
- Python: `3.13.1`
- PyYAML: `6.0.3`
- OS: Windows 11 `10.0.26200`
- 開始時 `git status --short`: 空
- 終了直前 `git status --short`: 空
- リポジトリ内の変更: なし

## r1 所見の再検査

### IA-01 — resolved

対象: 不正な `statuses` 型による traceback・exit 1  
該当箇所: `method/tools/bomdd-job.py:87-120,155-170,196-205,295-320`

OS temp に検査個体を複製し、`verified-promotion.statuses` を以下の三種類へ変更して通常 CLI を実行しました。

```text
statuses: 7
statuses: "verified"
statuses: {verified: 1}
```

三腕とも実測結果は同じでした。

```text
exit: 0
traceback: false
required_skills.value: null
required_skills.source: unknown(...activation-map 不正(MAP_INVALID)...statuses が文字列配列でない)
skills_observed.value: [preflight, converge]
skills_missing.value: null
skills_missing.source: unknown(required が判定不能)
stop_type.value: NONE
```

`_class_matches()` の防御的判定も三型すべて `None` でした。r1 の TypeError・文字反復・辞書キー反復は再現せず、IA-01 は解消しています。

### IA-02 — resolved

対象: glob が区切りを跨ぐこと、およびパス区切りの OS 依存  
該当箇所: `method/tools/bomdd-job.py:174-218`

`_glob_match()` と実 map の `instrument-change` を使った `_class_matches()` の直接 probe:

```json
{
  "method/tools/x.py": true,
  "method/tools/sub/x.py": false,
  "method\\tools\\x.py": true,
  "bomdd/hooks/pre-push": true,
  "docs/x.py": false
}
```

追加境界:

```text
_glob_match("a/b/c/x.py", "a/**/x.py") = true
_glob_match("a/x.py",     "a/**/x.py") = false
_glob_match("a/x.py",     "a/?.py")    = true
_glob_match("a/xy.py",    "a/?.py")    = false
_glob_match("a//.py",     "a/?.py")    = false
```

`*` と `?` は `/` を跨がず、`**` は複数階層に一致し、`\` は `/` へ正規化されました。IA-02 は解消しています。

### IA-03 — resolved

対象: `anchor` への契約意味の転写  
該当箇所: `method/templates/product-profile/skills/activation-map.yaml:25-45`

v1.1 の各 `anchor` は次の台帳・order 側の観測事実だけを記述しています。

- ECO エントリの存在
- fence 除去後 order と `CONVERGE_HARD_POSITIVES` の一致
- `register.status` と `statuses` の一致
- `register.affected_refs` と `instrument_paths` の glob 一致

「verification 節を書くイベント」「検査器の新設・変更」という契約意味は `contract_item` へ分離されています。

コード全体を検索した結果、`contract_item` の参照は `activation-map.yaml` の説明・データだけであり、`bomdd-job.py` の判定には使用されていません。値を任意 object に置換した ablation でも `_class_matches()` の結果は不変でした。IA-03 は解消しています。

### IA-04 — resolved

対象: `source` の `#` 断片を検査していなかったこと  
該当箇所: `method/tools/bomdd-job.py:124-151,455-460`

実測:

```text
validate_map(実 map) = []
source 断片を #不存在 に変更 = 問題あり
.md の見出し行に断片あり = []
.md の本文だけに同語あり = 問題あり
.py の本文に識別子あり = []
# なし = 問題あり
存在しないファイル = 問題あり
```

参照先の literal も独立に確認しました。

```text
preflight.md:21   ## 自発起動契約(...)
converge.md:15    ## 自発起動契約(...)
calibrate.md:22   ## 自発起動契約(...)
self-conformance.py:1156  CONVERGE_HARD_POSITIVES
self-conformance.py:1435  C17_SCOPE_MIN
```

selftest に `#不存在` の陰性対照が追加されていることも確認しました。IA-04 は解消しています。

## 新規所見

### IA-06 — MEDIUM — 空の `source` 要素が MAP_INVALID にならない

- evidence class: `validate_map()` の直接陰性対照と通常 CLI
- 該当箇所: `method/tools/bomdd-job.py:128-131`
- 内容: `source` を `;` で分割した後、空要素をエラーにせず `continue` しています。

直接 probe:

```text
source: "code.py#PY_MARKER ; ; code.py#PY_MARKER"
validate_map(...) = []

source: "; code.py#PY_MARKER"
validate_map(...) = []
```

通常 CLI でも空要素を含む map が採用されました。

```text
exit: 0
traceback: false
required_skills.value: [preflight, converge, calibrate]
stop_type.value: NONE
```

再現手順:

1. OS temp に検査個体を複製する。
2. `start.source` を次へ変更する。

```yaml
source: "method/templates/product-profile/skills/preflight.md#自発起動契約 ; ; method/templates/product-profile/skills/preflight.md#自発起動契約"
```

3. `python method/tools/bomdd-job.py ECO-064 --json` を実行する。

`source` 内の空要素を不正として弾くという副経路要件を満たしていません。

### IA-07 — HIGH — unhashable な `id` で通常 CLI が traceback・exit 1

- evidence class: OS temp での故障注入・通常 CLI
- 該当箇所: `method/tools/bomdd-job.py:102-108,155-170,540,561`
- 内容: `id` が文字列かを検査した後も、無条件に `seen.add(cid)` を実行します。list や dict は hashable でないため、validator 自身が例外終了します。

再現 map:

```yaml
classes:
  - id: [start]
    required_skills: [preflight]
    anchor_kind: always
    anchor: "a"
    source: "method/templates/product-profile/skills/preflight.md#自発起動契約"
```

実測:

```text
exit: 1
traceback: true
TypeError: unhashable type: 'list'
  validate_map(), line 108: seen.add(cid)
```

これは r1 IA-01 と同型の「不正 map を unknown にせず通常 CLI を exit 1 にする」経路であり、`--selftest` 以外は常に exit 0 という契約に反します。

### IA-08 — MEDIUM — 空の trigger 配列が class を silently 無効化する

- evidence class: `validate_map()` と `_class_matches()` の直接陰性対照
- 該当箇所: `method/tools/bomdd-job.py:87-88,118-121,201-212`
- 内容: `_is_str_list([])` が true になるため、`statuses` と `instrument_paths` の空配列は validator を通過します。対応する class はエラーや unknown ではなく false になります。

実測:

```json
{
  "statuses_empty_validate": [],
  "statuses_empty_match": false,
  "instrument_paths_empty_validate": [],
  "instrument_paths_empty_match": false
}
```

これにより malformed map が MAP_INVALID にならず、`verified-promotion` または `instrument-change` の要求スキルを `required_skills` から無言で除外できます。情報欄であって現時点では停止 gate ではありませんが、F1 の事前宣言を fail-open にするため不適合です。

## 副経路の陰性対照

次は期待どおり弾かれました。

```text
source に # なし       → source ... に # 断片がない
source のファイル不在 → source ... が実在しない
id 重複                → id 重複
classes に非 object    → class[0] が object でない
required_skills: []    → required_skills が非空の文字列配列でない
```

次は弾かれませんでした。

```text
source の ; 区切り空要素 → IA-06
statuses: []             → IA-08
instrument_paths: []     → IA-08
```

非文字列 `id` のうち unhashable な値は、問題を返す前に例外終了しました（IA-07）。

## 回帰

### V1 — 両 selftest

```text
python method/tools/bomdd-job.py --selftest
exit: 0
bomdd-job selftest PASS(...r1: 型不正 MAP_INVALID・source 断片の陰性対照・区切りを跨がない glob)
```

```text
python method/tools/bomdd-witness.py --selftest
exit: 0
bomdd-witness selftest PASS(...)
```

両 selftest は PASS しました。ただし IA-06〜IA-08 の陰性対照を持たないため、job selftest の証拠資格は条件付きです。

### V2 — 3 ECO の導出

```text
python method/tools/bomdd-job.py ECO-062 ECO-063 ECO-064 --json
exit: 0
```

| ECO | required_skills | skills_observed | skills_missing | stop_type |
|---|---|---|---|---|
| ECO-062 | preflight, converge, calibrate | preflight, converge, calibrate | `[]` | NONE |
| ECO-063 | preflight, calibrate | preflight, converge, calibrate | `[]` | NONE |
| ECO-064 | preflight, converge, calibrate | preflight, converge | `[calibrate]` | NONE |

r1 の期待値と一致しました。ECO-064 の `calibrate` は `instrument-change` 由来です。

### unknown 5 条件

| 条件 | exit | 実測 |
|---|---:|---|
| map 不在 | 0 | required=null + `unknown(...MAP_MISSING...)`、missing=null |
| classes 空 | 0 | required=null + `unknown(...classes 配列なし...)`、missing=null |
| self-conformance 不在 | 0 | map source 不在で required=null + `MAP_INVALID`、observed/missing=null |
| order 不在 | 0 | required=`[preflight, calibrate]`、design-synthesis 判定不能、observed/missing=null、stop=`MISSING_INPUT` |
| PyYAML 不在（`python -S`） | 0 | stop=`MISSING_INPUT`、source=`導出: PyYAML 不在` |

欠測を PASS に丸める経路は確認されませんでした。

### 停止語彙と引数処理

`d9fe305` と現在個体から AST で値を独立抽出し、同一であることを確認しました。

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

`git diff d9fe305..ee7c20a -- method/tools/bomdd-job.py` では、`select()` の既存引数解析部分に変更はなく、選択後に map と self-conformance を読み込む処理だけが追加されています。

実動作:

```text
--register 値なし   → exit 0 / MISSING_INPUT
未知の --bogus      → exit 0 / MISSING_INPUT
--json のみ         → exit 0 / MISSING_INPUT
```

## V4・常設検査

`python method/tools/self-conformance.py` は結果を確実に観測するため単独で実行しました。最初の実行は継続セッション識別子を保存できず結果を証拠採用できなかったため、二回目の観測結果のみを採用しています。

```text
exit: 1
C1〜C13: PASS
C14: FAIL ... 実 scaffold = 6/7 — 失敗: ['REAL']
C15〜C18: PASS
self-conformance FAILED — 1 件の不適合
```

C14 は r1 IA-05 と同じ実行基盤の Git ownership 制約に帰属するため、ECO-064 製造物の新規所見には数えません。ただし測定不能は PASS ではなく、V4 のローカル全 PASS は本検査から支持できません。

CI 確認:

```text
gh run list --repo akiramei/BomDD --limit 3
exit: 1
connectex: socket access forbidden by execution environment
```

対象 revision の CI 結論は `UNKNOWN` です。

## diff 監査

```text
git diff --name-status 24e16e0..ee7c20abb45fdeac8649d14d6e1323c23675a2dd
```

実測:

```text
M bomdd/60-change-order-eco-064.md
M bomdd/60-change-register.yaml
A bomdd/reports/independent-inspection-eco-064.md
M method/templates/product-profile/skills/activation-map.yaml
M method/tools/bomdd-job.py
```

製造物 2 ファイルと台帳系（order・register・r1 報告）だけであり、指定された窓に一致しました。

## 一時領域

本検査が作成した `eco064-r2-*` temp はすべて削除され、終了時に残置 0 件を確認しました。

`self-conformance` の二回の実行が作成した次の C14 temp は、絶対パス・親 temp・prefix を検証した上で削除を要求しましたが、実行基盤ポリシーに拒否されました。

```text
C:\Users\akira\AppData\Local\Temp\bomdd-selfconf-c14-4e7i9d9b
C:\Users\akira\AppData\Local\Temp\bomdd-selfconf-c14-rhz89wcj
```

終了時にも両方の残置を確認しました。開始前から存在した同 prefix の 5 件には触れていません。

## /preflight receipt

- task classification: 既存 revision に対する独立受入再検査（continuation + bug-fix）
- baseline: 指定 revision と HEAD の一致を confirmed
- current-work-state: ECO-064=`implemented`、r1 REJECT 後の r2 待ちを confirmed
- failing-behavior: r1 IA-01〜IA-04 の再現手順を confirmed
- expected-behavior: order §1・§3・§8.1 と r1 報告を confirmed
- acceptance-target: ユーザー指定の全検査観点を confirmed
- 開始判定: PROCEED
- override: なし

## /calibrate receipt

- IA-01〜IA-04 の是正: observed / 適格
- V1 selftest: observed / 条件付き適格（IA-06〜IA-08 の陰性対照なし）
- V2 導出結果: observed / 適格
- fail-closed map validation 全体: observed / 不適格（IA-06〜IA-08）
- self-conformance 全 PASS: observed / 不適格（C14 FAIL）
- 対象 revision の CI: unknown / 理由=`EXECUTION_ENVIRONMENT_NETWORK_BLOCKED`
- 検出した計器欠陥: IA-06〜IA-08
- battery:
  - Q1〜Q7: asked
  - Q8: NA（新規 gate なし）
  - Q9〜Q11: asked
- 検出力の限界:
  - Windows 以外での glob 動作は未測定
  - CI は実行基盤のネットワーク制約により未確認
  - 全 YAML 型・全パス表現の網羅検査ではない

## 未検査項目

- 対象 revision のリモート CI 結論
- Linux/macOS 上での glob・パス正規化
- calibrate の認識依存 trigger ②・④
- 実運用消費側が `unknown` を確実に確認するか

## この検査が支持しないもの

対象 revision のリモート CI 成功は支持しない。  
全 malformed YAML・全 OS に対する fail-closed 性は支持しない。  
`required_skills` を将来 gate 化して安全であることは支持しない。