[INFORM / COMPLETE]
REJECT IA-06、IA-07 — 同名ディレクトリ腕の回帰と、IA-01 の旧仕様コメント残存を確認。

対象個体: `d60471efd7aa7557e55feda710ef1c157ef3d750`  
range: ECO-073 r2（是正確認＋指定回帰のみ）  
環境: Windows 11 / Python 3.13.1 / sandbox=workspace-write / fixture・ledger=OS temp  
リポジトリ内の作成・変更・削除: なし。終了時 `git status --short --branch` は `## main...origin/main`、`$LASTEXITCODE=0`。

## /preflight receipt

- classification: corrective-verification。r1 所見への是正確認と限定回帰。
- baseline/current specimen: `HEAD=d60471e`、worktree clean — confirmed。
- current-work-state: register の ECO-073 は `implemented` — confirmed。
- unresolved-items: IA-02・IA-05 是正、IA-01 明確化、指定回帰 — confirmed。
- handoff-state: ECO-073 §5.1 と r1 報告から再構成 — confirmed。
- acceptance-target: 本ブリーフ 1〜5 — confirmed。
- 開始判定: PROCEED。override: なし。

## 所見

### IA-06 — 既存ディレクトリが MISSING から ARG_ERROR へ退行

再現コマンド:

```powershell
New-Item -ItemType Directory <fixture>\reports\dirtarget
python <repo>\method\tools\bomdd-run.py ECO-900 `
  --ledger <OS-temp>\ledger.jsonl `
  --cell <marker-cell> --executor EQ-002 `
  --report reports/dirtarget
$LASTEXITCODE
```

観測:

```text
UNMEASURABLE ARG_ERROR: --report の宛先が既に存在する: reports/dirtarget
$LASTEXITCODE=2
cell 起動=False / 台帳差分=0
```

期待との差: r1 の結線・例外境界では、同名ディレクトリは cell 起動後に `report MISSING (no file)`、入口 exit 0、台帳 `exists:false` だった。現物の `run()` は `(root / report).exists()` でファイルとディレクトリを区別せず、IA-02 の stale-file 防止をディレクトリにも適用している。

帰属: 製造物。指定済み回帰腕であり、新規境界探索ではない。

### IA-07 — IA-01 と矛盾する旧 exit コメントが残存

再現コマンド:

```powershell
rg -n "exit は cell に従う|入口の exit は R8" method/tools/bomdd-run.py
$LASTEXITCODE
```

観測:

```text
37: ...入口の exit は R8 のまま= 起動したら 0...
433: ...判定語の回収を 1 行で(exit は cell に従う・判定で行動しない)
$LASTEXITCODE=0
```

期待との差: R10 冒頭コメントは ECO-067 R8 に修正されたが、`run()` 内の R10 コメントは旧文言のまま。実挙動は入口 exit 0 で正しいものの、同一製造物内の仕様説明が相互矛盾する。

帰属: 製造物の仕様コメント。

## 1. IA-02 是正確認

### 起動前から通常ファイルが存在

```powershell
Set-Content <fixture>\reports\stale.md ACCEPT
python <repo>\method\tools\bomdd-run.py ECO-900 `
  --ledger <OS-temp>\ledger.jsonl --cell <marker-cell> `
  --executor EQ-002 --report reports/stale.md
$LASTEXITCODE
```

```text
UNMEASURABLE ARG_ERROR: --report の宛先が既に存在する: reports/stale.md
$LASTEXITCODE=2
cell 起動=False / 台帳差分=0
```

期待との差: なし。IA-02 の stale-file 是正は成立。

### 宛先が存在しない

```powershell
python <repo>\method\tools\bomdd-run.py ECO-900 `
  --ledger <OS-temp>\ledger.jsonl --cell <ACCEPT-write-cell> `
  --executor EQ-002 --report reports/fresh.md
$LASTEXITCODE
```

```text
ADVANCE ECO-900 OK → next · launching @965a073db9db
cell exit 0
report ACCEPT sha256:87139f0a6627 (EQ-002)
$LASTEXITCODE=0
```

台帳 report:

```json
{"path":"reports/fresh.md","exists":true,"size":28,"sha256":"87139f0a66273c0a06b20e7cac45aa0d63a3d2afa278c9d5b9fe644ce2410585","verdict":"ACCEPT","verdict_line":"ACCEPT"}
```

期待との差: なし。

### 遅延書込み

```powershell
python <repo>\method\tools\bomdd-run.py ECO-900 `
  --ledger <OS-temp>\delay-ledger.jsonl --cell <delayed-child-cell> `
  --executor EQ-002 --report reports/delay.md
$LASTEXITCODE
```

```text
ADVANCE ECO-900 OK → next · launching @965a073db9db
cell exit 0
report MISSING (no file) (EQ-002)
$LASTEXITCODE=0
```

入口読取り直後 `exists=False`、2 秒後 `exists=True`。期待との差なし。遅延書込みは cell 側責務のまま。

## 2. IA-05 是正確認

```powershell
python <repo>\method\tools\bomdd-run.py ECO-900 `
  --ledger <OS-temp>\ledger.jsonl --cell <write-leading-space-cell> `
  --executor EQ-002 --report reports/space.md
$LASTEXITCODE
```

```text
ADVANCE ECO-900 OK → next · launching @965a073db9db
cell exit 0
report UNPARSED sha256:d4d57f7bfcfe (EQ-002)
$LASTEXITCODE=0
```

台帳:

```json
{"verdict":"UNPARSED","verdict_line":"  ACCEPT"}
```

`ACCEPT` 直書きは `ACCEPT`、`verdict_line:"ACCEPT"`。期待との差なし。

## 3. IA-01 明確化

```powershell
python <repo>\method\tools\bomdd-run.py ECO-900 `
  --ledger <OS-temp>\ledger.jsonl --cell <write-REJECT-and-exit-7-cell> `
  --executor EQ-002 --report reports/exit7.md
$LASTEXITCODE
```

```text
ADVANCE ECO-900 OK → next · launching @965a073db9db
cell exit 7
report REJECT sha256:199aa1ac7fa3 (EQ-002)
$LASTEXITCODE=0
```

台帳 cell 行 event は `cell_exit:7`、report verdict=`REJECT`、sha256 完全値を保持。実挙動と3行順に期待との差なし。コメントについては IA-07。

## 4. 限定回帰

### 判定語の境界

再現:

```powershell
python -c "<現物をimportし、r1の入力をreport_verdictへ投入>"
$LASTEXITCODE
```

`$LASTEXITCODE=0`。

| 入力 | verdict / verdict_line | r1との差 |
|---|---|---|
| ヘッダ2行 | `UNPARSED` / `[H2]` | なし |
| ヘッダ前の空行 | `ACCEPT` / `ACCEPT` | なし |
| BOM | `UNPARSED` / `﻿ACCEPT` | なし |
| `  ACCEPT` | `UNPARSED` / `  ACCEPT` | IA-05 是正済み |
| `ACCEPT:` | `ACCEPT` | なし |
| `ACCEPT—reason` | `ACCEPT` | なし |
| `ACCEPTED` | `UNPARSED` | なし |
| `Accept` | `UNPARSED` | なし |
| 要約先行 | `UNPARSED` / `summary` | なし |
| fence | `UNPARSED` / `` ``` `` | なし |
| `# ACCEPT` | `UNPARSED` | なし |
| `> ACCEPT` | `UNPARSED` | なし |
| 空 | `UNPARSED` / null | なし |

### 結線・例外境界

- BOM+CRLF: `size=11`、sha256=`402dc5d826ef…`、`UNPARSED`。実ファイルと一致。
- 空ファイル: `exists=true`、`size=0`、sha256=`e3b0c44298fc…`、`UNPARSED`。
- 報告なし: `exists=false`、size/hash=null、`MISSING`。
- `PermissionError` 注入: `MISSING`、traceback なし、`$LASTEXITCODE=0`。
- REJECT / MISSING / UNPARSED: 入口はいずれも exit 0。
- 同名ディレクトリ: IA-06 の退行。

### パス検証

| 入力 | 観測 |
|---|---|
| `./reports/dot.md` | 受理・起動・exit 0 |
| `reports\back.md` | 受理・起動・exit 0 |
| `.gitx/x.md` | 受理・起動・exit 0 |
| 約200文字 | 受理・起動・exit 0 |
| 末尾 `/` | ARG_ERROR・exit 2・起動なし・台帳不変 |
| `.git` | ARG_ERROR・exit 2・起動なし・台帳不変 |
| 絶対パス | ARG_ERROR・exit 2・起動なし・台帳不変 |
| `..` | ARG_ERROR・exit 2・起動なし・台帳不変 |
| 前空白 | ARG_ERROR・exit 2・起動なし・台帳不変 |
| `//` 空要素 | ARG_ERROR・exit 2・起動なし・台帳不変 |
| 別 cwd | `job:MISSING_INPUT`・exit 2・起動なし・台帳1行 |

同名ディレクトリ以外は r1 との差なし。

### 出力互換・80桁・順序

`--report` なし:

```text
ADVANCE ECO-900 OK → next · launching @965a073db9db
cell exit 0
$LASTEXITCODE=0
```

出力は従来どおり2行。`--report` ありは decision → cell exit → report の3行。測定した全行は80桁以内（最大79）。

### selftest

```text
bomdd-run.py --selftest
ADVANCE OK: selftest PASS(...報告22...)
$LASTEXITCODE=0
```

```text
bomdd-job.py --selftest
bomdd-job selftest PASS(...)
$LASTEXITCODE=0
```

```text
bomdd-witness.py --selftest
ADVANCE OK: selftest PASS(...)
$LASTEXITCODE=0
```

`bomdd-run.py --selftest` は既存通常ファイルを検査するが、既存ディレクトリの回帰を捕捉していない。

## 5. 既存 order の非影響

```powershell
python method/tools/bomdd-job.py ECO-073 --json
$LASTEXITCODE
```

観測:

```text
required_capability={"producer":"EQ-001","inspector":"EQ-002"}
stop_type=NONE
$LASTEXITCODE=0
```

期待との差なし。

## /calibrate receipt

査定主張: r2 証拠が IA-02・IA-05・IA-01 の是正と、指定回帰の全成立を証明するか。

- 測定成立性: observed。
- 証拠資格: REJECT 根拠として適格。IA-02・IA-05・IA-01 の実挙動は成立したが、指定回帰に IA-06、仕様記述に IA-07 があるため ACCEPT 根拠にはならない。
- 計器欠陥: `bomdd-run.py --selftest` が既存ディレクトリ退行を捕捉しない。製造物内 selftest に帰属。
- battery: Q1 asked / Q2 asked / Q3 asked / Q4 asked / Q5 asked / Q6 asked / Q7 asked / Q8 asked / Q9 asked / Q10 asked / Q11 asked。
- Q5/Q6: fixture 初回の TREE_MISMATCH と後処理停止は合格に数えず、clean fixture で再実行。各対象コマンド直後に `$LASTEXITCODE` を採取。
- 検出力の限界: 実 OS ACL の不可読通常ファイル、POSIX でのバックスラッシュ、極端な Windows 長パス、実 Codex `-o` の内部書込み時系列は測れなかった。

## 範囲外の観察

- `python method/tools/self-conformance.py` は C14 `kit-freshness` の `REAL` 腕だけ FAIL（6/7）し、最終 `self-conformance FAILED`、`$LASTEXITCODE=1`。本判定には含めない。
- temp fixture の git 操作で global ignore 参照の `Permission denied` 警告を1回観測したが、fixture commit と後続測定は成立した。

human_action: none。ECO-073 r2 の指定範囲は検査完了。