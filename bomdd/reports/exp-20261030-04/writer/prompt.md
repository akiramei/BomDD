# 依頼: MoviePad のユースケースシナリオを書く

あなたの仕事は、動画編集アプリ MoviePad のユースケースシナリオを、決まった JSON の形で書くことです。
書いたシナリオは、あとで画面設計の確認に使います。

## 読んでよいもの・書いてよい場所

- 読んでよい: このフォルダ(`writer/`)、`../authority/`(MoviePad のソース一式・読み取り専用)、`../bindings.json`。
- 書いてよい: このフォルダ(`writer/`)だけ。
- それ以外のフォルダやリポジトリ(BomDD・MoviePad・MoviePad-Remake など)は開かないでください。`../authority/` も書き換えないでください。

## 何を書くか

- 利用者が MoviePad で実際にすること: 主な流れ(main)と、代替の流れ(alternate: 取り消す・やり直す・キャンセルする・
  別の入口から同じことをする・失敗から戻る など)。
- 書くのは「このアプリが実際にどう動くか」です。こう動くべきだ、という意見は書きません。
- 下の道具でシナリオが通らないときは、シナリオを消すのではなく、アプリが実際にする手順に直してください。
  どうしても直せないものだけ残して、最後の報告で理由を書いてください。
- 本数の目安は 10〜25 本。各シナリオは 2〜10 手順。利用者が本当にする流れを書いてください。
- 根拠は `../authority/README.md`・`README.ja.md`・`ViewModels/MainWindowViewModel.cs`・`Views/*.axaml` などを読んでください。

## 形(`writer/scenarios.json`)

```
{"states": [{"id": "...", "name": "日本語の説明", "predicate": {"<VMのプロパティ>": <値>, ...}}],
 "scenarios": [{"id": "UC-01", "title": "...", "goal": "...", "flow": "main" | "alternate",
                "setup": [<setup>],
                "steps": [{"in": "<状態id>", "action": "<操作id>", "surface": "<画面>", "expect": "<状態id>"}]}]}
```

- **操作 id** は `../bindings.json` の `Id`(44 種)だけが使えます: `Undo`・`Split`・`ApplySpeedPreset:0.5`・`ShowExportDialog` など。
  `surface` はその要素の `Surface`(`ToolbarView`・`InspectorView`・`TransportView`・`TimelineView`・`TitleBarView`・
  `ExportDialogView`・`AboutDialogView`・`MainWindow`)。
- **状態**は `MainWindowViewModel` の公開プロパティへの等式の組です(bool・数値・文字列・`null`・`"not-null"`)。
  道具は、同じ状態に入ったとき毎回、使える操作(有効・無効・非表示)とその行き先が同じであることを求めます。
  違うと「AMBIGUOUS」と出るので、そのときは状態を細かく分けてください。画面に効く変数は次の 15 個です:
  `CanDeleteBoundary CanRedo CanSetTrimIn CanSetTrimOut CanSplit CanUndo FfmpegInstalling HasClip HasLoadError HasSelection
  IsExporting ShowAbout ShowExport ShowFfmpegSetup ShowReset`。必要なら他のプロパティ(`Playing` など)も使えます。
- **setup**(開始点を作るためだけ): `{"set": "<プロパティ>", "value": <値>}`(例: `ShowFfmpegSetup` を false、`Playhead`、
  `UseExternalPlayback`)、`{"state_call": "<DocumentState のメソッド>", "args": [...]}`(`State = State.<メソッド>(...)`)。
  アプリは起動時にサンプル動画が読み込まれた状態から始まります(`Models/Sample.cs`)。
- ファイルダイアログや外部プロセスを使う操作(`Open`・`ConfirmExport`・`InstallFfmpeg`)は、その手順に `"harness": "no"` を付けます。
  その手順は実行されず、シナリオはそこで終わります(その手順までは確かめられます)。

## 道具(シナリオが実際に通るかを、アプリの画面の中心を動かして確かめる)

```
dotnet C:/Users/akira/AppData/Local/Temp/claude/C--Users-akira-source-repos-BomDD/c6a0cd2c-98cc-4b3c-bca7-73f54d8a43a0/scratchpad/exp04/harness/bin/Debug/net10.0/Harness.dll certify C:/Users/akira/AppData/Local/Temp/claude/C--Users-akira-source-repos-BomDD/c6a0cd2c-98cc-4b3c-bca7-73f54d8a43a0/scratchpad/exp04/bindings.json scenarios.json certify.json mockdata.json
```
(`writer/` で実行)。`FAIL`(どの手順がなぜ通らないか)・`AMBIGUOUS`(分けるべき状態)・`DROP` が出ます。
`certify.json` の `points` に、各手順の前後の変数の値があります。何度実行してもかまいません。

## 時間と報告

- 60 分以内に終えてください。
- 最後に、書いた本数・通った本数・直せなかったものとその理由を短く報告してください。
