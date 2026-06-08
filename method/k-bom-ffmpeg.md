# K-BOM: ffmpeg-command-grammar-pack v1

知識部品(Knowledge-BOM)。要求BOMとは別に、製造装置が参照する**外部ツール(ffmpeg)の文法・慣用の管理された知識**。
これが無いと装置は自前の暗黙知で埋め、工場間でばらつく(Loop2 で実証)。K-BOM はその暗黙知を**管理対象**にする。

供給元: ffmpeg filter documentation（外部仕様）。バージョン: filter graph 構文 / atempo[0.5,2.0] 制約 / setpts・asetrate。

## 文法規約(製造装置はこれに厳密に従う)
**ラベル方式**: 非除外かつ交差する区間を i=0,1,... と採番。区間映像ラベル `v{i}`、区間音声ラベル `a{i}`。
連結後の映像 `[cv]`、音声 `[ca]`。最終映像 `[vout]`、最終音声 `[aout]`。**区間が1つでも concat=n=1 を使い [cv]/[ca] を作る**(分岐させない)。

**区間映像**: `[0:v]trim=start={F(s-seekBase)}:end={F(e-seekBase)},setpts=(PTS-STARTPTS)/{F(speed)}[v{i}];`
（映像入力は seekBase 前詰め。setpts は STARTPTS を引いてから speed で割る一体形）。

**区間音声**(hasAudio): `[{ain}:a]atrim=start={F(s)}:end={F(e)},asetpts=PTS-STARTPTS,{tempo}{vol}[a{i}];`
- **ain = (seekBase>0 && hasAudio) ? "1" : "0"**。**音声は絶対時刻 s,e を使う**（seekBaseを引かない=別入力でシークしないため。座標系規約 / CHEAT-008 対策）。
- tempo: ピッチ維持 = `atempo` を [0.5,2.0] 段に分解連結(>2は`atempo=2.0,`繰返し、<0.5は`atempo=0.5,`繰返し、最後 `atempo={F(残)}`)。非維持 = `asetrate={SR*speed},aresample={SR}`。
- vol: 非full(≠1.0)のとき `,volume={F(vol)}`、full は省略。

**連結**: `{各[v{i}](hasAudio時 [a{i}])を順に}` の後に `concat=n={k}:v=1:a=1[cv][ca];`(音声有) / `concat=n={k}:v=1:a=0[cv];`(無)。

**末尾**: 映像 `[cv]{tail}[vout]`。tail は NeedsScale 時 `scale={W}:{H}:flags=lanczos`、NeedsRerate 時 `fps={F(OutFps)}` を**この順でカンマ連結**、どちらも無ければ `null`。音声有なら続けて `;[ca]anull[aout]`。

**数値書式 F**: InvariantCulture、`"0.######"`(指数表記なし、末尾0除去）。

## 引数規約(BuildFilterArgs 相当)
`-y -hide_banner -nostats -progress pipe:1 ` + (seekBase>0)`-ss {F(seekBase)} ` + `-i "{path}" ` + (seekBase>0 && hasAudio)`-i "{path}" `
+ `-filter_complex "{filter}" -map "[vout]" ` + (hasAudio)`-map "[aout]" ` + EncoderArgs + ` "{outPath}"`。

**EncoderArgs**(形式別):
- Mp4: `-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p ` + (audio)`-c:a aac -b:a 192k ` + `-movflags +faststart`
- Lossless: `-c:v ffv1 -level 3 ` + (audio)`-c:a pcm_s16le`
- ProRes: `-c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le ` + (audio)`-c:a pcm_s16le`

**クォート**: 入力パス・filter・出力パスは常にダブルクォートで囲む。
