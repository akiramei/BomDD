# equip-03 protocol — claude-opus-5 の ECO 適用製造測定(**凍結版**)

- 凍結: 2026-08-02。[protocol-draft.md](protocol-draft.md) の gate ① 裁定済み確定版
  (draft は歴史的記録として保持・本書が正本)。以後、実行開始後に本文を変更しない
  (必要になった変更は逸脱として measurements へ正直記載)。
- gate ① 裁定(2026-08-02 maintainer・4 点とも確定):
  1. 題材= **Plm ECO-006(仮)「repo: 形パス参照の repo 不在を R-004 error でなく X-XREPO 系
     skip(info)へ」で確定**
  2. 影響分析(61 相当)の起草= **工場(Opus 5)スコープに含める**
  3. 別ベンダー独立検査(Codex fresh・read-only・情報遮断)= **入れる**
     (EXP-20260726-01 別ベンダー検査軸の 2 回目を兼ねる)
  4. M-BOM 写像被覆ギャップの便乗= **載せない**(候補記録どおり「次回 32-mbom 改訂時」まで待つ・
     測定解釈の単純性を優先)

## 1. 目的・測定 4 次元

draft §1 のとおり: ①影響範囲の抽出(under/over-inclusion — 工場起草の影響分析を
impact-retrospective+R-052 diff 監査で機械採点)②変更対象外の非破壊(既存オラクル・全テスト・
self-hosting lint・ViewPrism2 workspace 回帰)③BOM/as-built の同期 ④証拠を残して閉じる
(diff_audit baseline→head 窓)。

## 2. 比較セルと拘束

Plm eco_001(opus-4.8/sonnet-4.5= 27/27・27/27)・eco_002(同= 33/33・33/33)。
比較は工程指標のみ・率の統計判定なし・routing 根拠への使用禁止(equip-01 凍結裁定の継承)。

## 3. 実行手順(凍結)

1. **起票**(設計者側= 主観察者): Plm へ ECO-006 order を起票(change・裁定記録・受入基準・
   diff_audit baseline 宣言)。**入力固定(EXP-20260802-06 初適用)**: 起票 commit に対し
   input tag(`eco-006-input`)+expected_commit+**input_tree_hash**+凍結オラクル成果物 hash+
   prompt bundle sha256 を measurements へ記録。実行開始時の再解決値と不一致なら fail-closed。
2. **較正**(設計者側): X-XREPO 分岐のオラクル拡張を変更前個体で FAIL 確認(較正= 差分が変更
   断面のみであることの凍結)。オラクルはループ中不変。
3. **製造**(工場= claude-opus-5・Agent subagent・equip-02 と同一構成): 影響分析起草 → 製造 →
   自己受入 → as-built 起草。介入 0 原則・時間分解/トークン/3 カウンタ全記録。
   BOM/Control Plan 本体の変更提案は権限外(提案は報告に載せ人間承認へ)。
4. **機械受入**(合否の主証拠): 凍結オラクル全数+全テスト+self-hosting --eco error/warn 0+
   ViewPrism2 workspace 回帰。
5. **独立検査**: Codex fresh(read-only・情報遮断)による BOM・工程適合の敵対レビュー →
   全所見を真偽裁定・カウンタ記帳。
6. **裁定・クローズ**(人間): maintainer 採否+golden → verified → head アンカーで窓閉鎖 →
   measurements 確定・還元候補記帳。

## 4. 設備・記録様式

equip-02 と同一(ECO-028 様式): requested= Agent `model: "opus"` / resolved= self-reported
(unknown 規律)/ harness / 主観察者= claude-fable-5 / prompt bundle sha256 / 時間分解 /
トークン / 費用(unknown 可・推定禁止)/ 介入・差戻・範囲外。
二車線(OBS-20260802-07): 必須製造車線の合否は凍結受入のみ。自主拡張は別枠観測・救済に使わない。

## 5. 事前予測(反証可能な形で)

- H-e3-1: 機械受入は一発到達(eco_001/002 の opus-4.8/sonnet-4.5 と同値)。
- H-e3-2: 影響分析の under-inclusion にビルドキャッシュ系(tsbuildinfo 等)が出る
  (Plm ECO-004/005 で 2 例の同型 — 3 例目が出るか)。
- H-e3-3: 独立検査は機械受入通過後にも真正所見を出す(transfer-04/equip-01 X1 の再現)。
- 探索的観測(予測固定なし): 自主拡張の発生有無・cheat 報告の粒度。

## 6. 採らないもの

資格制度・routing 基準の導出なし/webapi-02 セル反復なし(draft §9 のとおり)。
