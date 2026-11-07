# 入力一覧 — MoviePad 再実装: 出力フレームレート

対象製品・機能: 動画編集アプリ MoviePad の再実装。**出力フレームレート**(インスペクターの「出力フレームレート (fps)」プリセット)と、原製品でそれに関わる振る舞い(読込時の既定値・注記・書き出しダイアログ表示・高速コピー可否・未保存表示・履歴との関係・タイムコード/コマ送りとの関係・書き出し時の再サンプル)。
今回の作業先: 作業フォルダの `out/`(本文書群)と `examples.json`。
振る舞いの正本: `moviepad/` の原製品 MoviePad 126eae9(依頼の指定)。
実施してよいこと: 資料を読む・文書作成・`python check_examples.py examples.json`。
実施しないこと: コード作成、ビルド、アプリ実行、作業フォルダ外の読み書き。
今回の範囲・終了条件: 1 機能について、要求・CAD・ドメインモデル・振る舞い契約の対応、操作例(examples.json)、未決と最小の問い、次に触る範囲を納品する。

## 資料

| 資料ID | 正本の場所・版 | 種類・対象範囲 | 作成者／確認者 | 実際の確認範囲(今回読んだ所) | 参照可否 |
|---|---|---|---|---|---|
| SRC-CODE-VM | moviepad/ViewModels/MainWindowViewModel.cs (126eae9) | 実装(振る舞いの正本) | 不明 / 未確認 | `_outFps` 宣言(125行)、`CanFastExport`(214-224)、`ShowVfrCopyNote`(234)、`Fps`(305)、`PlayheadTc`/`DurTc`(335-336)、`FpsText`/`FpsSourceTip`(441-443)、`OutFpsText`/`FpsSourceActive`/`FpsUpsampling`(458-461)、`OnOutFpsChanged`(494-500)、`LoadClip`(526-563)、`StepFrame`(640-644)、履歴 `BeginInteractiveEdit`/`CommitEdit`/`Undo`/`Redo`(656-712)、`SetFps`(850-857)、`ConfirmExport`(1015-1078、成功時 1065-1068)、`LoadFileAsync`(1182-1198) | 可 |
| SRC-CODE-VIEW | moviepad/Views/InspectorView.axaml、ExportDialogView.axaml、TitleBarView.axaml、ToolbarView.axaml、TransportView.axaml | 画面定義(ソフトウェアCADとして使用) | 不明 | Inspector 86-105(出力fps)、247-270(クリップ情報)、ExportDialog 83-117(高速コピー・サマリ)、TitleBar 30-38(状態表示)、Toolbar 22-27(元に戻す/やり直す)、Transport 15-33(コマ送り・タイムコード) | 可 |
| SRC-CODE-MODEL | moviepad/Models/TimeMath.cs、ClipInfo.cs、DocumentState.cs(ResolveSelection 85-91) | 実装 | 不明 | `DefaultFps`、`FormatTimecode`、`FormatSpeed`、`SnapFrame`、`ClipInfo.Fps/IsVariableFrameRate` | 可 |
| SRC-CODE-EXP | moviepad/Services/FfmpegExporter.cs、ExportClock.cs、MediaProbe.cs | 実装(外部出力) | 不明 | `ExportPlan.Analyze`(465-490)、fps フィルタ付与(261-264)、`ExportClock.Build` の fps 関連(154-221)、`RecognizeRate`(96-106)、`ParseFrameRate`(88-98) | 可(読みのみ。出力ファイルは観測していない) |
| SRC-CONV | moviepad/Converters/EqualsConverter.cs | 実装 | 不明 | 全文(文字列一致で active) | 可 |
| SRC-STR | moviepad/Resources/Strings.ja.resx、Strings.resx | 画面文言 | 不明 | Inspector_OutputFps/FpsSource/FpsSourceTip/FpsUpsampleHint/FrameRate、Status_*、Toolbar_*、Transport_*、Export_* | 可 |
| SRC-TEST | moviepad/tests/MoviePad.Tests/ResolutionTests.cs 49-61、ExportPlanTests.cs 28-80, 169-206 | 既存テスト(期待の一部) | 不明 | 読込時既定=ソースfps、fps変更→再サンプル要・コピー不可 | 可(実行していない: NOT_RUN) |
| SRC-QS | moviepad/docs/QUICKSTART.ja.md §4.6・§5「高速・無劣化コピー」、QUICKSTART.md 同節 | 利用者向け手引き(規範的な記述として扱う) | 不明 | 「出力フレームレート」は `ソース / 24 / 30 / 60 / 120` から選べる。fps を変えるとコピーのトグルが隠れる | 可 |
| SRC-IMG | moviepad/docs/images/10-resolution-fps.png、11-export.png | 静止画(ある場面の外観) | 不明 | 30 fps 素材で「ソース」と「30」が両方強調、書き出しダイアログに「フレームレート 30 fps」、状態「保存済み」 | 可(外観のみ。押した結果は決まらない) |
| SRC-MOCK | moviepad/design_handoff_moviepad/README.md §6・§8・「フレーム単位操作(fps=30)」、components/inspector.jsx・utils.jsx | 設計モック | 不明 | **出力フレームレートの操作は無い**。FPS は定数 30。クリップ情報は「未選択」時表示。書き出しダイアログに fps 行は無い | 可 |

既存の優先順位・採択済み判断: 依頼により「振る舞いの正本は原製品(moviepad/)」。本書では **実装コード > 利用者向け手引き・画像 > 設計モック** の順で読むが、これは依頼の指定(原製品が正本)からの導出であり、手引きとコードが衝突した場合の業務上の優先は未決(今回衝突は見つからなかった)。
優先順位自体が未決の資料: 設計モックと実装の差(出力fps の有無、クリップ情報の表示条件)。モックは「原製品」の一部として同梱されているが、振る舞いの正本ではないと読む(SOURCE_DERIVED: 依頼文の「振る舞いの正本は moviepad/ の原製品」と、モックに当機能が無いことから)。

画面の言語: 日本語 UI として記述した。言語は設定ファイル、無ければ OS の UI 言語が ja なら日本語・それ以外は英語(Program.cs 26-33)。英語 UI の文言は Strings.resx(Output frame rate (fps) / Source / Frame rate / An fps higher than the source duplicates frames (quality does not improve).)。

## 出発点の具体例(原資料にある期待)

| 例ID | 初期条件・履歴 | 操作列 | 原資料にある期待 | 根拠位置 | 確認済みの範囲 |
|---|---|---|---|---|---|
| SRC-EX-1 | 30 fps 素材(画像のサンプル 1280×720) を開いた後 | 書き出しダイアログを開く | 出力fps プリセットで「ソース」「30」が強調、ダイアログに「フレームレート 30 fps」 | SRC-IMG 11-export.png | 外観のみ。画像の素材が CFR かは不明 |
| SRC-EX-2 | 任意の素材 | 出力 fps を変える | 書き出しは再エンコードになり、コピーのトグルが隠れる | SRC-QS §5 | 手引きの記述。値は SRC-TEST ExportPlanTests 46-51 と一致(机上) |
| SRC-EX-3 | fps 30/60/144/23.976 の素材 | 読み込む | 出力fps = ソース fps | SRC-TEST ResolutionTests 49-61 | テストの記述のみ・NOT_RUN |

## 不足資料

| 不足 | 影響する範囲 | 今進められること | 必要な最小の追加情報 |
|---|---|---|---|
| 業務要求文書(なぜ出力fps を選ばせるか、Undo/保存との関係) | B-07(履歴対象外)・B-06(押し直しで未保存) が意図か偶然か | 実装どおりに契約化し UNRESOLVED を付ける | 06 の Q-1・Q-2 への回答 |
| 書き出し結果の観測(実ファイルの fps・フレーム数) | 外部出力契約 B-10 | コードからの導出として記述 | 実ファイルを書き出して ffprobe で確認(今回は禁止範囲) |
| 30 fps 以外の素材(29.97・VFR) の画面観測 | B-02・B-11 | コードから導出して記載 | 29.97/VFR 素材での画面確認 |
