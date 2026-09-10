# 判定: REJECT

対象 revision `24e16e06e8b527ec268c4227dc28488f0bdc1b65` に対する異系統・独立受入検査の結果、主要正常系は期待どおりでしたが、exit 契約違反を含む不適合を確認しました。

## 検査個体・設備

- 対象: `24e16e06e8b527ec268c4227dc28488f0bdc1b65`
- branch: `main`
- 検査官設備: OpenAI Codex / GPT-5 系モデル（self-reported）
- CLI: `codex-cli 0.154.0`
- Python: `3.13.1`
- PyYAML: `6.0.3`
- OS: Windows 11
- 開始時 `git status --short`: 空
- 終了直前 `git status --short`: 空
- リポジトリ内の変更: なし

## 所見

### IA-01 — HIGH — 不正な `statuses` 型で exit 0 契約が破られる

- evidence class: OS temp での故障注入・実行再現
- 該当箇所:
  - `method/tools/bomdd-job.py:92-95`
  - `method/tools/bomdd-job.py:103-104`
  - `method/tools/bomdd-job.py:406-417`
- 内容:
  - `load_map()` は `classes` が非空リストであることしか検査せず、各 class のフィールド型を検証しない。
  - `verified-promotion.statuses` を整数 `7` にすると `_class_matches()` が反復しようとして `TypeError` となる。
  - 通常実行が traceback と exit 1 で終了し、「`--selftest` 以外は常に exit 0」という契約を破る。
  - `statuses: "verified"` はクラッシュしないが文字単位で反復され、verified が silently false になる。辞書ではキーを反復して true になり得る。

再現:

```text
temp の activation-map.yaml:
verified-promotion:
  anchor_kind: ledger-status
  statuses: 7

python method/tools/bomdd-job.py ECO-X --json
```

出力:

```text
exit: 1
TypeError: 'int' object is not iterable
  at bomdd-job.py:104
```

期待される帰結は、map 形状不正を `null + unknown(...)` または構造化された `MISSING_INPUT` として返し、exit 0 を維持することです。

### IA-02 — MEDIUM — `method/tools/*.py` が下位ディレクトリにも一致する

- evidence class: 関数単位の境界実測
- 該当箇所:
  - `method/templatesלית/product multiline`? Correction: `method/templatesOLF`? 
  - `method/templates/product-profile/skills/activation skeleton`? 
  - `method/templates/product-profile/skills/activation-map.yaml:34-39`
  - `method/tools/bomdd-job.py:105-109`
- 内容:
  - 実装は `fnmatch.fnmatch()` を使用している。
  - `method/tools/*.py` は単一階層を意図したパターンだが、`method/tools/sub/x.py` にも一致した。
  - Windows では `method\tools\x.py` にも一致し、結果が OS のパス正規化に依存する。
  - これにより instrument-change が過剰に成立し、不要な `calibrate` が `required_skills` に入る。

実測出力:

```json
{
  "method/tools/x.py": true,
  "method/tools/sub/x.py": true,
  "method\\tools\\x.py": true,
  "docs/x.py": false
}
```

仕様どおりなら `method/tools/sub/x.py` は不一致であるため、区切りを跨がない glob 判定が必要です。情報欄であり現時点では gate ではありませんが、F1 の導出精度に直接影響します。

### IA-03 — MEDIUM — anchor に契約の意味が転写されている

- evidence class: 正本間の静的照合
- 該当箇所:
  - `method/templates/product-profile/skills/activation-map.yaml:32`
  - `method/templates/product-profile/skills/activation-map.yaml:39`
  - `bomdd/60-change-order-eco-064.md:30-35`
- 内容:
  - §0.3 は対応表を所在参照に留め、契約文の二重正本化を避けることを要求している。
  - 次の anchor は台帳側の機械的事実に加え、参照先契約の意味を括弧内で再解釈している。

```text
register.status == verified(verification 節を書くイベント)
register.affected_refs ... に一致する(検査器の新設・変更)
```

- `status == verified` と「verification 節を書くイベント」、パス一致と「検査器の新設・変更」は同一事実ではなく、契約意味の対応付けである。
- 契約変更時に source と anchor の意味が分岐し得るため、「所在参照に留まる」という V3/§0.3 の制約を満たさない。

### IA-04 — MEDIUM — V3 selftest は `#` 以降の節を検査していない

- evidence class: negative control
- 該当箇所:
  - `method/tools/bomdd-job.py:315-319`
  - `bomdd/60-change-order-eco-064.md:69-71`
  - `bomdd/60-change-order-eco-064.md:129-131`
- 内容:
  - selftest は `source` を `#` で切り、ファイル部分の存在しか確認しない。
  - OS temp の map で全 source fragment を `#不存在` に変更しても selftest は PASS した。

実測:

```text
python method/tools/bomdd-job.py --selftest
exit: 0
bomdd-job selftest PASS(... F1: map 実在+source 実在 ...)
```

現行 map の参照先は手作業では以下へ追跡できました。

- `preflight.md:21` — 自発起動契約
- `converge.md:15` — 自発起動契約
- `calibrate.md:22` — 自発起動契約、本文の ①・③
- `self-conformance.py:1115,1156` — C16 と `CONVERGE_HARD_POSITIVES`
- `self-conformance.py:1408,1439` — C17 と `C17_RECEIPT_RE`

ただし `#C16 CONVERGE_HARD_POSITIVES` や `#自発起動契約 ③` は literal な節見出しではなく、人間による解釈を要する座標です。製造者の「selftest が V3 を確認した」という証拠は、節の実在について弁別力がありません。

### IA-05 — ENVIRONMENT / UNKNOWN — `self-conformance` の C14 が測定不能

- evidence class: 常設検査と原因分離
- 該当箇所:
  - `method/tools/self-conformance.py:655-734`
- コマンド:

```text
python method/tools/self-conformance.py
```

結果:

```text
exit: 1
C1〜C13: PASS
C14: FAIL ... 実 scaffold = 6/7 — 失敗: ['REAL']
C15〜C18: PASS
self-conformance FAILED — 1 件の不適合
```

単独再現:

```text
python method/tools/bomdd-init.py FreshSmoke --dir <OS-temp> --no-gui --no-git
INIT_EXIT=0

python method/tools/kit-freshness.py --root <OS-temp>/FreshSmoke
FRESHNESS_EXIT=3
kit-freshness: UNKNOWN reason=ORIGIN_NOT_GIT
```

原因出力:

```text
fatal: detected dubious ownership in repository
repository owner: straw? Akira account
current user: CodexSandboxOffline
```

これは実行基盤の Git ownership 制約であり、ECO-064 の製造物欠陥とは帰属しません。ただし測定不能は PASS ではないため、常設検査の全 PASS は本検査から支持できません。

## V1 — selftest

### bomdd-job

```text
python method/tools/bomdd-job.py --selftest
exit: 0
bomdd-job selftest PASS(整合 NONE / 不整合 2 方向 / order 不在 /
fence 内見出し無視 / 出所なし欄 null / 全欄 source /
r2: 複数 --json 単一文書・引数不正 MISSING_INPUT・null エントリ・
r2b: 対象なし/未知オプション MISSING_INPUT /
F1: map 実在+source 実在・陽性/陰性 class・fence 内 receipt 無視・
map 不在/sc 不能/order 不在= unknown)
```

### bomdd-witness

```text
python method/tools/bomdd-witness.py --selftest
exit: 0
bomdd-witness selftest PASS(known-good 0 / hash・fail・missing・stop・dirty 1 /
不在 2 / 不正 stop 2 / 作業木内出力 2 /
r2: 構造不完全 gate 1・不BEL? ...)
```

V1 の二つの指定 selftest は PASS です。ただし IA-04 のとおり、job selftest の V3 表示は source fragment の実在まで証明しません。

## V2 — 導出結果

コマンド:

```text
python method/tools/bomdd-job.py ECO-062 ECO-063 ECO-064 --json
exit: 0
```

order と register を独立に読んで得た期待値との突合:

| ECO | 独立に判定した class | required_skills | skills_observed | skills_missing | 結果 |
|---|---|---|---|---|---|
| ECO-062 | start / design-synthesis / verified-promotion / instrument-change | preflight, converge, calibrate | preflight, converge, calibrate | `[]` | 一致 |
| ECO-063 | start / verified-promotion / instrument-change | preflight, calibrate | preflight, converge, calibrate | `[]` | 一致 |
| ECO-064 | start / design-synthesis / instrument-change | preflight, converge, calibrate | preflight, converge | `[calibrate]` | 一致 |

C16 hard-positive を同じ fence 除去後テキストに対して独立列挙した結果:

```json
{
  "ECO-062": {
    "adjudication-gate": ["gate ①", "gate ①"],
    "open-gate": ["残ゲート", "残ゲート"]
  },
  "ECO-063": {},
  "ECO-064": {
    "adjudication-request": ["裁定を求め"],
    "adjudication-gate": ["gate ①"],
    "adjudication-target": ["裁定対象"],
    "open-gate": ["残ゲート", "残ゲート"]
  }
}
```

ECO-063 には指定された 5 種の hard-positive はありません。ECO-064 の calibrate 要求は `status=implemented` なので verified-promotion ではなく、` affected_refs` の `method/tools/bomdd-job.py` による instrument-change から来ています。

## V3 — 参照実在

- required skill ファイル:
  - `preflight.md`: 実在
  - `converge.md`: 実在
  - `calibrate.md`: 実在
- source のファイル部分: 全件実在
- source の意図された節・記号: 手作業で追跡可能
- literal fragment の自動検証: 不成立（IA-04）
- anchor の所在参照限定: 不適合（IA-03）

したがって V3 は総合 FAIL です。

## 二重正本

`bomdd-job.py:71-81` は以下を `self-conformance.py` から import しています。

```text
CONVERGE_HARD_POSITIVES
CONVERGE_RECEIPT_HEAD_RE
C17_RECEIPT_RE
_strip_fences_all
```

C16 hard-positive、converge receipt、calibrate receipt、fence 除去の再実装は確認されませんでした。preflight receipt のみ、C 検査側に正本がないため `PREFLIGHT_RECEIPT_RE` を job 側で保持しています。

self-conformance 不在の temp 複製:

```json
{
  "exit": 0,
  "required_skills": {
    "value": ["preflight", "calibrate"],
    "source": "... 判定不能 class= design-synthesis ..."
  },
  "skills_observed": {
    "value": null,
    "source": "unknown(order 不在または self-conformance import 不能)"
  },
  "skills_missing": {
    "value": null,
    "source": "unknown(observed が判定不能)"
  }
}
```

この故障経路は PASS に丸められていません。

## unknown・欠測

| 条件 | exit | 観測 |
|---|---:|---|
| activation-map 不在 | 0 | required=null + `unknown(MAP_MISSING)`、missing=null+unknown |
| classes 空 | 0 | required=null + `unknown(...classes 配列なし)` |
| self-conformance 不在 | 0 | observed/missing=null+unknown、design-synthesis 判定不能 |
| order 不在 | 0 | stop_type=MISSING_INPUT、observed/missing=null+unknown |
| PyYAML 不在 (`python -S`) | 0 | stop_type=MISSING_INPUT、source=`導出: PyYAML 不在` |

PyYAML 不在では job の三つの skill 欄自体は生成されませんが、`MISSING_INPUT` なので PASS 表示にはなりません。通常の map/import/order 欠測でも、skill 欄の source は明示的に unknown です。`stop_type=NONE` は skill 欄を gate 化しない設計のため map/import 欠測時にも残ります。

## receipt 境界ケース

実測結果:

```json
{
  "``` fence 内": [],
  "~~~ fence 内": [],
  "未閉鎖 fence": [],
  "見出し前4空白": [],
  "preflight  receipt": ["preflight"],
  "PREFLIGHT RECEIPT": ["preflight"],
  "converge  receipt": ["converge"],
  "CONVERGE RECEIPT": ["converge"],
  "CALIBRATE RECEIPT": ["calibrate"]
}
```

指定された fence、インデント、空白、大文字小文字の枝は期待どおりです。

## 停止語彙・引数・既存欄

`d9fe305..24e16e06` の diff を照合しました。

STOP_VOCABULARY 8 値:

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

DERIVABLE_FROM_LEDGER 3 値:

```text
NONE
LEDGER_INCONSISTENT
MISSING_INPUT
```

いずれも `d9fe305` から変更なし。`select()` の既存引数処理にも diff はありません。

実測:

```text
python method/tools/bomdd-job.py --register
exit 0 / stop_type: MISSING_INPUT / --register に値がない

python method/tools/bomdd-job.py --bogus ECO-064
exit 0 / stop_type: MISSING_INPUT / 未知のオプション: --bogus

python method/tools/bomdd-job.py --json
exit 0 / stop_type: MISSING_INPUT / 対象指定なし
```

通常入力における既存欄と stop_type の変化は確認されませんでした。IA-01 の malformed map では通常 CLI が exit 1 になります。

## diff 監査・案超過

コマンド:

```text
git diff --name-status da41238..24e16e06e8b527ec268c4227dc28488f0bdc1b65
```

出力:

```text
M bomdd/60-change-order-eco-064.md
M bomdd/60-change-register.yaml
A method/templates/product-profile/skills/activation-map.yaml
M method/tools/bomdd-job.py
```

以下には diff なし:

```text
method/tools/self-conformance.py
method/templates/product-profile/skills/*.md
README.md
bomdd/hooks/*
.github/workflows/*
```

§1「採らない」のうち、以下の実装は確認されませんでした。

- `skills_missing` の gate 化・停止種別化
- preflight 最小表への行追加
- F2〜F6 の同時実装
- calibrate ②④の機械化

一方、契約文転写の禁止は IA-03 の括弧内説明により満たしていません。

## 一時領域

本検査が直接作成した `eco064-*` temp は `TemporaryDirectory` 終了時に削除され、存在しないことを確認しました。

`self-conformance.py` 実行時刻に作成された次の C14 temp について削除を要求しましたが、実行基盤に拒否されました。

```text
C:\Users\akira\AppData\Local\Temp\bomdd-selfconf-c14-drftjzov
C:\Users\akira\AppData\Local\Temp\bomdd-selfconf-c14-938ogxns
```

同 prefix のより古いディレクトリは本検査開始前から存在したものとして、削除対象にしていません。

## /preflight receipt

- task classification: 既存 revision に対する独立受入検査
- baseline: 指定 revision と HEAD の一致を confirmed
- current-work-state: ECO-064 status=implemented、独立検査待ちを confirmed
- acceptance-target: ユーザー指定 V1〜V3・故障注入・diff・案超過を confirmed
- repository state: 開始時・終了時とも clean
- 開始判定: PROCEED
- override: なし

## /calibrate receipt

- 査定した主張:
  - V1 selftest PASS: observed / 条件付き適格（IA-04 の未検次元あり）
  - V2 現行 3 ECO の導出: observed / 適格
  - V3 source/anchor: observed / 不適格
  - exit 0 契約: observed / 不適格
  - self-conformance 全 PASS: observed / 不適格（C14 は環境制約による UNKNOWN）
- 計器欠陥:
  - malformed map の型検査欠落
  - glob の区切り非認識
  - source fragment の negative control 欠落
- 検出力の限界:
  - Linux/macOS 上の glob 動作は未測定
  - リモート CI は未確認
  - 認識依存 trigger ②④の意味的被覆は対象外
- battery:
  - Q1 asked
  - Q2 asked
  - Q3 asked
  - Q4 asked
  - Q5 asked
  - Q6 asked
  - Q7 asked
  - Q8 NA（新規 gate なし）
  - Q9 asked
  - Q10 asked
  - Q11 asked

## 未検査項目

- 対象 revision のリモート CI 結論
- Windows 以外での glob・パス区切り動作
- calibrate の認識依存 trigger ②・④
- 実運用消費側が unknown source を必ず確認するか

## この検査が支持しないもの

リモート CI が成功していることは支持しない。  
全 OS・全 malformed YAML に対する安全性は支持しない。  
`required_skills` の情報欄を将来 gate 化して安全であることは支持しない。