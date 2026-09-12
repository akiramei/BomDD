[INFORM / COMPLETE]

ACCEPT

対象: ECO-073 r3  
range: r2 所見 IA-06/IA-07 の是正確認および指定回帰のみ  
検体: `HEAD ddae2ee9ea81aad12087077f658a8645a5f53a8e`  
環境: Windows PowerShell、sandbox=`workspace-write`  
作業木: 検査前後とも clean。リポジトリ内の作成・変更・削除なし。

## 1. preflight receipt

- task classification: continuation／是正後の独立再検査。
- baseline・状態: ECO-073 §5.2、register の `implemented`、対象コードを確認。
- acceptance target: IA-06/IA-07 の是正と指定された回帰腕。
- 判定: `PROCEED_WITH_LIMITS`。新規境界探索、register/witness 更新、C14 は除外。
- override: なし。

## 2. IA-06 — 既存ディレクトリ

再現コマンド:

```powershell
python method/tools/bomdd-run.py ECO-073 `
  --ledger <OS-temp>\directory.jsonl `
  --cell <marker作成コマンド> --executor EQ-002 `
  --report bomdd/reports
$LASTEXITCODE
```

観測:

```text
UNMEASURABLE ARG_ERROR: --report の宛先が既に存在する: bomdd/reports
LASTEXITCODE=2
ledger_unchanged=True marker_exists=False
```

期待との差: なし。実リポと OS-temp fixture の双方で同じ結果。

## 3. IA-06 — 既存ファイル

再現コマンド:

```powershell
python method/tools/bomdd-run.py ECO-073 `
  --ledger <OS-temp>\file.jsonl `
  --cell <marker作成コマンド> --executor EQ-002 `
  --report bomdd/60-change-order-eco-073.md
$LASTEXITCODE
```

観測:

```text
UNMEASURABLE ARG_ERROR: --report の宛先が既に存在する: bomdd/60-change-order-eco-073.md
LASTEXITCODE=2
ledger_unchanged=True marker_exists=False
```

期待との差: なし。

## 4. IA-06 — fresh 宛先

再現コマンド:

```powershell
python <current-bomdd-run.py> ECO-073 `
  --ledger <OS-temp>\fresh.jsonl `
  --cell <BOMDD_REPORTへACCEPTを書くcell> --executor EQ-002 `
  --report bomdd/reports/r3-fresh.md
$LASTEXITCODE
```

観測:

```text
ADVANCE ECO-073 OK → next · launching @b0f129a16774
cell exit 0
report ACCEPT sha256:b1b56e128ae5 (EQ-002)
```

```text
LASTEXITCODE=0
ledger: verdict=ACCEPT exists=True size=8
sha256=b1b56e128ae55aeb3a5d9f8a3f76d6d7b3d137a0c8b962d5fe1e262fbca53f72
```

実ファイルの SHA-256 と台帳値は完全一致。期待との差: なし。

## 5. IA-02 — stale/fresh/遅延

- stale: 上記既存ファイル腕で ARG_ERROR、exit 2、起動なし、台帳不変。
- fresh: 上記 fresh 腕で起動・ACCEPT・hash 結線。
- 遅延書込み:

```text
ADVANCE ECO-073 OK → next · launching @b0f129a16774
cell exit 0
report MISSING (no file) (EQ-002)
```

```text
LASTEXITCODE=0 verdict=MISSING exists=False
delayed_exists_immediate=False
delayed_exists_after_3s=True
```

cell 終了時点を測定点として MISSING。期待との差: なし。

## 6. IA-07 — コメント是正

再現コマンド:

```powershell
rg -n "exit は cell に従う" method/tools/bomdd-run.py
$LASTEXITCODE
```

観測:

```text
MATCH_COUNT=0
LASTEXITCODE=1
```

`rg` の exit 1 は一致なしを表す。R8 は「起動したら入口 exit 0」、R10 は「入口の exit は R8 のまま 0・判定で行動しない」と記載され、`run()` は cell 起動後に `return 0`。相互矛盾なし。

期待との差: なし。

## 7. IA-01 — cell 非ゼロ

再現コマンド:

```powershell
python <current-bomdd-run.py> ECO-073 `
  --ledger <OS-temp>\exit7.jsonl `
  --cell <REJECTを書いてexit 7のcell> --executor EQ-002 `
  --report bomdd/reports/r3-exit7.md
$LASTEXITCODE
```

観測:

```text
ADVANCE ECO-073 OK → next · launching @b0f129a16774
cell exit 7
report REJECT sha256:46784afcfa44 (EQ-002)
```

```text
LASTEXITCODE=0 ledger.cell_exit=7 ledger.verdict=REJECT
```

期待との差: なし。

## 8. IA-05・判定語境界表

再現コマンド: 現行 `report_verdict()` に r2 固定入力表を投入。

観測:

```text
BOUNDARY_TABLE: 14/14 expected
leading_space: got=UNPARSED line='  ACCEPT' ok=True
LASTEXITCODE=0
```

成立した境界:

- ACCEPT、REJECT、UNMEASURABLE、ヘッダ0/1行、先行空行、コロン、em dash。
- ヘッダ2行、BOM、`ACCEPTED`、大小文字差、要約先行、fence、見出し、引用、行頭空白は UNPARSED。
- `verdict_line` は行頭空白を含む原文を保持。

期待との差: なし。

## 9. パス検証表

再現コマンド: 現行 `_report_path_error()` に r2 固定入力表を投入。

観測:

```text
PATH_TABLE: 11/11 expected
accepted=./, backslash, .gitx/, 200文字
rejected=絶対, .., .git/, 前後空白, 末尾/, 空要素
LASTEXITCODE=0
```

期待との差: なし。

## 10. 出力互換・80桁

`--report` なし:

```text
ADVANCE ECO-073 OK → next · launching @b0f129a16774
cell exit 0
LASTEXITCODE=0 lines=2 maxlen=51
```

`--report` ありの正常系は3行。測定した最大行長は既存ファイル腕の77文字で、全腕80文字以内。

期待との差: なし。

## 11. selftest

`bomdd-run.py`:

```text
ADVANCE OK: selftest PASS(起動4/dry2/kb5/job停止/不能3/独立性9/報告23/構文5/台帳3/引数13/80桁/表)
LASTEXITCODE=0
```

報告腕は23で、コード上に `dirtarget` ディレクトリ腕を確認。

`bomdd-job.py`:

```text
bomdd-job selftest PASS(...)
LASTEXITCODE=0
```

`bomdd-witness.py`:

```text
ADVANCE OK: selftest PASS(...)
LASTEXITCODE=0
```

期待との差: なし。

## 12. required_capability

再現コマンド:

```powershell
python method/tools/bomdd-job.py ECO-073 --json
$LASTEXITCODE
```

観測:

```json
"required_capability": {
  "value": {"producer": "EQ-001", "inspector": "EQ-002"}
}
```

```text
state=implemented stop_type=NONE
LASTEXITCODE=0
```

r2 からの変更なし。期待との差: なし。

## 13. calibrate receipt

- 主張: ECO-073 r2b は IA-06/IA-07 を是正し、指定された IA-01/02/05 と既存契約を退行させていない。
- 測定成立性: `observed`。
- 証拠資格: `条件付き適格`。指定 range の ACCEPT 根拠として適格。新規入力クラス、別 root、C14、CI は測っていない。
- 計器欠陥: 製品計器について新規検出なし。
- fixture 操作: 最初の temp clone は Git ownership 制約で setup exit 128。copy＋temp `git init` へ切替。最初の fresh cell は検査側の改行 quoting 誤りで SyntaxErrorとなったため不採用とし、修正版を再実行した。
- Q1 asked: 仕様文・コメント・selftest 表示と実挙動を突合。
- Q2 asked: fresh を known-good、既存 file/dir を known-bad として実測。
- Q3 asked: IA-06/07 と各指定回帰腕を個別に判定。
- Q4 asked: OS-temp fixture と実 CLI を使用し、台帳・marker・報告を実入力として観測。
- Q5 asked: setup不能と fixture 操作ミスを PASS に算入せず。
- Q6 asked: 各コマンド直後の `$LASTEXITCODE` を採取。
- Q7 asked: 3ツールの selftest と独立腕を併用。
- Q8 NA: gate の例外・override 設計は本 round の対象外。
- Q9 asked: `HEAD ddae2ee…` と検査後の clean 状態を確認。
- Q10 asked: 未測定次元を上記のとおり限定。
- Q11 asked: file/dir/fresh/delayed、判定語、パスの意味的クラスを分離。

## 範囲外の観察

- sandbox SID と元 `.git` 所有者の相違により temp `git clone` は `dubious ownership` で exit 128。OS-temp copy＋新規 git repository で回避し、製品判定には算入していない。
- temp fixture の `git add` で global ignore への Permission denied 警告を観測したが、commit・witness・全検査腕は成立した。

human_action: none。指定された r3 検査範囲は完了し、新規所見はない。