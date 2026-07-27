# ECO-022 — 工程 donor intake 雛形の標準装備(OBS-20260725-01 の 2 例目判定= intake のみ昇格)

> 状態: **verified(2026-07-27)**。gate ① 承認(還元レビューで採択)・fix= 8fd9c77・
> V1〜V3 PASS・self-conformance 全 PASS(C1= 20 件)・窓閉鎖 baseline 9452936 → head 8fd9c77。
> CI 緑は push 後に実測(accept 後の還元 push と同一 run で確認 — 結果は register 系列の
> push 記録参照)。

## 起票(2026-07-27)

### 背景(判定データ)

OBS-20260725-01 が事前指定していた「工程調達の完全様式の標準成果物化は 2 例目で判定する」が
MoviePad 実運用初回(2 例目)で到達。判定データ:

- 1 例目(ViewTube・手動移植): 完全様式 9 ファイル(donor intake / reuse map / process BOM /
  IQ-OQ-PQ / First Article ほか)を手で作成。
- 2 例目(MoviePad・kit 標準経路): bomdd-init が調達・版固定(bomdd.lock= revision+
  manifest sha256)・設置・初回 IQ/OQ を**装置で自動化**。手で書いたのは
  **donor intake 1 ファイルのみ**(工程/製品 donor の分離登録・delta 記録・line readiness 記録 —
  装置が書けない「裁定と由来」)。

### 裁定(レビュー 2026-07-27)

**intake 雛形のみ** `method/templates/process-core/` へ標準装備する。完全セット(reuse map /
process BOM / First Article ほか)は**見送り** — 装置が不要化したため 3 例目まで knowledge 参照
(ViewTube 実物一式)のまま。早すぎる形式化の回避(B3 先例)と、実測 2 例で収斂した部分だけを
昇格する原則の適用。

## 内容

1. `method/templates/process-core/process-donor-intake.yaml` を新設 — MoviePad 実物
   (2 例目)を placeholder 化した雛形。YAML として厳格パース可能な形で置く(C1 対象)。
2. `method/onboarding/ai-onboarding-pack.md` §11 の「標準成果物化は 2 例目で判定する」文言を
   判定結果へ更新(雛形参照+完全セットは 3 例目で再判定)。

## スコープ外(明示)

- bomdd-init による intake の自動設置・自動生成(intake は装置が書けない裁定文書 —
  雛形はテンプレ置き場と kit 同梱で参照可能になれば足りる。自動化の要否は必要の実測後)。
- 完全セット(reuse map / process BOM / First Article)のテンプレ化(3 例目で再判定)。
- ViewTube・MoviePad の既存 intake の書き換え(実物は証拠正本 — 遡及不変)。

## 受入基準(事前登録 — 製造前に凍結する)

- 雛形が YAML 厳格パースする(self-conformance C1 が対象に含める — 件数 19→20)。
- **雛形→実物の被覆**: MoviePad 実物 intake の全トップレベルキー(bomdd / process_donor /
  product_donor / deltas / line_readiness / intake_checks / verification)が雛形に存在する。
- onboarding §11 が判定結果を反映し、雛形の実在パスを参照する(空ポインタなし)。
- self-conformance 全 PASS+**push 後 CI 緑の実測**(ECO-020 規律)。

## 影響分析(製造前予測 — 未凍結)

- 新設 1 ファイル+onboarding §11 の文言更新のみ。既存テンプレ・治具・bomdd-init の挙動は不変
  (bomdd-init は本雛形を特別扱いしない — kit 同梱物として配布されるのみ)。
- C1 の件数が 19→20 に変わる(件数は pin されていないため判定不変)。

## 是正(2026-07-27)

1. 雛形新設(MoviePad 実物の placeholder 化・様式出典と記入指針をコメントで併記)。
2. onboarding §11 更新(判定結果+雛形参照+3 例目再判定の予約)。

## 検証(2026-07-27・受入基準=起票時凍結分)

- V1(パース): 雛形が PyYAML 厳格パース PASS・self-conformance C1 = 20 件全 PASS。
- V2(被覆): MoviePad 実物のトップレベルキー 7 種すべてが雛形に存在(機械突合)。
- V3(参照): onboarding §11 の雛形パスが実在(空ポインタなし)。
- V4: self-conformance 全 PASS+CI 緑(accept 節に記録)。
