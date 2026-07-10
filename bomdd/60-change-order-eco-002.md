# ECO-002 — stage0-survey の git 失敗黙殺(fail-open → fail-closed)

## 起票(2026-07-10)

- 出典: メンバー外部レビュー所見4(P1)。「stage-0 健診が Git 失敗を空の健全データとして返す。
  存在しないリポジトリを指定しても `head: ""`・コミット 0 件の JSON を出して終了コード 0」。
- 再現(是正前・実測): `--repo /c/nonexistent-repo-xyz --skip-loc` → **exit 0**、
  `head: ""`、`commits_analyzed: 0`、`fix_rate: null` の「健全に見える」JSON を出力。
- 工程診断: 健診器=測定器が「測定不能」を「問題なし」として報告する構造。MSA の観点で
  測定器として最悪の故障モード(transfer-02 還元第2R の測定系規律とも矛盾)。
  該当箇所= `subprocess.run(...).stdout` の直取り 3 箇所(rev-parse / log / ls-tree)。
- 既発表データへの波及: stage0-oss(3 リポ・HA core 5.41M 行)は実在リポ相手で
  正常系のみ通過しており、**測定値への波及なし**(下記回帰検証で正常系不変を機械確認)。

## 裁定

- ユーザー承認(2026-07-10)「1から着手して」。
- 是正方針: 欠測を exit 2 で停止する fail-closed 化。**測定規約(protocol §2 で凍結)の
  測定定義は変更しない** — 変えるのは欠測の扱いのみ(正常系の出力はバイト同一であること)。

## 影響分析(製造前凍結)

- 影響なし予測: `method/tools/stage0-survey.py` 以外は diff ゼロ。正常系の出力 JSON は
  是正前後でバイト同一(反証可能: 実リポで前後の出力を diff)。

## 是正

1. `die(msg)`: `[stage0-survey] 測定不能: …` を stderr へ出し **exit 2**。
2. `run_git(repo, *args)`: returncode 検査つき git 実行ヘルパ。失敗時は stderr 先頭行を添えて die。
   rev-parse / log / ls-tree の 3 箇所を置換。
3. 前提検査: リポジトリディレクトリの存在 + `rev-parse HEAD` 成功。
4. ゼロ件ガード: 解析可能コミット 0 件・HEAD の解析可能追跡ファイル 0 件も「測定不能」
   (欠測は健全データではない)。
5. stderr を UTF-8 に固定(Windows コンソールでのメッセージ化け防止)。

## 検証(2026-07-10)

- **陽性対照**(是正前は全て exit 0 の空データ):
  - 存在しないリポ → `測定不能: リポジトリディレクトリが存在しない` **exit 2**
  - git 管理外ディレクトリ → `測定不能: git rev-parse が失敗 (exit 128): fatal: not a git repository` **exit 2**
- **回帰**: 実リポ(BomDD 自身・`--max-commits 100 --skip-loc`)の出力 JSON が
  是正前後で **diff なし(バイト同一)** — 測定定義の不変を機械確認。
- 影響なし予測: 的中。

## 教訓(還元候補 — lesson-promote 経由)

- 測定治具の検査には**異常系の陽性対照**(存在しないリポ・git 外・空履歴で「止まる」こと)を
  正常系 golden と対で持つ — mutation matrix(レビュー方法論提案)の治具版。
- `subprocess.run(...).stdout` 直取りは fail-open の定型 — 他治具
  (time-decomposition.py / impact-retrospective.py / ui-extract 系)の横展開検査は
  所見3・6 の是正時に実施。
