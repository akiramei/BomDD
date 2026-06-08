# ① 原版証拠の棚卸し — Export seek/audio 経路

リバースの入力。MoviePad `Services/FfmpegExporter.cs` の seek/audio 関連箇所(出典 file:line)。

| 証拠ID | 場所 | 内容 |
|---|---|---|
| E1 | FfmpegExporter.cs:40 | `SeekFromSeconds = 1.0`。前トリムがこの秒数以上なら映像入力をシークする閾値 |
| E2 | :72 | `seekBase = plan.SpanStart >= SeekFromSeconds ? plan.SpanStart : 0` |
| E3 | :130-132 | BuildFilterArgs: `seek`時 `-ss seekBase` を**1つ目の入力**前に。`seek && hasAudio`時、音声用に**2つ目の `-i`(シークなし)** |
| E4 | :181 | BuildFilterGraph: `aIn = (seekBase>0 && hasAudio) ? "1" : "0"`(音声の入力インデックス) |
| E5 | :192 | 映像: `trim=start={s-seekBase}:end={e-seekBase}`(seekBase 前詰め=相対) |
| E6 | :196 | 音声: `atrim=start={s}:end={e}`(**絶対時刻**、seekBaseを引かない) |
| E7 | :66-75(コメント) | 根拠: 映像はキーフレーム入力シークで先頭の無駄デコードを省く。**音声は別入力(シークなし)で絶対時刻=AACのシーク由来サンプルずれを避け、出力をビット完全一致に保つ** |
| E8 | tests/ExportPlanTests.cs:239-261 | テスト: `[0:v]trim=start=0:end=5` / `[1:a]atrim=start=5:end=10`(seek時)・非seek時は単一入力絶対 |

危険点(既知): **E5 と E6 の非対称(映像=相対・音声=絶対)** が CHEAT-008 の発生源。読み手がここを取り違えると音ズレ。
