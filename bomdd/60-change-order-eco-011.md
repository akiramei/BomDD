# ECO-011 — 台帳の重複キーによる情報損失(ECO-009 フィールドの ECO-010 への誤帰属+verified 3 件の verification 欄未更新)

> 状態: **起票のみ(裁定・製造前)**。是正/検証は未着手 — gate(製造承認)で停止中。

## 起票(2026-07-16)

- 出典: **保存形式レビュー(2026-07-16)所見1**(最優先所見)。`bomdd/60-change-register.yaml` の
  ECO-010 ブロックに `summary` が 2 つ(231/239 行)・`verification` が 2 つ(238/247 行)存在し、
  PyYAML `safe_load` は重複キーをエラーにせず**後勝ちで上書き**する。現行の自己適合検査
  (C1=構文パース・C3=台帳パース)はパース成功のみを見るため**全 PASS のまま情報損失**。
- 根因(当セッションの git 履歴解析で特定):
  1. `fba7f1b`(transfer-04 還元)が **ECO-009 の正規フィールドとして** summary/verification を起票
     (`git show fba7f1b` で ECO-009 エントリ内にあることを確認済み)。
  2. `0fbc34a`(ECO-010 起票)が **ECO-009 の diff_audit と summary の間**に ECO-010 エントリを
     挿入したため、ECO-009 の summary/verification が ECO-010 ブロック内に孤立。
  3. その後 ECO-010 自身の summary/verification が追記され(製造・検証時)、重複キーが成立。
- 実害(safe_load 意味論):
  - ECO-010 の正本 summary(AGENTS.md 入口の根因記述)が transfer-04 文面で上書き=**誤帰属**。
  - ECO-009 は summary/verification を**持たない**エントリになっている(欠落)。
- 付随所見(同型全数走査で発見・本 ECO スコープに含める): accept(verified 化)コミット
  (bc27115 / 588af6d / b586cea)は status と diff_audit.head の 2 行のみ書き換える様式だったため、
  **verified 3 件(ECO-008/009/010)の verification 欄が「(製造前 — 未実施)」のまま残存**
  (status: verified と矛盾)。実検証記録は accept コミットメッセージと各 order の検証節に現存。
- 同型全数走査(2026-07-16 実測): 重複キー検出つき厳格ローダーで bomdd/+method/ の全 YAML を
  走査 → 重複キーは**本 1 件のみ**。verification プレースホルダ残存は verified エントリ中
  **ECO-008/009/010 の 3 件のみ**(ECO-001〜007 は実検証記録あり)。

## 裁定

- **未(gate 承認待ち)**。以下は証拠に基づく裁定案 — gate で採否。
- **裁定案(帰属先)**: 239〜247 行の summary/verification は **ECO-009 ブロックへ復帰**
  (`fba7f1b` の原型どおり)。根拠= git 履歴が一次証拠(上記根因 1)。

### 是正方針案(製造前・凍結前の草案)

1. 239〜247 行(transfer-04 N=3 summary+verification)を ECO-009 ブロック末尾
   (diff_audit の後)へ移動。
2. verification 欄の実記録復元(3 件):
   - ECO-008: 変異 A(tool 退避= C5a FAIL)/B(空 suites= C9 FAIL)/B2(doc None)+--dotnet 基線
     (bc27115・詳細は order 参照)。
   - ECO-009: 治具 13 項目全 PASS(git 不在/不完全 kit/部分集合/CAD)+予測部分不的中の正直記載
     (588af6d・詳細は order 参照)。
   - ECO-010: 治具 10 項目全 PASS(3 経路+CAD 版+fail-safe+変異 2 種)+C4 恒久収載
     (b586cea・詳細は order 参照)。
3. クローズ条件: 厳格ローダーで bomdd/+method/ 全 YAML の重複キー 0 件・verified エントリの
   verification プレースホルダ 0 件・safe_load 意味論上の変化が予測(ECO-010.summary 復元+
   ECO-009 フィールド出現)と一致すること(前後の safe_load 差分で機械確認)。

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `bomdd/60-change-register.yaml` 以外 diff ゼロ。移動・更新は ECO-008/009/010 の
  summary/verification のみ — 全エントリの id/date/status/source/order_ref/affected_refs/
  diff_audit は不変。ECO-001〜007 はバイト不変。
- 順序依存: **ECO-012(C1 厳格化)の gate は本 ECO 適用後** — 是正前の台帳が ECO-012 の
  天然の陽性対照(是正前 FAIL/是正後 PASS の等価証明に使える)。

## 是正

- (未着手)

## 検証

- (未実施)

## 教訓(還元候補 — lesson-promote 経由)

- **構文 PASS は情報保存 PASS を含意しない**(寛容パーサの既定挙動=重複キー後勝ちは保存正本の
  沈黙損失面)— transfer-04 4類型「存在 vs 完全性」の再演を、検査転移の設計外である通常の
  外部レビューが検出した(OBS-20260716-01)。
- **accept 段の部分更新様式**(status/head のみ書き換え・verification 素通り)はクローズ書式の
  完了条件が field 単位で検査されていないことの現れ(OBS-20260716-02)。
- **台帳編集後の帰属の機械検証**: エントリ挿入位置の誤りが「別 ECO への帰属変化」として現れた —
  OBS-20260711-03(台帳の ID 帰属の機械検証)の 2 例目。
