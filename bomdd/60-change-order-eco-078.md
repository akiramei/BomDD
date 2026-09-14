# Change Order — ECO-078(ECO-077 還元の織り込み: 報告の正本経路を 1 つに固定する — playbook §3 の 1 段落+factory-delegate 工程 5 の検査官ブリーフ欄〔文書のみ〕)

> 裁定: user 2026-09-15 DECIDE「1:A 2:A」(lesson-promote の織り込み案 2 節を両方採用)。記帳は commit bbac82c(improvements.md 2026-09-15 還元節)で完了済み。
> **起票と製造を同一 commit で行う**(文書のみ・ECO-069/076 の型)・受入は製造者較正のみ。verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で。
> factory-delegate 正本は method/templates(ハーネス)のため AGENTS.md 規律 1 により起票する(前例= ECO-069: 工程 5 の range 欄の織り込み)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**。
- producer: EQ-001
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)。

## 0. 実測(起票根拠)

- 出典= [improvements.md 2026-09-15 還元節](../method/improvements.md)(ECO-077 r2 1 回目の報告上書き・3 例目)。命題= 証拠の出力座標には書き手を 1 つだけ置く。委譲では報告の正本経路を
  1 つに固定し他方を禁止する。受理側は verdict の回収と証拠十分性を別に検査する(hash は同一性の証明で十分性の証明ではない)。
- 3 例(独立): ViewPrism2 ECO-082/083(後続 run が試験結果を上書き)/ ET-001(並列 run が同一出力を上書き)/ ECO-077 r2(検査官のファイルをハーネスの最終メッセージが上書き)。
- 織り込み案(user 採用): ①playbook §3 独立検査規則の報告様式段落に 1 段落 ②factory-delegate 工程 5 に「報告の正本経路を 1 つ宣言する」bullet(+写し再生成)。

## 1. 変更要求(凍結・文書のみ)

1. `method/bomdd-playbook-v1.md` §3: 「本規則は前向き適用であり…再解釈しない。」の直後に **報告の正本経路** の段落(環境非依存・ツール名は実例として括弧内のみ)。
2. `method/templates/product-profile/skills/factory-delegate.md` 工程 5: 検査官ブリーフの役割欄 bullet の直後に **報告の正本経路を 1 つ宣言する** bullet。写し `.claude/skills/factory-delegate/SKILL.md` は
   正本から再生成(既知 2 hunk)。
3. `method/improvements.md` 2026-09-15 還元節に織り込み実施の 1 行。

**採らない**: 報告サイズの閾値 gate / bomdd-run の必須節検査(OBS-20260915-01 のトリガー待ち)/ 60-change-order テンプレの変更 / Codex `-o` 固有の記述を正本に置くこと(実例として括弧内のみ)。

## 2. 影響なし予測(製造前・凍結)

diff= playbook 1 段落+factory-delegate 正本 1 bullet+写し+improvements.md 1 行+台帳系(order・register)。tools・hooks・.github・他 templates は diff 0。C7 13 本不変・C12/C13 リンク先不変
(新規リンクなし)・写しの diff= 既知 2 hunk・`{{METHOD}}` 0・worklist 新規 ID 0・警告 0。

## 3. 受入

- **V1** grep: playbook §3 に `報告の正本経路`・factory-delegate 正本と写しに `報告の正本経路を 1 つ宣言する`(各 1)。
- **V2** 写しの diff= 既知 2 hunk(8c8,12・10c14)のみ・`{{METHOD}}` 0。
- **V3** self-conformance 全 PASS(exit 0 観測後に commit)・CI 緑・窓= allowed_paths のみ。
- **V4** 製造者較正のみ。**V5(非クローズ条件)**: 効果= 次の独立検査ブリーフで報告経路の読み違いが 0(OBS-20260915-01 のトリガー「同型 2 例目」で観測)。

## /preflight receipt(起動経路: **自発** — 既裁定の適用実装〔織り込み〕)

- 分類= 既裁定の適用実装(user 1:A 2:A)。baseline `bbac82c`= **confirmed**(git log -1)/ 次番 078 未使用= **confirmed**(grep 0)/ 挿入位置の実在(§3「再解釈しない。」・工程 5 役割欄 bullet)=
  **confirmed**(実読)/ 同一ファイルへの進行中 ECO なし(ECO-077 は verified)= **confirmed**。
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-15・同一 commit)

- 製造物: playbook §3 段落 / factory-delegate 正本 bullet / 写し(再生成)/ improvements.md 1 行。
- **V1**・**V2**= §5 に実測。**V3**= §5(観測後)。

## 5. クローズ(2026-09-15・verified)— 実測と受入

- **V1**= PASS(grep: playbook `報告の正本経路` 1・正本/写し `報告の正本経路を 1 つ宣言する` 各 1)。**V2**= PASS(写しの diff= 8c8,12・10c14 の 2 hunk のみ・`{{METHOD}}` 0)。worklist 警告 0。
- **V3**= self-conformance 全 PASS(exit 0 観測後に witness → 入口 dry ADVANCE → 製造 commit)→ push → CI 結論は受入 commit で記す。
- 実測(正直記載): self-conformance 1 回目 **exit=1・C1/C3/C16/C17 FAIL**(register 重複キー `source`)。機序= 受理側の register 編集で、ECO-078 ブロックを ECO-077 エントリの
  `receipt_author_role` 行(status 直後に置いていた)をアンカーに挿入したため、ECO-077 の `source` 以降が ECO-078 ブロックの後ろへ回った。製造物の欠陥ではなく台帳編集の手順欠陥
  (アンカーが「エントリ末尾」でなかった)。是正= ブロックを末尾へ移動・厳格パースで 78 件・ECO-077 のキー 13 件を確認 → 2 回目を実行。ゲートは機能した(commit 前に停止)。
- **V3**= PASS(2 回目 全 PASS → witness 363aba516fd3 → 入口 dry ADVANCE → 製造 commit 7e060c9 → push → CI run 34867400275 **success**)。diff 監査の窓: baseline `bbac82c` → head `7e060c9`
  (**窓閉鎖**・受入 commit は台帳系のみ)。窓内= allowed_paths のみ。
- **V4**= 製造者較正のみ(独立検査なし)。register: `implemented → verified`・head 凍結・`receipt_author_role: producer`。
- **V5(非クローズ条件)**: 次の独立検査ブリーフで報告経路の読み違い 0 を OBS-20260915-01 のトリガー「同型 2 例目」で観測。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格。文書のみの変更・著者役割= producer)

- 査定した主張と判定:
  1. 「playbook §3 と factory-delegate 工程 5・写しに命題が入った」— **observed / 適格**(grep 1/1/1・V1)。
  2. 「写しは正本と同期」— **observed / 適格**(diff 2 hunk・`{{METHOD}}` 0・V2)。
  3. 「正本は環境非依存(ツール名は括弧内の実例のみ)」— **observed / 適格**(実読: 規範文に Codex・`-o` は出ず、実例は括弧内)。
  4. 「織り込みは読み違いを消す」— **unknown(未測定)**: 効果は次の独立検査ブリーフでしか測れない(OBS-20260915-01)。
- 検出した計器欠陥(帰属つき): 製造物 0 件。受理側 1 件= register 編集のアンカー誤り(重複キー → C1/C3/C16/C17 が正しく FAIL・計器は健全・手順欠陥)。
- 検出力の限界: 効果未測定・独立検査なし・製品リポでの配布結果(bomdd-init 後の写し)は未測定。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | grep・diff(V1/V2) |
  | Q2 | asked | NA 相当 | — | 文書変更に known-bad 対照なし(宣言)。register 重複キーは意図しない known-bad として C1/C3/C16/C17 の発火を実測 |
  | Q3 | asked | observed/適格 | 実測 | 変更前(§3・工程 5 に報告経路の規則なし)→ 変更後(段落 1・bullet 1) |
  | Q4 | asked | 読解 | 読解 | 「書き手 2 つで後勝ち」は 3 例からの一般化(improvements 2026-09-15 節) |
  | Q5 | asked | observed/適格 | 実測 | 未測定(効果・独立検査・配布)を宣言 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測(1 回目 FAIL → 是正 → 2 回目 PASS)→ witness → 入口 dry → commit → push → CI success |
  | Q7 | asked | NA | — | 陽性対照なし(文書) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness(ECO-078.json)・register・commit 7e060c9・run 台帳(ECO-078.jsonl) |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= playbook / 正本 / 写し / 記帳の 4 文書 |

- このクローズが支持しないもの: 織り込みの効果(次の独立検査で観測)/ 機械化(OBS-20260915-01 のトリガー待ち)/ 製品リポでの適用結果。
- 実測(正直記載・受入段): 入口 dry が **STOP LEDGER_INCONSISTENT**(register verified・order のクローズ節見出しに verified 語なし)→ 見出しを是正して再実行。ゲートは機能した(受入 commit 前に停止)。
- 実測(正直記載・受入段 2 回目): 再び STOP LEDGER_INCONSISTENT — クローズ節の検出正規表現は「N. クローズ」の直結を要求(「実測とクローズ」は不一致)。見出しを「5. クローズ(…verified)」へ是正。
