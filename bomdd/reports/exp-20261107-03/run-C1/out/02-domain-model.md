# 02 ドメインモデル — 出力フレームレート

## 概念と属性

```
Clip(ソース動画, 開いた時点で固定)
  sourceFps        : 実数 > 0      ffprobe avg_frame_rate → r_frame_rate → 30
  isVariableFrameRate : bool       avg と r の乖離で判定
  width, height, duration, videoCodec, audioCodec, sampleRate, path

OutputSettings(書き出し設定, 1 つの Clip に 1 つ。文書状態の外)
  outFps           : 実数 > 0      開いた時点 = Clip.sourceFps
  outWidth, outHeight, keepAspect
  ─ 派生 ─
  outFpsText       = outFps を小数 2 桁まで・末尾 0 を削った文字列("30", "23.98")
  isSourceFps      = |outFps − sourceFps| < 0.05
  isUpsampling     = outFps > sourceFps + 0.05
  fpsChanged       = |outFps − sourceFps| > 0.05     (書き出し計画の側の判定)

DocumentState(編集文書, 取り消しの対象)
  trimStart, trimEnd, regions[ {id, start, end, speed, preservePitch, volume, excluded} ]
  ※ fps を持たない。ただし編集操作は sourceFps のグリッドへスナップする

SessionFlags(画面の状態)
  edited           : bool          Saved / Unsaved changes の表示
  fastExport       : bool          高速コピーのチェック(保持される)
  showExport       : bool          書き出しダイアログ
  history          : DocumentState のスタック(最大 50)

ExportPlan(書き出し計画, 書き出し要求から都度導出する純粋値)
  needsRerate      = 速度変更あり ∨ fpsChanged ∨ isVariableFrameRate
  videoCopyEligible= MP4 形式 ∧ 解像度無変更 ∧ 速度無変更 ∧ ¬fpsChanged ∧ 映像が H.264/H.265
  canStreamCopy    = videoCopyEligible ∧ audioCopyEligible ∧ 単一連続区間

ExportClock(CFR ソースの厳密クロック, 書き出し時)
  srcRate, outRate : 有理数(q∈{1,1001} で一致すれば p/q、そうでなければ double の二進厳密値)
  VFR ソースでは作らない(従来経路: concat 後に fps=outFps)
```

## 関係

- Clip 1 — 1 OutputSettings。Clip を開き直すと OutputSettings は作り直し(outFps = 新しい sourceFps)。
- Clip 1 — 1 DocumentState(+ history)。開き直すと history は空。
- OutputSettings と DocumentState は**独立**。DocumentState の Undo/Redo は OutputSettings に触れない。
- ExportPlan は (Clip, DocumentState, OutputSettings, 形式) の関数。画面の「Fast, lossless (copy)」の表示可否はその canStreamCopy
  (+ ファイルパスがあること)。
- 時間の表示・操作の単位(タイムコード FF、1 フレーム送り、スナップ)は **Clip.sourceFps**。OutputSettings.outFps は
  書き出し(ExportPlan / ExportClock / ffmpeg 引数)と、その表示(プリセット・注記・ダイアログ)にだけ現れる。

## 状態ごとの「取り消せるか」「開き直しで戻るか」

| 状態 | Undo/Redo の対象 | プリセットを押すと | 開き直すと | 書き出し成功で |
|---|---|---|---|---|
| outFps | 対象外 | 変わる | sourceFps に戻る | そのまま |
| edited | 対象外(Undo で Saved には戻らない) | true(値が同じでも) | false | false |
| fastExport | 対象外 | 変わらない(隠れても値は保持) | false | そのまま |
| DocumentState | 対象 | 変わらない | 新規(1 区間・全長) | そのまま |
| history | — | 変わらない(Undo は有効にならない) | 空 | そのまま |

## outFps の状態遷移(30 fps CFR ソース)

```
            Source / 30            24              60              120
[30] ─────────────→ [30]   ───→ [24]    ───→ [60]    ───→ [120]
 ↑  どの状態からでも Source または 30 で [30] に戻る。どの状態からでも 24/60/120 で直接移る。
 全遷移で edited := true(既に同じ値でも)

表示:
 [30] : Source=active, 30=active, 24/60/120=not active, 注記 hidden, ダイアログ "30 fps"
 [24] : 24=active, 他 not active, 注記 hidden, ダイアログ "24 fps"
 [60] : 60=active, 他 not active, 注記 visible, ダイアログ "60 fps"
 [120]: 120=active, 他 not active, 注記 visible, ダイアログ "120 fps"
 [24]/[60]/[120] では Fast, lossless (copy) は hidden(他の条件にかかわらず)
```

## 不変条件(原製品で成り立っているもの)

- I1 outFps は常に {sourceFps, 24, 30, 60, 120} のいずれか。
- I2 isSourceFps が真なら fastExport の可否は fps 以外の条件だけで決まる。
- I3 タイムコード・フレーム送り・スナップの結果は outFps に依存しない。
- I4 出力時間(After speed / Output duration)は outFps に依存しない。
