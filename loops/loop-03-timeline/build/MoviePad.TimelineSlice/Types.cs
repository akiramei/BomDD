namespace MoviePad.Timeline;

/// <summary>Axis-aligned rectangle in pixel space.</summary>
public readonly record struct Rect(double X, double Y, double W, double H);

/// <summary>A timeline region (clip segment) with playback attributes.</summary>
public sealed record RegionData(
    int Id,
    double Start,
    double End,
    double Speed,
    bool PreservePitch,
    bool Excluded = false,
    double Volume = 1.0)
{
    /// <summary>True when the playback speed is effectively 1.0 (|Speed-1| &lt; 0.001).</summary>
    public bool IsNormalSpeed => System.Math.Abs(Speed - 1.0) < 0.001;
}

/// <summary>Immutable document state for the timeline slice.</summary>
public sealed record DocState(
    double TrimStart,
    double TrimEnd,
    System.Collections.Immutable.ImmutableList<RegionData> Regions);
