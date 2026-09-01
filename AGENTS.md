# AGENTS.md — BomDD 方法論リポの作業入口(ハーネス中立)

本リポで作業する担当者(人間・AI・自動化)が最初に読む入口。**特定の AI ハーネスに依存しない**
形で作業規律だけを置く(Claude 固有の補足は [CLAUDE.md](CLAUDE.md))。

本リポは**方法論そのものの開発リポ**であり、製品リポではない。したがって `bomdd-init` が
製品リポへ設置する工程設備(process-core: hooks + lifecycle validator)は**設置しない**
(裁定: [ECO-025](bomdd/60-change-order-eco-025.md) — 変更管理は自己適用台帳と
`self-conformance` が担っており、二重統治にしない)。

## 作業規律(6 項目)

1. **変更前に自己適用台帳と対象手順を確認する** — 変更状態の正本は
   [bomdd/60-change-register.yaml](bomdd/60-change-register.yaml)。ハーネス
   (`method/tools/` `method/templates/` `.github/`)の変更は**起票なしに行わない**
   (register エントリ + `bomdd/60-change-order-eco-NNN.md`)。
2. **ローカル必須検査は指定された単一の入口から実行する**:

   ```bash
   python method/tools/self-conformance.py
   ```

3. **検査の終了コードを後続コマンド・pipeline・`echo` 等で上書きしない。**
   検査と後続操作を**条件で結ばずに同一の実行要求へ並べない** — 結果が観測される前に
   後続操作が実行されると、ゲートは存在しないのと同じになる。
4. **必須検査が非 0 終了または実行不能なら push しない。** 実行不能(測定不能)は合格ではない。
5. **push 後は対象 revision の CI 結論を確認する**:

   ```bash
   gh run list --repo akiramei/BomDD --limit 3
   ```

   ローカル全 PASS はクローズ条件ではない。赤なら次の作業へ進む前に是正または起票する。
6. **CI 未実行・到達不能・権限不足を成功として扱わない。** これらは `UNKNOWN` であって
   `PASS` ではない(例外的に先へ進める場合は、その旨を ECO かレジスタへ記録して残す)。

## 作業スキル(ハーネス非依存の契約)

`/preflight`(開始条件再認証)・`/converge`(設計収束)・`/calibrate`(証拠資格査定)の正本は
[method/templates/product-profile/skills/](method/templates/product-profile/skills/)
(Claude 用写し: `.claude/skills/`)。各ファイル冒頭の**自発起動契約は本リポで作業する
全ハーネスに適用される** — Claude 以外のハーネスもここから正本を読む。散文契約だけでは
起動が保証されない(実測あり)ため、非起動の一部は機械ゲートが捕捉する
(C16= order の converge receipt / C17= verified ECO の calibrate receipt)。

## 正本の所在

| 対象 | 正本 |
|---|---|
| 方法論の内容 | [method/](method/) — playbook・checklist・control-plan・onboarding ほか |
| 作業スキル(自発起動契約) | [method/templates/product-profile/skills/](method/templates/product-profile/skills/)(写し: `.claude/skills/`) |
| 実証データ | [FINDINGS.md](FINDINGS.md) |
| 改善の追跡(EXP/OBS) | [method/improvements.md](method/improvements.md)(一覧は `python method/tools/worklist.py`) |
| 変更状態 | [bomdd/60-change-register.yaml](bomdd/60-change-register.yaml) + 各 ECO order |
| 方法論固有の機械検査 | [method/tools/self-conformance.py](method/tools/self-conformance.py) |
| Claude 固有の補足 | [CLAUDE.md](CLAUDE.md) |

## 限界(この文書が担保しないこと)

本ファイルは**規範と入口**を与えるが、全規律を機械的に強制するわけではない。
規律 4 の **push 経路のみ** pre-push hook + PASS witness
([bomdd/hooks/pre-push](bomdd/hooks/pre-push)・ECO-046・設置検収= C18)が機械強制する —
到達目標は「うっかり型の素通り遮断」までで、対象は branch(`refs/heads/*`)のみ。
witness/hook の除去(意図的回避)は信頼境界外。規律 3 のチェーン自体と commit 段階は
明文化のまま自動検出されない。押し戻しの最終層は従来どおり CI(第 2 層)である。
