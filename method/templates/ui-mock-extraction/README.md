# UI Mock Extraction Templates

HTML / JavaScript / CSS で作られた実行可能 UI モックから、UI-IR / UI-BOM / trace map を生成するためのテンプレート。

この一式は E-BOM の前段で使う。正式品番は採番せず、`TMP-UI-*` の仮品番で候補を追跡する。

| ファイル | 役割 |
|---|---|
| [ui-ir.json](ui-ir.json) | UI モックから抽出した観測・追跡用の中間表現 |
| [ui-bom.json](ui-bom.json) | UI-IR から BOM 対象だけを昇格した候補部品表 |
| [ui-trace-map.json](ui-trace-map.json) | HTML selector / UI-IR / UI-BOM / E-BOM 候補の対応 |
| [design-intent.md](design-intent.md) | DESIGN DIRECTION / 原則 / COLOR・TYPE・ROW 等の設計意図 |
| [extraction-report.md](extraction-report.md) | 抽出概要、BOM 対象理由、対象外理由、E-BOM 連携候補 |
| [unresolved-questions.md](unresolved-questions.md) | 仕様・UI 設計・E-BOM 昇格前の確認事項 |

推奨配置:

```
bomdd/
  ui/
    ui-ir.json
    ui-bom.json
    ui-trace-map.json
    extraction-report.md
    unresolved-questions.md
```

関連:

- 方法論: [../../ui-ir-ui-bom.md](../../ui-ir-ui-bom.md)
- AI 抽出プロンプト: [../../prompts/ui-mock-to-ui-bom.md](../../prompts/ui-mock-to-ui-bom.md)
- E-BOM テンプレート: [../30-ebom.yaml](../30-ebom.yaml)
- Design System BOM テンプレート: [../35-design-system-bom.yaml](../35-design-system-bom.yaml)
- Visual Gap Analysis テンプレート: [../43-visual-gap-analysis.md](../43-visual-gap-analysis.md)
