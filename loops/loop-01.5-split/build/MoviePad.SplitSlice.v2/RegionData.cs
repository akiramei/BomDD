namespace MoviePad.Models;

/// <summary>
/// 1 つの再生区間を表す不変レコード。
/// 半開区間 [<see cref="Start"/>, <see cref="End"/>) として扱う(最終区間のみ終端を含む)。
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
    /// <summary>区間の長さ(End - Start)。</summary>
    public double Duration => End - Start;
}
