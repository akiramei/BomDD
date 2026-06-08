using System.Collections.Immutable;

namespace MoviePad.Models;

/// <summary>
/// ドキュメント全体の不変状態。トリム範囲と、隙間なく順序付きで敷き詰まった区間列を保持する。
/// 不変条件: region[i].End == region[i+1].Start。全編集操作は新インスタンスを返す。
/// </summary>
public sealed record DocumentState(
    double TrimStart,
    double TrimEnd,
    ImmutableList<RegionData> Regions)
{
    /// <summary>
    /// クリップ全体を 1 区間で覆う初期状態を生成する。
    /// 区間: [0, duration]、speed=1.0、pitch=true、id=<paramref name="firstId"/>。
    /// </summary>
    public static DocumentState ForClip(double duration, int firstId = 1)
    {
        var region = new RegionData(
            Id: firstId,
            Start: 0.0,
            End: duration,
            Speed: 1.0,
            PreservePitch: true,
            Excluded: false,
            Volume: 1.0);
        return new DocumentState(
            TrimStart: 0.0,
            TrimEnd: duration,
            Regions: ImmutableList.Create(region));
    }

    /// <summary>
    /// 時刻 <paramref name="t"/> 直下の区間を返す。半開区間 [Start, End) で判定し、
    /// 境界時刻は後続区間に属する。最終区間のみ t==End を拾う。
    /// トリム範囲外(t&lt;TrimStart または t&gt;TrimEnd)は null。
    /// </summary>
    public RegionData? RegionAt(double t)
    {
        if (t < TrimStart || t > TrimEnd) return null;
        if (Regions.Count == 0) return null;

        for (int i = 0; i < Regions.Count; i++)
        {
            var r = Regions[i];
            bool isLast = i == Regions.Count - 1;
            if (t >= r.Start && (t < r.End || (isLast && t <= r.End)))
            {
                return r;
            }
        }
        return null;
    }

    /// <summary>指定 Id の区間を返す。無ければ null。</summary>
    public RegionData? FindById(int id)
    {
        foreach (var r in Regions)
        {
            if (r.Id == id) return r;
        }
        return null;
    }

    /// <summary>指定 Id の区間のインデックスを返す。無ければ -1。</summary>
    public int IndexOfId(int id)
    {
        for (int i = 0; i < Regions.Count; i++)
        {
            if (Regions[i].Id == id) return i;
        }
        return -1;
    }

    /// <summary>
    /// 再生ヘッド <paramref name="playhead"/> で分割可能か。
    /// 直下区間 r が在り、かつ ph &gt; r.Start + MinLen かつ ph &lt; r.End - MinLen のときだけ true。
    /// </summary>
    public bool CanSplitAt(double playhead)
    {
        var r = RegionAt(playhead);
        if (r is null) return false;
        return playhead > r.Start + TimeMath.MinLen
            && playhead < r.End - TimeMath.MinLen;
    }

    /// <summary>
    /// 再生ヘッドで対象区間を左=[start, ph] と右=[ph, end] の 2 区間に分割した新状態を返す。
    /// 分割位置決定の前に playhead を <see cref="TimeMath.SnapFrame"/> でフレームグリッドへスナップする。
    /// スナップ後の値が区間の端から MinLen 以内、または直下に区間が無い場合は null を返し何も変えない。
    /// 右区間は Id=<paramref name="newId"/>、左の Speed/PreservePitch/Volume を継承(Excluded も継承)。
    /// </summary>
    public DocumentState? SplitAt(double playhead, int newId, double fps)
    {
        double ph = TimeMath.SnapFrame(playhead, fps);

        // スナップ後の値で判定する。
        if (!CanSplitAt(ph)) return null;

        var r = RegionAt(ph);
        if (r is null) return null; // CanSplitAt が true なら到達しないが防御的に。

        int idx = IndexOfId(r.Id);
        if (idx < 0) return null;

        var left = r with { End = ph };
        var right = r with { Id = newId, Start = ph };

        var newRegions = Regions
            .SetItem(idx, left)
            .Insert(idx + 1, right);

        return this with { Regions = newRegions };
    }

    /// <summary>
    /// 選択を解決する。
    /// 再生ヘッド直下に区間が在ればその Id。無ければ current が生存していれば current 維持。
    /// それも無効なら先頭区間 Id(区間が無ければ null)。
    /// </summary>
    public int? ResolveSelection(int? current, double playhead)
    {
        var under = RegionAt(playhead);
        if (under is not null) return under.Id;

        if (current is int c && FindById(c) is not null) return c;

        if (Regions.Count > 0) return Regions[0].Id;

        return null;
    }
}
