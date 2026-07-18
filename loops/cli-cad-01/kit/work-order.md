# Work Order: CLI「worklist」の新規製造

## 製造範囲

[cli-cad.md](cli-cad.md)(設計正本)が規定する CLI「worklist」を**新規に実装**する。

- 成果物 1: `worklist.py` — Python 3・標準ライブラリのみ・単一ファイル。作業ディレクトリ直下へ納品。
- 成果物 2: `assumptions.md` — 実装中に置いた**仮定・解釈の全件記録**(下記)。

## 入力資料(この kit 内のみ)

- [cli-cad.md](cli-cad.md) — CLI の設計正本(文法・解析意味論・出力・終了・環境の契約)。
- [schema-excerpt.md](schema-excerpt.md) — 上位正本(入力データ= 記帳スキーマ v1 の意味論)。
- `fixtures/` — 入力例 5 件(f1〜f5)。**期待出力は同梱しない**(仕様である — 受入は独立検査で行う)。

## 規律

- **kit 外の情報参照の禁止**: web・他リポジトリ・kit 外のファイルを参照しない。
  同名の既存実装を探索しない。
- **未規定次元(cli-cad.md §U)は実装者裁量で決定してよい** — ただし置いた仮定・解釈・
  裁量決定は `assumptions.md` へ全件記録する(1 行 1 件: 何を・どう決めたか・根拠)。
  cli-cad.md 自体(未規定台帳を含む)は変更しない。
- 質問がある場合は発注者へ提出してよいが、回答は「その次元は未規定 — 実装者裁定とし
  assumptions.md へ記録」に限られる。
- fixtures を自分で実行して動作確認してよい(期待出力の突合は受入側の仕事)。

## 完了条件

`worklist.py` と `assumptions.md` の納品。
