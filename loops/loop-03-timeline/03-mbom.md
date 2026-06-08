# ③ M-BOM — タイムライン描画スライス(Unit G 幾何完全 / Unit R 描画・速度色のみ未規定)

成果物 = C#ライブラリ `MoviePad.TimelineSlice`(net10.0)。技術は原版固定だが、UI 受入を自己完結化するため
Avalonia/Skia/フォントは使わず、決定的 RGBA ラスタ(整数矩形塗り)で実装する(描画の本質=幾何→画素の写像を保つ)。

## 公開契約(signature 固定。speed-tint 色は Render の引数にしない=manufacturer 裁量)
```csharp
namespace MoviePad.Timeline;
public readonly record struct Rect(double X, double Y, double W, double H);
public sealed record RegionData(int Id, double Start, double End, double Speed, bool PreservePitch,
                                bool Excluded = false, double Volume = 1.0) { public bool IsNormalSpeed { get; } } // |Speed-1|<0.001
public sealed record DocState(double TrimStart, double TrimEnd, System.Collections.Immutable.ImmutableList<RegionData> Regions);

public static class TimelineLayout {
    public const double TrackTop = 30; public const double TrackH = 92;
    public static double X(double t, double px);
    public static Rect RegionRect(RegionData r, double px);
    public static double PlayheadX(double playhead, double px);
    public static Rect TrimMaskLeft(DocState s, double px);
    public static Rect TrimMaskRight(DocState s, double px, double width);
    public static System.Collections.Generic.IReadOnlyList<double> BoundaryXs(DocState s, double px);
    public static double NiceStep(double targetSec);  // steps{0.5,1,2,5,10,15,30,60,120,300} で target以上の最小、無ければ600
    public static System.Collections.Generic.IReadOnlyList<(double t, double x)> RulerTicks(double dur, double px); // step=NiceStep(70/px)
}
public static class TimelineRaster {
    public static byte[] Render(DocState s, double playhead, double px, int width, int height,
        (byte r,byte g,byte b) canvasBg, (byte r,byte g,byte b) surface, (byte r,byte g,byte b) excluded,
        (byte r,byte g,byte b) trimMask, (byte r,byte g,byte b) boundary, (byte r,byte g,byte b) playheadColor);
}
```

## Unit G 受入(規則=完全規定。検査=unit)
- `X(t,px)=t*px`、`TrackTop=30,TrackH=92`、`RegionRect=(X(Start),30,X(End)-X(Start),92)`、`PlayheadX=X(playhead)`。
- `TrimMaskLeft=(0,30,X(TrimStart),92)`、`TrimMaskRight=(X(TrimEnd),30,width-X(TrimEnd),92)`。
- `BoundaryXs=[X(Regions[i].End)] (i=0..Count-2)`。`NiceStep`/`RulerTicks` 上記。
- レイアウト定数・NiceStep の steps/target=70/px は**設計知識**だが BOM が運ぶ(→ C2 を記録)。

## Unit R 受入(描画。検査=golden ラスタ画素差分)
固定キャンバスへ z-order で整数矩形塗り。RGBA8888・行優先・各画素 [R,G,B,255]。矩形塗り規則:
`x0=floor(X),x1=floor(X+W),y0=floor(Y),y1=floor(Y+H)`、`c∈[max(0,x0),min(width,x1))`,`r∈[max(0,y0),min(height,y1))`。
z-order: ①canvasBg 全面 → ②surface でトラック(0,30,width,92) → ③**速度ティント**(非除外かつ非等速の RegionRect。**色は manufacturer 裁量**) →
④excluded で除外 RegionRect → ⑤trimMask で TrimMaskLeft/Right → ⑥boundary で各境界 `(x-1,33,2,86)` → ⑦playheadColor で `(PlayheadX-1,0,2,height)`。

**唯一の未規定**: 速度→ティント色の対応(原版は OKLCH 設計トークン)。これが知覚ギャップの測定点。
