using System.Collections.Immutable;
using MoviePad.Timeline;
using Xunit;
using Xunit.Abstractions;

namespace MoviePad.TimelineSlice.Tests;

/// <summary>
/// Loop3 隠しオラクル。Unit G(幾何)=単体検査 / Unit R(描画)=golden ラスタ画素差分。
/// 製造装置には未開示。幾何は industrialize するか、描画の未規定トークン(速度色)はどう乖離するかを測る。
/// </summary>
public class TimelineSliceTests
{
    private readonly ITestOutputHelper _out;
    public TimelineSliceTests(ITestOutputHelper o) => _out = o;

    private const double Px = 10;
    private const int W = 800, H = 122;

    // シナリオ: dur=80, trim[10,70], 区間: 等速/2x/0.5x/除外, playhead=35
    private static DocState Scene() => new(10, 70, ImmutableList.Create(
        new RegionData(1, 0, 20, 1.0, true),
        new RegionData(2, 20, 40, 2.0, true),
        new RegionData(3, 40, 55, 0.5, true),
        new RegionData(4, 55, 80, 1.0, true, Excluded: true)));

    // 指定パレット(製造物にも golden にも同じものを渡す)
    private static readonly (byte r, byte g, byte b) CanvasBg = (14, 14, 14);
    private static readonly (byte r, byte g, byte b) Surface = (23, 26, 30);
    private static readonly (byte r, byte g, byte b) Excluded = (26, 5, 8);
    private static readonly (byte r, byte g, byte b) TrimMask = (11, 5, 7);
    private static readonly (byte r, byte g, byte b) Boundary = (150, 152, 154);
    private static readonly (byte r, byte g, byte b) Playhead = (242, 244, 246);
    // golden 側の「速度ティント設計トークン」(製造装置には未開示=BOM 未規定)
    private static (byte r, byte g, byte b) GoldenTint(double speed)
        => speed > 1 ? ((byte)200, (byte)90, (byte)40) : ((byte)40, (byte)90, (byte)200);

    // ===== Unit G(幾何) =====
    [Fact] public void X_IsLinear() => Assert.Equal(350.0, TimelineLayout.X(35, Px));
    [Fact] public void RegionRect_MapsToPixels()
    {
        var r = TimelineLayout.RegionRect(new RegionData(2, 20, 40, 2.0, true), Px);
        Assert.Equal(200.0, r.X); Assert.Equal(30.0, r.Y); Assert.Equal(200.0, r.W); Assert.Equal(92.0, r.H);
    }
    [Fact] public void PlayheadX_IsMapped() => Assert.Equal(350.0, TimelineLayout.PlayheadX(35, Px));
    [Fact] public void TrimMasks_AreCorrect()
    {
        var l = TimelineLayout.TrimMaskLeft(Scene(), Px);
        Assert.Equal(0.0, l.X); Assert.Equal(100.0, l.W);
        var rr = TimelineLayout.TrimMaskRight(Scene(), Px, W);
        Assert.Equal(700.0, rr.X); Assert.Equal(100.0, rr.W);
    }
    [Fact] public void BoundaryXs_AtRegionEnds()
        => Assert.Equal(new double[] { 200, 400, 550 }, TimelineLayout.BoundaryXs(Scene(), Px));
    [Fact] public void NiceStep_PicksFirstStepAtOrAboveTarget()
    {
        Assert.Equal(10.0, TimelineLayout.NiceStep(70 / Px)); // target 7 → 10
        Assert.Equal(2.0, TimelineLayout.NiceStep(1.3));      // → 2
        Assert.Equal(600.0, TimelineLayout.NiceStep(999));    // 超過 → 600
    }
    [Fact] public void RulerTicks_StepAndPositions()
    {
        var ticks = TimelineLayout.RulerTicks(80, Px); // step=10
        Assert.Equal(9, ticks.Count);
        Assert.Equal((0.0, 0.0), ticks[0]);
        Assert.Equal((80.0, 800.0), ticks[^1]);
    }

    // ===== Unit R(描画): golden ラスタ画素差分 =====

    private static void Fill(byte[] buf, int w, int h, Rect rect, (byte r, byte g, byte b) c)
    {
        int x0 = Math.Max(0, (int)Math.Floor(rect.X)), x1 = Math.Min(w, (int)Math.Floor(rect.X + rect.W));
        int y0 = Math.Max(0, (int)Math.Floor(rect.Y)), y1 = Math.Min(h, (int)Math.Floor(rect.Y + rect.H));
        for (int y = y0; y < y1; y++)
            for (int x = x0; x < x1; x++)
            {
                int i = (y * w + x) * 4;
                buf[i] = c.r; buf[i + 1] = c.g; buf[i + 2] = c.b; buf[i + 3] = 255;
            }
    }

    // 検査者の参照(golden)レンダラ: 製造物と同じ z-order・同じ矩形規則・同じ指定パレット。
    // 違いは「速度ティント色」だけ(=BOM 未規定の設計トークン)。
    private static byte[] Golden(DocState s, double playhead)
    {
        var buf = new byte[W * H * 4];
        Fill(buf, W, H, new Rect(0, 0, W, H), CanvasBg);
        Fill(buf, W, H, new Rect(0, 30, W, 92), Surface);
        foreach (var r in s.Regions) if (!r.Excluded && !r.IsNormalSpeed) Fill(buf, W, H, TimelineLayout.RegionRect(r, Px), GoldenTint(r.Speed));
        foreach (var r in s.Regions) if (r.Excluded) Fill(buf, W, H, TimelineLayout.RegionRect(r, Px), Excluded);
        Fill(buf, W, H, TimelineLayout.TrimMaskLeft(s, Px), TrimMask);
        Fill(buf, W, H, TimelineLayout.TrimMaskRight(s, Px, W), TrimMask);
        foreach (var x in TimelineLayout.BoundaryXs(s, Px)) Fill(buf, W, H, new Rect(x - 1, 33, 2, 86), Boundary);
        Fill(buf, W, H, new Rect(TimelineLayout.PlayheadX(playhead, Px) - 1, 0, 2, H), Playhead);
        return buf;
    }

    // 速度ティント領域(製造物と golden が違い得る唯一の場所)の画素か判定
    private static bool InTintRegion(DocState s, int col, int row)
    {
        foreach (var r in s.Regions)
        {
            if (r.Excluded || r.IsNormalSpeed) continue;
            var rect = TimelineLayout.RegionRect(r, Px);
            int x0 = (int)Math.Floor(rect.X), x1 = (int)Math.Floor(rect.X + rect.W);
            int y0 = (int)Math.Floor(rect.Y), y1 = (int)Math.Floor(rect.Y + rect.H);
            if (col >= x0 && col < x1 && row >= y0 && row < y1) return true;
        }
        return false;
    }

    [Fact] // 画素一致(golden) は失敗する = 過剰結合(妥当な設計差を拒否)
    public void GoldenPixelExact_RejectsValidDesignVariation()
    {
        var s = Scene();
        byte[] m = TimelineRaster.Render(s, 35, Px, W, H, CanvasBg, Surface, Excluded, TrimMask, Boundary, Playhead);
        byte[] g = Golden(s, 35);

        int diff = 0;
        for (int p = 0; p < W * H; p++)
            if (m[p * 4] != g[p * 4] || m[p * 4 + 1] != g[p * 4 + 1] || m[p * 4 + 2] != g[p * 4 + 2]) diff++;

        _out.WriteLine($"画素差分: {diff} / {W * H} ({100.0 * diff / (W * H):0.0}%)");
        Assert.True(diff > 0, "画素一致オラクルは差分を検出する(妥当な設計差でも不一致)");
    }

    [Fact] // 差分は未規定の速度ティント領域に局在(幾何・指定トークンはピクセル完全一致)
    public void Divergence_IsLocalizedToUnspecifiedSpeedTint()
    {
        var s = Scene();
        byte[] m = TimelineRaster.Render(s, 35, Px, W, H, CanvasBg, Surface, Excluded, TrimMask, Boundary, Playhead);
        byte[] g = Golden(s, 35);

        int diff = 0, outsideTintDiff = 0;
        for (int row = 0; row < H; row++)
            for (int col = 0; col < W; col++)
            {
                int i = (row * W + col) * 4;
                bool d = m[i] != g[i] || m[i + 1] != g[i + 1] || m[i + 2] != g[i + 2];
                if (!d) continue;
                diff++;
                if (!InTintRegion(s, col, row)) outsideTintDiff++;
            }

        _out.WriteLine($"総差分 {diff} 画素, うちティント領域外 {outsideTintDiff}");
        // 指定トークン+幾何の領域は完全一致(差分ゼロ)。差分は未規定トークン(速度色)に局在。
        Assert.Equal(0, outsideTintDiff);
        Assert.True(diff > 0);
    }
}
