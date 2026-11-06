## 作業の境界(共通)

- 読んでよいのは、このフォルダ(以下「作業フォルダ」)の中のファイルだけです。それ以外のフォルダ・リポジトリ・ネットワークは使わないでください。
- 書いてよいのは、作業フォルダの `out/` の中と、作業フォルダ直下の `examples.json` だけです。
- コードは書きません。アプリの実行もしません。
- 時間は 45 分以内です。

## 資料

- `sources/README.md`・`sources/README.ja.md` — MoviePad(動画編集アプリ)の説明書
- `sources/10-requirements.yaml` — MoviePad の再実装のために書かれた要求
- `cad/actions.json` — 画面にある操作の一覧(操作 id・置かれた画面・ボタンの文言)
- `cad/observations.json` — 画面で読み取れる表示の一覧(名前と意味)
- `cad/start-screen.json` — 起動直後の画面を観測した値(サンプル動画が読み込まれ、ffmpeg の案内は閉じ、再生ヘッドを 20 秒へ動かした状態)
- `check_examples.py` — `examples.json` の形を確かめる道具

## 納品物

1. `out/` の中の文書(形式・ファイル数は自由)。
2. `examples.json` — 具体的な操作例を決まった形で書いたもの(下記)。

## `examples.json` の形

```
{"examples": [{"id": "EX-01", "title": "...", "basis": "<資料のどこに基づくか>",
               "steps": [{"action": null または "<操作 id>", "expect": {"<表示名>": <値>}}]}]}
```

- 各例は起動直後の画面(`cad/start-screen.json`)から始まります。
- 最初の手順の `action` は `null`(何も押さず、起動直後の画面について書く)か操作 id。2 番目以降の手順は、操作を 1 つ押します。
- `expect` は、その手順のあとに画面に出ている値です。
- 押すのは、その時点で使えるボタンだけです。ボタンが使えないことを言いたいときは、押さずに `*_enabled` の表示を `false` と書いてください。
- 例で使える操作は次だけです: `Undo`・`Redo`・`Split`・`DeleteSelectedBoundary`・`SetTrimIn`・`SetTrimOut`・`ApplySpeedPreset:*`・`ApplyVolumePreset:*`・`Scale:*`・`SetFps:*`・`ToStart`・`ToEnd`・`StepBack`・`StepForward`(`*` は `cad/actions.json` にある値)。
- 値は、真偽は `true`/`false`、数は秒・パーセント・ピクセルで小数 3 桁まで。区間は「選択中の区間」の表示(`selected_*`)だけで指せます。
- 例は 3〜30 個、各例の手順は 1〜15 個。
- `python check_examples.py examples.json`(作業フォルダで実行)で形を確かめられます。値は確かめません。何度実行してもかまいません。

## 最後の報告

作った文書の一覧、例の数、迷ったところを短く報告してください。
