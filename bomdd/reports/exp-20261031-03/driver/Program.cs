// EXP-20261031-03 step 1 (definitions sections 3, 5 and 6): the expected table from the authority.
// For each case: a fresh view model, LoadClip with the case's source rate, the presses through SetFpsCommand, then the
// slots V1-V8 by the view bindings of section 5 (the views themselves are not run). Writes the table as JSON to argv[0].
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Nodes;
using MoviePad.Models;
using MoviePad.Services;
using MoviePad.ViewModels;

var en = new CultureInfo("en");
CultureInfo.DefaultThreadCurrentCulture = en;
CultureInfo.DefaultThreadCurrentUICulture = en;
CultureInfo.CurrentCulture = en;
CultureInfo.CurrentUICulture = en;
Localizer.Instance.SetCulture(en);

double[] rates = { 25, 29.97, 30 };
string?[] firsts = { null, "24", "30", "60", "120" };
string[] seconds = { "Source", "24", "30", "60", "120" };
string Param(string button) => button == "Source" ? "source" : button;

var cases = new JsonArray();
foreach (var rate in rates)
{
    var list = new List<(string id, string[] presses)> { ($"{R(rate)}|opened", Array.Empty<string>()) };
    foreach (var f in firsts)
        foreach (var s in seconds)
            list.Add(($"{R(rate)}|{f ?? "none"}|{s}", f is null ? new[] { s } : new[] { f, s }));
    foreach (var (id, presses) in list)
    {
        var vm = new MainWindowViewModel();
        vm.LoadClip(Sample.Clip with { Fps = rate }, Sample.Doc);
        foreach (var b in presses) vm.SetFpsCommand.Execute(Param(b));
        string outText = vm.OutFpsText;
        bool Sel(string p) => string.Equals(outText, p, StringComparison.Ordinal);   // EqualsConverter
        cases.Add(new JsonObject
        {
            ["id"] = id,
            ["rate"] = rate,
            ["presses"] = new JsonArray(presses.Select(p => (JsonNode)JsonValue.Create(p)!).ToArray()),
            ["V1"] = string.Format("{0} fps", outText),                               // StringFormat '{}{0} fps'
            ["V2"] = vm.FpsSourceActive,
            ["V3"] = Sel("24"),
            ["V4"] = Sel("30"),
            ["V5"] = Sel("60"),
            ["V6"] = Sel("120"),
            ["V7"] = vm.FpsUpsampling,
            ["V8"] = vm.FpsSourceTip,
            ["outFps"] = vm.OutFps,
        });
    }
}

var doc = new JsonObject
{
    ["authority"] = "MoviePad 126eae9",
    ["CurrentCulture"] = CultureInfo.CurrentCulture.Name,
    ["CurrentUICulture"] = CultureInfo.CurrentUICulture.Name,
    ["LocalizerCulture"] = Localizer.Instance.Culture.Name,
    ["cases"] = cases,
};
File.WriteAllText(args[0], doc.ToJsonString(new JsonSerializerOptions { WriteIndented = true }) + "\n");
Console.WriteLine($"{cases.Count} cases; cultures {CultureInfo.CurrentCulture.Name} / {CultureInfo.CurrentUICulture.Name} / {Localizer.Instance.Culture.Name}");
return 0;

static string R(double r) => r.ToString(CultureInfo.InvariantCulture);
