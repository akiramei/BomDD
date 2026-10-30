// EXP-20261030-04 harness (definitions.md sections 4-5).
//   harness extract  <authority-dir> <bindings.json>
//   harness certify  <bindings.json> <scenarios.json> <certify.json> <mockdata.json>
//   harness selftest
// Extraction reads Views/*.axaml as XML; certification executes scenario steps on a fresh view model per scenario.
using System.Globalization;
using System.Reflection;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using System.Windows.Input;
using System.Xml.Linq;

namespace Exp04;

public record Cond(string Kind, string Path, bool Negate, string? Constant);          // Kind: visible | enabled
public record Elem(string Id, string Command, string? Param, string Surface, int Line, List<Cond> Conds, string? Modal,
                   string? Label, string? Unknown);
public record Modal(string Id, int Order, List<Cond> Conds);
public record Bindings(List<Elem> Elements, List<Modal> Modals, List<string> CodeBehind);

public static class Extractor
{
    static readonly Regex BindRx = new(@"^\{Binding\s+(!?)([A-Za-z_][\w.]*)\s*\}$");
    static readonly Regex CmdRx = new(@"^\{Binding\s+([A-Za-z_]\w*)Command\s*\}$");
    static readonly Regex TrRx = new(@"^\{l:Translate\s+([\w.]+)\s*\}$");

    record Raw(Elem E);
    record Placement(string Surface, int Line, List<Cond> Conds, string? Modal);

    // files: surface name -> axaml text; strings: resource key -> text
    public static Bindings Extract(IDictionary<string, string> files, IDictionary<string, string> strings,
                                   IEnumerable<string> codeBehind)
    {
        var local = new Dictionary<string, List<Elem>>();
        var localModals = new Dictionary<string, List<(string id, int line, List<Cond> conds)>>();
        var placements = new List<Placement>();
        foreach (var (surface, text) in files)
        {
            var doc = XDocument.Parse(text, LoadOptions.SetLineInfo);
            var elems = new List<Elem>();
            var modals = new List<(string, int, List<Cond>)>();
            Walk(doc.Root!, surface, new List<Cond>(), null, false, elems, modals, placements, strings);
            local[surface] = elems;
            localModals[surface] = modals;
        }
        var outElems = new List<Elem>();
        var outModals = new List<Modal>();
        Placement? Place(string s) => placements.FirstOrDefault(p => p.Surface == s);
        foreach (var (surface, elems) in local)
        {
            var pl = surface == "MainWindow" ? null : Place(surface);
            var baseConds = pl?.Conds ?? new List<Cond>();
            // stacking: document order in MainWindow; a placed view's own overlays sit at its placement line
            foreach (var (id, line, conds) in localModals[surface])
                outModals.Add(new Modal(id, surface == "MainWindow" ? line * 100000 : (pl?.Line ?? 0) * 100000 + line,
                                        baseConds.Concat(conds).ToList()));
            foreach (var e in elems)
            {
                var unknown = e.Unknown;
                if (pl == null && surface != "MainWindow") unknown ??= "surface not placed in MainWindow";
                outElems.Add(e with { Conds = baseConds.Concat(e.Conds).ToList(), Modal = e.Modal ?? pl?.Modal, Unknown = unknown });
            }
        }
        return new Bindings(outElems.OrderBy(e => e.Surface).ThenBy(e => e.Line).ToList(),
                            outModals.OrderBy(m => m.Order).ToList(), codeBehind.ToList());
    }

    static Cond? ParseCond(string kind, string value, out string? unknown)
    {
        unknown = null;
        var v = value.Trim();
        if (v == "True" || v == "False") return new Cond(kind, "", false, v);
        var m = BindRx.Match(v);
        if (m.Success) return new Cond(kind, m.Groups[2].Value, m.Groups[1].Value == "!", null);
        unknown = $"{kind} binding not a plain path: {v}";
        return null;
    }

    static string? Text(string? v, IDictionary<string, string> strings)
    {
        if (v == null) return null;
        var m = TrRx.Match(v.Trim());
        if (m.Success) return strings.TryGetValue(m.Groups[1].Value, out var s) ? s : m.Groups[1].Value;
        return v.StartsWith("{") ? null : v;
    }

    static void Walk(XElement x, string surface, List<Cond> inherited, string? modal, bool inheritedUnknown,
                     List<Elem> elems, List<(string, int, List<Cond>)> modals, List<Placement> placements,
                     IDictionary<string, string> strings)
    {
        int line = ((System.Xml.IXmlLineInfo)x).LineNumber;
        var conds = new List<Cond>(inherited);
        string? unknown = null;
        foreach (var attrName in new[] { "IsVisible", "IsEnabled" })
        {
            var a = x.Attribute(attrName);
            if (a == null) continue;
            var c = ParseCond(attrName == "IsVisible" ? "visible" : "enabled", a.Value, out var u);
            if (c != null) conds.Add(c); else unknown = u;
        }
        bool isUnknown = inheritedUnknown || unknown != null;
        string? unknownReason = unknown ?? (inheritedUnknown ? "an ancestor's binding is not a plain path" : null);
        var bg = x.Attribute("Background")?.Value ?? "";
        if (bg.Contains("ScrimBrush"))
        {
            modal = $"{surface}:{line}";
            modals.Add((modal, line, new List<Cond>(conds)));
        }
        var name = x.Name.LocalName;
        if (x.Name.NamespaceName.Contains("MoviePad.Views") || (name.EndsWith("View") && x.Name.NamespaceName.StartsWith("using:")))
            placements.Add(new Placement(name, line, new List<Cond>(conds.Where(c => c.Kind == "visible")), modal));
        var cmd = x.Attribute("Command")?.Value;
        if (cmd != null)
        {
            var cm = CmdRx.Match(cmd.Trim());
            var p = x.Attribute("CommandParameter")?.Value;
            var label = Text(x.Attribute("Content")?.Value, strings) ?? Text(x.Attribute("Header")?.Value, strings)
                        ?? Text(x.Attribute(XName.Get("ToolTip.Tip"))?.Value, strings)
                        ?? x.Descendants().Select(d => Text(d.Attribute("Text")?.Value, strings)).FirstOrDefault(t => t != null);
            if (!cm.Success)
                elems.Add(new Elem(cmd, cmd, p, surface, line, conds, modal, label, "Command not a plain {Binding XCommand}"));
            else
            {
                var c = cm.Groups[1].Value;
                elems.Add(new Elem(p == null ? c : $"{c}:{p}", c, p, surface, line, conds, modal, label,
                                   isUnknown ? unknownReason : null));
            }
        }
        foreach (var child in x.Elements()) Walk(child, surface, conds, modal, isUnknown, elems, modals, placements, strings);
    }

    public static Dictionary<string, string> ReadResx(string path)
    {
        var d = new Dictionary<string, string>();
        if (!File.Exists(path)) return d;
        foreach (var data in XDocument.Load(path).Root!.Elements("data"))
            d[(string)data.Attribute("name")!] = (string?)data.Element("value") ?? "";
        return d;
    }
}

public class StepResult
{
    public string Scenario = "", Action = "", In = "", Expect = "", Surface = "";
    public int Index;
    public bool Pass;
    public string? Reason;
    public bool Executed;
}

public class Certifier
{
    readonly Func<object> _factory;
    readonly Type _vmType;
    readonly Bindings _b;
    readonly Dictionary<string, List<Elem>> _byId = new();
    public readonly List<object> UnresolvedElements = new();
    readonly JsonObject _states;
    readonly JsonArray _scenarios;

    public Certifier(Func<object> factory, Bindings b, JsonObject scenarioFile)
    {
        _factory = factory;
        _vmType = factory().GetType();
        _b = b;
        _states = new JsonObject();
        foreach (var s in scenarioFile["states"]!.AsArray())
            _states[(string)s!["id"]!] = s["predicate"]!.DeepClone();
        _scenarios = scenarioFile["scenarios"]!.AsArray();
        foreach (var e in b.Elements)
        {
            string? why = e.Unknown;
            if (why == null && _vmType.GetProperty(e.Command + "Command") == null) why = $"no property {e.Command}Command";
            foreach (var c in e.Conds)
                if (why == null && c.Constant == null && !Resolvable(c.Path)) why = $"path {c.Path} not on the view model";
            foreach (var m in b.Modals)
                foreach (var c in m.Conds)
                    if (why == null && c.Constant == null && !Resolvable(c.Path)) why = $"modal path {c.Path} not on the view model";
            if (why != null) { UnresolvedElements.Add(new { e.Id, e.Surface, e.Line, why }); continue; }
            if (!_byId.TryGetValue(e.Id, out var l)) _byId[e.Id] = l = new List<Elem>();
            l.Add(e);
        }
    }

    public IEnumerable<string> KnownIds => _byId.Keys.OrderBy(k => k, StringComparer.Ordinal);

    bool Resolvable(string path)
    {
        Type t = _vmType;
        foreach (var part in path.Split('.'))
        {
            var p = t.GetProperty(part);
            if (p == null) return false;
            t = p.PropertyType;
        }
        return true;
    }

    static object? Get(object o, string path)
    {
        object? cur = o;
        foreach (var part in path.Split('.'))
        {
            if (cur == null) return null;
            var p = cur.GetType().GetProperty(part);
            if (p == null) throw new InvalidOperationException($"no property {part}");
            cur = p.GetValue(cur);
        }
        return cur;
    }

    static bool Truthy(object? v) => v is bool b ? b : v != null;

    bool CondHolds(object vm, Cond c)
    {
        bool v = c.Constant != null ? c.Constant == "True" : Truthy(Get(vm, c.Path));
        return c.Negate ? !v : v;
    }

    static bool Matches(object? actual, JsonNode? expected)
    {
        if (expected == null) return actual == null;
        if (expected is JsonValue jv)
        {
            if (jv.TryGetValue<string>(out var s))
            {
                if (s == "not-null") return actual != null;
                return actual != null && Convert.ToString(actual, CultureInfo.InvariantCulture) == s;
            }
            if (jv.TryGetValue<bool>(out var b)) return actual is bool ab && ab == b;
            if (jv.TryGetValue<double>(out var d))
                return actual != null && actual is IConvertible && Math.Abs(Convert.ToDouble(actual, CultureInfo.InvariantCulture) - d) < 1e-9;
        }
        return false;
    }

    public bool Holds(object vm, string stateId)
    {
        if (_states[stateId] is not JsonObject pred) throw new InvalidOperationException($"unknown state {stateId}");
        foreach (var (path, val) in pred)
            if (!Matches(Get(vm, path), val)) return false;
        return true;
    }

    public List<string> Holding(object vm) =>
        _states.Select(kv => kv.Key).Where(id => Holds(vm, id)).OrderBy(x => x, StringComparer.Ordinal).ToList();

    Modal? TopModal(object vm) => _b.Modals.Where(m => m.Conds.All(c => CondHolds(vm, c))).OrderBy(m => m.Order).LastOrDefault();

    // "enabled" | "disabled" | "absent", with the surface of the first visible element
    public (string status, string? surface) Avail(object vm, string id)
    {
        if (!_byId.TryGetValue(id, out var elems)) return ("unknown", null);
        var top = TopModal(vm);
        string best = "absent"; string? surf = null;
        foreach (var e in elems)
        {
            bool visible = e.Conds.Where(c => c.Kind == "visible").All(c => CondHolds(vm, c)) && (top == null || e.Modal == top.Id);
            if (!visible) continue;
            bool enabled = e.Conds.Where(c => c.Kind == "enabled").All(c => CondHolds(vm, c))
                           && Cmd(vm, e).CanExecute(e.Param);
            if (enabled) return ("enabled", e.Surface);
            if (best == "absent") { best = "disabled"; surf = e.Surface; }
        }
        return (best, surf);
    }

    ICommand Cmd(object vm, Elem e) => (ICommand)_vmType.GetProperty(e.Command + "Command")!.GetValue(vm)!;

    // commands the harness never executes: async ones, and those with effects outside the process (definitions D8)
    public static readonly HashSet<string> NoExecuteCommands = new();

    public bool IsAsync(string id) =>
        _byId.TryGetValue(id, out var es) && (NoExecuteCommands.Contains(es[0].Command)
            || Cmd(_factory(), es[0]).GetType().GetInterfaces().Any(i => i.Name == "IAsyncRelayCommand"));

    public string Vector(object vm) => string.Join(";", KnownIds.Select(id => $"{id}={Avail(vm, id).status[0]}"));

    void Execute(object vm, string id)
    {
        var e = _byId[id][0];
        Cmd(vm, e).Execute(e.Param);
    }

    void Setup(object vm, JsonArray? ops)
    {
        if (ops == null) return;
        foreach (var op in ops)
        {
            if (op!["set"] is JsonNode setNode)
            {
                var p = vm.GetType().GetProperty((string)setNode!)!;
                var raw = op["value"];
                object? v = raw == null ? null : p.PropertyType == typeof(bool) ? raw.GetValue<bool>()
                    : p.PropertyType == typeof(string) ? raw.GetValue<string>()
                    : Convert.ChangeType(raw.GetValue<double>(), Nullable.GetUnderlyingType(p.PropertyType) ?? p.PropertyType,
                                         CultureInfo.InvariantCulture);
                p.SetValue(vm, v);
            }
            else if (op["state_call"] is JsonNode callNode)
            {
                var sp = vm.GetType().GetProperty("State")!;
                var st = sp.GetValue(vm)!;
                var args = op["args"]?.AsArray() ?? new JsonArray();
                var m = st.GetType().GetMethods().First(mm => mm.Name == (string)callNode! && mm.GetParameters().Length == args.Count);
                var conv = m.GetParameters().Select((pi, i) => ConvertArg(args[i], pi.ParameterType)).ToArray();
                sp.SetValue(vm, m.Invoke(st, conv));
            }
            else throw new InvalidOperationException($"unknown setup op {op.ToJsonString()}");
        }
    }

    static object? ConvertArg(JsonNode? n, Type t)
    {
        if (n == null) return null;
        if (t == typeof(bool)) return n.GetValue<bool>();
        if (t == typeof(string)) return n.GetValue<string>();
        return Convert.ChangeType(n.GetValue<double>(), t, CultureInfo.InvariantCulture);
    }

    static bool HarnessNo(JsonNode step) => (string?)step["harness"] == "no";

    // VM after setup and the first k executed steps of scenario s
    public object Replay(JsonObject s, int k)
    {
        var vm = _factory();
        Setup(vm, s["setup"]?.AsArray());
        var steps = s["steps"]!.AsArray();
        for (int i = 0; i < k; i++) Execute(vm, (string)steps[i]!["action"]!);
        return vm;
    }

    public record Point(string Scenario, int K, List<string> States, string Vector)
    {
        public Dictionary<string, string?> Values { get; init; } = new();
    }

    // every view-model path the bindings read, for the writer to make states exact
    public Dictionary<string, string?> Values(object vm) =>
        _b.Elements.SelectMany(e => e.Conds).Concat(_b.Modals.SelectMany(m => m.Conds))
            .Where(c => c.Constant == null && Resolvable(c.Path)).Select(c => c.Path).Distinct().OrderBy(p => p, StringComparer.Ordinal)
            .ToDictionary(p => p, p => Convert.ToString(Get(vm, p), CultureInfo.InvariantCulture));
    public record Trans(string Scenario, int K, string Action, List<string> From, List<string> To);

    public (List<StepResult> steps, List<Point> points, List<Trans> trans, Dictionary<string, bool> certified) Run(
        ISet<string>? only = null)
    {
        var results = new List<StepResult>();
        var points = new List<Point>();
        var trans = new List<Trans>();
        var certified = new Dictionary<string, bool>();
        foreach (var sn in _scenarios)
        {
            var s = sn!.AsObject();
            var sid = (string)s["id"]!;
            if (only != null && !only.Contains(sid)) continue;
            bool ok = true;
            object vm;
            try { vm = _factory(); Setup(vm, s["setup"]?.AsArray()); }
            catch (Exception ex) { results.Add(new StepResult { Scenario = sid, Reason = "setup: " + ex.Message }); certified[sid] = false; continue; }
            var steps = s["steps"]!.AsArray();
            points.Add(new Point(sid, 0, Holding(vm), Vector(vm)) { Values = Values(vm) });
            for (int i = 0; i < steps.Count; i++)
            {
                var st = steps[i]!;
                var r = new StepResult { Scenario = sid, Index = i, Action = (string)st["action"]!, In = (string)st["in"]!,
                                         Expect = (string)st["expect"]!, Surface = (string)st["surface"]! };
                results.Add(r);
                try
                {
                    if (!_byId.ContainsKey(r.Action)) r.Reason = "unknown action id";
                    else if (!_states.ContainsKey(r.In) || !_states.ContainsKey(r.Expect)) r.Reason = "unknown state id";
                    else if (!Holds(vm, r.In)) r.Reason = $"in-state {r.In} does not hold";
                    else
                    {
                        var (status, surf) = Avail(vm, r.Action);
                        if (status != "enabled") r.Reason = $"action {status}";
                        else if (surf != r.Surface) r.Reason = $"surface is {surf}";
                        else if (HarnessNo(st)) { r.Pass = true; r.Reason = "harness:no (not executed)"; }
                        else if (IsAsync(r.Action)) r.Reason = "async command: mark harness:no";
                        else
                        {
                            var from = Holding(vm);
                            Execute(vm, r.Action);
                            r.Executed = true;
                            var to = Holding(vm);
                            trans.Add(new Trans(sid, i, r.Action, from, to));
                            points.Add(new Point(sid, i + 1, to, Vector(vm)) { Values = Values(vm) });
                            if (!Holds(vm, r.Expect)) r.Reason = $"expect-state {r.Expect} does not hold (holding: {string.Join(",", to)})";
                            else r.Pass = true;
                        }
                    }
                }
                catch (Exception ex) { r.Reason = "exception: " + (ex.InnerException ?? ex).Message; }
                if (!r.Pass) { ok = false; break; }
                if (HarnessNo(st)) break;
            }
            certified[sid] = ok;
        }
        return (results, points, trans, certified);
    }

    public JsonArray ScenarioArray => _scenarios;

    // representative point per state, ambiguity, mock data — over the given certified scenarios
    public (JsonObject mock, JsonObject ambiguity) Mock(List<Point> points, List<Trans> trans)
    {
        var rep = new Dictionary<string, Point>();
        var vectors = new Dictionary<string, HashSet<string>>();
        foreach (var p in points)
            foreach (var st in p.States)
            {
                rep.TryAdd(st, p);
                if (!vectors.TryGetValue(st, out var set)) vectors[st] = set = new HashSet<string>();
                set.Add(p.Vector);
            }
        var amb = new JsonObject();
        foreach (var (st, set) in vectors)
            if (set.Count > 1)
            {
                var parts = set.Select(v => v.Split(';').ToHashSet()).ToList();
                var common = parts.Aggregate((a, b) => a.Intersect(b).ToHashSet());
                var differing = parts.SelectMany(x => x).Except(common).Select(x => x.Split('=')[0]).Distinct().OrderBy(x => x);
                amb[st] = "availability differs between visits: " + string.Join(",", differing);
            }
        var scen = _scenarios.Select(n => n!.AsObject()).ToDictionary(o => (string)o["id"]!);
        var gotoCache = new Dictionary<(string, string), List<string>>();
        List<string> GotoAt(string st, string action)
        {
            if (gotoCache.TryGetValue((st, action), out var g)) return g;
            var p = rep[st];
            var vm = Replay(scen[p.Scenario], p.K);
            Execute(vm, action);
            return gotoCache[(st, action)] = Holding(vm);
        }
        foreach (var t in trans)
            foreach (var st in t.From)
            {
                if (amb.ContainsKey(st)) continue;
                List<string> g;
                try { g = GotoAt(st, t.Action); } catch (Exception ex) { amb[st] = $"goto of {t.Action} failed: {ex.Message}"; continue; }
                if (!g.SequenceEqual(t.To)) amb[st] = $"transition of {t.Action} differs between visits";
            }
        var states = new JsonArray();
        foreach (var st in rep.Keys.OrderBy(x => x, StringComparer.Ordinal))
        {
            if (amb.ContainsKey(st)) continue;
            var p = rep[st];
            var vm = Replay(scen[p.Scenario], p.K);
            var actions = new JsonArray();
            foreach (var id in KnownIds)
            {
                var (status, surf) = Avail(vm, id);
                if (status == "absent") continue;
                string gotoStr;
                if (status != "enabled") gotoStr = "-";
                else if (IsAsync(id)) gotoStr = "unknown";
                else
                {
                    try { gotoStr = string.Join(" ", GotoAt(st, id)); if (gotoStr == "") gotoStr = "unknown"; }
                    catch { gotoStr = "unknown"; }
                }
                actions.Add(new JsonObject
                {
                    ["id"] = id, ["surface"] = surf, ["enabled"] = status == "enabled", ["goto"] = gotoStr,
                    ["label"] = _byId[id][0].Label
                });
            }
            states.Add(new JsonObject { ["id"] = st, ["representative"] = $"{p.Scenario}@{p.K}", ["actions"] = actions });
        }
        return (new JsonObject { ["states"] = states }, amb);
    }
}

public static class Program
{
    static readonly JsonSerializerOptions Opts = new() { WriteIndented = true, IncludeFields = true,
        Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping };

    public static int Main(string[] a)
    {
        CultureInfo.DefaultThreadCurrentCulture = CultureInfo.InvariantCulture;
        switch (a.FirstOrDefault())
        {
            case "selftest": return SelfTest.Run();
            case "extract":
            {
                var dir = a[1];
                var files = Directory.GetFiles(Path.Combine(dir, "Views"), "*.axaml")
                    .ToDictionary(f => Path.GetFileNameWithoutExtension(f), f => File.ReadAllText(f));
                var strings = Extractor.ReadResx(Path.Combine(dir, "Resources", "Strings.resx"));
                var cb = Directory.GetFiles(Path.Combine(dir, "Views"), "*.axaml.cs")
                    .SelectMany(f => File.ReadAllLines(f).Select((l, i) => (f, l, i)))
                    .Where(t => Regex.IsMatch(t.l, @"\w+Command\.Execute\(|vm\.\w+\(|vm\.Selected\w+ ="))
                    .Select(t => $"{Path.GetFileName(t.f)}:{t.i + 1}: {t.l.Trim()}");
                var b = Extractor.Extract(files, strings, cb);
                File.WriteAllText(a[2], JsonSerializer.Serialize(b, Opts));
                Console.WriteLine($"elements {b.Elements.Count} (unknown {b.Elements.Count(e => e.Unknown != null)}) modals {b.Modals.Count} code-behind {b.CodeBehind.Count}");
                return 0;
            }
            case "certify":
            {
                var b = JsonSerializer.Deserialize<Bindings>(File.ReadAllText(a[1]), Opts)!;
                var sf = JsonNode.Parse(File.ReadAllText(a[2]))!.AsObject();
                // SwitchLanguage changes a static singleton; every fresh view model starts in the culture the run began with
                var initialCulture = CultureInfo.CurrentUICulture;
                // SwitchLanguage saves %LOCALAPPDATA%\MoviePad\settings.json (AppSettings.Save) — the user's real settings
                Certifier.NoExecuteCommands.Add("SwitchLanguage");
                return Certify(() =>
                {
                    MoviePad.Services.Localizer.Instance.SetCulture(initialCulture);
                    return new MoviePad.ViewModels.MainWindowViewModel();
                }, b, sf, a[3], a[4]);
            }
        }
        Console.Error.WriteLine("usage: harness selftest | extract <dir> <out> | certify <bindings> <scenarios> <certify-out> <mock-out>");
        return 2;
    }

    public static int Certify(Func<object> factory, Bindings b, JsonObject sf, string certifyOut, string mockOut)
    {
        var c = new Certifier(factory, b, sf);
        var (steps, points, trans, certified) = c.Run();
        // drop scenarios touching an ambiguous state until stable (definitions section 12, departure D2)
        var keep = certified.Where(kv => kv.Value).Select(kv => kv.Key).ToHashSet();
        var droppedAmb = new JsonObject();
        JsonObject mock, amb;
        var (_, p0, t0, _) = c.Run(keep);
        var amb0 = c.Mock(p0, t0).ambiguity;
        while (true)
        {
            var (_, p2, t2, _) = c.Run(keep);
            (mock, amb) = c.Mock(p2, t2);
            var bad = p2.Where(p => p.States.Any(s => amb.ContainsKey(s))).Select(p => p.Scenario).Distinct().ToList();
            if (bad.Count == 0) break;
            foreach (var s in bad) { keep.Remove(s); droppedAmb[s] = string.Join("; ", p2.Where(p => p.Scenario == s).SelectMany(p => p.States).Where(x => amb.ContainsKey(x)).Distinct().Select(x => $"{x}: {amb[x]}")); }
        }
        var env = new JsonObject
        {
            ["FfmpegLocator.Available"] = SafeStatic("MoviePad.Services.FfmpegLocator, MoviePad", "Available"),
            ["CurrentUICulture"] = CultureInfo.CurrentUICulture.Name,
        };
        var outObj = new JsonObject
        {
            ["environment"] = env,
            ["known_actions"] = new JsonArray(c.KnownIds.Select(x => (JsonNode)x).ToArray()),
            ["unresolved_elements"] = JsonNode.Parse(JsonSerializer.Serialize(c.UnresolvedElements, Opts)),
            ["steps"] = JsonNode.Parse(JsonSerializer.Serialize(steps, Opts)),
            ["certified"] = new JsonObject(certified.Select(kv => KeyValuePair.Create(kv.Key, (JsonNode?)kv.Value))),
            ["ambiguous_states_before_drops"] = amb0.DeepClone(),
            ["ambiguous_states"] = amb.DeepClone(),
            ["points"] = JsonNode.Parse(JsonSerializer.Serialize(points, Opts)),
            ["dropped_for_ambiguity"] = droppedAmb,
            ["kept"] = new JsonArray(keep.OrderBy(x => x).Select(x => (JsonNode)x).ToArray()),
        };
        File.WriteAllText(certifyOut, outObj.ToJsonString(Opts));
        File.WriteAllText(mockOut, mock.ToJsonString(Opts));
        Console.WriteLine($"scenarios {certified.Count} certified {certified.Count(kv => kv.Value)} kept {keep.Count} " +
                          $"states-in-mock {mock["states"]!.AsArray().Count} ambiguous {amb.Count}");
        foreach (var r in steps.Where(r => !r.Pass)) Console.WriteLine($"  FAIL {r.Scenario}#{r.Index} {r.Action}: {r.Reason}");
        foreach (var (s, why) in amb0) Console.WriteLine($"  AMBIGUOUS {s}: {why}");
        foreach (var (s, why) in droppedAmb) Console.WriteLine($"  DROP {s}: {why}");
        return 0;
    }

    static JsonNode? SafeStatic(string type, string prop)
    {
        try { return JsonValue.Create(Type.GetType(type)?.GetProperty(prop, BindingFlags.Public | BindingFlags.Static)?.GetValue(null)?.ToString()); }
        catch (Exception ex) { return "error: " + ex.Message; }
    }
}
