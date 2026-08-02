using BomDD.WebApiSample.Core;

namespace BomDD.WebApiSample.Api;

/// <summary>OpenAPI schema CreateBookingRequest (M-OPENAPI-DOCUMENT-001).</summary>
public sealed record CreateBookingRequest(
    string? RoomId,
    string? CustomerId,
    string? StartUtc,
    string? EndUtc,
    string? IdempotencyKey);

/// <summary>OpenAPI schema BookingResponse (M-OPENAPI-DOCUMENT-001).</summary>
public sealed record BookingResponse(
    string Id,
    string RoomId,
    string CustomerId,
    string StartUtc,
    string EndUtc,
    string Status)
{
    public static BookingResponse From(Booking booking) => new(
        booking.Id,
        booking.RoomId,
        booking.CustomerId,
        UtcTimestamp.Format(booking.StartUtc),
        UtcTimestamp.Format(booking.EndUtc),
        booking.Status == BookingStatus.Confirmed ? "confirmed" : "cancelled");
}

/// <summary>
/// OpenAPI schema ErrorResponse.
/// E-ERROR-SCHEMA-001: errors are application/json with code and message.
/// </summary>
public sealed record ErrorResponse(string Code, string Message);
