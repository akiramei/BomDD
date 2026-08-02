using System.Text;
using System.Text.Json;

namespace BomDD.WebApiSample.Acceptance;

/// <summary>One HTTP exchange, decoded far enough to assert on status, error code and body fields.</summary>
public sealed record Probe(int Status, string Body, JsonElement? Json)
{
    public string? Code => Text("code");

    public string? Text(string property)
        => Json is { ValueKind: JsonValueKind.Object } json &&
           json.TryGetProperty(property, out var value) &&
           value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;

    public string Describe() => $"HTTP {Status} {Body}";
}

/// <summary>Thin HTTP client for the L1/L3 depths. The API key is the M-BOM default demo key.</summary>
public sealed class HttpProbe(HttpClient http)
{
    public const string ApiKey = "demo-key";

    public Task<Probe> GetAsync(string path, string? apiKey = ApiKey)
        => SendAsync(HttpMethod.Get, path, apiKey, null);

    public Task<Probe> DeleteAsync(string path, string? apiKey = ApiKey)
        => SendAsync(HttpMethod.Delete, path, apiKey, null);

    public Task<Probe> PostJsonAsync(string path, object payload, string? apiKey = ApiKey)
        => SendAsync(HttpMethod.Post, path, apiKey, JsonSerializer.Serialize(payload));

    public Task<Probe> PostRawAsync(string path, string rawBody, string? apiKey = ApiKey)
        => SendAsync(HttpMethod.Post, path, apiKey, rawBody);

    public async Task<Probe> SendAsync(HttpMethod method, string path, string? apiKey, string? rawBody)
    {
        using var request = new HttpRequestMessage(method, ApiProcess.BaseUrl + path);
        if (apiKey is not null)
        {
            request.Headers.Add("X-Api-Key", apiKey);
        }

        if (rawBody is not null)
        {
            request.Content = new StringContent(rawBody, Encoding.UTF8, "application/json");
        }

        using var response = await http.SendAsync(request);
        var body = await response.Content.ReadAsStringAsync();

        JsonElement? json = null;
        try
        {
            using var document = JsonDocument.Parse(body);
            json = document.RootElement.Clone();
        }
        catch (JsonException)
        {
            // Not every response carries JSON; the caller asserts on that when it matters.
        }

        return new Probe((int)response.StatusCode, body, json);
    }

    public async Task<(int Status, string? Location, Probe Probe)> PostWithLocationAsync(string path, object payload)
    {
        using var request = new HttpRequestMessage(HttpMethod.Post, ApiProcess.BaseUrl + path);
        request.Headers.Add("X-Api-Key", ApiKey);
        request.Content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");

        using var response = await http.SendAsync(request);
        var body = await response.Content.ReadAsStringAsync();

        JsonElement? json = null;
        try
        {
            using var document = JsonDocument.Parse(body);
            json = document.RootElement.Clone();
        }
        catch (JsonException)
        {
        }

        var location = response.Headers.Location?.ToString()
                       ?? (response.Headers.TryGetValues("Location", out var values) ? values.FirstOrDefault() : null);

        return ((int)response.StatusCode, location, new Probe((int)response.StatusCode, body, json));
    }
}
