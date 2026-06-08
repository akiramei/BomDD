namespace MoviePad.Models;

/// <summary>
/// Time-domain math helpers shared by the slicing model.
/// </summary>
public static class TimeMath
{
    /// <summary>Minimum usable length of a region (seconds).</summary>
    public const double MinLen = 0.5;

    /// <summary>Default frames-per-second used when an invalid fps is supplied.</summary>
    public const double DefaultFps = 30.0;

    /// <summary>
    /// Clamps <paramref name="v"/> into the inclusive range [<paramref name="a"/>, <paramref name="b"/>].
    /// </summary>
    public static double Clamp(double v, double a, double b)
    {
        if (v < a) return a;
        if (v > b) return b;
        return v;
    }

    /// <summary>
    /// Snaps a time value onto the frame grid defined by <paramref name="fps"/>.
    /// When <paramref name="fps"/> &lt;= 0, <see cref="DefaultFps"/> is used.
    /// </summary>
    public static double SnapFrame(double t, double fps)
    {
        double effectiveFps = fps <= 0 ? DefaultFps : fps;
        return Math.Round(t * effectiveFps, MidpointRounding.AwayFromZero) / effectiveFps;
    }
}
