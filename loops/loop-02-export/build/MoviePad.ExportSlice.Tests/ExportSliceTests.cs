using System.Collections.Immutable;
using MoviePad.Models;
using MoviePad.Services;
using Xunit;

namespace MoviePad.ExportSlice.Tests;

/// <summary>
/// Loop2 隠しオラクル。原版 ExportPlanTests を移植(slice の public 面に対して)。
/// Unit A(plan フラグ)= 規則ベース / Unit B(filter/args 文字列)= 外部ツール文法。
/// 製造装置(ExportSlice)には未開示。どの assertion が通り/落ちるかで C2/外部文法ギャップを測る。
/// </summary>
public class ExportSliceTests
{
    private static ClipInfo Clip(int w = 1920, int h = 1080, double fps = 30,
        string vcodec = "H.264", string acodec = "AAC", bool vfr = false)
        => new("in.mp4", "in.mp4", 10, w, h, fps, vcodec, acodec, 48000, vfr);

    private static DocumentState SingleRegion(double speed = 1.0, double dur = 10)
        => new(0, dur, ImmutableList.Create(new RegionData(1, 0, dur, speed, true)));

    private static FfmpegExporter.Request Req(ClipInfo clip, DocumentState doc,
        int outW, int outH, double outFps, ExportFormat fmt = ExportFormat.Mp4)
        => new(clip, doc, outW, outH, fmt, "out.mp4", outFps);

    private static int InputCount(string args)
        => args.Split(new[] { "-i \"" }, StringSplitOptions.None).Length - 1;

    // ===== Unit A: ExportPlan.Analyze(plan フラグ) =====

    [Fact] public void A01_Identity_NoScaleNoRerate_CanCopy()
    {
        var plan = ExportPlan.Analyze(Req(Clip(), SingleRegion(), 1920, 1080, 30));
        Assert.False(plan.NeedsScale); Assert.False(plan.NeedsRerate);
        Assert.True(plan.SingleSpan); Assert.True(plan.CanStreamCopy);
    }
    [Fact] public void A02_DifferentResolution_NeedsScale_NoCopy()
    {
        var plan = ExportPlan.Analyze(Req(Clip(), SingleRegion(), 1280, 720, 30));
        Assert.True(plan.NeedsScale); Assert.False(plan.CanStreamCopy);
    }
    [Fact] public void A03_FpsChange_NeedsRerate_NoCopy()
    {
        var plan = ExportPlan.Analyze(Req(Clip(fps: 30), SingleRegion(), 1920, 1080, 60));
        Assert.True(plan.NeedsRerate); Assert.False(plan.CanStreamCopy);
    }
    [Fact] public void A04_SpeedChange_NeedsRerate_NoCopy()
    {
        var plan = ExportPlan.Analyze(Req(Clip(), SingleRegion(speed: 2.0), 1920, 1080, 30));
        Assert.True(plan.NeedsRerate); Assert.False(plan.CanStreamCopy);
    }
    [Fact] public void A05_VfrSource_SameSettings_CanCopy()
    {
        var plan = ExportPlan.Analyze(Req(Clip(vfr: true), SingleRegion(), 1920, 1080, 30));
        Assert.True(plan.NeedsRerate); Assert.True(plan.VideoCopyEligible); Assert.True(plan.CanStreamCopy);
    }
    [Fact] public void A06_VfrSource_WithFpsChange_NoCopy()
    {
        var plan = ExportPlan.Analyze(Req(Clip(fps: 30, vfr: true), SingleRegion(), 1920, 1080, 60));
        Assert.False(plan.CanStreamCopy);
    }
    [Fact] public void A07_VfrSource_WithSpeedChange_NoCopy()
    {
        var plan = ExportPlan.Analyze(Req(Clip(vfr: true), SingleRegion(speed: 2.0), 1920, 1080, 30));
        Assert.False(plan.CanStreamCopy);
    }
    [Fact] public void A08_ExcludedMiddle_TwoSpans_NoCopy()
    {
        var doc = new DocumentState(0, 10, ImmutableList.Create(
            new RegionData(1, 0, 3, 1.0, true),
            new RegionData(2, 3, 6, 1.0, true, Excluded: true),
            new RegionData(3, 6, 10, 1.0, true)));
        var plan = ExportPlan.Analyze(Req(Clip(), doc, 1920, 1080, 30));
        Assert.False(plan.SingleSpan); Assert.False(plan.CanStreamCopy);
    }
    [Fact] public void A09_TrimOnly_SingleSpan_SpanMatchesTrim()
    {
        var doc = new DocumentState(2, 8, ImmutableList.Create(new RegionData(1, 2, 8, 1.0, true)));
        var plan = ExportPlan.Analyze(Req(Clip(), doc, 1920, 1080, 30));
        Assert.True(plan.SingleSpan); Assert.Equal(2, plan.SpanStart, 3); Assert.Equal(8, plan.SpanEnd, 3);
        Assert.True(plan.CanStreamCopy);
    }
    [Fact] public void A10_MultipleAdjacentRegions_AllNormalSpeed_SingleSpan_CanCopy()
    {
        var doc = new DocumentState(0, 10, ImmutableList.Create(
            new RegionData(1, 0, 4, 1.0, true), new RegionData(2, 4, 10, 1.0, true)));
        var plan = ExportPlan.Analyze(Req(Clip(), doc, 1920, 1080, 30));
        Assert.True(plan.SingleSpan); Assert.True(plan.CanStreamCopy);
    }
    [Fact] public void A11_NonMp4Format_NoCopy()
    {
        var plan = ExportPlan.Analyze(Req(Clip(), SingleRegion(), 1920, 1080, 30, ExportFormat.Lossless));
        Assert.False(plan.CanStreamCopy);
    }
    [Fact] public void A12_NonMp4Codec_NoCopy()
    {
        var plan = ExportPlan.Analyze(Req(Clip(vcodec: "VP9", acodec: "Opus"), SingleRegion(), 1920, 1080, 30));
        Assert.False(plan.VideoCopyEligible); Assert.False(plan.CanStreamCopy);
    }
    [Fact] public void A13_NoAudio_AudioCopyEligible()
    {
        var plan = ExportPlan.Analyze(Req(Clip(acodec: "—"), SingleRegion(), 1920, 1080, 30));
        Assert.True(plan.AudioCopyEligible); Assert.True(plan.CanStreamCopy);
    }
    [Fact] public void A14_VolumeChange_DisablesAudioCopy_NoStreamCopy()
    {
        var doc = new DocumentState(0, 10, ImmutableList.Create(new RegionData(1, 0, 10, 1.0, true, Volume: 0.5)));
        var plan = ExportPlan.Analyze(Req(Clip(), doc, 1920, 1080, 30));
        Assert.False(plan.AudioCopyEligible); Assert.False(plan.CanStreamCopy); Assert.True(plan.VideoCopyEligible);
    }
    [Fact] public void A15_MutedRegion_DisablesStreamCopy()
    {
        var doc = new DocumentState(0, 10, ImmutableList.Create(new RegionData(1, 0, 10, 1.0, true, Volume: 0.0)));
        var plan = ExportPlan.Analyze(Req(Clip(), doc, 1920, 1080, 30));
        Assert.False(plan.CanStreamCopy);
    }

    // ===== Unit B: filter_complex / args(文字列) =====

    [Fact] public void B01_FilterGraph_Identity_OmitsScaleAndFps()
    {
        var req = Req(Clip(), SingleRegion(), 1920, 1080, 30);
        var plan = ExportPlan.Analyze(req);
        string f = FfmpegExporter.BuildFilterGraph(req, plan, req.Clip.HasAudio, 0, out int seg);
        Assert.True(seg > 0);
        Assert.DoesNotContain("scale=", f);
        Assert.DoesNotContain("fps=", f);
        Assert.Contains("[cv]null[vout]", f);
    }
    [Fact] public void B02_FilterGraph_ScaleChange_ContainsScale()
    {
        var req = Req(Clip(), SingleRegion(), 1280, 720, 30);
        var plan = ExportPlan.Analyze(req);
        string f = FfmpegExporter.BuildFilterGraph(req, plan, req.Clip.HasAudio, 0, out _);
        Assert.Contains("scale=1280:720", f);
    }
    [Fact] public void B03_FilterGraph_SpeedChange_ContainsFps()
    {
        var req = Req(Clip(), SingleRegion(speed: 2.0), 1920, 1080, 30);
        var plan = ExportPlan.Analyze(req);
        string f = FfmpegExporter.BuildFilterGraph(req, plan, req.Clip.HasAudio, 0, out _);
        Assert.Contains("fps=", f);
    }
    [Fact] public void B04_FilterGraph_VfrSource_ContainsFps_EvenAtSameRate()
    {
        var req = Req(Clip(vfr: true), SingleRegion(), 1920, 1080, 30);
        var plan = ExportPlan.Analyze(req);
        string f = FfmpegExporter.BuildFilterGraph(req, plan, req.Clip.HasAudio, 0, out _);
        Assert.Contains("fps=", f);
    }
    [Fact] public void B05_FilterGraph_VolumeChange_ContainsVolumeFilter()
    {
        var doc = new DocumentState(0, 10, ImmutableList.Create(new RegionData(1, 0, 10, 1.0, true, Volume: 0.5)));
        var req = Req(Clip(), doc, 1920, 1080, 30);
        var plan = ExportPlan.Analyze(req);
        string f = FfmpegExporter.BuildFilterGraph(req, plan, req.Clip.HasAudio, 0, out _);
        Assert.Contains("volume=0.5", f);
    }
    [Fact] public void B06_FilterGraph_FullVolume_OmitsVolumeFilter()
    {
        var req = Req(Clip(), SingleRegion(), 1920, 1080, 30);
        var plan = ExportPlan.Analyze(req);
        string f = FfmpegExporter.BuildFilterGraph(req, plan, req.Clip.HasAudio, 0, out _);
        Assert.DoesNotContain("volume=", f);
    }
    [Fact] public void B07_FilterGraph_Muted_ContainsVolumeZero()
    {
        var doc = new DocumentState(0, 10, ImmutableList.Create(new RegionData(1, 0, 10, 1.0, true, Volume: 0.0)));
        var req = Req(Clip(), doc, 1920, 1080, 30);
        var plan = ExportPlan.Analyze(req);
        string f = FfmpegExporter.BuildFilterGraph(req, plan, req.Clip.HasAudio, 0, out _);
        Assert.Contains("volume=0", f);
    }
    [Fact] public void B08_FilterGraph_Seeked_OffsetsVideo_AndAudioFromSecondInput()
    {
        var doc = new DocumentState(5, 10, ImmutableList.Create(new RegionData(1, 5, 10, 1.0, true)));
        var req = Req(Clip(), doc, 1920, 1080, 30);
        var plan = ExportPlan.Analyze(req);
        string f = FfmpegExporter.BuildFilterGraph(req, plan, req.Clip.HasAudio, 5.0, out int seg);
        Assert.True(seg > 0);
        Assert.Contains("[0:v]trim=start=0:end=5", f);
        Assert.Contains("[1:a]atrim=start=5:end=10", f);
    }
    [Fact] public void B09_FilterGraph_NoSeek_AbsoluteTimes_FirstInput()
    {
        var doc = new DocumentState(5, 10, ImmutableList.Create(new RegionData(1, 5, 10, 1.0, true)));
        var req = Req(Clip(), doc, 1920, 1080, 30);
        var plan = ExportPlan.Analyze(req);
        string f = FfmpegExporter.BuildFilterGraph(req, plan, req.Clip.HasAudio, 0, out _);
        Assert.Contains("[0:v]trim=start=5:end=10", f);
        Assert.Contains("[0:a]atrim=start=5:end=10", f);
    }
    [Fact] public void B10_FilterArgs_FrontTrim_AddsInputSeek_AndSecondAudioInput()
    {
        var req = Req(Clip(), SingleRegion(), 1920, 1080, 30);
        string a = FfmpegExporter.BuildFilterArgs(req, 5.0, "x", hasAudio: true);
        Assert.Contains("-ss 5", a);
        Assert.Equal(2, InputCount(a));
    }
    [Fact] public void B11_FilterArgs_NoFrontTrim_SingleInput_NoSeek()
    {
        var req = Req(Clip(), SingleRegion(), 1920, 1080, 30);
        string a = FfmpegExporter.BuildFilterArgs(req, 0, "x", hasAudio: true);
        Assert.DoesNotContain("-ss ", a);
        Assert.Equal(1, InputCount(a));
    }
    [Fact] public void B12_FilterArgs_FrontTrim_NoAudio_SingleSeekedInput()
    {
        var req = Req(Clip(acodec: "—"), SingleRegion(), 1920, 1080, 30);
        string a = FfmpegExporter.BuildFilterArgs(req, 5.0, "x", hasAudio: false);
        Assert.Contains("-ss 5", a);
        Assert.Equal(1, InputCount(a));
    }
    [Fact] public void B13_CopyArgs_UsesStreamCopy_NoFilter()
    {
        var doc = new DocumentState(2, 8, ImmutableList.Create(new RegionData(1, 2, 8, 1.0, true)));
        var req = Req(Clip(), doc, 1920, 1080, 30) with { FastCopy = true };
        var plan = ExportPlan.Analyze(req);
        string a = FfmpegExporter.BuildCopyArgs(req, plan, req.Clip.HasAudio);
        Assert.Contains("-c copy", a);
        Assert.Contains("-ss 2", a);
        Assert.DoesNotContain("-filter_complex", a);
    }
    [Fact] public void B14_CopyArgs_WithKeyframeOverride_UsesEarlierStartAndExactEnd()
    {
        var doc = new DocumentState(2.1, 8, ImmutableList.Create(new RegionData(1, 2.1, 8, 1.0, true)));
        var req = Req(Clip(), doc, 1920, 1080, 30) with { FastCopy = true, CopyStartOverride = 1.5 };
        var plan = ExportPlan.Analyze(req);
        string a = FfmpegExporter.BuildCopyArgs(req, plan, req.Clip.HasAudio);
        Assert.Contains("-ss 1.5", a);
        Assert.Contains("-t 6.5", a);
    }
    [Fact] public void B15_CopyArgs_InvalidOverride_FallsBackToSpanStart()
    {
        var doc = new DocumentState(2, 8, ImmutableList.Create(new RegionData(1, 2, 8, 1.0, true)));
        var req = Req(Clip(), doc, 1920, 1080, 30) with { FastCopy = true, CopyStartOverride = 5.0 };
        var plan = ExportPlan.Analyze(req);
        string a = FfmpegExporter.BuildCopyArgs(req, plan, req.Clip.HasAudio);
        Assert.Contains("-ss 2", a);
        Assert.DoesNotContain("-ss 5", a);
    }
}
