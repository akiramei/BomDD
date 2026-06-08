using System.Collections.Immutable;
using System.Diagnostics;
using System.Globalization;
using System.Text.Json;
using MoviePad.Models;
using MoviePad.Services;

// ===== Loop2.5: execution 受入ハーネス =====
// 製造ライブラリ(MoviePad.ExportSlice)が生成したコマンドで実際に ffmpeg を回し、
// 出力を ffprobe して要求基準(尺・解像度・コーデック)と照合する。
// 目的: (1) 様式差(ラベル名/引用)の誤検出が消えるか (2) 沈黙乖離(Lossless別コーデック)を捕えるか。

string ffdir = LocateFfmpegDir();
string ffmpeg = Path.Combine(ffdir, "ffmpeg.exe");
string ffprobe = Path.Combine(ffdir, "ffprobe.exe");
string work = Path.Combine(AppContext.BaseDirectory, "work");
Directory.CreateDirectory(work);
string src = Path.Combine(work, "src.mp4");

Console.WriteLine($"ffmpeg: {ffmpeg}");

// --- ソース生成(1920x1080@30, H.264 + AAC 48k, 6s) ---
if (!File.Exists(src))
{
    int gen = RunFfmpeg(ffmpeg,
        $"-y -nostdin -f lavfi -i testsrc=duration=6:size=1920x1080:rate=30 " +
        $"-f lavfi -i sine=frequency=440:sample_rate=48000:duration=6 " +
        $"-c:v libx264 -pix_fmt yuv420p -preset ultrafast -c:a aac -shortest \"{src}\"", out _);
    if (gen != 0) { Console.WriteLine("ソース生成失敗"); return 1; }
}

var clip = new ClipInfo(src, "src.mp4", 6.0, 1920, 1080, 30, "H.264", "AAC", 48000, false);
DocumentState Full() => new(0, 6, ImmutableList.Create(new RegionData(1, 0, 6, 1.0, true)));

// シナリオ: (名前, Request, 期待 width, height, vcodec, acodec, 期待尺秒, この乖離は既知の予測FAILか)
var scenarios = new (string name, FfmpegExporter.Request req, int w, int h, string vc, string ac, double dur, string note)[]
{
    ("S1 恒等コピー(FastCopy)",
        new(clip, Full(), 1920, 1080, ExportFormat.Mp4, Path.Combine(work, "s1.mp4"), 30, FastCopy: true),
        1920, 1080, "h264", "aac", 6.0, "コピー経路"),
    ("S2 スケール 1280x720(再エンコード)",
        new(clip, Full(), 1280, 720, ExportFormat.Mp4, Path.Combine(work, "s2.mp4"), 30),
        1280, 720, "h264", "aac", 6.0, "scaleフラグ差(bicubic/lanczos)は尺/寸法に出ない"),
    ("S3 速度2x(再エンコード)",
        new(clip, new(0, 6, ImmutableList.Create(new RegionData(1, 0, 6, 2.0, true))),
            1920, 1080, ExportFormat.Mp4, Path.Combine(work, "s3.mp4"), 30),
        1920, 1080, "h264", "aac", 3.0, "尺が半分=速度変換が実際に効くかの機能検査"),
    ("S4 前トリム+シーク [3,6]",
        new(clip, new(3, 6, ImmutableList.Create(new RegionData(1, 3, 6, 1.0, true))),
            1920, 1080, ExportFormat.Mp4, Path.Combine(work, "s4.mp4"), 30),
        1920, 1080, "h264", "aac", 3.0, "seek経路の尺。B08(音声位置)は尺では出ず信号比較が要る"),
    ("S5 Lossless(要求 FFV1/PCM)",
        new(clip, Full(), 1920, 1080, ExportFormat.Lossless, Path.Combine(work, "s5.mkv"), 30),
        1920, 1080, "ffv1", "pcm_s16le", 6.0, "要求はffv1/pcm。製造物はlibx264/flacの想定→execution が捕捉するか"),
};

int pass = 0, fail = 0;
Console.WriteLine();
Console.WriteLine("シナリオ                                  | 結果 | 実測(寸法/vcodec/acodec/尺)");
Console.WriteLine(new string('-', 110));

foreach (var s in scenarios)
{
    if (File.Exists(s.req.OutputPath)) File.Delete(s.req.OutputPath);
    string cmdArgs = BuildArgs(s.req);
    // execution 環境フラグのみ前置(変換ロジックは製造物のまま): 非対話・上書き許可
    int ec = RunFfmpeg(ffmpeg, "-nostdin -y " + cmdArgs, out string ffErr);

    if (ec != 0 || !File.Exists(s.req.OutputPath))
    {
        Console.WriteLine($"{s.name,-40} | FAIL | ffmpeg 異常終了({ec}) {Tail(ffErr)}");
        fail++;
        continue;
    }

    var (pw, ph, pvc, pac, pdur) = Probe(ffprobe, s.req.OutputPath);
    bool ok = pw == s.w && ph == s.h && pvc == s.vc && (pac == s.ac) && Math.Abs(pdur - s.dur) <= 0.4;
    Console.WriteLine($"{s.name,-40} | {(ok ? "PASS" : "FAIL")} | {pw}x{ph}/{pvc}/{pac}/{pdur:0.00}s  期待 {s.w}x{s.h}/{s.vc}/{s.ac}/{s.dur:0.0}s");
    if (ok) pass++; else fail++;
}

Console.WriteLine(new string('-', 110));
Console.WriteLine($"合計: PASS {pass} / FAIL {fail}");
return 0;

// === ヘルパ ===
string BuildArgs(FfmpegExporter.Request req)
{
    var plan = ExportPlan.Analyze(req);
    bool hasAudio = req.Clip.HasAudio;
    if (req.FastCopy && plan.CanStreamCopy)
        return FfmpegExporter.BuildCopyArgs(req, plan, hasAudio);
    // 統合グルー(ExportAsync 相当=スライス外): 前トリム1秒以上なら入力シーク
    double seekBase = plan.SpanStart >= 1.0 ? plan.SpanStart : 0;
    string filter = FfmpegExporter.BuildFilterGraph(req, plan, hasAudio, seekBase, out _);
    return FfmpegExporter.BuildFilterArgs(req, seekBase, filter, hasAudio);
}

static string LocateFfmpegDir()
{
    string la = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
    string c = Path.Combine(la, "MoviePad", "ffmpeg");
    if (File.Exists(Path.Combine(c, "ffmpeg.exe"))) return c;
    return c;
}

static int RunFfmpeg(string exe, string args, out string stderr)
{
    var psi = new ProcessStartInfo(exe, args)
    { RedirectStandardError = true, RedirectStandardOutput = true, UseShellExecute = false };
    var p = Process.Start(psi)!;
    string err = p.StandardError.ReadToEnd();
    p.StandardOutput.ReadToEnd();
    p.WaitForExit();
    stderr = err;
    return p.ExitCode;
}

static (int w, int h, string vc, string ac, double dur) Probe(string ffprobe, string path)
{
    var psi = new ProcessStartInfo(ffprobe,
        $"-v error -print_format json -show_format -show_streams \"{path}\"")
    { RedirectStandardOutput = true, UseShellExecute = false };
    var p = Process.Start(psi)!;
    string json = p.StandardOutput.ReadToEnd();
    p.WaitForExit();
    using var doc = JsonDocument.Parse(json);
    int w = 0, h = 0; string vc = "-", ac = "-"; double dur = 0;
    foreach (var st in doc.RootElement.GetProperty("streams").EnumerateArray())
    {
        string ct = st.GetProperty("codec_type").GetString() ?? "";
        if (ct == "video")
        {
            vc = st.GetProperty("codec_name").GetString() ?? "-";
            w = st.GetProperty("width").GetInt32();
            h = st.GetProperty("height").GetInt32();
        }
        else if (ct == "audio")
            ac = st.GetProperty("codec_name").GetString() ?? "-";
    }
    if (doc.RootElement.TryGetProperty("format", out var fmt) &&
        fmt.TryGetProperty("duration", out var d) &&
        double.TryParse(d.GetString(), NumberStyles.Float, CultureInfo.InvariantCulture, out double ds))
        dur = ds;
    return (w, h, vc, ac, dur);
}

static string Tail(string s)
{
    var lines = s.Replace("\r", "").Split('\n', StringSplitOptions.RemoveEmptyEntries);
    return lines.Length == 0 ? "" : lines[^1];
}
