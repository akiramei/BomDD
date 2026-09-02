# BomDD — BOM-Driven Development 実証研究

> 🧭 **進行中の BomDD プロジェクトに参加する人はまずここ** → [進行中プロジェクトへの参加(操作チェックリスト)](method/onboarding/joining-a-project.md)。協働の作法は [working-with-ai.md](method/onboarding/working-with-ai.md)。**このリポ自体で作業する人・AI の入口は [AGENTS.md](AGENTS.md)**(作業規律 6 項目・正本の所在・作業スキル契約)。以下は研究リポとしての説明。

ソフトウェアの「工業化」(設計BOM→製造BOM→保守BOM を貫く工程としてのソフトウェア開発)が
成立するかを、既存アプリ [MoviePad](../MoviePad) の **BOM手法による再実装**を通じて検証する研究。

> これは開発でなく**研究**である。真の成果物は動くアプリではなく、
> 「**BOM手法がどこで破れ(=ずる)、どう埋めるか**」の記録と手法改善である。

BomDD の核は BOM 概念そのものではなく、**隔離 AI 工場、固定オラクルと探索プローブの分離、ずる報告、
工場間分散の帰属を、一つの検証可能な製造ループとして結合する点**にあります。

📕 **公開版ホワイトペーパー: [WHITEPAPER.md](WHITEPAPER.md)** — 「BOM-Driven Development: AIをソフトウェア製造装置とみなす工業化手法の実証研究」(7ループ・10章・強い主張/未検証の分離)。
📄 **詳細総括は [FINDINGS.md](FINDINGS.md)** — 7ループの実験記録・ずる台帳12件・三層BOM構想へのフィードバック。
📘 **正規の方法論は [method/bomdd-method-v1.md](method/bomdd-method-v1.md)** — 実証済みの規則だけを束ねた薄い手順(E/M-BOM・K-BOM・Control Plan・FMEA・マルチファクトリ・受入の梯子・品質二軸)。
🔬 **v2 — 別ドメインでも再現済み(N=3)**: 題材は MoviePad だけではない。**Web/API**(会議室予約)で BOM 補正により原版との差分が **2→3→0** に収束・多工場で **0/1/3**。**分散Saga**(非同期イベント駆動)で多工場(opus/sonnet/haiku)の**挙動契約が 0/0/0**=仕様面は全ティアへ転移し未規定面のみ分散。証拠リポ [BomDD-WebApi-Sample](https://github.com/akiramei/BomDD-WebApi-Sample)・[BomDD-DistributedSaga-Sample](https://github.com/akiramei/BomDD-DistributedSaga-Sample) / まとめ [FINDINGS.md §6](FINDINGS.md) / **自分の手で追う [reproduce-webapi-v2](docs/reproduce-webapi-v2.md)・[reproduce-saga-v2](docs/reproduce-saga-v2.md)**。

🛠 **実用パイプライン(フォワード・モード): [method/bomdd-playbook-v1.md](method/bomdd-playbook-v1.md)** — 原版の無い新規開発(ブレスト→仕様→BOM・工程設計→AI製造→受入・収束)を回すための実践手順。リバースで実証した装置群(固定オラクル・隔離ファクトリ・ずる報告・マルチファクトリ分散)をフォワードへ移植し、**forward-01〜04・scale-01・transfer-01〜03(N=3・ベンダー横断・説明介入ゼロ)で実証済み**(FINDINGS §7/9/11)。付属: [沈黙次元カタログ](method/silence-checklist.md)(BOMが沈黙しがちな次元の掃討表)/ [テンプレ一式](method/templates/) / [フェーズ実行プロンプト](method/prompts/)(**実行手順の正典**。ツール固有 adapter 層= [product-profile テンプレ](method/templates/product-profile/)+スキル 11 本 — 2026-07 に ViewPrism2 実運用から 5 本を一般化・後に UI-CAD 系 3 本を追加・2026-08 に TimetableAdv 実績から `/converge`(設計収束ループ)を昇格・2026-08-31 に `/calibrate`(測定系較正ループ)・2026-09-01 に `/preflight`(作業開始条件の再認証)を新設)。**新規開始は `python method/tools/bomdd-init.py <Product> --gui`**(プロダクト+CAD リポを生成・[人間向け協働ガイド](method/onboarding/working-with-ai.md)つき)。

🧩 **UIモック入口(candidate): [method/ui-ir-ui-bom.md](method/ui-ir-ui-bom.md)** — HTML/JavaScript/CSSで作った実行可能UIモックを、UI-IR→UI-BOM→E-BOM/Control Plan/S-BOMへ接続するための候補拡張。テンプレートは [method/templates/ui-mock-extraction/](method/templates/ui-mock-extraction/)、抽出AIへの指示は二段プロンプト [method/prompts/ui-raw-to-candidates.md](method/prompts/ui-raw-to-candidates.md) → [method/prompts/ui-apply-rulings-to-bom.md](method/prompts/ui-apply-rulings-to-bom.md)(旧一発変換は deprecated)。

> **用語の注意**: 本研究の **S-BOM は一般的な SBOM(Software Bill of Materials)ではなく、Service BOM / 保守部品表**を指す。OSS 依存一覧はその一部に過ぎず、「何が影響し・何を再検査し・交換/再製造が要るか」を導く保守層である。概念は [docs/concept.md](docs/concept.md)、用語の固定は [docs/terminology.md](docs/terminology.md)。

## 方法 — アクションリサーチのループ

1. **リバース**: MoviePad のソース/doc/テストから要求仕様・機能仕様を復元
2. **E-BOM**: 論理部品構成 + 各部品の存在理由↔仕様トレース
3. **M-BOM**: 実現技術・非機能・**合否判断基準**・調達部品
4. **工程設計**: 生成→検査のルーティング
5. **AI製造**: BOM のみから成果物を生成(→ 製造装置の隔離: [method/cheat-taxonomy.md](method/cheat-taxonomy.md))
6. **合否**: M-BOM 基準で判定
7. **限界に当たったら止めず従来手法で進む(=ずる)** → ずるを記録 → 分析 → 次ループへ

## 構成

```
AGENTS.md           ★このリポで作業する入口(作業規律 6 項目・正本の所在・作業スキル契約)
CLAUDE.md           Claude 固有の補足(ハーネス依存の運用・実測の背景)
WHITEPAPER.md       公開版ホワイトペーパー
FINDINGS.md         実験記録の総括(7ループ・v2・フォワード・転移・自己適用 §11)
docs/               公開ドキュメント
  concept.md          構想の全体像(概念)
  terminology.md      用語集(E/M/S/K-BOM・核/表面・ずる・鋳造・裁定・receipt・UNKNOWN)
  evidence-index.md   論文主張と公開証拠の対応
  reproduce-*.md      第三者再現ガイド(webapi-v2 / saga-v2 / forward-01)
method/             手法定義(ループ毎に進化)
  bomdd-method-v1.md  正規の方法論(薄い版・v1〜v1.3 の実証済み規則のみ)
  bomdd-playbook-v1.md ★実用パイプライン(フォワード・モード。§8 ECO 規律・§9 裁定配置・§13 工具化ラダー)
  ui-ir-ui-bom.md       UIモック→UI-IR/UI-BOM→E-BOM接続(candidate)
  gap-analysis-v1.md  ギャップ分析(仕様→BOM/BOM→製造/検証パターン/運用の課題と優先度)
  silence-checklist.md 沈黙次元カタログ(BOM設計時の掃討表)
  cheat-taxonomy.md   ずるの分類・記録様式・製造装置の隔離規律
  control-plan.md     製造条件表+検査計画(検査深さ/許容差/承認者)
  k-bom-ffmpeg.md     知識部品BOM(ffmpeg文法パック)
  s-bom-template.md   Service BOM の語彙と運用
  improvements.md     手法改善ログ(EXP/OBS 台帳 — 一覧は tools/worklist.py)
  templates/          フォワード成果物テンプレ一式(00〜64)+ product-profile/(製品リポ運用プロファイル+スキル 11 本)+ process-core/(hooks・lifecycle validator)
  prompts/            フェーズ実行プロンプト(Phase 0〜7+UI モック系)— 実行手順の正典
  onboarding/         参加・開始・移行・協働ガイド(人間向け/AI 向け)
  contracts/          PLM-ready 契約・BOM 粒度・トレース規則
  tools/              bomdd-init(製品リポ生成)/ self-conformance(本リポの機械検査)/ kit-freshness / 採点・健診治具
bomdd/              ★方法論リポ自身の変更管理(自己適用): 60-change-register.yaml + ECO order 群 + hooks/
loops/
  metrics.csv / metrics-v2.csv  測定値集約(二軸品質)
  loop-01〜07-*/      MoviePad 7 ループ(区間分割・書き出し・UI・マルチファクトリ・L3 信号・S-BOM/PLM・リバース)
  transfer-01〜03/    方法論の転移試験(ベンダー横断・説明介入ゼロ)
  equip-01〜03/       AI 設備認定(製造セルの適格性)
  stage0-oss-01/ cli-cad-01/ bdr-01/ onboarding-t0-01/ cheat-reclassification-01/  個別実験
  各 build/ = 隔離装置が製造した成果物 + 受入オラクル/治具(同格管理)
experiments/        探索的実験(legacy-wpf-rdb・obsidian-stage0)
paper/              論文原稿・査読対応
```

## 関連

- 構想の全体像: [docs/concept.md](docs/concept.md) / 用語定義: [docs/terminology.md](docs/terminology.md)
- 題材 MoviePad: Avalonia 12 + .NET 10 + C# / LibVLC + ffmpeg の非破壊動画編集デスクトップアプリ。
