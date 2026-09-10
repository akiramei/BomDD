# 判定: ACCEPT

ECO-062 第1弾の独立受入検査 r4（IA-08／IA-08b 是正、8腕統合回帰に限定）は **ACCEPT**。IA-08・IA-08b はともに **resolved**、指定回帰は全て期待値と一致した。新規所見 IA-09 以降はない。

## 検査対象・設備

- 対象 revision: `d9fe30594d11a01276c030b1b53f59f4c1600b5f`
- 検査官: OpenAI Codex / GPT-5 系（self-reported。詳細な serving variant は非開示）
- Codex CLI: `codex-cli 0.154.0`
- Python: `3.13.1`
- OS: Windows、PowerShell 7
- 開始時・終了時とも `git status --short` は出力なし、exit 0
- リポジトリ内への書込み: なし

開始確認:

```text
$ git rev-parse HEAD
d9fe30594d11a01276c030b1b53f59f4c1600b5f

$ git status --short
（出力なし）
```

## preflight receipt

- task classification: bug-fix/continuation の独立受入再検査
- baseline: confirmed — 指定 revision と HEAD が一致
- current-work-state: confirmed — order §8.3 は r3b 是正済み・r4 引き渡し中
- failing behavior: confirmed — r3 IA-08 の再現手順あり
- expected behavior: confirmed — W5、IA-08、IA-08b の期待 exit と生成有無が明記
- acceptance target: confirmed — IA-08/08b と8腕統合回帰に限定
- discovered prerequisites: confirmed — Python、Git、OS temp が利用可能
- 開始判定: `PROCEED_WITH_LIMITS`
- 制限: CI、self-conformance 全体、範囲外の既存 IA-01〜07 は今回の受入根拠として再検査しない
- override: なし

## IA-08 — resolved

実装座標:

```text
method/tools/bomdd-witness.py:112-134  _canon / _inside_worktree
method/tools/bomdd-witness.py:147-150  W5 拒否
method/tools/bomdd-witness.py:324-333  selftest の拡張長パス対照
```

OS temp の独立 git リポ:

```text
T=C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r4-inspection-20260910
OUTSIDE=C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r4-outside-20260910
```

### 4腕実測

通常表記・作業木内:

```text
$ python tools/bomdd-witness.py produce --eco ECO-908 \
  --gate "g=0:logs/g.log:12" \
  --out C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r4-inspection-20260910\normal-inside.json \
  --producer independent-r4

witness を束縛対象の作業木内に置けない(自己参照): ...\normal-inside.json — .git 配下か作業木外を指定
exit=2
exists=False
```

通常表記・作業木外:

```text
$ python tools/bomdd-witness.py produce --eco ECO-908 \
  --gate "g=0:logs/g.log:12" \
  --out C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r4-outside-20260910\normal-outside.json \
  --producer independent-r4

witness 生成: ...\normal-outside.json(tree cab1737b89be・gates 1・stop NONE)
exit=0
exists=True
```

拡張長表記・作業木内:

```text
arg=\\?\C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r4-inspection-20260910\extended-inside-correct.json

$ python tools/bomdd-witness.py produce --eco ECO-908 \
  --gate "g=0:logs/g.log:12" --out <上記 arg> \
  --producer independent-r4

witness を束縛対象の作業木内に置けない(自己参照): \\?\C:\...\extended-inside-correct.json — .git 配下か作業木外を指定
exit=2
normal_path_exists=False
```

拡張長表記・`.git\bomdd-witness` 配下:

```text
arg=\\?\C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r4-inspection-20260910\.git\bomdd-witness\extended-git-correct.json

$ python tools/bomdd-witness.py produce --eco ECO-908 \
  --gate "g=0:logs/g.log:12" --out <上記 arg> \
  --producer independent-r4

witness 生成: \\?\C:\...\.git\bomdd-witness\extended-git-correct.json(tree cab1737b89be・gates 1・stop NONE)
exit=0
normal_path_exists=True
```

参考対照として、通常表記の `.git\bomdd-witness` も exit 0・生成ありだった。

なお、最初の拡張長パス試行では検査側の接頭辞生成が `\?C:\...` となっていたため、その2結果は判定根拠から除外した。上記は文字コード値から正しい `\\?\` を構成し、実引数を表示して再測定した結果である。

結論: 拡張長パスの作業木内出力は exit 2・未生成、`.git` 配下は exit 0・生成。W5 と一致する。

## IA-08b — resolved

実装座標:

```text
method/tools/bomdd-witness.py:156-160
```

既存ファイル `x.json` の下を出力先とした実 CLI:

```text
$ python tools/bomdd-witness.py produce --eco ECO-908 \
  --gate "g=0:logs/g.log:12" \
  --out C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r4-outside-20260910\x.json\y.json \
  --producer independent-r4

witness を書けない: ...\x.json\y.json(FileExistsError)— 測定不能は合格ではない
exit=2
child_exists=False
```

標準出力・標準エラーを統合して観測したが traceback はなかった。期待する exit 2、未生成、例外の利用者向け分類を満たす。

## r1 8腕統合回帰

独立 git リポで実 witness を生成し、各不良腕では一項目のみ変更した。

```text
$ python tools/bomdd-witness.py produce --eco ECO-900 \
  --gate "g=0:logs/g.log:12" --producer independent-r4

witness 生成: ...\.git\bomdd-witness\ECO-900.json(tree cab1737b89be・gates 1・stop NONE)
exit=0
```

| 腕 | 実測出力 | exit | 判定 |
|---|---|---:|---|
| known-good | `ADVANCE: tree 一致(cab1737b89be)・gates 1 件 exit 0・stop NONE` | 0 | 期待一致 |
| hash | `STOP: tree 不一致(witness 000000000000 / 現 cab1737b89be)` | 1 | 期待一致 |
| FAIL | `STOP: gate FAIL 混入(g)` | 1 | 期待一致 |
| gates 空 | `STOP: gates 欠測(測定不能は合格ではない)` | 1 | 期待一致 |
| stop≠NONE | `STOP: stop_type=NORMATIVE_RULING` | 1 | 期待一致 |
| dirty | `STOP: tree 不一致(witness cab1737b89be / 現 ac972f63b5d4)` | 1 | 期待一致 |
| 不在 | `witness 読取不能: ...does-not-exist.json([Errno 2] No such file or directory...)` | 2 | 期待一致 |
| 作業木内出力 | `witness を束縛対象の作業木内に置けない(自己参照): inside-8arm.json`、`exists=False` | 2 | 期待一致 |

結果: **8/8 期待一致**。IA-08 是正による既存腕の退行は観測されなかった。

## selftest

```text
$ python method/tools/bomdd-witness.py --selftest
bomdd-witness selftest PASS(known-good 0 / hash・fail・missing・stop・dirty 1 / 不在 2 / 不正 stop 2 / 作業木内出力 2 / r2: 構造不完全 gate 1・不完全 gate 生成拒否 2・個体不一致 1・git 不能 2・引数不正 ArgError・r2b: temp 不能 2・作業木内 temp 2・r3: 拡張長パス 2/.git 配下 0・書込不能 2)
exit 0
```

```text
$ python method/tools/bomdd-job.py --selftest
bomdd-job selftest PASS(整合 NONE / 不整合 2 方向 / order 不在 / fence 内見出し無視 / 出所なし欄 null / 全欄 source / r2: 複数 --json 単一文書・引数不正 MISSING_INPUT・null エントリ・r2b: 対象なし/未知オプション MISSING_INPUT)
exit 0
```

## diff 監査

```text
$ git diff --name-status 1440ef9..d9fe30594d11a01276c030b1b53f59f4c1600b5f
M  bomdd/60-change-order-eco-062.md
M  bomdd/60-change-register.yaml
A  bomdd/reports/independent-inspection-eco-062-r3.md
M  method/tools/bomdd-witness.py
```

指定どおり、製造物は `method/tools/bomdd-witness.py` のみで、残りは order・register・r3 報告だった。

```text
$ git diff --quiet 1440ef9..d9fe30594d11a01276c030b1b53f59f4c1600b5f -- method/tools/bomdd-job.py
exit 0
```

`bomdd-job.py` に差分なし。diff 監査は PASS。

## 副経路

`_inside_worktree()`／`_canon()` を対象個体から直接ロードして測定した。

```text
direct-inside=True
direct-outside=False
inside-junction-to-outside=False
outside-junction-to-inside=True
unc-normal-canon=\\server\share\dir\x.json
unc-extended-canon=\\server\share\dir\x.json
unc-canon-equal=True
exit=0
```

- 通常パスの作業木内／外: 期待一致
- 作業木内 junction → 外部: 外部判定、期待一致
- 作業木外 junction → 内部: 内部判定、期待一致
- 通常 UNC と `\\?\UNC\` の正規化: 同値
- junction は実作成して測定後、両方削除済み
- 実ネットワーク共有上での書込みは未実施

## 新規所見

IA-09 以降: **なし**。

独立 fixture 作成時に利用者側 Git ignore ファイルへのアクセス警告が1件出たが、fixture の commit、全試験、exit 観測は成立した。製造物の所見には分類しない。

## /calibrate receipt

| 主張 | 測定成立性 | 証拠資格 |
|---|---|---|
| IA-08 は解消した | observed | 適格。正しい `\\?\` 実引数、実 CLI、exit、通常パス上の生成有無を確認 |
| IA-08b は解消した | observed | 適格。実 FileExistsError 経路で exit 2・未生成・traceback なし |
| 8腕に退行がない | observed | 適格。独立 git リポで 8/8 期待一致 |
| 両 selftest が成功する | observed | 適格。各 exit 0 |
| 指定 diff 窓が限定範囲内 | observed | 適格。4ファイルのみ、`bomdd-job.py` 差分なし |
| UNC 経路全般が正しい | observed | 条件付き適格。文字列表記の正規化同値のみ。実共有上のI/Oは未測定 |

検出した計器欠陥: 最初の拡張長パス入力を組み立てた検査側コマンドに接頭辞誤りあり。誤測定を除外し、正しい引数を表示して再測定した。製造物の新規欠陥はなし。

| battery | 記録 | 要点 |
|---|---|---|
| Q1 | asked | W5、IA-08、IA-08b の主張と実測を照合 |
| Q2 | asked | 受理・拒否の対照腕を実測 |
| Q3 | asked | 8腕を個別に測定 |
| Q4 | asked | 実 CLI・実ファイルを入力として使用 |
| Q5 | asked | 未実施項目を PASS に算入せず |
| Q6 | asked | 各 exit を取得後に次の試験へ進行 |
| Q7 | asked | 両 selftest の陽性対照を実行 |
| Q8 | NA | 新規予防ゲートの受入ではない |
| Q9 | asked | HEAD と指定 revision を開始・終了時に突合 |
| Q10 | asked | 未測定次元を下記に宣言 |
| Q11 | asked | 通常、拡張長、junction、UNC 表記を別クラスで測定 |

## 後片付けと終了確認

junction 2件の削除は成功した。検査ディレクトリ本体の再帰削除は、明示パスを OS temp 直下と確認した後も実行基盤に拒否されたため、次の2パスが残置している。

```text
C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r4-inspection-20260910
C:\Users\akira\AppData\Local\Temp\BomDD-eco062-r4-outside-20260910
```

残置物は本検査用 fixture と witness のみ。相互参照していた junction は削除済み。

最終確認:

```text
$ git rev-parse HEAD
d9fe30594d11a01276c030b1b53f59f4c1600b5f

$ git status --short
（出力なし）
exit 0
```

## 未検査項目

- 対象 revision の CI 結論、対象リポでの `self-conformance`
- 実ネットワーク共有上の UNC I/O、symbolic link、linked worktree、submodule、Linux、同時更新
- IA-01〜07 の個別再検査（指定された8腕と両 selftestによる限定回帰のみ）
- witness に申告された gate 値が実際の検査結果と一致するか

## この検査が支持しないもの

対象 revision の CI 成功や self-conformance 全体の成立は支持しない。  
実共有を含む全パス表記・全 Git 構成での正しさ、witness 申告値の真正性は支持しない。  
通常の `git status` が表示しない対象まで無変更であること、未検査入力に不適合がないことは支持しない。