# ECO-023 — --skills-only 設置経路が空ポインタ入口を作る(参照と被参照の設置単位分離+参照実在の検査ゼロ面)

> 状態: **製造完了・検証済み(2026-07-27)**。gate ① 承認(裁定 3 点は推奨採択)・
> baseline= 起票コミット 540d59e。
> 発見経緯: MoviePad 初製造 ECO-001(R3 送付 — 製品側は是正済み・本 ECO は harness 側の根治)。

## 裁定(gate ① — 2026-07-27)

**製造承認(maintainer — 「製造承認します、裁定 3 点は推奨どおりで」)**: ①不在正本は
**設置**(不在時のみ・既存保持)②**IQ-08 追加**(受入で既定/adapt 両 profile の全対照回帰を
再実行)③MoviePad への**遡及不要**(IQ-08 適用の再適格性確認のみ — 正本治具の直接実行で行い、
設置物は書き換えない)。

## 是正(2026-07-27)

1. **不在正本の設置**: --skills-only が `CLAUDE.md`・`bomdd/change-management.md` を
   **不在時のみ** render(既存テンプレ流用 — 新規テンプレ作成は不要だった。既存は保持)。
2. **CAD 参照の実在検査**: `cad_ref()` を新設 — CAD リポが実在すれば md リンク+裁定優先の
   方針文・実在しなければ「**未登録** — 設置後に記入」の明示プレースホルダ+設置ログ警告
   (既定名 `<name>UI` を実在確認なしに書かない)。scaffold 経路も同関数を共有
   (`{{CAD_REF}}` 変数化 — 単一解釈関数)。
3. **権威方針の中立化(6 テンプレ)**: 「乖離時は常に CAD が正」の断定を
   「**製品の裁定台帳の個別裁定が最優先** — 未裁定の面は fidelity policy の既定に従う」へ
   (AGENTS.product / CLAUDE.product / change-management / AGENTS.cad / CLAUDE.cad /
   02_mock_fidelity_policy §P2)。スコープ注記: skills 内(eco-file の診断分岐等)の CAD 前提
   記述は入口でないため今回対象外 — 観測として還元へ。
4. **IQ-08 新設**: 入口(AGENTS.md)の相対 markdown リンク全数の実在検査。AGENTS.md 不在も
   FAIL。対象は機械判定可能な md リンクのみ(散文中のパス文字列は契約にしない)。

## 検証(2026-07-27・受入基準=起票時凍結分)

- **V1(陽性対照)**: CAD・CLAUDE.md・change-management.md を持たない既存リポへ
  --skills-only 設置 → 警告発火+不在時設置 2 件+CAD 参照は「未登録」プレースホルダ
  (空ポインタ 0)+**IQ-08 PASS(相対リンク 11 件すべて実在)**+line ready。
- **V2(負例)**: 設置後に `bomdd/change-management.md` を削除 → **IQ-08 FAIL
  (参照不在 1 件を明示)・「製造を開始しない」**(無音 PASS しない)。
- **V3(回帰・scaffold)**: fresh GUI scaffold(CAD リポ同時生成)→ IQ-08 相対リンク 12 件
  すべて実在・qualification 全 PASS。
- **V4(既存保持)**: 再実行で AGENTS.md/CLAUDE.md/change-management.md/設備/kit の
  5 面すべて「既存のため保持」。
- **MoviePad 再適格(裁定 3)**: 正本治具の直接実行(設置物は不変)で IQ-08 = 相対リンク
  15 件すべて実在・OQ-00 probe=Controls/・**PASS — line ready**(adapt profile の全対照回帰を
  兼ねる)。
- self-conformance 全 PASS(C4= scaffold 参照実在の回帰・C11= IQ-08 を含む scaffold 適格性)。
- CI 緑は push 後に実測(accept 節へ記録)。

## 起票(2026-07-27)

### 事実(実測 — MoviePad 2026-07-27)

- `bomdd-init --skills-only` が設置した AGENTS.md に**空ポインタ 3 件**:
  1. `../MoviePadUI` — CAD リポ名の既定 `<name>UI` を**実在確認なしに仮定**して書く
     (bomdd-init.py L303/L335: `args.cad_name or f"{args.name}UI"`)。
  2. `bomdd/change-management.md` — scaffold 経路でのみ生成される文書。skills-only は
     **設置しないのに参照だけ設置**する。
  3. `CLAUDE.md` — 同上(テンプレ `CLAUDE.product.md` は存在するが skills-only は設置しない)。
- 加えてテンプレ既定の権威方針「乖離時は常に CAD が正」が、製品の裁定台帳
  (MoviePad 37-ui-rulings UQ-0016 = 実機優先推定)と**矛盾したまま設置**された。
- 製品側は MoviePad ECO-001 で是正済み(155adbd → 3efd9a6 → b9732f4・golden 承認済み)。

### 見逃しの構造

1. **参照と被参照の設置単位が分離している**: AGENTS テンプレは scaffold 文脈(CAD リポ・
   change-management.md・CLAUDE.md が同時生成される)を前提に書かれ、ECO-010 が 3 経路生成を
   足したとき、skills-only 経路は前提物なしで参照だけを設置する形になった。
2. **検査ゼロ面**: C4 の参照実在検査(ECO-010)は scaffold 経路の生成物のみ。IQ(line
   readiness)条件 1「入口から全 workflow へ到達可能」は skill 表の到達のみ実測し、入口が
   参照する**関連正本の実在は未検査**。設置三要素の起動経路検査はあるが、入口文書の
   リンク健全性はどの検査面にも属していない。
3. **既定値が裁定を上書きする**: テンプレの一般既定(CAD が正)が、製品固有の裁定
   (実機優先)を無言で覆す誤誘導源になる — 既定値系教訓群(EXP-20260714-04 ほか)の入口文書版。

## 是正方針案(製造前・凍結前の草案)

1. **不在正本の設置**: skills-only 設置時、`CLAUDE.md`(アダプタ)と
   `bomdd/change-management.md`(最小正本 — installed profile の 2 状態と一致する内容)を
   **不在時のみ**設置する(register 追設と同じ様式・既存は保持)。
2. **CAD 参照の実在検査**: CAD リポ(または リポ内 CAD)の実在を確認できない場合、既定名を
   仮定して書かず「CAD 正典の所在は設置後に記入する」**明示プレースホルダ**+設置ログ警告。
3. **権威方針文言の中立化**: テンプレから「乖離時は常に CAD が正」の断定を外し、
   「乖離解決の優先方針は製品の裁定台帳に従う(未裁定ならここで宣言する)」へ。
4. **検査面の追加(IQ-08)**: line readiness に「入口(AGENTS.md)の相対参照 全数の実在」を
   追加(条件 1 の精密化: 到達可能 ⊇ 参照実在)。

## 裁定を要する設計点(gate ①)

1. 不在正本の扱い: **設置(推奨・不在時のみ)** vs 参照除去。MoviePad ECO-001 の実測では
   新設が正解だった(eco-fix が CLAUDE.md の機械受入コマンドを参照する等、正本群は運用上必要)。
2. IQ-08 追加の可否: **追加を推奨**。qualification は ECO-021 で是正したばかり — 対照追加は
   同治具への連続変更になるため、受入で既定/adapt 両 profile の全対照回帰を再実行する。
3. 既設リポ(MoviePad)への遡及: **不要(推奨)** — ECO-001 で是正済み。IQ-08 適用の
   再適格性確認のみ実施(PASS 見込み)。

## 受入基準(事前登録 — 製造前に凍結する)

- **陽性対照(今回の見逃しを直接塞ぐ)**: CAD・change-management.md・CLAUDE.md を持たない
  既存リポへ --skills-only 設置 → **空ポインタ 0**(不在時設置+明示プレースホルダ)+
  IQ-08 PASS。
- **負例**: 設置後に参照先を 1 つ削除 → IQ-08 FAIL(明示・無音 PASS しない)。
- **回帰**: scaffold 経路(fresh scaffold)で C4 不変・qualification 全対照 PASS(既定
  profile)。adapt profile(MoviePad 実物)でも全対照 PASS。既存ファイルがあるリポへの
  設置で**既存が保持される**こと(上書きしない)。
- **MoviePad 再適格**: IQ-08 を含む qualification が PASS(ECO-001 是正済みのため)。
- self-conformance 全 PASS+**push 後 CI 緑の実測**(ECO-020 規律)。

## 影響分析(製造前予測 — 未凍結)

- 変更: `method/tools/bomdd-init.py`(skills-only 設置系)+
  `method/templates/product-profile/AGENTS.product.md`(文言中立化)+最小テンプレの追加
  (change-management 最小正本 — 置き場は製造時に確定・既存 CLAUDE.product.md は流用可否を
  製造時判定)+ `method/templates/process-core/tools/process-qualification.py`(IQ-08)。
- scaffold 経路の生成物は**文言変更を除き不変**(C4 で回帰確認)。C11 は IQ-08 追加で
  対照数が変わる — 判定構造は不変の予測。

## スコープ外(明示)

- MoviePad の入口文書の再変更(ECO-001 で完結・遡及しない)。
- AGENTS テンプレの全面改稿(空ポインタと方針断定の是正のみ — 構成は変えない)。
- kit 設置済みリポへの一括再配布(更新は手動 — ECO-021 で記録済みの経路)。
