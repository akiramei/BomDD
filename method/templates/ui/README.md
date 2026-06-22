# UI テンプレート入口

このディレクトリは、対象プロジェクトの `bomdd/ui/` を作るときの入口である。既存の詳細テンプレートは `method/templates/ui-mock-extraction/` にあるため、実プロジェクトでは必要なファイルを `bomdd/ui/<screen-or-flow>/` へコピーして使う。

## 標準配置

```text
bomdd/ui/
  mock/
    <人間が置く HTML/Figma export/スクリーンショット/注釈>
  <screen-or-flow>/
    ui-ir.json
    ui-bom.json
    ui-trace-map.json
    extraction-report.md
    design-intent.md
    unresolved-questions.md
```

## AI が行うこと

1. `bomdd/ui/mock/` の原典を読む。
2. 画面、領域、操作、入力、状態、表示要素を抽出する。
3. `ui-ir.json` に観測中間表現を書く。
4. BOM 対象だけを `ui-bom.json` に昇格する。
5. selector、UI id、UI-BOM、E-BOM 候補を `ui-trace-map.json` で接続する。
6. 不明点を `unresolved-questions.md` に残す。
7. UI-BOM 候補を `20-spec.md`、`30-ebom.yaml`、`33-control-plan.yaml` へ昇格する。

## ID 規則

| 種別 | 形式 | 例 |
|---|---|---|
| screen | `screen.<name>` | `screen.checkout` |
| region | `region.<name>` | `region.checkout.summary` |
| component | `component.<name>` | `component.total-card` |
| action | `action.<target>.<verb>` | `action.cart.submit` |
| input | `input.<target>.<field>` | `input.customer.email` |
| state | `state.<target>.<state>` | `state.cart.empty` |
| temp part | `TMP-UI-<KIND>-NNNN` | `TMP-UI-CMP-0001` |
| display contract | `DC-<SCREEN>-NNN` | `DC-CHECKOUT-001` |
| display element | `DE-<SCREEN>-NNN` | `DE-CHECKOUT-003` |

## E-BOM へ昇格する基準

昇格する:

- 要求、表示契約、業務操作、入力検証、状態、保守対象に接続できる。
- Control Plan で存在、意味、状態、操作を検査できる。
- 変更時の影響分析単位として意味がある。
- Card / CTA / Chip / Badge / IconButton など UI-CAD の design language を構成する。

昇格しない:

- 余白調整だけの wrapper。
- 意味を持たない `div` / `span`。
- 単発の border、shadow、radius。必要なら Design System BOM または K-BOM の token として扱う。

## TraceLink 例

```json
{
  "trace_id": "TL-UI-E-001",
  "from": "TMP-UI-CMP-0001",
  "to": "E-CHECKOUT-SUMMARY-001",
  "relation": "satisfies",
  "evidence": "bomdd/ui/checkout/ui-trace-map.json",
  "status": "active"
}
```

## PLM-ready checklist

- `ui-ir.json`、`ui-bom.json`、`ui-trace-map.json` が揃っている。
- UI-BOM item は `tempPartNo`、`kind`、`sourceRef`、`traceRefs` を持つ。
- 表示契約へ昇格する要素は `DC-*` / `DE-*` を持つ。
- 推測した仕様は `unresolved-questions.md` に残す。
- UI-CAD の design parts は `35-design-system-bom.yaml`、E-BOM、K-BOM、Control Plan へ接続する。
