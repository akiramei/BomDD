[INFORM / COMPLETE]

ACCEPT — ECO-077 V1〜V3 に適合。製造物に帰属する所見なし。

- range: 境界探索
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: `5917e29bbeb0fa56ffddf4d6d4ab78e76a83d74a`
- commit: 開始・終了とも同 revision（commit 0）

開始時 `git status --short`:

```text
（出力なし）
```

終了時 `git status --short`:

```text
（出力なし）
EXIT=0
```

## 判定結果

### V1 — selftest・MAP_INVALID

以下はすべて PASS。

```text
python method/tools/bomdd-job.py --selftest
bomdd-job selftest PASS(... F7〔ECO-077〕: roles 必須キー・by_role ... )
EXIT=0

python method/tools/bomdd-run.py --selftest
ADVANCE OK: selftest PASS(...)
EXIT=0

python method/tools/bomdd-witness.py --selftest
ADVANCE OK: selftest PASS(...)
EXIT=0
```

OS temp に map を複製し、`start.roles` を削除して `load_map(temp, repo)` を実行:

```text
classes= None
error= activation-map 不正(MAP_INVALID): class 'start': roles が非空の文字列配列でない
EXIT=0
```

期待との差: なし。欠落は fail-closed。  
帰属: 製造物。

### validate_map 境界

各入力の観測結果:

```text
dict                  → roles が非空の文字列配列でない
number                → roles が非空の文字列配列でない
[""]                  → roles が非空の文字列配列でない
[" producer"]         → 語彙にない
["PRODUCER"]          → 語彙にない
[null]                → roles が非空の文字列配列でない
["human"]             → 語彙にない
["producer","producer"] → 重複
["producer","inspector"] → 問題なし
["inspector","producer"] → 問題なし
EXIT=0
```

traceback なし。期待との差なし。  
帰属: 製造物。

### V2 — project・回帰

- 複数 class・複数 role の同一 skill は重複なく辞書順。
- class 順序反転後も `required_skills_by_role` は同一。
- map 不在時は `value: null`、source は `unknown`。
- `receipt_author_role`:

```text
""                    → ""
"Producer"            → "Producer"
["producer"]          → null
{"role":"producer"}   → null
7                     → null
```

全入力で `stop_type`・`required_skills`・`skills_missing` は不変。空文字・語彙外文字列の透過は、ブリーフに明記された観測欄仕様と一致するため所見にしない。

ECO-076 実測:

```text
required_skills: ["calibrate","preflight"]
required_skills_by_role:
  inspector: ["calibrate"]
  producer: ["calibrate","preflight"]
receipt_author_role: null
stop_type: NONE
EXIT=0
```

旧版 `940e757` と全 register entry 77 件を比較:

```text
entries_compared: 77
required_skills_differences: []
new_field_missing: []
EXIT=0
```

`--all --json` の旧新版比較でも、選択された ECO-077 に required 差分・新欄欠落ともなし。

ECO-077 を OS-temp 相当の verified/producer entry として射影:

```text
required_skills: ["calibrate","preflight"]
required_skills_by_role:
  inspector: ["calibrate"]
  producer: ["calibrate","preflight"]
receipt_author_role: "producer"
EXIT=0
```

`bomdd-run ECO-076` の既定実行は revision 外の環境状態により測定不成立だった:

```text
UNMEASURABLE ARG_ERROR: 台帳を書けない(PermissionError): …git\bomdd-run\ECO-076.jsonl
EXIT=2
```

OS temp ledger を指定すると、既存 ECO-076 witness が旧 tree のため:

```text
STOP ECO-076 TREE_MISMATCH → operator @cda1e4dd7c8f
EXIT=1
```

対象 revision を `git bundle` で OS temp に正確に複製し、同 tree の controlled known-good witness で統合経路を再測定:

```text
FIXTURE_HEAD=5917e29bbeb0fa56ffddf4d6d4ab78e76a83d74a
FIXTURE_TREE=cda1e4dd7c8fc851ca8879b5c1ff0ae786747d02
ADVANCE ECO-076 OK → next · dry @cda1e4dd7c8f
INNER_EXIT=0
EXIT=0
```

期待との差: 製造物についてなし。既定実行の不成立は `.git` の権限と旧 witness という環境帰属であり、exact-revision fixture では additive な job 欄を処理して ADVANCE。  
帰属: 環境／製造物を分離済み。

### V3 — 文書・scaffold

正本と写しの diff:

```text
@@ -8 +8,5 @@
  正本注記の置換
@@ -10 +14 @@
  {{METHOD}} のリポ相対解決
EXIT=1
```

差分は期待された 2 hunk のみ。写しの `{{METHOD}}` 検索は 0 件（`rg` exit 1）。

工程1には producer の責任・使用手順・diff/commit/register/受入判定により観測可能な禁止、工程5には inspector の対応欄が存在。「注意して」「意識」等の観測不能な禁止は役割欄に混入していない。

テンプレ YAML:

```text
dict list 1
EXIT=0
```

scaffold:

```text
python method/tools/bomdd-init.py Smoke --dir <OS-temp> --no-gui --no-git
[ok] <OS-temp>\Smoke を生成しました
INNER_EXIT=0
REGISTER_COUNT=2
PARSED=True
EXIT=0
```

`ROLE_VOCAB` と `ASSIGN_RE` はともに `producer / inspector`。map は v1.2 で、4 class の roles は order §1 と一致。停止語彙は旧版から不変。`bomdd-run.py`・`bomdd-witness.py` は baseline との差分なし。

期待との差: なし。  
帰属: 製造物。

## 所見

IA 所見は 0 件。測れなかった項目は、既定 `.git` を使う ECO-076 dry のみ。上記 controlled exact-revision fixture で対象の回帰主張を代替測定した。

## 較正 receipt

- 査定した主張と判定:
  - V1: 測定成立・証拠資格あり — PASS。
  - V2: 測定成立・証拠資格あり — PASS。既定 witness の revision 外状態は合格に数えず、exact-revision fixture と77件比較で補完。
  - V3: 測定成立・証拠資格あり — PASS。
- 検出した計器欠陥と帰属: 製造物の計器欠陥なし。既定 ledger の書込権限不足と旧 ECO-076 witness は環境帰属。
- 検出力の限界: V4・CI・verified 昇格後の実 register 行、V5/V6、POSIX、並行実行、網羅的 fuzz は測っていない。境界探索 round なので打ち切りを支持しない。
- battery:
  - Q1 asked — header・map コメント・実装主張を突合。
  - Q2 asked — 凍結要求に基づく known-good/known-bad を実測。
  - Q3 asked — roles の指定境界を入力クラス別に独立測定。
  - Q4 asked — temp map を実際に `load_map` の入力へ接続。
  - Q5 asked — exit 2/1 を PASS に数えず環境原因を分離。
  - Q6 asked —有効証拠は終了コードを直後に観測した単独再実行から採用。
  - Q7 asked — roles 欠落の陽性対照を実測。
  - Q8 asked — 情報欄・停止語彙不変・run/witness 非接触を確認。
  - Q9 asked — HEAD と bundle fixture の revision/tree を刻印・突合。
  - Q10 asked — 上記検出力限界を宣言。
  - Q11 asked — 非配列、要素型、大小文字、空白、語彙外、重複、map 不在、receipt 型を分離測定。

## 範囲外の観察

なし。

human_action: none  
execution state: 独立検査の境界探索 round は完了。リポ内 diff 0、commit 0。