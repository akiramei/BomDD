# AGENTS.md — エージェント向け入口(ハーネス中立)

このリポジトリは **{{PRODUCT}} の UI/UX 設計原器(CAD)** です。製品コードは存在せず、
**ここでは実装しません**。あなたのハーネスの種類に関わらず、以下が正本です。

## 最初に読む

- 運用宣言の全体: [CLAUDE.md](CLAUDE.md)(Claude Code 向けアダプタ — 本ファイルと
  同じ正本群を指す)
- 権威の規律: [docs/02_mock_fidelity_policy.md](docs/02_mock_fidelity_policy.md)
  (実装と乖離したら**常に CAD が正**。CAD 側を直す場合は必ず裁定記録を残す)

## 裁定と記録(このリポに入口スキルはない)

- 裁定台帳: [docs/review_points.md](docs/review_points.md)
- 裁定資料: `docs/decisions/`(事実表+選択肢+diff 規模+推奨を作り、人間の裁定
  〔gate①〕を待つ — **自然文の了承を裁定に昇格させない**)
- 画面仕様: `docs/screens/`・モック: `資料/`

## 製品への反映

CAD の決定を製品へ取り込むときは**製品リポ側で ECO を起票**する
(`../{{PRODUCT}}` の AGENTS.md / CLAUDE.md 参照。CAD コミットが先・製品コミットが後)。
