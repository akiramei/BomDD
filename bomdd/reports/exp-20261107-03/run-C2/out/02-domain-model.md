# 出力フレームレート — ドメインモデル

## 1. 概念

```
Clip(開いた動画, 読み取り専用)
  ├─ sourceFps : 実数 > 0       … ffprobe の avg_frame_rate(無ければ r_frame_rate、どちらも無ければ 30)
  ├─ isVariableFrameRate : 真偽  … avg と r が max(0.1, 0.5%) を超えて食い違うとき真
  ├─ videoCodec / audioCodec / hasAudio / width / height / duration
  │
Document(編集内容, 元に戻す/やり直すの対象)
  ├─ trimStart / trimEnd
  └─ regions[] : { start, end, speed, volume, preservePitch, excluded }
        └─ 位置はすべて sourceFps のフレームに吸着

OutputSettings(書き出し設定, 元に戻す/やり直すの対象外・保存されない)
  ├─ outputFps : 実数 > 0       … 本書の主題
  ├─ outW / outH / keepAspect
  ├─ exportFormat : MP4 | 中間ファイル(FFV1/PCM) | ProRes
  └─ fastCopy : 真偽            … 「高速・無劣化（コピー）」

SessionStatus
  └─ edited : 真偽              … タイトルバー「未保存の変更」/「保存済み」
```

- `Document` と `OutputSettings` は別物。履歴(最大 50 段)は `Document` だけを積む。
- `outputFps` を参照するのは **書き出し**(と、その可否判定・ダイアログの表示)だけ。
  画面上の時間(タイムコード・コマ送り・吸着)はすべて `sourceFps`。

## 2. outputFps の状態と遷移

値の取りうる範囲(原製品): `sourceFps`(開いた直後か「ソース」押下)、24、30、60、120。

| 契機 | outputFps | edited | 履歴 | fastCopy |
|---|---|---|---|---|
| 動画を開く | ← sourceFps | ← 偽 | 空にする | ← 偽 |
| 「ソース」を押す | ← sourceFps | ← 真 | 変化なし | 変化なし |
| 「24/30/60/120」を押す | ← その値 | ← 真(値が同じでも) | 変化なし | 変化なし |
| 元に戻す / やり直す | 変化なし | 変化なし | Document を 1 段戻す/進める | 変化なし |
| 書き出し成功 | 変化なし | ← 偽 | 変化なし | 変化なし |
| 書き出し失敗・中止 | 変化なし | 変化なし | 変化なし | 変化なし |

(起動直後、動画を開く前の内部サンプルでも outputFps = サンプルの 30。サンプルは書き出せない。)

## 3. 派生する値(画面に出るもの)

| 派生値 | 定義 | 出る場所 |
|---|---|---|
| outputFpsText | outputFps を小数 2 桁まで・末尾の 0 と小数点を除いた文字列(30 → "30"、29.97 → "29.97"、23.976 → "23.98") | 書き出しダイアログ「フレームレート」= outputFpsText + " fps" |
| sourcePresetActive | \|outputFps − sourceFps\| < 0.05 | 「ソース」ボタンの点灯 |
| numberPresetActive(n) | outputFpsText == "n"(文字列一致) | 「24/30/60/120」の点灯 |
| upsampling | outputFps > sourceFps + 0.05 | 注記「ソースより高いfpsは…」 |
| sourceFpsText | sourceFps の同じ整形 + " fps" | 「ソース」のツールチップ、クリップ情報「フレームレート」 |
| fpsChanged | \|outputFps − sourceFps\| > 0.05 | (コピー可否・CFR 化の判定) |

注: `sourcePresetActive` は「< 0.05」、`fpsChanged` は「> 0.05」。差がちょうど 0.05 のときはどちらも偽(固定のプリセット値では起こりにくい)。

## 4. 書き出しとの関係

```
canStreamCopy = format == MP4
              ∧ outW,outH == ソースの幅・高さ
              ∧ 区間速度の変更なし ∧ ¬fpsChanged ∧ videoCodec ∈ {H.264, H.265}
              ∧ (音声なし ∨ (音量変更なし ∧ audioCodec ∈ {AAC, MP3, AC-3}))
              ∧ トリム×除外後の残りが 1 つの連続区間
「高速・無劣化（コピー）」の表示 = canStreamCopy
実際にコピーで書き出す       = fastCopy ∧ canStreamCopy

needsRerate = 区間速度の変更あり ∨ fpsChanged ∨ isVariableFrameRate
```

- 再エンコード時、`needsRerate` なら出力を `outputFps` の CFR へ揃える(ffmpeg の fps フィルタ)。
  そうでなければフレームの再サンプルをしない。
- ソースが CFR のときは「意図クロック」(`ExportClock`)が働く:
  - ソース・出力のレートを有理数で認識(q = 1 または 1001 で厳密に一致すれば p/q、例 30 → 30/1、
    29.97002997… → 30000/1001)。
  - 出力フレーム数 N = round_half_up(速度適用後の総出力時間 × outputFps)。
  - 各出力フレーム i は、出力時刻 i / outputFps に表示されているソースのフレーム(sample-and-hold)を取る。
    よって outputFps > sourceFps はフレームの複製、< は間引きになる。
  - 出力ファイルに公称フレームレート `-r p/q` を付け、MP4 は動画トラックのタイムスケールを p にする。
- コピーで書き出すときは outputFps は使われない(元のタイムスタンプのまま。VFR は VFR のまま)。

## 5. 不変条件(原製品で成り立つこと)

- I1 動画を開いた直後は sourcePresetActive が真(差 0)。
- I2 outputFps を変える操作は Document と履歴に触れない。Document を変える操作は outputFps に触れない。
- I3 画面上の時間表示とフレーム移動は outputFps に依存しない。
- I4 fpsChanged が真のあいだ、コピーの選択肢は表示されない。
