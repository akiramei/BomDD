namespace MoviePad.Models;

/// <summary>
/// An immutable region (slice) on the timeline. Half-open interval [Start, End).
/// </summary>
public sealed record RegionData(
    int Id,
    double Start,
    double End,
    double Speed,
    bool PreservePitch,
    bool Excluded = false,
    double Volume = 1.0)
{
    /// <summary>Length of the region in seconds.</summary>
    public double Duration => End - Start;
}
