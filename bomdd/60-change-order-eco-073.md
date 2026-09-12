# Change Order — ECO-073(ECO-062 Phase 7 第 2 弾: cell の判定を入口が receipt として回収 — `--report` の束ね・判定語の契約・fail-closed〔製造中・裁定 A〕)

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
   あるが一致しない→ `UNPARSED`。いずれも記録のみ。**入口の exit は ECO-067 R8 のまま(起動したら 0)**。cell の終了コードは 2 行目と台帳に残す(入口は判定に基づいて行動しない・
   register/witness を動かさない)。〔r1 IA-01: 起票時の文言「exit は cell の終了コードに従う」は R8 と矛盾していたため訂正〕
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

## 4. 製造裁定と製造(2026-09-12・user DECIDE「A」= 全部)

- **製造裁定 A**: §1 の 1〜4 すべて。register `filed → implemented`(本 commit)・allowed_paths 再凍結= `bomdd-run.py`+自リポ order(本 ECO・ECO-062)+register+improvements.md+
  `bomdd/reports/independent-inspection-eco-073*.md`。
- **製造物**(`method/tools/bomdd-run.py` R10): `--report PATH`(`--cell` と組・`_report_path_error`= リポ相対・`..`/絶対/空要素/前後空白/.git 配下の拒否・作業木外の拒否)/ `report_verdict`
  (先頭の `[` 行を 1 行まで飛ばし、最初の非空行の先頭を `ACCEPT|REJECT|UNMEASURABLE` と照合・大小文字区別・契約外= UNPARSED)/ `bind_report`(存在・size・sha256・verdict・verdict_line・
  読めない/無い= MISSING)/ `launch(…, report)`(env `BOMDD_REPORT`・cell 終了後に束ねる)/ 出力 3 行目 `report <VERDICT> sha256:<12> (<EQ>)`(MISSING は `(no file)`)/ 台帳の cell 行に
  `executor`・`report`、decision 行に `report`(パス)。exit は cell の終了コードに従う(判定で行動しない)。
- **V1**= PASS: `bomdd-run.py --selftest` exit 0(報告 18 腕: ACCEPT ヘッダあり / REJECT ヘッダなし / UNMEASURABLE 空行+ヘッダ / MISSING / UNPARSED 5 種〔要約が先・fence・ヘッダ 2 行・小文字・
  接頭辞 ACCEPTED〕/ 空ファイル / CRLF・コロン / `--report` の構文 8 種= ARG_ERROR・起動なし・台帳不変 / `--report` なしの回帰= cell 行 report None・出力 2 行)。自己捕捉 2 件: usage 行と
  selftest 報告行が 80 桁超(R7)→ 短縮。`bomdd-job.py`・`bomdd-witness.py` の selftest exit 0(不変)。
- **V2(出口条件)**: 本 ECO の独立検査 r1 を `--report bomdd/reports/independent-inspection-eco-073.md` で起動し、台帳の cell 行の verdict・sha256 を §5 に記録(結果は §5)。

## 5. 独立検査(異系統・Codex EQ-002・入口 bomdd-run から `--report` つきで起動)

### 5.1 r1(2026-09-12・range= 境界探索・sandbox workspace-write)— 報告: [independent-inspection-eco-073.md](reports/independent-inspection-eco-073.md)

- **V2(出口条件)の実測**(台帳 `.git/bomdd-run/ECO-073.jsonl`・witness tree 31f3d8da694e):
  - **1 回目(想定外の本番例)**: Codex の応答が OpenAI 側のコンテンツ判定(「cybersecurity risk」・ブリーフの「抜け道」「外へ出る」等の語)で遮断され報告なし・sandbox の `CreateProcessWithLogonW failed: 267`
    も 1 件 → 入口は `cell exit 1` → `report MISSING (no file) (EQ-002)`・台帳 cell 行 `report: {exists: false, verdict: MISSING}`・入口 exit 0(R8)。**MISSING 経路の実測 1 例(環境帰属・製造物は仕様どおり)**。
    ブリーフを中立な表現(入力検証の仕様確認)に書き換えて再送(v2)。
  - **2 回目**: `cell exit 0` → `report REJECT sha256:632863fec4eb (EQ-002)`・台帳 cell 行 `report: {exists: true, size: 9135, sha256: 632863fec4eb…907cd, verdict: REJECT, verdict_line: "REJECT — 理由: IA-01、…IA-05。"}`。
    `sha256sum` の実測値と**完全一致**・報告は handoff ヘッダ → 判定語の契約どおり。**人間の読解なしに判定と hash が台帳へ入った初例**(EXP-20260912-03 ①)。
- 判定: **REJECT**(IA-01〜05)。受理側の真正判定(帰属つき):

  | 所見 | 内容 | 受理側判定 | 是正(r1b) |
  |---|---|---|---|
  | IA-01 | cell exit 7 でも入口 exit は 0(`return 0`)— §1-2「exit は cell の終了コードに従う」に反する | **CONFIRMED・受理側(仕様文言)** — ECO-067 R8(0= 起動した・1= STOP・2= 測定不能)が正本で、cell の exit を入口の exit に写すと STOP/UNMEASURABLE と衝突する。起票時の文言が誤り | §1-2 と R10 の文言を R8 に揃える。selftest 腕: cell exit 7 → 入口 0・2 行目 `cell exit 7`・報告は束ねる |
  | IA-02 | 起動前から存在する報告を今回の cell の報告として束ねる(stale)/ 子プロセスの遅延書込みは MISSING | **CONFIRMED(stale)・製造物** / 遅延は仕様(cell 終了時点で無ければ MISSING・cell 側の責務) | 宛先が起動前に存在したら ARG_ERROR で起動しない(fail-closed)。selftest 腕 stale。遅延は R10 に明記 |
  | IA-03 | 別 cwd から呼ぶと root= cwd となり register 不在= MISSING_INPUT・起動なし | **NOT CONFIRMED(設計どおり)** — root= cwd は ECO-067 の規約(job/witness と同じ)。挙動は fail-closed | R10 に明記(是正なし) |
  | IA-04 | `--report` なしの台帳が ECO-072 基線と同一でない(decision 行に `report: null`・cell 行に `executor`・`report: null` が増えた) | **NOT CONFIRMED(additive)・受理側(予測文言)** — 出力は同一・台帳は欄の追加のみ(既存欄不変) | §2 の「不変」を「出力不変・台帳は欄の追加のみ」に明確化 |
  | IA-05 | 行頭空白を strip してから照合(`  ACCEPT` → ACCEPT)・verdict_line が原文でない | **CONFIRMED・製造物**(契約 `^` は行頭) | 行頭を保って照合(空白始まり= UNPARSED)・verdict_line 原文。selftest 腕 |

- 検査官のその他の観測(受理側で確認): 判定語の境界表(ヘッダ 2 行/BOM/`ACCEPTED`/`Accept`/要約先行/fence/見出し/引用= UNPARSED・ヘッダ前の空行/`ACCEPT:`/`ACCEPT—理由`= ACCEPT)= 契約どおり /
  BOM・CRLF 込みの size/sha256 が実ファイルと一致 / 空ファイル= UNPARSED・同名ディレクトリ= MISSING(exists=false と記録— 「exists= 読める通常ファイル」の意味で仕様どおり)・PermissionError= MISSING・
  traceback なし / REJECT・MISSING・UNPARSED で入口 exit 0(判定で行動しない)/ パス: `./`・`\`・`.gitx/`・200 桁= 受理、末尾 `/`・`.git`= ARG_ERROR / 80 桁・3 行の順不変 / selftest 被覆表(BOM・
  行頭空白・stale・cell 非 0 が未被覆= r1b で腕を追加)。
- 環境の記録: 1 回目の遮断(コンテンツ判定)は**検査ブリーフの語彙が cell の実行可否を左右する**という設備属性(EQ-002 の note 候補)。sandbox の global ignore 参照に Permission denied 警告(測定は成立)。
- r1b 後の V1: `bomdd-run.py --selftest` exit 0(報告 22 腕)。

### 5.2 r2(2026-09-12・range= 是正確認+回帰・範囲限定)— 報告: [independent-inspection-eco-073-r2.md](reports/independent-inspection-eco-073-r2.md)

- 起動: 入口から `--report` つき(fix commit d60471e の作業木・witness tree 862c995e5bd6)→ `cell exit 0` → `report REJECT sha256:5914c85e2481 (EQ-002)`・台帳 cell 行
  `verdict_line: "REJECT IA-06、IA-07 — …"`(`sha256sum` と一致・**受入判定は台帳の verdict から転記**= EXP-20260912-03 ③の 1 例目)。
- 判定: **REJECT**(IA-06・IA-07)。是正確認: IA-02(stale → ARG_ERROR 起動なし / fresh → 束ね / 遅延 → MISSING)・IA-05(`  ACCEPT` → UNPARSED・verdict_line 原文)・IA-01 明確化(cell exit 7 →
  入口 0・3 行の順)= **すべて成立**。回帰: 判定語の境界表 13 腕・結線 5・パス 11・出力互換・80 桁・selftest 3 ツール= 不変。受理側の真正判定:

  | 所見 | 内容 | 受理側判定 | 是正(r2b) |
  |---|---|---|---|
  | IA-06 | 宛先に同名ディレクトリがあるとき、r1 では起動後 MISSING だったのが ARG_ERROR(起動なし)に変わった= 指定回帰腕の差 | **CONFIRMED(差の事実)・受理側帰属** — r1b の事前存在検査はファイル/ディレクトリを区別せず、書けない宛先へ起動しないのは fail-closed として正しい。r2 ブリーフの回帰期待(ディレクトリ= MISSING)が旧仕様だった | 仕様を明文化(宛先に何かが存在すれば ARG_ERROR)・selftest 腕 dirtarget 追加(検査官指摘: selftest がディレクトリを覆っていなかった) |
  | IA-07 | `run()` 内の R10 コメントに旧文言「exit は cell に従う」が残存(冒頭は R8 に修正済み) | **CONFIRMED・製造物(仕様コメント)** | 文言を R8 に揃える |

- 範囲外の観察(環境帰属): 検査官 sandbox で self-conformance の C14 REAL が FAIL(ECO-072 r1 と同じ git 所有者問題)/ global ignore の Permission denied 警告 1(測定成立)。
- r2b 後の V1: `bomdd-run.py --selftest` exit 0(報告 23 腕)。
