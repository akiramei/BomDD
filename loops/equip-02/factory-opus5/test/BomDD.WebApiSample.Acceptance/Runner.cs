namespace BomDD.WebApiSample.Acceptance;

/// <summary>Raised by <see cref="Check.Expect"/> when an acceptance expectation is not met.</summary>
public sealed class AcceptanceException(string message) : Exception(message);

public static class Check
{
    public static void Expect(bool condition, string message)
    {
        if (!condition)
        {
            throw new AcceptanceException(message);
        }
    }

    public static void ExpectEqual<T>(T expected, T actual, string what)
    {
        if (!EqualityComparer<T>.Default.Equals(expected, actual))
        {
            throw new AcceptanceException($"{what}: expected <{expected}>, actual <{actual}>.");
        }
    }
}

/// <summary>
/// Collects the Control Plan characteristics as they are exercised and reports a single verdict.
/// Every case is labelled with the Control Plan characteristic id (or the depth) it covers.
/// </summary>
public sealed class Runner
{
    private readonly List<string> _failures = [];
    private int _passed;

    public void Case(string id, string title, Action body)
    {
        try
        {
            body();
            _passed++;
            Console.WriteLine($"PASS  {id}  {title}");
        }
        catch (Exception exception)
        {
            Record(id, title, exception);
        }
    }

    public async Task CaseAsync(string id, string title, Func<Task> body)
    {
        try
        {
            await body();
            _passed++;
            Console.WriteLine($"PASS  {id}  {title}");
        }
        catch (Exception exception)
        {
            Record(id, title, exception);
        }
    }

    public void Fatal(string id, string title, string message)
    {
        _failures.Add($"{id}  {title}: {message}");
        Console.WriteLine($"FAIL  {id}  {title}");
        Console.WriteLine($"      {message}");
    }

    public int Summarize()
    {
        Console.WriteLine();
        Console.WriteLine(new string('-', 72));
        Console.WriteLine($"acceptance: {_passed} passed, {_failures.Count} failed");

        if (_failures.Count == 0)
        {
            Console.WriteLine("ACCEPTANCE: PASS");
            return 0;
        }

        Console.WriteLine();
        foreach (var failure in _failures)
        {
            Console.WriteLine($"  - {failure}");
        }

        Console.WriteLine("ACCEPTANCE: FAIL");
        return 1;
    }

    private void Record(string id, string title, Exception exception)
    {
        var message = exception is AcceptanceException ? exception.Message : exception.ToString();
        _failures.Add($"{id}  {title}: {message}");
        Console.WriteLine($"FAIL  {id}  {title}");
        Console.WriteLine($"      {message}");
    }
}

/// <summary>Deterministic clock for the cancellation window checks (E-CANCELLATION-001).</summary>
public sealed class FixedTimeProvider(DateTimeOffset now) : TimeProvider
{
    public DateTimeOffset Now { get; set; } = now;

    public override DateTimeOffset GetUtcNow() => Now;
}
