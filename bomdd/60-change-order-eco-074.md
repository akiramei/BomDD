# Change Order — ECO-074(ECO-062 Phase 7 第 3 弾: verified 昇格を台帳の verdict に機械的に依存させる — witness の inspection gate を run 台帳から導出・入口が verified+inspector 宣言で gate を要求・round の range を台帳に〔filed〕)

> 裁定: user 2026-09-12 DECIDE「1:A 2:A」(次の工程= 第 3 弾・EXP-20260912-01 の評価をいま行う)→ gate の所在と根拠の DISCUSS(thesis: witness の gate として置き、根拠は run 台帳から機械導出・
> register は自動で動かさない・range を台帳に)に user AGREE。**起票のみ**(製造裁定は別 DECIDE)。親= [ECO-062](60-change-order-eco-062.md) §7 Phase 7・[ECO-073](60-change-order-eco-073.md) §6
> (残り= 第 3 弾候補)。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**。
- producer: EQ-001
- inspector: EQ-002
- 検査官(独立検査併用時): gpt-5.6-sol @ Codex CLI(入口 `bomdd-run --executor EQ-002 --report … --range …` から起動・round の range と実行環境の差は各ブリーフに宣言)。

## 0. 実測(起票根拠)

- **判定と hash は台帳に入ったが、verified 昇格はまだ人間の手にある**: ECO-072/073 とも、当方が台帳の verdict を読んで order §5 に転記し、register を手で `verified` にした(転記主体= 製造者・
  2 例)。入口は昇格 commit の前に dry で走るが、witness に検査結果の gate がないので「独立検査 ACCEPT なしの verified」を止められない(ECO-073 §6「支持しないもの」)。
- **round には目的(range)がある**: ECO-072 は r1(境界探索・REJECT)→ r2(是正確認+回帰・ACCEPT)、ECO-073 は r1/r2(REJECT)→ r3(是正確認+回帰・ACCEPT)。台帳の cell 行は verdict を持つが range を
  持たないので、「最後の cell 行が ACCEPT」だけでは境界探索 round の ACCEPT(受入根拠にならない・playbook §3)と区別できない。
- **転写値の経路は取れない**: 報告の sha256 を order に書くのは転写(ハッシュ規約: 転写値禁止・座標同一性)。台帳は入口が書いた機械記録で、witness は W2「申告値を再実測しない」を宣言している —
  申告でなく**台帳からの導出**なら W2 を壊さない。
- **既存の停止機構に乗る**: verified 昇格 commit の前に `bomdd-run <ECO>`(dry)を通す運用は固定済み(produce → run → commit・ECO-069 で LEDGER_INCONSISTENT を止めた実例)。gate が 1 種増えるだけで
  新しい入口や手順は要らない。
- **CI の限界**: 台帳は `.git` 配下(リポ外)なので CI/self-conformance は読めない(ECO-020 gate ①の裁定: リポ内検査をリポ外状態へ依存させない)。gate はローカル(入口)の第 1 層で、CI は報告ファイルの
  実在(C13)まで。二層化(order の検査官行に verdict 語+報告リンク)は製造裁定の候補 B。

## 1. 変更要求(候補 — 製造裁定で凍結)

1. **`bomdd-run.py --range 境界探索|是正確認+回帰`**(`--report` と組で必須): 台帳の cell 行 `report.range` と env `BOMDD_RANGE` に残す。語彙外は ARG_ERROR。
2. **`bomdd-witness.py produce --inspection-from-ledger`**: 既定台帳 `.git/bomdd-run/<ECO>.jsonl` の**最後の cell 行のうち report を持つもの**を読み、inspection gate
   `{name: inspection, exit, source: <report path>, verdict, sha256, executor, range, run_id}` を生成する。exit の固定写像= ACCEPT かつ range が「是正確認+回帰」→ 0 / REJECT → 1 /
   MISSING・UNPARSED・range が境界探索・range なし → 2。produce 時に**現在の報告ファイルの sha256 が台帳と一致**することを確認(不一致・不在は gate を作らず ARG_ERROR)。台帳不在・cell 行なしは ARG_ERROR。
3. **入口(bomdd-run)**: job.state が `verified` かつ `required_capability.inspector` が非 null のとき、witness に inspection gate が無ければ STOP(新 code `INSPECTION_MISSING` → 配送先 operator)。
   gate があって exit≠0 なら既存の GATE_FAIL(→ factory)。state が verified 以外、または inspector 宣言なしは従来どおり(後方互換)。
4. **job 射影 F6**: `independent_inspection` を配員欄から導出 `{required: true, inspector: EQ-NNN}`(inspector 宣言なし→ 従来の null F6)。
5. **selftest 腕**: witness(from-ledger: ACCEPT+是正確認→0 / ACCEPT+境界探索→2 / REJECT→1 / MISSING・UNPARSED→2 / sha 不一致→ARG_ERROR / 台帳不在・cell 行なし→ARG_ERROR)・run(verified+inspector+
   gate 0→ADVANCE / verified+inspector+gate なし→STOP INSPECTION_MISSING / verified+inspector+gate 1→STOP GATE_FAIL / verified+inspector なし→ADVANCE / 非 verified+inspector+gate なし→ADVANCE /
   `--report` に `--range` なし→ARG_ERROR)・job(F6 導出)。
6. **受入**(候補): **V1** selftest。**V2(出口条件)**: 本 ECO 自身の verified 昇格 commit で、(a) inspection gate なしの witness → 入口 STOP INSPECTION_MISSING(known-bad・実測)(b) 最終 round の ACCEPT
   (range= 是正確認+回帰)から導出した gate → ADVANCE(陽性対照)(c) 境界探索 round の ACCEPT/REJECT から導出した gate → STOP(range の弁別)。**V3** self-conformance・CI・窓。**V4** 異系統独立検査
   (`--range` つきで起動)。**V5** 較正 receipt。

**採らない**(起票時点): register の自動遷移(遷移は人間の accept commit・入口は止めるだけ)/ CI・self-conformance を台帳に依存させる / 報告の hash を order に転写 / 報告の様式テンプレート。
二層化(候補 B)は裁定で決める。

## 2. 影響なし予測(製造前・起票時点 — 製造裁定で凍結)

範囲 A なら diff= tools 3(bomdd-run・bomdd-witness・bomdd-job)+台帳系+reports。templates 不変。既存 ECO(配員欄なし)は F6 null のまま → gate 不要 → 従来どおり(V1 回帰腕)。`--report` の既存呼び出しは
`--range` 必須化で ARG_ERROR になる(意図・ECO-073 の運用手順を更新)。witness の既存 gate(self-conformance)は不変。hooks・.github diff 0。

## 3. 製造裁定の候補(別 DECIDE で提示)

- **A** §1 の 1〜5 すべて(witness gate・ローカル 1 層)。
- **B** A+二層化: order の検査官行に verdict 語(hash なし)と報告リンクを書かせ、self-conformance の新検査が「verified かつ inspector 宣言なら検査官行に ACCEPT+実在する報告リンク」を検査(CI でも効く)。
- **C** §1 の 2〜4 のみ(`--range` なし・最後の cell 行をそのまま使う・range の弁別は運用)。

## /converge receipt(起動経路: handoff DISCUSS — gate の所在と根拠の設計を user と収束させてから起票)

- **判定: 収束**(round 軌跡: 3→1→0)。
- DoD: ✔ verified 昇格を機構が止められる(独立検査 ACCEPT なしの verified を入口が STOP)/ ✔ 根拠は申告でも転写でもなく機械記録からの導出(W2・ハッシュ規約と両立)/ ✔ round の目的(range)を弁別
  できる(境界探索の ACCEPT を受入根拠にしない・playbook §3)/ ✔ register は自動で動かさない(遷移は人間の accept commit)/ ✔ 既存の運用(produce → run → commit)に乗る。
- round 1(DISCUSS・新規 3 件): ①gate の所在= witness(ローカル)か order+self-conformance(CI)か → witness を第 1 層・二層化は counterpoint として残し製造裁定の候補 B に ②根拠の出所= 台帳から
  導出(`--inspection-from-ledger`)・produce 時に報告の sha256 を再照合 ③range の欠落= 台帳の cell 行に `--range` を足し、gate は「是正確認+回帰」の ACCEPT だけを exit 0 に。
- round 2(user AGREE・新規 1 件): 候補 C(`--range` なし・最後の cell 行をそのまま)を比較用に残す → 製造裁定で決める。
- round 3: 新規 0。**未収束事項: なし**(二層化 B / range なし C は収束済みの選択肢であり、裁定は DECIDE で出す)。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-074` の出力を開始 artifact として読んだ)

- 分類= 新規機能(親 ECO-062 Phase 7 第 3 弾・DISCUSS→AGREE 済)。baseline `a8ad524`= **confirmed** / 次番 074= **confirmed**(grep 0)/ ECO-073 verified= **confirmed** / range の実例= **confirmed**
  (ECO-072/073 の round 記録)/ 同一ファイル(tools 3)への進行中 ECO なし= **confirmed**(ECO-072/073 は verified・head 凍結)。
- job ビュー: required_skills= `["calibrate", "converge", "preflight"]`・skills_missing= `["calibrate", "converge"]`(instrument-change クラス・製造時に応答)・required_capability= `{"producer": "EQ-001", "inspector": "EQ-002"}`・independent_inspection= null(F6・本 ECO で導出化)
- 開始判定: **PROCEED(起票のみ)**・override 0。製造は裁定後。

## 4. 製造と受入の実測

- (製造裁定後に記入)
