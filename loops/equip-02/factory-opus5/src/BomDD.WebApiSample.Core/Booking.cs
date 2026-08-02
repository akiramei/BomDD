namespace BomDD.WebApiSample.Core;

/// <summary>E-AVAILABILITY-001: only confirmed bookings are overlap candidates.</summary>
public enum BookingStatus
{
    Confirmed,
    Cancelled
}

/// <summary>
/// A room booking.
/// <para>M-CORE-BOOKING-SERVICE-001: <see cref="RoomId"/> is stored normalized (uppercase).</para>
/// <para>E-BOOKING-INTERVAL-001: the interval is half-open [StartUtc, EndUtc).</para>
/// </summary>
public sealed record Booking(
    string Id,
    string RoomId,
    string CustomerId,
    DateTimeOffset StartUtc,
    DateTimeOffset EndUtc,
    BookingStatus Status,
    string? IdempotencyKey,
    string Fingerprint);

/// <summary>
/// Create input. Timestamps stay raw strings so that the literal-Z rule
/// (E-BOOKING-INTERVAL-001 / K-UTC-ISO8601-001) is enforced by the core, not by the transport.
/// </summary>
public sealed record CreateBookingCommand(
    string? RoomId,
    string? CustomerId,
    string? StartUtc,
    string? EndUtc,
    string? IdempotencyKey = null);

/// <summary>Outcome of a core operation: either a booking, or an error code + message.</summary>
public sealed record BookingResult
{
    private BookingResult(Booking? booking, string? errorCode, string? message)
    {
        Booking = booking;
        ErrorCode = errorCode;
        Message = message;
    }

    public Booking? Booking { get; }

    public string? ErrorCode { get; }

    public string? Message { get; }

    public bool IsSuccess => ErrorCode is null;

    public static BookingResult Ok(Booking booking) => new(booking, null, null);

    public static BookingResult Fail(string errorCode, string message) => new(null, errorCode, message);
}
