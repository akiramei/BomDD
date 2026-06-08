# BomDD — BOM-Driven Development 実証研究

ソフトウェアの「工業化」(設計BOM→製造BOM→保守BOM を貫く工程としてのソフトウェア開発)が
成立するかを、既存アプリ [MoviePad](../MoviePad) の **BOM手法による再実装**を通じて検証する研究。

> これは開発でなく**研究**である。真の成果物は動くアプリではなく、
> 「**BOM手法がどこで破れ(=ずる)、どう埋めるか**」の記録と手法改善である。

📕 **公開版ホワイトペーパー: [WHITEPAPER.md](WHITEPAPER.md)** — 「BOM-Driven Development: AIをソフトウェア製造装置とみなす工業化手法の実証研究」(7ループ・10章・強い主張/未検証の分離)。
📄 **詳細総括は [FINDINGS.md](FINDINGS.md)** — 7ループの実験記録・ずる台帳12件・三層BOM構想へのフィードバック。
📘 **正規の方法論は [method/bomdd-method-v1.md](method/bomdd-method-v1.md)** — 実証済みの規則だけを束ねた薄い手順(E/M-BOM・K-BOM・Control Plan・FMEA・マルチファクトリ・受入の梯子・品質二軸)。

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
FINDINGS.md         5ループ最終総括(核/表面の法則)
method/             手法定義(ループ毎に進化)
  bomdd-method-v1.md  ★正規の方法論(薄い版)
  cheat-taxonomy.md   ずるの分類・記録様式・製造装置の隔離規律
  improvements.md     手法改善ログ(各ループの効果測定)
  control-plan.md     製造条件表+検査計画(検査深さ/許容差/承認者)
  k-bom-ffmpeg.md     知識部品BOM(ffmpeg文法パック)
loops/
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

- 構想の全体像はセッションメモリ参照(`bomdd-core-concept` / `bomdd-open-questions` / `bomdd-moviepad-research`)。
- 題材 MoviePad: Avalonia 12 + .NET 10 + C# / LibVLC + ffmpeg の非破壊動画編集デスクトップアプリ。
