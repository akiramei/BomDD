# BomDD — BOM-Driven Development 実証研究

ソフトウェアの「工業化」(設計BOM→製造BOM→保守BOM を貫く工程としてのソフトウェア開発)が
成立するかを、既存アプリ [MoviePad](../MoviePad) の **BOM手法による再実装**を通じて検証する研究。

> これは開発でなく**研究**である。真の成果物は動くアプリではなく、
> 「**BOM手法がどこで破れ(=ずる)、どう埋めるか**」の記録と手法改善である。

📕 **公開版ホワイトペーパー: [WHITEPAPER.md](WHITEPAPER.md)** — 「BOM-Driven Development: AIをソフトウェア製造装置とみなす工業化手法の実証研究」(7ループ・10章・強い主張/未検証の分離)。
📄 **詳細総括は [FINDINGS.md](FINDINGS.md)** — 7ループの実験記録・ずる台帳12件・三層BOM構想へのフィードバック。
📘 **正規の方法論は [method/bomdd-method-v1.md](method/bomdd-method-v1.md)** — 実証済みの規則だけを束ねた薄い手順(E/M-BOM・K-BOM・Control Plan・FMEA・マルチファクトリ・受入の梯子・品質二軸)。
🔬 **v2 — 別ドメインでも再現済み(N=3)**: 題材は MoviePad だけではない。**Web/API**(会議室予約)で BOM 補正により原版との差分が **2→3→0** に収束・多工場で **0/1/3**。**分散Saga**(非同期イベント駆動)で多工場(opus/sonnet/haiku)の**挙動契約が 0/0/0**=仕様面は全ティアへ転移し未規定面のみ分散。証拠リポ [BomDD-WebApi-Sample](https://github.com/akiramei/BomDD-WebApi-Sample)・[BomDD-DistributedSaga-Sample](https://github.com/akiramei/BomDD-DistributedSaga-Sample) / まとめ [FINDINGS.md §6](FINDINGS.md) / **自分の手で追う [reproduce-webapi-v2](docs/reproduce-webapi-v2.md)・[reproduce-saga-v2](docs/reproduce-saga-v2.md)**。

🛠 **実用パイプライン(フォワード・モード): [method/bomdd-playbook-v1.md](method/bomdd-playbook-v1.md)** — 原版の無い新規開発(ブレスト→仕様→BOM・工程設計→AI製造→受入・収束)を回すための実践手順。リバースで実証した装置群(固定オラクル・隔離ファクトリ・ずる報告・マルチファクトリ分散)をフォワードへ移植した **prescriptive draft(未実証・forward ループで検証予定)**。付属: [沈黙次元カタログ](method/silence-checklist.md)(BOMが沈黙しがちな次元の掃討表)/ [テンプレ一式](method/templates/) / [フェーズ実行プロンプト](method/prompts/)(**実行手順の正典**。ツール固有の skill/slash command 化は forward-01 検証後に adapter 層として検討)。

🧩 **UIモック入口(candidate): [method/ui-ir-ui-bom.md](method/ui-ir-ui-bom.md)** — HTML/JavaScript/CSSで作った実行可能UIモックを、UI-IR→UI-BOM→E-BOM/Control Plan/S-BOMへ接続するための候補拡張。テンプレートは [method/templates/ui-mock-extraction/](method/templates/ui-mock-extraction/)、抽出AIへの指示は [method/prompts/ui-mock-to-ui-bom.md](method/prompts/ui-mock-to-ui-bom.md)。

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
docs/               公開ドキュメント
  concept.md          構想の全体像(概念)
  terminology.md      用語集(E/M/S/K-BOM・核/表面・ずる・鋳造の固定)
FINDINGS.md         7ループ最終総括(核/表面の法則)
method/             手法定義(ループ毎に進化)
  bomdd-method-v1.md  ★正規の方法論(薄い版・実証済み規則のみ)
  bomdd-playbook-v1.md ★実用パイプライン(フォワード・モード/prescriptive draft)
  ui-ir-ui-bom.md       UIモック→UI-IR/UI-BOM→E-BOM接続(candidate)
  gap-analysis-v1.md  ギャップ分析(仕様→BOM/BOM→製造/検証パターン/運用の課題と優先度)
  silence-checklist.md 沈黙次元カタログ(BOM設計時の掃討表)
  templates/          フォワード成果物テンプレ一式(00〜52)
  prompts/            フェーズ実行プロンプト(Phase1〜5)
  cheat-taxonomy.md   ずるの分類・記録様式・製造装置の隔離規律
  improvements.md     手法改善ログ(各ループの効果測定)
  control-plan.md     製造条件表+検査計画(検査深さ/許容差/承認者)
  k-bom-ffmpeg.md     知識部品BOM(ffmpeg文法パック)
loops/
  metrics.csv         全ループの測定値集約(二軸品質: 合格率/介入/ずる/工場間ばらつき/再検査絞込)
  loop-01-split/      Loop1 区間分割(純粋ロジック): 00-charter〜06-acceptance, cheat-log
  loop-01-report.md   Loop1 総括
  loop-01.5-split/    Loop1.5 改善効果測定(再製造でずる減を実測)
  loop-02-export/     Loop2 書き出し(外部ツールIO): 文字列照合の破綻
  loop-02-report.md
  loop-02.5-export-exec/ Loop2.5 execution受入(L2 ffprobe)
  loop-03-timeline/   Loop3 UI/知覚(golden画素差分)
  loop-03-report.md
  loop-04-multifactory/ Loop4 マルチファクトリ×K-BOM(ばらつきで品質測定)
  loop-05-L3-signal/  Loop5 execution L3(音声信号比較で座標系バグ捕捉)
  各 build/ = 隔離装置が製造した成果物 + 受入オラクル/治具(同格管理)
```

## 関連

- 構想の全体像: [docs/concept.md](docs/concept.md) / 用語定義: [docs/terminology.md](docs/terminology.md)
- 題材 MoviePad: Avalonia 12 + .NET 10 + C# / LibVLC + ffmpeg の非破壊動画編集デスクトップアプリ。
