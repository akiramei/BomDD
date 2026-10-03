[INFORM / COMPLETE]

ACCEPT

- range: 是正確認+回帰
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: 76e2a010e58a2589e7061d60f9cbf78f6cf4e054
- commit: 0
- 外部 API: 呼出しなし
- 読んだファイル一覧: `bomdd/60-change-order-eco-096.md` §3・§5・§6.1、`bomdd/reports/independent-inspection-eco-096.md`、`bomdd/60-change-register.yaml` の ECO-096 entry、`method/tools/bomdd-witness.py`、`.github/workflows/self-conformance.yml`
- 開始時 `git status --short`: 空
- 開始時 `git ls-files -v | grep -c '^[Sh]'` 相当（case-sensitive）: 0
- 終了時 `git status --short`: 空
- 終了時 `git ls-files -v | grep -c '^[Sh]'` 相当（case-sensitive）: 0
- 終了時 revision: 76e2a010e58a2589e7061d60f9cbf78f6cf4e054
- 本リポの `.git/index`: 操作なし
- リポ内ファイルの作成・変更・削除: 0

## 判定概要

| 項目 | 判定 | 観測 |
|---|---|---|
| 1. 製造物の不変・差分窓 | PASS | `f34a6d6..76e2a010` の `bomdd-witness.py` と workflow の差分は空。`a2eae9e..76e2a010` の6パスはすべて ECO-096 `allowed_paths` 内。 |
| 2. V1 回帰 | PASS | selftest は exit 0、1行目 `ADVANCE OK:`。正規化を no-op にしたメモリ上の変異は exit 1、`STOP SELFTEST_FAIL: 3 件`。リポのファイルは変更していない。 |
| 3. V2〜V4 回帰 | PASS | V2 は旧・新 tree が同一。V3 は旧=index blob、新=worktree blob。V4 の失敗注入は exit 2、`UNMEASURABLE TREE_UNAVAILABLE(INDEX_NORMALIZE_FAILED)`。 |
| 4. 境界表の抜き取り | PASS | 指定された6行すべてを再測し、r1 と同一判定。各隔離腕で実 index 不変。 |

## 回帰の表

| 入力 | r1 の判定 | r2 の判定 |
|---|---|---|
| フラグ0件 | 旧・新 tree 同一 | 同一（`e28aa1cb7393…`）、PASS |
| V3: index=不正 bytes・S・worktree=正しい bytes | 旧=index、新=worktree | 旧 blob `16c51c1e…`、新 blob=期待値 `2724f963…`、PASS |
| assume-only（`sub/a.txt`） | 新=worktree、旧=index | 同一。`h sub/a.txt` を維持、PASS |
| 両フラグ | 新=worktree、旧=index | 同一。`s f.txt` を維持、PASS |
| 空白パス（`sp ace.txt`） | NUL区切りで完全に処理 | 新=worktree、旧=index、PASS |
| 作業ツリー削除+S | 新treeから削除、旧treeにはindex blob | 新treeにpathなし、旧treeにpathあり、PASS |
| produce→verify 往復 | 不変なら `ADVANCE OK` | produce exit 0、verify exit 0・`ADVANCE OK`、PASS |
| produce後のworktree変更 | `STOP TREE_MISMATCH` | exit 1・`STOP TREE_MISMATCH`。旧経路は変更前後で同一tree、PASS |
| 2オプション同時指定 | exit 0でもSが残る | 正順・逆順とも exit 0、`S f.txt` が残留、PASS |
| 正規化失敗注入 | `INDEX_NORMALIZE_FAILED`、exit 2 | `UNMEASURABLE TREE_UNAVAILABLE(INDEX_NORMALIZE_FAILED)`、exit 2、PASS |

## 所見

なし（blocking 0 / non-blocking 0）。

## 範囲外の観察（判定に含めない）

- 新しい境界探索は実施していない。
- 最初の隔離試験は Windows の読み取り専用 Git object を一時ディレクトリから削除する段階で中断したため、後片付けを修正して全測定を最初から再実行した。中断時の外部一時ディレクトリ `eco096-r2-vodbri2q` は、sandbox policy が削除操作を拒否したため残存している。本リポ外であり、判定およびリポ状態には影響しない。