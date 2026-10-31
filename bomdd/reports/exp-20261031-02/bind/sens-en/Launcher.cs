using System.Globalization;
using System.Reflection;

// launcher <ui-culture> <harness args...>: sets the UI culture of this thread (and of new threads), then calls the harness's
// own entry point with the rest of the arguments. The harness reads CultureInfo.CurrentUICulture at its start (initialCulture).
public static class Launcher
{
    public static int Main(string[] a)
    {
        var c = new CultureInfo(a[0]);
        CultureInfo.DefaultThreadCurrentUICulture = c;
        CultureInfo.CurrentUICulture = c;
        var harness = Assembly.Load("Harness");
        return (int)harness.EntryPoint!.Invoke(null, new object[] { a.Skip(1).ToArray() })!;
    }
}
