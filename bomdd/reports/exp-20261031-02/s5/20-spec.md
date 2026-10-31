# 仕様書 — MoviePad(作り直し)

> 製造パッケージに含まれる(製造装置が読む)。REQ への双方向トレースを保つ。
> 上流: `10-requirements.yaml`(95 要求)・`domain-model.json`(25 entity・81 操作)・`screens.json`(12 画面)・
> `scenarios.json`(151 シナリオ)。動作の正は `authority/`(元のアプリ。説明書とソースが食い違うときはソース)。
> 元のアプリの不具合も、そのまま再現する振る舞いとして書く(各節の「再現する不具合」)。

## 1. 概要と用語

MoviePad は、1 本の動画ファイルを読み込み、トリム・区間ごとの速度/音量/ピッチ維持/除外を編集して、ffmpeg で書き出す
Windows 向けのデスクトップ動画編集アプリ(Avalonia 12.0.0・CommunityToolkit.Mvvm 8.4.0・LibVLC)。範囲は全機能・全画面。
プレビューの映像そのものの描画と再生のタイミングだけは範囲外(要求の範囲の定義)。

用語(本書はドメインモデルの名前で書く。`Entity.attribute` は属性、`Operation` は操作):

| 用語 | 意味 | モデルの名前 |
|---|---|---|
| クリップ | 読み込んだ動画のメタ情報(不変)。起動時はサンプル | `Clip` |
| ドキュメント | トリム開始・終了と区間の列(履歴の対象) | `Document`・`Region` |
| 編集対象 | インスペクターが表示・編集する区間 | `EditSession.selectedRegionId`・`EditSession.selectedRegion` |
| 再生ヘッドの位置の区間 | `RegionAt(playhead)` | `EditSession.activeRegion` |
| 偶数丸め | 中点を偶数側へ(.NET `Math.Round` の既定)。本書の「丸め」は断りがなければこれ | — |
| RoundHalfUp | 中点を切り上げる丸め。書き出しの時間計算だけで使う | — |
| SnapFrame(t) | 偶数丸め(t·fps)/fps(fps ≤ 0 なら 30) | — |
| Even(n) | max(2, 偶数丸め(n/2)·2)(出力寸法の偶数化) | — |
| FormatTimecode(s, fps) | 「M:SS:FF」。s' = max(0, s) + 1e-6、分 = floor(s'/60)、秒 = floor(s' mod 60)、FF = floor((s' mod 1)·fps) | — |
| FormatClock(s) | 「M:SS」。FormatTimecode と同じ式で分と秒だけ | — |
| FormatSpeed(v) | 小数 2 桁まで・末尾の 0 と小数点を除く(2・1.5・0.25)。カルチャ不変(小数点はピリオド) | — |
| 最小長 | 区間の最小長の定数 0.5 秒 | — |
| 出来事 | 部品からでなく時間・プレイヤー・裏の処理が起こす操作(kind = event) | `PlaybackTick` ほか 15 |
| 未保存の変更 | Edited | `EditSession.edited` |

文言は en を正として書き、ja は resx(`authority/Resources/Strings.ja.resx`)の同じキーの値を使う(§2.4)。

## 2. 機能仕様

<a id="startup"></a>
### 2.1 起動とサンプル (REQ-001, REQ-002)
- 仕様節ID: SPEC-STARTUP-001
- 振る舞い:
  - 起動直後は読み込み済みのサンプルを表示する。`Clip`: `path` = ""(空文字)・`fileName` = interview_raw.mp4・`duration` = 138・
    `width`×`height` = 1920×1080・`fps` = 30・`videoCodec` = H.264・`audioCodec` = AAC・`sampleRate` = 48000・
    `isVariableFrameRate` = false(`isSample` は `path` が空なので真)。
  - `Document`: `trimStart` = 6・`trimEnd` = 132・`regions` = id 1 [6,40) 1x・id 2 [40,64) 2x・id 3 [64,104) 1x・id 4 [104,132] 0.5x
    (すべて `preservePitch` = true・`volume` = 1.0・`excluded` = false)。秒は浮動小数の等値で照合する。
  - `EditSession`: `playhead` = 6・`playing` = false・`selectedRegionId` = 1・`edited` = false(`statusText` = Saved)・
    `nextRegionId` = 5・`loadGeneration` = 0。`OutputSettings`: `outputWidth`×`outputHeight` = 1920×1080・`outputFps` = 30・
    `keepAspect` = true。`History.past`/`future` は空。`PreviewPlayer.externalPlayback` = false(実映像を読み込まず、再生は内蔵
    タイマー `PlaybackTick` が進める・§2.10)。
  - サンプルは書き出せない(`ConfirmExport` で専用の文言・§2.20)。
  - `Clip` は一度設定されると null に戻らない(読み込みの失敗も前のクリップを残す・§2.7)。したがって空状態(タイトルバーの
    「No project loaded」/ja: プロジェクト未読み込み・ツールバーの Open 以外の非表示・タイムライン/インスペクター/プレビュー/
    トランスポートの非表示)は到達しない。空状態の表示条件(元のアプリの HasClip/NoClip)を作り込む場合も、到達する経路を
    作らない(作るかどうかは UQ-SPEC-001)。
- 核/表面: core(出所: authority/ViewModels/MainWindowViewModel.cs#MainWindowViewModel()・authority/Models/Sample.cs)
- 受入観点(深さ・許容差の根拠): unit・exact(REQ-001 の数値の完全一致)/ L1(読み込み失敗後も前のクリップが残る・REQ-002)
- 画面: SCR-TITLEBAR(EL-TB-FILENAME・EL-TB-STATUS・EL-TB-NOPROJECT〔到達しない〕)・SCR-TRANSPORT・SCR-INSPECTOR・SCR-TIMELINE
- シナリオ: UC-001・UC-003・UC-004・UC-148
- E-BOM 候補: E-STARTUP-001
- M-BOM 候補: M-STARTUP-001
- Control Plan 候補: CP-STARTUP-001
- 表示契約:
  - 原典参照: authority/Models/Sample.cs・authority/Views/TitleBarView.axaml
  - 提示要素: ファイル名・状態表示(Saved)・サンプルの区間 4 つ・再生ヘッド 0:06:00 / 2:18:00
  - 対象外要素: 空状態の表示(到達しない・UQ-SPEC-001)

<a id="window"></a>
### 2.2 メインウィンドウ・オーバーレイ (REQ-003, REQ-004, REQ-005, REQ-092, REQ-095)
- 仕様節ID: SPEC-WINDOW-001
- 振る舞い:
  - タイトル「MoviePad」・アイコン Assets/moviepad.ico・Fluent のダーク(RequestedThemeVariant=Dark。OS の明暗に関わらず
    ダーク)。OS 標準の枠とタイトルバーは使わない(自前のタイトルバー §2.3 と縁)。
  - `MainWindow.width`×`height` の既定は 1280×880、最小 960×600(論理 px)。既定サイズが表示先の作業領域より大きいときは、
    作業領域に収まる大きさ(最小以上)へ縮め、`position` を作業領域の中央(整数除算の切り捨て)にする。収まるときの初期位置は
    OS / Avalonia の既定(未決・UQ-SPEC-002)。`windowState` の初期値は Normal、`open` は true。
  - 四辺・四隅に幅 6 px のリサイズ用の縁(EL-MAIN-RESIZE-NORTHWEST・EL-MAIN-RESIZE-NORTH・EL-MAIN-RESIZE-NORTHEAST・EL-MAIN-RESIZE-WEST・EL-MAIN-RESIZE-EAST・
    EL-MAIN-RESIZE-SOUTHWEST・EL-MAIN-RESIZE-SOUTH・EL-MAIN-RESIZE-SOUTHEAST)。
    左ボタンのドラッグで `ResizeWindow`(param = 辺/隅)が `width`・`height`(左・上の辺なら `position` も)を変える(最小 960×600)。
    縁は本体(タイトルバー・ツールバー・インスペクター・タイムライン)より上、オーバーレイとエラーのバナーより下に重なる。
    外周 6 px の押下は下の部品に届かない。`windowState` = Maximized の間も縁は押下を取り、何もしない。
  - 閉じる(`CloseWindow`・EL-TB-CLOSE)は未保存の変更があっても確認なしに即座に閉じる(`MainWindow.open` = false)。閉じるとき
    再生を止め、進行中の書き出し・サムネイル/波形の生成を中断し、キューを空にし、サムネイルを捨てる。中断した書き出しの途中の
    ファイルは残る(`OutputFile.state` = partial)。
  - オーバーレイ: 書き出しダイアログ(`ExportJob.dialogShown`)・About(`AboutDialog.shown`)・ffmpeg セットアップ
    (`FfmpegSetup.shown`)のどれかを表示している間 `MainWindow.modalOverlayShown` が真。オーバーレイはタイトルバーと縁を含む
    ウィンドウ全体を覆い、背景を Scrim の色で暗くする。表示中はタイトルバーのドラッグ移動・ダブルクリックの最大化・縁のリサイズ・
    最小化/最大化/閉じる/言語/About のボタン・ツールバー・プレビュー・タイムライン・インスペクターのマウス操作が届かない。
    キーボードの操作(§2.19)とファイルのドロップ(`DropFile`)は働く。読み込みエラーのバナーはオーバーレイの下になる。
  - 書き出しダイアログ(EL-EX-SCRIM → `CloseExport`)と About(EL-AB-SCRIM → `CloseAbout`)は、タイトルバーの上を含むモーダルの
    外の押下(マウスのどのボタンでも)で閉じる。書き出し中の書き出しダイアログは閉じない。ffmpeg セットアップは外を押しても
    閉じない(押下の処理を持たない)。
- 再現する不具合: 未保存の変更の確認なしで終了する(UQ-SPEC-003)。
- 核/表面: core(出所: authority/Views/MainWindow.axaml・MainWindow.axaml.cs・App.axaml)
- 表示契約:
  - 原典参照: authority/Views/MainWindow.axaml・App.axaml・Assets/moviepad.ico
  - 提示要素: ウィンドウのタイトル「MoviePad」とアイコン・ダークのテーマ・四辺四隅の 6 px の縁(見た目は透明で、押下とカーソルだけを持つ)・
    オーバーレイの Scrim(ウィンドウ全体・タイトルバーと縁を含む)と、その上の各モーダル(書き出し §2.20・About §2.22・ffmpeg §2.6)
  - 対象外要素: OS 標準の枠とタイトルバー(使わない)
- 受入観点: L2・exact(ウィンドウの寸法・最小・オーバーレイの遮断は実機で)
- 画面: SCR-MAIN(EL-MAIN-WINDOW・EL-MAIN-RESIZE-*・EL-MAIN-DROP)・SCR-TITLEBAR(EL-TB-CLOSE)・SCR-EXPORT(EL-EX-SCRIM)・
  SCR-ABOUT(EL-AB-SCRIM)・SCR-FFMPEG(EL-FF-OVERLAY)
- シナリオ: UC-120・UC-122・UC-125・UC-126・UC-151・UC-161・UC-165・UC-166・UC-168・UC-178・UC-193・UC-201・UC-203
- E-BOM 候補: E-WINDOW-001
- M-BOM 候補: M-WINDOW-001
- Control Plan 候補: CP-WINDOW-001

<a id="title-bar"></a>
### 2.3 タイトルバー (REQ-006, REQ-007, REQ-008)
- 仕様節ID: SPEC-TITLEBAR-001
- 振る舞い:
  - 高さ 44 px。左にブランド(再生アイコン+「MoviePad」)、中央に、左から フィルムのアイコン(13 px・Text2)・`Clip.fileName`(EL-TB-FILENAME・
    12.5・Text2・最大幅 420 px で末尾省略)・5×5 の Text4 の丸い点・状態表示(EL-TB-STATUS)を間隔 8 で並べ、右に言語(EL-TB-LANGUAGE)・About(EL-TB-ABOUT)・最小化(EL-TB-MINIMIZE)・最大化(EL-TB-MAXIMIZE)・
    閉じる(EL-TB-CLOSE)。
  - 状態表示: `EditSession.statusText` は `edited` が真なら「Unsaved changes」(ja: 未保存の変更)、偽なら「Saved」(ja: 保存済み)。
    `statusColor` は真なら accent-text #8EC1FF、偽なら text-2 #ADB1B7。
  - 中央の領域の左ボタンのドラッグは `MoveWindow`(`position` を変える・EL-TB-DRAG)、ダブルクリックは `ToggleMaximize`
    (EL-TB-DRAG-DOUBLE)。最大化ボタンも `ToggleMaximize`(`windowState` を Maximized と Normal の間で切り替える)。最大化ボタンの
    アイコンとツールチップ「Maximize」(ja: 最大化)は最大化中も変わらない。最小化ボタンは `MinimizeWindow`(Minimized)、閉じるは `CloseWindow`。
  - ボタンのツールチップ: 言語「Language」(ja: 言語・TitleBar_Language)・About「About MoviePad」(ja: MoviePad について・
    TitleBar_About)・最小化「Minimize」(ja: 最小化・TitleBar_Minimize)・最大化「Maximize」(ja: 最大化・TitleBar_Maximize)・
    閉じる「Close」(ja: 閉じる・Common_Close)。
  - 言語ボタン(地球アイコン)は `OpenLanguageMenu` で「日本語」「English」の 2 項目のメニューを出す(項目名はどちらの言語でも
    翻訳しない)。項目(EL-TB-LANG-JA / EL-TB-LANG-EN)は `SwitchLanguage`(ja / en)で即座に切り替え、`AppSettings.language` に
    保存する(§2.4・§2.5)。メニューが開いているかはモデルに属性が無い(UQ-SPEC-019)。
  - EL-TB-NOPROJECT(TitleBar_NoProject「No project loaded」・ja: プロジェクト未読み込み)はクリップが無いときの表示で、到達しない(§2.1)。
- 核/表面: core(出所: authority/Views/TitleBarView.axaml・TitleBarView.axaml.cs)
- 受入観点: L1・exact(文言・色・切り替え)/ L2(ドラッグ移動・最大化)
- 画面: SCR-TITLEBAR(全 12 部品)
- シナリオ: UC-041・UC-121・UC-123・UC-124・UC-125・UC-127・UC-130
- E-BOM 候補: E-TITLEBAR-001
- M-BOM 候補: M-TITLEBAR-001
- Control Plan 候補: CP-TITLEBAR-001
- 表示契約:
  - 原典参照: authority/Views/TitleBarView.axaml
  - 提示要素: ブランド・フィルムのアイコン(13 px・Text2)・ファイル名(12.5・Text2)・5×5 の Text4 の丸い点・状態表示(2 値・2 色・12.5)・言語/About/最小化/最大化/閉じるのボタンとそのツールチップ 5 つ・言語メニュー 2 項目
  - 対象外要素: なし(No project は到達しない表示として扱う)

<a id="localization"></a>
### 2.4 言語 (REQ-009, REQ-010, REQ-011)
- 仕様節ID: SPEC-LOCALE-001
- 振る舞い:
  - UI の文字列は en(Strings.resx)と ja(Strings.ja.resx)の 2 言語で、両方に同じ 120 個のキーが揃う。キーに対応する文字列が
    無いときはキーそのものを表示する。製品名 MoviePad・形式名「MP4 (H.264 / AAC)」「ProRes 422 HQ / PCM」(`ExportFormat.title` の
    固定の 2 つ)・ライセンス名・数値表記は翻訳しない。中間ファイルの見出しとタグ 3 つは resx(Export_TitleLossless・
    Export_TagSharing/TagLossless/TagEditing)で、言語で変わる。
  - 起動時の `Localization.uiLanguage`(Program.InitCulture): lang = `AppSettings.language` が null のときだけ OS の UI 言語の 2 文字
    コードが ja なら "ja"、それ以外 "en"。null でなければその文字列のまま new CultureInfo(lang) にする。存在しないカルチャ名
    (CultureNotFoundException)なら en。空文字列は不変カルチャになり英語(既定の resx)の文字列になる。ja-JP などの地域付きは resx の
    代替で ja の文字列、fr など resx の無い言語は英語の文字列になる。
  - `SwitchLanguage` は再起動なしに即時に反映し、表示中のすべての文字列を新しい言語で表示し直す。表示中の一時メッセージのうち、
    翻訳元のキーを持つものは新しい言語で書き直す: `LoadError.message`・`ExportJob.statusMessage` のうち `statusMessageKey` を持つもの
    (「Samples cannot be exported. Open an actual file.」と「Exporting…」)・`FfmpegSetup.errorMessage` の定型部分(続く例外メッセージは
    そのまま)・`AboutDialog.notices` が案内文(`noticesIsFallback`)のとき。
  - 書き直さないもの: 書き出しの結果の文言(「Export canceled.」「Output duration is zero.」「There are no regions to export.」と
    ffmpeg のエラー。定型文でも表示したときの言語のまま)・ライセンス全文。
  - 数値の書式(タイムコード・速度「1.5x」・fps・リード秒数「0.0」)は言語に関わらず不変(小数点はピリオド・カルチャ不変)。
    言語の切り替え(SetCulture)が変えるのは UI カルチャ(CurrentUICulture・DefaultThreadCurrentUICulture)だけで、CurrentCulture(数値・
    日付の書式)は変えない。例外は MOVIEPAD_INSPECTOR_SCROLL の読み取りで、CurrentCulture(OS の地域の書式。UI の言語では変わらない)で
    読む(§2.24)。
- 核/表面: core(出所: authority/Services/Localizer.cs・Resources/Strings*.resx・Markup/TranslateExtension.cs)
- 受入観点: unit・exact(キー集合の一致・キーそのものの表示・起動時の決定)/ L1(切り替えの即時反映と書き直しの対象)
- 画面: 全画面の文言。SCR-TITLEBAR(EL-TB-LANG-JA・EL-TB-LANG-EN)・SCR-MAIN(EL-MAIN-ERROR-BANNER)・SCR-EXPORT(EL-EX-STATUS)・
  SCR-FFMPEG(EL-FF-ERROR)・SCR-ABOUT(EL-AB-NOTICES)
- シナリオ: UC-130・UC-131・UC-132・UC-133・UC-134・UC-167・UC-180
- E-BOM 候補: E-LOCALE-001
- M-BOM 候補: M-LOCALE-001
- Control Plan 候補: CP-LOCALE-001

<a id="settings"></a>
### 2.5 設定の保存 (REQ-012)
- 仕様節ID: SPEC-SETTINGS-001
- 振る舞い:
  - `%LOCALAPPDATA%\MoviePad\settings.json` に JSON(インデント付き)で保存する。項目は `AppSettings.language`(キー language・
    値 ja / en)だけ。書くのは `SwitchLanguage` のとき。
  - ファイルが無い・壊れている・読めないときは既定値(言語未設定 = null)として扱う。保存の失敗は無視する(エラーを出さない)。
  - 書き出し形式・出力解像度・fps・ズームなどは保存しない。
- 核/表面: core(出所: authority/Services/AppSettings.cs)
- 受入観点: unit・exact(ファイルの内容・壊れたファイルの扱い・保存失敗の無視)
- 画面: なし(画面に出ない)
- シナリオ: UC-133
- E-BOM 候補: E-SETTINGS-001
- M-BOM 候補: M-SETTINGS-001
- Control Plan 候補: CP-SETTINGS-001

<a id="ffmpeg"></a>
### 2.6 ffmpeg の解決とセットアップ (REQ-013, REQ-014, REQ-015)
- 仕様節ID: SPEC-FFMPEG-001
- 振る舞い:
  - `FfmpegInstallation.ffmpegPath` / `ffprobePath` の探索順: `StartupEnvironment.ffmpegDir`(MOVIEPAD_FFMPEG_DIR)のフォルダ →
    アプリのフォルダの ffmpeg/ → `%LOCALAPPDATA%\MoviePad\ffmpeg` → アプリのフォルダ直下 → 見つからなければ実行ファイル名だけ
    (ffmpeg.exe / ffprobe.exe・PATH で解決)。`available` は解決した 2 つのパスがどちらも実在のファイルのとき真(PATH の解決は判定に
    含めない。最後の段は名前だけを返すので、カレントディレクトリに ffmpeg.exe と ffprobe.exe があると真になる)。
  - 起動時に `available` が偽なら `FfmpegSetup.shown` を真にし、画面中央に幅 470 px のオーバーレイ(背景を暗くする)を出す
    (EL-FF-OVERLAY)。タイトル「ffmpeg setup」・説明文・「Later」(EL-FF-LATER)・「Download」(EL-FF-DOWNLOAD)。
  - 「Later」= `DismissFfmpegSetup`: オーバーレイを閉じるだけで保存しない(次回の起動で再び出る)。閉じた後も UI と(サンプルの)
    編集操作は使える。
  - 「Download」= `InstallFfmpeg`: 取得中なら何もしない。`installing` を真・`errorMessage` を消し・`installProgress` を 0 に戻し(失敗の
    後は戻さないので、失敗のときの値のまま残る)、固定の URL(GyanD essentials
    build 2024-12-23-git-6c9218d748 の zip・authority/Services/FfmpegInstaller.cs の定数)を取得し、ffmpeg.exe・ffprobe.exe と zip の
    2 階層以内にある LICENSE / COPYING を `%LOCALAPPDATA%\MoviePad\ffmpeg` に展開し、2 つの実行ファイルの SHA-256 を固定値と照合する。
    取得中はボタンを隠し、進捗バーと `installText`「Downloading… N%」(N = 偶数丸め(`installProgress`·100))を出す
    (EL-FF-PROGRESS)。`FfmpegInstallProgressReported` が `installProgress` を 取得 0〜0.9(応答に Content-Length があるときだけ。
    無ければ 0 のまま展開の 0.92 へ飛ぶ)・展開 0.92・検証 0.97・完了 1.0 にする。
  - 成功: SHA-256 が一致したらパスの解決をやり直し(進捗 1.0 を届ける)、解決し直した `FfmpegInstallation.available` が真ならオーバーレイを
    閉じる。`available` が偽なら(探索順で解決した 2 つのパスがどちらも実在にはならないとき)失敗として扱い、何も削除せずに `errorMessage` =
    「ffmpeg verification failed. Please try again later.」にする。SHA-256 の不一致: ffmpeg.exe と ffprobe.exe だけを削除し(展開した LICENSE/COPYING
    は残る)、`errorMessage` =「ffmpeg verification failed. Please try again later.」。通信などの例外: `errorMessage` =
    「Download failed (please check your network): 」+ 例外メッセージ(EL-FF-ERROR)。どちらもボタンを戻す(再試行できる)。一時 zip は
    成否に関わらず削除する。終わったら `installing` を偽にする。
  - ffprobe / ffmpeg がどこにも無いまま開く・書き出すと、プロセスの起動の例外が捕捉されずに UI へ伝わる: 読み込みエラーのバナーも
    書き出しの失敗文言も出ず、クリップは変わらない。CommunityToolkit.Mvvm 8.4.0 の非同期コマンドが例外を UI スレッドへ投げ直し、
    アプリは未処理の例外の処理を持たないので、アプリは異常終了する(ドロップの async void も同じ経路)。書き出しのとき VM に残る状態は
    §2.20 と同じ。サムネイル・波形は失敗を握りつぶして擬似表示のまま。
- 再現する不具合: ffmpeg 不在での異常終了(UQ-SPEC-004・UQ-SPEC-005)。
- 核/表面: core(出所: authority/Services/FfmpegLocator.cs・FfmpegInstaller.cs・Views/MainWindow.axaml)
- 受入観点: unit・exact(探索順・available の判定)/ L1(オーバーレイの表示と Later)/ L2(取得・検証・異常終了は実機)
- 画面: SCR-FFMPEG(EL-FF-OVERLAY・EL-FF-PROGRESS・EL-FF-ERROR・EL-FF-LATER・EL-FF-DOWNLOAD)
- シナリオ: UC-190・UC-191・UC-192・UC-194・UC-220・UC-221・UC-222
- E-BOM 候補: E-FFMPEG-001
- M-BOM 候補: M-FFMPEG-001
- Control Plan 候補: CP-FFMPEG-001
- 表示契約:
  - 原典参照: authority/Views/MainWindow.axaml(ffmpeg セットアップの部分)
  - 提示要素: タイトル・説明文・Later・Download・進捗バー・進捗の文言・エラーの文言
  - 対象外要素: なし

<a id="open"></a>
### 2.7 ファイルを開く・読み込み (REQ-016, REQ-017, REQ-018, REQ-019, REQ-020, REQ-021)
- 仕様節ID: SPEC-OPEN-001
- 振る舞い:
  - `Open`(EL-TL-OPEN): OS のファイル選択ダイアログ(SCR-OPEN-PICKER / EL-OP-PICKER・タイトル「Open video」・単一選択・種類の
    フィルタ「Video files」(*.mp4 *.mov *.mkv *.m4v *.webm)と「All files」(*))を開く。選ばずに閉じたら何も変えない。
  - `DragOver`(EL-MAIN-DRAGOVER): ドラッグしているデータにファイルが含まれるときだけ受け入れ(コピー)の表示、それ以外は受け入れない
    表示。モデルの値は変えない。
  - `DropFile`(EL-MAIN-DROP): ウィンドウ全体で受け付ける(オーバーレイの表示中・書き出し中も)。最初の 1 ファイルだけを対象に、
    拡張子が .mp4 .mov .mkv .m4v .webm(大文字小文字を区別しない)なら `Open` で選んだときと同じ読み込みを始める。それ以外は何も
    表示せずに無視する。
  - 読み込みの開始: `EditSession.loadGeneration` を 1 増やし、`LoadError.message` を消し、ffprobe の JSON 出力で解析する。結果は
    その世代がまだ最新のときだけ適用する(最後に始めた読み込みが勝つ・先の結果は捨てる)。
  - 解析: 読み込めるのは、ファイルが存在し、ffprobe が正常終了し、映像ストリームがあり、幅と高さが正、長さが正のとき。
    `Clip.duration` = format の duration(無ければ最初の映像ストリームの duration)。`fps` = avg_frame_rate が正ならその値、無ければ
    r_frame_rate、どちらも無ければ 30。`isVariableFrameRate` = 両方が正で |avg − r| > max(0.1, 0.005·max(avg, r))。
    `videoCodec` / `audioCodec` の表示名 = h264→H.264・hevc→H.265・vp9→VP9・av1→AV1・aac→AAC・mp3→MP3・opus→Opus・ac3→AC-3・
    pcm_s16le→PCM・それ以外は大文字化。音声が無ければ `audioCodec` =「—」(`hasAudio` は偽)。`sampleRate` = 最初の音声ストリームの値
    (無ければ 48000)。
  - 失敗: `Clip` と編集状態を変えずに `LoadError.message` =「Could not load this file (the format may be unsupported).」
    (ja: このファイルを読み込めませんでした（対応していない形式の可能性があります）。)。バナー(EL-MAIN-ERROR-BANNER・`LoadError.visible` = message が空でないとき表示・画面下部中央・
    警告色の点・文言・✕)。✕(EL-MAIN-ERROR-CLOSE)= `ClearError` で消える。次の読み込みの開始でも消える。
  - 成功(読み込みの初期状態): `playing` = false・`History.past`/`future` を空・`Document` = 全長 1 区間(id 1・開始 0・終了 = 長さ・
    速度 1・ピッチ維持 true・音量 1.0・除外 false)・`trimStart` = 0・`trimEnd` = 長さ・`playhead` = 0・`selectedRegionId` = その区間・
    `nextRegionId` = 読み込んだドキュメントの最大 ID + 1(= 2)・`outputWidth`×`outputHeight` = ソースの幅×高さ・`outputFps` = ソースの
    fps・`keepAspect` = true・`edited` = false・`ExportJob.fastExport` = false・`copyCutStart` = null(`copyCutGeneration` を 1 増やす)・
    `PreviewPlayer.externalPlayback` = false(プレイヤーが新しいクリップを読み込む `PlayerClipLoaded` まで、再生は内蔵タイマーで進む)・
    `MediaPreviewData` と `MediaJobQueue` を捨てて波形の生成を投入(§2.16)。
  - 読み込みが変えないもの: `ExportJob.selectedFormat`・`ExportJob.statusMessage`(サンプルの書き出しエラーなどが実ファイルの読み込み後も
    残る)・`ExportJob.dialogShown`・`TimelineView.pxPerSec`・`MediaPreviewData.waveformMemoryCache`。`TimelineView.scrollOffset` は
    直接は変えない(UQ-SPEC-020)。
  - 書き出し中に読み込むと、進行中の書き出しは開始時の `ExportRun.request` で続き、成功するとダイアログを閉じて新しいクリップの
    `edited` も偽にする。
  - Open と ConfirmExport は非同期のコマンドで、実行中(選択ダイアログ・解析・書き出しの間)はボタンが無効の表示になる
    (CommunityToolkit.Mvvm の既定。モデルに属性が無い・UQ-SPEC-018)。
  - ffprobe が起動できないときは例外で異常終了(§2.6)。
- 核/表面: core(出所: authority/ViewModels/MainWindowViewModel.cs#Open・#LoadFileAsync・#LoadClip・Services/MediaProbe.cs・
  Views/MainWindow.axaml.cs#OnDrop)
- 受入観点: unit・exact(解析の規則・初期状態・ドロップの拡張子・最後の読み込みが勝つ)/ L1(ダイアログ・バナー)
- 画面: SCR-TOOLBAR(EL-TL-OPEN)・SCR-OPEN-PICKER(EL-OP-PICKER)・SCR-MAIN(EL-MAIN-DRAGOVER・EL-MAIN-DROP・EL-MAIN-ERROR-BANNER・
  EL-MAIN-ERROR-CLOSE)
- シナリオ: UC-131・UC-140・UC-141・UC-142・UC-143・UC-144・UC-145・UC-146・UC-147・UC-148・UC-149・UC-150・UC-151
- E-BOM 候補: E-OPEN-001
- M-BOM 候補: M-OPEN-001
- Control Plan 候補: CP-OPEN-001
- 表示契約:
  - 原典参照: authority/Views/MainWindow.axaml(エラーのバナー)
  - 提示要素: 警告色の点・エラーの文言・✕ボタン
  - 対象外要素: 対応外の拡張子をドロップしたときの通知(元のアプリに無い・UQ-SPEC-006)

<a id="document-model"></a>
### 2.8 編集ドキュメントと丸め (REQ-022, REQ-023, REQ-024, REQ-025)
- 仕様節ID: SPEC-DOCMODEL-001
- 振る舞い:
  - `Document` は `trimStart`・`trimEnd` と、時刻順に隙間なく並んだ `regions` からなる。各 `Region` は `id`・`start`・`end`(秒・
    ソース基準)・`speed`・`preservePitch`・`excluded`・`volume` を持つ。先頭区間の `start` = `trimStart`、末尾区間の `end` = `trimEnd`、
    隣り合う区間は `end` = 次の `start`(INV-001)。編集操作はすべて新しい `Document` を作り、元の `Document` は変えない(INV-002・
    履歴はスナップショットの参照を積む)。
  - RegionAt(t)(= `EditSession.activeRegion` の t = `playhead`): t が [`trimStart`, `trimEnd`] の外なら無し。範囲内なら各区間を半開区間
    [start, end) として探し、境界ちょうどの時刻は後ろの区間に属する。末尾区間だけは end を含む。
  - 丸め: 本書の「偶数丸め」は中点を偶数側へ(四捨五入ではない)。書き出しの時間計算(§2.21)の RoundHalfUp は 0.5 を切り上げる。
    分割・境界・トリムの時刻は SnapFrame で ソースの fps の格子に乗せる。分割は格子に丸めた後で判定するので、分割でできる区間は必ず
    0.5 秒以上。境界の移動とトリムの移動は先に [下限, 上限](最小長 0.5 秒を残す範囲)に収めてから SnapFrame するので、丸めで下限を
    割り、区間が 0.5 秒より最大で半フレーム短くなることがある(例: 25 fps で下限 0.5 → SnapFrame(0.5) = 偶数丸め(12.5)/25 = 0.48)。
  - `Document.sourceLength`(トリム後の長さ・速度適用前)= 除外していない各区間の [max(start, trimStart), min(end, trimEnd)] の長さの
    合計。`outputLength`(書き出しの長さ)= 同じ重なりの長さを区間ごとに `speed` で割った合計。除外した区間は含めない。
    `sourceLengthClock` / `outputLengthClock` = FormatClock。`regionCount` = 区間数。
  - `Region` の派生: `duration` = end − start、`outputDuration` = speed > 0 なら duration/speed(それ以外 0)、`isNormalSpeed` =
    |speed − 1| < 0.001、`isMuted` = volume < 0.001、`isFullVolume` = |volume − 1| < 0.001、`speedColor`(§2.15 の式)。
- 核/表面: core(出所: authority/Models/DocumentState.cs・RegionData.cs・TimeMath.cs)
- 受入観点: unit・exact(浮動小数の等値・丸めの方向は中点の入力で確かめる)
- 画面: SCR-TIMELINE(EL-TM-REGIONS)・SCR-TRANSPORT(EL-TP-LENGTH-PILL)・SCR-INSPECTOR(EL-INS-AFTER-TRIM・EL-INS-AFTER-SPEED)
- シナリオ: UC-002・UC-004・UC-010・UC-030・UC-034・UC-036・UC-050・UC-051・UC-056・UC-060・UC-061・UC-071・UC-093
- E-BOM 候補: E-DOCMODEL-001
- M-BOM 候補: M-DOCMODEL-001
- Control Plan 候補: CP-DOCMODEL-001

<a id="selection"></a>
### 2.9 編集対象の決まり方 (REQ-026, REQ-027)
- 仕様節ID: SPEC-SELECTION-001
- 振る舞い:
  - 区間を選ぶ専用の操作は無い。`EditSession.selectedRegionId` は次の 4 つで決まる:
    - (a) `playhead` の値が変わったとき: 新しい位置の区間(RegionAt)があり、その ID が今と違えばその ID にする。位置の区間が無い
      (トリムのドラッグで `playhead` がトリム範囲の外に残ったとき)か同じ ID なら変えない。値が変わらない操作(同じ位置への移動)では
      何もしない。
    - (b) 編集対象の再解決(`Document` を変える操作 `DeleteSelectedBoundary`・`SetTrimIn`/`SetTrimOut`・プリセット・トグル・ミュート・
      除外・`Move*`・`Set*Continuous` と `Undo`・`Redo` の後): 再生ヘッドの位置の区間があればその ID、無ければ今の ID がまだ `Document`
      にあればそれ、それも無ければ先頭の区間の ID(区間が無ければ null)。
    - (c) `Split`: (b) の後に新しい後半の ID で上書きする。`playhead` は格子に乗っていないので、分割点が丸めで `playhead` より後ろに
      なると、再生ヘッドは前半にいるのに編集対象は後半になる。このずれは次に `playhead` の値か `Document` が変わるまで続き、その間
      インスペクターは後半を、速度ピルとプレビューの速度フラグ(`activeRegion`)は前半を表す。
    - (d) 読み込み: 先頭の区間の ID。
  - 再生ヘッドを動かす操作(`ToStart`・`ToEnd`・`Scrub`・`StepBack`・`StepForward`・`StepSecondBack`・`StepSecondForward`)は
    `playing` を偽にし、`playhead` を [`trimStart`, `trimEnd`] に収める。`ToStart` = trimStart、`ToEnd` = trimEnd、`StepBack`/
    `StepForward` = (偶数丸め(playhead·fps) ∓/± 1)/fps、`StepSecondBack`/`StepSecondForward` = playhead ∓/± 1。`Scrub` は
    x/`pxPerSec` を [0, `Clip.duration`] に収め、さらに [trimStart, trimEnd] に収める。
- 再現する不具合: 分割直後の編集対象と再生ヘッドの位置の区間のずれ(c)。トリムで再生ヘッドがトリム範囲の外に残ったときインスペクターは
  前の編集対象を出し続ける(UQ-SPEC-008)。
- 核/表面: core(出所: authority/ViewModels/MainWindowViewModel.cs の選択の更新・ResolveSelection)
- 受入観点: unit・exact
- 画面: SCR-INSPECTOR(EL-INS-REGION-*)・SCR-TIMELINE(EL-TM-SELECTED-OUTLINE・EL-TM-PLAYHEAD)・SCR-TRANSPORT(EL-TP-TOSTART・
  EL-TP-TOEND・EL-TP-STEPBACK・EL-TP-STEPFWD)
- シナリオ: UC-001・UC-002・UC-010・UC-011・UC-012・UC-013・UC-015・UC-016・UC-017・UC-019・UC-024・UC-030・UC-034・UC-035・UC-039・UC-055・UC-058
- E-BOM 候補: E-SELECTION-001
- M-BOM 候補: M-SELECTION-001
- Control Plan 候補: CP-SELECTION-001

<a id="playback"></a>
### 2.10 再生 (REQ-028, REQ-029)
- 仕様節ID: SPEC-PLAYBACK-001
- 振る舞い:
  - `TogglePlay`(EL-TP-PLAY・EL-KEY-SPACE・EL-PV-FRAME): 再生中なら `playing` を偽にする。停止中なら、`playhead` が `trimStart` より
    前か `trimEnd` − 0.05 以上なら `trimStart` へ、除外区間の上なら次の除外していない区間の先頭へ(後ろに無ければ最初の除外していない
    位置へ・それも無ければ trimStart へ)移してから `playing` を真にする。再生開始時に `playhead` が画面外なら横スクロールを追従させる
    (§2.15)。実クリップのプレイヤーがあれば、開始時に `PreviewPlayer.rateSentToPlayer`・`volumeSentToPlayer` をその位置の区間の値にする。
  - 再生ヘッドを進めるのは: `PreviewPlayer.externalPlayback` が偽のとき内蔵タイマー `PlaybackTick`(16 ms ごと・dt)で `playhead` +=
    dt·その位置の区間の速度(サンプル・プレイヤーが使えない実ファイル・プレイヤーの準備中の実ファイル。再生を始めた時点で偽なら停止
    するまでタイマー)。真のときは `PlayerTimeChanged`(プレイヤーの時刻 ms・シーク中の到着は判定で捨てることがある)。
  - どちらも、除外区間に入ったら次の除外していない区間の先頭へ飛び、最後の除外していない区間の終わりに達したら最初の除外していない
    位置へ戻って繰り返す(ループ)。再生中の速度はその位置の区間の `speed`、プレビューの音量はその位置の区間の `volume`(×100 を丸めた
    0〜200)。プレイヤーに渡すのは速度と音量だけで、`preservePitch` は渡さない(音の高さは LibVLC の既定のまま・起動の引数は
    --no-osd --quiet だけ。ピッチ維持オフの区間でも書き出しの asetrate と違う音になりうる・UQ-SPEC-009)。
  - `playing` は `TogglePlay` で切り替わり、再生ヘッドを動かす操作・読み込み・`HaltPlayback`(プレイヤーのエラー・再生中の進捗の
    途絶(ウォッチドッグ)・シークのタイムアウト: 目標位置に届かないまま再試行 2 回を超えたとき。再試行の回数はシークを始めるたびと
    一時停止・最初のフレームで 0 に戻る)で偽に戻る。
  - 停止に戻る契機の定数(PreviewView.axaml.cs): 監視は 500 ms ごと。再生中(同期状態 Playing)に採用した時刻の通知が 2000 ms を
    超えて来なければ停止。シークは、通知の時刻と目標の差が 650 ms 以下で到達とみなし、5000 ms で打ち切る。打ち切りのたびに同じ目標へ
    シークし直して期限を 5000 ms 延ばし(最大 2 回)、それを超えたらプレイヤーを一時停止して `HaltPlayback`。時刻の通知 t の後の次の
    再生位置 target(除外の飛び越し・末尾のループ)が t + 0.02 秒より後のとき(または次の再生位置が無いとき)だけシークする。
  - `EditSession.playIcon` は `playing` なら pause、それ以外 play(EL-TP-PLAY)。`showCenterPlayButton` は `playing` でないとき真
    (EL-PV-CENTER-PLAY)。
- 範囲外: プレビューの映像の描画と再生のタイミング(プレイヤーの同期状態の詳細は UQ-SPEC-021)。
- 核/表面: core(出所: authority/ViewModels/MainWindowViewModel.cs の再生・Views/PreviewView.axaml.cs・Services/VlcVideoPlayer.cs)
- 受入観点: unit・exact(開始位置・除外の飛び越し・ループ・渡す速度と音量)/ L1(アイコン・中央の再生ボタン・停止に戻る契機)
- 画面: SCR-TRANSPORT(EL-TP-PLAY)・SCR-PREVIEW(EL-PV-FRAME・EL-PV-CENTER-PLAY)・SCR-MAIN(EL-KEY-SPACE)
- シナリオ: UC-020・UC-021・UC-022・UC-023・UC-024・UC-025・UC-026
- E-BOM 候補: E-PLAYBACK-001
- M-BOM 候補: M-PLAYBACK-001
- Control Plan 候補: CP-PLAYBACK-001

<a id="transport"></a>
### 2.11 トランスポート (REQ-030, REQ-031, REQ-032)
- 仕様節ID: SPEC-TRANSPORT-001
- 振る舞い:
  - 左から「先頭へ」(EL-TP-TOSTART → `ToStart`)・「1 フレーム戻る」(EL-TP-STEPBACK → `StepBack`)・「再生/一時停止」(EL-TP-PLAY →
    `TogglePlay`)・「1 フレーム進む」(EL-TP-STEPFWD → `StepForward`)・「末尾へ」(EL-TP-TOEND → `ToEnd`)、タイムコード(EL-TP-TIMECODE)
    と単位表示、右に現在速度のピル(EL-TP-SPEED-PILL)と書き出しの長さのピル(EL-TP-LENGTH-PILL)。
  - ツールチップ: 「To start」/「Step back 1 frame  (← / ,)」(括弧の前は空白 2 個)/「Play / Pause (Space)」/
    「Step forward 1 frame  (→ / .)」(空白 2 個)/「To end」。ja も「1フレーム戻る  (← / ,)」「1フレーム進む  (→ / .)」と空白 2 個。
  - タイムコード: `EditSession.playheadTimecode` = FormatTimecode(playhead, Clip.fps)「/」`Clip.durationTimecode` =
    FormatTimecode(Clip.duration, Clip.fps)(分母はトリム後ではなくクリップの長さ)。単位表示は「h:m:frame」(ja: 時:分:フレーム)。
    単位表示の文言と実際の書式(分:秒:フレーム)は食い違うが、文言はそのまま再現する(UQ-SPEC-010)。
  - 現在速度のピル: `speedNowText` = FormatSpeed(`speedNow`) + "x"(`speedNow` = `activeRegion.speed`、無ければ 1)。ツールチップ
    「Playback speed」。
  - 書き出しの長さのピル: `Document.exportLengthPillText` =「Export length {sourceLengthClock} → {outputLengthClock}」。ツールチップ
    「Trimmed length → export length after speed」。
- 核/表面: core(出所: authority/Views/TransportView.axaml・Models/TimeMath.cs)
- 受入観点: unit・exact(書式)/ L1(並び・ツールチップの文言の完全一致)
- 画面: SCR-TRANSPORT(全 8 部品)
- シナリオ: UC-001・UC-002・UC-015・UC-016・UC-018・UC-020・UC-036・UC-059・UC-142
- E-BOM 候補: E-TRANSPORT-001
- M-BOM 候補: M-TRANSPORT-001
- Control Plan 候補: CP-TRANSPORT-001
- 表示契約:
  - 原典参照: authority/Views/TransportView.axaml
  - 提示要素: 5 つのボタンとツールチップ・タイムコード・単位表示・速度のピル・書き出しの長さのピル
  - 対象外要素: なし

<a id="preview"></a>
### 2.12 プレビュー (REQ-033, REQ-034, REQ-035)
- 仕様節ID: SPEC-PREVIEW-001
- 振る舞い:
  - 映像枠(EL-PV-FRAME): 利用できる領域の中に、`PreviewPlayer.frameAspect`(= `Clip.aspectRatio`。height > 0 なら width/height、
    それ以外 16/9)を保った最大の大きさで中央に置く(`frameWidth`・`frameHeight` は px の切り捨て)。計算し直すのは `LayoutChanged`
    (利用できる領域の大きさが変わったとき)と `PlayerClipLoaded`(プレイヤーに実クリップを読み込んだとき)だけ。`playerAvailable` が
    偽のときは読み込みで計算し直さないので、領域の大きさが変わるまで前の縦横比のまま。枠の左クリックは `TogglePlay`。
  - 実映像が無い間(読み込み中・サンプル・プレイヤーが使えない)は `sceneVisible` が真で、場面(EL-PV-SCENE)= 上から下への線形
    グラデーション #26303A(0)→ #0E1116(1)を映像の上に出す。
  - 停止中(`showCenterPlayButton`): 枠全体に OverlayBlack18 の暗幕(押下を通す)をかけ、中央に 64×64 の丸(White12・縁 White18 1 px)と
    白の再生アイコン(26 px)を出す(EL-PV-CENTER-PLAY)。
  - 速度フラグの見た目: OverlayBlack50 の背景・White10 の縁 1 px・角丸 8・余白 10,6・右上から 12,12。中身は間隔 7 で gauge アイコン
    (14・Text)・`speedNowText`(太字 12・Text)・音符アイコン(13・`activePitchColor`)。バッジの見た目: OverlayBlack50・White08 の縁 1 px・
    角丸 7・余白 9,5・左下から 14,12。`playheadTimecode`(等幅 12・Text)と「/ {durationTimecode}」(等幅 12・Text4)を間隔 4。
  - プレイヤー: `PlayerInitialized`(背景での準備の完了)で `playerAvailable` を設定し、保留中の実クリップがあれば読み込む。
    `PlayerClipLoaded`: 使えれば `externalPlayback` を真・シーンを表示・映像枠を計算し直す。使えなければ `externalPlayback` を偽。
    `PlayerFrameReady`(最初のフレーム): シーンを隠し(`sceneVisible` = false)、同期の状態が Priming で、かつ `playing` が偽のときだけ、
    トリム開始の位置へシークしてから一時停止する(この順。自動で再生しない)。準備中に再生が始まっていれば(`playing` が真)止めない。
    停止中に `playhead` が動くと、プレビューはその位置を表示する。
  - 速度フラグ(EL-PV-SPEED-FLAG・右上): `showSpeedFlag` = |speedNow − 1| > 0.001 のときだけ。速度アイコン・`speedNowText`・音符
    アイコン。音符の色 `activePitchColor` は `activeRegion.preservePitch`(無ければ true)なら accent-text #8EC1FF、偽なら warn #E5A14B。
  - タイムコードのバッジ(EL-PV-TIMECODE・左下・常に): `playheadTimecode` / `Clip.durationTimecode`。
- 範囲外: 映像の描画内容と同期のタイミング。
- 表示契約:
  - 原典参照: authority/Views/PreviewView.axaml
  - 提示要素: 映像枠・場面の背景(縦のグラデーション #26303A → #0E1116)・停止中の暗幕と中央の再生ボタン・右上の速度フラグ・
    左下のタイムコードのバッジ(重なり順は 映像 → 場面 → 速度フラグ → バッジ → 暗幕)
  - 対象外要素: 映像の内容(範囲外)
- 核/表面: core(出所: authority/Views/PreviewView.axaml・PreviewView.axaml.cs)
- 受入観点: L2・exact(枠の寸法の計算・再計算の契機は実機)/ L1(速度フラグ・バッジ)
- 画面: SCR-PREVIEW(全 5 部品)
- シナリオ: UC-011・UC-021・UC-090・UC-142
- E-BOM 候補: E-PREVIEW-001
- M-BOM 候補: M-PREVIEW-001
- Control Plan 候補: CP-PREVIEW-001

<a id="toolbar"></a>
### 2.13 ツールバーと区間の編集 (REQ-036, REQ-037, REQ-038, REQ-039)
- 仕様節ID: SPEC-TOOLBAR-001
- 振る舞い:
  - 並び: 左に「Open」(EL-TL-OPEN)、区切り線、元に戻す(EL-TL-UNDO)・やり直す(EL-TL-REDO)(アイコン)、区切り線、「Split」(EL-TL-SPLIT)・
    「Merge」(EL-TL-MERGE)、区切り線、「Set In」(EL-TL-SETIN)・「Set Out」(EL-TL-SETOUT)、右端に主ボタン「Export」(EL-TL-EXPORT →
    `ShowExportDialog`)。区切り線は 3 本(幅 1・高さ 22・LineSoft・左右の余白 6)。Open 以外はクリップがあるとき表示(常に有る)。
  - 押せる条件: 元に戻す = `History.canUndo`、やり直す = `canRedo`、Split = `EditSession.canSplit`、Merge = `canDeleteBoundary`、
    Set In = `canSetTrimIn`、Set Out = `canSetTrimOut`。
  - ツールチップ: Undo / Redo / Split the region at the playhead (S) / Merge the current region with the one before it /
    Set the trim start (In) to the playhead (I) / Set the trim end (Out) to the playhead (O)。ja は resx の値(区間を分割・分割を解除・
    開く 等)。
  - `canSplit`: 丸める前の `playhead` の位置の区間 r があり、playhead ∈ (r.start + 0.5, r.end − 0.5)(開区間)。
  - `Split`(EL-TL-SPLIT・EL-KEY-S): ph = SnapFrame(playhead)。ph の位置の区間を選び直し、ph が [その区間の start + 0.5, end − 0.5]
    (閉区間)の外なら何もしない(ちょうど start + 0.5 なら分割する)。前半は元の ID、後半は `nextRegionId`。両方とも speed・
    preservePitch・excluded・volume を引き継ぐ。`nextRegionId` を 1 増やす(元に戻すでは戻らない)。編集対象は後半(§2.9 (c))。
    履歴に 1 件。`edited` を真。
  - `canDeleteBoundary`: 編集対象の区間の位置 > 0。`DeleteSelectedBoundary`(Merge・ja: 分割を解除): 編集対象とその前の区間を 1 つに
    する。結果は前の区間の id・speed・preservePitch・excluded・volume を持ち、end は編集対象の end。編集対象を再解決。履歴に 1 件。
  - `canSetTrimIn`: playhead ∈ [先頭区間の start, 先頭区間の end − 0.5]。`SetTrimIn`(EL-TL-SETIN・EL-KEY-I): `trimStart` と先頭区間の
    start を SnapFrame(playhead) にする(実行はボタン・キーとも、先頭で `canSetTrimIn` が偽なら何もしない)。`canSetTrimOut`: playhead ∈ [末尾区間の start + 0.5, 末尾区間の end]。`SetTrimOut`
    (EL-TL-SETOUT・EL-KEY-O): `trimEnd` と末尾区間の end を SnapFrame(playhead) にする(先頭で `canSetTrimOut` が偽なら何もしない)。どちらも差が 1e-6 未満なら何もしない
    (記録もしない)。変わったときだけ履歴に 1 件。`playhead` は動かさない。
  - 履歴に記録する操作はすべて `edited` を真にする(§2.18)。
- 核/表面: core(出所: authority/Views/ToolbarView.axaml・Models/DocumentState.cs・ViewModels/MainWindowViewModel.cs)
- 受入観点: unit・exact(押せる条件の境界・分割の丸め・ID)/ L1(並びとツールチップ)
- 画面: SCR-TOOLBAR(全 8 部品)・SCR-MAIN(EL-KEY-S・EL-KEY-I・EL-KEY-O)
- シナリオ: UC-003・UC-030・UC-031・UC-032・UC-033・UC-034・UC-036・UC-037・UC-038・UC-040・UC-050・UC-051・UC-052・UC-053・UC-230
- E-BOM 候補: E-TOOLBAR-001
- M-BOM 候補: M-TOOLBAR-001
- Control Plan 候補: CP-TOOLBAR-001
- 表示契約:
  - 原典参照: authority/Views/ToolbarView.axaml
  - 提示要素: 8 つのボタン・区切り線 3 本・ツールチップ・無効の表示
  - 対象外要素: なし

<a id="timeline-edit"></a>
### 2.14 タイムラインの編集操作 (REQ-040, REQ-041, REQ-042, REQ-043)
- 仕様節ID: SPEC-TLEDIT-001
- 振る舞い:
  - 押下の振り分け(左ボタン): 縦位置がトラック上端(30 px)より上のルーラー帯(EL-TM-RULER)なら `Scrub`。縦位置 30 px 以上(トラックの
    矩形 30〜122 px と、その下の高さ 16 px の余白のすべて)では、トリム開始ハンドルから 7 px 以内なら `BeginTrimStartDrag`
    (EL-TM-TRIMSTART-HANDLE)、次にトリム終了ハンドルから 7 px 以内なら `BeginTrimEndDrag`(EL-TM-TRIMEND-HANDLE)、次に内部の境界から
    7 px 以内(先頭側から最初に見つかったもの)なら `BeginBoundaryDrag`(EL-TM-BOUNDARY・param = 境界の番号 i)、それ以外は `Scrub`
    (EL-TM-TRACK-SCRUB)。`TimelineView.dragMode` を Scrub / TrimStart / TrimEnd / Boundary にする。押したままの移動でその操作を続け
    (`Scrub` の繰り返し・`MoveTrimStart`・`MoveTrimEnd`・`MoveBoundary`)、離すと `ReleaseTimelinePointer` で `dragMode` = None。
  - `Begin*Drag` は押した時点で履歴に 1 件記録し `edited` を真にする(`Document` は変えない。押して離すだけでも記録と未保存の変更は残る)。
    移動は記録しない(1 回のドラッグの記録は押下の 1 件だけ)。
  - `MoveTrimStart`(EL-TM-TRIMSTART-MOVE): `trimStart` と先頭区間の start を SnapFrame(t を [0, 先頭区間の end − 0.5] に収めた値)にする。
    `MoveTrimEnd`(EL-TM-TRIMEND-MOVE): `trimEnd` と末尾区間の end を SnapFrame(t を [末尾区間の start + 0.5, Clip.duration] に収めた値)に
    する。トリムは内部の境界をまたげない(UQ-SPEC-007)。`playhead` は動かさない(トリム範囲の外に取り残されることがある・§2.9)。
  - `MoveBoundary`(EL-TM-BOUNDARY-MOVE): 境界 i を SnapFrame(t を [区間 i の start + 0.5, 区間 i+1 の end − 0.5] に収めた値)へ動かし、両側の
    区間を同時に変える。
  - どの移動も編集対象を再解決し、`edited` を真にする。収めてから丸めるので区間が 0.5 秒をわずかに割ることがある(§2.8)。
  - ホバー(ドラッグしていないとき・`HoverTimeline` / EL-TM-HOVER): 縦位置 30 px 以上でトリムハンドルか内部の境界から 7 px 以内なら
    `TimelineView.cursor` = SizeWestEast(EL-TM-CURSOR)、それ以外 Arrow。トリムハンドルから 7 px 以内でなく境界の上なら `hoverBoundary` =
    その境界(accent-text 色の縦の帯の掴みの表示・EL-TM-BOUNDARY-LINES)、それ以外 −1(ハンドルが優先)。ルーラー帯では通常のカーソル。
    `LeaveTimeline`(EL-TM-LEAVE): `hoverBoundary` = −1・`cursor` = Arrow。
- 核/表面: core(出所: authority/Controls/TimelineControl.cs)
- 受入観点: unit・exact(収める範囲と丸め・振り分けの優先順・記録の件数)/ L1(押下の振り分け)/ L2(カーソルと掴みの表示)
- 画面: SCR-TIMELINE(EL-TM-RULER・EL-TM-TRACK-SCRUB・EL-TM-TRIMSTART-HANDLE・EL-TM-TRIMEND-HANDLE・EL-TM-BOUNDARY・
  EL-TM-TRIMSTART-MOVE・EL-TM-TRIMEND-MOVE・EL-TM-BOUNDARY-MOVE・EL-TM-RELEASE・EL-TM-HOVER・EL-TM-LEAVE・EL-TM-CURSOR)
- シナリオ: UC-010・UC-011・UC-013・UC-014・UC-054・UC-055・UC-056・UC-057・UC-058・UC-059・UC-060・UC-061・UC-062・UC-063
- E-BOM 候補: E-TLEDIT-001
- M-BOM 候補: M-TLEDIT-001
- Control Plan 候補: CP-TLEDIT-001

<a id="timeline-view"></a>
### 2.15 タイムラインの表示 (REQ-044, REQ-045, REQ-046, REQ-047, REQ-048, REQ-049, REQ-093)
- 仕様節ID: SPEC-TLVIEW-001
- 振る舞い:
  - 見出し行: 「Timeline」(ja: タイムライン)と `Document.timelineSummary`「{regionCount} regions · trim {FormatClock(trimStart)}–
    {FormatClock(trimEnd)}」(EL-TM-SUMMARY)、右端にズームアウト(EL-TM-ZOOMOUT・ツールチップ「Zoom out」)とズームイン
    (EL-TM-ZOOMIN・「Zoom in」)。サムネイル生成の進捗「Generating thumbnails {N}/{M}」(EL-TM-THUMB-PROGRESS)は作り込むが、表示の
    条件 `MediaPreviewData.thumbnailsRefining` が真になる経路が無いので表示されない(読み込みで false に戻すだけ)。
  - ズーム: `TimelineView.pxPerSec` の既定 8.5。`ZoomIn` で ×1.4、`ZoomOut` で ÷1.4、[4, 120] に収める(読み込みでは戻らない)。
    `contentWidth` = Clip.duration·pxPerSec + 48(EndPad)。タイムラインの本体は ScrollViewer(Padding="16,0,16,0")の中にあり、最大
    スクロール = max(0, Extent − Viewport)(Extent・Viewport は ScrollViewer の値)。元のアプリの注記では横の Padding 32 px が Extent を
    縮めるので EndPad 48(32 + ハンドルの余裕 16)で補っている(Avalonia の既定の動作・UQ-SPEC-031)。本書の viewportWidth は Viewport の幅。ズームの横スクロール: 表示幅・
    新旧の倍率・長さのどれかが 0 以下なら動かさない。最大が 0 なら 0。それ以外は、基準(再生ヘッドが画面内 [0, 表示幅] にあれば
    再生ヘッドの時刻とその画面位置、無ければ画面中央の時刻と 表示幅/2)をズーム後も同じ画面位置に置く値を [0, 最大] に収める(差が
    0.5 px 未満なら動かさない)。`LayoutChanged` が `viewportWidth` を更新する。
  - 再生中の追従(`TogglePlay` の開始・`PlaybackTick`・`PlayerTimeChanged`): ドラッグ中・表示幅 0・最大 0 なら動かさない。再生ヘッドの
    x が scrollOffset + 表示幅·0.92 を超えるか scrollOffset より左なら、x − 表示幅·0.12 を [0, 最大] に収めた値にする(差が 1 px 未満なら
    動かさない)。
  - ルーラー: `rulerStep` = 70/pxPerSec 以上で最小の {0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300} 秒(どれも足りなければ 600)。0 秒から
    長さまで目盛りと FormatClock のラベル。目盛りは各時刻の x で (x, 8)〜(x, 22) の縦線、ラベルは左上を (x + 5, 1) に置く。
  - スクロール(EL-TM-SCROLL → `ScrollTimeline`): 横スクロールだけ(縦スクロールは無効)。横スクロールバーは自動では隠れない
    (AllowAutoHide=False・内容が収まらないときに表示)。ポインタが乗っていないときは細い表示(サムを Fluent 既定の細表示に縮小・
    トラックとボタンは透明)、乗ったときだけ太い表示。スクロールバーは自分の行を占め、内容に重ならない。
  - トラックの描画(EL-TM-REGIONS ほか。描く順・後ろほど上): ルーラー → トラックの背景 → サムネイル(§2.16)→ 波形 → ミュート表示 →
    速度の塗りとラベル → 除外のマスク → トリム外のマスク → 編集対象の枠 → 境界 → トリムハンドル → コピーのリード → 再生ヘッド。
    - 色と線幅の表(REQ-048 の完全一致の対象。トークンのあるものは名前も示す。authority/Controls/TimelineControl.cs の定数):
      トラックの背景 Surface #171A1E・縁 LineSoft #24272B 1 px・角丸 10(トラックの幅が 12000 px 以下のとき。中身は角丸でクリップ。12000 px を
      超えるときは角丸の背景と縁を描かず、可視範囲だけを Surface で塗り、上下の辺に LineSoft 1 px の線、トラックの両端が可視範囲にあればその
      位置に上下 10 px 内側までの LineSoft 1 px の縦線を引き、中身は可視範囲の矩形でクリップする・DrawTrackShell)/ ルーラーの目盛り LineSoft #24272B 1 px(y 8〜22・RulerH = 22。トラックの上端は 30)・ラベル Text4
      #5A5E63(JetBrains Mono 10・左上 (x + 5, 1))/ 波形 Wave #8CBCC5D1 / ミュートの覆い #D0171A1E(トークンなし・アルファ 0xD0 で不透明ではない)・平らな線
      Warn #E5A14B 1.5 px / ラベルの背景 OverlayBlack42 #6B000000(角丸 7)・文字 Text #F2F4F6(Manrope 11.5)・「♪off」とミュートの
      アイコン Warn #E5A14B / 除外のマスクとトリム外のマスク TrimMask #BD050608・除外の取り消し線 Text3 #7C8186 1.5 px(丸い端)/
      区切り線と上端の刻み #80FFFFFF(トークンなし)線幅 1.5・刻みは幅 3・高さ 5 / 掴みの帯 AccentText #8EC1FF(幅 3・トラック高の 60%)/
      編集対象の枠 Accent #579BF4 2 px・角丸 4 / トリムハンドル Accent #579BF4 の塗り・縁 Text #F2F4F6 1.25 px・横線 Text #F2F4F6 1.4 px・
      角丸 3 / コピーのリードの帯 #33E5A14B(トークンなし)・破線 Warn #E5A14B 1.5 px(3・3)/ 再生ヘッド Text #F2F4F6 2 px と 13×13・
      角丸 4 のマーカー / サムネイルの目地 #0A0B0D。本書の「白」はこの Text #F2F4F6(純白ではない)。
    - 速度の塗り: `isNormalSpeed` でなく除外していない区間に `Region.speedColor`(不透明度 0.34)。speedColor: d = log2(speed)(speed ≤ 0
      なら 1 とみなす)、L = clamp(0.42 + 0.07d, 0.30, 0.62)、C = clamp(0.05 + 0.07|d|, 0.04, 0.16)、H = d ≥ 0 なら 256 − 14d、それ以外
      256 + 6|d| の OKLCH を、トークンと同じ変換(authority/Util/OklchColor.cs)で sRGB にしたもの。
    - ラベル(EL-TM-REGION-LABEL): 除外していない区間で、幅 rw > 44 px かつ labelX = max(区間の左端 + 8, 描画範囲の左端 + 8)(描画範囲の
      左端 = max(0, scrollOffset − 400 px))が 区間の右端 − 44 より左のとき(区間の左端が描画範囲の中にあれば幅が 52 px を超えるとき)。
      速度アイコン+「{FormatSpeed(speed)}x」、preservePitch が偽かつ速度 ≠ 1 なら「♪off」(warn 色)、ミュートならスピーカー×アイコン
      (warn 色)。
    - 境界(EL-TM-BOUNDARY-LINES): 内部の境界ごとに区切り線と上端の小さな刻み。`hoverBoundary` の境界に accent-text 色の縦の帯。
    - トリム外のマスク(EL-TM-TRIM-MASK): トリム範囲の外に暗いマスク(TrimMask)。
    - 除外(EL-TM-EXCLUDED-MASK): 除外した区間はトリム外と同じ色の暗いマスクと左下から右上への斜めの取り消し線(タイムラインに残す)。取り消し線は
      見えている幅が 10 px を超えるときだけ、(左 + 4, 下 − 6) から (右 − 4, 上 + 6) へ引く(マスクは幅に関わらず塗る)。
    - ミュート(EL-TM-MUTED-AUDIO): 除外していないミュートの区間は、`showWaveform` のとき波形の帯を #D0171A1E(半透明)で覆い、帯の中央に warn 色の
      平らな線(1.5 px・丸い端・帯の見えている幅が 6 px を超えるときだけ・左右 2 px 内側まで)。覆いは幅に関わらず塗る。
    - 編集対象の枠(EL-TM-SELECTED-OUTLINE): accent 色 #579BF4 の 2 px の枠。
    - トリムハンドル(EL-TM-TRIM-HANDLES): trimStart・trimEnd の位置に幅 7 px・トラック高の 66%・縦中央・accent 色の角丸の棒に白の縁取りと
      中央の短い横線 2 本。
    - コピーのリード(EL-TM-COPYCUT-MARKER): `ExportJob.showCopyCutMarker` のときキーフレームの位置の破線とリードの帯(§2.20)。
    - 再生ヘッド(EL-TM-PLAYHEAD): Text #F2F4F6 の線と上端のマーカー。
- 核/表面: core(出所: authority/Controls/TimelineControl.cs・Views/TimelineView.axaml・Util/SpeedColor.cs・OklchColor.cs)
- 受入観点: unit・exact(ズーム・追従・ルーラー・色の式)/ L2(描画要素の有無と色の値は完全一致・位置は pixel-exact でない・REQ-048)/
  L1(見出し)
- 画面: SCR-TIMELINE(EL-TM-SUMMARY・EL-TM-THUMB-PROGRESS・EL-TM-ZOOMOUT・EL-TM-ZOOMIN・EL-TM-SCROLL・EL-TM-RULER・EL-TM-REGIONS・
  EL-TM-REGION-LABEL・EL-TM-EXCLUDED-MASK・EL-TM-MUTED-AUDIO・EL-TM-TRIM-MASK・EL-TM-SELECTED-OUTLINE・EL-TM-BOUNDARY-LINES・
  EL-TM-TRIM-HANDLES・EL-TM-PLAYHEAD・EL-TM-COPYCUT-MARKER)
- シナリオ: UC-026・UC-030・UC-037・UC-050・UC-064・UC-065・UC-070・UC-071・UC-085・UC-092・UC-093・UC-094・UC-140・UC-174
- E-BOM 候補: E-TLVIEW-001
- M-BOM 候補: M-TLVIEW-001
- Control Plan 候補: CP-TLVIEW-001
- 表示契約:
  - 原典参照: authority/Controls/TimelineControl.cs・Views/TimelineView.axaml・docs/images/02-overview.png
  - 提示要素: 見出し・要約・ズームの 2 ボタン・ルーラー・区間の塗りとラベル・境界・マスク・枠・ハンドル・リード・再生ヘッド・スクロールバー
  - 対象外要素: サムネイル進捗の文言(到達しない・作り込みのみ)

### 2.16 サムネイル・波形・キャッシュ (REQ-050, REQ-051, REQ-052, REQ-053, REQ-054, REQ-055)
- 仕様節ID: SPEC-MEDIA-001(要求の trace は #timeline-view)
- 振る舞い:
  - 表示(EL-TM-THUMBNAILS・EL-TM-WAVEFORM): `MediaPreviewData.showThumbnails` と `showWaveform` は常に真(切り替える UI は無い)。
    実データが届くまでは、サムネイルの代わりに色のグラデーションのブロック、波形の代わりに擬似の波形を描く。
    - 代わりのブロック: max(6, 偶数丸め(全幅/120)) 個の等幅。i 番目(p = i/個数)は上 OKLCH(0.45, 0.10, 250 + 90p)・下
      OKLCH(0.26, 0.07, 210 + 110p)(どちらも不透明度 0.42)の、(0, 0) から (0.3, 1) への線形グラデーション。
    - 実サムネイルのコマは縦横比を保ち、幅 = トラック高 92 px × 縦横比。
    - 全体のフィルムストリップ(`filmstrip`・キャッシュにあったもの): コマ幅の格子(描画範囲の左端を格子に切り下げた位置から)にコマを
      並べ、各コマにはコマの中心の時刻に最も近いサムネイルを使い、不透明度 0.5 で描く(`filmstripApproximate` は常に偽なので 0.4 の
      経路は到達しない・UQ-SPEC-011)。目地は幅 3 px の #0A0B0D を不透明でコマ幅ごと。
    - 可視範囲のサムネイル(`visibleThumbnails`): 各サムネイルの時刻を中心にコマを置いて不透明で描き、目地は幅 2 px の #0A0B0D を各コマの
      右端。全体のフィルムストリップが無いときは代わりのブロックの上に重ねる。
    - 波形: クリップ全長を等分したバケットごとの最小/最大の包絡を、トラック下部の高さ 38 px の帯に描く。
  - サムネイルの生成(`RequestVisibleTimelinePreview`): 読み込み時に動画全体を読まず、見えている範囲だけを生成する。要求の契機は
    タイムラインの描画のたびで、描画の最初に可視範囲を最新にしてから (max(0, 可視左端)/pxPerSec, min(長さ, 可視右端/pxPerSec),
    pxPerSec) で要求する(可視右端は 全幅 + 右端の余白 で頭打ち)。再生が止まったときはタイムラインを再描画するので、それも契機になる
    (再生中に取りこぼした分を補う。再生の開始では再描画せず再生ヘッドの追従だけ)。以下の条件で要求は実際の生成にならないことがある。働くのは、
    サムネイルを表示し、`filmstrip` が無く、可視範囲の終了 > 開始 かつ pxPerSec > 0 のとき。間隔 sp' = clamp(164/pxPerSec, 0.75, 30)。
    範囲 = 描画範囲(左端 max(0, scrollOffset − 400 px)・右端 min(全幅 + 右端の余白, scrollOffset + 表示幅 + 400 px) を秒にし、右端は
    長さで頭打ち)の前後に 2·sp' を足して [0, 長さ] に収めたもの。前回 `lastVisibleRequest` [S, E]・sp があり、開始 ≥ S − sp'・
    終了 ≤ E + sp'・sp' ≥ 0.85·sp なら再要求しない。それ以外は bucket = max(sp', 1) として開始を floor(開始/bucket)·bucket、終了を
    ceil(終了/bucket)·bucket に揃え、`lastVisibleRequest` をその範囲と sp' にし、要求(高さ 96 px・1 回で最大 36 枚・180 ms まとめてから
    実行)をキューへ入れる。再生中も生成する。
    抜き出す時刻(BuildVisibleThumbnailTimes): 範囲を [0, 長さ] に収め(終了 ≤ 開始なら 0 枚)、間隔を [0.5, 120] に収め、枚数 =
    clamp(ceil(範囲/間隔), 1, 36)、実際の間隔 = 範囲/枚数、時刻 i = clamp(開始 + 実際の間隔·(i + 0.5), 0, 長さ)。各時刻のキャッシュの
    ファイルは `<root>/<キー>/thumbs-visible/h96/t{ms:12 桁 0 埋め}.jpg`(ms = 偶数丸め(max(0, 時刻)·1000))。ファイルがあれば
    それを使い、無いものだけを生成する(オンラインのみのファイルでは生成しない)。生成: 範囲を [0, 長さ] に収めた窓が 0 秒を超え 30 秒
    以下で、未生成が 2 枚以上なら、1 回の ffmpeg でまとめて抜き出す(-ss 最初の時刻・-t 枚数·間隔・-vf fps=1/間隔,scale=-2:96・
    -q:v 5・打ち切り 30 秒・失敗は無視し、生成されたフレームを時刻の順に 1 対 1 で対応づける)。まとめて抜き出さなかったとき、また
    取りこぼした分は、1 枚ずつ(-ss 時刻・-frames:v 1・scale=-2:96・-q:v 5・最大 2 並列・1 枚 12 秒の打ち切り)で埋める。どちらも
    一時ファイルに書いてから置き場へ移す。秒の引数は小数 6 桁まで・カルチャ不変。終わったらキーのフォルダの更新時刻を今にする。
    結果は時刻の順。`VisibleThumbnailsGenerated`(要求がまだ最新で filmstrip が無いとき)で `visibleThumbnails`
    にし、ディスクキャッシュに書く。`CachedThumbnailsLoaded`(キャッシュの全体のフィルムストリップ)で `filmstrip`・`filmstripInterval`
    を設定し、1 枚以上あれば `visibleThumbnails` を捨てる(以後は可視範囲の生成をしない)。
  - 波形の生成: 読み込みの後、キャッシュの全体のフィルムストリップの読み出し(EmitCachedThumbnailsAsync)を待ってから、波形の要求を
    キューへ入れる(優先度 Waveform・サムネイルより低い)。読み出しが取り消し以外の例外で失敗したときは要求を入れない(擬似の波形のまま)。
    1200 ms の待ちは、作業者がその要求を実行し始めたときに始まる(作業者は 1 つで、優先度の高い要求が先に処理されるので、読み込みからの
    時間は 1200 ms より長くなりうる。待ちの間も作業者は占有される)。バケット数 = clamp((int)(長さ·40),
    1000, 16000)(int への切り捨て・authority/Services/MediaPreviewService.cs#BucketsFor・UQ-SPEC-012)。`WaveformGenerated` で
    `waveform` にし、メモリ(`waveformMemoryCache`・アプリ終了まで残る)とディスクのキャッシュに入れる。失敗・音声なし(`Clip.hasAudio`
    が偽なら生成しない)は擬似の波形のまま。新しいクリップの読み込みで生成中のものは捨てる。
  - オンラインのみのファイル(`Clip.isOnlineOnly`: ファイルの属性 Offline・RECALL_ON_OPEN・RECALL_ON_DATA_ACCESS のいずれか)の間は、
    サムネイル・波形・キーフレームを新しく生成・解析しない。既存のディスクキャッシュ(可視範囲のサムネイル・全体のサムネイル列・
    波形 wave2.bin)とメモリの波形キャッシュは読んで表示し、キーフレームも覚えている値があれば返す。再生と ffprobe のメタ情報の解析は行う。
  - ディスクキャッシュ(`DiskCache`): `root` = `%LOCALAPPDATA%\MoviePad\Cache`(MOVIEPAD_CACHE_DIR があればそこ)、`entries` = `<キー>`
    のフォルダ。キー = SHA1(UTF-8 の「{パス}|{サイズ(バイト)}|{更新時刻 UTC の Ticks}」)の 16 進(大文字)の先頭 16 文字(ファイル
    情報が読めなければサイズと Ticks は 0)。キーのフォルダの中身: thumbs-visible/h96/t*.jpg(可視範囲のサムネイル)・thumbs2/t*.jpg
    (全体のフィルムストリップの正確版)・thumbs2-fast/t*.jpg(高速版)・wave2.bin(波形)。全体のフィルムストリップは thumbs2 を先に、
    無ければ thumbs2-fast を読み(この版は新しく作らない)、`filmstripInterval` = 長さ/枚数。MOVIEPAD_CACHE_DIR は空白だけなら無視。読み込みのたびに、全体が `sizeLimit` 1 GiB を超えていれば、フォルダの
    更新時刻の古い順に削除して 1 GiB 以下にする。
  - キュー(`MediaJobQueue`): 単一の作業者。`pending` の中から優先度の高いもの(シーク用のサムネイル → 可視範囲のサムネイル → 波形 →
    アイドルのキャッシュ・同じ優先度は先着順)を `MediaJobCompleted` の後に `running` にする。実行中は横取りしない(波形の要求が実行中
    — 1200 ms の待ちを含む — の間は、後から来た可視範囲のサムネイルはその完了を待つ)。失敗した要求は無視して次へ。ffmpeg は優先度
    BelowNormal で動かす。同じ種類の要求は最新の 1 件だけ残す。新しいクリップの読み込みでキューの要求をすべて取り消す。
- 核/表面: core(出所: authority/Services/MediaPreviewService.cs・MediaJobQueue.cs・Controls/TimelineControl.cs・Util/Waveform.cs)
- 表示契約:
  - 原典参照: authority/Controls/TimelineControl.cs・docs/images/02-overview.png
  - 提示要素: 代わりのグラデーションのブロック・全体のフィルムストリップのコマと目地(3 px)・可視範囲のサムネイルのコマと目地(2 px)・
    擬似の波形・実波形(Wave #8CBCC5D1・高さ 38 px の帯)・ミュートの覆いと平らな線(§2.15)
  - 対象外要素: サムネイル生成の進捗の文言(到達しない・§2.15)・近似版の不透明度 0.4(到達しない・UQ-SPEC-011)
- 受入観点: unit・exact(要求の範囲・再要求の判定・バケット数・キューの順序・キャッシュの削除)/ L2(描画とオンラインのみの扱い)
- 画面: SCR-TIMELINE(EL-TM-THUMBNAILS・EL-TM-WAVEFORM・EL-TM-MUTED-AUDIO)
- シナリオ: UC-140(出来事が要るので多くは手順に書けない・UQ-SPEC-022)
- E-BOM 候補: E-MEDIA-001
- M-BOM 候補: M-MEDIA-001
- Control Plan 候補: CP-MEDIA-001

<a id="inspector"></a>
### 2.17 インスペクター (REQ-056 〜 REQ-070)
- 仕様節ID: SPEC-INSPECTOR-001(区間の情報と編集・REQ-056〜066)・SPEC-INSPECTOR-002(出力解像度と fps・REQ-067〜070)
- 振る舞い(SPEC-INSPECTOR-001):
  - 配置: ウィンドウの右側の幅 320 px の列(タイトルバーの下の全高)。上部はスクロールする領域(EL-INS-SCROLL → `ScrollInspector`・
    `InspectorView.scrollOffset`)で編集対象の区間の情報と設定、下部には常に書き出し設定(After trim / After speed)・出力解像度・出力
    フレームレートを固定して表示する。
  - 区間の情報(`EditSession.hasSelection` が真のとき): 「Region at playhead」(ja: 再生位置の区間)、速度の色の見本
    (EL-INS-REGION-SWATCH・`selectedSwatchColor` = 速度 ≠ 1 なら `speedColor` を不透明で、1 なら surface-3 #2A2E33)、`regionTitle`
    「Region {位置 + 1} / {regionCount}」(EL-INS-REGION-TITLE)、`regionStartTimecode`・`regionEndTimecode`(M:SS:FF・EL-INS-REGION-START /
    EL-INS-REGION-END)、`regionDurationClock`(M:SS・EL-INS-REGION-DURATION)。
  - `hasSelection` が偽のときは上部に代わりにクリップ情報(「Clip info」・`Clip.fileName`(EL-INS-CLIP-NAME)・`originalResolutionText`
    「W×H」(EL-INS-CLIP-RESOLUTION)・`Clip.fpsText`「{fps} fps」(EL-INS-CLIP-FPS)・`Clip.durationTimecode`(EL-INS-CLIP-DURATION)・
    `Clip.codecText`「映像 · 音声」(EL-INS-CLIP-CODEC))を出す。編集対象の再解決は常に先頭区間へ落ちるので到達しない(作るかは
    UQ-SPEC-013)。
  - 再生速度の欄: 数値 `selectedSpeedText`(大きな文字・`selectedSpeedColor` = 速度 ≠ 1 なら accent-text #8EC1FF、それ以外 text #F2F4F6)と
    「x」(EL-INS-SPEED-VALUE)、スライダー(EL-INS-SPEED-SLIDER・`speedSliderValue` = log2(speed)・範囲 [−2, 2])、プリセット 0.25x・
    0.5x・1x・1.5x・2x・3x・4x(EL-INS-SPEED-0_25・EL-INS-SPEED-0_5・EL-INS-SPEED-1・EL-INS-SPEED-1_5・EL-INS-SPEED-2・EL-INS-SPEED-3・
    EL-INS-SPEED-4 → `ApplySpeedPreset`)、要約 `regionSpeedSummary`「This region exports as
    {FormatClock(outputDuration)} (originally {FormatClock(duration)}).」(EL-INS-SPEED-SUMMARY)。`activeSpeedPreset` = 表記が
    `selectedSpeedText` と一致するプリセットを選択状態で表示する。
  - 速度の値: 0.01 単位に偶数丸め(偶数丸め(速度·100)/100)してから [0.25, 4.0] に収める(INV-004)。スライダーの値の変更 1 回 =
    `SetSpeedContinuous`(速度 = 2^値・連続して反映・記録しない・編集対象を再解決・`edited` を真)。プリセットは押すたびに 1 件記録
    (値が同じでも)。
  - スライダーの履歴の結線(速度・音量とも同じ): 記録(`BeginInteractiveEdit`・1 件・`edited` を真)はスライダー自身の PointerPressed の
    通常のハンドラ(処理済みのイベントは受けない)だけに結線する。スライダーのテンプレート(Styles/Controls.axaml の Slider.rng)は高さ
    28 px の透明な枠の中央に Track を置き、Track の横幅全体をつまみ(Thumb 18×18)と左右の透明な RepeatButton(PART_DecreaseButton /
    PART_IncreaseButton)が埋める。Thumb と RepeatButton は押下を処理済みにするので、つまみ・トラックを押したドラッグでは記録されず値の
    変更だけが反映される。このとき元に戻すは、スライダーの変更とその前に記録した最後の操作をまとめて戻す(1 回でその操作の前の状態)。
    記録されるのは押下がスライダーまで届いたとき(Track の上下の透明な余白の押下・EL-INS-SPEED-SLIDER-PRESS / EL-INS-VOLUME-SLIDER-PRESS)
    だけで、押した時点の 1 件。再製造は同じテンプレート構成と同じ結線にし、操作ごとの記録件数が元のアプリと一致すること(UQ-SPEC-014)。
  - 音声の欄: スピーカーアイコン・「Volume」・`volumeText`「{偶数丸め(volume·100)}%」(EL-INS-VOLUME-VALUE・`selectedVolumeColor` =
    ミュートなら warn #E5A14B、100% なら text #F2F4F6、それ以外 accent-text #8EC1FF)、スライダー(EL-INS-VOLUME-SLIDER・
    `volumeSliderValue` = volume·100(編集対象が無ければ 100)・0〜200・線形・`SetVolumeContinuous`: 音量 = 値/100)、プリセット Mute(0)・50%・100%・150%(EL-INS-VOLUME-0・EL-INS-VOLUME-50・EL-INS-VOLUME-100・EL-INS-VOLUME-150 → `ApplyVolumePreset`・押す
    たびに 1 件)。`activeVolumePreset` = `volumeText` と一致するプリセット。注記: `showMuteNote`(ミュート)で「Silences this region
    (video unchanged).」(EL-INS-MUTE-NOTE)、`showClippingNote`(volume > 1.001)で「Above 100% may cause clipping.」(EL-INS-CLIP-NOTE)。
  - 音量の値: 0.01 単位に偶数丸めしてから [0.0, 2.0] に収める。`isMuted` = < 0.001、`isFullVolume` = |v − 1| < 0.001。
  - `ToggleMute`(EL-KEY-M): 編集対象がミュートなら音量 1.0、それ以外 0.0(前の音量は覚えない・UQ-SPEC-015)。1 件記録。
  - ピッチ維持の行(EL-INS-PITCH-ROW → `TogglePitch`): トグル・「Preserve pitch」・説明。行のどこを押しても(マウスのどのボタンでも)
    反転し、1 件記録。`showNoPitchCorrectionNote`(編集対象の速度が 1)で「No correction is applied at normal speed.」(EL-INS-PITCH-NOTE)。
  - 除外の行(EL-INS-EXCLUDE-ROW → `ToggleExclude`): トグル・「Exclude this region (cut)」・説明。行を押すと(どのボタンでも)反転し 1 件
    記録。`canToggleExclude`(編集対象があり、それが除外済みか、他に除外していない区間があるとき)が偽なら行を無効にして操作できない
    (除外していない最後の区間は除外できない・INV-005)。解除はいつでもできる。
  - 書き出し設定(下部): 「After trim」= `sourceLengthClock`(EL-INS-AFTER-TRIM)、「After speed」= `outputLengthClock`(accent-text 色・
    EL-INS-AFTER-SPEED)。
- 振る舞い(SPEC-INSPECTOR-002):
  - 幅・高さの入力欄(EL-INS-WIDTH / EL-INS-HEIGHT・`OutputSettings.widthInputText` / `heightInputText`): 打った文字(`EditWidthText` /
    `EditHeightText`)は確定まで出力寸法を変えない。フォーカス(EL-INS-WIDTH-FOCUS / EL-INS-HEIGHT-FOCUS → `FocusWidthInput` /
    `FocusHeightInput`・`InspectorView.focusedInput`)がある間はキーボードの操作が働かない(§2.19)。確定は Enter(フォーカスは残る)か
    フォーカスが外れたとき(EL-INS-WIDTH-COMMIT → `ApplyWidth` / EL-INS-HEIGHT-COMMIT → `ApplyHeight`)。
  - 確定: 入力から数字以外の文字を取り除き、整数にできなければ値を変えない。幅は [16, 7680]、高さは [16, 4320] に収めてから Even。
    `keepAspect` が真なら、もう一方を Even(入力値 × ソースの縦横比)で計算する(この結果は上限・下限に収めない・UQ-SPEC-016。例: 縦長
    1080×1920 で幅 7680 → 高さ 13654)。確定すると `edited` を真(値が変わらなくても・整数にできたとき)。確定後の入力欄は実際の値を表示する。
    入力欄は出力寸法に OneWay で結ばれる(確定前の文字と後続の操作の関係は UQ-SPEC-017)。
  - 縦横比の維持の行(EL-INS-ASPECT-ROW → `ToggleAspect`・どのボタンでも): `keepAspect` を反転。オンにしたときは高さを Even(幅 ×
    ソースの高さ / ソースの幅)にする。この切り替えでは `edited` は変わらない(UQ-SPEC-016)。行に `aspectRatioText`
    「{FormatSpeed(W/H)}:1」と説明「Changing the width keeps the height proportional automatically.」を出す(高さを変えたときも幅が変わる)。
  - スケールのプリセット 100%・75%・50%(EL-INS-SCALE-100・EL-INS-SCALE-75・EL-INS-SCALE-50 → `Scale` 1・0.75・0.5)と Reset(EL-INS-SCALE-RESET・100% と同じ・
    ツールチップ「Restore original」・`showReset` = 出力がソースと違うときだけ表示): `keepAspect` に関わらず幅と高さをそれぞれ Even(ソースの
    寸法 × 倍率)にし `edited` を真。各プリセットは出力寸法がその値に一致するとき選択状態(プリセットごとに独立に判定する。同時に 2 つ
    以上が選択状態になりうる・モデルの `activeScalePreset` は 1 値・UQ-SPEC-023)。下に `originalResolutionText`「Original {W×H}」と、違う
    ときは `resolutionDiffText`「 → scaled to {W}×{H}」(EL-INS-ORIGINAL-RES)。
  - 出力フレームレートのプリセット「Source」・24・30・60・120(EL-INS-FPS-SOURCE・EL-INS-FPS-24・EL-INS-FPS-30・EL-INS-FPS-60・EL-INS-FPS-120 → `SetFps`): Source はソースの fps、数字は
    その値を `outputFps` にし、値が同じでも `edited` を真。上限なし。Source のツールチップ `fpsSourceTip`「Same as source ({Clip.fpsText})」。
    選択状態: `fpsSourceActive` = |outputFps − Clip.fps| < 0.05 で Source、`activeFpsPreset` = FormatSpeed(outputFps) が数字と一致する
    もの(両方が選択状態になりうる)。`fpsUpsampling`(outputFps > Clip.fps + 0.05)で「An fps higher than the source duplicates frames
    (quality does not improve).」(EL-INS-FPS-NOTE)。
  - 出力解像度・縦横比の維持・出力 fps は履歴の対象外(§2.18)。
- 核/表面: core(区間の情報・値の規則・解像度・fps)/ surface(速度と音量の欄の見た目とスライダーの結線・REQ-058・REQ-060)
  (出所: authority/Views/InspectorView.axaml・InspectorView.axaml.cs・Styles/Controls.axaml#Slider.rng・ViewModels/MainWindowViewModel.cs)
- 受入観点: unit・exact(値の丸め・範囲・Even・選択状態の判定・edited の契機)/ L2(スライダーの押下の場所ごとの記録件数を元のアプリと
  比べる・REQ-058・REQ-060)/ L1(ピッチ維持の注記)
- 画面: SCR-INSPECTOR(全 54 部品)
- シナリオ: UC-004・UC-012・UC-032・UC-035・UC-039・UC-044・UC-058・UC-070・UC-072・UC-073・UC-074・UC-075・UC-076・UC-077・UC-080・UC-081・UC-082・UC-083・UC-084・UC-086・UC-087・UC-090・UC-091・UC-092・UC-093・UC-094・UC-100・UC-101・UC-102・UC-103・UC-105・UC-106・UC-107・UC-108・UC-109・UC-110・UC-111・UC-112・UC-113・UC-141・UC-168・UC-181・UC-190
- E-BOM 候補: E-INSPECTOR-001・E-INSPECTOR-002
- M-BOM 候補: M-INSPECTOR-001・M-INSPECTOR-002
- Control Plan 候補: CP-INSPECTOR-001・CP-INSPECTOR-002
- 表示契約:
  - 原典参照: authority/Views/InspectorView.axaml・docs/images/06-speed.png・08-volume.png・10-resolution-fps.png
  - 提示要素: 見出し・見本・区間番号・開始/終了/長さ・速度の数値/スライダー/7 プリセット/要約・音量の数値/スライダー/4 プリセット/2 注記・
    ピッチ維持の行と注記・除外の行・After trim/After speed・幅/高さの入力欄・縦横比の行・スケールの 3 プリセットと Reset・Original と
    scaled to・fps の 5 プリセットと注記
  - 対象外要素: クリップ情報(到達しない・UQ-SPEC-013)

<a id="history"></a>
### 2.18 履歴と未保存の変更 (REQ-071, REQ-072)
- 仕様節ID: SPEC-HISTORY-001
- 振る舞い:
  - 対象は `Document`(トリムと区間列)だけ。`History.capacity` = 50。記録 = 記録の前の `Document` を `past` の末尾に積み、`future` を空に
    する。50 件を超えたら古いものから捨てる。
  - 1 操作 1 件: `Split`・`DeleteSelectedBoundary`・`SetTrimIn`/`SetTrimOut`(変わったときだけ)・`ApplySpeedPreset`・`ApplyVolumePreset`・
    `TogglePitch`・`ToggleExclude`(変わったときだけ)・`ToggleMute`。タイムラインのドラッグは押した時点の 1 件(`Begin*Drag`)。
    スライダーは `BeginInteractiveEdit` の 1 件だけ(§2.17)。値の変更・移動(`Set*Continuous`・`Move*`・`Scrub`)は記録しない。
  - `Undo`(EL-TL-UNDO・EL-KEY-CTRL-Z): 現在の `Document` を `future` に積み、`past` の末尾に戻す。`Redo`(EL-TL-REDO・EL-KEY-CTRL-SHIFT-Z・
    EL-KEY-CTRL-Y): 現在を `past` に積み、`future` の末尾にする。どちらも編集対象を再解決する。`nextRegionId` は戻さない。
  - 履歴の対象外: 出力解像度・縦横比の維持・出力 fps・書き出し形式(元に戻しても変わらない・UQ-SPEC-024)。読み込みで `past`・`future` は空。
  - `EditSession.edited`: 真にする = `Document` を変える操作(上の 1 件の操作と `Set*Continuous`・`Move*`)・`Begin*Drag`・
    `BeginInteractiveEdit`・`ApplyWidth`/`ApplyHeight`・`Scale`・`SetFps`。偽にする = 読み込みの成功・書き出しの成功。変えない =
    `ToggleAspect`・`Undo`・`Redo`(元に戻して最初の状態に戻っても真のまま)。起動直後(サンプル)は偽。
- 核/表面: core(出所: authority/Services/History.cs・ViewModels/MainWindowViewModel.cs)
- 受入観点: unit・exact(件数・上限・やり直しの消去・対象外)
- 画面: SCR-TOOLBAR(EL-TL-UNDO・EL-TL-REDO)・SCR-TITLEBAR(EL-TB-STATUS)・SCR-MAIN(EL-KEY-CTRL-Z・EL-KEY-CTRL-SHIFT-Z・EL-KEY-CTRL-Y)
- シナリオ: UC-003・UC-004・UC-031・UC-038・UC-040・UC-041・UC-042・UC-043・UC-044・UC-045・UC-054・UC-072・UC-073・UC-074・UC-077・UC-086・UC-091・UC-100・UC-105・UC-107・UC-109・UC-110・UC-127
- E-BOM 候補: E-HISTORY-001
- M-BOM 候補: M-HISTORY-001
- Control Plan 候補: CP-HISTORY-001

<a id="keyboard"></a>
### 2.19 キーボード (REQ-073, REQ-074)
- 仕様節ID: SPEC-KEYBOARD-001
- 振る舞い:
  - 割り当て: Space = `TogglePlay`(EL-KEY-SPACE)・← または , = `StepBack`(EL-KEY-LEFT)・→ または . = `StepForward`(EL-KEY-RIGHT)・
    Shift+← / Shift+, = `StepSecondBack`(EL-KEY-SHIFT-LEFT)・Shift+→ / Shift+. = `StepSecondForward`(EL-KEY-SHIFT-RIGHT)・S(Ctrl なし)=
    `Split`(EL-KEY-S)・I(Ctrl なし)= `SetTrimIn`(EL-KEY-I)・O(Ctrl なし)= `SetTrimOut`(EL-KEY-O)・Delete または Backspace =
    `ToggleExclude`(EL-KEY-DELETE・`canToggleExclude` が偽なら何もしない)・M(Ctrl なし)= `ToggleMute`(EL-KEY-M)・Ctrl+Z = `Undo`
    (EL-KEY-CTRL-Z)・Ctrl+Shift+Z と Ctrl+Y = `Redo`(EL-KEY-CTRL-SHIFT-Z・EL-KEY-CTRL-Y)。S・I・O・M は Shift の有無に関わらず働く。
  - 修飾キーの扱い(MainWindow.axaml.cs の OnKeyDown): Space・←・→・,・.・Delete・Backspace は Ctrl を見ない(Ctrl+Space は再生/
    一時停止、Ctrl+→ は 1 フレーム進む、Ctrl+Shift+→ は 1 秒進む、Ctrl+Delete は除外の切り替え)。←・→・,・. は Shift だけを見る。S・I・O・M は
    Ctrl が無いときだけ。Z は Ctrl があるときだけ(Shift ありなら Redo、なければ Undo)、Y は Ctrl があるときだけ Redo(Shift は問わない)。
    Alt は見ない。どの文字の入力欄(TextBox)にフォーカスがあっても、ここで処理しない。
  - キーを受ける経路: ショートカットはウィンドウの OnKeyDown の上書き(base.OnKeyDown の後に処理)だけで受ける。これはバブルの
    クラスハンドラなので、フォーカスのある部品が先に処理済み(Handled)にしたキーは届かない(先取りの PreviewKeyDown やトンネルの
    ハンドラは使わない)。ボタン・チェックボックス・ラジオ・スライダーはどれも Focusable を外していないので、クリックでフォーカスを得た
    部品がキーを先に取りうる(例: ボタンにフォーカスがあると Space / Enter はそのボタンの押下になり、再生/一時停止にならない)。
    どの部品がどのキーを取るかは Avalonia 12 の各コントロールの既定に従い、本書では列挙しない(UQ-SPEC-033)。
  - キーの S・I・O はボタンと同じコマンドを実行する(§2.13)。I・O は実行の先頭で `canSetTrimIn` / `canSetTrimOut` を確かめ、偽なら何も
    しない(ボタンの押せる条件と同じ判定)。S だけは押せる条件 `canSplit`(丸める前の playhead の開区間)を確かめず、`Split` 自身の判定
    (SnapFrame した ph の閉区間)で決まる。したがって Split のボタンが無効でも S キーで分割できることがある(例: playhead が start + 0.5 の
    わずかに手前で、SnapFrame で start + 0.5 に乗るとき)。
  - `InspectorView.focusedInput` が none でない(幅・高さの入力欄にフォーカスがある)間は、キーボードの操作はすべて働かない。
  - オーバーレイ(書き出し・About・ffmpeg セットアップ)の表示中も働く(例: 書き出しダイアログの裏で Space で再生、Delete で除外)。
    ただし上の経路のとおり、オーバーレイの中でフォーカスを得た部品が取ったキーは届かない。
- 核/表面: core(出所: authority/Views/MainWindow.axaml.cs#OnKeyDown)
- 受入観点: L1・exact(キーごとの操作・入力欄のフォーカス中の無効・オーバーレイ中の有効)
- 画面: SCR-MAIN(EL-KEY-*)・SCR-INSPECTOR(EL-INS-WIDTH-FOCUS・EL-INS-HEIGHT-FOCUS)
- シナリオ: UC-015・UC-017・UC-019・UC-023・UC-025・UC-032・UC-033・UC-042・UC-045・UC-051・UC-053・UC-083・UC-094・UC-104・UC-165・UC-168・UC-173・UC-193
- E-BOM 候補: E-KEYBOARD-001
- M-BOM 候補: M-KEYBOARD-001
- Control Plan 候補: CP-KEYBOARD-001

<a id="export-dialog"></a>
### 2.20 書き出しダイアログ (REQ-075 〜 REQ-083)
- 仕様節ID: SPEC-EXPORTDLG-001
- 振る舞い:
  - 開く・閉じる: `ShowExportDialog`(EL-TL-EXPORT)で `ExportJob.dialogShown` を真。背景を暗くするオーバーレイの中央の幅 520 px の
    モーダル(EL-EX-DIALOG)。見出し「Export」と「Outputs with speed, pitch, and trim applied.」。「Cancel」(EL-EX-CANCEL)または背景
    (EL-EX-SCRIM・モーダルの外・タイトルバーの上を含む・マウスのどのボタンでも)= `CloseExport`。モーダル本体のクリックでは閉じない。
    `isExporting` の間はどちらでも閉じない。Esc では閉じない。
  - 形式(EL-EX-FORMAT-MP4・EL-EX-FORMAT-LOSSLESS・EL-EX-FORMAT-PRORES → `SelectFormat`): 3 つのカード「MP4 (H.264 / AAC)」(タグ For sharing)・
    「Intermediate file (FFV1 / PCM)」(タグ Lossless)・「ProRes 422 HQ / PCM」(タグ For editing)と各 `cardDescription`。カードのどこを
    (どのボタンで)押しても選択(書き出し中も押せる。進行中の書き出しは開始時の形式のまま・選択の表示とその後の選択だけが変わる)。選択中の
    カードはラジオの点。形式の識別子 `ExportFormat.key` は Mp4・Lossless・ProRes(SelectFormat の引数)。既定は Mp4。選択はアプリの終了まで保つ(閉じても・別のクリップを読み込んでも)。保存しない。
  - 要約: `outputResolutionText`「W×H」(EL-EX-SUMMARY-RES)・「{outputFpsText} fps」(EL-EX-SUMMARY-FPS)・`outputDurationText`
    「{outputLengthClock} (orig {sourceLengthClock})」(EL-EX-SUMMARY-DURATION)。
  - コピー(高速・無劣化)の切り替え(EL-EX-FASTCOPY → `SetFastExport`): `canFastExport` のときだけ表示する。`canFastExport` = `Clip` が
    実ファイル(`isSample` が偽)・形式が Mp4・`isOriginalResolution`・除外していない区間の速度がすべて 1・|outputFps − Clip.fps| ≤ 0.05・
    `videoCodec` が H.264 か H.265・音声が無いか(AAC・MP3・AC-3 で除外していない区間の音量がすべて 100%)・`ExportRun.singleSpan`
    (トリムと除外の後に残る範囲が 1 つ)。除外した区間の速度・音量は見ない。既定はオフ、読み込みのたびにオフ。条件を満たさないときは
    切り替えの枠ごと隠し、`fastExport` が真のまま残っていても再エンコードで書き出す。
  - 切り替えの枠(`canFastExport` のとき表示)の中身: チェックボックス「Fast, lossless (copy)」(ja: 高速・無劣化（コピー）・Export_FastCopy・EL-EX-FASTCOPY)、その下に説明「Copies without
    re-encoding. …」(Export_FastCopyHint・EL-EX-FASTCOPY-HINT)。説明は枠の中で条件を持たないので、`fastExport` がオフでも
    `canFastExport` なら出る。
  - コピーの表示(`showFastExportNote` = fastExport かつ canFastExport のときだけ・枠の中で説明の下): `showVfrCopyNote`(VFR)で
    VFR の注記(EL-EX-VFR-NOTE)、コピーの範囲の帯(EL-EX-COPY-STRIP・CopyPreviewStrip・高さ 28・横幅いっぱい):
    kf = `copyCutStart`(null なら trimStart)、全体 = trimEnd − kf。背景 #22272C の角丸 6 を描き、全体 ≤ 0 なら背景だけ。リードの幅 =
    clamp((trimStart − kf)/全体, 0, 1)·幅。角丸 6 でクリップして、リードの幅が 0.5 px を超えれば [0, リード] を #C9E5A14B、残り [リード, 幅] を
    #579BF4 で塗り、リードが 0.5 px を超えればその境に #1A1D21 の 1 px の仕切り線を引く(どれもトークンに無い値)、キーフレームの注記。`copyLeadInSeconds` = copyCutStart があれば max(0, trimStart −
    copyCutStart)、無ければ 0。`showCopyCutMarker`(> 0.02)で `copyLeadInText`「About {リード秒数(小数 1 桁・カルチャ不変)} s of lead
    footage is included at the start.」(EL-EX-LEADIN)とタイムラインの破線とリードの帯(§2.15)。
  - キーフレームの算出の契機: 値が実際に変わったときだけ — `ExportJob.dialogShown` が偽から真になったとき(`ShowExportDialog`)・
    `fastExport` の値が変わったとき(`SetFastExport`)・`selectedFormat` が別の形式に変わったとき(`SelectFormat`。いま選んでいる形式の
    カードを押し直しても契機にならない)・`Document` の変化・`ConfirmExport` の開始。
    その時点で fastExport かつ canFastExport のときだけ `copyCutGeneration` を 1 増やして算出を始め、`KeyframeResolved` で世代が変わって
    いなければ `copyCutStart` にする。`Document` が変わると先に `copyCutStart` = null にしてから契機の判定をする。覚えている値
    (`KeyframeCache`・同じトリム開始)があれば同期に答えが返るので、表示は消えずに残る(UQ-SPEC-025)。出力解像度・出力 fps の変更で
    コピーできる状態に戻っても求め直さないので、次の契機まで帯とリードは出ない(書き出しの開始では必ず求める)。コピーできない状態で
    `Document` が変わったときは世代が進まないので、前のトリム開始で始めた算出の結果が後から入ることがある(再現する)。
  - キーフレームの算出(`KeyframeCache`): トリム開始以下で最大のキーフレームの時刻。トリム開始 ≤ 0 なら 0 → 覚えている値(パスと時刻 ms
    (偶数丸め))があればそれ → `Clip.isOnlineOnly` なら null(求めない)→ ffprobe で窓 [max(0, 対象 − 幅), 対象] を読む(幅 12・48・192・768
    秒の順に最大 4 回)。窓の開始が 0 に達しても見つからない・4 回で見つからない(トリム開始 > 768 秒)ときは 0。ffprobe が 0 以外で終了した
    ときは「その窓に無い」と同じ扱い(失敗でも答えは 0・ファイルの先頭からのコピーで、0〜トリム開始がすべてリードになり、文言と帯もこの
    値)。結果(失敗による 0 も)を覚える。1 回の ffprobe は 20 秒で打ち切り、打ち切りは例外として呼び出し側へ出る(覚えない)。
  - 「Export」(EL-EX-CONFIRM → `ConfirmExport`): `isExporting` なら何もしない。サンプルなら `statusMessage` =「Samples cannot be exported.
    Open an actual file.」(`statusMessageKey` を持つ)で終わる。実ファイルなら保存先の選択ダイアログ(SCR-SAVE-PICKER・タイトル
    「Export to」・既定のファイル名 `suggestedFileName`「{fileName の拡張子なし}_export{extension}」(EL-SP-FILENAME)・種類は
    resx の Dialog_FileSuffix で「{拡張子の大文字(先頭の . を除く)} file」の 1 つ・パターン *.{拡張子}・既定の拡張子付き(EL-SP-PICKER))を開き、選ばなければ何もしない。拡張子は
    Mp4 = .mp4・Lossless = .mkv・ProRes = .mov(ダイアログに見える値の受入は UQ-SPEC-029)。選んだら `outputPath` を設定し、`isExporting` = 真・`progress`/`frame`/`ffmpegSpeed` = 0・
    `statusMessage` =「Exporting…」(キーあり)にして時計を測り始め、コピーならキーフレームを確定(`copyCutStart`)してから、その時点の
    Document・出力設定・形式・コピーの指定を `ExportRun.request` に固定して書き出す(§2.21)。
  - 書き出し中の表示: 「Cancel」「Export」を隠し、進捗バーと `percentText`「{偶数丸め(progress·100)}%」(12.5% は 12・EL-EX-PROGRESS)、
    `detailText`「Frame {frame}」(frame ≥ 1 のときだけ。0 なら速度も含めて何も出さない)に ffmpegSpeed > 0.01 なら「 · ×{FormatSpeed
    (ffmpegSpeed)}」を続ける、`etaText`「About {FormatClock(残り)} left」(progress > 0.02 から。ffmpegSpeed > 0.01 なら outputLength·
    (1 − progress)/ffmpegSpeed。outputLength は書き出しの開始時の値ではなく、表示を計算するその時点の `Document.outputLength`
    なので、書き出し中に編集すると表示される残り時間が変わる、無ければ elapsedSeconds·(1 − progress)/progress)(EL-EX-DETAIL)、「Abort」(EL-EX-ABORT → `CancelExport`)。
    `ExportProgressReported` が progress(ffmpeg の出力済み時刻 / `ExportRun.totalOutputSeconds` を [0, 1] に収めたもの)・frame・
    ffmpegSpeed を更新する(elapsedSeconds は更新しない。成功で終わるときは最後に 1 を届ける)。
  - 結果: 終わったら `isExporting` = 偽・時計を止める。成功 = `dialogShown` = 偽・`edited` = 偽・`statusMessage` = null・
    `OutputFile.state` = complete(同名は上書き・中身 `OutputFile.contents` は §2.21 の経路と符号化に従う)。中断(Abort)=「Export canceled.」(`OutputFile.state` = partial・途中のファイルを削除
    しない)。判定の順は 総時間 → 区間 → ffmpeg の終了: `totalOutputSeconds` ≤ 0 =「Output duration is zero.」、`segmentCount` = 0(条件は §2.21)=
    「There are no regions to export.」(どちらも ffmpeg を起動しない・`OutputFile.state` = absent)、ffmpeg が 0 以外で終了 =「ffmpeg exited
    with an error (code {N}).」の次の行に標準エラーの最後の 8 行(空行を除く)(`OutputFile.state` = partial・UQ-SPEC-026)。結果の文言は
    キーを持たず(言語の切り替えで訳し直さない)、`showStatus`(書き出し中でなく文言が空でない)のときボタンの上に warn 色で出す
    (EL-EX-STATUS)。ダイアログを閉じて開き直しても次の書き出しを始めるまで残る(UQ-SPEC-027)。
  - 異常終了の経路(再現する不具合): コピーの開始時のキーフレームの算出の例外(ffprobe の 20 秒の打ち切り・起動の失敗)は ConfirmExport の
    try の外の EnsureCopyCutAsync から出て、コマンドの外へ捕捉されずに出る → 異常終了。VM には書き出し中の状態が残る(isExporting は真・
    Abort の取り消しは算出に渡されない・閉じる操作は効かない)。再エンコードの ffmpeg の起動の例外も異常終了。VM は finally で書き出し中が
    解け、`statusMessage` が「Exporting…」のまま残る(UQ-SPEC-004)。
- 核/表面: core(出所: authority/Views/ExportDialogView.axaml・ViewModels/MainWindowViewModel.cs#ConfirmExport・Services/KeyframeIndex.cs・
  Services/ExportClock.cs)
- 受入観点: unit・exact(canFastExport・キーフレームの探索・文言の判定順・進捗の書式)/ L1(ダイアログの開閉・表示・結果の文言)/
  L2(リードの帯)
- 画面: SCR-EXPORT(全 19 部品)・SCR-SAVE-PICKER(EL-SP-PICKER・EL-SP-FILENAME)・SCR-TOOLBAR(EL-TL-EXPORT)
- シナリオ: UC-151・UC-160・UC-161・UC-162・UC-163・UC-164・UC-166・UC-167・UC-170・UC-171・UC-172・UC-173・UC-174・UC-175・UC-176・UC-177・UC-178・UC-179・UC-180・UC-181・UC-231
- E-BOM 候補: E-EXPORTDLG-001
- M-BOM 候補: M-EXPORTDLG-001
- Control Plan 候補: CP-EXPORTDLG-001
- 表示契約:
  - 原典参照: authority/Views/ExportDialogView.axaml・docs/images/11-export.png
  - 提示要素: 見出し・説明・3 カード(見出し/タグ/説明/ラジオ)・コピーの切り替えと説明/VFR 注記/帯/リードの文言・要約 3 行・進捗バー/
    %/Frame/速度/残り時間・Abort・状態の文言・Cancel・Export
  - 対象外要素: なし

<a id="export-content"></a>
### 2.21 書き出しの内容 (REQ-084 〜 REQ-088)
- 仕様節ID: SPEC-EXPORT-001
- 振る舞い:
  - 経路 `ExportRun.path`: request のコピーの指定(fastExport かつ canFastExport)かつ `canStreamCopy` なら copy。それ以外で、ソースが CFR
    (`isVariableFrameRate` が偽)でソース fps・出力 fps・各区間の速度が正の有限値なら exactCfr、それ以外は legacy。
  - 残る範囲: 除外していない各区間の [max(start, trimStart), min(end, trimEnd)] のうち長さが 0.0001 秒を超えるものを時刻順に並べ、前の
    終わり + 0.0001 以内で始まるものを同じ範囲にまとめる(`spanCount`・`singleSpan`・`spanStart`・`spanEnd`)。
  - 再エンコード(共通): 除外していない区間とトリム範囲の重なり(0.0001 秒以下は除く)を、タイムラインの順に、各区間の速度で再生した映像と
    音声をつなぐ。出力寸法がソースと違うときだけ lanczos で W×H に拡大縮小。音声は区間ごとに速度の変換の後、音量 ≠ 100% なら一定の
    倍率を掛ける。速度の変換は preservePitch なら atempo(1 段あたり [0.5, 2.0] に収まるよう複数段)、偽なら asetrate(サンプルレート·速度)の
    後に aresample=元のサンプルレート。exactCfr では速度 ≠ 1 のときだけ入れ、legacy では速度 1 でも入れる(atempo=1 / asetrate=SR,
    aresample=SR)。ソースのファイルは変更しない。
  - exactCfr(有理数で厳密): 出力は出力 fps の CFR。値はすべて有理数で計算し、double の値は次の認識の規則で有理数にする(認識に外れた値を
    格子や c/100 へ丸めて寄せてはならない。外れた値は double の厳密な二進有理数のまま使う。authority/Services/ExportClock.cs の
    RecognizeRate・CanonicalTime・CanonicalSpeed):
    - レート(ソース fps・出力 fps): q ∈ {1, 1001} の順に p = Math.Round(fps·q) とし、p > 0 かつ (double)p/q == fps(ビット一致)なら p/q。
      どちらでもなければ fps の二進厳密値。以下の「ソース fps」「出力 fps」はこの有理数(周期はその逆数)。
    - 時刻(各区間の重なりの端 max(start, trimStart)・min(end, trimEnd)): n = Math.Round(x·Clip.fps)(偶数丸め)とし、n/Clip.fps == x
      (double のビット一致・許容窓なし)なら n·ソースの周期(格子点)、そうでなければ x の二進厳密値。SnapFrame で作った時刻は格子点になるが、
      読み込み直後の既定の trimEnd(= 末尾区間の end = ffprobe の duration)は普通格子に乗らないので、既定の経路では格子外の値で計算される。
    - 速度: c = Math.Round(speed·100) とし、25 ≤ c ≤ 400 かつ c/100 == speed(ビット一致)なら c/100、そうでなければ speed の二進厳密値。
    - サンプルレート SR = Clip.sampleRate(0 以下なら 48000)。
    - 各区間の速度が正の有限値でない、または残る区間が 0 なら exactCfr の計画は作らず legacy へ回す。
    `runs` = ソース上で
    連続し(前の end の有理数 == 次の start の有理数)、速度(有理数)・音量(double の等値)・ピッチ維持が同じ隣り合う区間を 1 つにまとめた列(分割/結合しただけでは出力のフレーム列・枚数・タイムスタンプ・音声を
    変えない・ゼロの挿入もない・INV-011)。`exactOutputTime` T = Σ(重なりの長さ/速度)、`outputFrameCount` N = RoundHalfUp(T·出力 fps)、
    `outputSampleCount` = RoundHalfUp(T·サンプルレート)。run k の出力上の開始 T_0 = 0、T_{k+1} = T_k + (end − start)/speed。run k の出力
    フレームは [min(ceil(T_k·出力 fps), N), min(ceil(T_{k+1}·出力 fps), N))、出力フレーム i のソースフレームは floor((start + (i/出力 fps −
    T_k)·speed)·ソース fps)(sample-and-hold: その時刻以前で最も新しいソースのフレーム)、run が読むソースフレームは floor(start·ソース fps)
    から ceil(end·ソース fps) まで(最低 1 枚)。音声は run ごとにソースのサンプル [RoundHalfUp(start·SR), RoundHalfUp(end·SR)) を切り出し、
    速度変換(速度 1 は無し)と音量の後、出力上の長さ RoundHalfUp(T_{k+1}·SR) − RoundHalfUp(T_k·SR) サンプルへ無音の付け足しか切り詰めで
    揃える。映像と音声は別々につなぐ(run ごとの値はモデルの属性に無く、この式を正とする・UQ-SPEC-030)。`segmentCount` = グラフでつないだ run の数。次のどれかなら 0: N ≤ 0、音声ありで outputSampleCount ≤ 0、出力フレームを 1 枚以上
    持つ映像の run が 0 本、音声ありで出力の長さが 1 サンプル以上の音声の run が 0 本。0 のときは totalOutputSeconds > 0 でも ffmpeg を
    起動せず「There are no regions to export.」で終わる(§2.20)。
  - legacy(厳密な時間の保証の対象外・グラフの構成だけ完全一致): 区間ごとに映像を trim+setpts、音声を atrim(絶対時刻)→ asetpts → 速度の
    変換 → 音量(100% でないとき)で処理して concat でつなぎ、速度・fps の変更・VFR のいずれかがあれば最後に fps フィルタで出力 fps の CFR
    にする。映像の trim の時刻は入力シークの位置を引いた値。`segmentCount` = 重なりが 0.0001 秒を超える除外していない区間の数。
  - 符号化 `ExportRun.encoding`: Mp4 = libx264(-preset medium・-crf 18・yuv420p)+ AAC 192 kbps・+faststart(exactCfr だけ映像トラックの
    タイムスケール -video_track_timescale = 出力 fps の分子 p(0 < p ≤ int.MaxValue のときだけ付ける)、ムービーのタイムスケール
    -movie_timescale = lcm(p, サンプルレート)・音声なしは p(その値が 0 < m ≤ int.MaxValue のときだけ付ける))。Lossless = FFV1 level 3 +
    PCM 16bit。ProRes = prores_ks profile 3(422 HQ)・yuv422p10le + PCM 16bit。exactCfr はどの形式も -r p/q を付け、legacy は -r も
    タイムスケールも付けない。ソースに音声が無ければ音声のストリームを出力しない(`hasAudioStream`)。同名のファイルは上書き。
  - 再エンコードの引数の並び: -y -hide_banner -nostats -progress pipe:1、[S > 0 のとき -ss S]、-i ソース、[S > 0 で音声があるとき、シーク
    しない 2 本目の -i ソース]、-filter_complex グラフ、-map [vout]、[音声があれば -map [aout]]、符号化の引数、出力の時間の引数、出力パス。
    S = `inputSeek` = spanStart ≥ 1.0 なら spanStart、未満なら 0。exactCfr では S > 0 のとき (n0 − 1/2)/ソース fps(n0 = 最初の run の最初の
    ソースフレーム・ExportClock.SeekTarget)に置き換える(その値が 0 以下なら置き換えない)。S > 0 のときグラフの映像の時刻は S を引いた値、
    音声は [1:a] から絶対時刻で切り出す(S = 0 なら [0:a])。秒の値は小数 6 桁まで(末尾の 0 を付けない・カルチャ不変)。
  - copy: `copyStart` = copyCutStart が 0 以上 spanStart 以下(誤差 1e-6)なら max(0, copyCutStart)、範囲外か null なら spanStart。長さ =
    spanEnd − copyStart(`totalOutputSeconds` = max(0, その値))。最初の映像と最初の音声のストリームを再エンコードせずにコピーする(負の
    タイムスタンプは 0 起点・+faststart)。欲しい範囲は欠けず、先頭にキーフレームからトリム開始までのリードが付く。VFR は VFR のまま。
    キーフレームはトリム開始を基準に求め spanStart 以下なら採用するので、先頭側の区間を除外して残る範囲がその後ろから始まるときは、除外した
    区間がまるごと(さらにその前のリードも)出力に入る(再現する不具合)。このときもリードの表示はトリム開始との差だけを示し、ダイアログの帯も
    トリム開始・終了を基準に描く。
  - `totalOutputSeconds`(進捗の分母): copy なら max(0, spanEnd − copyStart)、それ以外は request の `Document.outputLength`。
- 核/表面: surface(出所: authority/Services/FfmpegExporter.cs・ExportClock.cs・Models/ExportFormat.cs)
- 受入観点: L3(区間の順序と有無は完全一致・音量の倍率は 0.01 単位・REQ-084 / フレーム数・サンプル数・PTS は完全一致(ZERO)・REQ-085 /
  符号化の引数は exact・REQ-087 / 開始 = キーフレーム時刻・長さは 1e-6 秒単位の引数で完全一致・REQ-088)/ unit(legacy のグラフの構成は完全
  一致・時間精度は対象外・REQ-086)
- 画面: なし(ファイルの中身)
- シナリオ: なし(書き出しの完了は出来事なので手順に無い・UQ-SPEC-022)
- E-BOM 候補: E-EXPORT-001
- M-BOM 候補: M-EXPORT-001
- Control Plan 候補: CP-EXPORT-001

<a id="about"></a>
### 2.22 About (REQ-089, REQ-090)
- 仕様節ID: SPEC-ABOUT-001
- 振る舞い:
  - タイトルバーの ⓘ(EL-TB-ABOUT → `OpenAbout`): `AboutDialog.notices` が空ならアプリのフォルダの THIRD-PARTY-NOTICES.txt を読んで設定し
    (無いか読めないときは「Third-party license information (THIRD-PARTY-NOTICES.txt) was not found.」で始まる案内文・`noticesIsFallback` =
    真)、`shown` を真にする。一度読んだ内容は再読込しない。案内文は言語の切り替えで訳し直す。
  - 表示(EL-AB-DIALOG): 幅 560 px・最大高 660 px のモーダル。アイコン・「MoviePad」・`version`(EL-AB-VERSION)・「A video editor for
    trimming, per-region speed, and exporting mp4.」・ライセンスの要約(Application = MIT License、Bundled fonts = Manrope / JetBrains Mono —
    SIL OFL 1.1、Playback engine = LibVLC / LibVLCSharp — LGPL-2.1+、ffmpeg = 別プロセスで起動する旨)・「Full license text
    (THIRD-PARTY-NOTICES)」と全文(EL-AB-NOTICES・等幅・折り返しなし・選択できる文字・縦横にスクロール EL-AB-NOTICES-SCROLL)。
  - `version` = 「v」+ アセンブリの情報バージョンの「+」より前。無ければ「v」+ アセンブリのバージョンの 3 桁、それも無ければ v1.0.0。
  - 「Close」(EL-AB-CLOSE)か背景(EL-AB-SCRIM・どのボタンでも)= `CloseAbout`。
- 核/表面: core(出所: authority/Views/AboutDialogView.axaml・AboutDialogView.axaml.cs)
- 受入観点: unit・exact(バージョンの決定・案内文)/ L1(開閉と表示)
- 画面: SCR-ABOUT(全 6 部品)・SCR-TITLEBAR(EL-TB-ABOUT)
- シナリオ: UC-200・UC-201・UC-202・UC-203・UC-233
- E-BOM 候補: E-ABOUT-001
- M-BOM 候補: M-ABOUT-001
- Control Plan 候補: CP-ABOUT-001
- 表示契約:
  - 原典参照: authority/Views/AboutDialogView.axaml
  - 提示要素: アイコン・製品名・バージョン・説明・ライセンスの要約 4 行・全文の見出しと全文・Close
  - 対象外要素: なし

<a id="visual-design"></a>
### 2.23 外観(デザイントークンとスタイル) (REQ-091)
- 仕様節ID: SPEC-VISUAL-001
- 振る舞い:
  - 暗い配色・フォント Manrope(UI)と JetBrains Mono(等幅の数値表示)・角丸・影・各ボタンの見た目はデザイントークンと UI の契約に従う。配色は
    styles.css の oklch の定義を sRGB に厳密に変換した値(Styles/Tokens.axaml の計算値)。
  - 完全一致の範囲 (1): Styles/Tokens.axaml の値を持つ全キー。Color と Brush の両方 = BgWindow・BgApp・Surface・Surface2・Surface3・Line・
    LineSoft・Text・Text2・Text3・Text4・Accent・AccentSoft・AccentLine・AccentText・OnAccent・PrimaryHover・Warn・Ok・CloseHover・
    OverlayBlack50・OverlayBlack42・OverlayBlack18・Scrim・White12・White18・White10・White08・White06・TrimMask・Wave・EmptyCard(32 色・
    名前+Color / 名前+Brush)。Color のみ = BrandGrad2Color・StageRadialColor。Brush のみ = BrandGradientBrush・StageBackgroundBrush。
    RadiusSm/Md/Lg/Xl/Pill・FontUi・FontMono。EqualsConverter は値の照合の対象外で、値の等しさを返す変換として同じ働きを持つこと。
  - 完全一致の範囲 (2): Styles/Controls.axaml の全 56 のスタイル(セレクター)が設定するプロパティの値とテンプレート。要求 REQ-091 の
    列挙(Button.btn と primary・ghost-line・icon・sm・disabled・pointerover、Button.preset と active、Button.tp と play、Button.win と close、
    Border.pill・Border.section、Border.fmt と sel・radio・tag・dot、ToggleButton.toggle と checked、Slider.rng、TextBox.num-input と focus・
    pointerover、TextBlock.eyebrow・h4・k・v・mono・muted)は一部を欠くので(共有テンプレート・Button.btn StackPanel・Button.btn.icon.sm・
    Border.fmt:pointerover など・UQ-SPEC-032)、本書はファイルの全セレクターを範囲にする。一覧(ファイルの順): Button.btn, Button.preset, Button.tp, Button.win / Button.btn / Button.btn:pointerover /template/ ContentPresenter#PART_ContentPresenter / Button.btn:pointerover / Button.btn:disabled / Button.btn StackPanel / Button.btn.ghost-line / Button.btn.primary / Button.btn.primary /template/ ContentPresenter#PART_ContentPresenter / Button.btn.primary:pointerover /template/ ContentPresenter#PART_ContentPresenter / Button.btn.primary:pointerover / Button.btn.icon / Button.btn.sm / Button.btn.icon.sm / Button.preset / Button.preset:pointerover /template/ ContentPresenter#PART_ContentPresenter / Button.preset:pointerover / Button.preset.active / Button.preset.active /template/ ContentPresenter#PART_ContentPresenter / Button.tp / Button.tp:pointerover /template/ ContentPresenter#PART_ContentPresenter / Button.tp:pointerover / Button.tp.play / Button.tp.play:pointerover /template/ ContentPresenter#PART_ContentPresenter / Button.win / Button.win:pointerover /template/ ContentPresenter#PART_ContentPresenter / Button.win:pointerover / Button.win.close:pointerover /template/ ContentPresenter#PART_ContentPresenter / Button.win.close:pointerover / Border.pill / TextBox.num-input / TextBox.num-input:pointerover /template/ Border#PART_BorderElement / TextBox.num-input:focus /template/ Border#PART_BorderElement / ToggleButton.toggle / ToggleButton.toggle /template/ Border#knob / ToggleButton.toggle:checked /template/ Border#track / ToggleButton.toggle:checked /template/ Border#knob / Slider.rng / TextBlock.mono / TextBlock.eyebrow / Border.fmt / Border.fmt:pointerover / Border.fmt.sel / Border.fmt Border.radio / Border.fmt.sel Border.radio / Border.fmt Ellipse.dot / Border.fmt.sel Ellipse.dot / Border.fmt Border.tag / Border.fmt Border.tag TextBlock / Border.fmt.sel Border.tag / Border.fmt.sel Border.tag TextBlock / Border.section / TextBlock.h4 / TextBlock.k / TextBlock.v / TextBlock.muted。
    とくに Button.btn・Button.preset・Button.tp・Button.win は共有のテンプレート(ContentPresenter#PART_ContentPresenter が Background・
    BorderBrush・BorderThickness・CornerRadius・Foreground・Content・ContentTemplate・Padding・Transitions を TemplateBinding し、
    内容を左右上下とも中央に置く)を使い、Button.btn の中の StackPanel は Orientation=Horizontal・Spacing 8・VerticalAlignment=Center
    (アイコン+文字のボタンの並び)。
  - 配置(並び・入れ子・どの要素にどのクラスが付くか)は各 View の構造どおり。ピクセル単位の位置は合わせない。
- 核/表面: core(出所: authority/Styles/Tokens.axaml・Controls.axaml・design_handoff_moviepad/styles.css)
- 受入観点: L2(トークンとスタイルのプロパティ値は完全一致・配置は構造で・pixel-exact でない)
- 画面: 全画面
- シナリオ: UC-081・UC-090・UC-127
- E-BOM 候補: E-VISUAL-001
- M-BOM 候補: M-VISUAL-001
- Control Plan 候補: CP-VISUAL-001

<a id="debug-hooks"></a>
### 2.24 起動時の環境変数(デバッグ・撮影用) (REQ-094)
- 仕様節ID: SPEC-DEBUG-001
- 振る舞い:
  - `ApplyStartupEnvironment`(ウィンドウを開いた直後に 1 回)。未設定なら何もしない。処理の順は 開く → シナリオ → 書き出し → About。
    - `StartupEnvironment.openPath`(MOVIEPAD_OPEN): そのファイルを読み込む(`Open` と同じ・完了を待つ)。
    - `scenario`(MOVIEPAD_SCENARIO): 編集状態を直接作る(履歴に積まない・編集対象の再解決 (b) を通らず、続く `playhead` の設定で (a) だけが
      働く・`nextRegionId` は振り直さない)。ffmpeg = `FfmpegSetup.shown` を真(ffmpeg があっても)。trim = トリム 2〜17 秒・1 区間・playhead 9。
      split = トリム 0〜90 の 3 区間(30 秒ずつ)・playhead 15。speed = 3 区間で中央を 2x・playhead 45。exclude = 3 区間で中央を除外・
      playhead 15。volume = 3 区間で中央の音量 0.5・playhead 45。mute = 3 区間で中央の音量 0・playhead 45。それ以外の名前は何もしない。
    - `showExport` / `showAbout`(MOVIEPAD_SHOWEXPORT / MOVIEPAD_SHOWABOUT): 空でなければ書き出しダイアログ(`ShowExportDialog` と同じ)/
      About(`OpenAbout` と同じ)を開く。
    - `shotPath`(MOVIEPAD_SHOT): 上の処理(OPEN の完了を待ち、シナリオとダイアログを適用した後)から 1800 ms 後にウィンドウを PNG(96 dpi・
      クライアント領域の大きさ)に保存して閉じる(`MainWindow.open` = false・保存の失敗は無視して閉じる)。
    - `inspectorScroll`(MOVIEPAD_INSPECTOR_SCROLL): shotPath があり、CurrentCulture(OS の地域の書式。UI の言語・settings.json の language では変わらない)の数値として読める(double.TryParse)なら、
      同じ起点から 1200 ms 後に `InspectorView.scrollOffset` をその値にする。
    - `ttiPath`(MOVIEPAD_TTI): 読み込みの各段の経過時間を 1 行ずつそのファイルに追記する。行の書式は
      `[MoviePad][TTI] {ms,6} ms  {stage,-22}  ({label})`(ms は計測開始からの経過 ms を右寄せ 6 桁、stage は左寄せ 22 桁)+ 改行。
      書き込みの失敗は無視する(authority/Util/LoadProfiler.cs)。
    - `cacheDir`(MOVIEPAD_CACHE_DIR): `DiskCache.root` をそこにする。
  - openPath と scenario を両方指定すると、読み込みで `nextRegionId` が 2 になった後に ID 1〜3 の区間が入るので、次の分割が ID 2 を重複して
    振る(再現の対象とするかは UQ-SPEC-028)。
- 核/表面: core(出所: authority/Views/MainWindow.axaml.cs#ApplyScreenshotScenario・Util/LoadProfiler.cs)
- 受入観点: L2・exact(環境変数ごとの起動直後の状態)
- 画面: SCR-MAIN(EL-MAIN-WINDOW)・SCR-EXPORT(EL-EX-DIALOG)・SCR-ABOUT(EL-AB-DIALOG)・SCR-FFMPEG(EL-FF-OVERLAY)
- シナリオ: UC-230・UC-231・UC-232・UC-233・UC-234
- E-BOM 候補: E-DEBUG-001
- M-BOM 候補: M-DEBUG-001
- Control Plan 候補: CP-DEBUG-001

## 3. 不変条件(M-BOM へ前倒し)
| ID | 不変条件 | 関係する REQ | 検査する CP(または未検査の理由) |
|---|---|---|---|
| INV-001 | `Document.regions` は時刻順に隙間なく並び、先頭の start = trimStart・末尾の end = trimEnd・隣は end = 次の start。区間は 1 つ以上 | REQ-022, REQ-037, REQ-038, REQ-039, REQ-040, REQ-041 | CP-DOCMODEL-001 |
| INV-002 | 編集操作は新しい `Document` を作り、元(履歴のスナップショット)を変えない | REQ-022, REQ-071 | CP-DOCMODEL-001・CP-HISTORY-001 |
| INV-003 | 区間 ID は分割で `nextRegionId` から振り、`nextRegionId` は単調増加(元に戻すで戻らない)。通常の操作では ID は重複しない(MOVIEPAD_OPEN と SCENARIO の併用だけが重複を作る・UQ-SPEC-028) | REQ-020, REQ-037, REQ-094 | CP-TOOLBAR-001 |
| INV-004 | `Region.speed` は 0.01 単位(偶数丸め)かつ [0.25, 4.0]、`Region.volume` は 0.01 単位かつ [0.0, 2.0] | REQ-059, REQ-061 | CP-INSPECTOR-001 |
| INV-005 | 除外していない区間は常に 1 つ以上(最後の 1 つは除外できない) | REQ-064 | CP-INSPECTOR-001 |
| INV-006 | 再生ヘッドを動かす操作の後 `playhead` ∈ [trimStart, trimEnd](トリムの移動・Set In/Out の後は保証しない) | REQ-027, REQ-039, REQ-040 | CP-SELECTION-001 |
| INV-007 | 分割・境界・トリムの時刻はソースの fps の格子(SnapFrame・偶数丸め)に乗る | REQ-024, REQ-037, REQ-039, REQ-040, REQ-041 | CP-DOCMODEL-001 |
| INV-008 | `Clip` は一度設定されると null に戻らない | REQ-002 | CP-STARTUP-001 |
| INV-009 | 読み込みは最後に始めたものが勝つ(`loadGeneration` の世代で古い結果を捨てる)。キーフレームの結果も `copyCutGeneration` の世代で同じ | REQ-021, REQ-079 | CP-OPEN-001・CP-EXPORTDLG-001 |
| INV-010 | `History.past` は 50 件以下。新しい記録で `future` は空 | REQ-071 | CP-HISTORY-001 |
| INV-011 | exactCfr では、区間を分割/結合しただけでは出力(フレーム列・枚数・PTS・音声)が変わらない | REQ-085 | CP-EXPORT-001 |
| INV-012 | 書き出しは開始時の `ExportRun.request` に固定され、書き出し中の編集・形式の選択・読み込みの影響を受けない | REQ-020, REQ-076 | CP-EXPORTDLG-001 |
| INV-013 | 数値の表示書式(タイムコード・速度・fps・リード秒数・ffmpeg の引数の秒)はカルチャに依存しない(小数点はピリオド) | REQ-011, REQ-087 | CP-LOCALE-001 |
| INV-014 | 丸めは書き分ける: 編集・表示の丸めは偶数丸め、書き出しの時間計算は RoundHalfUp | REQ-024, REQ-085 | CP-DOCMODEL-001・CP-EXPORT-001 |
| INV-015 | 出力寸法は確定・スケール・縦横比の計算の後は偶数(Even)。上限・下限は入力した側だけに掛かる | REQ-067, REQ-068, REQ-069 | CP-INSPECTOR-002 |

## 3.5 DB / 永続化意図(DB がある場合)
DB は無い。アプリが持つ永続化はファイル 2 種とメモリのキャッシュだけ。
| Entity/Field | 意図 | REQ | E-BOM候補 | M-BOM候補 | Control Plan候補 |
|---|---|---|---|---|---|
| DB-ENT-001 | 設定ファイル `%LOCALAPPDATA%\MoviePad\settings.json`(`AppSettings.language` だけ・壊れていれば未設定・保存の失敗は無視) | REQ-012 | E-SETTINGS-001 | M-SETTINGS-001 | CP-SETTINGS-001 |
| DB-ENT-002 | 派生データのディスクキャッシュ `DiskCache`(キー = SHA1(パス|サイズ|更新時刻の Ticks) の 16 進の先頭 16 文字・中身は §2.16・上限 1 GiB・古い順に削除) | REQ-053, REQ-054 | E-MEDIA-001 | M-MEDIA-001 | CP-MEDIA-001 |
| DB-ENT-003 | キーフレームのメモ `KeyframeCache`(メモリのみ・(パス, 時刻 ms) → 時刻・打ち切りは覚えない) | REQ-080 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 |
| DB-ENT-004 | ffmpeg の取得先 `%LOCALAPPDATA%\MoviePad\ffmpeg`(ffmpeg.exe・ffprobe.exe・LICENSE/COPYING) | REQ-013, REQ-015 | E-FFMPEG-001 | M-FFMPEG-001 | CP-FFMPEG-001 |

## 4. 沈黙次元の第1回掃討(silence-checklist)
| 次元 | 宣言 | 内容/参照 |
|---|---|---|
| 表示要素集合・原典表示パリティ | specified | §2 の表示契約と `screens.json` の 12 画面 175 部品。到達しない表示(No project・クリップ情報・サムネイル進捗)は明記 |
| 日時表現(時刻・タイムコード) | specified | §1 の FormatTimecode / FormatClock。秒はソース基準の double。日付・タイムゾーンは扱わない |
| 数値書式・丸め | specified | §1 の偶数丸め / RoundHalfUp / SnapFrame / Even / FormatSpeed・INV-013・INV-014 |
| エラー語彙 | specified | 読み込みエラー 1 種(§2.7)・書き出しの結果 5 種+Exporting…(§2.20)・ffmpeg の取得 2 種(§2.6)。異常終了の経路(§2.6・§2.20) |
| 言語・翻訳 | specified | §2.4(120 キー・書き直す/書き直さない文言の区別) |
| 永続化 | specified | §3.5 |
| 非同期・競合 | specified | 読み込みの世代(INV-009)・キーフレームの世代・書き出し中の読み込み(§2.7)・メディアのキュー(§2.16)。非同期コマンドの実行中の無効表示はモデルに属性なし(UQ-SPEC-018) |
| 外部プロセス(ffprobe・ffmpeg・LibVLC) | specified | §2.6・§2.7・§2.16・§2.21。20 秒の打ち切り・BelowNormal |
| 時間の定数 | specified | 16 ms(PlaybackTick)・500 ms / 2000 ms(再生の監視・§2.10)・650 ms / 5000 ms / 2 回(シーク・§2.10)・0.02 秒(再シークの閾値)・12 秒 / 30 秒(サムネイルの抜き出しの打ち切り・§2.16)・180 ms(可視範囲のまとめ)・1200 ms(波形の待ち・INSPECTOR_SCROLL)・1800 ms(SHOT)・20 秒(ffprobe の打ち切り) |
| 入力の検証 | specified | 解像度の入力(§2.17)・ドロップの拡張子(§2.7)・カルチャ名(§2.4) |
| 終了時の保護 | specified | 確認なしで閉じる(§2.2・UQ-SPEC-003) |
| セキュリティ(取得物の検証) | specified | ffmpeg の SHA-256 の照合(§2.6) |
| 映像の描画・再生のタイミング | out-of-scope | 要求の範囲の定義で除く(§1・§2.10・§2.12) |
| アクセシビリティ(スクリーンリーダー・キーボードのフォーカス順) | exploratory | 要求に無い。元のアプリの既定(Avalonia)のまま。M-BOM で 3 択に解消する |
| 性能(読み込みの所要時間) | exploratory | MOVIEPAD_TTI の計測の作り込みだけ(§2.24)。目標値は要求に無い |
| 高 DPI・複数モニター | deferred-to-phase3 | 位置は物理 px・寸法は論理 px(§2.2)。収まるときの初期位置は UQ-SPEC-002。M-BOM で解消する |

## 5. トレース表
| TraceLink | REQ | 実現節 | E-BOM | M-BOM | Control Plan | 受入観点 |
|---|---|---|---|---|---|---|
| TL-REQ-SPEC-001 | REQ-001 | SPEC-STARTUP-001 | E-STARTUP-001 | M-STARTUP-001 | CP-STARTUP-001 | unit |
| TL-REQ-SPEC-002 | REQ-002 | SPEC-STARTUP-001 | E-STARTUP-001 | M-STARTUP-001 | CP-STARTUP-001 | L1 |
| TL-REQ-SPEC-003 | REQ-003 | SPEC-WINDOW-001 | E-WINDOW-001 | M-WINDOW-001 | CP-WINDOW-001 | L2 |
| TL-REQ-SPEC-004 | REQ-004 | SPEC-WINDOW-001 | E-WINDOW-001 | M-WINDOW-001 | CP-WINDOW-001 | L2 |
| TL-REQ-SPEC-005 | REQ-005 | SPEC-WINDOW-001 | E-WINDOW-001 | M-WINDOW-001 | CP-WINDOW-001 | L2 |
| TL-REQ-SPEC-006 | REQ-006 | SPEC-TITLEBAR-001 | E-TITLEBAR-001 | M-TITLEBAR-001 | CP-TITLEBAR-001 | L1 |
| TL-REQ-SPEC-007 | REQ-007 | SPEC-TITLEBAR-001 | E-TITLEBAR-001 | M-TITLEBAR-001 | CP-TITLEBAR-001 | L2 |
| TL-REQ-SPEC-008 | REQ-008 | SPEC-TITLEBAR-001 | E-TITLEBAR-001 | M-TITLEBAR-001 | CP-TITLEBAR-001 | L1 |
| TL-REQ-SPEC-009 | REQ-009 | SPEC-LOCALE-001 | E-LOCALE-001 | M-LOCALE-001 | CP-LOCALE-001 | unit |
| TL-REQ-SPEC-010 | REQ-010 | SPEC-LOCALE-001 | E-LOCALE-001 | M-LOCALE-001 | CP-LOCALE-001 | unit |
| TL-REQ-SPEC-011 | REQ-011 | SPEC-LOCALE-001 | E-LOCALE-001 | M-LOCALE-001 | CP-LOCALE-001 | L1 |
| TL-REQ-SPEC-012 | REQ-012 | SPEC-SETTINGS-001 | E-SETTINGS-001 | M-SETTINGS-001 | CP-SETTINGS-001 | unit |
| TL-REQ-SPEC-013 | REQ-013 | SPEC-FFMPEG-001 | E-FFMPEG-001 | M-FFMPEG-001 | CP-FFMPEG-001 | unit |
| TL-REQ-SPEC-014 | REQ-014 | SPEC-FFMPEG-001 | E-FFMPEG-001 | M-FFMPEG-001 | CP-FFMPEG-001 | L1 |
| TL-REQ-SPEC-015 | REQ-015 | SPEC-FFMPEG-001 | E-FFMPEG-001 | M-FFMPEG-001 | CP-FFMPEG-001 | L2 |
| TL-REQ-SPEC-016 | REQ-016 | SPEC-OPEN-001 | E-OPEN-001 | M-OPEN-001 | CP-OPEN-001 | L1 |
| TL-REQ-SPEC-017 | REQ-017 | SPEC-OPEN-001 | E-OPEN-001 | M-OPEN-001 | CP-OPEN-001 | unit |
| TL-REQ-SPEC-018 | REQ-018 | SPEC-OPEN-001 | E-OPEN-001 | M-OPEN-001 | CP-OPEN-001 | unit |
| TL-REQ-SPEC-019 | REQ-019 | SPEC-OPEN-001 | E-OPEN-001 | M-OPEN-001 | CP-OPEN-001 | L1 |
| TL-REQ-SPEC-020 | REQ-020 | SPEC-OPEN-001 | E-OPEN-001 | M-OPEN-001 | CP-OPEN-001 | unit |
| TL-REQ-SPEC-021 | REQ-021 | SPEC-OPEN-001 | E-OPEN-001 | M-OPEN-001 | CP-OPEN-001 | unit |
| TL-REQ-SPEC-022 | REQ-022 | SPEC-DOCMODEL-001 | E-DOCMODEL-001 | M-DOCMODEL-001 | CP-DOCMODEL-001 | unit |
| TL-REQ-SPEC-023 | REQ-023 | SPEC-DOCMODEL-001 | E-DOCMODEL-001 | M-DOCMODEL-001 | CP-DOCMODEL-001 | unit |
| TL-REQ-SPEC-024 | REQ-024 | SPEC-DOCMODEL-001 | E-DOCMODEL-001 | M-DOCMODEL-001 | CP-DOCMODEL-001 | unit |
| TL-REQ-SPEC-025 | REQ-025 | SPEC-DOCMODEL-001 | E-DOCMODEL-001 | M-DOCMODEL-001 | CP-DOCMODEL-001 | unit |
| TL-REQ-SPEC-026 | REQ-026 | SPEC-SELECTION-001 | E-SELECTION-001 | M-SELECTION-001 | CP-SELECTION-001 | unit |
| TL-REQ-SPEC-027 | REQ-027 | SPEC-SELECTION-001 | E-SELECTION-001 | M-SELECTION-001 | CP-SELECTION-001 | unit |
| TL-REQ-SPEC-028 | REQ-028 | SPEC-PLAYBACK-001 | E-PLAYBACK-001 | M-PLAYBACK-001 | CP-PLAYBACK-001 | unit |
| TL-REQ-SPEC-029 | REQ-029 | SPEC-PLAYBACK-001 | E-PLAYBACK-001 | M-PLAYBACK-001 | CP-PLAYBACK-001 | L1 |
| TL-REQ-SPEC-030 | REQ-030 | SPEC-TRANSPORT-001 | E-TRANSPORT-001 | M-TRANSPORT-001 | CP-TRANSPORT-001 | L1 |
| TL-REQ-SPEC-031 | REQ-031 | SPEC-TRANSPORT-001 | E-TRANSPORT-001 | M-TRANSPORT-001 | CP-TRANSPORT-001 | unit |
| TL-REQ-SPEC-032 | REQ-032 | SPEC-TRANSPORT-001 | E-TRANSPORT-001 | M-TRANSPORT-001 | CP-TRANSPORT-001 | unit |
| TL-REQ-SPEC-033 | REQ-033 | SPEC-PREVIEW-001 | E-PREVIEW-001 | M-PREVIEW-001 | CP-PREVIEW-001 | L2 |
| TL-REQ-SPEC-034 | REQ-034 | SPEC-PREVIEW-001 | E-PREVIEW-001 | M-PREVIEW-001 | CP-PREVIEW-001 | L1 |
| TL-REQ-SPEC-035 | REQ-035 | SPEC-PREVIEW-001 | E-PREVIEW-001 | M-PREVIEW-001 | CP-PREVIEW-001 | L2 |
| TL-REQ-SPEC-036 | REQ-036 | SPEC-TOOLBAR-001 | E-TOOLBAR-001 | M-TOOLBAR-001 | CP-TOOLBAR-001 | L1 |
| TL-REQ-SPEC-037 | REQ-037 | SPEC-TOOLBAR-001 | E-TOOLBAR-001 | M-TOOLBAR-001 | CP-TOOLBAR-001 | unit |
| TL-REQ-SPEC-038 | REQ-038 | SPEC-TOOLBAR-001 | E-TOOLBAR-001 | M-TOOLBAR-001 | CP-TOOLBAR-001 | unit |
| TL-REQ-SPEC-039 | REQ-039 | SPEC-TOOLBAR-001 | E-TOOLBAR-001 | M-TOOLBAR-001 | CP-TOOLBAR-001 | unit |
| TL-REQ-SPEC-040 | REQ-040 | SPEC-TLEDIT-001 | E-TLEDIT-001 | M-TLEDIT-001 | CP-TLEDIT-001 | unit |
| TL-REQ-SPEC-041 | REQ-041 | SPEC-TLEDIT-001 | E-TLEDIT-001 | M-TLEDIT-001 | CP-TLEDIT-001 | unit |
| TL-REQ-SPEC-042 | REQ-042 | SPEC-TLEDIT-001 | E-TLEDIT-001 | M-TLEDIT-001 | CP-TLEDIT-001 | L1 |
| TL-REQ-SPEC-043 | REQ-043 | SPEC-TLEDIT-001 | E-TLEDIT-001 | M-TLEDIT-001 | CP-TLEDIT-001 | L2 |
| TL-REQ-SPEC-044 | REQ-044 | SPEC-TLVIEW-001 | E-TLVIEW-001 | M-TLVIEW-001 | CP-TLVIEW-001 | L1 |
| TL-REQ-SPEC-045 | REQ-045 | SPEC-TLVIEW-001 | E-TLVIEW-001 | M-TLVIEW-001 | CP-TLVIEW-001 | unit |
| TL-REQ-SPEC-046 | REQ-046 | SPEC-TLVIEW-001 | E-TLVIEW-001 | M-TLVIEW-001 | CP-TLVIEW-001 | unit |
| TL-REQ-SPEC-047 | REQ-047 | SPEC-TLVIEW-001 | E-TLVIEW-001 | M-TLVIEW-001 | CP-TLVIEW-001 | unit |
| TL-REQ-SPEC-048 | REQ-048 | SPEC-TLVIEW-001 | E-TLVIEW-001 | M-TLVIEW-001 | CP-TLVIEW-001 | L2 |
| TL-REQ-SPEC-049 | REQ-049 | SPEC-TLVIEW-001 | E-TLVIEW-001 | M-TLVIEW-001 | CP-TLVIEW-001 | L2 |
| TL-REQ-SPEC-050 | REQ-050 | SPEC-MEDIA-001 | E-MEDIA-001 | M-MEDIA-001 | CP-MEDIA-001 | L2 |
| TL-REQ-SPEC-051 | REQ-051 | SPEC-MEDIA-001 | E-MEDIA-001 | M-MEDIA-001 | CP-MEDIA-001 | unit |
| TL-REQ-SPEC-052 | REQ-052 | SPEC-MEDIA-001 | E-MEDIA-001 | M-MEDIA-001 | CP-MEDIA-001 | unit |
| TL-REQ-SPEC-053 | REQ-053 | SPEC-MEDIA-001 | E-MEDIA-001 | M-MEDIA-001 | CP-MEDIA-001 | L2 |
| TL-REQ-SPEC-054 | REQ-054 | SPEC-MEDIA-001 | E-MEDIA-001 | M-MEDIA-001 | CP-MEDIA-001 | unit |
| TL-REQ-SPEC-055 | REQ-055 | SPEC-MEDIA-001 | E-MEDIA-001 | M-MEDIA-001 | CP-MEDIA-001 | unit |
| TL-REQ-SPEC-056 | REQ-056 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | L2 |
| TL-REQ-SPEC-057 | REQ-057 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | unit |
| TL-REQ-SPEC-058 | REQ-058 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | L2 |
| TL-REQ-SPEC-059 | REQ-059 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | unit |
| TL-REQ-SPEC-060 | REQ-060 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | L2 |
| TL-REQ-SPEC-061 | REQ-061 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | unit |
| TL-REQ-SPEC-062 | REQ-062 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | unit |
| TL-REQ-SPEC-063 | REQ-063 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | L1 |
| TL-REQ-SPEC-064 | REQ-064 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | unit |
| TL-REQ-SPEC-065 | REQ-065 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | unit |
| TL-REQ-SPEC-066 | REQ-066 | SPEC-INSPECTOR-001 | E-INSPECTOR-001 | M-INSPECTOR-001 | CP-INSPECTOR-001 | unit |
| TL-REQ-SPEC-067 | REQ-067 | SPEC-INSPECTOR-002 | E-INSPECTOR-002 | M-INSPECTOR-002 | CP-INSPECTOR-002 | unit |
| TL-REQ-SPEC-068 | REQ-068 | SPEC-INSPECTOR-002 | E-INSPECTOR-002 | M-INSPECTOR-002 | CP-INSPECTOR-002 | unit |
| TL-REQ-SPEC-069 | REQ-069 | SPEC-INSPECTOR-002 | E-INSPECTOR-002 | M-INSPECTOR-002 | CP-INSPECTOR-002 | unit |
| TL-REQ-SPEC-070 | REQ-070 | SPEC-INSPECTOR-002 | E-INSPECTOR-002 | M-INSPECTOR-002 | CP-INSPECTOR-002 | unit |
| TL-REQ-SPEC-071 | REQ-071 | SPEC-HISTORY-001 | E-HISTORY-001 | M-HISTORY-001 | CP-HISTORY-001 | unit |
| TL-REQ-SPEC-072 | REQ-072 | SPEC-HISTORY-001 | E-HISTORY-001 | M-HISTORY-001 | CP-HISTORY-001 | unit |
| TL-REQ-SPEC-073 | REQ-073 | SPEC-KEYBOARD-001 | E-KEYBOARD-001 | M-KEYBOARD-001 | CP-KEYBOARD-001 | L1 |
| TL-REQ-SPEC-074 | REQ-074 | SPEC-KEYBOARD-001 | E-KEYBOARD-001 | M-KEYBOARD-001 | CP-KEYBOARD-001 | L1 |
| TL-REQ-SPEC-075 | REQ-075 | SPEC-EXPORTDLG-001 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 | L1 |
| TL-REQ-SPEC-076 | REQ-076 | SPEC-EXPORTDLG-001 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 | L1 |
| TL-REQ-SPEC-077 | REQ-077 | SPEC-EXPORTDLG-001 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 | unit |
| TL-REQ-SPEC-078 | REQ-078 | SPEC-EXPORTDLG-001 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 | unit |
| TL-REQ-SPEC-079 | REQ-079 | SPEC-EXPORTDLG-001 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 | L2 |
| TL-REQ-SPEC-080 | REQ-080 | SPEC-EXPORTDLG-001 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 | unit |
| TL-REQ-SPEC-081 | REQ-081 | SPEC-EXPORTDLG-001 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 | L1 |
| TL-REQ-SPEC-082 | REQ-082 | SPEC-EXPORTDLG-001 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 | L1 |
| TL-REQ-SPEC-083 | REQ-083 | SPEC-EXPORTDLG-001 | E-EXPORTDLG-001 | M-EXPORTDLG-001 | CP-EXPORTDLG-001 | L1 |
| TL-REQ-SPEC-084 | REQ-084 | SPEC-EXPORT-001 | E-EXPORT-001 | M-EXPORT-001 | CP-EXPORT-001 | L3 |
| TL-REQ-SPEC-085 | REQ-085 | SPEC-EXPORT-001 | E-EXPORT-001 | M-EXPORT-001 | CP-EXPORT-001 | L3 |
| TL-REQ-SPEC-086 | REQ-086 | SPEC-EXPORT-001 | E-EXPORT-001 | M-EXPORT-001 | CP-EXPORT-001 | unit |
| TL-REQ-SPEC-087 | REQ-087 | SPEC-EXPORT-001 | E-EXPORT-001 | M-EXPORT-001 | CP-EXPORT-001 | L3 |
| TL-REQ-SPEC-088 | REQ-088 | SPEC-EXPORT-001 | E-EXPORT-001 | M-EXPORT-001 | CP-EXPORT-001 | L3 |
| TL-REQ-SPEC-089 | REQ-089 | SPEC-ABOUT-001 | E-ABOUT-001 | M-ABOUT-001 | CP-ABOUT-001 | L1 |
| TL-REQ-SPEC-090 | REQ-090 | SPEC-ABOUT-001 | E-ABOUT-001 | M-ABOUT-001 | CP-ABOUT-001 | unit |
| TL-REQ-SPEC-091 | REQ-091 | SPEC-VISUAL-001 | E-VISUAL-001 | M-VISUAL-001 | CP-VISUAL-001 | L2 |
| TL-REQ-SPEC-092 | REQ-092 | SPEC-WINDOW-001 | E-WINDOW-001 | M-WINDOW-001 | CP-WINDOW-001 | L2 |
| TL-REQ-SPEC-093 | REQ-093 | SPEC-TLVIEW-001 | E-TLVIEW-001 | M-TLVIEW-001 | CP-TLVIEW-001 | L2 |
| TL-REQ-SPEC-094 | REQ-094 | SPEC-DEBUG-001 | E-DEBUG-001 | M-DEBUG-001 | CP-DEBUG-001 | L2 |
| TL-REQ-SPEC-095 | REQ-095 | SPEC-WINDOW-001 | E-WINDOW-001 | M-WINDOW-001 | CP-WINDOW-001 | L2 |

## 6. PLM-ready 契約
- 仕様節は `SPEC-*` と見出しの anchor(要求の trace_links の `bomdd/20-spec.md#<anchor>`)で参照できる。SPEC-MEDIA-001 と SPEC-INSPECTOR-002 は
  anchor を持たないが、要求の anchor(#timeline-view・#inspector)の節の中に置く。
- 全 REQ が少なくとも 1 つの仕様節へ到達する(§5 で 95/95)。
- UI-IR / UI-BOM 参照: 本書は HTML モックから抽出していない(画面の正は authority/ の View と `screens.json`)。authority/bomdd/ui/ の
  ui-ir.json・ui-bom.json・ui-trace-map.json(メインウィンドウと export-dialog/)は元のアプリの側の過去の抽出物で、本書の正には使わない。
  そのため各節のテンプレートの「UI-IR / UI-BOM 参照」欄は置いていない。
- UI 表示要素は `screens.json` の `EL-*` を E-BOM / Control Plan へ接続する(§2 の各節の「画面」)。
- DB entity/field は `DB-ENT-*` として §3.5 に置く(DB は無い)。
- 未解決事項は下表に残す。blocker は 0 件(すべて元のアプリの動作で書けるか、受入で確かめる点)。

## 7. Unresolved Questions
| ID | Question | Severity | Owner | Affected refs | Status |
|---|---|---|---|---|---|
| UQ-SPEC-001 | 空状態(No project loaded・ツールバー等の非表示)は到達しない。到達しない作り込みとして再現するか、作らないか(要求の UQ-REQ-002-001)。本書はどちらでも到達経路を作らない | non-blocker | human | REQ-002 / SPEC-STARTUP-001 / EL-TB-NOPROJECT | open |
| UQ-SPEC-002 | 既定サイズが作業領域に収まるときのウィンドウの初期位置は MainWindow.axaml に WindowStartupLocation が無く、OS / Avalonia の既定に任されている(モデルは unknown)。再製造で何に固定するか、元のアプリを観測して合わせるか | non-blocker | human | REQ-003 / MainWindow.position / SPEC-WINDOW-001 | open |
| UQ-SPEC-003 | 閉じるときに未保存の変更の確認をしないのは要求漏れとして記録されている(UQ-REQ-005-001)。再製造でも確認なしのままでよいか。本書は元のアプリどおり確認なし | non-blocker | human | REQ-005 / CloseWindow / SPEC-WINDOW-001 | open |
| UQ-SPEC-004 | ffprobe/ffmpeg の起動の失敗・キーフレーム算出の 20 秒の打ち切りでアプリが異常終了することは、CommunityToolkit.Mvvm 8.4.0 と Avalonia の既定の例外の扱いから導いた(ライブラリのソースは読んでいない・UQ-REQ-014-001)。また異常終了の後の状態を表す属性がモデルに無く(MainWindow.open は変わらない)、シナリオ UC-194 は expect が unknown。L2 で ffmpeg を外した起動で確かめる前提でよいか | non-blocker | AI | REQ-014 / REQ-083 / ExportJob.statusMessage / UC-194 / SPEC-FFMPEG-001 / SPEC-EXPORTDLG-001 | open |
| UQ-SPEC-005 | ffmpeg の取得の結果(成功・SHA-256 の不一致・通信の失敗の後)と進捗の値は出来事(FfmpegInstallProgressReported・取得の完了)の後で決まり、シナリオは取得の開始と失敗の後の状態だけを持つ。成功と検証失敗の受入は L2 の実機(取得先を差し替えた試験)で行う前提でよいか | non-blocker | AI | REQ-015 / InstallFfmpeg / UC-191 / UC-192 / SPEC-FFMPEG-001 | open |
| UQ-SPEC-006 | 対応外の拡張子をドロップしたときに何も知らせないのは意図どおりか(UQ-REQ-017-001)。本書は元のアプリどおり無視 | non-blocker | human | REQ-017 / DropFile / SPEC-OPEN-001 | open |
| UQ-SPEC-007 | トリムが内部の境界をまたげない制約は製品の決定か(ソースのコメントは仕様判断事項・UQ-REQ-040-001)。本書は元のアプリどおり | non-blocker | human | REQ-040 / MoveTrimStart / MoveTrimEnd / SPEC-TLEDIT-001 | open |
| UQ-SPEC-008 | トリムで再生ヘッドがトリム範囲の外に残ったとき、インスペクターは前の編集対象を出し続ける。直さずに再現する前提でよいか(UQ-REQ-040-002) | non-blocker | human | REQ-040 / REQ-026 / EditSession.selectedRegionId / SPEC-SELECTION-001 | open |
| UQ-SPEC-009 | LibVLC の既定で速度を変えたときに音の高さが保たれるか(ピッチ維持オフの区間でもプレビューは高さを保つのか)は実機で未確認(UQ-REQ-028-001)。本書は「preservePitch をプレイヤーへ渡さない」ことまでを決める | non-blocker | AI | REQ-028 / PreviewPlayer.rateSentToPlayer / SPEC-PLAYBACK-001 | open |
| UQ-SPEC-010 | トランスポートの単位表示「h:m:frame / 時:分:フレーム」は実際の書式(分:秒:フレーム)と食い違う。文言を元のアプリどおり再現するか(UQ-REQ-031-001)。本書は再現する | non-blocker | human | REQ-031 / EL-TP-TIMECODE / SPEC-TRANSPORT-001 | open |
| UQ-SPEC-011 | 要求 REQ-050 は全体のフィルムストリップを「近似版の間は 0.4」と書くが、モデルの MediaPreviewData.filmstripApproximate は真になる経路が無い(キャッシュの正確版も高速版も近似ではないとして渡す)ので 0.4 は到達しない。本書はモデル(元のアプリの到達する動作)に従い常に 0.5 とした。要求の文の書き直しが要るか | non-blocker | AI | REQ-050 / MediaPreviewData.filmstripApproximate / EL-TM-THUMBNAILS / SPEC-MEDIA-001 | open |
| UQ-SPEC-012 | 要求 REQ-052 は波形のバケット数を clamp(長さ·40, 1000, 16000) と書くが、ソース(MediaPreviewService.BucketsFor)は (int)(長さ·40) の切り捨ての後に収める(モデルも floor と書く)。本書はソースに従った。要求の文の補足が要るか | non-blocker | AI | REQ-052 / MediaPreviewData.waveform / SPEC-MEDIA-001 | open |
| UQ-SPEC-013 | 編集対象が無いときのクリップ情報(Clip info)は、編集対象の再解決が常に先頭区間へ落ちるので到達しない。再製造で作るか(UQ-REQ-065-001) | non-blocker | human | REQ-065 / EditSession.hasSelection / EL-INS-CLIP-* / SPEC-INSPECTOR-001 | open |
| UQ-SPEC-014 | 速度・音量のスライダーで Thumb と RepeatButton が押下を処理済みにする(つまみ・トラックのドラッグで履歴が記録されない)のは Avalonia 12.0.0 の既定として書いた(フレームワークのソースは読んでいない・UQ-REQ-058-001・UQ-REQ-060-001)。受入の L2 で、つまみのドラッグ・トラックの押下・余白の押下の後の元に戻すの結果を元のアプリと比べる | non-blocker | AI | REQ-058 / REQ-060 / REQ-071 / BeginInteractiveEdit / SetSpeedContinuous / SPEC-INSPECTOR-001 | open |
| UQ-SPEC-015 | ミュートの解除(M キー)で元の音量でなく 100% に戻るのは意図どおりか(UQ-REQ-062-001)。本書は元のアプリどおり | non-blocker | human | REQ-062 / ToggleMute / SPEC-INSPECTOR-001 | open |
| UQ-SPEC-016 | 縦横比の維持で計算された側を上限で収めない(例: 1080×1920 で幅 7680 → 高さ 13654・UQ-REQ-067-001)こと、縦横比の切り替えだけでは未保存の変更にならないこと(UQ-REQ-068-001)を不具合として再現する前提でよいか。本書は再現する | non-blocker | human | REQ-067 / REQ-068 / OutputSettings.outputHeight / ToggleAspect / SPEC-INSPECTOR-002 | open |
| UQ-SPEC-017 | 幅・高さの入力欄は出力寸法に OneWay で結ばれる。(1) 打ったまま確定せずに別の操作(Scale など)で寸法が変わったとき打った文字が置き換わるか、(2) 確定でコードから Text を設定した後も結びつけが生きるか、(3) 確定でフォーカスが外れた先(InspectorView.focusedInput)は、Avalonia の既定でソースからは決まらない。元のアプリで観測して決める | non-blocker | AI | REQ-067 / REQ-074 / OutputSettings.widthInputText / InspectorView.focusedInput / SPEC-INSPECTOR-002 | open |
| UQ-SPEC-018 | Open と ConfirmExport の非同期コマンドの実行中(選択ダイアログ・解析・書き出しの間)はボタンが無効の表示になる(CommunityToolkit.Mvvm の既定・ライブラリのソースは読んでいない)が、この「実行中」の属性がモデルに無い(screens の model_gaps EL-TL-OPEN)。モデルに属性を足すか、M-BOM で扱うか | non-blocker | AI | REQ-016 / REQ-081 / EL-TL-OPEN / EL-EX-CONFIRM / SPEC-OPEN-001 | open |
| UQ-SPEC-019 | 言語のメニューが開いているかの属性がモデルに無く(OpenLanguageMenu は何も変えない)、EL-TB-LANG-JA / EN が使える条件をシナリオに書けない(screens の model_gaps)。属性を足すか | non-blocker | AI | REQ-008 / OpenLanguageMenu / EL-TB-LANGUAGE / SPEC-TITLEBAR-001 | open |
| UQ-SPEC-020 | 読み込み(新しいクリップ)で TimelineView.scrollOffset がどうなるかは要求に無い(ScrollViewer の内容幅が変わったときの扱いは Avalonia 任せ・モデルの質問)。元のアプリを観測して決める | non-blocker | AI | REQ-020 / REQ-045 / TimelineView.scrollOffset / SPEC-OPEN-001 | open |
| UQ-SPEC-021 | プレビューの同期状態(Disabled・Priming・Paused・SeekingPaused・StartingPlayback・Playing・SeekingPlayback・Faulted)とシークの再試行の回数を属性に入れるか。モデルは停止に戻る遷移を HaltPlayback にまとめ、playerAvailable・映像枠の初期値を unknown にした。本書は範囲外(再生のタイミング)の部分として HaltPlayback の契機だけを決める | non-blocker | human | REQ-029 / REQ-033 / HaltPlayback / PreviewPlayer / SPEC-PLAYBACK-001 | open |
| UQ-SPEC-022 | 出来事を経ないと検証できない要求(REQ-009 のキー集合、REQ-012 の保存内容、REQ-046 の再生中の追従、REQ-051〜055、REQ-084〜088 の書き出したファイル、REQ-091 のスタイル値、REQ-092、REQ-093、REQ-094 の SHOT・TTI・CACHE_DIR など)はシナリオの手順に無い。要求の acceptance_intent(unit / L2 / L3)で確かめる前提でよいか、画面に出ない属性をシナリオに書くことを許すか(シナリオの質問) | non-blocker | human | REQ-009 / REQ-012 / REQ-046 / REQ-051〜055 / REQ-084〜088 / REQ-091〜094 / SPEC-MEDIA-001 / SPEC-EXPORT-001 | open |
| UQ-SPEC-023 | スケールのプリセットの選択状態は元のアプリでは 100%・75%・50% ごとの独立の真偽値で同時に 2 つ以上が真になりうるが、モデルの OutputSettings.activeScalePreset は 1 値(screens の model_gaps)。本書は元のアプリどおり独立に判定する。モデルの属性を直すか | non-blocker | AI | REQ-069 / OutputSettings.activeScalePreset / EL-INS-SCALE-100 / SPEC-INSPECTOR-002 | open |
| UQ-SPEC-024 | 出力解像度・縦横比の維持・出力 fps が元に戻すの対象外なのは意図どおりか(UQ-REQ-071-001)。本書は元のアプリどおり対象外 | non-blocker | human | REQ-071 / History / SPEC-HISTORY-001 | open |
| UQ-SPEC-025 | 要求 REQ-079 は「ドキュメントが変わると先に求めた値は消える(帯・リードの表示も消える)」と書くが、元のアプリでは同じトリム開始のキーフレームを覚えていると、null にした直後に同期で同じ値が戻るので表示は残る(シナリオ UC-173 は元のアプリどおり)。本書は元のアプリに従った。要求の文の書き直しが要るか | non-blocker | AI | REQ-079 / ExportJob.copyCutStart / KeyframeCache / UC-173 / SPEC-EXPORTDLG-001 | open |
| UQ-SPEC-026 | 中断・ffmpeg の失敗のとき書き出し先に途中までのファイルが残る(削除しない・UQ-REQ-083-001)のを直さずに再現する前提でよいか。また ffmpeg が 0 以外で終了したときに何が残るか(空・途中まで・作られない)は ffmpeg の動作で決まり、モデルの partial は未確認 | non-blocker | human | REQ-083 / OutputFile.state / CancelExport / SPEC-EXPORTDLG-001 | open |
| UQ-SPEC-027 | 書き出しの失敗の文言がダイアログを開き直しても残るのは意図どおりか(UQ-REQ-083-002)。本書は元のアプリどおり残す | non-blocker | human | REQ-083 / ExportJob.statusMessage / SPEC-EXPORTDLG-001 | open |
| UQ-SPEC-028 | 起動時の環境変数(REQ-094)は利用者向けでない撮影・計測用の作り込みで、再製造で再現するか(could)の裁定が要る(UQ-REQ-094-001)。再現する場合、MOVIEPAD_OPEN と MOVIEPAD_SCENARIO を両方指定したときの区間 ID の重複(次の分割が ID 2 を重複して振り、FindById が先頭の一致を返す)も再現の対象とするか | non-blocker | human | REQ-094 / ApplyStartupEnvironment / EditSession.nextRegionId / INV-003 / SPEC-DEBUG-001 | open |
| UQ-SPEC-029 | 書き出し先の選択ダイアログ(既定のファイル名・種類)は ConfirmExport の途中で開くので、シナリオにはダイアログに見える値を確かめる手順が無い(シナリオの質問)。L1 の受入で ExportJob.suggestedFileName と種類の文言を直接確かめる前提でよいか | non-blocker | AI | REQ-081 / EL-SP-PICKER / EL-SP-FILENAME / SPEC-EXPORTDLG-001 | open |
| UQ-SPEC-030 | exactCfr の run ごとの境界(出力上の開始 T_k・出力フレームの範囲・読むソースフレーム)はモデルの属性に展開されていない(モデルの質問)。本書は要求 REQ-085 の式を正とし、受入 L3 はフレーム数・サンプル数・PTS の完全一致で見る。run ごとの属性を足すか | non-blocker | AI | REQ-085 / ExportRun.runs / SPEC-EXPORT-001 | open |
| UQ-SPEC-031 | タイムラインの最大スクロールは ScrollViewer(Padding 16,0,16,0)の Extent − Viewport で決まり、元のアプリの注記は「横の Padding 32 px が Extent を縮めるので EndPad 48 で補う」とする。Padding が Extent をどう変えるかは Avalonia 12.0.0 の既定の動作で、フレームワークのソースは読んでいない。L2 で最大スクロールの値(と追従・ズームの位置)を元のアプリと比べる前提でよいか | non-blocker | AI | REQ-045 / REQ-046 / REQ-093 / TimelineView.scrollOffset / SPEC-TLVIEW-001 | open |
| UQ-SPEC-032 | 要求 REQ-091 は Styles/Controls.axaml の完全一致の範囲をセレクターの列挙で書くが、列挙はファイルの全セレクターを覆っていない(共有のテンプレート・Button.btn StackPanel・Button.btn.icon.sm・Border.fmt:pointerover など)。本書は元のアプリの全セレクターを範囲にした。要求の列挙の書き直しが要るか | non-blocker | AI | REQ-091 / SPEC-VISUAL-001 | open |
| UQ-SPEC-033 | ショートカットはフォーカスのある部品が処理済みにしたキーを受けない(ウィンドウの OnKeyDown のクラスハンドラ)。どのコントロールがどのキーを取るか(Button の Space/Enter・Slider の矢印・CheckBox/RadioButton の Space など)は Avalonia 12 の既定に委ね、本書では列挙していない。L2 で元のアプリと作り直しの両方で、主要な部品にフォーカスがある状態の Space・←/→・Delete を比べて確かめる | non-blocker | AI | REQ-073 / SPEC-KEYBOARD-001 | open |

---
## ゲート記録(G2/G2')
- マルチリーダー監査: リーダー数 N= / 差分箇所= / 補正後再監査=
- MeasurementCapability: 全 REQ が adequate へ到達可能(unmeasurable ゼロ)= yes/no
  - human-approval-required の REQ と承認者:
  - 観測契約が必要な REQ(in-process):
- 原典パリティサインオフ(原典ありの移植・再現案件):
  - 原典表示要素の全数照合: done/not-needed
  - 未トレース表示要素: 0 件 / <件数と差し戻し先>
  - 承認者:
