# Change Order — ECO-081(配布 第 2 弾: 運転層の契約と設備台帳の文書配布 — product-profile に運転層契約〔core/adapter〕・70-equipment.yaml テンプレート・register の配員注記〔記述欄〕・機械検査なし)

> 裁定: user 2026-09-19「ECO-062 第 2 弾の運転層配布に進んで」→ 範囲の DECIDE(A 契約と台帳の文書配布 / B 機械検査を process-core に載せる / C ツールごと移植)に **user「A」**。
> 設備台帳の初期値は user 指定なし → 雛形のみ(値は placeholder)。**起票のみ**(製造裁定は別 DECIDE)。
> 出自= ECO-075 §1-6 の第 2 弾候補(EXP-20260914-01・既知の未実装の記名追跡)。ECO-062 §7 の現在地= 配布 第 2 弾。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- inspector: EQ-002
- 検査官(独立検査併用時): 製造裁定 A で inspector 行が有効(gpt-5.6-sol @ Codex CLI・入口 `bomdd-run --executor EQ-002 --report … --range …`)。B/C なら独立検査は行わず、inspector 行は製造裁定時に除く。

## 0. 実測(起票根拠)

- **第 2 弾の残課題(EXP-20260914-01・4 項目)**: bomdd-job の self-conformance 非依存化 / 配員欄の機械検査 / run 台帳の配置と hook / 設備台帳テンプレート。user DECIDE A(2026-09-19)で
  本 ECO の範囲は「契約と台帳の文書配布」— 4 項目のうち設備台帳テンプレートと配員の記述先を配布し、機械検査・ツール配布・hook は範囲外(実害 1 件 or 裁定で再開)。
- **製品側の変更管理は process-core**(実読 `method/templates/process-core/process-profile.yaml`): profile が register の場所(既定 `bomdd/60-change-register.yaml`)と状態語彙
  (既定 `[staged, applied]`・ViewTube 型 3 状態)を決め、hooks(pre-commit / commit-msg)と `process-validator.py`(1,013 行)が強制する。ViewTube の実物: register= `bomdd/process/change-register.yaml`・
  ECO 本文= `bomdd/eco/ECO-VT-NNN.md`(自由形式・260 本)・**配員欄なし**(ECO-VT-166 実読: producer/inspector/EQ- の一致 0)。
- **運転層 3 ツールは自リポの配置に結合**(実読): `bomdd-job.py:86` activation-map を `method/templates/…` の相対パスで参照・`:91` self-conformance.py を import・`:107` register の状態語彙を
  自リポの語彙(filed / in-progress / implemented / verified)に限定・`bomdd-run.py:503` `bomdd/70-equipment.yaml`。停止語彙 10 語(`bomdd-job.py:57`)と配送先表(`bomdd-run.py:81`)は
  ツール間で 1 対 1。合計 2,464 行(job 881 / run 829 / witness 754)。
- **ViewTube は独自の設備検査を持つ**(`bomdd/hooks/commit-msg` 実読: 「process equipment missing from prospective index」・ECO-VT-164/165): 装置パスを staged にする commit は ECO を
  名乗る、という検査。設備の概念は製品側で先に芽生えており、配布物はこれと衝突しない形(記述欄・機構なし)でなければならない。
- **product-profile の現状**(実読): README.md / change-management.md に witness・run・job・運転層の語 0。`bomdd-init.py:46` は `[0-9][0-9]-*.yaml` を製品の `bomdd/` へ複写する
  (`70-equipment.yaml` を templates に置けば bomdd-init の変更なしに配布される)。`60-change-register.yaml` テンプレには `# receipt_author_role` の**注記欄の前例**(記述欄・gate にしない・ECO-077)。
  `60-change-order.md` の配員欄は ECO-075 で「製品リポでは記述欄・機械化なし」と明記済み。
- **既裁定との関係**: ECO-025(自リポに process-core を設置しない= 二重統治にしない)の裏返しとして、製品側に運転層ツールを置くと process-validator との二重統治になる(範囲 C を退けた理由)。
  converge 凍結時の裁定(証明のための複雑性を足さない)により、実害未観測の機械検査(範囲 B)は採らない。

## 1. 変更要求(候補 — 製造裁定で凍結)

1. **`method/templates/product-profile/operator-layer.md` 新規**(handoff.md と同じ core/adapter 形): **core(環境非依存・固有語なし)**= ①運転層の 3 形式(job / receipt / ruling)は
   既存の台帳(register・order・検査結果・裁定記録)の**射影**であり、二重正本を作らない ②停止語彙 10 語と配送先(次 / 人 / 工場 / 設計者 / 工程 / 台帳の所有者 / 運転員)の固定表
   ③設備台帳の規約(`EQ-NNN`・再利用しない・独立性の 3 軸= model / harness / account_lineage・来歴 4 種= self-reported / harness-measured / user-declared / unknown・**unknown は照合不能であって
   通過ではない**)④独立性の規則(同一 id / 3 軸すべて一致 / いずれかの軸が unknown → 不成立)⑤配員の記述先(register エントリの `producer` / `inspector`・order の担当設備節)⑥判定語の契約
   (検査報告の先頭非空行の行頭 `ACCEPT | REJECT | UNMEASURABLE`・なし= MISSING・契約外= UNPARSED)⑦**機構がない環境では人間の配員規律が担う**(本文書は記述の規約であり、
   読む機構の存在を主張しない)。**BomDD adapter 区画**= 自リポでの機械化の所在(bomdd-job / bomdd-run / bomdd-witness・ECO-062 / 072 / 073 / 074)・出自と計測。固有語は adapter のみ。
2. **`method/templates/70-equipment.yaml` 新規**(雛形): 規約の注記+placeholder 1 件(`EQ-001`・kind / model / harness / account_lineage / provenance / qualification_ref / status)。値は空欄
   (user 指定なし)。bomdd-init の `PHASE_TEMPLATE_GLOBS` で製品 `bomdd/70-equipment.yaml` へ自動複写(bomdd-init 変更なし)。
3. **`method/templates/60-change-register.yaml` のエントリ雛形に注記 2 行**: `# producer: EQ-NNN` / `# inspector: EQ-NNN`(任意・記述欄・設備台帳の id を書く・機械的な導出・検証・強制は
   存在しない・`receipt_author_role` と同形)。
4. **結線**: `bomdd-init.py` `scaffold_product` に `operator-layer.md` の render 1 行(`change-management.md` と同列・生成先 `bomdd/operator-layer.md`)/ `product-profile/README.md` の一覧に 1 行
   +参照 1 行(「配員と設備の記述は operator-layer.md」)。`change-management.md` は**触らない**(ECO-079〔implemented〕の allowed_paths に含まれ窓が重なる— preflight で実測)。
5. **記帳**: improvements.md の EXP-20260914-01 を行内更新(第 2 弾= 文書配布で「設備台帳テンプレート・配員の記述先」を回収・残= self-conformance 非依存化・機械検査・run 台帳と hook・
   next trigger= 製品リポでの配員取り違えの実害 1 件 or user 裁定)。

**採らない**: bomdd-job / bomdd-witness / bomdd-run の配布 / process-validator・hooks の変更 / 配員欄の機械検査 / ViewTube への設置(kit 再設置は別作業)/ 設備台帳の初期値(空欄)/
playbook 本文の改訂 / activation-map への追加 / 60-change-order.md の配員欄文言の変更(ECO-075 で確定)。

## 2. 影響なし予測(製造前・起票時点 — 製造裁定で凍結)

diff= product-profile/operator-layer.md(新規)・templates/70-equipment.yaml(新規)・templates/60-change-register.yaml(注記 2 行・既存フィールド不変)・bomdd-init.py(render 1 行・SKILLS 不変= 13)・
product-profile/README.md(2 行)+台帳系(order・register・improvements・reports/independent-inspection-eco-081*)。change-management.md diff 0(ECO-079 の窓)。process-core diff 0・self-conformance.py diff 0・
bomdd-job / run / witness diff 0・playbook diff 0・既存製品リポは kit 再設置まで非波及。C7(SKILLS 13)不変・C4/C14 advisory・C13 新リンク実在。

## 3. 受入条件(製造前に凍結・二部形)

- V1(条件): `operator-layer.md` の core 区画(adapter 見出しより前)に BomDD 固有語(`bomdd-job|bomdd-run|bomdd-witness|self-conformance|EQ-00[1-3]|ECO-0[0-9][0-9]|Codex|Claude`)が 0 であること — 検査法: adapter 見出しで分割して grep。
- V2(条件): `bomdd-init.py` で temp へ生成した製品リポに `bomdd/70-equipment.yaml` と `bomdd/operator-layer.md` が実在し、`{{` 未解決が 0 であること — 検査法: 生成後に ls+grep。
- V3(条件): register テンプレの注記 2 行と `70-equipment.yaml` の注記に enforcement 語(`工程が止まる|STOP|LEDGER_INCONSISTENT|INDEPENDENCE_FAIL|解決し|照合し`)が 0 であること — 検査法: grep。
- V4(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI success・diff 窓= allowed_paths のみであること — 検査法: 単一入口・`gh run list --commit <full sha>`・`git diff --stat baseline..head`。
- V5(条件): 製造裁定 A なら異系統独立検査(r1 境界探索: 「BomDD を知らない書き手が core だけで設備台帳を書き、配員を記述できるか」「core に機構の存在を示唆する文がないか」→
  r2 是正確認+回帰・inspection gate 経由の昇格)/ B なら製造者較正のみ、であること。
- V6(条件): 較正 receipt(trigger ①: verified 昇格)があること。

## 3b. 製造裁定の候補(別 DECIDE で提示)

- **A** §1 の 1〜5 すべて+異系統独立検査(EQ-002)。
- **B** §1 の 1〜5 すべて・製造者較正のみ。
- **C** §1 の 1〜3 のみ(bomdd-init 非変更・operator-layer.md は kit 同梱の正本のみで製品 `bomdd/` へ render しない)・製造者較正のみ。
当方の推す案= A。製品側の書き手が読む文書なので、第三者が core だけで台帳と配員を書けることを独立に確かめたい(ECO-075 と同型・r1 所見 0 の前例あり)。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-081` の出力を開始 artifact として読んだ)

- 分類= continuation(既裁定の適用: user 範囲 DECIDE A・2026-09-19)。根拠= memory 再開候補・ECO-062 §7 現在地・EXP-20260914-01。
- 最小契約: baseline `e0d4b52`= **confirmed**(作業木 clean)/ current-work-state= **confirmed**(register ECO-075 verified・ECO-080 verified・進行中 ECO なし)/ unresolved-items= **confirmed**
  (EXP-20260914-01 の 4 項目・improvements.md:7459)/ handoff-state= **confirmed**(memory+ECO-062 §7+improvements 2026-09-14 節から再構成)/ acceptance-target= **confirmed**(範囲 A の裁定後・§3)。
- discovered(推測・契約外): 製品側 process-core の register/状態語彙・ViewTube の装置検査・ViewTube の ECO 本文に配員欄なし・bomdd-init の yaml 複写 glob= いずれも実読で **confirmed**(§0)。
- 次番 081= **confirmed**(register grep 0)/ 同一ファイルへの進行中 ECO= **contradicted → 是正済み**(ECO-079〔implemented〕の allowed_paths に `product-profile/change-management.md` が
  含まれ、§1-4 の当初案〔change-management.md に参照 1 行〕と交差した → 参照行を README 側へ移し、本 ECO の allowed_paths から change-management.md を外した)。
- job ビュー(order 生成後・`bomdd-job.py ECO-081`): state= filed・required_skills= `["calibrate", "preflight"]`(class= instrument-change, start)・skills_observed= `["preflight"]`・
  skills_missing= `["calibrate"]`(較正 receipt は verified 昇格時・情報欄)・required_capability= `{"producer": "EQ-001", "inspector": "EQ-002"}`(台帳で実在確認)・
  independent_inspection= required(inspector 宣言)・stop_type= **NONE**。
- 開始判定: **PROCEED(起票のみ)**・override 0。製造は裁定後。
