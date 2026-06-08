# ③ M-BOM — 書き出しスライス(Unit A 規則完全 / Unit B 挙動のみ)

技術固定。成果物 = C#ライブラリ `MoviePad.ExportSlice`(net10.0)。
**実験変数**: Unit A は規則を完全列挙(industrializable 対照)、Unit B は内部様式を manufacturer に委ねる(外部文法ギャップ露出)。

## 公開契約(オラクル互換のため signature 固定。元 internal は public 化)
`ClipInfo` / `RegionData` / `DocumentState`(Loop1 と同形、本スライスで使う派生のみ)、`enum ExportFormat{Mp4,Lossless,ProRes}`、
`FfmpegExporter.Request(Clip,Doc,OutWidth,OutHeight,Format,OutputPath,OutFps,FastCopy=false,CopyStartOverride=null)`、
`ExportPlan(NeedsScale,NeedsRerate,VideoCopyEligible,AudioCopyEligible,SingleSpan,SpanStart,SpanEnd)` + `CanStreamCopy` + `static Analyze(Request)`、
`FfmpegExporter.BuildFilterGraph(Request,ExportPlan,bool hasAudio,double seekBase,out int segCount)` / `BuildFilterArgs(Request,double seekBase,string filter,bool hasAudio)` / `BuildCopyArgs(Request,ExportPlan,bool hasAudio)`。

## Unit A 受入(規則=[01-reverse-spec.md](01-reverse-spec.md) の Analyze 規則を完全規定。検査=unit)
plan フラグ群を入力から決定。コーデック白名簿・VFR非対称・eps・閾値すべて明記済み。**ここは導出可能であるべき(対照)**。

## Unit B 受入(挙動のみ。検査モダリティ=本来は execution/golden、Loop2 では文字列照合で“ギャップ可視化”に使う)
- 非除外かつ [TrimStart,TrimEnd] と交差する区間ごとに、映像と(音声があれば)音声をトリムし、区間速度・区間音量(非full時)を適用して連結し、`NeedsScale` 時のみ scale、`NeedsRerate` 時のみ fps を適用、最終映像を **`[vout]`**、最終音声を **`[aout]`** として出力する単一 filter_complex を作る(出力パッド名のみ固定)。
- 音声速度はピッチ維持/非維持で方式が異なる(維持: テンポのみ変更、非維持: サンプルレート変更)。
- BuildFilterArgs は `[vout]`/`[aout]` を `-map` し、前トリム高速化のため必要に応じ映像入力をシークしてよい。BuildCopyArgs は stream copy 引数を作る。
- **意図的に未規定(= manufacturer 判断)**: 中間ラベル名、恒等変換時の透過フィルタの綴り、スケール補間フラグ、シーク時の入力構成、数値書式、引数の正確な並び。

## 効果測定
- Unit A オラクル合格率 / 「導けない規則(白名簿等)」の自己申告数。
- Unit B オラクル合格内訳: 通る assertion(=標準ffmpeg慣用=タダのC2) vs 落ちる assertion(=実装固有様式)。
