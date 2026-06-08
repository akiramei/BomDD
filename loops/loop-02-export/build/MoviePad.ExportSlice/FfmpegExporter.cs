using System.Globalization;
using System.Text;
using MoviePad.Models;

namespace MoviePad.Services;

/// <summary>
/// ffmpeg 引数 / filter_complex を組み立てる純粋ロジック。
/// プロセス起動は行わない。
/// </summary>
public sealed class FfmpegExporter
{
    /// <summary>
    /// 1 回の書き出し要求。
    /// </summary>
    public sealed record Request(
        ClipInfo Clip,
        DocumentState Doc,
        int OutWidth,
        int OutHeight,
        ExportFormat Format,
        string OutputPath,
        double OutFps,
        bool FastCopy = false,
        double? CopyStartOverride = null);

    // 数値は invariant・固定小数で出力する(ロケール非依存)。
    private static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    private static string F(double v) => v.ToString("0.######", Inv);

    /// <summary>
    /// filter_complex グラフ文字列を組み立てる。
    /// 非除外かつ [TrimStart,TrimEnd] と交差する区間ごとに、
    /// 映像トリム→区間速度(setpts)、音声(hasAudio時)トリム→区間速度(atempo/asetrate)、
    /// 区間音量(非full時 volume)を適用し、全区間を順に連結する。
    /// plan.NeedsScale のときだけスケール、plan.NeedsRerate のときだけ fps を適用。
    /// 最終映像出力パッドは必ず [vout]、最終音声出力パッドは必ず [aout]。
    /// 出力区間数を segCount に返し、0 区間なら "" を返す。
    /// </summary>
    public static string BuildFilterGraph(
        Request req,
        ExportPlan plan,
        bool hasAudio,
        double seekBase,
        out int segCount)
    {
        var doc = req.Doc;
        var sb = new StringBuilder();

        // 入力本数構成(様式選択):
        //   seekBase > 0 のとき、映像入力は -ss で前トリック済みと見なし
        //   入力インデックス 0 は「シーク済み映像」、音声は別入力(インデックス 1)から
        //   フルでデコードする、という構成にする。
        //   seekBase <= 0 のときは映像・音声とも単一入力 0 を共有する。
        //   ここではグラフ内の入力ラベルだけを決める。
        bool useSeek = seekBase > 0.0;
        string vInLabel = "0:v";
        string aInLabel = useSeek ? "1:a" : "0:a";

        var segLabelsV = new List<string>();
        var segLabelsA = new List<string>();
        int idx = 0;

        foreach (var r in doc.Regions)
        {
            if (r.Excluded)
                continue;

            double s = Math.Max(r.Start, doc.TrimStart);
            double e = Math.Min(r.End, doc.TrimEnd);
            // [TrimStart,TrimEnd] と交差しない / 縮退区間はスキップ。
            if (e - s <= 1e-4)
                continue;

            // seekBase ぶん前方に詰めたトリム座標。
            double ts = s - seekBase;
            double te = e - seekBase;
            if (ts < 0) ts = 0;

            double speed = r.Speed;
            bool identitySpeed = r.IsNormalSpeed;

            // ----- 映像区間 -----
            string vl = $"v{idx}";
            sb.Append('[').Append(vInLabel).Append(']');
            sb.Append("trim=start=").Append(F(ts)).Append(":end=").Append(F(te)).Append(',');
            sb.Append("setpts=PTS-STARTPTS");
            if (!identitySpeed)
            {
                // 速度 = 再生倍率。PTS を 1/speed 倍にすると speed 倍速になる。
                sb.Append(',').Append("setpts=").Append(F(1.0 / speed)).Append("*PTS");
            }
            sb.Append('[').Append(vl).Append("];");
            segLabelsV.Add(vl);

            // ----- 音声区間 -----
            if (hasAudio)
            {
                string al = $"a{idx}";
                sb.Append('[').Append(aInLabel).Append(']');
                // CHEAT-008: 音声入力はシークしない別入力のため、atrim は絶対時刻 s/e を使う
                //（seekBase オフセットを掛けてはいけない。原版準拠 / REQ-EXP-4）。
                sb.Append("atrim=start=").Append(F(s)).Append(":end=").Append(F(e)).Append(',');
                sb.Append("asetpts=PTS-STARTPTS");

                if (!identitySpeed)
                {
                    if (r.PreservePitch)
                    {
                        // ピッチ維持=テンポのみ変更。atempo は 0.5〜2.0 の制約があるため連鎖する。
                        AppendAtempoChain(sb, speed);
                    }
                    else
                    {
                        // ピッチ非維持=サンプルレート変更でリサンプル。
                        int newRate = (int)Math.Round(req.Clip.SampleRate * speed);
                        sb.Append(',').Append("asetrate=").Append(newRate.ToString(Inv));
                        sb.Append(',').Append("aresample=").Append(req.Clip.SampleRate.ToString(Inv));
                    }
                }

                if (!r.IsFullVolume)
                {
                    sb.Append(',').Append("volume=").Append(F(r.Volume));
                }

                sb.Append('[').Append(al).Append("];");
                segLabelsA.Add(al);
            }

            idx++;
        }

        segCount = idx;
        if (segCount == 0)
        {
            sb.Clear();
            return "";
        }

        // ----- 連結 -----
        // 映像連結 → スケール → fps → [vout]
        string vConcat;
        if (segCount == 1)
        {
            vConcat = segLabelsV[0];
        }
        else
        {
            foreach (var l in segLabelsV)
                sb.Append('[').Append(l).Append(']');
            sb.Append("concat=n=").Append(segCount.ToString(Inv)).Append(":v=1:a=0[vcat];");
            vConcat = "vcat";
        }

        string vChainIn = vConcat;
        // スケール / fps を後段に積む。中間ラベルを更新しながら最後に [vout] へ落とす。
        bool needScale = plan.NeedsScale;
        bool needRerate = plan.NeedsRerate;

        if (needScale || needRerate)
        {
            sb.Append('[').Append(vChainIn).Append(']');
            bool first = true;
            if (needScale)
            {
                // 補間フラグ: 既定の縮小/拡大両対応として bicubic を明示。
                sb.Append("scale=").Append(req.OutWidth.ToString(Inv)).Append(':')
                  .Append(req.OutHeight.ToString(Inv)).Append(":flags=bicubic");
                first = false;
            }
            if (needRerate)
            {
                if (!first) sb.Append(',');
                sb.Append("fps=").Append(F(req.OutFps));
            }
            sb.Append("[vout];");
        }
        else
        {
            // 恒等変換: null フィルタを 1 つ置いて [vout] を必ず作る。
            sb.Append('[').Append(vChainIn).Append(']').Append("null[vout];");
        }

        // 音声連結 → [aout]
        if (hasAudio)
        {
            if (segCount == 1)
            {
                sb.Append('[').Append(segLabelsA[0]).Append(']').Append("anull[aout];");
            }
            else
            {
                foreach (var l in segLabelsA)
                    sb.Append('[').Append(l).Append(']');
                sb.Append("concat=n=").Append(segCount.ToString(Inv)).Append(":v=0:a=1[aout];");
            }
        }

        // 末尾の余分な ';' を除去。
        if (sb.Length > 0 && sb[^1] == ';')
            sb.Length--;

        return sb.ToString();
    }

    /// <summary>
    /// atempo は係数 0.5〜2.0 の範囲しか取れないため、範囲外は連鎖で表現する。
    /// </summary>
    private static void AppendAtempoChain(StringBuilder sb, double speed)
    {
        double remaining = speed;
        // speed > 2 のとき 2.0 を繰り返す。speed < 0.5 のとき 0.5 を繰り返す。
        while (remaining > 2.0 + 1e-9)
        {
            sb.Append(',').Append("atempo=2.0");
            remaining /= 2.0;
        }
        while (remaining < 0.5 - 1e-9)
        {
            sb.Append(',').Append("atempo=0.5");
            remaining /= 0.5;
        }
        sb.Append(',').Append("atempo=").Append(F(remaining));
    }

    /// <summary>
    /// BuildFilterGraph の出力を -filter_complex に入れ、[vout]/[aout] を -map する
    /// ffmpeg 引数を組む。前トリム高速化のため必要に応じ映像入力を -ss でシークする。
    /// 形式別エンコーダ引数も付ける。
    /// </summary>
    public static string BuildFilterArgs(Request req, double seekBase, string filter, bool hasAudio)
    {
        var args = new List<string>();
        bool useSeek = seekBase > 0.0;

        // 入力: シーク使用時は映像をシーク済みで開き、音声をフルで別途開く。
        if (useSeek)
        {
            args.Add("-ss");
            args.Add(F(seekBase));
            args.Add("-i");
            args.Add(Q(req.Clip.Path));
            // 音声用フル入力(seekBase なし)。
            args.Add("-i");
            args.Add(Q(req.Clip.Path));
        }
        else
        {
            args.Add("-i");
            args.Add(Q(req.Clip.Path));
        }

        args.Add("-filter_complex");
        args.Add(Q(filter));

        args.Add("-map");
        args.Add("[vout]");
        if (hasAudio)
        {
            args.Add("-map");
            args.Add("[aout]");
        }

        // ----- 形式別エンコーダ引数 -----
        AppendEncoderArgs(args, req.Format, hasAudio);

        args.Add(Q(req.OutputPath));
        return string.Join(' ', args);
    }

    /// <summary>
    /// stream copy(-c copy)の引数を組む。
    /// 開始は CopyStartOverride が妥当(0〜SpanStart)ならそれ、無ければ SpanStart。
    /// 長さは SpanEnd − 開始。
    /// </summary>
    public static string BuildCopyArgs(Request req, ExportPlan plan, bool hasAudio)
    {
        double start = plan.SpanStart;
        if (req.CopyStartOverride is double ov && ov >= 0.0 && ov <= plan.SpanStart)
            start = ov;

        double duration = plan.SpanEnd - start;
        if (duration < 0) duration = 0;

        var args = new List<string>();
        // -ss を入力前に置いて高速シーク。
        args.Add("-ss");
        args.Add(F(start));
        args.Add("-i");
        args.Add(Q(req.Clip.Path));
        args.Add("-t");
        args.Add(F(duration));
        args.Add("-c");
        args.Add("copy");

        // 音声が無いクリップでは映像のみマップ。
        args.Add("-map");
        args.Add("0:v");
        if (hasAudio)
        {
            args.Add("-map");
            args.Add("0:a");
        }

        args.Add(Q(req.OutputPath));
        return string.Join(' ', args);
    }

    /// <summary>
    /// 形式別のエンコーダ/品質引数を付ける。
    /// </summary>
    private static void AppendEncoderArgs(List<string> args, ExportFormat fmt, bool hasAudio)
    {
        switch (fmt)
        {
            case ExportFormat.Mp4:
                args.Add("-c:v");
                args.Add("libx264");
                args.Add("-crf");
                args.Add("18");
                args.Add("-pix_fmt");
                args.Add("yuv420p");
                if (hasAudio)
                {
                    args.Add("-c:a");
                    args.Add("aac");
                    args.Add("-b:a");
                    args.Add("192k");
                }
                break;

            case ExportFormat.Lossless:
                args.Add("-c:v");
                args.Add("libx264");
                args.Add("-qp");
                args.Add("0");
                if (hasAudio)
                {
                    args.Add("-c:a");
                    args.Add("flac");
                }
                break;

            case ExportFormat.ProRes:
                args.Add("-c:v");
                args.Add("prores_ks");
                args.Add("-profile:v");
                args.Add("3");
                if (hasAudio)
                {
                    args.Add("-c:a");
                    args.Add("pcm_s16le");
                }
                break;
        }
    }

    /// <summary>
    /// 空白を含むトークンを引用する(様式: 必要なときだけダブルクォート)。
    /// </summary>
    private static string Q(string s)
    {
        if (s.Length == 0)
            return "\"\"";
        bool needs = false;
        foreach (var ch in s)
        {
            if (char.IsWhiteSpace(ch)) { needs = true; break; }
        }
        return needs ? "\"" + s + "\"" : s;
    }
}
