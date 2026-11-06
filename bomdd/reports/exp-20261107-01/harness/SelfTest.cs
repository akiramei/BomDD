// Synthetic selftest (definitions.md section 8 step 1): every extraction rule and every step check, each with a firing case
// and a silent twin, reported check by check. Touches no authority file.
using System.Text.Json.Nodes;
using System.Windows.Input;
using CommunityToolkit.Mvvm.Input;

namespace Exp04;

public class StubVm
{
    public bool A { get; set; } = true;     // panel visible
    public bool B { get; set; }             // went
    public bool M { get; set; }             // modal open
    public string? P { get; set; }
    public int N { get; set; }
    public ICommand GoCommand { get; }
    public ICommand BackCommand { get; }
    public ICommand OpenCommand { get; }
    public ICommand CloseCommand { get; }
    public ICommand PickCommand { get; }
    public ICommand ConvCommand { get; }
    public ICommand LoadCommand { get; }
    public StubVm()
    {
        GoCommand = new RelayCommand(() => B = true);
        BackCommand = new RelayCommand(() => B = false);
        OpenCommand = new RelayCommand(() => M = true);
        CloseCommand = new RelayCommand(() => M = false);
        PickCommand = new RelayCommand<string>(s => { P = s; N++; });
        ConvCommand = new RelayCommand(() => { });
        LoadCommand = new AsyncRelayCommand(() => Task.CompletedTask);
    }
}

public static class SelfTest
{
    const string Main = """
        <Window xmlns="https://github.com/avaloniaui" xmlns:views="using:MoviePad.Views">
          <Panel>
            <views:PanelView IsVisible="{Binding A}" />
            <Button Command="{Binding OpenCommand}" Content="Open" />
            <Button Command="{Binding LoadCommand}" Content="Load" />
            <Panel IsVisible="{Binding M}" Background="{StaticResource ScrimBrush}">
              <Button Command="{Binding CloseCommand}" Content="{l:Translate K_Close}" />
            </Panel>
          </Panel>
        </Window>
        """;
    const string PanelV = """
        <UserControl xmlns="https://github.com/avaloniaui">
          <StackPanel>
            <Button Command="{Binding GoCommand}" IsEnabled="{Binding !B}" Content="Go" />
            <Button Command="{Binding BackCommand}" IsEnabled="{Binding B}" Content="Back" />
            <Button Command="{Binding PickCommand}" CommandParameter="x" Content="Pick x" />
            <Button Command="{Binding ConvCommand}" IsEnabled="{Binding B, Converter={StaticResource C}}" />
          </StackPanel>
        </UserControl>
        """;
    const string Orphan = """
        <UserControl xmlns="https://github.com/avaloniaui"><Button Command="{Binding GoCommand}" /></UserControl>
        """;

    static int _fail;
    static void Check(string name, bool fires, bool silentTwin)
    {
        bool ok = fires && silentTwin;
        if (!ok) _fail++;
        Console.WriteLine($"  {(ok ? "PASS" : "FAIL")} {name} (fires={fires}, silent twin={silentTwin})");
    }

    static JsonObject Scen(string steps, string setup = "[]") => JsonNode.Parse($$$"""
        {"states": [
          {"id": "start", "predicate": {"B": false, "M": false, "A": true}},
          {"id": "went",  "predicate": {"B": true,  "M": false, "A": true}},
          {"id": "modal", "predicate": {"B": false, "M": true}},
          {"id": "hidden", "predicate": {"A": false, "M": false}},
          {"id": "picked", "predicate": {"P": "x", "B": false, "M": false, "A": true}},
          {"id": "any", "predicate": {"M": false}}],
         "scenarios": [{"id": "s", "title": "t", "goal": "g", "flow": "main", "setup": {{{setup}}}, "steps": {{{steps}}}}]}
        """)!.AsObject();

    static StepResult First(Bindings b, string steps, string setup = "[]")
    {
        var c = new Certifier(() => new StubVm(), b, Scen(steps, setup));
        var r = c.Run().steps;
        return r.FirstOrDefault(x => !x.Pass) ?? r.Last();
    }

    static string S(string a, string inS, string exp, string surf = "PanelView", string extra = "") =>
        $$$"""{"in": "{{{inS}}}", "action": "{{{a}}}", "surface": "{{{surf}}}", "expect": "{{{exp}}}"{{{extra}}}}""";

    public static int Run()
    {
        var files = new Dictionary<string, string> { ["MainWindow"] = Main, ["PanelView"] = PanelV, ["OrphanView"] = Orphan };
        var b = Extractor.Extract(files, new Dictionary<string, string> { ["K_Close"] = "Close it" }, Array.Empty<string>());
        Console.WriteLine("extraction");
        var pick = b.Elements.FirstOrDefault(e => e.Id == "Pick:x");
        Check("X1 parameter id", pick != null, b.Elements.Any(e => e.Id == "Go"));
        Check("X2 surface and placement condition", pick?.Surface == "PanelView" && pick.Conds.Any(c => c.Path == "A" && c.Kind == "visible"),
              b.Elements.First(e => e.Id == "Open").Conds.All(c => c.Path != "A"));
        Check("X3 negation and enabledness", b.Elements.First(e => e.Id == "Go" && e.Surface == "PanelView").Conds.Any(c => c.Path == "B" && c.Negate && c.Kind == "enabled"),
              b.Elements.First(e => e.Id == "Back").Conds.Any(c => c.Path == "B" && !c.Negate));
        Check("X4 converter binding is unknown", b.Elements.First(e => e.Id == "Conv").Unknown != null,
              b.Elements.First(e => e.Id == "Back").Unknown == null);
        Check("X5 unplaced surface is unknown", b.Elements.First(e => e.Surface == "OrphanView").Unknown != null, pick?.Unknown == null);
        Check("X6 scrim overlay is a modal", b.Modals.Count == 1 && b.Elements.First(e => e.Id == "Close").Modal == b.Modals[0].Id,
              b.Elements.First(e => e.Id == "Open").Modal == null);
        Check("X7 translated label", b.Elements.First(e => e.Id == "Close").Label == "Close it", b.Elements.First(e => e.Id == "Go" && e.Surface == "PanelView").Label == "Go");

        Console.WriteLine("step checks");
        var good = First(b, $"[{S("Go", "start", "went")}]");
        Check("C1 in-state must hold", !First(b, $"[{S("Go", "went", "went")}]").Pass, good.Pass);
        Check("C2 disabled action", First(b, $"[{S("Back", "start", "start")}]").Reason == "action disabled", good.Pass);
        Check("C2b absent by placement condition",
              First(b, $"[{S("Go", "hidden", "hidden")}]", """[{"set": "A", "value": false}]""").Reason == "action absent", good.Pass);
        var occluded = First(b, $"[{S("Open", "start", "modal", "MainWindow")},{S("Go", "modal", "went")}]");
        var insideModal = First(b, $"[{S("Open", "start", "modal", "MainWindow")},{S("Close", "modal", "start", "MainWindow")}]");
        Check("C2c occluded by an open modal", occluded.Index == 1 && occluded.Reason == "action absent", insideModal.Pass);
        Check("C3 surface must match", First(b, $"[{S("Go", "start", "went", "MainWindow")}]").Reason!.StartsWith("surface"), good.Pass);
        Check("C4 expect-state must hold", First(b, $"[{S("Go", "start", "start")}]").Reason!.StartsWith("expect"), good.Pass);
        Check("C5 unknown action id", First(b, $"[{S("Nope", "start", "went")}]").Reason == "unknown action id", good.Pass);
        Check("C6 async needs harness:no", First(b, $"[{S("Load", "start", "start", "MainWindow")}]").Reason!.StartsWith("async"),
              First(b, $"[{S("Load", "start", "start", "MainWindow", ", \"harness\": \"no\"")}]").Pass);
        Check("C7 parameter passed", First(b, $"[{S("Pick:x", "start", "picked")}]").Pass,
              !First(b, $"[{S("Pick:x", "start", "went")}]").Pass);
        Check("C8 setup op", First(b, $"[{S("Go", "start", "went")}]", """[{"set": "N", "value": 3}]""").Pass,
              !First(b, $"[{S("Go", "start", "went")}]", """[{"set": "B", "value": true}]""").Pass);

        Console.WriteLine("mock generation and ambiguity");
        var cert = new Certifier(() => new StubVm(), b, Scen($"[{S("Go", "start", "went")},{S("Back", "went", "start")}]"));
        var (_, pts, trans, _) = cert.Run();
        var (mock, amb) = cert.Mock(pts, trans);
        var start = mock["states"]!.AsArray().First(s => (string)s!["id"]! == "start")!;
        var goEntry = start["actions"]!.AsArray().First(x => (string)x!["id"]! == "Go")!;
        var backEntry = start["actions"]!.AsArray().First(x => (string)x!["id"]! == "Back")!;
        Check("G1 goto is the set of states holding after", ((string)goEntry["goto"]!).Split(' ').Contains("went"),
              (bool)backEntry["enabled"]! == false && (string)backEntry["goto"]! == "-");
        Check("G2 only visited states are in the mock", !mock["states"]!.AsArray().Any(s => (string)s!["id"]! == "modal"),
              start["actions"]!.AsArray().Any(x => (string)x!["id"]! == "Open"));
        // "any" holds both before and after Go with different availability -> ambiguous; "start" is consistent
        Check("A1 ambiguous state detected", amb.ContainsKey("any"), !amb.ContainsKey("start") && !amb.ContainsKey("went"));

        Console.WriteLine(_fail == 0 ? "selftest PASS" : $"selftest FAIL ({_fail})");
        return _fail == 0 ? 0 : 1;
    }
}
