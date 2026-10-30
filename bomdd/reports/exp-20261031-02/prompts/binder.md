# 依頼: シナリオを元のアプリの view model に結びつける

デスクトップの動画編集アプリ **MoviePad** を作り直すために、ユースケースシナリオ(`scenarios.json`)が書かれました。シナリオは
作り直しの言葉(ドメインモデルの属性と、画面の部品)で書かれています。あなたの仕事は、そのシナリオを、**元のアプリの view
model の上でそのまま実行できる形**(`harness-scenarios.json`)に書き直すことです。書き直したものは、元のアプリの view model
を動かす道具が実行し、シナリオが元のアプリで書いたとおりに進むかを確かめます。

## 読んでよいもの・書いてよい場所

- 読んでよい: このフォルダの中のファイルだけ。
  - `scenarios.json` — 結びつけるシナリオ。`screens.json` — 画面と部品。`domain-model.json` — ドメインモデル。
  - `authority/` — 元のアプリ MoviePad の一式。view model は `authority/ViewModels/`、view は `authority/Views/` です。
  - `harness-schema.md` — 実行する道具が読む形と、その決まり(状態・動作 id・setup・実行できない手順の書き方)
  - `authority-bindings.json` — 道具が元のアプリから読み取った、部品ごとの command・引数・表示条件と、それが読む view
    model のパス
- 書いてよい: このフォルダの `harness-scenarios.json` と `binding-notes.json`、作業用のファイルだけ。
- それ以外のフォルダやリポジトリは開かないでください。

## 何をするか

- **状態**: `scenarios.json` の状態ごとに、同じ id で、`shows` の値を元のアプリの view model のプロパティの値として書いた
  `predicate` を書きます(`harness-schema.md` §3)。`"unknown"` の値は predicate に入れません。結びつけられない属性は
  predicate に入れず、`binding-notes.json` に書きます。
- **手順**: シナリオごと・手順ごとに、同じ順で、部品と操作と引数を、`authority-bindings.json` の動作 id(`<command 名>` または
  `<command 名>:<引数>`)と `surface` に結びつけます。`in` と `expect` は状態の id のままです(`expect` が `"unknown"` の手順は
  `"unknown"` のまま)。
- 開始点に command では届かない状態が要るときだけ、`setup` を使います(`harness-schema.md` §3)。
- ファイルダイアログや外部プロセスが要る手順は、`"harness": "no"` を付けます。
- シナリオの意味は変えません。足りない・合わないと思ったところは、直さずに `binding-notes.json` に書きます。

## 形

`harness-scenarios.json` は `harness-schema.md` §3 の形です(シナリオの `id` と状態の `id` は `scenarios.json` と同じ)。
`binding-notes.json`:
```
{"unbound_attributes": [{"state": "ST-…", "attribute": "実体名.属性名", "why": "..."}],
 "unbound_steps": [{"scenario": "UC-…", "step": <番号>, "why": "..."}],
 "notes": [{"where": "...", "text": "..."}]}
```

## 時間と報告

- 60 分以内に終えてください。
- 最後に、結びつけた状態と手順の数、結びつけられなかったものの数、迷ったところを短く報告してください。
