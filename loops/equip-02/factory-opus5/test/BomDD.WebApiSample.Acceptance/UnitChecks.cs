using BomDD.WebApiSample.Core;

namespace BomDD.WebApiSample.Acceptance;

/// <summary>
/// Control Plan depth "unit": domain rule inspection without an HTTP process.
/// Covers CP-CORE-OVERLAP-001, CP-CORE-IDEMPOTENCY-001, CP-CORE-CANCEL-001
/// and the E-BOM invariants those characteristics rest on.
/// </summary>
public static class UnitChecks
{
    private static readonly DateTimeOffset Clock = new(2026, 1, 1, 0, 0, 0, TimeSpan.Zero);

    public static void Run(Runner runner)
    {
        Console.WriteLine("== depth: unit (core booking rules, no HTTP) ==");

        runner.Case("CP-CORE-OVERLAP-001", "overlapping range in the same room is slot_unavailable", () =>
        {
            var service = NewService();
            var first = service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z"));
            Check.Expect(first.IsSuccess, $"the first booking should succeed, got {first.ErrorCode}");

            var overlapping = service.Create(Command("room-a", "cust-2", "2026-06-01T10:30:00Z", "2026-06-01T11:30:00Z"));
            Check.ExpectEqual(ErrorCodes.SlotUnavailable, overlapping.ErrorCode, "overlap error code");
        });

        runner.Case("E-AVAILABILITY-001", "adjacent range (end == start) is not an overlap", () =>
        {
            var service = NewService();
            Check.Expect(
                service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z")).IsSuccess,
                "the first booking should succeed");

            var adjacent = service.Create(Command("room-a", "cust-2", "2026-06-01T11:00:00Z", "2026-06-01T12:00:00Z"));
            Check.Expect(adjacent.IsSuccess, $"the adjacent booking should succeed, got {adjacent.ErrorCode}");
        });

        runner.Case("E-AVAILABILITY-001", "a different room may hold the same range", () =>
        {
            var service = NewService();
            Check.Expect(
                service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z")).IsSuccess,
                "the first booking should succeed");

            var otherRoom = service.Create(Command("room-b", "cust-2", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z"));
            Check.Expect(otherRoom.IsSuccess, $"a different room should be free, got {otherRoom.ErrorCode}");
        });

        runner.Case("M-CORE-BOOKING-SERVICE-001", "roomId is normalized to uppercase before overlap comparison", () =>
        {
            var service = NewService();
            var first = service.Create(Command("ROOM-A", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z"));
            Check.Expect(first.IsSuccess, "the first booking should succeed");
            Check.ExpectEqual("ROOM-A", first.Booking!.RoomId, "stored roomId");

            var lowercase = service.Create(Command("room-a", "cust-2", "2026-06-01T10:30:00Z", "2026-06-01T11:30:00Z"));
            Check.ExpectEqual(ErrorCodes.SlotUnavailable, lowercase.ErrorCode, "case-insensitive overlap error code");
        });

        runner.Case("E-AVAILABILITY-001", "cancelled bookings are not overlap candidates", () =>
        {
            var service = NewService();
            var first = service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z"));
            Check.Expect(first.IsSuccess, "the first booking should succeed");

            var cancelled = service.Cancel(first.Booking!.Id);
            Check.Expect(cancelled.IsSuccess, $"cancellation should succeed, got {cancelled.ErrorCode}");

            var reused = service.Create(Command("room-a", "cust-2", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z"));
            Check.Expect(reused.IsSuccess, $"the freed slot should be bookable, got {reused.ErrorCode}");
        });

        runner.Case("CP-CORE-IDEMPOTENCY-001", "same key + same payload returns the same booking id", () =>
        {
            var service = NewService();
            var first = service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z", "key-1"));
            Check.Expect(first.IsSuccess, $"the first booking should succeed, got {first.ErrorCode}");

            var replay = service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z", "key-1"));
            Check.Expect(replay.IsSuccess, $"the replay should succeed, got {replay.ErrorCode}");
            Check.ExpectEqual(first.Booking!.Id, replay.Booking!.Id, "replayed booking id");
            Check.ExpectEqual(1, service.List().Count, "stored booking count after replay");
        });

        runner.Case("E-IDEMPOTENCY-001", "same key + different time range is idempotency_conflict", () =>
        {
            var service = NewService();
            Check.Expect(
                service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z", "key-1")).IsSuccess,
                "the first booking should succeed");

            var conflicting = service.Create(Command("room-a", "cust-1", "2026-06-02T10:00:00Z", "2026-06-02T11:00:00Z", "key-1"));
            Check.ExpectEqual(ErrorCodes.IdempotencyConflict, conflicting.ErrorCode, "conflict error code");
        });

        runner.Case("CP-IDEMPOTENCY-FIELDS-001", "same key + same room/time + different customerId is idempotency_conflict", () =>
        {
            var service = NewService();
            Check.Expect(
                service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z", "key-1")).IsSuccess,
                "the first booking should succeed");

            var conflicting = service.Create(Command("room-a", "cust-2", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z", "key-1"));
            Check.ExpectEqual(ErrorCodes.IdempotencyConflict, conflicting.ErrorCode, "conflict error code");
        });

        runner.Case("E-IDEMPOTENCY-001", "the fingerprint excludes the idempotency key", () =>
        {
            var start = DateTimeOffset.Parse("2026-06-01T10:00:00Z");
            var end = DateTimeOffset.Parse("2026-06-01T11:00:00Z");
            var fingerprint = BookingService.CanonicalFingerprint("room-a", "cust-1", start, end);

            Check.Expect(
                fingerprint.Contains("ROOM-A", StringComparison.Ordinal) &&
                fingerprint.Contains("cust-1", StringComparison.Ordinal),
                $"the fingerprint should cover roomId and customerId, got '{fingerprint}'");
            Check.Expect(
                !fingerprint.Contains("key-", StringComparison.OrdinalIgnoreCase),
                $"the fingerprint must not carry the idempotency key, got '{fingerprint}'");
        });

        runner.Case("CP-CORE-CANCEL-001", "cancelling inside the 24h window is cancellation_window_closed", () =>
        {
            var clock = new FixedTimeProvider(Clock);
            var service = new BookingService(clock);
            var booking = service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z"));
            Check.Expect(booking.IsSuccess, "the booking should be created");

            // 23 hours before the start: the window has closed.
            clock.Now = DateTimeOffset.Parse("2026-05-31T11:00:00Z");
            var late = service.Cancel(booking.Booking!.Id);
            Check.ExpectEqual(ErrorCodes.CancellationWindowClosed, late.ErrorCode, "late cancellation error code");
        });

        runner.Case("E-CANCELLATION-001", "cancelling exactly 24h before the start is allowed", () =>
        {
            var clock = new FixedTimeProvider(Clock);
            var service = new BookingService(clock);
            var booking = service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z"));
            Check.Expect(booking.IsSuccess, "the booking should be created");

            clock.Now = DateTimeOffset.Parse("2026-05-31T10:00:00Z");
            var cancelled = service.Cancel(booking.Booking!.Id);
            Check.Expect(cancelled.IsSuccess, $"cancellation at the boundary should succeed, got {cancelled.ErrorCode}");
            Check.ExpectEqual(BookingStatus.Cancelled, cancelled.Booking!.Status, "status after cancellation");
        });

        runner.Case("E-CANCELLATION-001", "cancelling an already cancelled booking repeats the same result", () =>
        {
            var clock = new FixedTimeProvider(Clock);
            var service = new BookingService(clock);
            var booking = service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z"));
            var first = service.Cancel(booking.Booking!.Id);
            Check.Expect(first.IsSuccess, "the first cancellation should succeed");

            // Move past the window: a repeat cancellation must still report the same outcome.
            clock.Now = DateTimeOffset.Parse("2026-06-01T09:00:00Z");
            var repeat = service.Cancel(booking.Booking!.Id);
            Check.Expect(repeat.IsSuccess, $"the repeated cancellation should succeed, got {repeat.ErrorCode}");
            Check.ExpectEqual(BookingStatus.Cancelled, repeat.Booking!.Status, "status after the repeated cancellation");
            Check.ExpectEqual(first.Booking!.Id, repeat.Booking!.Id, "booking id after the repeated cancellation");
        });

        runner.Case("E-CANCELLATION-001", "cancelling an unknown booking is not_found", () =>
        {
            var service = NewService();
            Check.ExpectEqual(ErrorCodes.NotFound, service.Cancel("bk_ffffffffffffffffffffffff").ErrorCode, "unknown id error code");
            Check.ExpectEqual(ErrorCodes.NotFound, service.Get("bk_ffffffffffffffffffffffff").ErrorCode, "unknown id error code");
        });

        runner.Case("E-BOOKING-INTERVAL-001", "duration below 30 minutes is invalid_request", () =>
        {
            var service = NewService();
            var tooShort = service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T10:15:00Z"));
            Check.ExpectEqual(ErrorCodes.InvalidRequest, tooShort.ErrorCode, "short duration error code");
        });

        runner.Case("E-BOOKING-INTERVAL-001", "duration above 4 hours is invalid_request", () =>
        {
            var service = NewService();
            var tooLong = service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T15:00:00Z"));
            Check.ExpectEqual(ErrorCodes.InvalidRequest, tooLong.ErrorCode, "long duration error code");
        });

        runner.Case("E-BOOKING-INTERVAL-001", "the 30 minute and 4 hour boundaries are accepted", () =>
        {
            var service = NewService();
            Check.Expect(
                service.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T10:30:00Z")).IsSuccess,
                "a 30 minute booking should be accepted");
            Check.Expect(
                service.Create(Command("room-b", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T14:00:00Z")).IsSuccess,
                "a 4 hour booking should be accepted");
        });

        runner.Case("E-BOOKING-INTERVAL-001", "endUtc must be later than startUtc", () =>
        {
            var service = NewService();
            Check.ExpectEqual(
                ErrorCodes.InvalidRequest,
                service.Create(Command("room-a", "cust-1", "2026-06-01T11:00:00Z", "2026-06-01T10:00:00Z")).ErrorCode,
                "reversed range error code");
        });

        runner.Case("CP-OFFSET-Z-001", "a non-Z offset is invalid_request", () =>
        {
            var service = NewService();
            var offset = service.Create(Command("room-a", "cust-1", "2026-06-01T19:00:00+09:00", "2026-06-01T20:00:00+09:00"));
            Check.ExpectEqual(ErrorCodes.InvalidRequest, offset.ErrorCode, "non-Z offset error code");

            Check.Expect(!UtcTimestamp.TryParse("2026-06-01T19:00:00+09:00", out _), "+09:00 must not parse");
            Check.Expect(!UtcTimestamp.TryParse("2026-06-01T19:00:00+00:00", out _), "+00:00 must not parse (a literal Z is required)");
            Check.Expect(!UtcTimestamp.TryParse("2026-06-01T19:00:00", out _), "a bare local timestamp must not parse");
            Check.Expect(UtcTimestamp.TryParse("2026-06-01T19:00:00Z", out _), "a literal Z timestamp must parse");
            Check.Expect(UtcTimestamp.TryParse("2026-06-01T19:00:00.500Z", out _), "fractional seconds with a literal Z must parse");
        });

        runner.Case("E-BOOKING-INTERVAL-001", "missing roomId or customerId is invalid_request", () =>
        {
            var service = NewService();
            Check.ExpectEqual(
                ErrorCodes.InvalidRequest,
                service.Create(Command(null, "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z")).ErrorCode,
                "missing roomId error code");
            Check.ExpectEqual(
                ErrorCodes.InvalidRequest,
                service.Create(Command("room-a", "  ", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z")).ErrorCode,
                "blank customerId error code");
            Check.ExpectEqual(
                ErrorCodes.InvalidRequest,
                service.Create(Command("room-a", "cust-1", null, "2026-06-01T11:00:00Z")).ErrorCode,
                "missing startUtc error code");
        });

        runner.Case("M-CORE-BOOKING-SERVICE-001", "the booking id is a deterministic bk_ prefixed hash", () =>
        {
            var serviceA = NewService();
            var serviceB = NewService();
            var a = serviceA.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z", "key-1"));
            var b = serviceB.Create(Command("room-a", "cust-1", "2026-06-01T10:00:00Z", "2026-06-01T11:00:00Z", "key-1"));

            Check.Expect(a.Booking!.Id.StartsWith("bk_", StringComparison.Ordinal), $"id prefix, got '{a.Booking!.Id}'");
            Check.ExpectEqual(a.Booking!.Id, b.Booking!.Id, "the id should be deterministic across service instances");
        });

        runner.Case("M-CORE-BOOKING-SERVICE-001", "concurrent overlapping creates yield exactly one confirmed booking", () =>
        {
            var service = NewService();
            var results = new BookingResult[16];
            Parallel.For(0, results.Length, index =>
            {
                results[index] = service.Create(Command(
                    "room-parallel",
                    $"cust-{index}",
                    "2026-06-01T10:00:00Z",
                    "2026-06-01T11:00:00Z"));
            });

            var accepted = results.Count(result => result.IsSuccess);
            Check.ExpectEqual(1, accepted, "accepted concurrent creates");
            Check.Expect(
                results.Where(result => !result.IsSuccess).All(result => result.ErrorCode == ErrorCodes.SlotUnavailable),
                "every rejected concurrent create should be slot_unavailable");
        });

        Console.WriteLine();
    }

    private static BookingService NewService() => new(new FixedTimeProvider(Clock));

    private static CreateBookingCommand Command(
        string? roomId,
        string? customerId,
        string? startUtc,
        string? endUtc,
        string? idempotencyKey = null)
        => new(roomId, customerId, startUtc, endUtc, idempotencyKey);
}
