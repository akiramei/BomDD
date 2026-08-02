using System.Security.Cryptography;
using System.Text;

namespace BomDD.WebApiSample.Core;

/// <summary>
/// M-CORE-BOOKING-SERVICE-001.
/// Realizes E-BOOKING-INTERVAL-001, E-AVAILABILITY-001, E-IDEMPOTENCY-001, E-CANCELLATION-001.
/// </summary>
public sealed class BookingService
{
    private readonly object _gate = new();
    private readonly Dictionary<string, Booking> _bookings = new(StringComparer.Ordinal);
    private readonly List<string> _order = [];
    private readonly Dictionary<string, string> _byIdempotencyKey = new(StringComparer.Ordinal);
    private readonly TimeProvider _timeProvider;

    public BookingService(TimeProvider? timeProvider = null)
        => _timeProvider = timeProvider ?? TimeProvider.System;

    /// <summary>
    /// Creates a booking.
    /// Order of checks: validation -> idempotency -> availability.
    /// The idempotency check precedes availability so that a replay of the same key + same payload
    /// returns the original booking instead of colliding with itself (K-IDEMPOTENCY-HTTP-001).
    /// </summary>
    public BookingResult Create(CreateBookingCommand command)
    {
        if (command is null)
        {
            return BookingResult.Fail(ErrorCodes.InvalidRequest, "A request body is required.");
        }

        var roomId = command.RoomId?.Trim();
        if (string.IsNullOrEmpty(roomId))
        {
            return BookingResult.Fail(ErrorCodes.InvalidRequest, "roomId is required.");
        }

        var customerId = command.CustomerId?.Trim();
        if (string.IsNullOrEmpty(customerId))
        {
            return BookingResult.Fail(ErrorCodes.InvalidRequest, "customerId is required.");
        }

        if (!UtcTimestamp.TryParse(command.StartUtc, out var startUtc))
        {
            return BookingResult.Fail(
                ErrorCodes.InvalidRequest,
                "startUtc must be an ISO-8601 timestamp in UTC with a literal Z offset (for example 2026-08-03T10:00:00Z).");
        }

        if (!UtcTimestamp.TryParse(command.EndUtc, out var endUtc))
        {
            return BookingResult.Fail(
                ErrorCodes.InvalidRequest,
                "endUtc must be an ISO-8601 timestamp in UTC with a literal Z offset (for example 2026-08-03T11:00:00Z).");
        }

        if (endUtc <= startUtc)
        {
            return BookingResult.Fail(ErrorCodes.InvalidRequest, "endUtc must be later than startUtc.");
        }

        var duration = endUtc - startUtc;
        if (duration < BookingRules.MinimumDuration || duration > BookingRules.MaximumDuration)
        {
            return BookingResult.Fail(
                ErrorCodes.InvalidRequest,
                "The booking duration must be between 30 minutes and 4 hours.");
        }

        var normalizedRoomId = NormalizeRoomId(roomId);
        var idempotencyKey = string.IsNullOrWhiteSpace(command.IdempotencyKey)
            ? null
            : command.IdempotencyKey.Trim();
        var fingerprint = CanonicalFingerprint(normalizedRoomId, customerId, startUtc, endUtc);

        lock (_gate)
        {
            // E-IDEMPOTENCY-001
            if (idempotencyKey is not null && _byIdempotencyKey.TryGetValue(idempotencyKey, out var existingId))
            {
                var existing = _bookings[existingId];
                return string.Equals(existing.Fingerprint, fingerprint, StringComparison.Ordinal)
                    ? BookingResult.Ok(existing)
                    : BookingResult.Fail(
                        ErrorCodes.IdempotencyConflict,
                        "The idempotency key was already used with a different request payload.");
            }

            // E-AVAILABILITY-001: half-open overlap over confirmed bookings of the same room only.
            foreach (var id in _order)
            {
                var candidate = _bookings[id];
                if (candidate.Status != BookingStatus.Confirmed)
                {
                    continue;
                }

                if (!string.Equals(candidate.RoomId, normalizedRoomId, StringComparison.Ordinal))
                {
                    continue;
                }

                if (Overlaps(startUtc, endUtc, candidate.StartUtc, candidate.EndUtc))
                {
                    return BookingResult.Fail(
                        ErrorCodes.SlotUnavailable,
                        "The room is already booked for an overlapping time range.");
                }
            }

            var booking = new Booking(
                NextId(fingerprint, idempotencyKey),
                normalizedRoomId,
                customerId,
                startUtc,
                endUtc,
                BookingStatus.Confirmed,
                idempotencyKey,
                fingerprint);

            _bookings.Add(booking.Id, booking);
            _order.Add(booking.Id);
            if (idempotencyKey is not null)
            {
                _byIdempotencyKey[idempotencyKey] = booking.Id;
            }

            return BookingResult.Ok(booking);
        }
    }

    /// <summary>E-CANCELLATION-001.</summary>
    public BookingResult Cancel(string? bookingId)
    {
        if (string.IsNullOrWhiteSpace(bookingId))
        {
            return BookingResult.Fail(ErrorCodes.NotFound, "The booking was not found.");
        }

        lock (_gate)
        {
            if (!_bookings.TryGetValue(bookingId, out var booking))
            {
                return BookingResult.Fail(ErrorCodes.NotFound, "The booking was not found.");
            }

            // "すでにcancelledの予約へのキャンセルは同じ結果を返す" -> repeat cancel is a no-op success.
            if (booking.Status == BookingStatus.Cancelled)
            {
                return BookingResult.Ok(booking);
            }

            var now = _timeProvider.GetUtcNow();
            if (now > booking.StartUtc - BookingRules.CancellationLeadTime)
            {
                return BookingResult.Fail(
                    ErrorCodes.CancellationWindowClosed,
                    "A booking can only be cancelled up to 24 hours before it starts.");
            }

            var cancelled = booking with { Status = BookingStatus.Cancelled };
            _bookings[cancelled.Id] = cancelled;
            return BookingResult.Ok(cancelled);
        }
    }

    /// <summary>Single booking lookup.</summary>
    public BookingResult Get(string? bookingId)
    {
        if (string.IsNullOrWhiteSpace(bookingId))
        {
            return BookingResult.Fail(ErrorCodes.NotFound, "The booking was not found.");
        }

        lock (_gate)
        {
            return _bookings.TryGetValue(bookingId, out var booking)
                ? BookingResult.Ok(booking)
                : BookingResult.Fail(ErrorCodes.NotFound, "The booking was not found.");
        }
    }

    /// <summary>All bookings, in creation order.</summary>
    public IReadOnlyList<Booking> List()
    {
        lock (_gate)
        {
            var items = new List<Booking>(_order.Count);
            foreach (var id in _order)
            {
                items.Add(_bookings[id]);
            }

            return items;
        }
    }

    /// <summary>M-CORE-BOOKING-SERVICE-001: roomId is normalized to uppercase before overlap comparison.</summary>
    public static string NormalizeRoomId(string roomId) => roomId.Trim().ToUpperInvariant();

    /// <summary>E-AVAILABILITY-001: half-open [start, end); end == start is adjacency, not overlap.</summary>
    public static bool Overlaps(DateTimeOffset startA, DateTimeOffset endA, DateTimeOffset startB, DateTimeOffset endB)
        => startA < endB && startB < endA;

    /// <summary>
    /// E-IDEMPOTENCY-001 / K-IDEMPOTENCY-HTTP-001:
    /// canonical fingerprint over roomId, customerId, startUtc, endUtc. The idempotency key is excluded.
    /// </summary>
    public static string CanonicalFingerprint(
        string roomId,
        string customerId,
        DateTimeOffset startUtc,
        DateTimeOffset endUtc)
        => string.Join(
            '|',
            NormalizeRoomId(roomId),
            customerId.Trim(),
            UtcTimestamp.Canonical(startUtc),
            UtcTimestamp.Canonical(endUtc));

    /// <summary>M-CORE-BOOKING-SERVICE-001: booking id is a deterministic hash with the prefix bk_.</summary>
    private string NextId(string fingerprint, string? idempotencyKey)
    {
        // Callers hold _gate.
        for (var attempt = 0; ; attempt++)
        {
            var seed = attempt == 0
                ? $"{fingerprint}|{idempotencyKey ?? string.Empty}"
                : $"{fingerprint}|{idempotencyKey ?? string.Empty}|{attempt}";
            var id = DeterministicId(seed);
            if (!_bookings.ContainsKey(id))
            {
                return id;
            }
        }
    }

    private static string DeterministicId(string seed)
    {
        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(seed));
        return "bk_" + Convert.ToHexString(hash)[..24].ToLowerInvariant();
    }
}
