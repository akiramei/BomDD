# 独立検査報告 — ECO-067 r3(Codex gpt-5.6-sol・CLI 直接・workspace-write・2026-09-11・対象 commit f4a2b5d・範囲= IA-01 残の是正確認+回帰)

> 検査官の最終メッセージをそのまま転記(受理側の判定は order §7.3)。

# ACCEPT

対象個体: commit `f4a2b5dff1f2ff1e34de5167807d8182175e659a`  
`bomdd-run.py` SHA-256: `F6D6CB9115292685467489534D5AD4FA8A85C3E37BC72A83086C80993C8084BA`

IA-01 の残所見は是正されています。指定された回帰および IA-02・IA-03 の是正維持も確認しました。新規所見はありません。

## 1. IA-01 残りの是正確認

OS temp に git repository、register、receipt、cell 起動痕跡、外部台帳を生成し、実 CLI を `subprocess.run` で実行しました。

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'
$env:GIT_OPTIONAL_LOCKS='0'
@'
# OS temp fixture を生成し、以下の各 CLI を実行
'@ | python -
```

### `--cell C C`

```powershell
python method/tools/bomdd-run.py ECO-900 --ledger L --cell C C
```

観測:

```text
rc=2
UNMEASURABLE ARG_ERROR: 未知の引数: C:\Pytho…encoding='utf-8'); print('CELL-OUTPUT')"
launched=false
ledger_exists=false
```

### `--ledger L L`

```powershell
python method/tools/bomdd-run.py ECO-900 --ledger L L
```

観測:

```text
rc=2
UNMEASURABLE ARG_ERROR: 未知の引数: C:\Users…\out\ia1b.jsonl
launched=false
ledger_exists=false
```

### `--ledger L --ledger L`

```powershell
python method/tools/bomdd-run.py ECO-900 --ledger L --ledger L
```

観測:

```text
rc=2
UNMEASURABLE ARG_ERROR: --ledger が重複
launched=false
ledger_exists=false
```

### 正常腕

```powershell
python method/tools/bomdd-run.py ECO-900 --ledger L --cell C
```

観測:

```text
rc=0
ADVANCE ECO-900 OK → next · launching @0e3a1a0d17af
CELL-OUTPUT
cell exit 0
launched=true
ledger events=["decision","cell"]
decision=ADVANCE
delivery=next
```

したがって、不正3腕は起動せず台帳にも書かず、正常腕は従来どおり起動しました。

## 2. 指定9腕の回帰

同じ OS temp fixture で、receipt/register/git を腕ごとに変更して CLI を実行しました。

```text
TREE_MISMATCH:
  rc=1
  STOP ECO-900 TREE_MISMATCH → operator @0e3a1a0d17af
  launched=false

IDENTITY_MISMATCH:
  rc=1
  STOP ECO-900 IDENTITY_MISMATCH → operator @0e3a1a0d17af
  launched=false

GATE_FAIL:
  rc=1
  STOP ECO-900 GATE_FAIL → factory @0e3a1a0d17af
  launched=false

GATES_MISSING:
  rc=1
  STOP ECO-900 GATES_MISSING → operator @0e3a1a0d17af
  launched=false

STOP_TYPE:
  rc=1
  STOP ECO-900 STOP_TYPE(NORMATIVE_RULING) → human @0e3a1a0d17af
  launched=false

job LEDGER_INCONSISTENT:
  rc=1
  STOP ECO-902 job:LEDGER_INCONSISTENT → ledger-owner @0e3a1a0d17af
  launched=false

witness absent:
  rc=2
  UNMEASURABLE ECO-900 WITNESS_UNREADABLE → operator @0e3a1a0d17af
  launched=false

register absent:
  rc=2
  UNMEASURABLE ECO-900 job:MISSING_INPUT → operator @-
  launched=false

git absent:
  rc=2
  UNMEASURABLE ECO-900 job:MISSING_INPUT → operator @-
  launched=false
```

9腕すべてで起動痕跡はありませんでした。

## 3. 正常腕・環境変数・一時 JSON

正常腕の cell 内から環境と起動時台帳を読みました。

```text
BOMDD_JOB=ECO-900
BOMDD_WITNESS=<temp>\repo\.git\bomdd-witness\ECO-900.json
BOMDD_JOB_JSON=<OS temp>\bomdd-job-k02st149.json
BOMDD_JOB_JSON existed during cell=true
BOMDD_JOB_JSON exists after cell=false
cell_saw="decision"
cell_exact=true
```

判定レコードは cell 起動前に存在し、cell 文字列は台帳に同一文字列で保存され、一時 JSON は終了後に削除されました。

## 4. IA-02 の是正維持

### 台帳がディレクトリ

```powershell
python method/tools/bomdd-run.py ECO-900 --ledger <temp>\ledger-as-directory --cell C
```

```text
rc=2
UNMEASURABLE ARG_ERROR: 台帳を書けない(PermissionError): …\ledger-as-directory
launched=false
ledger events=[]
```

### 台帳を排他ロック

Windows `CreateFileW(..., shareMode=0, ...)` で台帳を排他保持して実行しました。

```text
rc=2
UNMEASURABLE ARG_ERROR: 台帳を書けない(PermissionError): …\locked.jsonl
launched=false
ledger_bytes=0
```

台帳書込み不能時に cell は起動しませんでした。

## 5. IA-03 の是正維持

正常腕の標準出力順:

```text
1: ADVANCE ECO-900 OK → next · launching @0e3a1a0d17af
2: CELL-OUTPUT
3: cell exit 0
```

verifier の行と終了コードを独立に故障注入したコマンド:

```python
run(["ECO-900", "--ledger", L, "--cell", C], root, emitted.append)
```

観測:

```text
verifier exit 0 + "STOP GATE_FAIL:":
  rc=1
  STOP ECO-900 GATE_FAIL → factory @aaaaaaaaaaaa
  launched=false

verifier exit 1 + "ADVANCE OK:":
  rc=1
  STOP ECO-900 OK → next @aaaaaaaaaaaa
  launched=false
```

判定行は cell 出力より前で、AND 条件の一部だけが成立する腕では起動しませんでした。

## 6. 配送表被覆

実装モジュールと依存モジュールを読み込み、集合の対称差を計算しました。

```python
set(DELIVERY) ^ set(job.STOP_VOCABULARY)
set(WITNESS_DELIVERY) ^ set(witness.CODES)
```

```text
DELIVERY △ job.STOP_VOCABULARY = []
WITNESS_DELIVERY △ witness.CODES = []
```

## 7. `--selftest`

```powershell
python method/tools/bomdd-run.py --selftest
```

終了コード:

```text
0
```

出力:

```text
ADVANCE OK: selftest PASS(起動1/dry/kb5/job停止/測定不能2/構文5/台帳3/引数10/80桁/表)
```

## 8. 非接触・作業リポジトリ非汚染

```powershell
git diff 3c14c83 --stat -- method/tools/bomdd-job.py method/tools/bomdd-witness.py method/tools/self-conformance.py bomdd/hooks
```

観測出力なし、exit 0。差分は 0 です。

検査前後に実行:

```powershell
git status --short
git diff --name-only
```

いずれも観測出力なし、exit 0。リポジトリ内のファイルおよび `.git/bomdd-run/`・`.git/bomdd-witness/` に変更はありません。

## 較正 receipt

主張「IA-01 残りが是正され、指定された r2 回帰および IA-02・IA-03 の是正が維持されている」の測定成立性は `observed`、証拠資格は `適格` です。known-good と各 known-bad を実入力として対置し、対象 commit とファイル hash を識別しました。

Q1〜Q7・Q9〜Q11=`asked`、Q8=`NA`。測れなかった指定項目はありません。

検出力の限界: 指定どおり IA-04 の残りおよび新しい境界探索は測定対象に含めていません。

範囲外の観察: なし。