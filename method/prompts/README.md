# BomDD フェーズ実行プロンプト集

[bomdd-playbook-v1.md](../bomdd-playbook-v1.md) の各フェーズを Claude Code(または任意の AI アシスタント)で実行するための指示書。各ファイルをそのままセッションに貼る/読ませることで、設計者 AI がそのフェーズの手順と規律に従う。

| ファイル | フェーズ | ゲート |
|---|---|---|
| [phase0-charter.md](phase0-charter.md) | チャーター(工場構成・予算・役割の固定) | G0 固定項目完備 |
| [phase1-brainstorm.md](phase1-brainstorm.md) | ブレスト→要求台帳 | G1 根拠精度 |
| [phase2-spec.md](phase2-spec.md) | 仕様化 | G2 マルチリーダー監査 / G2' 測定可能性 |
| [ui-mock-coverage.md](ui-mock-coverage.md) | UIモック受入検査: 三層検査+復唱(candidate・§17。抽出より前・隔離実行) | スコープ十分の裁定(ゲート化は未裁定) |
| [ui-mock-refmodel.md](ui-mock-refmodel.md) | UIモック受入検査 層2.5: 参照概念モデル差分(candidate・§17.1。外→内・製品につき1回) | ヒアリング=①〜④裁定→台帳 |
| [ui-raw-to-candidates.md](ui-raw-to-candidates.md) | UIモック抽出 第1段: 意味候補+質問(candidate) | raw 全 interactable の会計(GU1) |
| [ui-apply-rulings-to-bom.md](ui-apply-rulings-to-bom.md) | UIモック抽出 第2段: 裁定反映→UI-BOM(candidate) | UI-CAD 裁定ゲート GU1–GU6(tools/ui-cad-gate.py) |
| [ui-mock-to-ui-bom.md](ui-mock-to-ui-bom.md) | UIモック抽出(**deprecated** 旧一発変換) | UI-IR / UI-BOM / trace map / 未解決事項 |
| [phase3-design.md](phase3-design.md) | BOM・工程設計 | G3 ドライラン |
| [phase4-manufacture.md](phase4-manufacture.md) | 製造(隔離ファクトリ) | 自己受入+ずる報告 |
| [phase5-accept.md](phase5-accept.md) | 受入・収束 | 未観測差分ゼロ+blocker ずるゼロ |
| (独立プロンプトなし — playbook §7 が正) | 引き渡し・保守(Phase 6) | G4 Closeout(playbook §7) |
| [phase7-change-order.md](phase7-change-order.md) | 変更オーダー(納品後の仕様変更・ECO) | 回帰ゼロ+変更受入通過 |

**実行手順の正典はこの prompts/ である**(運用方針 2026-06-10)。ただし規模既定(監査体数・工場数・ゲート要否)は playbook §11 テーラリングが上書きする(権限分離規則)。skill 化は forward-01 検証後の 2026-07 に **adapter 層**として追加済み — `tools/bomdd-init.py` が**製品リポ側**へスキル一式(`templates/product-profile/skills/`)を設置する。方法論リポ自体には `.claude/skills` を置かない(正典と adapter を分離)。
