namespace MoviePad.Models;

/// <summary>
/// 時刻に関する純粋な数学ユーティリティ。
/// </summary>
public static class TimeMath
{
    /// <summary>区間の最小長さ(秒)。</summary>
    public const double MinLen = 0.5;

    /// <summary>fps が不正(0 以下)の場合に用いる既定フレームレート。</summary>
    public const double DefaultFps = 30.0;

    /// <summary>
    /// 値 <paramref name="v"/> を閉区間 [<paramref name="a"/>, <paramref name="b"/>] にクランプする。
    /// </summary>
    public static double Clamp(double v, double a, double b)
    {
        if (v < a) return a;
        if (v > b) return b;
        return v;
    }

    /// <summary>
    /// 時刻 <paramref name="t"/> を、グリッド幅 1/fps 秒のフレームグリッド上の最近接フレームへ丸める。
    /// 中間値(ちょうど半フレーム)は偶数側へ丸める(<see cref="MidpointRounding.ToEven"/> =
    /// .NET の <c>Math.Round(double)</c> 既定の挙動)。
    /// <paramref name="fps"/> が 0 以下のときは <see cref="DefaultFps"/> を用いる。
    /// </summary>
    public static double SnapFrame(double t, double fps)
    {
        double f = fps <= 0 ? DefaultFps : fps;
        // フレーム番号へ変換 → 最近接整数(中間値は偶数側)へ丸め → 秒へ戻す。
        double frame = Math.Round(t * f);
        return frame / f;
    }
}
