using System.Collections.Immutable;

namespace MoviePad.Models;

/// <summary>
/// 入力クリップのメタ情報。元 internal 相当だがすべて public。
/// </summary>
public sealed record ClipInfo(
    string Path,
    string FileName,
    double Duration,
    int Width,
    int Height,
    double Fps,
    string VideoCodec,
    string AudioCodec,
    int SampleRate = 48000,
    bool IsVariableFrameRate = false)
{
    /// <summary>
    /// AudioCodec が "—"(em dash, U+2014)でも "" でもないとき true。
    /// </summary>
    public bool HasAudio => AudioCodec is not ("—" or "");
}

/// <summary>
/// 1 つの編集区間。
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
    public double Duration => End - Start;

    public bool IsNormalSpeed => Math.Abs(Speed - 1.0) < 0.001;

    public bool IsFullVolume => Math.Abs(Volume - 1.0) < 0.001;

    public bool IsMuted => Volume < 0.001;
}

/// <summary>
/// 文書状態(トリム範囲と区間集合)。
/// </summary>
public sealed record DocumentState(
    double TrimStart,
    double TrimEnd,
    ImmutableList<RegionData> Regions);

/// <summary>
/// 出力形式。
/// </summary>
public enum ExportFormat
{
    Mp4,
    Lossless,
    ProRes
}
