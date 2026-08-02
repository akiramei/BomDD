using System.Text.Json;
using System.Text.Json.Serialization;
using BomDD.WebApiSample.Api;
using BomDD.WebApiSample.Core;

// M-API-ENDPOINTS-001 — interface contract:
//   base_path            /v1
//   auth_header          X-Api-Key      (E-AUTH-APIKEY-001 / K-APIKEY-HEADER-001)
//   default_demo_key     demo-key
//   error_schema         ErrorResponse  (E-ERROR-SCHEMA-001)
//   validation_error_code invalid_request (K-HTTP-REST-001)
//   datetime_input       literal-Z UTC only (K-UTC-ISO8601-001)

var builder = WebApplication.CreateBuilder(args);

builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    options.SerializerOptions.PropertyNameCaseInsensitive = true;
    options.SerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.Never;
});

builder.Services.AddSingleton(TimeProvider.System);
builder.Services.AddSingleton<BookingService>();

// The acceptance harness drives the process over HTTP on port 5210.
if (string.IsNullOrEmpty(builder.Configuration["urls"]) &&
    string.IsNullOrEmpty(Environment.GetEnvironmentVariable("ASPNETCORE_URLS")))
{
    builder.WebHost.UseUrls("http://127.0.0.1:5210");
}

var app = builder.Build();

var apiKey = builder.Configuration["Api:Key"] is { Length: > 0 } configured
    ? configured
    : "demo-key"; // M-API-ENDPOINTS-001.default_demo_key

// E-AUTH-APIKEY-001: every /v1 resource requires a valid X-Api-Key header.
app.Use(async (context, next) =>
{
    if (!context.Request.Path.StartsWithSegments("/v1"))
    {
        await next(context);
        return;
    }

    var presented = context.Request.Headers["X-Api-Key"].ToString();
    if (string.IsNullOrEmpty(presented) || !string.Equals(presented, apiKey, StringComparison.Ordinal))
    {
        await ApiResults.WriteErrorAsync(
            context,
            StatusCodes.Status401Unauthorized,
            ErrorCodes.Unauthorized,
            "A valid X-Api-Key header is required.");
        return;
    }

    await next(context);
});

// Control Plan depth L1: process starts and health endpoint responds.
app.MapGet("/health", () => Results.Json(new { status = "ok" }));

// POST /v1/bookings — E-HTTP-CONTRACT-001
app.MapPost("/v1/bookings", async (HttpContext context, BookingService service) =>
{
    CreateBookingRequest? request;
    try
    {
        request = await context.Request.ReadFromJsonAsync<CreateBookingRequest>();
    }
    catch (Exception exception) when (exception is JsonException or InvalidOperationException or BadHttpRequestException)
    {
        return ApiResults.Error(
            StatusCodes.Status400BadRequest,
            ErrorCodes.InvalidRequest,
            "The request body must be a valid application/json document.");
    }

    if (request is null)
    {
        return ApiResults.Error(
            StatusCodes.Status400BadRequest,
            ErrorCodes.InvalidRequest,
            "A request body is required.");
    }

    var result = service.Create(new CreateBookingCommand(
        request.RoomId,
        request.CustomerId,
        request.StartUtc,
        request.EndUtc,
        request.IdempotencyKey));

    if (!result.IsSuccess)
    {
        return ApiResults.Error(ApiResults.StatusFor(result.ErrorCode!), result.ErrorCode!, result.Message!);
    }

    var booking = result.Booking!;
    context.Response.Headers.Location = $"/v1/bookings/{booking.Id}";

    // K-HTTP-REST-001: POST creates resources and returns 201.
    // K-IDEMPOTENCY-HTTP-001: a same-key/same-payload replay returns the original resource, also with 201.
    return Results.Json(BookingResponse.From(booking), statusCode: StatusCodes.Status201Created);
});

// GET /v1/bookings — E-HTTP-CONTRACT-001
app.MapGet("/v1/bookings", (BookingService service) =>
{
    var items = service.List().Select(BookingResponse.From).ToArray();
    return Results.Json(items, statusCode: StatusCodes.Status200OK);
});

// GET /v1/bookings/{id} — E-HTTP-CONTRACT-001
app.MapGet("/v1/bookings/{id}", (string id, BookingService service) =>
{
    var result = service.Get(id);
    return result.IsSuccess
        ? Results.Json(BookingResponse.From(result.Booking!), statusCode: StatusCodes.Status200OK)
        : ApiResults.Error(ApiResults.StatusFor(result.ErrorCode!), result.ErrorCode!, result.Message!);
});

// DELETE /v1/bookings/{id} — E-HTTP-CONTRACT-001 / E-CANCELLATION-001
app.MapDelete("/v1/bookings/{id}", (string id, BookingService service) =>
{
    var result = service.Cancel(id);
    return result.IsSuccess
        ? Results.Json(BookingResponse.From(result.Booking!), statusCode: StatusCodes.Status200OK)
        : ApiResults.Error(ApiResults.StatusFor(result.ErrorCode!), result.ErrorCode!, result.Message!);
});

app.Run();

namespace BomDD.WebApiSample.Api
{
    /// <summary>HTTP status mapping for the domain error codes (K-HTTP-REST-001).</summary>
    internal static class ApiResults
    {
        public static int StatusFor(string errorCode) => errorCode switch
        {
            ErrorCodes.InvalidRequest => StatusCodes.Status400BadRequest,
            ErrorCodes.Unauthorized => StatusCodes.Status401Unauthorized,
            ErrorCodes.NotFound => StatusCodes.Status404NotFound,
            ErrorCodes.SlotUnavailable => StatusCodes.Status409Conflict,
            ErrorCodes.IdempotencyConflict => StatusCodes.Status409Conflict,
            ErrorCodes.CancellationWindowClosed => StatusCodes.Status409Conflict,
            _ => StatusCodes.Status500InternalServerError
        };

        public static IResult Error(int statusCode, string code, string message)
            => Results.Json(new ErrorResponse(code, message), statusCode: statusCode);

        public static async Task WriteErrorAsync(HttpContext context, int statusCode, string code, string message)
        {
            context.Response.StatusCode = statusCode;
            context.Response.ContentType = "application/json; charset=utf-8";
            await context.Response.WriteAsJsonAsync(new ErrorResponse(code, message));
        }
    }
}
