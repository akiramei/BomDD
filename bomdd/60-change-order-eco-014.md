# ECO-014 — 正本↔派生↔テンプレの乖離検出検査(C10 新設 — 参照スキーマの派生同期検査)

> 状態: **起票のみ(裁定・製造前)**。是正/検証は未着手 — gate(製造承認)で停止中。
> **gate は ECO-013 適用後**(順序依存 — 現乖離が天然陽性対照。ECO-011→012 と同型の対)。
> **天然陽性対照(再実行可能・ハッシュ固定)**: `git show 71d6f5f:method/schemas/draft/bomdd-ref.draft.schema.json`
> = 是正前 Schema(uiId に domain 欠落)。C10 をこの内容に当てて FAIL、ECO-013 適用後に当てて
> PASS が是正と検査の等価証明になる。

## 起票(2026-07-16)

- 出典: **保存形式レビュー(2026-07-16)所見2 の同根**。README は「`id-grammar` と `ref-edges` が
  正本。JSON Schema はそこから導出された検査器向け表現」(§2)と宣言するが、**導出の同期を検査する
  機械がない** — 手管理の派生が無記録でズレる(実害= uiId の domain 欠落が検出されず残存・
  ECO-013 起票まで発見されなかった)。
- 方法論上の位置づけ: ECO-011/012 と同型の対(データ是正 → それを検出する検査)。「正本と派生の
  無記録乖離」は ECO-012 の「構文 PASS≠情報保存 PASS」と同じく、宣言(README の正本序列)が
  機械検査に裏付けられていない面。

## 裁定

- **未(gate 承認待ち)**。

### 是正方針案(製造前・凍結前の草案)

C10(schema-drift)を self-conformance fast tier へ新設:

1. **ID 層の機械突合**(起票時の全数走査スクリプトを恒久化):
   - `uiId`: Schema pattern = 正本 `families[prefix=ui-id].family_pattern`(文字列一致)
   - `tmpUiPartNo`: Schema の alternation 集合 = 正本 TMP-UI-* prefix 集合
   - `anyKnownId`: 正本の単純 prefix 全列挙が Schema の alternation に被覆される
   - `oracleCaseId`/`migrationCaseId`: 正本 S/M0 の family_pattern と文字列一致
   - 単純 prefix 家族の個別 def 被覆(^PREFIX- を持つ def の存在)
2. **構造層の三者突合**: ui-mock-extraction テンプレの実在キー ↔ ref-edges セレクタ起点 ↔
   Schema required — **二方言の判別込み**(ECO-013 裁定 a の判別キーで型を判別し、各方言が
   宣言に被覆されること。空振りセレクタ= FAIL)。
3. **陽性対照の常設**: inline の意図的乖離(正本 pattern の一部を欠いた偽 Schema 断片)を毎回
   検出確認してから走査(ECO-012 C1 と同じ様式・環境非依存 — shallow clone CI でも機能)。
4. **変異テスト(検証時)**:
   - 変異 A: Schema の uiId から任意の語を一時除去 → C10 FAIL
   - 変異 B: ref-edges のセレクタ起点を実在しないキーへ一時改変 → C10 FAIL(空振り検出)
   - 天然対照: 71d6f5f の是正前 Schema → FAIL / 現(ECO-013 適用後)→ PASS

## 影響分析(製造前予測 — 未凍結)

- 影響なし予測: `method/tools/self-conformance.py` 以外 diff ゼロ。既存 C1〜C9 の判定は不変。
  C10 は ECO-013 適用後の整合状態で PASS(適用前に導入すると uiId 乖離で FAIL =正しい検出だが、
  窓の分離のため ECO-013 先行とする)。
- exit code 体系(0/1/2)は不変。

## 是正

- (未着手)

## 検証

- (未実施)

## 教訓(還元候補 — lesson-promote 経由)

- **「正本と派生」の宣言は同期検査と対でのみ意味を持つ** — 正本序列を README に書いても、
  導出の同期を機械が検査しなければ派生は無記録でズレる(ECO-012「宣言された不変条件は
  機械検査に裏付ける」の参照スキーマ面への適用)。
