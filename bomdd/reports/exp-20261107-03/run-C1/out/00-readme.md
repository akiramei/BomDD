# MoviePad 出力フレームレート — 上流設計(原製品 126eae9 からの読み取り)

## 文書の一覧

| ファイル | 中身 |
|---|---|
| `00-readme.md` | この文書。範囲・出典の書き方・画面の言葉の約束 |
| `01-requirements.md` | 要求の整理(何がどう動くか)。要求ごとに出典 |
| `02-domain-model.md` | ドメインモデル(概念・状態・関係・取り消しの対象かどうか) |
| `03-behavior.md` | 振る舞い(操作ごとに前後で何が変わり、画面に何が出るか) |
| `04-questions.md` | 製品の持ち主に確認したいこと |
| `../examples.json` | 具体的な操作例 12 個(画面の言葉) |

## 範囲

「出力フレームレート」と、原製品でそれに関わるすべての振る舞い:

- インスペクターの「Output frame rate (fps)」プリセット(Source / 24 / 30 / 60 / 120)と、その強調・注記・ツールチップ
- 読み込み時の既定値(ソースの fps)と、ソース fps の取得(ffprobe)・VFR 判定
- タイトルバーの保存状態表示、取り消し/やり直しとの関係
- 書き出しダイアログの「Frame rate」表示、高速コピー(Fast, lossless (copy))の可否、VFR 注記
- 書き出し処理での fps の効き方(CFR 化・出力クロック)
- 出力 fps と**混同されやすいが別物**: タイムコード表示・1 フレーム送り・分割/トリムのフレームスナップは**ソース fps** を使う

## 出典の書き方

`MainWindowViewModel.cs:460` のように、`moviepad/` からの相対パスと行番号で示す。
VM = `ViewModels/MainWindowViewModel.cs`、Insp = `Views/InspectorView.axaml`、Exp = `Views/ExportDialogView.axaml`、
Exporter = `Services/FfmpegExporter.cs`。

## 画面の言葉の約束(examples.json も同じ)

- 画面の文言は**英語 UI**(`Resources/Strings.resx`、neutral)で書く。UI 言語は OS 既定または利用者の選択で
  日本語にもなる(`Services/Localizer.cs`、`Services/AppSettings.cs`)。対応する日本語は下表。
  数値(fps・タイムコード・速度)は言語によらず同じ表記(README.md:149)。
- `shows` の `active` / `not active` は、プリセットボタンでは「強調(選択中の見た目, `Classes.active`)されている/いない」、
  ツールバーの Undo / Redo などのコマンドボタンでは「押せる(有効)/押せない(無効)」を意味する。
- `visible` / `hidden` は、その要素が画面に出ている/出ていない。

| 英語 UI | 日本語 UI | 場所 |
|---|---|---|
| Output frame rate (fps) | 出力フレームレート (fps) | インスペクター下部「Output resolution」節の最下段 |
| Source | ソース | 同上、先頭のプリセット |
| Same as source (30 fps) | 元動画と同じ（30 fps） | Source のツールチップ |
| An fps higher than the source duplicates frames (quality does not improve). | ソースより高いfpsはフレーム複製になります（画質は向上しません）。 | プリセットの下の注記 |
| Frame rate | フレームレート | 書き出しダイアログのサマリ/クリップ情報 |
| Saved / Unsaved changes | 保存済み / 未保存の変更 | タイトルバー中央、ファイル名の右 |
| Fast, lossless (copy) | 高速・無劣化（コピー） | 書き出しダイアログのチェックボックス |
| Export | 書き出し | ツールバー右上のボタン / ダイアログの題名 |
| Cancel | キャンセル | 書き出しダイアログ右下 |
| Undo / Redo | 元に戻す / やり直す | ツールバー左のアイコン(ツールチップの文言) |
| Step forward 1 frame (→ / .) | 1フレーム進む (→ / .) | トランスポートのアイコン(ツールチップの文言) |
