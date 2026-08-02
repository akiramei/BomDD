# ECO-026 — kit 鮮度検査・リンク切れ検査の実装(ECO-004/006 残宿題の消化)

> 状態: **製造完了・検証済み(2026-08-02)**。gate ① 承認= 2026-08-02 maintainer 採択
> 「本文は触らない・台帳の棚卸しと裁定済み残宿題を消化する」(2026-08-02 台帳棚卸し工程節・
> to-ECO 2 件のうちの 1 件)。出典= EXP-20260710-09(2026-07-10 harness 還元・教訓 8)。
> baseline= 6056499(起票 commit)。

## 製造記録(2026-08-02)

1. **first-run が実所見 15 件を検出(全面突合イベントの再演 — L1719 知見どおり)**:
   設置先文脈の予備測定で、phase テンプレ 3 ファイル(51-cheat-log / 61-impact-analysis /
   README)の方法論本文への `../` 直リンク 15 件が **kit 同梱化(ECO-004)以降すべての
   設置先で死んでいた**ことが判明(bomdd/ 配下に設置されると `../` は製品ルートを指す)。
   是正= 設置先文脈で解決する `../bomdd-kit/method/...` へ全 15 リンクを置換(バイト置換・
   表現保存 — OBS-20260727-24)。**影響なし予測の部分不的中を正直記載**: 「method/templates/
   は diff ゼロ」は不的中(検出対象の欠陥がまさにそこにあった)。bomdd-init・製品リポ生成
   機構は予測どおり diff ゼロ。
2. **境界裁定の精密化(起票時裁定 3 の端点修正 — OBS-20260727-05 の適用)**: C13a の除外は
   product-profile でなく **method/templates/ 全体**へ変更。理由= phase テンプレも参照文脈は
   設置先であり(1 の実測が証明)、リポ文脈で検査すると「たまたま解決する」ことが欠陥
   (設置先で死ぬリンク)をマスクしていた。除外分の設置形は C13b が全数検証する。
   既知限界(宣言+掃射手段): scaffold が設置しないテンプレ(ui-mock-extraction/ 等)の
   リンクは自動検査外 — 設置経路へ載った時点で C13b が自動被覆。bomdd-kit/ 内部は凍結写し
   につき非規範・検査対象外。
3. **製造中の欠陥 1 件(検査が検出・即是正)**: kit-freshness 初版が cp932 コンソール下で
   em-dash を print できず UnicodeEncodeError で自壊(C14 の STALE/UNKNOWN 対照が検出)。
   是正= stdout/stderr の utf-8 reconfigure を治具自身に内蔵 — **OBS-20260727-10「検査は
   自分の前提を自分で満たす」の再演**(環境前提= コンソールエンコーディング)。

## 検証(2026-08-02・受入基準=起票時凍結分)

- **V1(実 corpus PASS)**: C13 PASS — リポ文脈 105 files/193 links 不在 0・設置先文脈
  24 files/70 links 不在 0・陽性対照 True。
- **V2(陽性対照)**: (a) FINDINGS.md へ壊れリンク注入 → **FAIL**(不在 1 件をファイル名+
  ターゲットつきで列挙)/ (b) 復元 → **PASS** / (c) 空 corpus(md 列挙 0 の合成 ROOT)→
  **FAIL**(正直記載: 発火点は列挙ガードでなく scaffold 段の bomdd-init 不在 — fail-closed は
  成立・発火位置が受入文言と異なることを記録)。
- **V3(C14 全分岐)**: 7/7 — FRESH(exit 0)/ STALE(exit 0・behind=1)/ UNKNOWN
  (exit 3・ORIGIN_MISSING)/ TAMPERED(exit 1・改変検出)/ 余剰ファイル(exit 1・
  fail-closed 双方向)/ 入力不正(exit 2・LOCK_MISSING)/ 実 scaffold の最初の正常後続取引
  (exit 0)— **control-plan 正本化前検査 (d) の初適用**(強制規則でなく検査治具だが、
  導入 ECO 内で「使われる形の一巡+時間軸の最初の取引」を実測した)。
- **V4(回帰)**: self-conformance **C1〜C14 全 PASS**(exit 0)。
- **V5(CI)**: push 後に追記。
- 効果の限界(事前登録どおり): 鮮度検査は乖離の可視化であり設備更新を自動化しない
  (EXP-20260727-19 が追跡)。origin 不在環境(CI 等)では鮮度は UNKNOWN(fail-open にしない)。

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
