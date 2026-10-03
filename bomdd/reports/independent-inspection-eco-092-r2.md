[INFORM / COMPLETE]

ACCEPT

- range: 是正確認+回帰
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: e0963695046f91bd09c0d50ed04d07de0f4eb684
- commit: 0
- 外部 API: 呼出しなし
- リポ内ファイル作成・変更・削除: 0
- 本リポ `.git/index` 操作: 0
- 読んだファイル一覧:
  - `bomdd/60-change-order-eco-092.md` §3・§4・§6.1
  - `bomdd/reports/independent-inspection-eco-092.md`
  - `bomdd/60-change-register.yaml` の ECO-092 `diff_audit`
  - `method/tools/self-conformance.py` の C18 限界宣言・`_witness_tree`・`_witness_selftest`・`_write_selfconf_witness`
  - `bomdd/hooks/pre-push`
- 読んだ差分:
  - `git diff --name-only 069e0d5 e0963695046f91bd09c0d50ed04d07de0f4eb684`
  - `git diff 5d90ba4 e0963695046f91bd09c0d50ed04d07de0f4eb684 -- method/tools/self-conformance.py`
  - `git diff --stat 069e0d5 e0963695046f91bd09c0d50ed04d07de0f4eb684 -- bomdd/hooks/`

開始時:

- `git rev-parse HEAD`: `e0963695046f91bd09c0d50ed04d07de0f4eb684`
- `git status --short`: 出力なし
- `git ls-files -v | grep -c '^[Sh]'` 相当: `1151`

終了時:

- `git rev-parse HEAD`: `e0963695046f91bd09c0d50ed04d07de0f4eb684`
- `git status --short`: 出力なし
- `git ls-files -v | grep -c '^[Sh]'` 相当: `1151`

## 判定概要

| 項目 | 判定 | 観測 |
|---|---|---|
| 1. IA-02 の是正確認 | PASS | 窓内 20 パスを ECO-092 の `allowed_paths` 20 エントリと機械照合し、範囲外は 0。ECO-094 の order と `reports/eco-094-upstream-sbom-trial/` が追加済み。register の直前コメントに、窓が開いている間の ECO-094 起票に伴う追加理由と tools 非接触が記載されている。 |
| 2. IA-03 の是正確認 | PASS | C18 限界宣言 (6) は、sparse 外の path が index 内容のまま tree に残ること、通常は index=HEAD であること、稀な index≠HEAD では未検査 bytes を証明することを明記。`5d90ba4..e096369` の対象差分はこのコメント4行への訂正だけで、`_witness_tree` 実装は不変。 |
| 3. V1〜V4 回帰 | PASS | V1 の較正3腕はすべて True。V2 はフラグ0件の隔離 clone で是正前後とも tree `3a69231ffb8332ba9f2d3ded748efb3559cbc49e`、実 index 不変。V3 は破損 index で stale witness 削除、stdout・stderr に同一の `[witness]` 行。V4 は hook diff 0、witness は `<40桁tree>\nPASS\n`、LF 2個・CRなし。 |
| 4. 境界表の抜き取り | PASS | 指定6行を隔離リポで再測し、すべて r1 と同一判定。いずれも実 index 不変。 |

## 回帰の表

| 入力 | r1 の判定 | r2 の判定 |
|---|---|---|
| V1: skip-worktree・対照・非 git の較正3腕 | PASS | PASS — `skip-worktree=True・対照=True・失敗腕=True` |
| V2: フラグ0件 | PASS | PASS — 是正前後の tree は同一、実 index 不変 |
| V3: 破損 index | PASS | PASS — `(None, why)`、stale witness 削除、stdout/stderr に同一行 |
| V4: hook・witness 形式 | PASS | PASS — hook diff 0、`<tree>\nPASS\n` |
| assume-unchanged | PASS | PASS — `h f`、tree の blob=作業ツリー、実 index 不変 |
| 両フラグ | PASS | PASS — `h a` と `S s`、両 blob=作業ツリー、実 index 不変 |
| 空白パス | PASS | PASS — `a b.txt` の blob=作業ツリー、実 index 不変 |
| 作業ツリー削除+S | PASS | PASS — 返却 tree から path 削除、実 index は `S f` のまま |
| 2オプション同時指定の再現 | PASS | PASS — exit 0 だが `S f` が残る |
| 非 git root | PASS | PASS — `(None, "ls-files 失敗(exit 128): fatal: not a git repository…")` |

## 所見(あれば IA-NN・blocking / non-blocking)

なし。

## 範囲外の観察(判定に含めない)

- 検査官の本作業木は sparse-checkout 状態で、開始時・終了時とも `S/h` カウントが `1151` だった。したがって V2 の「本リポ・フラグ0件」条件は、対象 revision を Git bundle 経由で OS temp の隔離リポへ展開して再現した。
- `python method/tools/self-conformance.py` 全体は、ブリーフの既知環境差に従って判定へ使用せず、実行もしていない。C18 の較正3腕は関数を直接実行した。
- 初回の隔離 clone は Git の dubious ownership により成立せず、次の試行は隔離 clone の後片付け時に sandbox のアクセス拒否で停止した。いずれも測定値として採用せず、Git bundle 経由の隔離リポで全腕を再実行した。本リポへの変更はない。