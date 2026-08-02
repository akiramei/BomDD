using BomDD.WebApiSample.Acceptance;

// M-ACCEPTANCE-HARNESS-001 — verifies M-CORE-BOOKING-SERVICE-001, M-OPENAPI-DOCUMENT-001
// and (through a live process on port 5210) M-API-ENDPOINTS-001.
//
// Control Plan depths exercised:
//   unit : core booking rules, no HTTP process
//   L1   : process starts and the health endpoint responds
//   L2   : OpenAPI contract inspection
//   L3   : interaction, replay, conflict and concurrency over HTTP

var runner = new Runner();
var workspaceRoot = WorkspaceLocator.Find();

Console.WriteLine($"workspace: {workspaceRoot}");
Console.WriteLine();

UnitChecks.Run(runner);
ContractChecks.Run(runner, workspaceRoot);

using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(30) };
ApiProcess? api = null;
try
{
    api = await ApiProcess.StartAsync(workspaceRoot, http);
    await HttpChecks.RunAsync(runner, new HttpProbe(http));
}
catch (Exception exception)
{
    runner.Fatal("L1", "the API process starts on port 5210", exception.Message);
}
finally
{
    if (api is not null)
    {
        await api.DisposeAsync();
    }
}

return runner.Summarize();

namespace BomDD.WebApiSample.Acceptance
{
    /// <summary>Locates the manufacturing workspace root from the harness output directory.</summary>
    internal static class WorkspaceLocator
    {
        public static string Find()
        {
            var directory = new DirectoryInfo(AppContext.BaseDirectory);
            while (directory is not null)
            {
                if (File.Exists(Path.Combine(directory.FullName, "openapi", "openapi.json")) &&
                    Directory.Exists(Path.Combine(directory.FullName, "src", "BomDD.WebApiSample.Api")))
                {
                    return directory.FullName;
                }

                directory = directory.Parent;
            }

            throw new InvalidOperationException(
                $"the workspace root could not be located from {AppContext.BaseDirectory}.");
        }
    }
}
