[INFORM / COMPLETE]

UNMEASURABLE 指定 commit に `bomdd/31-kbom.yaml` が存在せず、必須の裁定層4ファイルすべてを検索できないため

- inspector: EQ-002 / Codex CLI / GPT-5
- 対象: ViewTube `fe0250ef1c09fe3b642749b4636cdcdf17833d8a`（`git show` で読んだ）
- commit: 0 / ファイル変更: 0
- 開始時 HEAD・git status --short: HEAD=`fe0250ef1c09fe3b642749b4636cdcdf17833d8a`、既存の変更・未追跡ファイルあり / 終了時: HEADおよびstatusとも同一
- 読んだファイル一覧: `bomdd/32-mbom.yaml`、`bomdd/10-requirements.yaml`、`bomdd/20-spec.md`、`bomdd/30-ebom.yaml`
- 読み取り不能: `git show fe0250ef1c09fe3b642749b4636cdcdf17833d8a:bomdd/31-kbom.yaml` → `fatal: bad object`
- 禁止対象のファイルは読んでいない。ビルド・テスト・外部API呼び出しも実施していない。
- 開始時から存在した作業ツリーの変更は別作業によるものであり、当検査では一切変更していない。

## 分類表

必須裁定層の一つを検索できないため、盲検分類の正当な結果は作成しない。

## 集計

未集計（分類不能ではなく、検査入力欠落による測定不能）。

## 行ごとの区分の集合

未作成。

## 「人へ戻す」とした句の一覧

なし。K-BOM未検索の状態では「裁定層のどこにもない」と判定できない。

## 迷った句と決め方

該当なし。分類判断へ進む前に、必須入力の欠落で停止した。