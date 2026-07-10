# ECO-003 — impact-retrospective の unmapped 過少報告(fail-open 集計)+影響フィールド一括判定

## 起票(2026-07-10)

- 出典: メンバー外部レビュー所見3(P1)。「M-BOM へ写像できない実変更を `unmapped` に数えるが、
  概要の `ecos_with_real_under` と `real_under_files` に含めない。『未知の変更先があるのに
  under-inclusion 0』という見出しが成立する。影響フィールドを台帳全体で一度だけ選択するため、
  `impacted_bom` と `affected_refs` が混在すると片方が黙って欠測になる」。
- 再現(是正前・実測 2026-07-10):
  - **BomDD-Plm でレビューの攻撃シナリオが実在**: ECO-003 は unmapped 3 件(oracle/ 治具データ)・
    under 0 → 見出しでは「under なし」に計上。register 全体では unmapped 76 件
    (ECO-001: 22 / 002: 34 / 003: 3 / 004: 5 / 005: 12)が見出し外。
  - フィールド混在: ViewPrism2(56 ECO)・Plm とも現時点で混在なし — **潜在欠陥**(未発火)。
  - fail-open の同族(git returncode 未確認)も 3 箇所で確認(ECO-002 order の横展開予告どおり)。

## 裁定

- ユーザー承認(2026-07-10)「進めて」— 是正順序 2 番(研究数値への波及確認つき)。
- 是正方針: **採点規約 v2 の宣言つき変更**。規約 v1 の測定定義(1〜4: 対象選定・予測写像・
  実 diff・unit 帰属)は不変。変えるのは (a) 見出し集計= unmapped を fail-closed の under として
  `ecos_with_real_under`/`real_under_files` に算入(hub_concentration は unit 帰属が定義できる
  mapped のみ)(b) 影響フィールドの ECO 単位判定 (c) 読取り失敗の exit 2。
  **v1 数値は `summary.decomposition` で恒久再現可能**にする(過去測定との比較可能性の保存)。
  規約冒頭の「変更する場合は fork して宣言」は、fork でなく**同一ファイル内の版宣言(v1/v2 併記)**で
  満たす — ほぼ同一の複製は乖離債務になるため。

## 影響分析(製造前凍結)

- 影響なし予測: `method/tools/impact-retrospective.py` 以外は diff ゼロ。
  既存測定値(ViewPrism2/Plm の是正前出力)は decomposition で完全再現されること(反証可能)。

## 是正

1. 見出し= fail-closed(`under` ∪ `unmapped`)+ `summary.decomposition` に v1 内訳
   (`ecos_with_mapped_under`/`mapped_under_files`/`ecos_with_unmapped`/`unmapped_files`)。
2. 行データに `unmapped_files`(パス列挙 — 裁定・監査用)を追加。
3. `impact_decl(c)`: ECO ごとに impacted_bom → affected_refs の順で判定(--impact-field 指定時は固定)。
   出力の `field` を `fields_used`(ECO 数の内訳)へ置換。
4. `die()`+`git()` returncode 検査+register/M-BOM 読取り失敗の exit 2(ECO-002 と同族是正)。

## 検証(2026-07-10)

- **v1 再現(回帰)**: ViewPrism2(--test-unit M-HARNESS-015)= decomposition 12 ECO/65 files・
  hub_concentration 同一 / Plm = 4 ECO/35 files・hub 同一 — **是正前見出しと 3 項目とも完全一致**。
- **fail-closed 効果(陽性対照)**: Plm 見出し 4/5 → **5/5**・35 → **111 files**。
  ECO-003(unmapped のみの ECO)が見出しに現れることを確認 — レビューの攻撃シナリオが閉じた。
- **異常系**: 存在しないリポ → `測定不能: M-BOM の読取りに失敗` **exit 2**。
- 影響なし予測: 的中(diff は該当ファイルのみ)。

## 既発表データへの波及判定

- **scale-01(FINDINGS §9「実 under 55・14/16」)= 波及なし**。公表値は治具の生出力でなく
  **裁定済み 3 分解**(生 137 = test-only 74 + 写像未所有 8〔csproj/sln — 被覆ギャップとして
  52 に記録済み〕+ 実 under 55)であり、unmapped は黙殺でなく明示裁定されていた。
  さらに ViewPrism2 の現 M-BOM は ECO-035 で被覆ギャップ解消済み — 本日の再測定で
  unmapped 0(見出し不変 12/18・65)を確認。
- **Plm**: 見出しは変わる(4/5→5/5・35→111)が、これは公表値でなく「被覆ギャップ 2 例目」の
  52 候補記録の**定量精密化**(76 件の内訳= oracle/ 27・packages/ 43〔.map/.tsbuildinfo 等の
  生成物混在〕・.github/ 3・schemas/ 3)。Plm 側 52 への数値追記は Plm リポの作業として残す。

## 教訓(還元候補 — lesson-promote 経由)

- **集計の fail-open は測定定義が正しくても見出しで嘘をつく** — 「分解して残す」
  (observation-schema §6 の規律)は分解の**和が見出しと一致する**ことまで含めて初めて安全。
- 「凍結規約の変更は fork して宣言」は、集計層のみの変更では**同一ファイル内の版宣言+旧数値の
  恒久再現フィールド**の方が乖離債務を作らない(規約凍結の運用形 2 例目 — rule of three 待ち)。
- 治具の生成物除外(bin/obj)は言語生態系ごとに不足する(.map/.tsbuildinfo 等)—
  除外パターンの宣言化は F6(self-conformance)で検討。
