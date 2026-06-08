using MoviePad.Models;

namespace MoviePad.Services;

/// <summary>
/// 書き出し計画。Unit A の規則を忠実に実装する。
/// </summary>
public sealed record ExportPlan(
    bool NeedsScale,
    bool NeedsRerate,
    bool VideoCopyEligible,
    bool AudioCopyEligible,
    bool SingleSpan,
    double SpanStart,
    double SpanEnd)
{
    /// <summary>
    /// VideoCopyEligible &amp;&amp; AudioCopyEligible &amp;&amp; SingleSpan のとき、
    /// stream copy が可能。
    /// </summary>
    public bool CanStreamCopy => VideoCopyEligible && AudioCopyEligible && SingleSpan;

    private const double SpanEpsilon = 1e-4;
    private const double FpsEpsilon = 0.05;

    /// <summary>
    /// Request からエクスポート計画を算出する。
    /// </summary>
    public static ExportPlan Analyze(FfmpegExporter.Request req)
    {
        var clip = req.Clip;
        var doc = req.Doc;

        // ---- スパン算出 ----
        // Regions を順に見る。Excluded はスキップ。
        // s = max(Start, TrimStart), e = min(End, TrimEnd)。
        // e - s <= 1e-4 はスキップ。
        // 「先頭、または s が直前の e より 1e-4 超で後ろ」のとき新スパン開始。
        int spanCount = 0;
        double spanStart = 0.0;
        double spanEnd = 0.0;
        bool sawAny = false;
        double prevEnd = 0.0;

        foreach (var r in doc.Regions)
        {
            if (r.Excluded)
                continue;

            double s = Math.Max(r.Start, doc.TrimStart);
            double e = Math.Min(r.End, doc.TrimEnd);
            if (e - s <= SpanEpsilon)
                continue;

            bool newSpan = !sawAny || (s > prevEnd + SpanEpsilon);
            if (newSpan)
            {
                spanCount++;
                if (!sawAny)
                    spanStart = s; // 最初のスパンの s が SpanStart
            }

            prevEnd = e;
            sawAny = true;
        }

        spanEnd = sawAny ? prevEnd : 0.0; // 最後に見た e が SpanEnd
        bool singleSpan = spanCount == 1;

        // ---- スケール判定 ----
        bool needsScale = (req.OutWidth != clip.Width) || (req.OutHeight != clip.Height);

        // ---- fps 変更 ----
        bool fpsChange = Math.Abs(req.OutFps - clip.Fps) > FpsEpsilon;

        // ---- 速度変更 / 音量変更(非除外区間)----
        bool anySpeedChange = false;
        bool anyVolumeChange = false;
        foreach (var r in doc.Regions)
        {
            if (r.Excluded)
                continue;
            if (!r.IsNormalSpeed)
                anySpeedChange = true;
            if (!r.IsFullVolume)
                anyVolumeChange = true;
        }

        // ---- 再レート ----
        bool needsRerate = anySpeedChange || fpsChange || clip.IsVariableFrameRate;

        // ---- mp4 ----
        bool mp4 = req.Format == ExportFormat.Mp4;

        // ---- コピー白名簿 ----
        bool videoCopyEligible =
            mp4
            && !needsScale
            && !anySpeedChange
            && !fpsChange
            && IsMp4Video(clip.VideoCodec);

        bool audioCopyEligible =
            !clip.HasAudio
            || (mp4
                && !anySpeedChange
                && !anyVolumeChange
                && IsMp4Audio(clip.AudioCodec));

        return new ExportPlan(
            NeedsScale: needsScale,
            NeedsRerate: needsRerate,
            VideoCopyEligible: videoCopyEligible,
            AudioCopyEligible: audioCopyEligible,
            SingleSpan: singleSpan,
            SpanStart: spanStart,
            SpanEnd: spanEnd);
    }

    /// <summary>コピー可能な MP4 映像コーデック白名簿。</summary>
    private static bool IsMp4Video(string c) => c is "H.264" or "H.265";

    /// <summary>コピー可能な MP4 音声コーデック白名簿。</summary>
    private static bool IsMp4Audio(string c) => c is "AAC" or "MP3" or "AC-3";
}
