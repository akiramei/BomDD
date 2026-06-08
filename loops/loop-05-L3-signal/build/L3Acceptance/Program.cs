using System.Diagnostics;
using System.Globalization;

// ===== Loop5: execution L3(音声信号比較)受入ハーネス =====
// 目的: 座標系バグ(CHEAT-008級=音声を誤った時間位置から切り出す)を、ffmpeg実行+音声内容比較で捕捉。
// L2(尺/コーデック)では正/誤を区別できないことを同時に示す。
// 音源: 1秒ごとに周波数が変わるトーン(秒s = 300+100*s Hz)。SC4=trim[5,10]の正解音は 800,900,1000,1100,1200 Hz。

string ffdir = Path.Combine(
    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "MoviePad", "ffmpeg");
string ffmpeg = Path.Combine(ffdir, "ffmpeg.exe");
string ffprobe = Path.Combine(ffdir, "ffprobe.exe");
string work = Path.Combine(AppContext.BaseDirectory, "work");
Directory.CreateDirectory(work);
string src = Path.Combine(work, "src.mp4");
string Q(string p) => "\"" + p + "\"";

// --- 段階的トーン音源を生成(秒sで 300+100*s Hz) + testsrc 映像、H.264/AAC ---
if (!File.Exists(src))
{
    var segs = new List<string>();
    for (int i = 0; i < 10; i++)
    {
        int f = 300 + 100 * i;
        string seg = Path.Combine(work, $"seg{i}.wav");
        Run(ffmpeg, $"-nostdin -y -f lavfi -i sine=frequency={f}:duration=1:sample_rate=48000 {Q(seg)}", out _);
        segs.Add(seg);
    }
    string list = Path.Combine(work, "list.txt");
    File.WriteAllText(list, string.Join("\n", segs.Select(s => $"file '{s.Replace("\\", "/")}'")));
    string audio = Path.Combine(work, "audio.wav");
    Run(ffmpeg, $"-nostdin -y -f concat -safe 0 -i {Q(list)} -c copy {Q(audio)}", out _);
    Run(ffmpeg, $"-nostdin -y -f lavfi -i testsrc=duration=10:size=640x360:rate=30 -i {Q(audio)} " +
                $"-c:v libx264 -pix_fmt yuv420p -preset ultrafast -c:a aac -ar 48000 -shortest {Q(src)}", out _);
}

// --- SC4(trim[5,10], seekBase=5)の3変種。映像は全て source[5:10](入力0をシーク, trim 0:5) ---
string Filter(string audioPart) =>
    $"[0:v]trim=start=0:end=5,setpts=(PTS-STARTPTS)/1[v0];{audioPart}" +
    "[v0][a0]concat=n=1:v=1:a=1[cv][ca];[cv]null[vout];[ca]anull[aout]";
string Enc = "-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart";

var variants = new (string name, string inputs, string filter, string note)[]
{
    ("correct(K-BOM: 2入力・絶対時刻)",
        $"-ss 5 -i {Q(src)} -i {Q(src)}",
        Filter("[1:a]atrim=start=5:end=10,asetpts=PTS-STARTPTS,atempo=1[a0];"),
        "音声=未シーク入力1の絶対5:10=source[5:10]"),
    ("buggy(CHEAT-008: 未シーク入力に相対時刻)",
        $"-ss 5 -i {Q(src)} -i {Q(src)}",
        Filter("[1:a]atrim=start=0:end=5,asetpts=PTS-STARTPTS,atempo=1[a0];"),
        "音声=未シーク入力1の0:5=source[0:5] ← 誤った位置"),
    ("phaseA(Loop4共有: 単一シーク入力・相対)",
        $"-ss 5 -i {Q(src)}",
        Filter("[0:a]atrim=start=0:end=5,asetpts=PTS-STARTPTS,atempo=1[a0];"),
        "音声=シーク済入力0の0:5=source[5:10](内容は正・AACドリフトリスク)"),
};

int[] expected = { 800, 900, 1000, 1100, 1200 }; // source[5:10] の正解周波数

Console.WriteLine($"ffmpeg: {ffmpeg}");
Console.WriteLine($"SC4 正解音(source[5:10]): {string.Join(",", expected)} Hz\n");
Console.WriteLine("変種                                            | L2尺  | L3 毎秒周波数(Hz, 推定)        | 判定");
Console.WriteLine(new string('-', 108));

foreach (var v in variants)
{
    string outPath = Path.Combine(work, "out.mp4");
    string pcm = Path.Combine(work, "out.pcm");
    if (File.Exists(outPath)) File.Delete(outPath);
    if (File.Exists(pcm)) File.Delete(pcm);

    string cmdArgs = $"-nostdin -y -hide_banner {v.inputs} -filter_complex \"{v.filter}\" " +
                     $"-map \"[vout]\" -map \"[aout]\" {Enc} {Q(outPath)}";
    int ec = Run(ffmpeg, cmdArgs, out string err);
    if (ec != 0 || !File.Exists(outPath)) { Console.WriteLine($"{v.name,-46} | ffmpeg失敗 {Tail(err)}"); continue; }

    double dur = ProbeDuration(ffprobe, outPath);
    Run(ffmpeg, $"-nostdin -y -i {Q(outPath)} -ac 1 -ar 48000 -f s16le {Q(pcm)}", out _);
    int[] freqs = DominantFreqPerSecond(pcm, 48000);

    // 判定: 先頭秒の周波数が正解先頭(800)に近ければ内容OK、source[0:5]先頭(300)に近ければ誤位置
    string verdict;
    if (freqs.Length == 0) verdict = "不明";
    else if (Math.Abs(freqs[0] - expected[0]) <= 60) verdict = "内容OK(正しい区間)";
    else if (Math.Abs(freqs[0] - 300) <= 60) verdict = "★誤位置(source[0:5])= L3が捕捉";
    else verdict = $"不一致({freqs[0]}Hz)";

    Console.WriteLine($"{v.name,-46} | {dur:0.00}s | {string.Join(",", freqs),-28} | {verdict}");
}

Console.WriteLine(new string('-', 108));
Console.WriteLine("注: correct と buggy は L2(尺={同じ}/コーデック同じ)では区別不能。L3(音声内容)のみが buggy を捕捉する。");
return 0;

// ===== ヘルパ =====
static int Run(string exe, string args, out string stderr)
{
    var psi = new ProcessStartInfo(exe, args)
    { RedirectStandardError = true, RedirectStandardOutput = true, UseShellExecute = false };
    var p = Process.Start(psi)!;
    string e = p.StandardError.ReadToEnd();
    p.StandardOutput.ReadToEnd();
    p.WaitForExit();
    stderr = e;
    return p.ExitCode;
}

static double ProbeDuration(string ffprobe, string path)
{
    var psi = new ProcessStartInfo(ffprobe,
        $"-v error -show_entries format=duration -of default=nw=1:nk=1 \"{path}\"")
    { RedirectStandardOutput = true, UseShellExecute = false };
    var p = Process.Start(psi)!;
    string o = p.StandardOutput.ReadToEnd().Trim();
    p.WaitForExit();
    return double.TryParse(o, NumberStyles.Float, CultureInfo.InvariantCulture, out double d) ? d : 0;
}

// 1秒窓ごとに、ゼロ交差レートから単一トーンの支配的周波数を推定(freq ≈ 交差数/2)
static int[] DominantFreqPerSecond(string pcmPath, int sr)
{
    byte[] bytes = File.ReadAllBytes(pcmPath);
    int total = bytes.Length / 2;
    var samples = new short[total];
    Buffer.BlockCopy(bytes, 0, samples, 0, total * 2);
    var freqs = new List<int>();
    for (int w = 0; (w + 1) * sr <= total; w++)
    {
        int start = w * sr, crossings = 0;
        for (int i = start + 1; i < start + sr; i++)
            if ((samples[i - 1] < 0 && samples[i] >= 0) || (samples[i - 1] >= 0 && samples[i] < 0))
                crossings++;
        freqs.Add((int)Math.Round(crossings / 2.0 / 100.0) * 100); // 100Hz刻みに丸め
    }
    return freqs.ToArray();
}

static string Tail(string s)
{
    var l = s.Replace("\r", "").Split('\n', StringSplitOptions.RemoveEmptyEntries);
    return l.Length == 0 ? "" : l[^1];
}
