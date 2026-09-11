# 独立検査報告 — ECO-067 r1(Codex gpt-5.6-sol・CLI 直接・workspace-write・2026-09-11・対象 commit ff7cd9f)

> 検査官の最終メッセージをそのまま転記(受理側の真正判定は order §7)。

# REJECT — IA-01、IA-02、IA-03、IA-04

指定された known-bad receipt、job 停止、witness/register/git 不在については fail-open を再現しませんでした。しかし、ECO 値によるパス境界逸脱と、台帳書込不能時の起動が確認されました。後者は R8 の「exit 2＝測定不能・起動せず」に直接反します。

## IA-01 — ECO 値のパストラバーサルで receipt・既定台帳が所定ディレクトリ外へ出る

`ECO-NNN` の構文検証がありません。`default_path(git_dir, eco)` と既定台帳パスへ ECO をそのまま連結しているため、register にパス区切りを含む ID があると、任意位置の receipt を検証し、同じく任意位置へ台帳を書いたうえで cell を起動します。

再現手順:

```powershell
# OS temp の git repo に次の ID を登録
$eco = 'ECO-/../../../../<sibling-temp>/chosen'

# 同じ ECO を持つ witness を default_path() が解決する位置へ produce
# 外部 --ledger を指定せず実行
python C:\Users\akira\source\repos\BomDD\method\tools\bomdd-run.py `
  $eco --cell "<marker を書くコマンド>"
```

観測出力:

```text
run_exit: 0
ADVANCE ECO-/../../../../tmpde4zhli9/chosen OK → next · launched(exit 0) @3a02d659ac87
launched: true
default_ledger_raw:
  ...\.git\bomdd-run\ECO-\..\..\..\..\tmpde4zhli9\chosen.jsonl
default_ledger_resolved:
  C:\Users\akira\AppData\Local\Temp\tmpde4zhli9\chosen.jsonl
under_bomdd_run: false
ledger_exists: true
```

receipt も同様に逸脱しました:

```text
derived_raw:
  ...\.git\bomdd-witness\ECO-\..\..\..\..\tmprwnt8w5q\chosen.json
derived_resolved:
  C:\Users\akira\AppData\Local\Temp\tmprwnt8w5q\chosen.json
under_expected_dir: false
run_exit: 0
launched: true
```

影響: **fail-open**。不正な ECO 引数を `ARG_ERROR` / `UNMEASURABLE` にせず、R2 の receipt confinement と R4 の `.git/bomdd-run/<ECO>.jsonl` confinement をともに迂回して起動します。

補足として、明示的な `--receipt <alternate>` は receipt 選択には使用されず、既定 receipt が検証されました。ただし未知オプション自体は拒否されず、無視されて exit 0 になりました。

---

## IA-02 — 台帳書込不能でも cell を先に起動し、その後 exit 2 になる

`run()` は `launch()` を実行してから `write_ledger()` を呼びます。したがって台帳を開けない場合、起動事実が台帳へ残らず、結果だけが「測定不能」になります。

再現手順:

```powershell
New-Item -ItemType Directory $outside\ledger-as-directory

python C:\Users\akira\source\repos\BomDD\method\tools\bomdd-run.py `
  ECO-900 `
  --cell "<CELL-OUTPUT を出し marker を書くコマンド>" `
  --ledger $outside\ledger-as-directory
```

観測出力:

```text
CELL-OUTPUT
UNMEASURABLE ARG_ERROR: 台帳を書けない: ...\ledger-as-directory(PermissionError)
exit: 2
marker: true
ledger_is_dir: true
```

影響: **fail-open**。R8 の「2＝測定不能（起動せず）」と、R4 の「起動した事実を台帳に残す」を同時に破ります。

---

## IA-03 — 正常起動時、1 行目が decision ではなく cell の出力になる

cell の stdout/stderr を捕捉・分離せず継承しているため、runner の summary は cell 終了後に出ます。

再現手順:

```powershell
python C:\Users\akira\source\repos\BomDD\method\tools\bomdd-run.py `
  ECO-900 --cell "<CELL-OUTPUT を出すコマンド>"
```

観測出力:

```text
CELL-OUTPUT
ADVANCE ECO-900 OK → next · launched(exit 0) @ef0b1bb9e830
exit: 0
```

影響: **判定の誤り**。R7 の「標準出力は短い1行」「1行目が decision で始まる」を破り、1行目を機械判定する呼出側は cell が出した任意文字列を runner の判定と誤認できます。

なお、cell 文字列は台帳上で入力と完全一致し、`cell_exit=0` でした。

---

## IA-04 — 80桁制約を selftest 自身と引数エラー経路が覆っていない

再現手順:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$out = python method/tools/bomdd-run.py --selftest
$out.Length
```

観測出力:

```text
ADVANCE OK: selftest PASS(known-good 起動 1 / dry 0 / known-bad ... / 配送先表と語彙の 1 対 1)
EXIT=0
LEN=164
```

引数なし経路:

```powershell
$out = python method/tools/bomdd-run.py
$LASTEXITCODE
$out.Length
```

```text
UNMEASURABLE ARG_ERROR: usage: bomdd-run.py ECO-NNN [--cell CMD] [--ledger PATH] | --selftest
EXIT=2
LEN=93
```

作業木内台帳の拒否行も絶対パスを含むため80桁を超えました。

影響: **文言のみ**。V6/R7 の「全経路で80桁以内」は成立しません。selftest は各 `arm()` の summary 長だけを調べ、selftest の最終報告、引数エラー、台帳エラー、cell 出力を検査していません。

## 所見外の確認結果

- 指定された fail-open 腕:

  - tree 不一致: exit 1、`TREE_MISMATCH`、不起動
  - 別 ECO witness: exit 1、`IDENTITY_MISMATCH`、不起動
  - FAIL 混入: exit 1、`GATE_FAIL`、不起動
  - gates 欠測: exit 1、`GATES_MISSING`、不起動
  - receipt `stop_type=NORMATIVE_RULING`: exit 1、human 配送、不起動
  - job `LEDGER_INCONSISTENT`: exit 1、ledger-owner 配送、不起動
  - witness 不在: exit 2、不起動
  - register 不在: exit 2、不起動
  - git 不可: exit 2、不起動

- 正常腕では `verifier_exit=0`、`ADVANCE OK:`、job stop type `NONE` のときだけ起動しました。
- `BOMDD_JOB`、`BOMDD_JOB_JSON`、`BOMDD_WITNESS` は cell 内で取得できました。一時 job JSON は cell 実行中に存在し、終了後は削除されていました。
- cell 文字列は加工されず台帳へ記録されました。承認迂回用のフラグ・環境変数は見つかりませんでした。
- `DELIVERY` のキー集合は `bomdd-job.py` の8語と一致しました。
- `WITNESS_DELIVERY` は witness の全15 CODE を過不足なく被覆しました。
- STOP_TYPE は receipt の `stop_type` を使って配送されました。
- 台帳レコードには `verifier_line`、`decision`、`delivery`、`cell`、`cell_exit` があり、人間手書き欄はありませんでした。通常パスの書込みは追記モードです。
- `git diff 3c14c83 --stat -- method/tools/bomdd-job.py method/tools/bomdd-witness.py method/tools/self-conformance.py bomdd/hooks/pre-push` は出力なし、対象4系統の差分は0でした。
- in-process import の観測結果:

```text
import_output: ''
stdout_restored: True
job_has_select: True
witness_has_verify: True
```

- `python method/tools/self-conformance.py`: exit 0、stdout なし。
- selftest は exit 0 でしたが、IA-01〜IA-04を覆っていません。
- CI は測れませんでした。`gh run list --repo akiramei/BomDD --limit 3` は実行基盤のネットワーク制約で接続不能となったため、結論は **UNKNOWN** です。
- 検査前後とも `git status --short` と `git diff --name-only` は出力なし。作業リポの変更はありません。