namespace MoviePad.Timeline;

using System.Collections.Generic;

/// <summary>Pure geometry for timeline layout. All coordinates are in pixels.</summary>
public static class TimelineLayout
{
    public const double TrackTop = 30;
    public const double TrackH = 92;

    /// <summary>Maps a time value (seconds) to an x pixel coordinate.</summary>
    public static double X(double t, double px) => t * px;

    /// <summary>Rectangle for a region's body on the track.</summary>
    public static Rect RegionRect(RegionData r, double px)
        => new Rect(X(r.Start, px), TrackTop, X(r.End, px) - X(r.Start, px), TrackH);

    /// <summary>X position of the playhead.</summary>
    public static double PlayheadX(double playhead, double px) => X(playhead, px);

    /// <summary>Mask covering the trimmed-out region on the left.</summary>
    public static Rect TrimMaskLeft(DocState s, double px)
        => new Rect(0, TrackTop, X(s.TrimStart, px), TrackH);

    /// <summary>Mask covering the trimmed-out region on the right.</summary>
    public static Rect TrimMaskRight(DocState s, double px, double width)
        => new Rect(X(s.TrimEnd, px), TrackTop, width - X(s.TrimEnd, px), TrackH);

    /// <summary>X coordinates of the internal boundaries between adjacent regions.</summary>
    public static IReadOnlyList<double> BoundaryXs(DocState s, double px)
    {
        var result = new List<double>();
        for (int i = 0; i <= s.Regions.Count - 2; i++)
            result.Add(X(s.Regions[i].End, px));
        return result;
    }

    /// <summary>Snaps a target step (seconds) up to the next "nice" value.</summary>
    public static double NiceStep(double targetSec)
    {
        double[] steps = { 0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300 };
        foreach (var step in steps)
            if (step >= targetSec)
                return step;
        return 600;
    }

    /// <summary>Ruler tick positions across the given duration.</summary>
    public static IReadOnlyList<(double t, double x)> RulerTicks(double dur, double px)
    {
        var result = new List<(double t, double x)>();
        double step = NiceStep(70 / px);
        for (double t = 0; t <= dur + 0.001; t += step)
            result.Add((t, X(t, px)));
        return result;
    }
}
