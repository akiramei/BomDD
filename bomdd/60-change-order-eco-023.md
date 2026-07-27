# ECO-023 — --skills-only 設置経路が空ポインタ入口を作る(参照と被参照の設置単位分離+参照実在の検査ゼロ面)

> 状態: **filed(2026-07-27)**。gate ①(製造承認+裁定 3 点)待ち。
> 発見経緯: MoviePad 初製造 ECO-001(R3 送付 — 製品側は是正済み・本 ECO は harness 側の根治)。

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
