# 03 振る舞い — 操作ごとの前後と画面

前提の表記: ソース = 30 fps CFR(既定の起点)。必要に応じて他のソースの場合を「別ソース」として併記する
(examples.json は 30 fps CFR 起点のものだけ)。画面の言葉は英語 UI(`00-readme.md`)。

## B0 動画を開いた直後(30 fps CFR)

| 見るもの | 出ているもの |
|---|---|
| インスペクター「Output frame rate (fps)」の `Source` | active |
| 同 `30` | active(Source と同時) |
| 同 `24` `60` `120` | not active |
| 注記「An fps higher than the source duplicates frames (quality does not improve).」 | hidden |
| `Source` のツールチップ(ホバー時) | Same as source (30 fps) |
| タイトルバーの保存状態 | Saved |
| ツールバーの Undo / Redo | not active(押せない) |
| トランスポートのタイムコード | 0:00:00(再生ヘッド = トリム開始 = 0) |
| 書き出しダイアログ | hidden |
| インスペクター「Clip info」節(ソースの「Frame rate 30 fps」行を含む) | hidden(区間「Region 1 / 1」が選択されているため) |

別ソース: 23.976 fps なら `Source` だけ active(表示文字列 "23.98" はどの数値ボタンとも一致しない)、ツールチップ「Same as source (23.98 fps)」。
60 fps なら `Source` と `60` が active。144 fps なら `Source` だけ active。

## B1 プリセットを押す(`SetFps`)

前: outFps = x。押したもの p。
後:
- outFps = (p が Source なら sourceFps、それ以外は p の数値)。
- edited = true → タイトルバー「Unsaved changes」。**値が変わらなくても**(30 のときに `30` や `Source` を押しても)そうなる。
- 強調: `Source` は |outFps − sourceFps| < 0.05 のとき、数値ボタンは outFpsText と文字が一致するとき。
- 注記: outFps > sourceFps + 0.05 のときだけ visible。
- 取り消し履歴: 変化なし(Undo / Redo の可否はそのまま)。
- 高速コピーの可否を再計算(書き出しダイアログを開いたときの表示に効く)。

| 押す | Source | 24 | 30 | 60 | 120 | 注記 | ダイアログの Frame rate |
|---|---|---|---|---|---|---|---|
| Source | active | – | active | – | – | hidden | 30 fps |
| 24 | – | active | – | – | – | hidden | 24 fps |
| 30 | active | – | active | – | – | hidden | 30 fps |
| 60 | – | – | – | active | – | visible | 60 fps |
| 120 | – | – | – | – | active | visible | 120 fps |

(– = not active。どの行も直前の状態によらない。)

## B2 書き出しダイアログを開く(ツールバー右上 `Export`)

- 後: ダイアログ visible。サマリ「Frame rate」= `{outFpsText} fps`。「Output resolution」「Output duration」は fps と無関係。
- outFps ≠ ソース(24/60/120)なら「Fast, lossless (copy)」チェックボックスとヒントは hidden。
- outFps = ソースなら、MP4 形式・H.264/H.265 映像・AAC/MP3/AC-3 音声(または音声なし)・単一連続区間・速度/音量/解像度無変更のとき visible。
  (起点の動画のコーデックは決まっていないので、examples.json ではこの「visible」側は主張しない。)
- MP4 以外(Intermediate file / ProRes)を選ぶと fps によらず hidden。

## B3 書き出しダイアログを閉じる(`Cancel` / 背景クリック)

- 後: ダイアログ hidden。outFps・edited は変わらない(閉じても選んだ fps は残る)。書き出し中は閉じられない。

## B4 書き出す(ダイアログの `Export`)

- 保存先を選んだ後に実行。出力 fps の効き方は `01-requirements.md` R7。
- 進捗の「Frame N」は出力フレーム数(60 を選ぶと 30 のときの約 2 倍の数まで進む)。
- 成功: ダイアログ hidden、edited = false → 「Saved」。outFps はそのまま(次の書き出しも同じ fps)。
- 失敗・中止: エラー文言を表示、outFps・edited そのまま。
- 高速コピーで書き出すとき outFps は使われない(コピーは outFps = ソースのときしか選べない)。VFR はそのまま VFR。

## B5 取り消し / やり直し(ツールバーの Undo / Redo、Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z)

- fps プリセットだけを押した後: Undo は not active のまま。Ctrl+Z を押しても何も起きない。
- 区間の編集(例: 速度プリセット `1.5x`)→ fps `60` → Undo: 速度は 1 に戻る、**fps は 60 のまま**、`60` active、注記 visible、
  タイトルバーは「Unsaved changes」のまま。Redo が active になる。
- fps `60` → 区間の編集 → Undo: 区間の編集だけが戻る。fps は 60 のまま。

## B6 フレーム送り(トランスポートの 1 フレーム進む/戻る、→ ← , .)

- 出力 fps によらずソース fps のグリッドで動く。30 fps ソースで出力 60 を選んでも、1 回押すごとに 1/30 秒進み、
  タイムコードは 0:00:00 → 0:00:01 → 0:00:02 と数える。
- fps プリセットを押しても再生ヘッド・タイムコードは動かない。
- 実ファイルでは VLC の再生位置が再生ヘッドへ書き戻されるが、それは再生中だけ(停止中のフレーム送りの値は上書きされない)。出典: Views/PreviewView.axaml.cs:252-270, 336-346。

## B7 分割・トリム・境界ドラッグ

- 位置はソース fps のフレームにスナップ。出力 fps は無関係。fps プリセットを押しても区間・トリムは変わらない。

## B8 出力解像度の操作(幅/高さ入力、100%/75%/50%、Reset、Keep aspect ratio)

- outFps に触れない。どれも edited = true(Keep aspect ratio の切替だけは edited を変えない)。
  解像度を変えると高速コピーは fps と同様に hidden。

## B9 別の動画を開く(`Open` / ドラッグ&ドロップ)

- outFps = 新しい動画の sourceFps。前に選んだ値は消える。edited = false、履歴は空、高速コピー OFF。
- 読み込みに失敗した場合は前の動画と設定がそのまま残る(エラーを表示)。

## B10 UI 言語の切替(タイトルバーの地球アイコン → 日本語 / English)

- 見出し・`Source` の文言・注記・ツールチップが切り替わる。outFps・強調・数値表記("30" "60 fps")は変わらない。
- 選んだ言語は利用者設定ファイルに保存される(`%LOCALAPPDATA%\MoviePad\settings.json`)。

## B11 VFR ソース(参考、起点外)

- 開いた時点の outFps = avg_frame_rate。
- 書き出しは fps を変えなくても常に outFps の CFR に揃える(再エンコード時)。
- 高速コピーは fps を変えなければ選べ、ON にすると VFR 注記(「Fast copy preserves the original timestamps, …」)が出る。
