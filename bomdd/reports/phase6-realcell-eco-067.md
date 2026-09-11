# Phase 6 実 cell 実測 — bomdd-run が Codex(read-only)を自動起動(2026-09-11・題材 ECO-067・user DECIDE「A」)

> 位置づけ: [ECO-062 order](../60-change-order-eco-062.md) §10.7 の記録(非正本)。入口= `method/tools/bomdd-run.py`(ECO-067 verified・commit 7480156)。
> 目的= Phase 6 出口の unknown(実製造セルの自動起動)を N=1 で埋める。cell の仕事の可否は入口の責務外(観測として記録)。

## 1. 実行

```text
python method/tools/bomdd-run.py ECO-067 --cell "codex exec -s read-only -m gpt-5.6-sol -C <repo> -o <report> - < <brief>"
```

入口の標準出力(全文):

```text
ADVANCE ECO-067 OK → next · launching @27c273fdb777
cell exit 0
```

run exit= 0。作業木= 前後とも `git status --porcelain` 空。

## 2. run 台帳(`.git/bomdd-run/ECO-067.jsonl` 末尾 2 行・原文)

```json
{"event": "decision", "run_id": "20260911T105234.465147Z", "eco": "ECO-067", "receipt": "C:\\Users\\akira\\source\\repos\\BomDD\\.git\\bomdd-witness\\ECO-067.json", "job_state": "verified", "job_stop_type": "NONE", "verifier_line": "ADVANCE OK: tree 一致(27c273fdb777)・gates 1 件 exit 0・stop NONE・個体 ECO-067 一致", "verifier_exit": 0, "code": "OK", "decision": "ADVANCE", "stop_type": "NONE", "delivery": "next", "cell": "codex exec -s read-only -m gpt-5.6-sol -C C:/Users/akira/source/repos/BomDD -o C:/Users/akira/AppData/Local/Temp/claude/C--Users-akira-source-repos-BomDD/73474582-17bf-4594-b067-b9ddb6355833/scratchpad/cell-eco-067-regression-report.md - < C:/Users/akira/AppData/Local/Temp/claude/C--Users-akira-source-repos-BomDD/73474582-17bf-4594-b067-b9ddb6355833/scratchpad/cell-brief-eco-067-regression.md > C:/Users/akira/AppData/Local/Temp/claude/C--Users-akira-source-repos-BomDD/73474582-17bf-4594-b067-b9ddb6355833/scratchpad/codex-cell-eco067.log 2>&1", "tree": "27c273fdb77729a2635e8b3aef36e8a72719c162"}
{"event": "cell", "run_id": "20260911T105234.465147Z", "eco": "ECO-067", "cell": "codex exec -s read-only -m gpt-5.6-sol -C C:/Users/akira/source/repos/BomDD -o C:/Users/akira/AppData/Local/Temp/claude/C--Users-akira-source-repos-BomDD/73474582-17bf-4594-b067-b9ddb6355833/scratchpad/cell-eco-067-regression-report.md - < C:/Users/akira/AppData/Local/Temp/claude/C--Users-akira-source-repos-BomDD/73474582-17bf-4594-b067-b9ddb6355833/scratchpad/cell-brief-eco-067-regression.md > C:/Users/akira/AppData/Local/Temp/claude/C--Users-akira-source-repos-BomDD/73474582-17bf-4594-b067-b9ddb6355833/scratchpad/codex-cell-eco067.log 2>&1", "started_at": "2026-09-11T10:52:34+00:00", "cell_exit": 0}
```

## 3. cell へ渡したブリーフ(原文)

# 製造セル向けブリーフ — ECO-067 回帰検査(入口 bomdd-run から自動起動された cell・read-only)

あなたはこの起動元(`bomdd-run.py`)から自動起動された製造セルです。環境変数 `BOMDD_JOB`(ECO)・`BOMDD_JOB_JSON`(job ビューの JSON)・`BOMDD_WITNESS`(receipt のパス)が渡っています。
作業ルート= 現在のディレクトリ。リポジトリ内のファイルを**作成・変更・削除しない**(read-only)。一時ファイルは OS temp へ。

## やること(範囲限定・回帰のみ)

1. 環境変数 3 つの値を報告する(`BOMDD_JOB_JSON` は中身の `eco.value` と `state.value` を読んで報告)。
2. `python method/tools/bomdd-run.py --selftest` を実行し、終了コードと 1 行目を報告する。
3. `python method/tools/bomdd-witness.py verify "$env:BOMDD_WITNESS" --eco $env:BOMDD_JOB`(PowerShell 表記)を実行し、1 行目を報告する。
4. `git status --porcelain` が空であることを確認する(あなたがリポジトリを変えていないこと)。

## 報告の形式(最終メッセージ)

- 冒頭に `ACCEPT`(2 の exit 0 かつ 3 の 1 行目が `ADVANCE OK:` で始まる)または `REJECT`(それ以外・理由)。
- 各項目の実行コマンドと観測出力。測れなかったことは「測れなかった」と書く。用語は中立に。

## 4. cell の最終報告(Codex・原文どおり転記)

REJECT — selftest が exit 1、witness 検証の先頭行が `ADVANCE OK:` ではないため。

1. 環境変数

```powershell
$env:BOMDD_JOB
$env:BOMDD_JOB_JSON
$env:BOMDD_WITNESS
```

```text
BOMDD_JOB=ECO-067
BOMDD_JOB_JSON=C:\Users\akira\AppData\Local\Temp\bomdd-job-1vkfhmai.json
BOMDD_WITNESS=C:\Users\akira\source\repos\BomDD\.git\bomdd-witness\ECO-067.json
eco.value=ECO-067
state.value=verified
```

2. selftest

```powershell
python method/tools/bomdd-run.py --selftest
```

```text
exit code: 1
1行目: Traceback (most recent call last):
```

一時ディレクトリが利用できず、selftest の合否は測れなかった。

3. witness 検証

```powershell
python method/tools/bomdd-witness.py verify "$env:BOMDD_WITNESS" --eco $env:BOMDD_JOB
```

```text
1行目: UNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE): 現 tree を取得できない(FileNotFoundError: [Errno 2] No usable temporary directory found in [...])— 測定不能は合格ではない
```

4. 作業ツリー

```powershell
git status --porcelain
```

```text
（出力なし）
```

作業ツリーは空で、リポジトリ変更は観測されなかった。

## 5. 採点側の観測

- 入口: 判定行が先・cell 起動・`cell exit 0`・台帳 decision/cell・環境変数 3 つが cell 内で読めた(eco/state を JSON から読了)。**入口の経路は実 cell で成立(N=1)**。
- cell: read-only sandbox に OS temp がなく、witness verify は `UNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE)`(ECO-066 の原因分離が実環境で効いた初例)、
  `bomdd-run.py --selftest` は Traceback exit 1(P6-01: selftest 自身の測定不能が 1 行にならない)。cell の報告は REJECT だが入口は cell exit 0 のみ記録(P6-02: 責務境界・Phase 7 の入力)。
- 承認プロンプト: 非対話 `codex exec` では発生しない(未測定のまま)。
