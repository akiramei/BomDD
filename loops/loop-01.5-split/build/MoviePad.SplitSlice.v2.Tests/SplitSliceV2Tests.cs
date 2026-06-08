using System.Collections.Immutable;
using MoviePad.Models;
using MoviePad.Slice;
using Xunit;

namespace MoviePad.SplitSlice.v2.Tests;

/// <summary>
/// Loop1.5 隠しオラクル。Loop1 の14ケース + 改善①の中間値丸めテスト(計15)。
/// 製造装置(v2)には未開示。1回目から全green なら CHEAT-004/005 消滅。
/// </summary>
public class SplitSliceV2Tests
{
    private const double Fps = 30;

    private static DocumentState Sample() => new(
        TrimStart: 6,
        TrimEnd: 132,
        Regions: ImmutableList.Create(
            new RegionData(1, 6, 40, 1.0, true),
            new RegionData(2, 40, 64, 2.0, true),
            new RegionData(3, 64, 104, 1.0, true),
            new RegionData(4, 104, 132, 0.5, true)));

    // ---- 改善①: 中間値丸め(ToEven)の被覆。Loop1 の製造物(AwayFromZero)ならここで落ちる ----
    [Fact] // AC-5 完全性
    public void SnapFrame_Midpoint_RoundsToEven()
    {
        Assert.Equal(0.0, TimeMath.SnapFrame(0.25, 2)); // 0.5 → 偶数 0
        Assert.Equal(1.0, TimeMath.SnapFrame(1.25, 2)); // 2.5 → 偶数 2
        Assert.Equal(1.0, TimeMath.SnapFrame(0.75, 2)); // 1.5 → 偶数 2
    }

    // ---- ドメイン(移植) ----
    [Fact]
    public void ForClip_CreatesSingleSpanningRegion()
    {
        var d = DocumentState.ForClip(120);
        Assert.Equal(0.0, d.TrimStart);
        Assert.Equal(120.0, d.TrimEnd);
        var r = Assert.Single(d.Regions);
        Assert.Equal(0.0, r.Start);
        Assert.Equal(120.0, r.End);
        Assert.Equal(1.0, r.Speed);
        Assert.True(r.PreservePitch);
    }

    [Fact]
    public void RegionAt_ReturnsContainingRegion()
    {
        var d = Sample();
        Assert.Equal(2, d.RegionAt(50)!.Id);
        Assert.Equal(1, d.RegionAt(6)!.Id);
        Assert.Null(d.RegionAt(5));
        Assert.Null(d.RegionAt(133));
    }

    [Fact]
    public void RegionAt_BoundaryTime_BelongsToLaterRegion()
    {
        var d = Sample();
        Assert.Equal(2, d.RegionAt(40)!.Id);
        Assert.Equal(3, d.RegionAt(64)!.Id);
        Assert.Equal(4, d.RegionAt(104)!.Id);
        Assert.Equal(1, d.RegionAt(6)!.Id);
        Assert.Equal(4, d.RegionAt(132)!.Id);
    }

    [Fact]
    public void SplitAt_ValidPlayhead_AddsRegionInheritingSpeedAndPitch()
    {
        var d = Sample();
        var split = d.SplitAt(50, newId: 999, Fps);
        Assert.NotNull(split);
        Assert.Equal(5, split!.Regions.Count);
        var left = split.FindById(2)!;
        var right = split.FindById(999)!;
        Assert.Equal(40.0, left.Start);
        Assert.Equal(50.0, left.End);
        Assert.Equal(50.0, right.Start);
        Assert.Equal(64.0, right.End);
        Assert.Equal(2.0, left.Speed);
        Assert.Equal(2.0, right.Speed);
        Assert.True(right.PreservePitch);
    }

    [Fact]
    public void SplitAt_TooCloseToEdge_ReturnsNull()
    {
        var d = Sample();
        Assert.Null(d.SplitAt(40.2, 999, Fps));
        Assert.Null(d.SplitAt(63.8, 999, Fps));
        Assert.Null(d.SplitAt(200, 999, Fps));
    }

    [Fact]
    public void CanSplitAt_RespectsMinLen()
    {
        var d = Sample();
        Assert.True(d.CanSplitAt(50));
        Assert.False(d.CanSplitAt(40.2));
        Assert.False(d.CanSplitAt(5));
    }

    [Fact]
    public void SplitAt_InheritsVolume()
    {
        var d = new DocumentState(6, 132, ImmutableList.Create(
            new RegionData(1, 6, 40, 1.0, true),
            new RegionData(2, 40, 64, 2.0, true, false, 0.4),
            new RegionData(3, 64, 104, 1.0, true),
            new RegionData(4, 104, 132, 0.5, true)));
        var split = d.SplitAt(50, newId: 999, Fps);
        Assert.NotNull(split);
        Assert.Equal(0.4, split!.FindById(2)!.Volume, 3);
        Assert.Equal(0.4, split.FindById(999)!.Volume, 3);
    }

    [Fact]
    public void SplitAt_DoesNotMutateOriginal()
    {
        var d = Sample();
        var before = d.Regions.Count;
        _ = d.SplitAt(50, 999, Fps);
        Assert.Equal(before, d.Regions.Count);
        Assert.Equal(2.0, d.FindById(2)!.Speed);
        Assert.Null(d.FindById(999));
    }

    [Fact]
    public void ResolveSelection_SnapsToPlayheadRegion()
    {
        var d = Sample();
        Assert.Equal(2, d.ResolveSelection(current: 999, playhead: 50));
        Assert.Equal(1, d.ResolveSelection(current: 2, playhead: 20));
    }

    [Fact]
    public void ResolveSelection_RecoversAfterSplitUndo()
    {
        var d = Sample();
        Assert.Null(d.FindById(100));
        Assert.Equal(1, d.ResolveSelection(current: 100, playhead: 20));
    }

    // ---- SplitController(REQ由来 受入) ----
    [Fact]
    public void Controller_Split_SelectsNewLaterRegion()
    {
        var c = new SplitController(Sample(), Fps) { Playhead = 50 };
        Assert.True(c.CanSplit);
        c.Split();
        Assert.Equal(5, c.State.Regions.Count);
        Assert.True(c.CanUndo);
        Assert.NotNull(c.SelectedId);
        var sel = c.State.FindById(c.SelectedId!.Value)!;
        Assert.Equal(50.0, sel.Start);
        Assert.Equal(64.0, sel.End);
    }

    [Fact]
    public void Controller_Split_WhenCannot_NoChange()
    {
        var c = new SplitController(Sample(), Fps) { Playhead = 40.2 };
        Assert.False(c.CanSplit);
        var before = c.State;
        c.Split();
        Assert.Same(before, c.State);
        Assert.False(c.CanUndo);
    }

    [Fact]
    public void Controller_UndoRedo_RoundTrips()
    {
        var c = new SplitController(Sample(), Fps) { Playhead = 50 };
        c.Split();
        Assert.Equal(5, c.State.Regions.Count);
        c.Undo();
        Assert.Equal(4, c.State.Regions.Count);
        Assert.True(c.CanRedo);
        c.Redo();
        Assert.Equal(5, c.State.Regions.Count);
    }

    [Fact] // AC-12 / NFR-SPLIT-2: 単調増加(Undoを挟んでも巻き戻らない)— Loop1.5では1回目から通るはず
    public void Controller_NewIds_MonotonicAcrossUndo()
    {
        var c = new SplitController(Sample(), Fps) { Playhead = 50 };
        c.Split();
        int first = c.SelectedId!.Value;
        c.Undo();
        c.Playhead = 50;
        c.Split();
        int second = c.SelectedId!.Value;
        Assert.True(second > first,
            $"単調増加(NFR-SPLIT-2)に反する: first={first}, second={second}");
    }
}
