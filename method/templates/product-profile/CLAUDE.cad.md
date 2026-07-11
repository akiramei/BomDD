# {{CAD}} — {{PRODUCT}} の UI/UX 設計原器(CAD)

このリポは **CAD(設計原器)** であり、製品コードは存在しない。**ここでは実装しない**。
非 Claude ハーネス(Codex 等)の入口は [AGENTS.md](AGENTS.md)(同じ正本群を指すポインタ)。

## 役割と規律

- **権威**: 製品 UI の適合はモック+本リポの screens 文書を基準に測る。実装と乖離したら
  **常に CAD が正**([docs/02_mock_fidelity_policy.md](docs/02_mock_fidelity_policy.md))。
  CAD 側を直す(意図的 mock 是正)場合は必ず裁定記録を残す。
- **裁定台帳**: 未確定事項と決定は [docs/review_points.md](docs/review_points.md)。
  複数選択肢の比較が要る裁定は `docs/decisions/` に裁定資料(事実表+選択肢+diff 規模+推奨)を
  作り、人間の裁定(gate①)を待つ。
- **設計の流れ**: デザインツール出力(モック)を `資料/` へ → 画面ごとの挙動仕様を
  `docs/screens/<screen>.md` に散文で固定 → 製品リポの UI-IR/BOM 抽出の入力にする。
- **製品リポ**: `../{{PRODUCT}}`。CAD の決定を製品へ取り込むときは、製品側で ECO を起票する
  (`/eco-file`。CAD コミットが先・製品コミットが後)。

## 構成

```
資料/            デザインツール出力(モック HTML・スクリーンショット)
docs/screens/    画面ごとの挙動仕様(製造の入力)
docs/decisions/  裁定資料(選択肢比較と決定記録)
docs/review_points.md  裁定台帳(一覧)
```

方法論の正典: `{{METHOD}}`。人間向け協働ガイド: `{{METHOD}}/method/onboarding/working-with-ai.md`。
