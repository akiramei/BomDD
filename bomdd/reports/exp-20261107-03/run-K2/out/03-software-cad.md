# ソフトウェアCADと振る舞いの対応 — 出力フレームレート

正本CADの場所・版: 原製品 MoviePad 126eae9 の Avalonia 画面定義(`moviepad/Views/*.axaml`)を CAD として参照する。別の画面仕様は作らない。
資料の性質: 既存画面の**定義**(コード)と、利用者手引きの静止画(docs/images/10, 11)。アプリは実行していない(画面を動かして観測したものではない)。
補助: 設計モック `design_handoff_moviepad/`(出力fps の操作は無い。差は C-2)。
確認者と確認範囲: AI 一人の机上読解のみ。
対象画面: メインウィンドウ(タイトルバー・ツールバー・再生コントロール・インスペクター)、書き出しダイアログ。

要素IDは本書内の参照用の短い名前(画面定義に x:Name は無い)。`active/not active` の意味は要素の種類で分ける:
- プリセットボタン(出力fps・再生速度): `active` = 強調表示(`Classes.active`)。
- ツールバーの元に戻す/やり直す: `active` = 押せる(`IsEnabled`)。
- 注記・欄・チェックボックス: `visible/hidden` = `IsVisible`。

## 画面と要素

| 画面ID | 要素ID | 種類・役割(画面の文言) | 操作・引数／観測 | 対応する要求・契約 | 根拠と未決 |
|---|---|---|---|---|---|
| MAIN/INSPECTOR | E-FPS-SRC | ボタン「ソース」 | 押す: SetFps("source") → 出力fps = ソースfps。観測: 強調 | R-01,R-03,R-07,R-14 / B-01,B-03 | InspectorView 91-93 |
| MAIN/INSPECTOR | E-FPS-24 / -30 / -60 / -120 | ボタン「24」「30」「60」「120」 | 押す: SetFps("24") 等。観測: 強調 | R-01,R-03 / B-02 | InspectorView 94-101 |
| MAIN/INSPECTOR | E-FPS-HINT | 注記「ソースより高いfpsはフレーム複製になります（画質は向上しません）。」 | 観測: visible/hidden | R-04 / B-02 | InspectorView 103-104 |
| MAIN/INSPECTOR | E-FPS-LABEL | 見出し「出力フレームレート (fps)」 | 観測のみ | R-01 | InspectorView 88 |
| MAIN/INSPECTOR | E-CLIPINFO-FPS | 「クリップ情報」欄の「フレームレート」行(値「30 fps」) | 観測: 欄ごと visible/hidden | R-15 / B-12 | InspectorView 247-270(fps 行 258-261)。通常操作で hidden(C-1) |
| MAIN/INSPECTOR | E-SPEED-PRESET-2 / E-SPEED-VALUE | 「再生速度」の「2x」ボタン / 大きな数値 | 履歴に入る編集の代表として使う | R-08,R-13 / B-07,B-08 | InspectorView 144-170(速度プリセット 155-168) |
| MAIN/TITLEBAR | E-STATUS | ファイル名右の状態表示「保存済み」/「未保存の変更」 | 観測: 文字 | R-07,R-17 / B-01,B-02,B-03 | TitleBarView 36-37、Strings Status_* |
| MAIN/TOOLBAR | E-UNDO / E-REDO | アイコンボタン(ツールチップ「元に戻す」「やり直す」) | 押す: Undo/Redo。観測: 押せるか | R-08 / B-07 | ToolbarView 22-27 |
| MAIN/TOOLBAR | E-EXPORT | ボタン「書き出し」(右上) | 押す: 書き出しダイアログを開く | R-05 / B-05 | ToolbarView 64-68 |
| MAIN/TRANSPORT | E-STEPF / E-TC | 「1フレーム進む」アイコンボタン / 現在位置タイムコード `M:SS:FF` | 押す: StepFrame(+1)。観測: 文字 | R-09 / B-09 | TransportView 21-33 |
| EXPORT | E-EXP-FPS | サマリ行「フレームレート」の値 `N fps` | 観測: 文字 | R-05 / B-05 | ExportDialogView 111-114 |
| EXPORT | E-EXP-COPY | チェックボックス「高速・無劣化（コピー）」を含む枠 | 観測: visible/hidden(押すと書き出し方式が変わる) | R-06 / B-06 | ExportDialogView 83-87 |
| EXPORT | E-EXP-CANCEL / E-EXP-OK | 「キャンセル」/「書き出す」 | 押す | R-17 / B-10 | ExportDialogView 157-162 |

## 表示と操作可否

| 要素ID | 状態から表示・選択・可否への関係 | どの場面で成立するか | 根拠・由来区分 |
|---|---|---|---|
| E-FPS-SRC | active ⇔ \|OutFps − SourceFps\| < 0.05 | クリップ読込中は常時 | VM 460 / SOURCE_DERIVED |
| E-FPS-24..120 | active ⇔ FormatSpeed(OutFps) == ボタンの数字(文字列一致)。FormatSpeed は `0.##`(小数 2 桁で丸め、末尾 0 除去、言語に依存しない書式) | 常時 | VM 459・TimeMath.FormatSpeed・EqualsConverter / SOURCE_DERIVED |
| E-FPS-SRC と数値の同時強調 | ソースfps が 24/30/60/120 のどれかと文字列一致すれば 2 つ同時に強調。29.97 素材なら「ソース」だけ強調(30 は強調されない)。どれも強調されない状態は原製品では生じない(押せる値は 5 つだけ・既定はソース) | 常時 | 上 2 行からの導出 / SOURCE_DERIVED。30 fps は画像 10/11 で確認(外観) |
| E-FPS-HINT | visible ⇔ OutFps > SourceFps + 0.05 | 常時 | VM 461 / SOURCE_DERIVED |
| E-FPS 群全体 | インスペクター全体が `HasClip` のときだけ表示。出力fps ボタンに無効化条件は無い(常に押せる) | クリップ読込中 | InspectorView 8-9 / SOURCE_DERIVED |
| E-EXP-FPS | 文字 = FormatSpeed(OutFps) + " fps" | ダイアログ表示中 | ExportDialogView 113 / SOURCE_DERIVED |
| E-EXP-COPY | visible ⇔ CanFastExport(実ファイル・mp4 形式・解像度/速度/fps 無変更・H.264/H.265・音声条件・単一連続区間)。**fps 変更はそれだけで hidden にする十分条件**。fps 無変更時の visible はコーデック等に依存 | ダイアログ表示中 | VM 214-224・ExportPlan.Analyze / SOURCE_DERIVED、QUICKSTART §5 / SOURCE_EXPLICIT |
| E-STATUS | 「未保存の変更」⇔ Edited。SetFps は値の変化にかかわらず Edited=true | 常時 | VM 343・855-856 / SOURCE_DERIVED |
| E-UNDO | 押せる ⇔ 履歴に戻り先がある。出力fps の変更では増えない | 常時 | VM 330・SetFps / SOURCE_DERIVED |
| E-TC | `M:SS:FF`、FF = floor(秒の小数部 × **ソースfps**) | 常時 | TimeMath.FormatTimecode・VM 335 / SOURCE_DERIVED |
| E-CLIPINFO-FPS | visible ⇔ 選択区間なし。読込直後は先頭区間を選択し、以後も再生ヘッド直下へ再同期するため通常は hidden | 常時 | VM 533・ResolveSelection / SOURCE_DERIVED |

表示形式の言語: 数値(fps・タイムコード)は言語非依存(README の Localization 節)。ラベルは日本語/英語の 2 言語。英語 UI での文言差は 01 を参照。

## 画面遷移・操作前後

| 操作例 | 操作前 | 操作 | 操作後の画面・観測 | 根拠・確認範囲 |
|---|---|---|---|---|
| EX-01 | 30fps 読込直後 | なし | ソース・30 強調、注記なし、保存済み、クリップ情報なし | 机上 / NOT_RUN |
| EX-02 | 同上 | 「24」 | 24 のみ強調、注記なし、未保存の変更 | 机上 / NOT_RUN |
| EX-03 | 同上 | 60→120→24→ソース | 注記 visible→visible→hidden→hidden、最後はソース・30 強調 | 机上 / NOT_RUN |
| EX-04/05 | 同上 | 「ソース」/「30」(値は不変) | 強調は不変、未保存の変更 | 机上 / NOT_RUN |
| EX-06/07 | 同上 | 書き出し→キャンセル→120→書き出し / 60→書き出し | ダイアログの「フレームレート」が 30 fps→120 fps / 60 fps、コピー枠 hidden | 机上 / NOT_RUN |
| EX-08/09 | 同上 | 2x→24→元に戻す→やり直す / 60 | 速度だけ戻り 24 は残る / 元に戻すは押せないまま | 机上 / NOT_RUN |
| EX-10 | 同上 | 60→1フレーム進む×2 | タイムコード 0:00:00→0:00:01→0:00:02(ソース 30fps 単位) | 机上 / NOT_RUN |
| EX-11 | 同上 | 2x→書き出し | 出力fps の選択は不変、ダイアログ 30 fps、コピー枠 hidden(速度変更のため) | 机上 / NOT_RUN |

静止画(画像 10/11)から確定したのは「30fps 素材で 2 つ同時強調」「ダイアログに 30 fps」の外観だけ。押した結果はコードからの導出であり、実画面で動かした観測ではない。

## 不足と次に触って確かめること

06 の「次に人間が触って確かめる範囲」を参照(EX-01・EX-04・EX-08 の 3 本を最初に触る)。
