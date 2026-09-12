# Change Order — ECO-074(ECO-062 Phase 7 第 3 弾: verified 昇格を台帳の verdict に機械的に依存させる — witness の inspection gate を run 台帳から導出・入口が verified+inspector 宣言で gate を要求・round の range を台帳に〔verified〕)

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

範囲 A なら diff= tools 3(bomdd-run・bomdd-witness・bomdd-job)+台帳系+reports。templates 不変。既存 ECO(配員欄なし)は F6 null のまま → gate 不要 → **判定と出力は従来どおり**(V1 回帰腕。
job JSON の停止語彙と F6 の source 文言・decision 行の `inspection` 欄は additive に増える= r1 IA-06 の明確化)。`--report` の既存呼び出しは
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

## 4. 製造裁定と製造(2026-09-12・user DECIDE「A」= 1 層)

- **製造裁定 A**: §1 の 1〜5 すべて(witness gate・ローカル 1 層)。register `filed → implemented`(本 commit)・allowed_paths 再凍結= tools 3+自リポ order(本 ECO・ECO-062)+register+improvements.md+
  `bomdd/reports/independent-inspection-eco-074*.md`。二層化(B)は別 ECO の候補として残す。
- **製造物**:
  1. `bomdd-run.py`(R11): `--range 境界探索|是正確認+回帰`(`--report` と組で必須・語彙外/片方のみ= ARG_ERROR・台帳 `report.range`・env `BOMDD_RANGE`)/ 入口の要求: job.state= verified かつ
     `independent_inspection.required` のとき witness の gates に `name=inspection` が無ければ `STOP <ECO> INSPECTION_MISSING → operator`(receipt が ADVANCE のあと・独立性の前)・gate exit≠0 は
     witness の GATE_FAIL(→ factory・既存)。台帳 decision 行に `inspection: {required, inspector, gate}`。DELIVERY と job の停止語彙に `INSPECTION_MISSING`。
  2. `bomdd-witness.py`: `produce --inspection-from-ledger`= `.git/bomdd-run/<ECO>.jsonl` の最後の report つき cell 行から gate `{name: inspection, exit, source: <path>, verdict, sha256, range,
     executor, run_id}` を導出。exit= ACCEPT かつ range 是正確認+回帰 → 0 / REJECT → 1 / MISSING・UNPARSED・境界探索・range なし → 2。現在の報告 sha256 が台帳と一致しない・報告不在・cell 行なし・
     台帳不在= ARG_ERROR(gate を作らない)。
  3. `bomdd-job.py`(F6): 配員欄 inspector → `independent_inspection= {required: true, inspector}`(なし= null F6)。
- **V1**= PASS: `bomdd-job.py --selftest` exit 0(F6 腕 2)/ `bomdd-witness.py --selftest` exit 0(inspection-from-ledger 11 腕: ACCEPT+是正確認→0・境界探索/range なし/MISSING/UNPARSED→2・REJECT→1・
  sha 不一致/報告不在/cell 行なし/台帳不在= ARG_ERROR・最後の行が採られる)/ `bomdd-run.py --selftest` exit 0(range 4 腕: --range なし/語彙外/--report なし/絶対パス= ARG_ERROR・既存 report 腕は range
  記録 / 検査 gate 6 腕: verified+inspector+gate 0→ ADVANCE・gate なし→ STOP INSPECTION_MISSING・gate 1/2→ STOP VERIFICATION_FAIL factory・verified+inspector なし→ ADVANCE・decided+inspector→ ADVANCE)。
- **V2(出口条件)**: (c) 境界探索 round(r1)の台帳から導出した gate(exit 2)で dry → STOP(§5.1 で実測)/ (a) accept 段で register= verified・gate なし witness → STOP INSPECTION_MISSING /
  (b) 最終 round の ACCEPT から導出した gate → ADVANCE(§6 で実測)。

## 5. 独立検査(異系統・Codex EQ-002・入口 bomdd-run から `--report`/`--range` つきで起動)

### 5.1 r1(2026-09-12・range= 境界探索・sandbox workspace-write)— 報告: [independent-inspection-eco-074.md](reports/independent-inspection-eco-074.md)

- 起動: `bomdd-run.py ECO-074 --executor EQ-002 --report bomdd/reports/independent-inspection-eco-074.md --range 境界探索 --cell "codex exec …"`(fix commit a43c7f8・witness tree 0685409ab255)→
  `cell exit 0` → `report REJECT sha256:1c172c902b2d (EQ-002)`・台帳 cell 行 `report.range: 境界探索`・verdict_line `REJECT — 理由: IA-01〜IA-07`(`sha256sum` と一致)。
- **V2(c) 実測(境界探索 round の gate は通らない)**: r1 直後に `bomdd-witness.py produce --eco ECO-074 --gate self-conformance=0:… --inspection-from-ledger` → gates 2(inspection exit 1・verdict REJECT・
  range 境界探索)→ `bomdd-run.py ECO-074 --executor EQ-002`(dry)→ `STOP ECO-074 GATE_FAIL → factory @68a1dcaa54a8` exit 1・台帳 `stop_type: VERIFICATION_FAIL`・`inspection: null`(IA-05 の再現= 是正前)。
  **境界探索 round の判定を受入根拠に使えないことを機構が止めた実測 1 例**(REJECT。ACCEPT+境界探索は selftest 腕で exit 2 → 同じ STOP)。
- 判定: **REJECT**(IA-01〜07)。受理側の真正判定(帰属つき):

  | 所見 | 内容 | 受理側判定 | 是正(r1b) |
  |---|---|---|---|
  | IA-01 | 台帳の壊れた JSON 行を黙って飛ばし別行の ACCEPT を採る | **CONFIRMED・製造物** | 壊れた行・object でない行= ARG_ERROR(台帳不正・測定不能は合格ではない)。selftest 腕 |
  | IA-02 | 台帳の cell 行の `eco` を要求個体と照合しない(別 ECO の行から gate) | **CONFIRMED・製造物** | `row.eco == --eco` を要求(個体照合・W7 と同型)。selftest 腕 |
  | IA-03 | 台帳の report.path に入口と同じ境界検証がなく作業木外・絶対パスから gate | **CONFIRMED・製造物** | `_ledger_report_path_error`(リポ相対・`..`/絶対/空要素/前後空白/.git 配下/作業木外を拒否)。selftest 腕 3 |
  | IA-04 | sha 欠落を exit 2 のときだけ許す(ACCEPT+境界探索・sha なし → gate) | **CONFIRMED・製造物** | sha は MISSING 以外で必須(64 桁小文字 hex・現在の報告と一致)。MISSING 行に sha があれば形状不正。selftest 腕 5 |
  | IA-05 | inspection gate が exit 1/2 のとき decision 行の `inspection` が null | **CONFIRMED・製造物**(§4 の記録仕様と不一致・V2(c) で再現) | gate の有無・値を receipt 判定の前に記録(失敗時も残す)。selftest 腕 |
  | IA-06 | ECO-071 の job JSON・decision 行が旧と同一でない(停止語彙・F6 文言・`inspection` 欄) | **NOT CONFIRMED(additive)・受理側(予測文言)** | §2 を「判定と出力は従来どおり・JSON/台帳は additive」に明確化 |
  | IA-07 | witness produce の 1 行目が 80 桁超(出力先の絶対パス) | **NOT CONFIRMED(仕様外)** — 80 桁契約は bomdd-run R7 のみ(witness W6 は 1 行目の形式)。中央省略は将来の候補 | 記録のみ |

- 検査官のその他の観測(受理側で確認): 台帳からの導出表(REJECT→ACCEPT で後の ACCEPT・ACCEPT→REJECT で後の REJECT・末尾 report null は直前の行・小文字/未知 verdict・語彙外/欠落 range= exit 2・
  短縮/大文字 sha・別内容 path= ARG_ERROR)= 仕様どおり / 入口の要求表(gate なし= INSPECTION_MISSING operator・exit 1/2= GATE_FAIL factory・`Inspection`/`inspection `= 名前不一致で MISSING・0 と 1 の
  2 個= GATE_FAIL・implemented+inspector= ADVANCE・verified+inspector なし= ADVANCE・台帳に無い inspector= LEDGER_INCONSISTENT が先行)= 仕様どおり / `--range` 6 種の不正= ARG_ERROR・正常時は
  cell の `BOMDD_RANGE` と台帳が一致 / **導出後に報告を書き換えても verify は gate を再照合しない**(追跡対象なら TREE_MISMATCH で止まる・gitignore 対象なら通る)= witness の宣言済み限界 (2)(3)
  を本 ECO の受理限界として §6 に記す / `--gate inspection=0:x` の申告 gate は通る(範囲外の観察・受理側の運用規律= produce は `--inspection-from-ledger` でのみ inspection を作る)。
- 検査官の較正 receipt: 主張 1「台帳からの導出だけで昇格を制御」= 不適格(IA-02/03)→ r1b で是正。selftest 3 本の PASS は受理根拠として不十分(被覆表)→ r1b で腕を追加。
- r1b 後の V1: `bomdd-witness.py --selftest` exit 0(inspection 22 腕)/ `bomdd-run.py --selftest` exit 0(IA-05 腕)/ `bomdd-job.py --selftest` exit 0。

### 5.2 r2(2026-09-12・range= 是正確認+回帰・範囲限定)— 報告: [independent-inspection-eco-074-r2.md](reports/independent-inspection-eco-074-r2.md)

- 起動: 入口から `--report … --range 是正確認+回帰`(r1b commit df0d7c3・witness tree c85e541d6ed9)→ `cell exit 0` → `report ACCEPT sha256:6d096b9c33b4 (EQ-002)`・台帳 cell 行 `range: 是正確認+回帰`・
  verdict_line `ACCEPT — IA-01〜IA-05 の是正を確認し、指定された回帰範囲に差異はありません。`(`sha256sum` と一致)。**本節の判定は台帳の verdict から転記**。
- 判定: **ACCEPT**・新規所見なし。IA-01(壊れた行 先頭/中間/末尾・非 object → ARG_ERROR・空行は無視)/ IA-02(別 ECO 行 → 個体不一致)/ IA-03(絶対・`..`・前後空白・空要素・`.git/`・junction 経由の
  作業木外 → ARG_ERROR・正常は gate)/ IA-04(ACCEPT/REJECT/UNPARSED の sha 欠落・短縮・大文字 → ARG_ERROR・MISSING は sha なしで exit 2・MISSING に sha → 形状不正)/ IA-05(exit 1/2 の gate も
  decision 行に記録・gate なしは `gate: null`)= **すべて成立**。回帰: 導出表・入口の要求表・`--range` 6 種・3 ツール selftest exit 0・ECO-074 の F6/配員・ECO-071 の dry 旧新同一(additive 差は仕様どおり)。
  検査官の較正 receipt: 計器欠陥なし。範囲外の観察: verify の sha 再照合・申告 gate・witness の 80 桁は §6 の限界/運用規律として除外。

## 6. クローズ(2026-09-12・verified)

- **V1**= PASS(selftest 3 ツール exit 0・§4/§5.1)/ **V3**= PASS(self-conformance 全 PASS・CI: fix a43c7f8= 34672485145 success・r1b df0d7c3= 34673758816 success)。diff 監査の窓: baseline `c180cc8` → head `df0d7c3`
  (**窓閉鎖**)。窓内= tools 3・order 2・register・improvements・reports(r1)= allowed_paths のみ。
- **V4**= 異系統独立検査 r1(境界探索・REJECT 7: 是正 5・明確化 1・仕様外 1)→ r2(是正確認+回帰・ACCEPT)。range と実行環境の差をブリーフに宣言・入口が `--range` で台帳に残した。
- **V2(出口条件)**: (c)= §5.1(境界探索 round の gate → STOP GATE_FAIL・起動なし)。(a)(b)= 本節末尾「accept 段の実測」(register を verified にした作業木で、gate なし witness → STOP INSPECTION_MISSING /
  r2 ACCEPT の台帳から導出した gate → ADVANCE)。
- **V5**= 下記 較正 receipt。register: `implemented → verified`・head 凍結。
- **受理限界(検査官の指摘を記録)**: ①`verify` は witness の gate を固定値として検証し、報告の sha256 を再照合しない(witness 冒頭の限界 (2)(3)。追跡対象の報告なら書き換えは TREE_MISMATCH で止まる・
  gitignore 対象なら通る → 報告は追跡対象に置く= 運用規律)②`--gate inspection=0:x` の申告 gate は produce が通す → inspection gate は `--inspection-from-ledger` でのみ作る(運用規律・機械化は次)
  ③witness produce 行の 80 桁契約はない(R7 は bomdd-run)。
- **Phase 7 第 3 弾の到達点**: verified 昇格 commit の直前に、入口が「是正確認+回帰 round の ACCEPT(sha 一致・個体一致)から導出した gate」を要求し、無ければ止める。独立検査の結果回収から
  昇格の停止までが機構で閉じた(register の遷移自体は人間の accept commit)。残り= 申告 gate の機械拒否・二層化(CI)・裁定キュー(保留)。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・③: 計器変更〔tools 3〕)

- 査定した主張と判定:
  1. 「独立検査 ACCEPT なしの verified を入口が止める」— **observed / 適格**(accept 段の実測 (a): register verified・inspector 宣言・gate なし witness → STOP INSPECTION_MISSING・起動なし)。
  2. 「境界探索 round の判定は受入根拠にならない」— **observed / 適格**(§5.1 V2(c): r1 REJECT の gate → STOP。ACCEPT+境界探索 → exit 2 は selftest 腕+検査官 r1/r2 の表)。
  3. 「gate は申告でなく台帳から導出し、個体・境界・形状を再検証する」— **observed / 適格**(r1 で 4 クラスの穴 → r1b → r2 で全成立。申告 gate の拒否は未実装= 運用規律・限界 ②)。
  4. 「正しい ACCEPT を止めない」— **observed / 適格**(accept 段の実測 (b): r2 ACCEPT の gate → ADVANCE。偽陽性の継続計測は EXP-20260912-04)。
  5. 「register を自動で動かさない」— **observed / 適格**(入口は STOP/ADVANCE のみ・遷移は本 commit)。
- 検出した計器欠陥(帰属つき): 製造物 5 件(IA-01〜05・r1 境界探索が検出・r1b 是正・selftest に腕 12 追加)。受理側 2 件= IA-06 予測文言 / IA-07 仕様外の桁(記録)。自己捕捉 2(80 桁)。
  受理側の手順欠陥 1= build スクリプトの anchor 不一致(job/witness 部だけ適用され run 部が未適用のまま selftest を回した → 語彙不一致で自己捕捉・再適用)。
- 検出力の限界: verify の報告 sha 再照合なし(限界 ①)/ 申告 gate(限界 ②)/ 同時 append・ACL・非 UTF-8 JSONL・強制終了中の部分書込み(未測定・検査官宣言)/ 検査官 1 系統(Codex)N=2 round。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | V2(a)(b)(c) 実入口・selftest 3 ツール・r1/r2 |
  | Q2 | asked | observed/適格 | 実測 | known-bad= gate なし/境界探索 gate/壊れた行/別 ECO/作業木外 path/sha 欠落・陽性対照= r2 ACCEPT gate で ADVANCE |
  | Q3 | asked | observed/適格 | 実測 | 是正前後: r1 で gate 生成 → r1b で ARG_ERROR(検査官 r2 で確認) |
  | Q4 | asked | observed/適格 | 実測 | 実 order・実台帳(r1/r2 の実 cell 行)・実報告 |
  | Q5 | asked | observed/適格 | 実測 | 未測定(限界 ①②・競合・ACL)を宣言 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測 → witness → 入口 dry → commit → push → CI(fix・r1b・accept ×2 回の検査) |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照あり(r2 gate ADVANCE・selftest gate 0) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness(gate 2 種)・register・run 台帳(decision/cell 行に inspection・report.range)・r1/r2 報告 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= 台帳の形状/個体/境界/sha/range・witness gate の有無と exit・job 状態(検査官の被覆表) |

- このクローズが支持しないもの: 申告 gate の機械拒否 / CI 側(二層)の押し戻し / verify の報告 sha 再照合 / 偽陽性率(EXP-20260912-04 で 3 ECO)/ 裁定キュー。

### accept 段の実測(V2(a)(b)・2026-09-12・register= verified の作業木・witness tree 5ee7d2d4881a)

- **(a) gate なし(known-bad)**: `bomdd-witness produce --eco ECO-074 --gate self-conformance=0:…`(gates 1)→ `bomdd-run ECO-074 --executor EQ-002` → `STOP ECO-074 INSPECTION_MISSING → operator @5ee7d2d4881a`
  exit 1・台帳 decision 行 `job_state: verified`・`inspection: {required: true, inspector: EQ-002, gate: null}`。**独立検査 ACCEPT なしの verified 昇格を入口が止めた実測 1 例**。
- **(b) 台帳から導出(陽性対照)**: `produce … --inspection-from-ledger`(最後の report つき cell 行= r2・ACCEPT・range 是正確認+回帰・sha 6d096b9c33b4…・run_id 20260912T044913.995808Z)→ gates 2 →
  dry → `ADVANCE ECO-074 OK → next · dry @5ee7d2d4881a` exit 0・台帳 `inspection.gate: {exit: 0, verdict: ACCEPT}`。本 commit はこの経路(検査 #2 → produce --inspection-from-ledger → dry ADVANCE → commit)で行った。
