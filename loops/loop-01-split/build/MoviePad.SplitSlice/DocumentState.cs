using System.Collections.Immutable;

namespace MoviePad.Models;

/// <summary>
/// Immutable document state: a trim range plus a gap-free, ordered list of regions.
/// Invariant: regions tile [TrimStart, TrimEnd] with region[i].End == region[i+1].Start.
/// All edit operations return new instances; existing instances are never mutated.
/// </summary>
public sealed record DocumentState(
    double TrimStart,
    double TrimEnd,
    ImmutableList<RegionData> Regions)
{
    /// <summary>
    /// Builds the initial state for a clip of the given <paramref name="duration"/>:
    /// a single region [0, duration] with speed 1.0 and pitch preservation enabled.
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
        return new DocumentState(0.0, duration, ImmutableList.Create(region));
    }

    /// <summary>
    /// Returns the region containing time <paramref name="t"/>, or null.
    /// Outside the trim range (t &lt; TrimStart or t &gt; TrimEnd) returns null.
    /// Half-open semantics: a boundary time belongs to the following region;
    /// only the final region includes its own End.
    /// </summary>
    public RegionData? RegionAt(double t)
    {
        if (t < TrimStart || t > TrimEnd)
            return null;

        int count = Regions.Count;
        for (int i = 0; i < count; i++)
        {
            var r = Regions[i];
            bool isLast = i == count - 1;
            if (isLast)
            {
                // Final region includes its End.
                if (t >= r.Start && t <= r.End)
                    return r;
            }
            else
            {
                // Half-open [Start, End): boundary belongs to the following region.
                if (t >= r.Start && t < r.End)
                    return r;
            }
        }
        return null;
    }

    /// <summary>Finds a region by Id, or null if none exists.</summary>
    public RegionData? FindById(int id)
    {
        foreach (var r in Regions)
        {
            if (r.Id == id)
                return r;
        }
        return null;
    }

    /// <summary>Returns the index of the region with the given Id, or -1.</summary>
    public int IndexOfId(int id)
    {
        for (int i = 0; i < Regions.Count; i++)
        {
            if (Regions[i].Id == id)
                return i;
        }
        return -1;
    }

    /// <summary>
    /// True only when a region lies directly under <paramref name="playhead"/> and the
    /// playhead is more than MinLen away from both of that region's edges.
    /// </summary>
    public bool CanSplitAt(double playhead)
    {
        var r = RegionAt(playhead);
        if (r is null)
            return false;
        return playhead > r.Start + TimeMath.MinLen
            && playhead < r.End - TimeMath.MinLen;
    }

    /// <summary>
    /// Splits the region under <paramref name="playhead"/> into a left part [start, ph]
    /// and a right part [ph, end]. The playhead is snapped to the frame grid first.
    /// Returns a new state, or null when the split is invalid (too close to an edge,
    /// or no region directly under the snapped playhead).
    /// </summary>
    public DocumentState? SplitAt(double playhead, int newId, double fps)
    {
        double ph = TimeMath.SnapFrame(playhead, fps);

        if (!CanSplitAt(ph))
            return null;

        var target = RegionAt(ph);
        if (target is null)
            return null;

        int index = IndexOfId(target.Id);
        if (index < 0)
            return null;

        var left = target with { End = ph };
        var right = target with { Id = newId, Start = ph };

        var newRegions = Regions
            .SetItem(index, left)
            .Insert(index + 1, right);

        return this with { Regions = newRegions };
    }

    /// <summary>
    /// Resolves which region Id should be selected:
    /// 1) the region under <paramref name="playhead"/> if any;
    /// 2) otherwise <paramref name="current"/> if it still refers to a live region;
    /// 3) otherwise the first region's Id, or null when there are no regions.
    /// </summary>
    public int? ResolveSelection(int? current, double playhead)
    {
        var under = RegionAt(playhead);
        if (under is not null)
            return under.Id;

        if (current is int cur && FindById(cur) is not null)
            return cur;

        if (Regions.Count > 0)
            return Regions[0].Id;

        return null;
    }
}
