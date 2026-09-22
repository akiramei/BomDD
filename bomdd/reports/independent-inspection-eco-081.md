[INFORM / COMPLETE]

REJECT IA-01, IA-02, IA-03, IA-04, IA-05

- range: 境界探索
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: `9e59d428372fcff2ec23a62fef2a792d16878d90`
- commit: 0（開始・終了とも同一 HEAD）
- 外部 API: 呼出しなし

開始時 `git status --short`:

```text
（出力なし）
```

終了時 `git status --short`:

```text
（出力なし）
```

## 判定概要

| 条件 | 判定 | 観測 |
|---|---|---|
| V1 core 固有語正規表現 | PASS | core 0件、adapter 陽性対照16件 |
| V2 生成物 | PASS | init exit 0、2ファイル実在、未解決 `{{` 0、正典参照先実在、YAML parse PASS、skills 13 |
| V3 注記の禁止語 | PASS | 70-equipment注記 0件、register注記2行 0件 |
| V4 self-conformance | FAIL | exit 1、C14 `kit-freshness ... REAL` |
| V4 diff窓 | FAIL | allowed_paths 外8ファイル |
| V4 CI | 測れなかった | 外部API禁止のため未照会 |
| 第三者記述試験 | 一部不成立 | 書式例は作成できたが、provenance範囲・status語彙などを推測で補った |

## 所見

### IA-01 — 凍結された diff 窓が allowed_paths 外を含む

- 再現コマンド:  
  `git diff --name-only e0d4b52 9e59d428372fcff2ec23a62fef2a792d16878d90`
- 観測: 次の8ファイルが ECO-081 の `allowed_paths` 外だった。

```text
bomdd/reports/jev-qualification-02/README.md
bomdd/reports/jev-qualification-02/gauge-log.jsonl
bomdd/reports/jev-qualification-02/gauge/03-r0-draft.md
bomdd/reports/jev-qualification-02/gauge/03-r1-rewrite.md
bomdd/reports/jev-qualification-02/gauge/04-r0-draft.md
bomdd/reports/jev-qualification-02/gauge/04-r1-rewrite.md
bomdd/reports/jev-qualification-02/gauge/04-r2-rewrite.md
method/bomdd-playbook-v1.md
```

- 期待との差: V4 は `baseline=e0d4b52` から対象 revision までを allowed_paths のみに限定する。さらに「採らない」の `playbook` 改訂について、指定窓では実際に17行の差分がある。
- 補足: 対象 commit `9e59d42` 単体の8変更ファイルは allowed_paths 内だった。違反は baseline 後に挟まった別commitを含む凍結窓で発生している。
- 帰属: 製造物（revision/diff窓管理）。

### IA-02 — 必須自己適合検査が非0

- 再現コマンド:  
  `python method/tools/self-conformance.py`
- 観測: exit 1。C1〜C13、C15〜C18はPASSしたが、次の1件がFAIL。

```text
[C14] FAIL kit-freshness 対照実測
(FRESH/STALE/UNKNOWN/TAMPERED/余剰/入力不正/実 scaffold = 6/7)
— 失敗: ['REAL']
self-conformance FAILED — 1 件の不適合
```

- 期待との差: V4 は全PASSかつ exit 0 を要求する。
- 帰属: 製造物／検査環境。`REAL` 腕の失敗原因までは本roundで切り分けていない。

### IA-03 — coreだけでは provenance の対象属性と status 語彙が一意に定まらない

- 読解箇所: `operator-layer.md` §3。
- 観測:
  - 「provenance は各属性に付す」と読めるが、対象が独立性3軸だけなのか、`kind`・`qualification_ref`・`status` 等も含むのか明示されない。
  - `status: retired` は指定される一方、使用中設備の値は定義されていない。試験成果物では雛形を見ずに `active` を推測した。
  - provenance のYAML構造も、属性別mapか各値との組かをcoreだけでは確定できなかった。
- 期待との差: BomDDを知らない書き手がcoreだけで§3準拠の設備エントリを一意に書けること。
- 帰属: 製造物。

### IA-04 — core内に配布元の規約を知らないと意味が定まらない語が残る

- 読解箇所: `operator-layer.md` 1、3、37、48、62、67、76、77、79、86行。
- 観測:
  - `verified` は状態語として使われるが、core内に定義や状態集合がない。
  - `executor` と `inspector` が同義か、別の役割かは括弧表記以上に定義されない。
  - `bomdd/` 配下の固定パス、`BOM`、`handoff`、`{{METHOD}}` は配布形態または方法論側の知識を要する。
- 期待との差: adapter以前が環境非依存かつ第三者だけで意味を確定できること。
- 帰属: 製造物。

### IA-05 — 「射影は手書きしない」が機構の存在を示唆する

- 読解箇所: core §1、§7。
- 観測:
  - §1は job / receipt / ruling を「台帳から導かれる射影」とし、「射影は手書きしない」と命令する。
  - 冒頭と§7は「読む機構の存在を主張しない」「機構がなければ運転員が手で行う」とする。
  - 機構がない環境で、手書きせずに射影をどう成立させるかが明示されず、第三者には自動生成機構が存在するようにも読めた。
  - §2の「運転員は解決しない」と§7の「運転員が手で行う」は、§7が分類・照合・記述・回収を列挙しているため、「問題の解決」と「工程操作」の区別として読めた。こちらは直接の矛盾とは判定しない。
- 期待との差: coreから機構の存在を読み取れず、人手運用との関係も一義的であること。
- 帰属: 製造物。

## 第三者記述試験の成果物

実ファイルをOS tempへ作成した。以下はその内容。

### (a) 架空設備2件

```yaml
equipment:
  - id: EQ-101
    kind: ai-model
    model: model-alpha
    harness: harness-red
    account_lineage: account-a
    provenance:
      model: self-reported
      harness: harness-measured
      account_lineage: user-declared
    qualification_ref: "qualification-record-ai-01"
    status: active
  - id: EQ-102
    kind: human
    model: human
    harness: manual-review
    account_lineage: account-b
    provenance:
      model: user-declared
      harness: user-declared
      account_lineage: user-declared
    qualification_ref: "qualification-record-human-01"
    status: active
```

`provenance` の対象と `status: active` はcoreだけでは確定できず、推測で補った。

### (b) 架空変更の配員

registerエントリ:

```yaml
producer: EQ-101
inspector: EQ-102
```

order担当設備節:

```markdown
- producer: EQ-101
- inspector: EQ-102
```

### (c) 独立性判定

```text
成立 — id は異なり、3軸はすべて既知で、model / harness /
account_lineage の全一致ではなく、producer と inspector の双方が
台帳に宣言されているため。
```

### (d) 検査報告の先頭3行

```text
[INFORM / COMPLETE]

ACCEPT
```

## core語彙一覧

| 語 | 件数 | 行 | 区分 |
|---|---:|---|---|
| V1正規表現全体 | 0 | — | 正規表現内 |
| `bomdd/` | 3 | 48, 76, 77 | 読解 |
| `verified` | 1 | 79 | 読解 |
| `executor` | 2 | 62, 67 | 読解 |
| `{{PRODUCT}}` | 1 | 1 | 読解 |
| `{{METHOD}}` | 1 | 3 | 読解 |
| `BOM` | 1 | 37 | 読解 |
| `handoff` | 1 | 86 | 読解 |
| `job` | 1 | 19 | 読解。ただし§1表で意味説明あり |
| `receipt` | 1 | 20 | 読解。ただし§1表で意味説明あり |
| `ruling` | 1 | 21 | 読解。ただし§1表で意味説明あり |

V1計器の陽性対照として、同じ正規表現はadapter内で16件一致した。

## 停止語彙と配送先

`bomdd-job.py:57-68` と `bomdd-run.py:81-92` を読んで比較した。10語と配送先は1対1で一致した。

```text
NONE                 -> next
NORMATIVE_RULING     -> human
CONVERGENCE_LIMIT    -> human
VERIFICATION_FAIL    -> factory
BOM_CONTRADICTION    -> designer
PREFLIGHT_HOLD       -> process
LEDGER_INCONSISTENT  -> ledger-owner
MISSING_INPUT        -> operator
INDEPENDENCE_FAIL    -> operator
INSPECTION_MISSING   -> operator
```

core §2とも一致した。

## 機構注記の検査

V3正規表現:

```text
工程が止まる|STOP|LEDGER_INCONSISTENT|INDEPENDENCE_FAIL|解決し|照合し
```

結果:

```text
70-equipment.yaml 注記: 0件
60-change-register.yaml の producer/inspector 注記2行: 0件
```

注記はいずれも、機械的な導出・検証・強制が存在しないことを明記しており、注記自体から機構が存在するとは読まなかった。

## 生成試験

再現コマンド:

```text
python method/tools/bomdd-init.py Smoke --dir <OS temp> --no-gui --no-git
```

観測:

```text
exit 0
bomdd/70-equipment.yaml: 実在
bomdd/operator-layer.md: 実在
対象2ファイルの未解決 "{{": 0
正典行: bomdd-kit/method/templates/product-profile/operator-layer.md
正典参照先: 実在
70-equipment.yaml strict YAML parse: PASS（equipment 1件）
.claude/skills/: 13
```

READMEの配置先 `<product>/bomdd/operator-layer.md` と実生成先は一致した。READMEの「phaseテンプレのglobで複写」も `PHASE_TEMPLATE_GLOBS` の `[0-9][0-9]-*.yaml` と一致した。

## 「採らない」の確認

凍結baselineからの指定差分で確認した結果:

- `change-management.md`: 差分なし
- `method/templates/60-change-order.md`: 差分なし
- `method/templates/process-core/`: 差分なし
- `bomdd-job.py` / `bomdd-run.py` / `bomdd-witness.py`: 差分なし
- `method/bomdd-playbook-v1.md`: 差分あり（IA-01）
- ViewTubeへの設置、設備台帳への実設備初期値、activation-map追加: 対象commit単体では観測なし

## 較正 receipt

- 査定した主張と判定:
  - V1: PASS — core regex 0、adapter陽性対照16。
  - V2: PASS — init exit 0、生成物・参照・YAML・skills確認。
  - V3: PASS — 対象注記の禁止語0。
  - V4: FAIL — diff窓違反およびself-conformance exit 1。
  - 第三者記述可能性: REJECT — provenance/statusの不足を推測で補う必要があった。
  - 機構非示唆性: REJECT — §1の「導かれる」「手書きしない」が自動機構を示唆し得る。
- 検出した計器欠陥と帰属:
  - V1正規表現は `bomdd/`、`verified`、`executor` 等の読解上の環境依存を検出しない。帰属は受入条件の正規表現。
  - V3正規表現は「導かれる」「手書きしない」の組合せによる機構示唆を検出しない。帰属は受入条件の正規表現。今回の読解検査で補完した。
- 検出力の限界:
  - 外部API禁止のため、対象revisionのCI結論は測っていない。
  - 製品リポでの実運用、人間間の理解一致、qualification参照の実在・有効性は測っていない。
  - 本roundは境界探索であり、全曖昧性の網羅を主張しない。
- battery:
  - Q1: NA — 定義本文はブリーフ指定の読取範囲外。
  - Q2: NA — 同上。
  - Q3: NA — 同上。
  - Q4: NA — 同上。
  - Q5: NA — 同上。
  - Q6: NA — 同上。
  - Q7: NA — 同上。
  - Q8: NA — 同上。
  - Q9: NA — 同上。
  - Q10: NA — 同上。
  - Q11: NA — 同上。

## 範囲外の観察

なし。