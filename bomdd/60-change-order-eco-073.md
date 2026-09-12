# Change Order — ECO-073(ECO-062 Phase 7 第 2 弾: cell の判定を入口が receipt として回収 — `--report` の束ね・判定語の契約・fail-closed〔filed〕)

> 裁定: user 2026-09-12 DECIDE「A」(ECO-072 verified 後の次= 第 2 弾 P6-02)→ 経路の DISCUSS(①cell 自身が witness を produce / ②入口が cell の報告を台帳に束ねる・thesis ②)に user AGREE。
> **起票のみ**(製造裁定は別 DECIDE・範囲の凍結は裁定時)。親= [ECO-062](60-change-order-eco-062.md) §7 Phase 7・§10.7 P6-02(入口が記録するのは cell の終了コードで、cell の判定は読まない)。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**。
- producer: EQ-001
- inspector: EQ-002
- 検査官(独立検査併用時): gpt-5.6-sol @ Codex CLI(`codex exec`・入口 `bomdd-run --executor EQ-002` から起動・round の range と実行環境の差は各ブリーフに宣言)。

## 0. 実測(起票根拠)

- **実 cell 3 回(ECO-067 §10.7・ECO-072 r1・r2)とも、入口が台帳に残したのは cell 文字列と `cell exit 0` だけ**。cell の判定(REJECT / ACCEPT)は当方が報告を読んで order に転記した —
  Phase 5 run-02 で測った人力転記の型(P5-10 CODE 転写誤り)がそのまま残っている(P6-02)。
- **報告の先頭形(実測 2 件)**: r1= `[INFORM / COMPLETE]` → 空行 → `REJECT — 理由: IA-01、IA-02、IA-03。` / r2= `[INFORM / COMPLETE]` → 空行 → `ACCEPT`。判定語は handoff ヘッダ行の次の
  非空行の先頭にある(検査官が契約を守った形・N=2)。
- **①(cell 自身が witness を produce)は sandbox で成立しない**: Codex read-only は `.git` 書込不可(Phase 5 P5-05・§10.7)。witness の既定パスは `.git/bomdd-witness/`。cell の自己申告
  receipt は来歴も弱い。
- **§1 採らない「起動先の出力の解釈」との関係**: 判定語の抽出は散文の解釈でなく、witness 1 行目契約(W6)と同型の**固定語彙の照合**。契約外は推定で埋めず MISSING/UNPARSED で止める。
- 台帳は run 台帳(`.git/bomdd-run/<ECO>.jsonl`・非正本・作業木外)。報告ファイル自体はリポ内(`bomdd/reports/`)に cell が書き commit される= 正本側の receipt。入口が束ねるのは両者の結線
  (パス・sha256・判定語・executor・時刻)。

## 1. 変更要求(候補 — 製造裁定で凍結)

1. **`bomdd-run.py --report PATH`**(`--cell` と組で任意): cell 終了後に PATH を読み、`report: {path, exists, size, sha256, verdict, verdict_line}` を台帳の cell 行に束ねる。出力に
   `report <VERDICT> sha256:<12 桁> (<EQ-NNN>)` の 1 行(80 桁以内)を足す。PATH はリポ相対・作業木内・`.git` 配下不可(受理側が commit できる場所に限る)・構文検査(`..`・絶対パス拒否)。
2. **判定語の契約(REPORT_VERDICT)**: 先頭の handoff ヘッダ行(`[` で始まる行)0〜1 行と空行を飛ばし、最初の非空行が `^(ACCEPT|REJECT|UNMEASURABLE)\b` に一致すればその語。報告なし→ `MISSING`、
   あるが一致しない→ `UNPARSED`。いずれも記録のみで exit は cell の終了コードに従う(入口は判定に基づいて行動しない・register/witness を動かさない)。
3. **起動先へ `BOMDD_REPORT`** を渡す(cell が同じパスへ書けるように・ブリーフが参照)。
4. **selftest 腕**: ACCEPT/REJECT/UNMEASURABLE(ヘッダあり・なし)/ MISSING / UNPARSED(要約が先・fence が先)/ パス外・`.git` 配下・絶対・`..` = ARG_ERROR 起動なし / `--report` のみ(--cell なし)= ARG_ERROR /
   80 桁 / 台帳の cell 行に report が入る / sha256 が実ファイルと一致。
5. **受入**(候補): **V1** selftest。**V2(出口条件)**: 本 ECO の独立検査 r1 自体を `--report bomdd/reports/independent-inspection-eco-073.md` で起動し、台帳の cell 行に verdict と sha256 が入り、
   sha256 が commit した報告と一致する(実 cell N=1)。**V3** self-conformance・CI・窓。**V4** 異系統独立検査(range・環境差を宣言)。**V5** 較正 receipt。

**採らない**(起票時点): 入口が判定に基づいて register/witness を動かす(第 3 弾= witness の gate 種別に inspection を足す)/ 散文の解釈(理由・所見番号の抽出)/ ①cell 自身の witness produce /
job 射影 F6(independent_inspection)の充足(run 台帳は非正本 — order の検査官行に report を書かせるかは第 3 弾で判断)/ 報告の様式テンプレート(必要が実測されてから)。

## 2. 影響なし予測(製造前・起票時点 — 製造裁定で凍結)

範囲 A なら diff= `bomdd-run.py` のみ(+台帳系・reports)。bomdd-job・bomdd-witness・templates 不変。`--report` なしの既存呼び出しは不変(V1 に回帰腕)。self-conformance の対象外(tools の selftest で担保)。
hooks・.github diff 0。

## 3. 製造裁定の候補(別 DECIDE で提示)

- **A** §1 の 1〜4 すべて(束ね+契約+env+selftest)。
- **B** 1・2 のみ(env なし・selftest は最小)。
- **C** 機構なし — ブリーフ側に `verdict:` 行を必須にする運用規則だけ。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-073` の出力を開始 artifact として読んだ)

- 分類= 新規機能(親 ECO-062 Phase 7 第 2 弾・DISCUSS→AGREE 済)。baseline `2a921bd`= **confirmed** / 次番 073= **confirmed**(grep 0)/ ECO-072 verified= **confirmed** / 報告の先頭形= **confirmed**
  (r1/r2 実読)/ 同一ファイル(bomdd-run.py)への進行中 ECO なし= **confirmed**(ECO-072 は verified・head 凍結)。
- job ビュー: required_skills= `["calibrate", "preflight"]`・skills_missing= `["calibrate"]`(instrument-change クラス・製造時に応答)・required_capability= `{"producer": "EQ-001", "inspector": "EQ-002"}`(配員欄の解決・ECO-072 の様式 2 例目)
- 開始判定: **PROCEED(起票のみ)**・override 0。製造は裁定後。

## 4. 製造と受入の実測

- (製造裁定後に記入)
