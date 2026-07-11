# ECO-009 — bomdd-init の版来歴の正直記録+kit 完全性(独立検査が検出した5件)

> 状態: **起票のみ(裁定・製造前)**。是正/検証は未着手 — ユーザー裁定で停止中。

## 起票(2026-07-11)

- 出典: **transfer-04(検査の転移)パイロット N=3**。独立受入検査官(Codex gpt-5.5・
  read-only 敵対レビュー)が `bomdd-init.py`(ECO-004)に5件を指摘。当方の実コード検証で
  **5/5 CONFIRMED・全件現 HEAD 4dd025b に残存**(bomdd-init.py は ECO-004 以降未変更)。
- 再現(実測 2026-07-11):
  1. **[med-high] git 不在で正直記録が破綻**: `_method_provenance` 内の `g()` が
     `subprocess.run(["git", ...])` を try 無しで呼ぶため、git 実行ファイル不在で
     `FileNotFoundError`(OSError)が送出され、`install_kit` が **copytree 後に中断**する。
     docstring「git 不在でも止めず not-computed を正直記録(t3 様式)」を**直接反証**。
     上位の `git()` は `except (OSError, CalledProcessError)` で守っているのに、内側 `g()`
     だけ非対称に無防備。
  2. **[med] 不完全 kit の fail-open**: `install_kit` は `if kit.exists(): return` で
     ディレクトリの存在のみを見るため、**manifest / bomdd.lock 欠落の壊れた kit も
     「保持」= 成功扱い**になる。fail-safe(無断上書きしない)を意図した所が fail-open。
     **#1 と連鎖**: #1 の中断で copytree 済み・manifest/lock 未生成の不完全 kit が残り、
     再実行時に #2 がそれを黙認する。
  3. **[low-med] dirty の誤記録**: `bool(g("status", "--porcelain"))` は、rev-parse 成功後に
     `git status` が失敗(returncode≠0 → None)した場合 `bool(None)=False` となり、
     **status 失敗を「clean」と混同**する。commit は not-computed/実値を区別するのに
     dirty は失敗と clean を区別しない — 正直記録の非対称。
  4. **[low-med] lock の adapter.skills 不正確**: bomdd.lock は常に全 `SKILLS` を記録する
     (`skills: [{', '.join(SKILLS)}]`)。`--skills-only --skills <subset>` で部分集合を
     設置した場合、**実際に設置したスキル集合と lock 記録が不一致**になる。`install_kit`
     が `selected` を受け取らないため構造的に記録できない。
  5. **[low] 協働ガイド参照の絶対パス**: 画面案内の working-with-ai.md 参照が
     `{product_root}/bomdd-kit/...`(絶対)のまま。兄弟の checklist/prompts/playbook は
     `{KIT_DIRNAME}/...`(kit 相対)。ECO-004 是正4「案内を kit 相対へ」の逸脱。
     ※ 画面出力のみで生成ファイルへの絶対パス漏れではない(C4 の検査対象外)。

## 裁定

- **未(ユーザー承認待ち)**。製造は個別 blocking 裁定+明示承認が前提。

### 是正方針案(製造前・凍結前の草案)

1. `g()` を `except OSError` で守り None を返す(→ not-computed 経路)。または
   `_method_provenance` 全体を try で包む。git() との対称化。
2. `kit.exists()` でなく **kit 完全性**(kit-manifest.json と bomdd.lock の存在・files 数一致)を
   検査。不完全なら明示エラーで停止(無断上書きしない設計は維持)。
3. `git status` の失敗を `"unknown"` として区別(commit と同じ扱い)。
4. `install_kit(root, created, selected)` に拡張し、lock に**実設置スキル**を記録。
5. working-with-ai 参照を `{KIT_DIRNAME}/...` 相対へ。

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `method/tools/bomdd-init.py` 以外 diff ゼロ。正常系(git あり・完全 kit・
  全スキル設置)の生成物は不変。#4 は lock の adapter.skills の値が部分集合時のみ変わる。

## 是正

- (未着手)

## 検証

- (未実施)

## 教訓(還元候補 — lesson-promote 経由・transfer-04 系列)

- 自己検証が張り損なう類型のうち3つを本 ECO が体現: **(a) 約束した挙動の未検枝**
  (docstring は「git 不在でも止めず」と約束するが、その枝は自己検証で一度も踏まれていない)・
  **(b) 存在 vs 完全性**(kit.exists() は存在を見て完全性を見ない)・**(c) 副経路の正確性**
  (--skills 部分集合という主経路でない枝で lock が嘘をつく)。独立×別ベンダー検査が
  高精度に突いた(transfer-04)。
