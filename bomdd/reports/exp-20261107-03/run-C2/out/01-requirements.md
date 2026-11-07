# 出力フレームレート — 要求の整理(原製品 MoviePad 126eae9 から)

対象: 出力フレームレート(以下「出力 fps」)と、原製品でそれに関わるすべての振る舞い。
根拠は `moviepad/` の中だけ。各項目に出典を付ける(パスは `moviepad/` からの相対)。

## 0. 前提と表記

- 画面の言葉は日本語 UI(`Resources/Strings.ja.resx`)で書く。UI 言語は設定(`settings.json` の language)か、
  無ければ OS の UI 言語が ja なら日本語・それ以外は英語(`Program.cs` InitCulture)。英語 UI の対応語は
  03 §B8 の対訳表を参照。
- 「点灯(active)」= プリセットボタンの強調表示(`Classes.active`)。ツールバーの「元に戻す」等の
  「押せる/押せない」は `IsEnabled` で、examples.json では active / not active と書いた。

## 1. 何がどう動くか

| ID | 要求 | 出典 |
|---|---|---|
| R1 | 動画を開くと、出力 fps はその動画のフレームレート(ソース fps)になる。上限・丸めはしない(144 も 23.976 もそのまま)。 | `ViewModels/MainWindowViewModel.cs` LoadClip `OutFps = clip.Fps`、`tests/.../ResolutionTests.cs` LoadClip_DefaultsOutFps_ToSource |
| R2 | 出力 fps はインスペクター下部(書き出し設定・出力解像度の下)の「出力フレームレート (fps)」で、5 つのプリセット「ソース / 24 / 30 / 60 / 120」から選ぶ。自由入力欄は無い。 | `Views/InspectorView.axaml` 86–105、`docs/QUICKSTART.ja.md` §4.6 |
| R3 | 「ソース」を押すと出力 fps はソース fps に戻る。数字のボタンはその値にする。 | MainWindowViewModel `SetFps` |
| R4 | 「ソース」ボタンは、出力 fps とソース fps の差が 0.05 未満のとき点灯する。数字ボタンは、出力 fps の表示文字列(小数 2 桁まで・末尾 0 除去)がボタンの文字と完全一致するとき点灯する。両方が同時に点灯しうる(30 fps の動画を開いた直後は「ソース」と「30」が両方点灯)。 | `FpsSourceActive`、`EqualsConverter`、`docs/images/10-resolution-fps.png` |
| R5 | 出力 fps がソース fps より 0.05 を超えて高いとき、プリセットの下に注記「ソースより高いfpsはフレーム複製になります（画質は向上しません）。」を出す。低くする方向には注記は無い。 | `FpsUpsampling`、`Inspector_FpsUpsampleHint` |
| R6 | 「ソース」ボタンのツールチップは「元動画と同じ（{ソース fps} fps）」(30 fps なら「元動画と同じ（30 fps）」)。 | `FpsSourceTip`、`Inspector_FpsSourceTip` |
| R7 | プリセットを押すと、値が変わらなくても文書は「未保存の変更」になる(タイトルバーの状態表示)。 | `SetFps` の `Edited = true` |
| R8 | 出力 fps の変更は元に戻す/やり直すの履歴に入らない。元に戻す/やり直すは区間編集(トリム・分割・速度・音量・除外)だけを戻し、出力 fps はそのまま残る。 | `SetFps` は `CommitEdit` を通らない、`History<DocumentState>` は DocumentState だけを持つ |
| R9 | 書き出しダイアログのサマリ「フレームレート」に出力 fps を「{値} fps」で出す。 | `Views/ExportDialogView.axaml` 111–114 |
| R10 | 出力 fps がソース fps から 0.05 を超えて違うと、「高速・無劣化（コピー）」は使えず、書き出しダイアログのコピーのチェックボックスが隠れる(通常の再エンコードになる)。 | `ExportPlan.Analyze` fpsChange、`CanFastExport`、QUICKSTART §5 |
| R11 | 再エンコードで書き出すとき、区間速度の変更・出力 fps の変更・ソースが可変フレームレート(VFR)のいずれかがあれば、出力を出力 fps の固定フレームレート(CFR)に揃える。どれも無ければフレームの再サンプルはしない。 | `ExportPlan.NeedsRerate`、`BuildFilterGraph` |
| R12 | 固定フレームレートのソースでは、出力の公称フレームレートを有理数で明示する(29.97 系は 30000/1001 と認識)。出力フレーム数は「速度適用後の出力時間 × 出力 fps」を四捨五入した数。 | `Services/ExportClock.cs` RecognizeRate / Build、`OutputClockArgs` |
| R13 | 出力 fps は書き出しに成功しても残る(状態表示だけ「保存済み」に戻る)。別の動画を開くとその動画のソース fps に戻る(同時にコピーのチェックも外れる)。 | `ConfirmExport`、`LoadClip` |
| R14 | 出力 fps は保存されない(設定ファイルにもプロジェクトにも残らない。プロジェクト保存の機能自体が無い)。 | `AppSettings.cs` は language のみ |

## 2. 出力 fps に関わるが、出力 fps ではないもの(取り違え注意)

| ID | 事実 | 出典 |
|---|---|---|
| N1 | 画面のタイムコード(再生位置・総尺・区間の開始/終了)は **ソース fps** で M:SS:FF を数える。出力 fps を変えても変わらない。 | `PlayheadTc` 等 `FormatTimecode(…, Fps)` |
| N2 | 1 フレーム移動(「1フレーム進む/戻る」・← → , .)はソース fps の 1 フレーム。 | `StepFrame` |
| N3 | 分割・境界移動・トリムの位置はソース fps のフレームに吸着する。 | `DocumentState.SplitAt/MoveBoundary/MoveTrim` の `SnapFrame(…, fps)` |
| N4 | 「出力時間」「書き出し尺」「速度適用後」は出力 fps に依存しない(速度とトリム・除外だけで決まる)。 | `OutputLength` |
| N5 | クリップ情報の「フレームレート」はソース fps(「{値} fps」)。ただし区間が選ばれていないときだけ出る欄で、動画を開くと先頭区間が選ばれるため、原製品では通常見えない(→ 質問 Q6)。 | InspectorView 246–270、`LoadClip`、`ResolveSelection` |
| N6 | ソース fps が取れないときは 30 として扱う(タイムコード・吸着・サンプル)。ffprobe の avg_frame_rate を優先し、無ければ r_frame_rate。 | `TimeMath.DefaultFps`、`MediaProbe.ParseFrameRate` |
| N7 | 区間速度の変更があると、出力 fps がソースと同じでも書き出しは CFR に揃える(R11)・コピー不可。 | `ExportPlan` |

## 3. 範囲外として扱ったもの

- サムネイル・波形の生成に使う fps(プレビュー用の間引き、`MediaPreviewService`)は出力 fps と無関係。
- 書き出し進捗の「フレーム N」は ffmpeg が報告する出力済みフレーム数(出力 fps のフレーム)。表示形式のみ記録。
- 設計モック(`design_handoff_moviepad/`)は fps を 30 固定とし、出力 fps の選択 UI を持たない(→ Q13)。
