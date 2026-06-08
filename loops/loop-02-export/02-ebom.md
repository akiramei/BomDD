# ② E-BOM(グラフ版) — 書き出しスライス

| コード | 部品 | 種別 | owner | consumers | スライス内 |
|---|---|---|---|---|---|
| EB-CLIP | クリップメタ(ClipInfo) | domain | 読込 | 書出/表示/プレビュー | 参照(共有) |
| EB-EDIT-DOC | 編集ドキュメント | domain | (基盤) | 全編集/書出 | 参照(共有) |
| EB-EXPFMT | 書き出し形式(ExportFormat) | domain | 書出 | 書出 | 固有 |
| EB-EXPREQ | 書き出し要求(Request) | domain | 書出 | 書出 | 固有 |
| EB-EXPPLAN | 変換解析(ExportPlan.Analyze) | domain(規則) | 書出 | 書出(コピー可否判定) | **固有・Unit A** |
| EB-FILTERGRAPH | filter_complex 構築 | io-adapter | 書出 | 書出(再エンコード経路) | **固有・Unit B** |
| EB-COPYARGS | stream copy 引数構築 | io-adapter | 書出 | 書出(高速経路) | **固有・Unit B** |
| EB-ENCODER | 形式別エンコーダ引数 | io-adapter | 書出 | 書出 | 固有 |
| EB-PROCRUN | ffmpegプロセス実行/進捗 | io | (基盤) | 書出/解析/サムネ | 共有・**Loop2対象外** |

## エッジ
```
EB-EXPREQ --aggregates--> EB-CLIP, EB-EDIT-DOC, EB-EXPFMT
EB-EXPPLAN --analyzes--> EB-EXPREQ
EB-FILTERGRAPH --uses--> EB-EXPPLAN, EB-EXPREQ
EB-COPYARGS --uses--> EB-EXPPLAN, EB-EXPREQ
(EB-PROCRUN --executes--> EB-FILTERGRAPH/EB-COPYARGS の出力)  ※Loop2対象外
```

## 所見(種別の新出)
Split は domain/orchestration/ui の3種だったが、書き出しは **io-adapter**(外部ツールへの変換アダプタ)が中心。
io-adapter の「責務」は「外部ツールの正しいコマンドを生成する」であり、その正しさは**外部ツールの仕様に従属**する。
→ E-BOM の責務記述だけでは閉じず、外部ツール(ffmpeg)の知識が暗黙の前提になる(H4/H5/H6 の構造的理由)。
