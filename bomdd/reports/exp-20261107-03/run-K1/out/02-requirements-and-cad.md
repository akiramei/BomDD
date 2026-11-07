# 02 要求候補とソフトウェアCADの対応

正本は原製品 `moviepad/`(126eae9)。ここは要求の**候補**の抽出であり、原資料を書き換えない。
位置は `moviepad/` からの相対パス:行。由来区分は kit/docs/artifact-contract.md §2。
「VM」= `ViewModels/MainWindowViewModel.cs`、「Insp」= `Views/InspectorView.axaml`、「Dlg」= `Views/ExportDialogView.axaml`、
「Exp」= `Services/FfmpegExporter.cs`、「ja」= `Resources/Strings.ja.resx`。

## 1. 要求候補

条件 / 操作 / 結果 / 観測 / 適用時点 に分けて書く。

| ID | 条件 | 操作 | 結果(状態) | 観測(画面・外部出力) | 時点 | 根拠 | 区分 |
|---|---|---|---|---|---|---|---|
| R-01 | 動画を開く | 開く | 出力 fps = 元動画の fps(上限なし) | 「ソース」が選択表示 | 読込完了時 | VM:536, tests ResolutionTests.cs:50-61(144/60/30/23.976) | SOURCE_EXPLICIT |
| R-02 | 動画あり | プリセット 24 / 30 / 60 / 120 を押す | 出力 fps = その値 | 押したボタンが選択表示 | 操作完了時 | VM:850-857, Insp:94-101, QUICKSTART.ja.md:113 | SOURCE_EXPLICIT |
| R-03 | 動画あり | 「ソース」を押す | 出力 fps = 元動画の fps | 「ソース」が選択表示 | 操作完了時 | VM:852-853 | SOURCE_EXPLICIT |
| R-04 | 常時 | — | — | 「ソース」の選択表示は \|出力 fps − 元 fps\| < 0.05 のとき | 常時(派生) | VM:460, Insp:91-93 | SOURCE_EXPLICIT |
| R-05 | 常時 | — | — | 数値プリセットの選択表示は、出力 fps を小数 2 桁以内の文字列(`0.##`・不変カルチャ)にしたものとボタンの文字が一致するとき | 常時(派生) | VM:459, Models/TimeMath.cs:47-52, Converters/EqualsConverter.cs:12-17 | SOURCE_EXPLICIT |
| R-06 | R-04 と R-05 から | — | — | 元 30 fps で出力 30 のとき「ソース」と「30」が**同時に**選択表示。ボタンは排他ではない | 常時 | R-04+R-05 | SOURCE_DERIVED |
| R-07 | 常時 | — | — | 出力 fps > 元 fps + 0.05 のとき注記「ソースより高いfpsはフレーム複製になります（画質は向上しません）。」を表示。それ以外は隠す | 常時(派生) | VM:461, Insp:103-104, ja:125 | SOURCE_EXPLICIT |
| R-08 | 動画あり | 任意の fps プリセットを押す(値が変わらなくても) | 編集済み = true | タイトルバー「未保存の変更」 | 操作完了時 | VM:856, VM:344, ja:65 | SOURCE_EXPLICIT(Q-02 で確認候補) |
| R-09 | — | fps プリセットを押す | 履歴(Undo スタック)に**積まない**。出力 fps は文書状態(DocumentState)の外 | Undo / Redo で出力 fps は変わらない | 常時 | VM:125(OutFps は VM の項目), VM:850-857(Snapshot 呼ばず), VM:691-712(Undo/Redo は State だけ差替) | SOURCE_DERIVED |
| R-10 | 出力 fps が元 fps と 0.05 以上違う | — | ストリームコピー不可 | 書き出しダイアログの「高速・無劣化（コピー）」を隠す | 常時(派生) | Exp:473, Exp:482, VM:214-225, Dlg:83-84, QUICKSTART.ja.md:132-136 | SOURCE_EXPLICIT |
| R-11 | 出力 fps が元 fps と 0.05 未満の差 | — | fps はコピー可否を妨げない(他の条件=コーデック・速度・音量・解像度・単一区間に依存) | トグルの表示は他の条件次第 | 常時 | Exp:470-484 | SOURCE_EXPLICIT |
| R-12 | 書き出しダイアログを開いている | — | — | サマリ「フレームレート」に `<出力 fps の 0.## 表記> fps` | 常時(派生) | Dlg:110-114, VM:459 | SOURCE_EXPLICIT |
| R-13 | 区間が選択されていない(通常は起きない、R-17) | — | — | インスペクターのクリップ情報「フレームレート」に `<元 fps の 0.##> fps` | 常時(派生) | Insp:247-262, VM:441 | SOURCE_EXPLICIT |
| R-14 | 常時 | 「ソース」にポインタを重ねる | — | ツールチップ「元動画と同じ（<元 fps> fps）」 | 常時 | VM:443, Insp:93, ja:124 | SOURCE_EXPLICIT |
| R-15 | 別の動画を開く | 開く | 出力 fps = 新しい動画の fps、編集済み = false、履歴クリア、高速コピー OFF | 「保存済み」 | 読込完了時 | VM:526-559 | SOURCE_EXPLICIT |
| R-16 | 書き出し成功 | 書き出す | 編集済み = false。出力 fps は保持 | 「保存済み」、ダイアログを閉じる | 書き出し完了時 | VM:1064-1070 | SOURCE_EXPLICIT |
| R-17 | 動画を開いた直後 | — | 選択 = 最初の区間(区間は 1 個・全長) | クリップ情報欄は隠れる → 元 fps の「フレームレート」行は見えない | 読込完了時 | VM:533, Models/DocumentState.cs:49-50, Insp:114, Insp:247 | SOURCE_DERIVED |
| R-18 | 常時 | 1 フレーム送り・フレームスナップ・分割・境界移動・タイムコード | **元動画の fps** を使い、出力 fps は使わない | タイムコード `M:SS:FF` の FF は元 fps 基準 | 常時 | VM:305, VM:335-336, VM:643, VM:718-729, Models/TimeMath.cs:20-44 | SOURCE_EXPLICIT |
| R-19 | 再エンコード書き出し | 書き出す | 出力の公称レートを有理数 `-r p/q` で指定(q∈{1,1001} で厳密に表せる値)。速度変更・fps 変更・VFR 素材なら fps で CFR 化 | 出力ファイル(観測不能・NOT_RUN) | 書き出し時 | Exp:150-170, Exp:261-264, Services/ExportClock.cs:96-106, 156-165 | SOURCE_EXPLICIT(未実行) |
| R-20 | 動画の解析 | 開く | 元 fps = avg_frame_rate(無ければ r_frame_rate、どちらも無ければ 30)。avg と r の差が max(0.1, 0.5%) を超えれば VFR | — | 読込時 | Services/MediaProbe.cs:88-98, Models/TimeMath.cs:12 | SOURCE_EXPLICIT |
| R-21 | VFR 素材・コピー有効 | — | — | 注記(Export_CopyVfrNote)を表示 | 常時 | VM:234, Dlg:90-91 | SOURCE_EXPLICIT(今回の開始状態=固定 fps では出ない) |
| R-22 | 常時 | — | fps の数値表記は言語に依存しない | — | 常時 | README.md:149 | SOURCE_EXPLICIT |

属性と表示義務の区別:

- 出力 fps の**値**は常に保持される(R-01〜R-03)。画面に値そのものを**常に出す義務は原製品に無い**。インスペクターではボタンの選択表示(R-04/R-05)でしか見えず、
  プリセット以外の値(例: 元が 29.97 や 144)は「ソース」の選択表示だけになる。数値が文字で出るのは書き出しダイアログ(R-12)だけ。
- 元 fps も保持されるが、文字で出る場所(R-13)は通常隠れており(R-17)、見える経路はツールチップ(R-14)とダイアログが「ソース」選択時に出す値。
  モック(inspector.jsx:148)の「フレームレート 30 fps」は未選択時の例で、一般の表示義務にしない。
- プリセットの数値の並び(24/30/60/120)は原製品と QUICKSTART が一致して明記している。任意値の入力欄は原製品に無い。これを「任意値は禁止」とは書かない(未規定)。

## 2. ソフトウェアCAD対応(既存の画面定義を参照)

CAD 正本 = 原製品の XAML(`Views/*.axaml`)。ここは参照表であり、手書きの別 CAD ではない。モックは出力 fps 部品を持たない。

| 画面要素(日本語 UI の文言 / 英語) | 定義位置 | 結ぶ要求 | 表示・操作可否 |
|---|---|---|---|
| インスペクター下部 見出し「出力フレームレート (fps)」/ "Output frame rate (fps)" | Insp:88-89, ja:122 | — | 動画があるとき見える(Insp:8-9 `HasClip`) |
| プリセット「ソース」/ "Source" | Insp:91-93 | R-03, R-04, R-14 | 常に押せる。選択表示 = `FpsSourceActive` |
| プリセット「24」「30」「60」「120」 | Insp:94-101 | R-02, R-05 | 常に押せる。選択表示 = 文字一致 |
| 注記「ソースより高いfps…」 | Insp:103-104, ja:125 | R-07 | `FpsUpsampling` のとき見える |
| クリップ情報「フレームレート」/ "Frame rate" | Insp:247-262 | R-13, R-17 | 区間未選択のときだけ見える |
| タイトルバーの保存状態 | Views/TitleBarView.axaml:36 | R-08, R-15, R-16 | 「未保存の変更」/「保存済み」 |
| ツールバー「書き出し」/ "Export" | Views/ToolbarView.axaml:64-68 | R-12 | ダイアログを開く |
| 書き出しダイアログ サマリ「フレームレート」 | Dlg:110-114 | R-12 | ダイアログ表示中 |
| 書き出しダイアログ「高速・無劣化（コピー）」 | Dlg:83-86 | R-10, R-11 | `ShowFastExport` のとき見える |
| 書き出しダイアログ「キャンセル」 | Dlg:157 | — | 書き出し中でなければ閉じる(VM:881-885) |
| ツールバー「元に戻す」/「やり直す」(アイコン) | Views/ToolbarView.axaml:22-27 | R-09 | `CanUndo` / `CanRedo` で有効 |
| トランスポート「1フレーム進む (→ / .)」・タイムコード | Views/TransportView.axaml:21, 29 | R-18 | — |
| インスペクター「再生速度」プリセット「2x」等 | Insp:155-167 | R-09 の確認用(履歴に積む操作) | 区間選択時に見える(Insp:114) |

キー操作で出力 fps を変える経路は無い(`SetFps` の呼出しは Insp のボタンだけ。grep で確認)。
