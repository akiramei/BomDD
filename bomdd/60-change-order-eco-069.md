# Change Order — ECO-069(織り込み案 B: factory-delegate 工程 5 と 60-change-order の検査官行に「round の目的(range)」と「実行環境の差」を追加〔起票+製造・製造者較正〕)

> 裁定: user 2026-09-11 DECIDE「B→C」— 2026-09-11 還元(improvements.md 還元節・織り込み案 B)の配布側。playbook §3 独立検査規則に織り込んだ 2 規則(「round の目的は受理側が宣言する」
> 「実行環境の差を設計項目にする」・commit f3974c9)を templates(配布物)へ写す。templates は規律 1 により ECO で扱う。**起票と製造を同一 commit で行う**(文書のみ・ECO-063 の型)・
> 受入は製造者較正のみ(user 裁定 B の帰結として当方が解釈— 異系統検査は不要な文書変更)。次に C(中断)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

- playbook §3 独立検査規則(commit f3974c9)は「range 欄(『境界探索』/『是正確認+回帰』)をブリーフに置く」「実行環境の差(sandbox・OS temp・PATH・パス表記・exit 伝播)を製造者環境と
  意図的に変える」を規則にしたが、配布物は未反映(実読): `factory-delegate.md` 工程 5(独立レビュー引き渡し)の観点 4 項に range も環境もない / `60-change-order.md` の検査官行は
  「同 4 項+read-only の強制方法・セッション分離の有無」で range・環境の欄がない。
- 実測(本弧): ECO-064〜067 の検査ブリーフは当方が手書きで range を宣言し(r2 以降)、環境は Codex の sandbox 既定に任せていた(意図的に変えたのは ECO-062 r1 の read-only のみ)。
  配布物に欄がないと製品リポの委譲では欄が書かれない(ECO-063 §0 の「リポ内正本がない → 再発見」型)。

## 1. 変更要求(凍結・文書のみ)

1. `method/templates/product-profile/skills/factory-delegate.md` 工程 5 に 2 項を追加: **range**(round の目的を受理側が宣言・境界探索 round は所見が尽きない・ACCEPT は是正確認+回帰に限定した
   round で・未探索クラスは「支持しないもの」・範囲外の発見は「範囲外の観察」欄で判定に含めない)/ **実行環境の差**(検査官の sandbox モード・OS temp・PATH・パス表記・exit 伝播を製造者環境と
   意図的に変え、ブリーフに記す・計器は原因を分離報告)。playbook §3 への参照つき。
2. `.claude/skills/factory-delegate/SKILL.md`(写し)へ同文を反映(`{{METHOD}}` は自リポ相対に解決・ECO-063 の同期規則)。
3. `method/templates/60-change-order.md` の検査官行に「round の range・実行環境の差(製造者環境との差を明記)」を追加。

**採らない**: playbook 本文の再改訂(織り込み済み)/ 検査ブリーフの独立テンプレート新設(必要が実測されてから)/ bomdd-init・README の変更(スキル本数不変)。

## 2. 影響なし予測(製造前・凍結)

diff は 3 文書+台帳系のみ。self-conformance: C7(スキル本数)不変・C13(リンク)は追加文にリンクなし・C4 scaffold/C14 kit-freshness は templates の内容変更に対し
kit の鮮度判定が advisory(既存 kit は bomdd.lock 凍結)。tools・hooks・.github diff 0。製品リポは次回 kit 再設置から反映。

## 3. 受入

- **V1**: 正本と写しの差分が ECO-063 の既知差分(注記ブロック+`{{METHOD}}` 解決)のみ(`diff` で実測)。**V2**: 60-change-order.md の検査官行に 2 欄が入る。**V3**: self-conformance 全 PASS・
  CI 緑・窓= 3 文書+台帳系。**V4**: 製造者較正のみ。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-069` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用実装(user DECIDE「B→C」)。baseline `764957c`= **confirmed** / 次番 069= **confirmed** / 織り込みの実在(playbook §3・f3974c9)= **confirmed** / 配布物の未反映= **confirmed**(実読)/
  凍結の非該当= **confirmed** / 同一ファイルへの進行中 ECO なし= **confirmed**。
- job ビュー: required_skills= `["preflight"]`・skills_missing= `[]`(order 生成後に出力)
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-11・同一 commit)

- 製造物: 3 文書(工程 5 に 2 項・写しに同文・検査官行に 2 欄)。
- **V1**= PASS(正本 vs 写しの diff は ECO-063 の既知 2 hunk〔冒頭注記・playbook 参照の相対化〕のみ — 実測 8 行= ECO-063 と同値)/ **V2**= PASS(検査官行)/ **V3**= self-conformance・CI は §5。

## 5. 受入完了の記入予定(accept commit で書き換え)

- (accept commit で記入: V3 の self-conformance・CI・窓閉鎖)
- 製造中の実測(正直記載): 起票+fix commit の直前、入口 `bomdd-run.py ECO-069` が **STOP job:LEDGER_INCONSISTENT → ledger-owner** を返し commit を止めた —
  本節の見出しを先に「クローズ(verified…)」と書いていたため、job 射影がクローズ節と読み register= implemented と矛盾した(F0 検出の実運用 1 例目・是正前に機構が止めた)。
  見出しを「クローズ予定(… verified に書き換え)」に直したが **2 回目も STOP**(見出し行に verified 語が残っていた= 検出は「## N. クローズ」+ verified 語)→ 見出しから両語を外して 3 回目で ADVANCE。
