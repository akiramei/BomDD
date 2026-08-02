namespace BomDD.WebApiSample.Core;

/// <summary>
/// Domain error codes.
/// E-ERROR-SCHEMA-001: errors carry a code and a message.
/// </summary>
public static class ErrorCodes
{
    /// <summary>K-HTTP-REST-001: all input validation failures use invalid_request.</summary>
    public const string InvalidRequest = "invalid_request";

    /// <summary>CP-CORE-OVERLAP-001 oracle: service.Create returns slot_unavailable for overlap.</summary>
    public const string SlotUnavailable = "slot_unavailable";

    /// <summary>E-IDEMPOTENCY-001 / K-IDEMPOTENCY-HTTP-001: same key + different fingerprint.</summary>
    public const string IdempotencyConflict = "idempotency_conflict";

    /// <summary>CP-CORE-CANCEL-001 oracle: service.Cancel returns cancellation_window_closed.</summary>
    public const string CancellationWindowClosed = "cancellation_window_closed";

    /// <summary>CHEAT-OPUS5-002: code name not fixed by BOM/K-BOM.</summary>
    public const string NotFound = "not_found";

    /// <summary>CP-AUTH-SURFACE-001 oracle: unauthorized request returns 401 + code=unauthorized.</summary>
    public const string Unauthorized = "unauthorized";
}
