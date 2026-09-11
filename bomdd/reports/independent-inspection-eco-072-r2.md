[INFORM / COMPLETE]

ACCEPT

ECO-072 r2 の指定 range「是正確認+回帰」はすべて期待どおりでした。新規所見 IA-05 以降はありません。

human_action: none。検査は完了し、リポジトリ内の作成・変更・削除はありません。最終 `git status --short` は空、`$LASTEXITCODE=0` です。

## 1. IA-01 是正確認

再現コマンド:

```powershell
python -B "$env:TEMP\eco072_r2_harness.py"
$LASTEXITCODE
```

観測:

```text
unselected_list:
STOP ECO-900 job:MISSING_INPUT → operator @e657d755d539
exit=1 / launched=false

unselected_number:
STOP ECO-900 job:MISSING_INPUT → operator @6654713a76ff
exit=1 / launched=false

unselected_dict:
STOP ECO-900 job:MISSING_INPUT → operator @26152056956b
exit=1 / launched=false

unselected_null:
ADVANCE ECO-900 OK → next · launching @5a74f3b042e2
exit=0 / launched=true

unselected_missing:
ADVANCE ECO-900 OK → next · launching @7603cc6a5448
exit=0 / launched=true

selected_null:
STOP ECO-900 INDEPENDENCE_FAIL(AXIS_UNKNOWN:model) → operator @2b1e19c81a14
exit=1 / launched=false

R2_HARNESS_LASTEXITCODE=0
```

job ビューでは不正な未選択 entry の3腕とも `required_capability.value=null`、`stop_type=MISSING_INPUT`。エラー source はそれぞれ `list` / `int` / `dict` を明示しました。

期待との差: なし。

## 2. IA-02 是正確認

同じ harness で観測:

```text
casefold_spaces:
STOP ECO-900 INDEPENDENCE_FAIL(SAME_LINEAGE) → operator @e152e4ac5a80
exit=1 / launched=false
axes={model:true,harness:true,account_lineage:true}

one_real_axis_diff:
ADVANCE ECO-900 OK → next · launching @475b93033a9a
exit=0 / launched=true
axes={model:false,harness:true,account_lineage:true}
```

producer `m1/h1/a1` と executor `M1/'  h1  '/A1` は同一来歴として停止。model を `m2` にすると起動しました。

期待との差: なし。

## 3. IA-03 是正確認

同じ harness で観測:

```text
comment_inside:
STOP ECO-900 INDEPENDENCE_FAIL(PRODUCER_UNDECLARED) → operator @6b442ba95203
exit=1 / launched=false

comment_outside:
STOP ECO-900 INDEPENDENCE_FAIL(PRODUCER_UNDECLARED) → operator @ccc84586d3a4
exit=1 / launched=false

other_section:
STOP ECO-900 INDEPENDENCE_FAIL(PRODUCER_UNDECLARED) → operator @070c7c979fda
exit=1 / launched=false

no_heading:
STOP ECO-900 INDEPENDENCE_FAIL(PRODUCER_UNDECLARED) → operator @01af7c35054d
exit=1 / launched=false

after_same_level:
STOP ECO-900 INDEPENDENCE_FAIL(PRODUCER_UNDECLARED) → operator @343a319d1fca
exit=1 / launched=false
```

採用される対照腕:

```text
direct_valid:
ADVANCE ECO-900 OK → next · launching @f505b609fc2f
exit=0 / launched=true

subheading_valid:
ADVANCE ECO-900 OK → next · launching @429c6c152a13
exit=0 / launched=true

equipment_english:
ADVANCE ECO-900 OK → next · launching @dbe91489977c
exit=0 / launched=true
```

HTML コメント内外、他節、見出しなし、次の同位見出し以降は不採用。担当設備節直下、下位見出し内、英語 `equipment` 見出しは採用されました。

期待との差: なし。

## 4. 回帰

境界回帰コマンド:

```powershell
python -B "$env:TEMP\eco072_boundary_harness.py"
$LASTEXITCODE
```

観測の要約:

- executor 欠落: `UNMEASURABLE ARG_ERROR...`、exit 2、起動なし。
- executor 構文外: `UNMEASURABLE ARG_ERROR...`、exit 2、起動なし。
- executor 未知 id: `INDEPENDENCE_FAIL(EXECUTOR_UNKNOWN)`、exit 1、起動なし。
- producer 未宣言: `INDEPENDENCE_FAIL(PRODUCER_UNDECLARED)`、exit 1、起動なし。
- 同一 id: `INDEPENDENCE_FAIL(SAME_ID)`、exit 1、起動なし。
- 3軸一致: `INDEPENDENCE_FAIL(SAME_LINEAGE)`、exit 1、起動なし。
- 同一 producer id の重複は起動。異なる id の重複は `job:LEDGER_INCONSISTENT`。
- fence、引用、見出し行、全角コロン、`=`、4文字インデントは不採用。3文字インデントは従来どおり採用。
- 台帳形状7種（配列なし、文字 entry、重複 id、短い/lowercase/長い id、タブ YAML）はすべて `job:MISSING_INPUT`、exit 1、起動なし。
- UTF-8 BOM 付き完全台帳は `ADVANCE`、exit 0。明確化された仕様どおり。
- 全引数エラーの1行目は `UNMEASURABLE`、判定経路は `ADVANCE` または `STOP`。最大長は80桁。
- harness `$LASTEXITCODE=0`。

停止優先順位の三条件同時腕:

```text
STOP ECO-900 job:LEDGER_INCONSISTENT → ledger-owner @89d46a670025
exit=1 / launched=false / independence=null
R2_TARGETED_LASTEXITCODE=0
```

receipt 不良+同一 executor では:

```text
STOP ECO-900 TREE_MISMATCH → operator @eaeecec61428
exit=1 / launched=false / stop_type=VERIFICATION_FAIL
```

したがって `job > receipt > independence` は不変です。

別プロセス・別 cwd・環境変数:

```powershell
python -B <repo>\method\tools\bomdd-run.py ECO-900 `
  --ledger "$env:TEMP\eco072-r2-external-valid.jsonl" `
  --executor EQ-002 `
  --cell 'python -c "import os; print(os.environ.get(''BOMDD_EXECUTOR''))"'
$LASTEXITCODE
```

```text
ADVANCE ECO-900 OK → next · launching @dbe91489977c
EQ-002
cell exit 0
EXTERNAL_PROCESS_VALID_LASTEXITCODE=0
```

後方互換 dry は旧個体と現個体で同一:

```text
旧: ADVANCE ECO-900 OK → next · dry @220237d0b906
OLD_DRY_LASTEXITCODE=0

現: ADVANCE ECO-900 OK → next · dry @220237d0b906
DRY_BACKCOMPAT_LASTEXITCODE=0
```

selftest:

```text
bomdd-job selftest PASS(...r1: IA-01...IA-03...)
JOB_SELFTEST_LASTEXITCODE=0

ADVANCE OK: selftest PASS(起動2/dry2/kb5/.../独立性9/.../80桁/表)
RUN_SELFTEST_LASTEXITCODE=0

ADVANCE OK: selftest PASS(known-good / hash・fail・missing・stop...)
WITNESS_SELFTEST_LASTEXITCODE=0
```

期待との差: なし。

## 5. 既存 order の非影響

再現コマンド:

```powershell
python -B method/tools/bomdd-job.py ECO-071 --json
$LASTEXITCODE

python -B method/tools/bomdd-job.py ECO-072 --json
$LASTEXITCODE
```

いずれも1行目は `{`、`$LASTEXITCODE=0`。

観測:

```text
ECO-071:
required_capability.value=null
stop_type.value=NONE

ECO-072:
required_capability.value={producer: EQ-001, inspector: EQ-002}
stop_type.value=NONE
```

期待との差: なし。

## 測定系較正 receipt

- 主張: IA-01〜03 の是正が成立し、r1 で観測した既存境界が指定範囲内で回帰していない。
- 測定成立性: `observed`。
- 証拠資格: `条件付き適格`。実 git fixture、起動 marker、decision ledger、旧個体との dry 比較、組込み selftest を使用。
- 計器欠陥: なし。r1 で欠けていた IA-01〜03 の対照腕が selftest に追加され、外部 fixture の known-bad/known-good 対でも弁別した。
- 限界: Windows/Python 3.13.1/PyYAML 6.0.3、単一 round。新しい入力クラス、Unicode 正規化、独立性の実効は未測定。
- battery: Q1 asked / Q2 asked / Q3 asked / Q4 asked / Q5 asked / Q6 asked / Q7 asked / Q8 NA / Q9 asked / Q10 asked / Q11 asked。

## /preflight receipt

- 分類: continuation（ECO-072 r1b 後の是正確認）。
- baseline、現在状態、r1 所見、受入目標: confirmed。
- 開始判定: `PROCEED_WITH_LIMITS`。
- 制限: 作業木 read-only、fixture/ledger は OS temp、range は是正確認+回帰。
- override: なし。

## 範囲外の観察

- なし。Unicode 正規化、独立性の実効、sandbox の git 所有者問題は探索・判定していません。