namespace BomDD.WebApiSample.Core;

/// <summary>Numeric limits taken directly from the E-BOM invariants.</summary>
public static class BookingRules
{
    /// <summary>E-BOOKING-INTERVAL-001: duration is at least 30 minutes.</summary>
    public static readonly TimeSpan MinimumDuration = TimeSpan.FromMinutes(30);

    /// <summary>E-BOOKING-INTERVAL-001: duration is at most 4 hours.</summary>
    public static readonly TimeSpan MaximumDuration = TimeSpan.FromHours(4);

    /// <summary>E-CANCELLATION-001: cancellable only while UtcNow &lt;= startUtc - 24h.</summary>
    public static readonly TimeSpan CancellationLeadTime = TimeSpan.FromHours(24);
}
