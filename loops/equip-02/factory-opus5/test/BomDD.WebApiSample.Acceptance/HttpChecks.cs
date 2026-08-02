using System.Globalization;
using System.Text.Json;
using BomDD.WebApiSample.Core;

namespace BomDD.WebApiSample.Acceptance;

/// <summary>
/// Control Plan depths L1 and L3 — interaction behavior, replay, conflict and concurrency over HTTP.
/// Covers CP-AUTH-SURFACE-001, CP-CONCURRENCY-SURFACE-001, CP-IDEMPOTENCY-FIELDS-001,
/// CP-VALIDATION-CODE-001 and CP-OFFSET-Z-001.
/// </summary>
public static class HttpChecks
{
    public static async Task RunAsync(Runner runner, HttpProbe probe)
    {
        Console.WriteLine("== depth: L1/L3 (HTTP surface on port 5210) ==");

        var nowUtc = DateTimeOffset.UtcNow;
        var hourFloor = new DateTimeOffset(nowUtc.UtcDateTime.Date, TimeSpan.Zero).AddHours(nowUtc.Hour);
        var far = hourFloor.AddDays(10);
        var soon = hourFloor.AddHours(2);

        await runner.CaseAsync("L1", "the health endpoint answers without an API key", async () =>
        {
            var response = await probe.GetAsync("/health", apiKey: null);
            Check.ExpectEqual(200, response.Status, "GET /health status");
            Check.ExpectEqual("ok", response.Text("status"), "GET /health status field");
        });

        await runner.CaseAsync("CP-AUTH-SURFACE-001", "a missing X-Api-Key header returns 401 unauthorized", async () =>
        {
            var listing = await probe.GetAsync("/v1/bookings", apiKey: null);
            Check.ExpectEqual(401, listing.Status, "GET /v1/bookings without a key");
            Check.ExpectEqual("unauthorized", listing.Code, "error code without a key");

            var creating = await probe.PostJsonAsync(
                "/v1/bookings",
                Payload("auth-room", "cust-1", far, far.AddHours(1)),
                apiKey: null);
            Check.ExpectEqual(401, creating.Status, "POST /v1/bookings without a key");
            Check.ExpectEqual("unauthorized", creating.Code, "error code without a key");
        });

        await runner.CaseAsync("CP-AUTH-SURFACE-001", "an unknown X-Api-Key value returns 401 unauthorized", async () =>
        {
            var response = await probe.GetAsync("/v1/bookings", apiKey: "not-the-demo-key");
            Check.ExpectEqual(401, response.Status, "GET /v1/bookings with a wrong key");
            Check.ExpectEqual("unauthorized", response.Code, "error code with a wrong key");
        });

        string createdId = string.Empty;
        await runner.CaseAsync("E-HTTP-CONTRACT-001", "POST /v1/bookings creates a booking and returns 201", async () =>
        {
            var start = far;
            var end = far.AddHours(1);
            var (status, location, response) = await probe.PostWithLocationAsync(
                "/v1/bookings",
                Payload("create-room", "cust-1", start, end));

            Check.ExpectEqual(201, status, "POST /v1/bookings status");
            createdId = response.Text("id") ?? throw new AcceptanceException($"no id in {response.Describe()}");
            Check.Expect(createdId.StartsWith("bk_", StringComparison.Ordinal), $"booking id, got '{createdId}'");
            Check.ExpectEqual("CREATE-ROOM", response.Text("roomId"), "the response echoes the normalized roomId");
            Check.ExpectEqual("cust-1", response.Text("customerId"), "customerId");
            Check.ExpectEqual(UtcTimestamp.Format(start), response.Text("startUtc"), "startUtc");
            Check.ExpectEqual(UtcTimestamp.Format(end), response.Text("endUtc"), "endUtc");
            Check.ExpectEqual("confirmed", response.Text("status"), "status");
            Check.ExpectEqual($"/v1/bookings/{createdId}", location, "Location header");
        });

        await runner.CaseAsync("E-HTTP-CONTRACT-001", "GET /v1/bookings/{id} returns the booking", async () =>
        {
            Check.Expect(createdId.Length > 0, "the create check must run first");
            var response = await probe.GetAsync($"/v1/bookings/{createdId}");
            Check.ExpectEqual(200, response.Status, "GET /v1/bookings/{id} status");
            Check.ExpectEqual(createdId, response.Text("id"), "booking id");
        });

        await runner.CaseAsync("E-HTTP-CONTRACT-001", "GET /v1/bookings lists the created booking", async () =>
        {
            var response = await probe.GetAsync("/v1/bookings");
            Check.ExpectEqual(200, response.Status, "GET /v1/bookings status");
            Check.Expect(response.Json is { ValueKind: JsonValueKind.Array }, $"the listing should be a JSON array, got {response.Describe()}");

            var ids = response.Json!.Value
                .EnumerateArray()
                .Select(item => item.TryGetProperty("id", out var id) ? id.GetString() : null)
                .ToArray();
            Check.Expect(ids.Contains(createdId), $"the listing should contain {createdId}");
        });

        await runner.CaseAsync("E-HTTP-CONTRACT-001", "an unknown booking id returns 404 not_found", async () =>
        {
            var read = await probe.GetAsync("/v1/bookings/bk_ffffffffffffffffffffffff");
            Check.ExpectEqual(404, read.Status, "GET of an unknown id");
            Check.ExpectEqual("not_found", read.Code, "error code for an unknown id");

            var cancel = await probe.DeleteAsync("/v1/bookings/bk_ffffffffffffffffffffffff");
            Check.ExpectEqual(404, cancel.Status, "DELETE of an unknown id");
            Check.ExpectEqual("not_found", cancel.Code, "error code for an unknown id");
        });

        await runner.CaseAsync("E-AVAILABILITY-001", "an overlapping create returns 409 slot_unavailable", async () =>
        {
            var start = far.AddDays(1);
            var first = await probe.PostJsonAsync("/v1/bookings", Payload("overlap-room", "cust-1", start, start.AddHours(2)));
            Check.ExpectEqual(201, first.Status, "the first create");

            var overlapping = await probe.PostJsonAsync(
                "/v1/bookings",
                Payload("overlap-room", "cust-2", start.AddHours(1), start.AddHours(3)));
            Check.ExpectEqual(409, overlapping.Status, "the overlapping create");
            Check.ExpectEqual("slot_unavailable", overlapping.Code, "overlap error code");

            var adjacent = await probe.PostJsonAsync(
                "/v1/bookings",
                Payload("overlap-room", "cust-3", start.AddHours(2), start.AddHours(3)));
            Check.ExpectEqual(201, adjacent.Status, "the adjacent create");
        });

        await runner.CaseAsync("CP-CORE-IDEMPOTENCY-001", "a same-key same-payload replay returns 201 and the same id", async () =>
        {
            var start = far.AddDays(2);
            var payload = Payload("replay-room", "cust-1", start, start.AddHours(1), "replay-key-1");

            var first = await probe.PostJsonAsync("/v1/bookings", payload);
            Check.ExpectEqual(201, first.Status, "the first create");

            var replay = await probe.PostJsonAsync("/v1/bookings", payload);
            Check.ExpectEqual(201, replay.Status, "the replay status (the original resource is returned)");
            Check.ExpectEqual(first.Text("id"), replay.Text("id"), "the replayed booking id");
        });

        await runner.CaseAsync("CP-IDEMPOTENCY-FIELDS-001", "same key + same room/time + different customerId is 409 idempotency_conflict", async () =>
        {
            var start = far.AddDays(3);
            var first = await probe.PostJsonAsync(
                "/v1/bookings",
                Payload("fingerprint-room", "cust-1", start, start.AddHours(1), "fingerprint-key-1"));
            Check.ExpectEqual(201, first.Status, "the first create");

            var conflicting = await probe.PostJsonAsync(
                "/v1/bookings",
                Payload("fingerprint-room", "cust-2", start, start.AddHours(1), "fingerprint-key-1"));
            Check.ExpectEqual(409, conflicting.Status, "the conflicting create status");
            Check.ExpectEqual("idempotency_conflict", conflicting.Code, "conflict error code");
        });

        await runner.CaseAsync("CP-VALIDATION-CODE-001", "a too short and a too long duration are 400 invalid_request", async () =>
        {
            var start = far.AddDays(4);

            var tooShort = await probe.PostJsonAsync(
                "/v1/bookings",
                Payload("duration-room", "cust-1", start, start.AddMinutes(15)));
            Check.ExpectEqual(400, tooShort.Status, "the short booking status");
            Check.ExpectEqual("invalid_request", tooShort.Code, "the short booking error code");

            var tooLong = await probe.PostJsonAsync(
                "/v1/bookings",
                Payload("duration-room", "cust-1", start, start.AddHours(5)));
            Check.ExpectEqual(400, tooLong.Status, "the long booking status");
            Check.ExpectEqual("invalid_request", tooLong.Code, "the long booking error code");
        });

        await runner.CaseAsync("CP-VALIDATION-CODE-001", "missing fields and malformed JSON are 400 invalid_request", async () =>
        {
            var start = far.AddDays(5);

            var missingRoom = await probe.PostRawAsync(
                "/v1/bookings",
                $$"""{"customerId":"cust-1","startUtc":"{{UtcTimestamp.Format(start)}}","endUtc":"{{UtcTimestamp.Format(start.AddHours(1))}}"}""");
            Check.ExpectEqual(400, missingRoom.Status, "the missing roomId status");
            Check.ExpectEqual("invalid_request", missingRoom.Code, "the missing roomId error code");

            var malformed = await probe.PostRawAsync("/v1/bookings", "{ this is not json");
            Check.ExpectEqual(400, malformed.Status, "the malformed body status");
            Check.ExpectEqual("invalid_request", malformed.Code, "the malformed body error code");

            var reversed = await probe.PostJsonAsync(
                "/v1/bookings",
                Payload("reverse-room", "cust-1", start.AddHours(1), start));
            Check.ExpectEqual(400, reversed.Status, "the reversed range status");
            Check.ExpectEqual("invalid_request", reversed.Code, "the reversed range error code");
        });

        await runner.CaseAsync("CP-OFFSET-Z-001", "a +09:00 offset is 400 invalid_request", async () =>
        {
            var start = far.AddDays(6);
            var local = start.ToOffset(TimeSpan.FromHours(9));
            const string offsetFormat = "yyyy'-'MM'-'dd'T'HH':'mm':'sszzz";
            var startLocal = local.ToString(offsetFormat, CultureInfo.InvariantCulture);
            var endLocal = local.AddHours(1).ToString(offsetFormat, CultureInfo.InvariantCulture);

            var response = await probe.PostRawAsync(
                "/v1/bookings",
                $$"""{"roomId":"offset-room","customerId":"cust-1","startUtc":"{{startLocal}}","endUtc":"{{endLocal}}"}""");
            Check.ExpectEqual(400, response.Status, "the non-Z offset status");
            Check.ExpectEqual("invalid_request", response.Code, "the non-Z offset error code");

            var listing = await probe.GetAsync("/v1/bookings");
            Check.Expect(
                !listing.Body.Contains("OFFSET-ROOM", StringComparison.Ordinal),
                "a rejected non-Z request must not have created a booking");
        });

        await runner.CaseAsync("E-CANCELLATION-001", "DELETE cancels a booking and repeats the same result", async () =>
        {
            var start = far.AddDays(7);
            var created = await probe.PostJsonAsync("/v1/bookings", Payload("cancel-room", "cust-1", start, start.AddHours(1)));
            Check.ExpectEqual(201, created.Status, "the create status");
            var id = created.Text("id")!;

            var cancelled = await probe.DeleteAsync($"/v1/bookings/{id}");
            Check.ExpectEqual(200, cancelled.Status, "the cancellation status");
            Check.ExpectEqual("cancelled", cancelled.Text("status"), "the booking status after cancellation");

            var repeat = await probe.DeleteAsync($"/v1/bookings/{id}");
            Check.ExpectEqual(200, repeat.Status, "the repeated cancellation status");
            Check.ExpectEqual("cancelled", repeat.Text("status"), "the booking status after the repeated cancellation");

            var reused = await probe.PostJsonAsync("/v1/bookings", Payload("cancel-room", "cust-2", start, start.AddHours(1)));
            Check.ExpectEqual(201, reused.Status, "the cancelled slot should be bookable again");
        });

        await runner.CaseAsync("CP-CORE-CANCEL-001", "a booking starting in 2 hours is 409 cancellation_window_closed", async () =>
        {
            var created = await probe.PostJsonAsync("/v1/bookings", Payload("window-room", "cust-1", soon, soon.AddHours(1)));
            Check.ExpectEqual(201, created.Status, "the create status");
            var id = created.Text("id")!;

            var cancelled = await probe.DeleteAsync($"/v1/bookings/{id}");
            Check.ExpectEqual(409, cancelled.Status, "the late cancellation status");
            Check.ExpectEqual("cancellation_window_closed", cancelled.Code, "the late cancellation error code");
        });

        await runner.CaseAsync("CP-CONCURRENCY-SURFACE-001", "parallel overlapping creates yield exactly one 201", async () =>
        {
            var start = far.AddDays(8);
            var attempts = Enumerable
                .Range(0, 8)
                .Select(index => probe.PostJsonAsync(
                    "/v1/bookings",
                    Payload("concurrency-room", $"cust-{index}", start, start.AddHours(1))))
                .ToArray();

            var responses = await Task.WhenAll(attempts);
            var accepted = responses.Count(response => response.Status == 201);
            Check.ExpectEqual(1, accepted, "accepted parallel creates");

            foreach (var rejected in responses.Where(response => response.Status != 201))
            {
                Check.ExpectEqual(409, rejected.Status, "the rejected parallel create status");
                Check.ExpectEqual("slot_unavailable", rejected.Code, "the rejected parallel create error code");
            }
        });

        Console.WriteLine();
    }

    private static object Payload(
        string roomId,
        string customerId,
        DateTimeOffset startUtc,
        DateTimeOffset endUtc,
        string? idempotencyKey = null)
    {
        var payload = new Dictionary<string, object?>(StringComparer.Ordinal)
        {
            ["roomId"] = roomId,
            ["customerId"] = customerId,
            ["startUtc"] = UtcTimestamp.Format(startUtc),
            ["endUtc"] = UtcTimestamp.Format(endUtc)
        };

        if (idempotencyKey is not null)
        {
            payload["idempotencyKey"] = idempotencyKey;
        }

        return payload;
    }
}
