# Change Order — ECO-075(配布 第 1 弾: handoff 契約の core/adapter 分割と product-profile 正本化 — SKILLS 13 本・写しの同期検査・AGENTS.md 参照・配員欄の文言境界〔filed〕)

> 裁定: user 2026-09-14 DECIDE「A」(Phase 7 を閉じて配布 ECO へ)→ 範囲の DISCUSS(第 1 弾= handoff のみ・運転層は第 2 弾)に user AGREE+境界条件 4 点(下記 §1-5)。**起票のみ**(製造裁定は別 DECIDE)。
> 出自= ECO-070(採用・配布は評価後)・ECO-071 節の第三者意見(core は汎用・現ファイルは BomDD 較正の distribution)・EXP-20260912-01 確定(2026-09-14・5/5・欠陥 4 類の再演 0)。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**。
- producer: EQ-001
- inspector: EQ-002
- 検査官(独立検査併用時): gpt-5.6-sol @ Codex CLI(入口 `bomdd-run --executor EQ-002 --report … --range …` から起動)。製造裁定 B(製造者較正のみ)なら inspector 行を外す。

## 0. 実測(起票根拠)

- **評価は確定**: EXP-20260912-01(v0.3/v0.4)= handoff 31+・DECIDE 5/5 が reply_format どおり・許容表外 0・申告送信 0・待機形 1 行・mode 訂正 0・第三者到達(Codex 報告のヘッダ)6/6・v0.2 の欠陥 4 類の
  再演 0(2026-09-14 回収)。ECO-070 の分岐「改善あり → product-profile 正本化を ECO で判断」の条件が揃った。
- **構造は記帳済み**: 第三者意見(2026-09-12・ECO-071 節)= 現 SKILL.md の BomDD 固有物 4 種(出自・配置履歴 / 生成規則のリポ前提 / 停止語彙の対応表 §2.6 / ECO 番号入りの例と §4 計測)。
  当方の読み替え= 出自は消さず adapter へ・core から adapter への参照 1 行・「監査記録は system of record に置き handoff は参照して再現しない」へ一般化。
- **現状の所在**: 正本= `.claude/skills/handoff/SKILL.md`(ハーネス側・ECO なしで新設 2026-09-11・v0.4)。`method/templates/product-profile/skills/` に handoff なし(12 本・bomdd-init.SKILLS も 12)。
  AGENTS.md は `.claude/skills/handoff/SKILL.md` を正本として参照。
- **運転層の結合(第 2 弾の理由)**: `bomdd-job.py` は required_skills の導出に自リポの `self-conformance.py` の正規表現を import する(`_load_selfconf`)。製品リポには self-conformance がなく
  unknown に落ちる。run 台帳の置き場(`.git/bomdd-run/`)・設備台帳のテンプレート・pre-push hook との関係も製品リポでは未設計。
- **配員欄の現行文言(実読・`method/templates/60-change-order.md`)**: 「job 射影が `required_capability` に解決し実在を確認する。台帳に無い ID・構文外は LEDGER_INCONSISTENT で工程が止まる」
  「入口 `bomdd-run --executor` と照合し … STOP INDEPENDENCE_FAIL」— これは BomDD 自リポの機構(ECO-072)であり、製品リポには job 射影も入口もない。**製品側では機械的な導出・検証・強制が
  存在するように読める**(user 指摘・境界条件)。

## 1. 変更要求(候補 — 製造裁定で凍結)

1. **core の正本**: `method/templates/product-profile/skills/handoff.md` を新設。内容= 契約 §1(v0.4 全文)・§2 classify/generate/validate/rewrite・§3 examples を **BomDD 固有語なし**で
   (ECO 番号・bomdd/ パス・Phase・run-02・R1〜R8・Codex を含めない)。生成規則の「監査記録はリポのファイルに置きパスで参照」は「detailed evidence lives in the system of record; the handoff
   references it rather than reproducing it」へ一般化。
2. **BomDD adapter**: 同ファイル末尾の明示区画 `## BomDD adapter`(または `handoff-bomdd.md`・製造裁定で決める)に、停止語彙の対応表(現 §2.6)・BomDD での system of record(order/register/
   reports のパス)・出自の所在(improvements.md 2026-09-11 節・ECO-070/071)を置く。core から adapter への参照 1 行を core 側に置く(到達性)。
3. **写し**: `.claude/skills/handoff/SKILL.md` を factory-delegate と同じ「写し」にする(冒頭注記+`{{METHOD}}` 相対解決・V2 の diff= 既知 hunk のみ)。現 §4 計測記録は improvements.md に
   あるので SKILL.md から除く(履歴は git)。
4. **kit と入口**: `bomdd-init.py` の SKILLS に `handoff`(12→13 本)・README の本数表記(C7)・AGENTS.md の「正本の所在」を product-profile/skills/handoff.md(写し `.claude/skills/`)へ。
   activation-map には足さない(毎ターン適用の契約で、台帳アンカーの class にならない)。
5. **配員欄の文言境界(user の境界条件・ECO-075 の適合条件)**: `method/templates/60-change-order.md` の `- producer:` / `- inspector:` の説明文を、**製品リポでは「記述可能な欄」であり機械的な
   導出・検証・強制は存在しない**と読める文言に改める(BomDD 自リポでの機械化は ECO-072 の注記として残し、製品側の機械化は第 2 弾候補と明記)。機械的 enforcement が存在するように
   読める表現を残さない。**ECO-075 は bomdd-job を配布せず、配員欄の enforcement を適合条件にしない**。
6. **第 2 弾候補の追跡**: improvements.md に EXP-20260914-01(運転層の製品配布: bomdd-job の self-conformance 非依存化・配員検査・run 台帳の配置・hook との関係)を **既知の未実装として記名**で
   残す(next trigger= 製品リポでの配員取り違えの実害 1 件 or user 裁定。実害が起きるまで無記名にしてよいという意味ではない)。

**採らない**: bomdd-job / bomdd-witness / bomdd-run / 設備台帳の配布(第 2 弾)/ 配員欄の enforcement を適合条件にする / activation-map への handoff 追加 / playbook 本文の改訂(handoff は方法論で
なくハーネス側の通信規約)/ 契約 v0.4 の内容変更(分割と配布のみ・契約は不変)。

## 2. 影響なし予測(製造前・起票時点 — 製造裁定で凍結)

diff= product-profile/skills/handoff.md(新規)・.claude/skills/handoff/SKILL.md(写し化)・bomdd-init.py(SKILLS 1 語)・README(本数)・AGENTS.md(所在 2 か所)・templates/60-change-order.md(配員欄の
文言)+台帳系+reports。self-conformance: C7(README 本数= SKILLS 実数 13)・C12(AGENTS.md リンク実在)・C13(新ファイルへのリンク)・C4/C14(kit 鮮度)は advisory。契約 v0.4 の意味は不変(V1 で core+
adapter の合計が現 SKILL.md の §1〜§3 と意味的に同一= 読解・V2 で写しの diff)。hooks・.github diff 0。製品リポは次回 kit 再設置から。

## 3. 受入(候補)

- **V1**: core(handoff.md の adapter 区画より前)に BomDD 固有語が 0(grep 表: `ECO-`・`bomdd/`・`Phase`・`run-02`・`R1`・`Codex`・`NORMATIVE_RULING` 等)。adapter 区画に集約。**V2**: 写しの diff が
  既知 hunk(冒頭注記・`{{METHOD}}` 解決)のみ。**V3**: self-conformance 全 PASS(C7 13 本)・CI 緑・窓。**V4**: 独立検査(製造裁定 A のとき: r1 境界探索「core に固有物が残っていないか・
  BomDD を知らない読者が契約を適用できるか」→ r2 是正確認+回帰・`--range` つきで起動・verified は inspection gate)。**V5**: 較正 receipt。**V6**: 60-change-order.md の配員欄に
  「機械的 enforcement が存在する」と読める語(解決・検証・止まる・STOP)が製品向け文言に残っていない(grep)。

## 3b. 製造裁定の候補(別 DECIDE で提示)

- **A** §1 の 1〜6 すべて+独立検査(Codex を「BomDD を知らない読者」の代役に: r1 境界探索 → r2 是正確認+回帰)。
- **B** §1 の 1〜6 すべて・製造者較正のみ(inspector 行を外す)。
- **C** 分割せず: 現 SKILL.md を単一ファイルのまま product-profile に正本化(固有物は残る)+4〜6。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-075` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用(user DECIDE A+DISCUSS AGREE+境界条件)。baseline `db44291`= **confirmed** / 次番 075= **confirmed**(grep 0)/ EXP-20260912-01 の回収= **confirmed**(improvements 行内)/
  SKILLS 12 本・handoff なし= **confirmed**(実読)/ 配員欄の現行文言= **confirmed**(実読・§0 引用)/ 同一ファイルへの進行中 ECO なし= **confirmed**。
- job ビュー: required_skills= `["calibrate", "preflight"]`・skills_missing= `["calibrate"]`(instrument-change クラス〔bomdd-init.py〕・製造時に応答)・required_capability= `{"producer": "EQ-001", "inspector": "EQ-002"}`・independent_inspection= `{"required": true, "inspector": "EQ-002"}`
- 開始判定: **PROCEED(起票のみ)**・override 0。製造は裁定後。

## 4. 製造と受入の実測

- (製造裁定後に記入)
