namespace MoviePad.Timeline;

using System;

/// <summary>
/// Software rasterizer that paints the timeline into an RGBA8888 buffer
/// (row-major, 4 bytes per pixel: [R,G,B,255]).
/// </summary>
public static class TimelineRaster
{
    public static byte[] Render(
        DocState s, double playhead, double px, int width, int height,
        (byte r, byte g, byte b) canvasBg,
        (byte r, byte g, byte b) surface,
        (byte r, byte g, byte b) excluded,
        (byte r, byte g, byte b) trimMask,
        (byte r, byte g, byte b) boundary,
        (byte r, byte g, byte b) playheadColor)
    {
        var buf = new byte[width * height * 4];

        // 1. Canvas background over the whole frame.
        Fill(buf, width, height, new Rect(0, 0, width, height), canvasBg);

        // 2. Track surface.
        Fill(buf, width, height, new Rect(0, TimelineLayout.TrackTop, width, TimelineLayout.TrackH), surface);

        // 3. Speed tint: non-excluded, non-normal-speed regions.
        //    The tint color is NOT supplied by the BOM; it is derived from speed (see report).
        foreach (var r in s.Regions)
            if (!r.Excluded && !r.IsNormalSpeed)
                Fill(buf, width, height, TimelineLayout.RegionRect(r, px), SpeedTint(r.Speed));

        // 4. Excluded regions.
        foreach (var r in s.Regions)
            if (r.Excluded)
                Fill(buf, width, height, TimelineLayout.RegionRect(r, px), excluded);

        // 5. Trim masks (left + right).
        Fill(buf, width, height, TimelineLayout.TrimMaskLeft(s, px), trimMask);
        Fill(buf, width, height, TimelineLayout.TrimMaskRight(s, px, width), trimMask);

        // 6. Region boundaries.
        foreach (var x in TimelineLayout.BoundaryXs(s, px))
            Fill(buf, width, height, new Rect(x - 1, 33, 2, 86), boundary);

        // 7. Playhead.
        Fill(buf, width, height, new Rect(TimelineLayout.PlayheadX(playhead, px) - 1, 0, 2, height), playheadColor);

        return buf;
    }

    /// <summary>
    /// Speed-derived tint color (BOM-unspecified, invented here).
    ///
    /// Mapping rationale:
    ///   - Slowed footage (Speed &lt; 1)  -> cool blue family.
    ///   - Sped-up footage (Speed &gt; 1) -> warm orange/red family.
    /// The deviation from 1.0 (clamped to [0,1] at a 3x reference) drives
    /// saturation/intensity, so an extreme speed reads more strongly than a
    /// mild one. Channels are produced by simple linear interpolation between a
    /// neutral grey baseline and a fully-saturated hue, then rounded.
    /// </summary>
    internal static (byte r, byte g, byte b) SpeedTint(double speed)
    {
        // How far from normal speed, normalized so that a 3x change (e.g. 0.33x
        // or 3x) reaches full intensity. Clamped to [0,1].
        double deviation = Math.Min(1.0, Math.Abs(speed - 1.0) / 2.0);

        // Neutral grey baseline that the hue is blended away from.
        const double baseR = 120, baseG = 120, baseB = 120;

        double tr, tg, tb;
        if (speed < 1.0)
        {
            // Slow -> cool blue.
            tr = 40; tg = 110; tb = 230;
        }
        else
        {
            // Fast -> warm orange/red.
            tr = 230; tg = 110; tb = 40;
        }

        byte Lerp(double a, double b) => (byte)Math.Round(a + (b - a) * deviation);
        return (Lerp(baseR, tr), Lerp(baseG, tg), Lerp(baseB, tb));
    }

    /// <summary>
    /// Paints an integer-snapped rectangle with the given opaque color.
    /// Snap rule: x0=floor(X), x1=floor(X+W), y0=floor(Y), y1=floor(Y+H);
    /// columns [max(0,x0), min(width,x1)) and rows [max(0,y0), min(height,y1)).
    /// </summary>
    private static void Fill(byte[] buf, int width, int height, Rect rect, (byte r, byte g, byte b) color)
    {
        int x0 = (int)Math.Floor(rect.X);
        int x1 = (int)Math.Floor(rect.X + rect.W);
        int y0 = (int)Math.Floor(rect.Y);
        int y1 = (int)Math.Floor(rect.Y + rect.H);

        int cStart = Math.Max(0, x0);
        int cEnd = Math.Min(width, x1);
        int rStart = Math.Max(0, y0);
        int rEnd = Math.Min(height, y1);

        for (int row = rStart; row < rEnd; row++)
        {
            int rowBase = row * width * 4;
            for (int col = cStart; col < cEnd; col++)
            {
                int i = rowBase + col * 4;
                buf[i] = color.r;
                buf[i + 1] = color.g;
                buf[i + 2] = color.b;
                buf[i + 3] = 255;
            }
        }
    }
}
