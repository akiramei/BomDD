# product-profile — 製品リポ用 運用プロファイル テンプレ

`tools(method/tools)/bomdd-init.py` が新規プロダクト/CAD リポを生成するときに、
プレースホルダを置換して配置するテンプレ群。**単一正本はここ**(生成先での改変は
その製品の運用プロファイルとして自由だが、一般形の改善はここへ還元する)。

| ファイル | 配置先 | 役割 |
|---|---|---|
| CLAUDE.product.md | `<product>/CLAUDE.md` | 製品リポの導線(全セッション自動ロード) |
| CLAUDE.cad.md | `<cad>/CLAUDE.md` | CAD リポの導線(役割境界: 実装しない) |
| change-management.md | `<product>/bomdd/change-management.md` | 変更管理の運用プロファイル(R1-R6・シナリオ別経路) |
| skills/bomdd-next.md | `<product>/.claude/skills/bomdd-next/SKILL.md` | フォワード Phase 0〜6 の現在地判定と次の一手 |
| skills/eco-file.md 他3本 | `<product>/.claude/skills/<name>/SKILL.md` | 納品後の変更管理入口(起票/是正/受入/脆弱性) |
| cad/02_mock_fidelity_policy.md | `<cad>/docs/` | 権威宣言(乖離時は CAD が正) |
| cad/review_points.md | `<cad>/docs/` | 裁定台帳(空の書式) |

プレースホルダ: `{{PRODUCT}}`(製品リポ名) / `{{CAD}}`(CAD リポ名) /
`{{METHOD}}`(BomDD 方法論リポの絶対パス) / `{{DATE}}`(生成日)。

出自: ViewPrism2 の実運用プロファイル(ECO-038/039 ケーススタディ)からの一般化(2026-07-04)。
