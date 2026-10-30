# 依頼: 動画編集アプリのユースケースシナリオを書く

あなたの仕事は、デスクトップの動画編集アプリ **MoviePad** を作り直すための**ユースケースシナリオ**(`scenarios.json`)を、
決まった JSON の形で書くことです。利用者がどの画面のどの部品を使い、そのたびにアプリがどの状態になるかを、手順として
書きます。シナリオは、あとで設計の確認に使います。

## 読んでよいもの・書いてよい場所

- 読んでよい: このフォルダの中のファイルだけ。
  - `10-requirements.yaml` — 要求、`domain-model.json` — ドメインモデル、`screens.json` — 画面(どれも監査を通ったもの。
    直さないでください)
  - `authority/` — 元のアプリ MoviePad の一式。動作の正です。
  - `check_upstream.py`・`check_model.py` — 形を確かめる道具
- 書いてよい: このフォルダの `scenarios.json` と、作業用のファイルだけ。
- それ以外のフォルダやリポジトリは開かないでください。

## 何を書くか

- **状態**(`states`): ある画面に見えている値の組です。`screen` に画面の id、`shows` にドメインモデルの属性と、その状態での
  値を書きます。値が決められないときは `"unknown"` と書きます。
- **シナリオ**(`scenarios`): 要求ごとに、少なくとも一つ書きます(`requirement` に要求の id)。主な流れは `main`、別の流れや
  失敗の流れは `alternate`。
- **手順**(`steps`): `in` の状態から、`element`(画面の部品 id)を使って `operation`(その部品が起こす操作。
  `screens.json` の `invokes` と同じ名前)を `param` の引数で行うと、`expect` の状態になる、を一行ずつ書きます。行き先の
  状態が決められないときは `expect` を `"unknown"` にします。
- 動作は元のアプリが正です。元のアプリの不具合も、そのまま書きます。決められないところは、推測で埋めずに、トップレベルの
  `questions` に `{"subject": "...", "text": "..."}` で書きます。

## 形(`scenarios.json`)

```
{"states": [{"id": "ST-…", "screen": "SCR-…", "shows": {"実体名.属性名": <値>|"unknown"}}],
 "scenarios": [{"id": "UC-…", "title": "...", "requirement": ["REQ-…"], "flow": "main"|"alternate",
                "steps": [{"in": "ST-…", "element": "EL-…", "operation": "<操作>", "param": <値>|null,
                           "expect": "ST-…"|"unknown"}]}],
 "questions": [{"subject": "...", "text": "..."}]}
```

## 道具

```
python check_upstream.py scenarios scenarios.json screens.json domain-model.json 10-requirements.yaml
```
(このフォルダで実行)。形と、状態・部品・操作・要求の id が実在するかだけを確かめます。`ERROR` が出なくなるまで直してください。

## 時間と報告

- 60 分以内に終えてください。
- 最後に、状態・シナリオ・手順の数、要求でシナリオを書けなかったもの、迷ったところを短く報告してください。
- 書いたものは、あとで別の読み手が監査します。指摘が届いたら、一つずつ答えて、必要ならこのフォルダの `scenarios.json` を
  直してください。
