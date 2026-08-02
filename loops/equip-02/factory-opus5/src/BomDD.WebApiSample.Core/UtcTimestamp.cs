using System.Globalization;

namespace BomDD.WebApiSample.Core;

/// <summary>
/// K-UTC-ISO8601-001 / E-BOOKING-INTERVAL-001:
/// request timestamps must be UTC with a literal Z offset; non-Z offsets (e.g. +09:00) are invalid_request.
/// </summary>
public static class UtcTimestamp
{
    /// <summary>Accepted request forms: with or without a fractional second part, always ending in a literal Z.</summary>
    private static readonly string[] AcceptedFormats =
    [
        "yyyy'-'MM'-'dd'T'HH':'mm':'ss'Z'",
        "yyyy'-'MM'-'dd'T'HH':'mm':'ss'.'FFFFFFF'Z'"
    ];

    /// <summary>Canonical form used inside the idempotency fingerprint (always full precision).</summary>
    private const string CanonicalFormat = "yyyy'-'MM'-'dd'T'HH':'mm':'ss'.'fffffff'Z'";

    private const string SecondsFormat = "yyyy'-'MM'-'dd'T'HH':'mm':'ss'Z'";

    private const string FractionFormat = "yyyy'-'MM'-'dd'T'HH':'mm':'ss'.'fffffff'Z'";

    /// <summary>
    /// Parses a literal-Z UTC timestamp. Any other offset (including +00:00 and a lowercase z)
    /// is rejected, because <c>format: date-time</c> alone would accept +09:00 (K-UTC-ISO8601-001).
    /// </summary>
    public static bool TryParse(string? value, out DateTimeOffset parsed)
    {
        parsed = default;
        if (string.IsNullOrWhiteSpace(value))
        {
            return false;
        }

        // Ordinal check first: the literal Z is the contract, not merely "some offset".
        if (!value.EndsWith('Z'))
        {
            return false;
        }

        return DateTimeOffset.TryParseExact(
            value,
            AcceptedFormats,
            CultureInfo.InvariantCulture,
            DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal,
            out parsed);
    }

    /// <summary>Response serialization (K-UTC-ISO8601-001: date-time strings). Always UTC, always literal Z.</summary>
    public static string Format(DateTimeOffset value)
    {
        var utc = value.ToUniversalTime();
        return utc.Ticks % TimeSpan.TicksPerSecond == 0
            ? utc.ToString(SecondsFormat, CultureInfo.InvariantCulture)
            : utc.ToString(FractionFormat, CultureInfo.InvariantCulture);
    }

    /// <summary>Canonical (full precision) rendering used by the idempotency fingerprint.</summary>
    public static string Canonical(DateTimeOffset value)
        => value.ToUniversalTime().ToString(CanonicalFormat, CultureInfo.InvariantCulture);
}
