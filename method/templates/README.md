# BomDD テンプレ一式(フォワード・モード)

[bomdd-playbook-v1.md](../bomdd-playbook-v1.md) の各フェーズ成果物のテンプレ。
YAML の語彙は v2 実証リポジトリ([BomDD-WebApi-Sample](https://github.com/akiramei/BomDD-WebApi-Sample) `bomdd/`、[BomDD-DistributedSaga-Sample](https://github.com/akiramei/BomDD-DistributedSaga-Sample))で実運用した形式をミラーしている。**JSON Schema ではない**(硬化は [schema-candidates-index.md](../schema-candidates-index.md) §5 の昇格条件を満たすまでしない)。

対象プロジェクトのリポジトリ直下に `bomdd/` を作り、コピーして埋める。

| 番号 | ファイル | フェーズ | 渡し先 |
|---|---|---|---|
| 00 | [00-charter.md](00-charter.md) | Phase 0 チャーター | 設計者 |
| 10 | [10-requirements.yaml](10-requirements.yaml) | Phase 1 要求台帳 | 設計者 |
| 20 | [20-spec.md](20-spec.md) | Phase 2 仕様書 | 設計者→**製造パッケージに含む** |
| UI | [ui-mock-extraction/](ui-mock-extraction/) | Phase 2–3 UIモック抽出(candidate) | 設計者(E-BOM 前段。工場へ渡す場合は20/30–34へ昇格後) |
| UI | [ui/README.md](ui/README.md) | Phase 2–3 UI標準配置 | 設計者(`bomdd/ui/` の入口) |
| DB | [db/schema-intent.md](db/schema-intent.md) | Phase 2–3 DB/永続化意図 | 設計者(E-BOM/M-BOM/Control Plan 前段) |
| 30 | [30-ebom.yaml](30-ebom.yaml) | Phase 3 E-BOM | 製造パッケージ |
| 31 | [31-kbom.yaml](31-kbom.yaml) | Phase 3 K-BOM | 製造パッケージ |
| 32 | [32-mbom.yaml](32-mbom.yaml) | Phase 3 M-BOM | 製造パッケージ |
| 33 | [33-control-plan.yaml](33-control-plan.yaml) | Phase 3 Control Plan | 製造パッケージ |
| 34 | [34-routing.yaml](34-routing.yaml) | Phase 3 Routing | 製造パッケージ |
| 35 | [35-design-system-bom.yaml](35-design-system-bom.yaml) | Phase 3 Design System BOM(candidate) | UI-CAD 案件では**製造パッケージ必須**。非UI案件は not-applicable |
| 36 | [36-ui-dictionary.yaml](36-ui-dictionary.yaml) | Phase 2–5 UI 用語辞書(candidate) | **設計者のみ**(canonical 名は 20/30 へ反映して渡す) |
| 37 | [37-ui-rulings.yaml](37-ui-rulings.yaml) | Phase 2–5 UI 裁定台帳(candidate) | **設計者のみ**(設計対話の来歴。41/42 と同様に工場非開示) |
| 40 | [40-work-order.md](40-work-order.md) | Phase 4 製造指示 | 製造パッケージ(表紙) |
| 41 | [41-fixed-oracle.yaml](41-fixed-oracle.yaml) | Phase 3–5 固定オラクル | **設計者のみ(工場非開示)** |
| 42 | [42-exploratory-probes.yaml](42-exploratory-probes.yaml) | Phase 3–5 探索プローブ | **設計者のみ(工場非開示)** |
| 43 | [43-visual-gap-analysis.md](43-visual-gap-analysis.md) | Phase 5 視覚ギャップ分析(UI-CAD vs 実機) | 設計者(検査結果。是正時はCAPAへ) |
| 50 | [50-as-built.yaml](50-as-built.yaml) | Phase 5–6 製造来歴 | 記録 |
| 51 | [51-cheat-log.md](51-cheat-log.md) | 全期間 ずる台帳 | 記録 |
| 52 | [52-metrics.yaml](52-metrics.yaml) | Phase 5 測定 | 記録 |
| 53 | [53-service-bom.yaml](53-service-bom.yaml) | Phase 6 保守部品表(概念は [s-bom-template.md](../s-bom-template.md)) | 納品物 |
| 60 | [60-change-order.md](60-change-order.md) | Phase 7 変更/是正オーダー(ECO/CAPA: 影響分析→部分再製造→回帰) | 設計者(改訂 BOM+ECO/CAPA を工場へ) |
| 61 | [61-impact-analysis.md](61-impact-analysis.md) | Phase 7 影響分析(影響なし予測の先行凍結) | 製造パッケージ(ECO/CAPA 時) |
| 62 | [62-migration-oracle.md](62-migration-oracle.md) | Phase 7 データ移行オラクル+fixture | **設計者のみ(実装・fixture 期待値は工場非開示)** |
| 63 | [63-diff-audit.md](63-diff-audit.md) | Phase 7 不要改変監査(diff 基準点+4分類) | 設計者(「diff を測る」の事前宣言のみ work order へ) |
| 64 | [64-part-lineage-reattribution.md](64-part-lineage-reattribution.md) | Phase 7 部品分割・置換の来歴+再帰属 | 設計者(ECO/CAPA 時。active graph gate の証跡) |

**隔離規律(再掲)**: 製造装置に渡してよいのは 20/30–34/40(+観測契約)だけ。UI-CAD 案件では 35 も必須で渡す。41/42 と設計対話の履歴は渡さない。

## 新規プロジェクト開始時の入口

- AI に最初に渡す文書: [../onboarding/ai-onboarding-pack.md](../onboarding/ai-onboarding-pack.md)
- 人間と AI の開始チェック: [../onboarding/new-project-checklist.md](../onboarding/new-project-checklist.md)
- 開発者の配置ナビ: [../onboarding/developer-navigation.md](../onboarding/developer-navigation.md)
- 既存プロジェクト移行パック: [../onboarding/existing-project-migration.md](../onboarding/existing-project-migration.md)
- 既存プロジェクト移行チェック: [../onboarding/migration-checklist.md](../onboarding/migration-checklist.md)
- PLM-ready の必須契約: [../contracts/plm-ready-contract.md](../contracts/plm-ready-contract.md)
- BOM 粒度判断: [../contracts/bom-granularity-guide.md](../contracts/bom-granularity-guide.md)
- TraceLink 規則: [../contracts/traceability-rules.md](../contracts/traceability-rules.md)

新規対象プロジェクトでは、まず `bomdd/` に本テンプレートをコピーし、`00/10/20` を作成してから PLM に初回同期する。実装は `30-34/40`、UI-CAD 案件では `35`、および PLM Gate が通るまで開始しない。

既存対象プロジェクトでは、先に `bomdd/plm-intake/migration-inventory.md` と `source-map.md` を作り、既存実装を変更せずに PLM-ready 化する。移行 Gate が通るまで Work Order を製造 AI へ渡さない。
