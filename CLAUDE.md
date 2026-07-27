# CLAUDE.md — 本リポ(BomDD 方法論リポ)の運用規律

方法論の内容は `method/` が正本。本ファイルは**このリポで作業するときの運用規律**だけを置く
(方法論の一般則は書かない — 一般則は `method/bomdd-playbook-v1.md` へ)。

## 変更管理(自己適用)

- ハーネス(`method/tools/` `method/templates/` `.github/`)の変更は
  **起票なしに行わない** — `bomdd/60-change-register.yaml` + `bomdd/60-change-order-eco-NNN.md`。
- 検証は `python method/tools/self-conformance.py`(`--dotnet` で C9 も)。

## push したら CI 結論を確認する(ECO-020)

**ローカルの self-conformance 全 PASS はクローズ条件ではない。** push 後に GitHub Actions の
結論を確認し、赤なら次の作業へ進む前に是正または起票する。

```bash
gh run list --repo akiramei/BomDD --limit 3
```

理由(実測): C11 導入(ECO-015)から **11 コミット・約 2 日・5 ECO を跨いで CI が赤のまま
潜伏**した。各 ECO でローカル全 PASS は確認していたが、**CI の結果を一度も見ていなかった** —
ECO-006 で CI を常設した目的(一括検証の入口)が、結果を観測する経路の欠落で無効化されていた
(装置・操作対象はあり、**結線だけが無い**)。ローカルと CI の環境差(git identity の有無)は
検査側で吸収するが(ECO-020)、**環境差は今後も起こりうる**前提で結論を見る。

- 赤を持ち越さない。持ち越す場合は理由と期限を ECO かレジスタへ記録する。
- CI 結論を機械検査へ組み込むこと(④)は**採らない裁定**(ECO-020 gate ①)— リポ内検査を
  リポ外状態へ依存させると、測定不能(API 不達・未実行・権限不足)の扱いを誤って新たな
  fail-open / 誤 FAIL を生むため。必要が実測されてから判断する。

## 未整備(観測 — 本ファイルは入口ではない)

本リポには製品リポ向けに `bomdd-init` が生成する **ハーネス中立入口(AGENTS.md)が無い**
(ECO-010 は製品リポ側のみを対象とした)。本ファイルは運用規律の置き場であって入口ではない。
入口整備の要否は別途裁定する。
