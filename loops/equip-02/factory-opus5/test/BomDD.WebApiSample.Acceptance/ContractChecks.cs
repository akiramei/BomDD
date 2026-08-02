using System.Text.Json;

namespace BomDD.WebApiSample.Acceptance;

/// <summary>
/// Control Plan depth L2 — CP-OPENAPI-SURFACE-001.
/// Oracle: System.Text.Json inspection of openapi/openapi.json.
/// </summary>
public static class ContractChecks
{
    public static void Run(Runner runner, string workspaceRoot)
    {
        Console.WriteLine("== depth: L2 (OpenAPI contract inspection) ==");

        var path = Path.Combine(workspaceRoot, "openapi", "openapi.json");
        JsonElement root;
        try
        {
            using var document = JsonDocument.Parse(File.ReadAllText(path));
            root = document.RootElement.Clone();
        }
        catch (Exception exception)
        {
            runner.Fatal("CP-OPENAPI-SURFACE-001", "openapi/openapi.json is readable JSON", $"{path}: {exception.Message}");
            Console.WriteLine();
            return;
        }

        runner.Case("CP-OPENAPI-SURFACE-001", "the document declares OpenAPI 3.1", () =>
        {
            var version = Get(root, "openapi").GetString();
            Check.Expect(version is not null && version.StartsWith("3.1", StringComparison.Ordinal), $"openapi version, got '{version}'");
        });

        runner.Case("CP-OPENAPI-SURFACE-001", "paths /v1/bookings and /v1/bookings/{id} are present", () =>
        {
            var paths = Get(root, "paths");
            var bookings = Get(paths, "/v1/bookings");
            Check.Expect(bookings.TryGetProperty("post", out _), "/v1/bookings should declare post");
            Check.Expect(bookings.TryGetProperty("get", out _), "/v1/bookings should declare get");

            var byId = Get(paths, "/v1/bookings/{id}");
            Check.Expect(byId.TryGetProperty("get", out _), "/v1/bookings/{id} should declare get");
            Check.Expect(byId.TryGetProperty("delete", out _), "/v1/bookings/{id} should declare delete");
        });

        runner.Case("CP-OPENAPI-SURFACE-001", "schemas CreateBookingRequest, BookingResponse and ErrorResponse are present", () =>
        {
            var schemas = Get(Get(root, "components"), "schemas");

            var request = Get(schemas, "CreateBookingRequest");
            var required = Required(request);
            foreach (var field in new[] { "roomId", "customerId", "startUtc", "endUtc" })
            {
                Check.Expect(required.Contains(field), $"CreateBookingRequest.required should contain {field}");
            }

            var response = Get(schemas, "BookingResponse");
            var responseRequired = Required(response);
            foreach (var field in new[] { "id", "roomId", "customerId", "startUtc", "endUtc", "status" })
            {
                Check.Expect(responseRequired.Contains(field), $"BookingResponse.required should contain {field}");
            }

            var error = Get(schemas, "ErrorResponse");
            var errorRequired = Required(error);
            Check.Expect(errorRequired.Contains("code"), "ErrorResponse.required should contain code");
            Check.Expect(errorRequired.Contains("message"), "ErrorResponse.required should contain message");
        });

        runner.Case("CP-OPENAPI-SURFACE-001", "securityScheme ApiKeyAuth declares the X-Api-Key header", () =>
        {
            var scheme = Get(Get(Get(root, "components"), "securitySchemes"), "ApiKeyAuth");
            Check.ExpectEqual("apiKey", Get(scheme, "type").GetString(), "ApiKeyAuth.type");
            Check.ExpectEqual("header", Get(scheme, "in").GetString(), "ApiKeyAuth.in");
            Check.ExpectEqual("X-Api-Key", Get(scheme, "name").GetString(), "ApiKeyAuth.name");
        });

        runner.Case("CP-OFFSET-Z-001", "the contract states the literal-Z requirement, not just format: date-time", () =>
        {
            var schemas = Get(Get(root, "components"), "schemas");
            var timestamp = Get(schemas, "UtcTimestamp");
            var pattern = Get(timestamp, "pattern").GetString();
            Check.Expect(
                pattern is not null && pattern.EndsWith("Z$", StringComparison.Ordinal),
                $"the timestamp pattern should pin a literal trailing Z, got '{pattern}'");
        });

        runner.Case("CP-VALIDATION-CODE-001", "the contract enumerates invalid_request and never validation_error", () =>
        {
            var error = Get(Get(Get(root, "components"), "schemas"), "ErrorResponse");
            var codes = Get(Get(error, "properties"), "code")
                .GetProperty("enum")
                .EnumerateArray()
                .Select(item => item.GetString())
                .ToArray();

            Check.Expect(codes.Contains("invalid_request"), "the ErrorResponse code enum should contain invalid_request");
            Check.Expect(!codes.Contains("validation_error"), "the ErrorResponse code enum must not contain validation_error");

            var raw = File.ReadAllText(path);
            Check.Expect(
                !raw.Contains("validation_error", StringComparison.Ordinal),
                "the contract document must not mention validation_error anywhere");
        });

        Console.WriteLine();
    }

    private static JsonElement Get(JsonElement parent, string name)
        => parent.TryGetProperty(name, out var value)
            ? value
            : throw new AcceptanceException($"the contract is missing '{name}'.");

    private static HashSet<string> Required(JsonElement schema)
        => schema.TryGetProperty("required", out var required)
            ? required.EnumerateArray().Select(item => item.GetString() ?? string.Empty).ToHashSet(StringComparer.Ordinal)
            : [];
}
