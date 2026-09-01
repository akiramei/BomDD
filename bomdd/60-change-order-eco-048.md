# Change Order — ECO-048(入口文書のドリフト是正 — AGENTS.md/CLAUDE.md 査定 A〜C)

> 裁定: user 2026-09-01「A〜C を起票して修正まで進めて」— 入口文書査定(3 観点: モデル
> バージョン依存・分量過多・内容の適切性)の所見 3 件の是正。裁定が gate ① を兼ねる。

## 担当設備(equipment)

- 製造: requested/resolved `claude-fable-5`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠 — 査定所見 3 件)

- **A(陳腐化)**: AGENTS.md 限界節「3・4 の違反は現状ローカルでは自動検出されず」/
  CLAUDE.md「現状ローカルに強制層はなく」— ECO-046 の pre-push hook + PASS witness 設置
  (`core.hooksPath=bomdd/hooks`・hook 実在を実機確認)と矛盾。書いた時点では正しく、
  機構が追い越した型のドリフト。
- **B(結線欠落)**: converge.md(写し)は「非 Claude ハーネスも AGENTS.md 経由で本ファイルを
  読み、同じ契約に従う」と主張するが、AGENTS.md にスキル参照が一切ない(全文実読)。
  装置(自発起動契約)はあるが入口からの到達経路が無い — ECO-020 と同型。
- **C(正本二重化)**: CLAUDE.md「変更管理」節 1 点目は AGENTS.md 規律 1 のほぼ逐語再掲。
  補足価値は `--dotnet` と `/lesson-promote` の 2 点のみ。
- 査定の他 2 観点(モデル依存・分量)は所見なし — モデル名参照ゼロ(grep 実測)・
  計 91 行で階層化が機能。

## 1. 変更要求(製造対象)

- **A**: AGENTS.md 限界節+ CLAUDE.md ECO-024 節末尾を現状へ更新。**逆方向の過大主張を
  作らない** — 機械強制されたのは規律 4 の push 経路のみ・到達目標は「うっかり型の素通り
  遮断」まで・branch(refs/heads/*)のみ・意図的回避は信頼境界外・commit 段階と規律 3 の
  チェーン自体は明文化のまま・最終層は CI(すべて hook 実文/ECO-046 宣言からの転記)。
- **B**: AGENTS.md へ「作業スキル(ハーネス非依存の契約)」節+正本の所在の表 1 行を追加 —
  preflight/converge/calibrate の正本パスと自発起動契約の適用宣言のみ(**契約本文は複製
  しない** — 正本二重化を作らない)。散文契約の起動非保証と機械ゲート(C16/C17)による
  非起動捕捉も 1 文で言及。
- **C**: CLAUDE.md「変更管理」節から規律 1 の逐語再掲を削除(`--dotnet`・`/lesson-promote`
  は保持)。

## 2. 影響なし予測(反証可能・製造前に凍結)

diff は AGENTS.md・CLAUDE.md+台帳系のみ。self-conformance に両ファイル本文の検査は
存在しないため全検査の判定不変。C16 は本 order を required と判定する見込み —
receipt 埋め込み済み。

## 3. 受入

- **V1**: 各修正が実測へトレース可能(A= hook 実文・ECO-046 §4/コード恒久宣言 / B=
  converge.md 実文+スキル正本の実在 / C= AGENTS.md 規律 1 実文)。A は限定列挙
  (push 経路のみ・うっかり型のみ)を含み過大主張なし。
- **V2**: self-conformance 全 PASS(判定不変)。
- **V3**: CI 緑(headSha 照合)。**V4**: diff 窓。

## /preflight receipt(起動経路: 自発 — 既存状態依存の是正タスク。V6 初回実使用)

- 契約: A/B/C の 3 修正(gate ① 裁定で固定)。
- 状態判定: AGENTS.md/CLAUDE.md 本文= **confirmed**(今セッション全文実読)/ hook 設置=
  **confirmed**(`git config core.hooksPath`+`ls` 実測)/ ECO-046 宣言済み限界=
  **confirmed**(order §4・hook コード実文)/ converge.md 主張= **confirmed**(実文)/
  次番= 048 **confirmed**(register 末尾= 047)。
- 開始判定: **PROCEED**(stale/contradicted/unknown なし)。

## /converge receipt(起動経路: 自発〔統治文書の文面変更〕)

- **判定: 収束**(round 軌跡: 1→0→0)。round 1 = 1 件(lesson-promote は自発起動契約を
  持たず templates 正本も無い〔ls 実測〕— B の一覧は契約 3 スキルに限定し、lesson-promote は
  CLAUDE.md の既存参照に留める)。
- 検証した主張: hook の到達目標・対象範囲(bomdd/hooks/pre-push 実文)/ AGENTS.md に
  スキル参照なし(全文)/ CLAUDE.md 重複(実文照合)/ スキル正本の所在(ls)。
- 未収束事項: なし。

## 4. 製造と受入の実測(2026-09-01)

- diff 監査の窓: baseline `fc41ee2`(起票直前 HEAD・起票+製造は同一窓)→ head は受入時に確定。
- A: AGENTS.md 限界節を書き換え(push 経路のみ・うっかり型まで・branch のみ・意図的回避は
  信頼境界外・最終層 CI — 全て hook 実文/ECO-046 からの転記)。CLAUDE.md ECO-024 節末尾を
  同期(「強制ではない」→「push 経路は機械化・commit 段階と規律 3 は明文化のまま」)。
- B: AGENTS.md へ「作業スキル(ハーネス非依存の契約)」節+正本の所在の表 1 行。契約 3 スキル
  (preflight/converge/calibrate)に限定・契約本文は複製せず・C16/C17 による非起動捕捉を 1 文。
- C: CLAUDE.md の規律 1 逐語再掲を削除し「正本は AGENTS.md 規律 1(ここに再掲しない)」へ。
  `--dotnet`・`/lesson-promote` は保持。
- 副次: EXP-20260901-03 第 2 回観測を記帳(preflight 起動 2/2 — 第 1 回= ECO-042 V6 は
  Q10 掃引開始時に完了済みだったことを確認。台帳系)。
- V1= 各修正のトレース先を §1 記載どおり確認。V2 以降は §5 で確定。

### 較正 receipt(/calibrate 自己適用 — trigger ③ 類: 統治文書の変更。二軸)

- 査定した主張と判定:
  1. 「A は過大主張を作らない(逆方向含む)」— **observed / 適格**(限定列挙= push 経路のみ・
     うっかり型のみ・commit 段階未強制を明記 — hook 実文と突合)。
  2. 「B は正本二重化を作らない」— **observed / 適格**(所在参照+適用宣言のみ・契約本文の
     複製なし — diff 実文)。
  3. 「C で情報喪失なし」— **observed / 適格**(削除は逐語再掲のみ・固有情報 2 点は残存)。
  4. 「入口文書の改訂が読み手の行動を実際に変える(実効到達)」— **unknown(理由コード:
     未実行)** — ECO-047 §4 と同種の限界。
- 検出した計器欠陥: なし。検出力の限界: 本査定は文書変更の妥当性のみ。

## 5. CI 実測(V3)

- (push 後に記入)

## 6. クローズ

- (受入時に記入)
