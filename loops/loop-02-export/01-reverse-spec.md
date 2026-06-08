# ① リバース復元仕様 — 書き出しスライス(出典: FfmpegExporter.cs / ExportFormat.cs / ClipInfo.cs / ExportPlanTests.cs)

## 要求(REQ)
- REQ-EXP-1: 区間速度(映像 setpts / 音声 atempo・asetrate)・トリム・除外・出力解像度・音量を**単一 filter_complex** で適用し書き出す。出典 FfmpegExporter.cs:11-13
- REQ-EXP-2: 再エンコード不要(無変換・単一連続スパン・mp4互換)なら **stream copy** で高速・無劣化。出典 :57-63, ExportPlan:287
- REQ-EXP-3: 恒等変換(解像度・レート無変更)では scale/fps を**省略**し世代劣化を避ける。出典 :220-225
- REQ-EXP-4: 前トリムが1秒以上なら映像入力を `-ss` で入力シークし無駄デコードを省く。音声は別入力(シークなし)で絶対時刻=AACずれ回避。出典 :40,66-75,119-139

## Unit A: ExportPlan.Analyze の規則(純粋判定)
- スパン: トリム×除外後に残る区間を時刻順に畳む。除外が挟まり不連続化するとスパン2以上。`SingleSpan = spans==1`。SpanStart/End は単一スパンの両端。eps=1e-4。出典 :297-316
- `NeedsScale = OutW!=clip.W || OutH!=clip.H`。出典 :327
- `fpsChange = |OutFps - clip.Fps| > 0.05`。`anySpeedChange = ∃ 非除外区間で !IsNormalSpeed`。出典 :318-320,328
- `NeedsRerate = anySpeedChange || fpsChange || clip.IsVariableFrameRate`。出典 :329
- `anyVolumeChange = ∃ 非除外区間で !IsFullVolume`。出典 :323-325
- `mp4 = Format==Mp4`。**コピー白名簿**: 映像 ∈ {H.264,H.265}、音声 ∈ {AAC,MP3,AC-3}。出典 :336,345-346
- `VideoCopyEligible = mp4 && !NeedsScale && !anySpeedChange && !fpsChange && IsMp4Video(vcodec)`。**VFRはコピー阻害しない**。出典 :337,334
- `AudioCopyEligible = !HasAudio || (mp4 && !anySpeedChange && !anyVolumeChange && IsMp4Audio(acodec))`。出典 :338
- `CanStreamCopy = VideoCopyEligible && AudioCopyEligible && SingleSpan`。出典 :288

## Unit B: filter_complex 文法(外部ツール — 実装の正確様式)
非除外区間ごと(k=0..)に、出典 :183-217:
- 映像: `[0:v]trim=start={s-seekBase}:end={e-seekBase},setpts=(PTS-STARTPTS)/{speed}[v{k}];`
- 音声: `[{aIn}:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,{AudioTempo}` + (非full)`,volume={vol}` + `[a{k}];`（aIn = seekBase>0&&hasAudio ? "1":"0"）
- 連結: `[v0][a0]...concat=n={k}:v=1:a=1[cv][ca];`（音声無→`a=0[cv]`)
- 末尾: `[cv]{scale=W:H:flags=lanczos と fps=F を必要時カンマ連結、無ければ null}[vout]` + 音声`;[ca]anull[aout]`
- AudioTempo(出典 :231-245): 非ピッチ維持=`asetrate={SR*speed},aresample={SR}`。維持=atempoを[0.5,2.0]段に分解連結(>2は`atempo=2.0,`、<0.5は`atempo=0.5,`を繰返し最後に`atempo={残}`)。
- 数値書式: `0.######`/InvariantCulture。出典 :33
- BuildFilterArgs(出典 :125-139): `-y -hide_banner -nostats -progress pipe:1 ` + (seek)`-ss {seekBase} ` + `-i "path" ` + (seek&&audio)`-i "path" ` + `-filter_complex "..." -map "[vout]" ` + (audio)`-map "[aout]" ` + EncoderArgs + ` "out"`。
- BuildCopyArgs(出典 :157-169): `... -ss {start} -i "path" -t {dur} -map 0:v:0 ` + (audio)`-map 0:a:0 ` + `-c copy -avoid_negative_ts make_zero -movflags +faststart "out"`。start=CopyStart(override妥当なら採用)、dur=SpanEnd-start。

## 復元の所見
Unit B の「正確様式」(ラベル名 v{k}/cv/vout、恒等時 null 透過、lanczos、seekBase 2入力)は **REQ から導けない**。
ffmpeg ドメイン知識 + 原版の任意選択。→ Loop2 の中心測定点。
