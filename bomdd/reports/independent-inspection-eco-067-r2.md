# 独立検査報告 — ECO-067 r2(Codex gpt-5.6-sol・CLI 直接・workspace-write・2026-09-11・対象 commit cc87371・範囲= r1 所見の是正確認+回帰)

> 検査官の最終メッセージをそのまま転記(受理側の判定は order §7.2)。

# REJECT — IA-01、IA-04

対象個体: commit `cc87371030c05e9da4ea5b68ba294bade3234837`  
`bomdd-run.py` SHA-256: `114820EB53DBB695A35DE0E908CAC7D2B5C0FBE69BCAE9D9F8B39621FC22784A`

IA-02・IA-03 は是正を確認しました。IA-01 は余分な位置引数の一部、IA-04 は cell 出力で未是正です。

## 1. IA-01 — 一部未是正

OS temp の git repository を作成し、次の形で CLI を実行しました。

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
@'
# temp repo、register、receipt、marker を生成し、
# subprocess.run([python, bomdd-run.py, ...]) で各腕を実行
'@ | python -
```

register にも登録した区切り付き ECO を含む不正 ECO 5 種:

```text
'ECO-/../../../x' rc=2 ARG_ERROR len=72 launched=false
'ECO-900/../x'    rc=2 ARG_ERROR len=69 launched=false
'..'               rc=2 ARG_ERROR len=59 launched=false
'ECO-900 x'        rc=2 ARG_ERROR len=66 launched=false
'ECO_900'          rc=2 ARG_ERROR len=64 launched=false
ledger bytes: before=0 after=0
```

未知オプションと通常の余分引数:

```text
--receipt x:
  rc=2
  UNMEASURABLE ARG_ERROR: 未知の引数: --receipt x

extra:
  rc=2
  UNMEASURABLE ARG_ERROR: 未知の引数: extra
```

ただし、オプション値と同じ文字列を余分な位置引数として追加すると拒否されませんでした。

```powershell
python bomdd-run.py ECO-900 `
  --ledger <temp>\dup.jsonl `
  --cell "<cell-command>" `
  "<cell-command>"
```

観測:

```text
rc=0
ADVANCE ECO-900 OK → next · launching @c797b2d070bb
CELL-OUTPUT
cell exit 0
launched=true
ledger_exists=true
```

原因は引数値を値集合として消費済みにしており、同値の余分引数も消費済みと判定するためです。したがって「余分な位置引数は ARG_ERROR」は全域では成立しません。

confinement の追加測定:

```text
拡張長パス:
  _under(\\?\C:\...\p\x, C:\...\p) = false
```

拡張長パスによる迂回は再現しませんでした。

実シンボリックリンクは両試行とも次で作成できませんでした。

```text
OSError(22): クライアントは要求された特権を保有していません。
```

よって、シンボリックリンクによる迂回は測れませんでした。

## 2. IA-02 — 是正確認

台帳をディレクトリにした腕:

```text
rc=2
UNMEASURABLE ARG_ERROR: 台帳を書けない(PermissionError): …\ledger-as-directory
len=78
launched=false
ledger events=[]
```

Windows の排他ハンドルで台帳ファイルをロックした権限相当腕:

```text
rc=2
UNMEASURABLE ARG_ERROR: 台帳を書けない(PermissionError): …\locked.jsonl
len=78
launched=false
```

正常起動時、cell 自身に起動直後の台帳先頭行を読ませました。

```text
rc=0
lines:
  ADVANCE ECO-900 OK → next · launching @bf52ec89b9b3
  cell exit 0
cell_saw="decision"
ledger events=["decision","cell"]
cell_exit=0
```

判定レコードは起動前に存在し、起動後に `event=cell` が追記されています。

## 3. IA-03 — 是正確認

cell が stdout に出力する正常腕:

```text
rc=0
1: ADVANCE ECO-900 OK → next · launching @c797b2d070bb
2: CELL-OUTPUT
3: cell exit 0
```

順序は「判定行 → cell 出力 → cell exit N」でした。

独立させた起動条件も確認しました。

```text
verifier exit 0 + "STOP GATE_FAIL:":
  rc=1
  STOP ECO-900 GATE_FAIL → factory ...
  launched=false

verifier exit 1 + "ADVANCE OK:":
  rc=1
  STOP ECO-900 OK → next ...
  launched=false
```

3 条件成立時のみ起動し、1 行目は decision で始まりました。

## 4. IA-04 — 未是正

tool 自身の主要出力は80桁以内でした。

```text
--selftest report: 74
ECO syntax errors: 59–72
unknown option: 42
extra argument: 36
ledger directory/locked: 78
worktree ledger rejection: 72
no arguments usage: 80
```

コマンド:

```powershell
python method/tools/bomdd-run.py --selftest
python method/tools/bomdd-run.py
python method/tools/bomdd-run.py ECO-900 --ledger <worktree-long-path>
```

しかし、cell が160文字の1行を出した場合、同じ標準出力に無加工で現れました。

```text
line lengths=[51,160,11]

ADVANCE ECO-900 OK → next · launching @b51245f19a3f
XXXXXXXXXXXXXXXX...(160文字)
cell exit 0
```

したがって「全経路の出力行が80桁以内」は成立しません。selftest もこの inherited cell stdout を検査していません。

## 5. 回帰

常設検査:

```powershell
python method/tools/bomdd-run.py --selftest
```

```text
ADVANCE OK: selftest PASS(起動1/dry/kb5/job停止/測定不能2/構文5/台帳3/引数7/80桁/表)
SELFTEST_EXIT=0
```

ただし上記 IA-01・IA-04 を検出しないため、この緑単独は受入根拠として不十分です。

指定9腕の直接観測:

```text
TREE_MISMATCH       rc=1 → operator       launched=false
IDENTITY_MISMATCH   rc=1 → operator       launched=false
GATE_FAIL           rc=1 → factory        launched=false
GATES_MISSING       rc=1 → operator       launched=false
STOP_TYPE           rc=1 → human          launched=false
job LEDGER_INCONSISTENT
                    rc=1 → ledger-owner   launched=false
witness absent      rc=2 → operator       launched=false
register absent     rc=2 → operator       launched=false
git absent          rc=2 → operator       launched=false
```

正常腕:

```text
rc=0
events=["decision","cell"]
decision=ADVANCE
delivery=next
cell_exit=0
```

環境変数・一時 JSON・cell 文字列:

```text
BOMDD_JOB=ECO-900
BOMDD_WITNESS=<temp-root>\.git\bomdd-witness\ECO-900.json
BOMDD_JOB_JSON existed during cell=true
BOMDD_JOB_JSON exists after cell=false
cell_exact=true
```

配送表被覆:

```text
DELIVERY △ job.STOP_VOCABULARY = []
WITNESS_DELIVERY △ witness.CODES = []
```

非接触 diff:

```powershell
git diff 3c14c83 --stat -- `
  method/tools/bomdd-job.py `
  method/tools/bomdd-witness.py `
  method/tools/self-conformance.py `
  bomdd/hooks
```

観測出力: なし。差分 0。

作業リポジトリ非汚染:

```powershell
git status --short
git diff --name-only
```

観測出力: いずれもなし。

## 較正 receipt

主張「ECO-067 r1 IA-01〜04 が是正され、指定回帰がない」の測定成立性は `observed`、証拠資格は `不適格` です。帰属は製造物側で、残存する IA-01・IA-04 が理由です。

Q1〜Q7・Q9〜Q11=`asked`、Q8=`NA`。known-good/known-bad を実入力として対置し、現在 commit を識別しました。検出力の限界は、実シンボリックリンク経路を権限不足により測れなかったことです。

範囲外の観察: なし。