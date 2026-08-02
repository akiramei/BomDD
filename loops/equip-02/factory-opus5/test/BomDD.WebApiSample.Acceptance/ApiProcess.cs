using System.Diagnostics;
using System.Text;

namespace BomDD.WebApiSample.Acceptance;

/// <summary>
/// Starts src/BomDD.WebApiSample.Api as a separate process so that the L1 and L3 Control Plan
/// depths are exercised over real HTTP. The port is fixed at 5210 by the work order harness setup.
/// </summary>
public sealed class ApiProcess : IAsyncDisposable
{
    public const int Port = 5210;
    public const string BaseUrl = "http://127.0.0.1:5210";

    private readonly Process _process;
    private readonly StringBuilder _log;

    private ApiProcess(Process process, StringBuilder log)
    {
        _process = process;
        _log = log;
    }

    public string Log
    {
        get
        {
            lock (_log)
            {
                return _log.ToString();
            }
        }
    }

    public static async Task<ApiProcess> StartAsync(string workspaceRoot, HttpClient http)
    {
        var startInfo = BuildStartInfo(workspaceRoot);
        startInfo.RedirectStandardOutput = true;
        startInfo.RedirectStandardError = true;
        startInfo.UseShellExecute = false;
        startInfo.Environment["ASPNETCORE_URLS"] = BaseUrl;
        startInfo.Environment["DOTNET_ENVIRONMENT"] = "Production";
        startInfo.Environment["ASPNETCORE_ENVIRONMENT"] = "Production";

        var log = new StringBuilder();
        var process = new Process { StartInfo = startInfo, EnableRaisingEvents = true };
        process.OutputDataReceived += (_, e) => Append(log, e.Data);
        process.ErrorDataReceived += (_, e) => Append(log, e.Data);

        Console.WriteLine($"starting API: {startInfo.FileName} {string.Join(' ', startInfo.ArgumentList)}");
        if (!process.Start())
        {
            throw new AcceptanceException("the API process could not be started.");
        }

        process.BeginOutputReadLine();
        process.BeginErrorReadLine();

        var host = new ApiProcess(process, log);
        try
        {
            await host.WaitUntilHealthyAsync(http);
        }
        catch
        {
            await host.DisposeAsync();
            throw;
        }

        return host;
    }

    public async ValueTask DisposeAsync()
    {
        try
        {
            if (!_process.HasExited)
            {
                _process.Kill(entireProcessTree: true);
            }

            await _process.WaitForExitAsync(new CancellationTokenSource(TimeSpan.FromSeconds(10)).Token);
        }
        catch
        {
            // The harness verdict must not depend on how cleanly the child process went away.
        }
        finally
        {
            _process.Dispose();
        }
    }

    private async Task WaitUntilHealthyAsync(HttpClient http)
    {
        var deadline = DateTime.UtcNow.AddSeconds(90);
        while (DateTime.UtcNow < deadline)
        {
            if (_process.HasExited)
            {
                throw new AcceptanceException(
                    $"the API process exited with code {_process.ExitCode} before becoming healthy.{Environment.NewLine}{Log}");
            }

            try
            {
                using var response = await http.GetAsync($"{BaseUrl}/health");
                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"API is healthy on {BaseUrl}");
                    return;
                }
            }
            catch (HttpRequestException)
            {
                // Not listening yet.
            }
            catch (TaskCanceledException)
            {
                // Not listening yet.
            }

            await Task.Delay(250);
        }

        throw new AcceptanceException($"the API did not answer {BaseUrl}/health within 90 seconds.{Environment.NewLine}{Log}");
    }

    private static ProcessStartInfo BuildStartInfo(string workspaceRoot)
    {
        var projectDirectory = Path.Combine(workspaceRoot, "src", "BomDD.WebApiSample.Api");
        var assembly = FindApiAssembly(projectDirectory);

        var startInfo = new ProcessStartInfo("dotnet");
        if (assembly is not null)
        {
            startInfo.ArgumentList.Add(assembly);
            startInfo.WorkingDirectory = Path.GetDirectoryName(assembly)!;
            return startInfo;
        }

        // Fallback: no build output found, let the SDK build and run the project.
        startInfo.ArgumentList.Add("run");
        startInfo.ArgumentList.Add("--project");
        startInfo.ArgumentList.Add(projectDirectory);
        startInfo.ArgumentList.Add("--no-launch-profile");
        startInfo.WorkingDirectory = workspaceRoot;
        return startInfo;
    }

    private static string? FindApiAssembly(string projectDirectory)
    {
        var binDirectory = Path.Combine(projectDirectory, "bin");
        if (!Directory.Exists(binDirectory))
        {
            return null;
        }

        return Directory
            .EnumerateFiles(binDirectory, "BomDD.WebApiSample.Api.dll", SearchOption.AllDirectories)
            .Where(path => File.Exists(Path.ChangeExtension(path, ".runtimeconfig.json")))
            .OrderByDescending(File.GetLastWriteTimeUtc)
            .FirstOrDefault();
    }

    private static void Append(StringBuilder log, string? line)
    {
        if (line is null)
        {
            return;
        }

        lock (log)
        {
            log.AppendLine(line);
        }
    }
}
