[INFORM / COMPLETE]
REJECT — 理由: IA-01、IA-02、IA-03、IA-04、IA-05。

対象: ECO-073 r1、range=境界探索、inspector=EQ-002。リポジトリ内のファイルは変更していない。

## 所見

### IA-01 — cell の非 0 exit が入口の exit に反映されない

再現コマンド:

```powershell
python method/tools/bomdd-run.py ECO-900 --ledger <temp>\ledger.jsonl `
  --cell '"python" "<temp>\write.py" ACCEPT_BASE64 7' `
  --executor EQ-002 --report reports/r.md
```

観測:

```text
ADVANCE ECO-900 OK → next · launching @b00a9a5b20ed
cell exit 7
report ACCEPT sha256:61164e4570e1 (EQ-002)
入口 exit=0 / harness $LASTEXITCODE=0
```

台帳の `cell_exit` は 7。報告も束ねられたが、入口は [bomdd-run.py:431](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-run.py:431) で常に `return 0`。

期待との差: §1-2、R10 の「exit は cell の終了コードに従う」に反する。

帰属: 製造物。

### IA-02 — 報告が今回の cell により生成されたことを識別できない

再現コマンド:

```powershell
Set-Content <fixture>\reports\stale.md "ACCEPT"
python method/tools/bomdd-run.py ECO-900 --ledger <temp>\ledger.jsonl `
  --cell '"python" -c "pass"' --executor EQ-002 `
  --report reports/stale.md
```

観測:

```text
ADVANCE ECO-900 OK → next · launching @12773d489254
cell exit 0
report ACCEPT sha256:61164e4570e1 (EQ-002)
入口 exit=0 / harness $LASTEXITCODE=0
```

cell は報告を書いていないが、既存ファイルが `ACCEPT` として束ねられた。

遅延子プロセス腕:

```text
1 行目: ADVANCE ECO-900 OK → next · launching @b00a9a5b20ed
2 行目: cell exit 0
3 行目: report MISSING (no file) (EQ-002)
入口読取り時 exists=false、1.8 秒後 exists=true・sha256=61164e4570e1…
```

期待との差: 「cell が報告を書かなかった→MISSING」と、cell 終了後にその cell の報告を束ねるという結線を満たさない。入口は [bomdd-run.py:306](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-run.py:306) で、実行前状態や生成時刻を確認せず単にパスを読む。

帰属: 製造物。遅延書込みの発火条件は意図的な環境差。

### IA-03 — リポ相対パスの基準が git root ではなく呼出し cwd

再現コマンド:

```powershell
Set-Location <fixture-root>\sub
python C:\Users\akira\source\repos\BomDD\method\tools\bomdd-run.py ECO-900 `
  --ledger <temp>\ledger.jsonl --cell '<marker cell>' `
  --executor EQ-002 --report reports/fromsub.md
```

観測:

```text
UNMEASURABLE ECO-900 job:MISSING_INPUT → operator @-
入口 exit=2 / ledger decision 1 行追記 / cell 起動なし
```

実装は [bomdd-run.py:725](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-run.py:725) の `Path.cwd()` を root とする。従って別 cwd では報告パスだけでなく register と worktree の基準も移る。

期待との差: `--report` の「リポ相対」と、入口から cell へ渡す `cwd=root` が実際の git worktree root に固定されない。

帰属: 製造物。別 cwd はブリーフ指定の環境差。

### IA-04 — `--report` なしの台帳は ECO-072 基線と同一でない

再現コマンド:

```powershell
git show 2a921bd:method/tools/bomdd-run.py > <temp>\base\bomdd-run.py
# 同一 temp fixture、同一 witness、同一 cell で基線と現物を各実行
```

観測:

```text
dry:
  output_equal=true
  ledger_equal=false
  現物 decision 行だけ report:null を追加

--cell:
  output_equal=true
  ledger_equal=false
  現物 decision 行に report:null
  現物 cell 行に executor:"EQ-002", report:null
```

両呼出しとも exit 0。harness `$LASTEXITCODE=0`。

期待との差: ブリーフ 5 と影響なし予測の「出力と台帳が同じ」のうち、出力は一致するが台帳スキーマは一致しない。selftest は新しい `report:null` を期待しており、基線との比較になっていない。

帰属: 製造物。

### IA-05 — 行頭空白を取り除いてから `^VERDICT` を照合する

再現コマンド:

```powershell
python -c "<bomdd-run.pyをimport>; print(report_verdict('  ACCEPT\n'))"
```

観測:

```text
('ACCEPT', 'ACCEPT')
$LASTEXITCODE=0
```

期待との差: §1-2 の `^(ACCEPT|REJECT|UNMEASURABLE)\b` なら、空白で始まる非空行は `UNPARSED`。実装は [bomdd-run.py:246](C:/Users/akira/source/repos/BomDD/method/tools/bomdd-run.py:246) の `.strip()` により字下げを消し、`verdict_line` にも原文を残さない。

帰属: 製造物。

## 判定語の境界観測

| 入力 | 記録 verdict |
|---|---|
| ヘッダ2行 | `UNPARSED`、line=`[2行目]` |
| ヘッダ前に空白行 | `ACCEPT` |
| UTF-8 BOM付き先頭 | `UNPARSED` |
| `  ACCEPT` | `ACCEPT`（IA-05） |
| `ACCEPT:` | `ACCEPT` |
| `ACCEPT—理由` | `ACCEPT` |
| `ACCEPTED` | `UNPARSED` |
| `Accept` | `UNPARSED` |
| 要約後の2行目に `ACCEPT` | `UNPARSED` |
| fence内 | `UNPARSED` |
| `# ACCEPT` | `UNPARSED` |
| `> ACCEPT` | `UNPARSED` |

## 結線・例外境界

- BOM・CRLF・末尾改行を含む34 bytes: 台帳 `size=34`、sha256 `79fd35e3db14…`。実ファイルと完全一致。BOMのため verdict は `UNPARSED`。
- 空ファイル: `exists=true`、`size=0`、sha256 `e3b0c44298fc…`、`UNPARSED`、tracebackなし。
- 報告なし: `exists=false`、size/hashなし、`MISSING`、tracebackなし。
- 同名ディレクトリ: `MISSING`、tracebackなし。ただし実在するパスを `exists=false` と記録する。
- 読めない通常ファイルの OS ACL 実測は測れなかった。`Path.read_bytes()` に `PermissionError` を注入した腕では `MISSING`、tracebackなし。
- REJECT / UNPARSED / MISSING と cell exit 0 は、いずれも入口 exit 0。判定語による行動はなかった。
- cell exit 7 でも報告は束ねられ、3行の順序も維持されたが、入口 exit は IA-01 のとおり不一致。

## パス検証

| 入力 | 観測 |
|---|---|
| `./reports/x.md` | 受理・起動 |
| `reports\x.md` | 受理・起動 |
| `reports/x.md/` | `ARG_ERROR`、exit 2、起動なし、台帳不変 |
| `.git` | `ARG_ERROR`、exit 2、起動なし、台帳不変 |
| `.gitx/x.md` | 受理・起動 |
| 絶対パス / `..` / 前後空白 / 空要素 | selftestで `ARG_ERROR`、exit 2、起動なし、台帳不変 |
| 約200文字のリポ相対パス | 受理・起動 |
| 別 cwd | IA-03 |

## selftest「報告18腕」の被覆

| クラス | 被覆あり | 未被覆 |
|---|---|---|
| 判定語 | 1ヘッダ、ヘッダなし、CRLF、コロン、2ヘッダ、要約、fence、小文字、`ACCEPTED`、空 | BOM、行頭空白、emdash、見出し、引用 |
| bytes結線 | UTF-8/LFのsize・hash、報告なし、空 | BOM/CRLF/末尾改行のhash、directory、unreadable、既存stale、遅延子 |
| パス | 絶対、`..`、`.git/x`、前後空白、先頭`/`、`//`、値なし、cellなし | `./`、`\`、末尾`/`、`.git`そのもの、`.gitx`、別cwd、長いパス |
| exit非介入 | REJECT/MISSING/UNPARSED＋cell 0 | cell非0を入口exitへ反映、非0時の束ね |
| 後方互換 | 現物の2行出力と`report:null` | ECO-072基線との台帳比較、dry台帳比較 |
| 80桁・順序 | 通常report行と全emit行 | 遅延子、非0 cell、長い原文の組合せ |

`--selftest` 自体は次を出し、直後の `$LASTEXITCODE=0`:

```text
ADVANCE OK: selftest PASS(起動3/dry2/kb5/job停止/不能3/独立性9/報告18/構文5/台帳3/引数13/80桁/表)
```

## 80桁と行順

測定した入口出力はすべて80文字以内。通常の起動では decision → `cell exit` → `report` の順を維持した。長い executor は構文段階で `ARG_ERROR`、1行80文字に短縮され、起動・台帳追記なし。長い `verdict_line` は台帳で120文字に切られ、3行目の長さには影響しなかった。

## /calibrate receipt

査定主張: selftestの緑がR10全仕様の受入根拠になるか。

判定: 測定成立性=`observed`。証拠資格=`不適格`（全仕様の受入根拠として）。収載腕の実行証拠としては条件付き適格だが、IA-01〜05と上表の未被覆次元が残る。検出した計器欠陥は「基線との比較なしに後方互換を合格化」と「cell非0・stale・遅延子・別cwdの未被覆」。帰属はselftest設計を含む製造物。

battery: Q1 asked / Q2 asked / Q3 asked / Q4 asked / Q5 asked / Q6 asked / Q7 asked / Q8 NA / Q9 asked / Q10 asked / Q11 asked。

検出力の限界: Windows ACLによる実ファイル不可読、POSIXでのバックスラッシュ挙動、極端なWindows長パス、実Codex `-o` の内部書込み時系列は未測定。

## 範囲外の観察

- temp fixture の git 操作で sandbox上の global ignore 参照に `Permission denied` 警告が出たが、各fixture commit・測定は成立した。
- register/witness更新や独立性裁定には触れていない。

human_action: none。境界探索roundは完了。是正確認と回帰roundは未実施。