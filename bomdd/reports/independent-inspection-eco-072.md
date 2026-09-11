[INFORM / COMPLETE]

REJECT — 理由: IA-01、IA-02、IA-03。

human_action: none。境界探索 round は完了しました。リポジトリ内の作成・変更・削除はありません。

## 所見

### IA-01 — 台帳内の未選択設備に不正な軸値があっても起動する

再現コマンド:

```powershell
python -B "$env:TEMP\eco072_boundary_harness.py" |
  Select-String '"unrelated_bad_axis"'
$LASTEXITCODE
```

入力は EQ-001/EQ-002 が正常、未選択 EQ-003 の `model: [bad]` が list。

観測:

```text
ADVANCE ECO-900 OK → next · launching @e657d755d539
inner exit=0 / harness $LASTEXITCODE=0 / launched=true
stop_type=NONE / delivery=next
```

期待との差: ブリーフは3軸の非文字列を設備台帳不正として停止させる要求だが、台帳全体を検証せず、選択された producer/executor の軸だけを後段で確認するため起動した。

帰属: **製造物**。`load_equipment()` は全 entry の id だけを検証し、3軸の型・欠落・空値を検証していない（`method/tools/bomdd-job.py:287-305`）。

### IA-02 — 大文字小文字だけの軸差を独立性の根拠にして起動する

再現コマンド:

```powershell
python -B "$env:TEMP\eco072_boundary_harness.py" |
  Select-String '"axis_uppercase"'
$LASTEXITCODE
```

入力:

```yaml
producer: {model: m1, harness: h1, account_lineage: a1}
executor: {model: M1, harness: h1, account_lineage: a1}
```

観測:

```text
ADVANCE ECO-900 OK → next · launching @6559eb6fd0e4
inner exit=0 / harness $LASTEXITCODE=0 / launched=true
axes={model:false,harness:true,account_lineage:true}
```

期待との差: 表記の大小文字だけでは異系統と確定できないが、文字列の大小文字を区別して比較し、1軸差として起動した。fail-closed 主張と一致しない。

帰属: **製造物**。比較が `pv.strip() == ev.strip()` のため大小文字を正規化しない（`method/tools/bomdd-run.py:153`）。

前後空白は strip 後に SAME_LINEAGE、`unknown` の大小文字・前後空白、空、欠落、数値、list、null はすべて `AXIS_UNKNOWN:model`、exit 1、起動なしだった。

### IA-03 — コメントまたは担当設備節外の mention を配員宣言として採用する

再現コマンド:

```powershell
python -B "$env:TEMP\eco072_boundary_harness.py" |
  Select-String '"html_comment"|"other_section"'
$LASTEXITCODE
```

観測:

```text
html_comment:
ADVANCE ECO-900 OK → next · launching @6b442ba95203
inner exit=0 / launched=true

other_section:
ADVANCE ECO-900 OK → next · launching @91d5f22fae86
inner exit=0 / launched=true

harness $LASTEXITCODE=0
```

HTML コメントの入力:

```markdown
<!--
- producer: EQ-001
-->
```

もう一方は `## 説明` 節内の `- producer: EQ-001`。

期待との差: どちらも担当設備欄の実宣言ではないが producer として解決され、異系統 executor の cell が起動した。use/mention の区別が閉じていない。

帰属: **製造物**。`assignments()` は fence だけを除去し、HTML コメントを除去せず、担当設備見出しにもスコープしない（`method/tools/bomdd-job.py:308-313`）。

### IA-04 — UTF-8 BOM の扱いについてブリーフと実装の境界が不一致

再現コマンド:

```powershell
python -B "$env:TEMP\eco072_boundary_harness.py" |
  Select-String '"bom_complete"'
$LASTEXITCODE
```

観測:

```text
ADVANCE ECO-900 OK → next · launching @8e55ed227e38
inner exit=0 / harness $LASTEXITCODE=0 / launched=true
```

期待との差: ブリーフは BOM を「YAML 読取不能」の例に含めて停止を要求している。一方、PyYAML は UTF-8 BOM 付きの正常 YAML を読み取るため、完全な台帳なら起動する。

帰属: **ブリーフ**。YAML として BOM を許容するのか、入力規格として明示的に拒否するのかが ECO-072 §1 にない。BOM 禁止を意図する場合は製造物にも検査が必要。

## その他の境界結果

- `--cell` に executor なし、`EQ-1`、`eq-002`、未知 id、producer 未宣言、同一 id、3軸一致はいずれも起動なし。
- 同じ producer id の重複は許容。異なる id の重複は `LEDGER_INCONSISTENT`。inspector のみは `PRODUCER_UNDECLARED`。
- fence、引用、見出し行、全角コロン、`producer=`、4文字インデントは宣言と認識されず起動なし。3文字インデントは認識された。
- `equipment` 配列なし、entry が文字列、id 重複、`EQ-1`、`eq-001`、`EQ-0001`、タブによる YAML エラーは `job:MISSING_INPUT`、exit 1、起動なし。
- 停止優先順位は `job > receipt > independence`。三条件同時では:

```text
STOP ECO-900 job:LEDGER_INCONSISTENT → ledger-owner @aea714cf2d3f
$LASTEXITCODE=1 / marker=false
ledger: stop_type=LEDGER_INCONSISTENT, delivery=ledger-owner
verifier_line=STOP TREE_MISMATCH
```

- receipt 欠陥と同一 executor の組合せでは `TREE_MISMATCH` が優先され、`VERIFICATION_FAIL/operator`。いずれも一意だった。
- `bomdd-run.py` の測定出力は最大80文字。400文字 executor の ARG_ERROR も80文字。全経路の1行目は `ADVANCE` / `STOP` / `UNMEASURABLE` で開始した。
- 別プロセス・fixture cwd・pwsh cell で正常腕を実行し、`BOMDD_EXECUTOR=EQ-002`、cell exit 0、run `$LASTEXITCODE=0` を確認。
- この環境では直接実行と入れ子の `pwsh -Command` の双方で exit 2 が保持された。既知の「2→1丸め」は再現しなかった。

## 後方互換

ECO-071 の現 worktree 比較:

```text
旧: UNMEASURABLE ECO-071 TREE_UNAVAILABLE(ADD_FAILED) → operator @-
新: UNMEASURABLE ECO-071 TREE_UNAVAILABLE(ADD_FAILED) → operator @-
旧/新 $LASTEXITCODE=2
```

dirty tree と sandbox の `.git` 制約によるため、正常 dry 経路は temp の配員欄なし fixture でも比較した:

```text
旧: ADVANCE ECO-900 OK → next · dry @220237d0b906
新: ADVANCE ECO-900 OK → next · dry @220237d0b906
旧/新 $LASTEXITCODE=0
```

job の `stop_type=NONE` と `required_capability=null` は同じ。JSON は `INDEPENDENCE_FAIL` の語彙追加、source 文言更新、run 台帳の executor/producer/independence 追加により完全一致ではないが、判定は後方互換だった。

## selftest 被覆表

| クラス | 組込み被覆 | 未被覆または部分被覆 |
|---|---|---|
| executor 引数 | 欠落、`EQ-1`、`eq-002`、未知 id | 長い値は本探索で追加 |
| 同一性 | 同一 id、3軸一致、1軸差 | 大小文字だけの差 |
| unknown 軸 | literal `unknown` | 空、欠落、数値、list、null、表記揺れ |
| producer | 未宣言 | HTML コメント、設備節外 mention |
| 配員パース | fence、未知 id、構文外、異なる重複 | 同じ重複、引用、見出し、全角コロン、`=`、indent 変種 |
| 設備台帳 | 不在、id 重複、id 構文外 | 配列なし、文字 entry、全軸型、未選択 entry の不正、タブ、BOM |
| 優先順位 | job stop の単独腕 | job+receipt+independence の同時成立 |
| 出力契約 | selftest 内の通常出力、80桁 | 長 executor は本探索で追加 |

組込み結果:

```text
bomdd-job selftest PASS
JOB_LASTEXITCODE=0
ADVANCE OK: selftest PASS(...独立性8...)
RUN_LASTEXITCODE=0
```

緑の8腕は IA-01〜03 の入力クラスを覆っていない。

## 測定系較正 receipt

- 主張: 上記3件は fail-closed 境界を通過して cell を起動する。
- 測定成立性: **observed**。
- 証拠資格: **条件付き適格**。実 fixture、現在の未コミット個体、起動 marker、decision ledger を結線。全可能入力の網羅性は主張しない。
- 計器欠陥: 組込み selftest に IA-01〜03 の陽性対照がなく、selftest 緑だけでは境界主張を支持しない。
- 限界: Windows/Python 3.13.1/PyYAML 6.0.3/workspace-write、単一 round。Linux、別 YAML 実装、Unicode 正規化、実効的独立性は未測定。
- battery: Q1 asked / Q2 asked / Q3 asked / Q4 asked / Q5 asked / Q6 asked / Q7 asked / Q8 NA / Q9 asked / Q10 asked / Q11 asked。

## /preflight receipt

- 分類: continuation。baseline `3e918de` 上の ECO-072 未コミット製造物の独立検査。
- baseline、対象差分、親 Phase 7、受入目標: confirmed。
- register は filed、order は製造裁定 A: 作業中状態として confirmed。ただし状態遷移の受入は範囲外。
- 開始判定: `PROCEED_WITH_LIMITS`。リポは読取専用、fixture/ledger は OS temp のみに限定。
- override: なし。

## 範囲外の観察

- `self-conformance.py` は exit 1。C1〜C13・C15〜C18 は PASS、C14 REAL のみ6/7 FAIL。原因は sandbox の別所有者と、`kit-freshness` が安全ディレクトリ注入を除去した後の Git `dubious ownership`（環境帰属、ECO-072製造物には帰属しない）。
- 重複起動した `self-conformance` の片方に sandbox 管理下の残存 process PID 39304 があり、停止要求はアクセス拒否。リポ状態は開始時と同じ5差分のまま。