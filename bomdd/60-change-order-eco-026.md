# ECO-026 — kit 鮮度検査・リンク切れ検査の実装(ECO-004/006 残宿題の消化)

> 状態: **起票(2026-08-02)**。gate ① 承認= 2026-08-02 maintainer 採択
> 「本文は触らない・台帳の棚卸しと裁定済み残宿題を消化する」(2026-08-02 台帳棚卸し工程節・
> to-ECO 2 件のうちの 1 件)。出典= EXP-20260710-09(2026-07-10 harness 還元・教訓 8)。

## §1 症状(実測)

ECO-004/006 が自ら宣言した残宿題が 2 件、起票されないまま 3 週間滞留していた:

- **kit 鮮度の自己検査**(ECO-004 order L30「スコープ外(F6 へ): kit 鮮度の自己検査
  (lock の commit と方法論リポの乖離検出)」)— kit は意図的な凍結スナップショットだが、
  **凍結の乖離量を測る装置がない**。設置先は「どれだけ古いか」「改変されていないか」を
  機械で知る手段を持たない(EXP-20260727-19: 設備更新は手動 3 手順 — 更新の要否を
  可視化する測定器が前提)。
- **リンク切れ検査**(ECO-006 order L67「残宿題: リンク切れ検査(所見 6 の「リンク」は
  未収載)」)— C12(ECO-025)は自リポ入口 AGENTS.md の 9 リンクのみ。**method corpus 全体**
  (リポ直下 *.md+method/**/*.md)のリンク実在は未検査。

起票時予備測定(読み取り専用・2026-08-02): リポ文脈の相対リンク 276 件中「解決不能」15 件 —
**全件が `method/templates/product-profile/` 配下**であり、これらは設置先(製品リポ)文脈で
解決されるテンプレリンク= リポ文脈で検査すると全て誤検出になる。→ 検査は**二文脈設計**が必要
(リポ文脈と設置先文脈を別々に張る。単一文脈の lint は 15 件の誤 FAIL か、除外による無被覆の
どちらかを生む)。

## 裁定(gate ① — 2026-08-02)

maintainer 採択「裁定済み残宿題を消化する」を製造承認とする。設計裁定(起票時確定):

1. **鮮度は advisory・改変は defect**: kit の凍結は設計(ECO-004)であり、STALE 自体は
   不適合ではない(更新の要否は設置先の裁定)。一方 manifest との乖離(TAMPERED)は
   不適合。exit 契約に反映する。
2. **判定は 4 値+理由コード**(playbook §13): FRESH / STALE / TAMPERED / UNKNOWN。
   UNKNOWN(origin 不達・commit 不明)を FRESH へ丸めない。
3. **リンク検査は二文脈**: (a) リポ文脈= リポ直下 *.md+method/**/*.md から
   product-profile テンプレを除外(除外根拠= 参照文脈が設置先。被覆対応= (b) が担う)
   (b) 設置先文脈= scaffold した一時製品リポ内の全 .md を設置先で解決(IQ-08 は入口
   AGENTS.md のみ — 全 md へ拡張)。
4. **First Article に「最初の正常後続取引」を含める**(control-plan 正本化前検査 (d) の
   初適用・2026-08-01 昇格): 新検査は本 ECO 内で実 corpus の正常一巡を実測し、accept
   commit 自体が新検査を通過する。台帳ゲート型でないため bootstrap 免除は不要(確認済み)。

## 是正方針

1. **`method/tools/kit-freshness.py` 新設** — 製品リポで実行(kit に同梱されて配布される)。
   入力= `bomdd.lock`(method.origin_path/commit・kit.root/manifest/manifest_sha256)+
   `kit-manifest.json`。検査= ①integrity: manifest 全 entry の sha256 再計算+manifest に
   ない余剰ファイル検出(fail-closed 双方向)②freshness: origin 到達時に lock commit と
   origin HEAD の乖離(behind count)。
   exit 契約(silence §10 — 意味写像の明示): **0= 判定成功(FRESH または STALE)/
   1= TAMPERED / 2= 入力不正(lock・manifest 不在/パース不能)/ 3= UNKNOWN(origin 不達等・
   理由コード付き)**。
2. **self-conformance C13 新設(リンク実在・二文脈)** — 裁定 3 のとおり。除外=
   http(s)/mailto/#のみ/`{{`プレースホルダ。対象欠落チャレンジ(md 列挙 0 → FAIL)+
   陽性対照(壊れリンクの検出を実測)。
3. **self-conformance C14 新設(kit-freshness の対照実測)** — scaffold → FRESH(exit 0)/
   kit ファイル改変 → TAMPERED(exit 1)/ lock commit 偽装 → STALE(exit 0・表示に behind)/
   origin_path 不達化 → UNKNOWN(exit 3)— **4 値すべてを実測**してから正本化
   (control-plan「安全装置の較正は真の故障モードでの発動実測」・「検出器は実在標本で較正」)。

## 影響分析(製造前凍結)

- 変更ファイル= `method/tools/self-conformance.py`(C13/C14 追加のみ・C1〜C12 は不変)・
  `method/tools/kit-freshness.py`(新規)・台帳(register/order)。
- 影響なし予測= `method/templates/`・`method/tools/bomdd-init.py`・製品リポ生成物の内容は
  diff ゼロ(kit へは copytree 経由で新 tool が自動同梱されるが、これは既存機構の通常動作)。
  README スキル本数(C7)に影響なし(スキル追加なし)。
- リスク= C13 リポ文脈の first-run は全面突合イベント(L1719 知見)— 予備測定で
  テンプレ以外の破れ 0 件を確認済み(誤検出 15 件は二文脈設計で構造的に解消)。

## 受入基準(起票時凍結)

- V1: C13 実 corpus PASS(リポ文脈・設置先文脈とも解決不能 0 件)。
- V2: 陽性対照 — リポ文脈に壊れリンクを注入して FAIL・列挙 0 件で FAIL(対象欠落)を実測し、
  復元後 PASS(無音 PASS しない)。
- V3: C14 の 4 値実測(FRESH/TAMPERED/STALE/UNKNOWN の全分岐が期待 exit と一致)。
- V4: 回帰 = self-conformance C1〜C12 全 PASS。
- V5: CI 緑(対象 revision・push 後に結論確認)。
- 効果の限界(事前登録): 鮮度検査は乖離の**可視化**であり、設置先の設備更新(手動 3 手順)を
  自動化しない — 更新実施は EXP-20260727-19 が別途追跡する。
