# Change Order — ECO-067(Phase 6 第 1 弾: 狭い自動起動の単一入口 `bomdd-run` — job → receipt 再検証 → 台帳の機械回収 → ADVANCE のときだけ製造セルを起動〔起票のみ〕)

> 裁定: user 2026-09-11 DECIDE「A」— Phase 5 の出口(fail-open 0/7 ×2・運転員 2 種・判断依存 0)を満たしたと見なし **Phase 6 を開く**。設計入力に P5-10(台帳を運転員が
> 手書きせず検証器の 1 行目を機械回収)と P5-08(1 行目の短縮)を含める。出典= [ECO-062 order](60-change-order-eco-062.md) §7 Phase 6・§10.6、
> [run 台帳 run-02](reports/phase5-run-02-eco-062.md) §4。**起票のみ**(製造着手・範囲の凍結は別裁定)。起票工程は job 経由(§0.4)。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

### 0.1 Phase 5 で実測できたこと・できなかったこと(§10.6)

| 量 | run-01(Codex) | run-02(人間) | 含意 |
|---|---|---|---|
| fail-open(known-bad 7 腕) | 0/7 | 0/7 | 検証器+手順で止まる |
| 判断依存の STOP | 2 | **0** | ECO-066 後は機構のみで止まる |
| 台帳の正確さ | 1 メッセージで完結 | 6 往復・R6 空欄・CODE 転写誤り 1・evidence 未提出 | **人間が台帳を手書きすると規格が守られない**(P5-09/10) |
| 1 行目の可読性 | 問題なし | 40 桁 ×2 で折り返し・VERDICT が視界外 | 報告形式は運転員の種類で最適が違う(P5-08) |
| 自動起動 | なし(自動実行なし) | なし | **Phase 6 の対象= 未測定** |

- Phase 6 の出口(§7): 「自動起動 job で witness 再検証が機械的に効いた実測」。Phase 5 は運転員が verify を**手で**回した。Phase 6 は verify を**入口が**回し、ADVANCE のときだけ
  次工程を起動する。「狭い」= 単一入口・1 job・1 起動先・コマンド単位の承認は維持(入口は承認を迂回しない)。

### 0.2 既存物(実読)

- `bomdd-job.py`(ECO-062/064): job ビュー(read-only・exit 0・`--json` で単一 JSON)。receipt のパスは出さない(job と receipt の束ねは運転員が手でやっていた= run-01 R3 の穴の遠因)。
- `bomdd-witness.py`(ECO-062/066): `verify PATH --eco ECO` で 1 行目 `<VERDICT> <CODE>[(<CAUSE>)]: msg`・exit 0/1/2。既定パス= `.git/bomdd-witness/<ECO>.json`。
- run 台帳: Phase 5 では **チャット**(非正本・手書き)。「運転状態は job に書き戻さない・運転員所有の run 台帳(正本でない)」(ECO-062 §1-1)は満たすが、機械可読でない。
- 停止語彙(F5・8 値)と配送先(§0.5): ①規範判断 → 人 / ②検査赤 → 工場へ差し戻し / ③BOM 矛盾 → 設計者 / ④収束上限 → 裁定点 / ⑤preflight HOLD/STOP → 工程判定 /
  ⑥台帳不整合 → 台帳の所有者。**配送先は散文で、機械定義がない**(§7 Phase 7 の対象・本 ECO では固定表として持つ候補)。

### 0.3 「自動起動」で新たに生じる失敗型(先回りせず、Phase 5 で実測した型の延長だけ)

- 入口が verify を回すなら、**入口自身が job と receipt を正しく束ねる**必要がある(R3 型の再演を入口が起こす)。→ receipt パスは job(ECO)から機械導出(既定パス)し、任意パスは受けない。
- 入口が起動するなら、**STOP なのに起動する**(fail-open の入口版)が最悪の失敗型。→ 起動は `ADVANCE OK` の 1 行目と exit 0 の**両方**を条件にし、known-bad 常設(§1-3)で毎回の
  selftest に持つ。
- 起動先が何をするかは入口の責務外(製造セルの契約)。入口は「起動した」事実(コマンド・時刻・job・witness の tree)を台帳に残すだけ。

### 0.4 起票工程(job 経由)

`bomdd-job.py ECO-067` を register 追記後に出力し required_skills / skills_missing を /preflight receipt に記す。

## 1. 変更要求(製造対象の候補 — 製造裁定時に凍結)

1. **`method/tools/bomdd-run.py <ECO> [--cell "<command>"] [--ledger PATH]`**(新規・単一入口):
   - (a) job ビューを `bomdd-job.py` から取得(`--json`・in-process import か subprocess・転写しない)。job の `stop_type` が NONE 以外なら **起動せず** STOP(配送先= 下記表)。
   - (b) receipt パスを **ECO から機械導出**(既定パス `.git/bomdd-witness/<ECO>.json`・任意パス不可)し、`bomdd-witness.py verify <path> --eco <ECO>` を回す。
   - (c) 台帳の**機械回収**(P5-10): 運転員所有の run 台帳 `.git/bomdd-run/<ECO>.jsonl`(作業木外・非正本・追記のみ)に 1 行= {run_id, eco, receipt, verifier_line(1 行目そのまま),
     verifier_exit, decision, stop_type, delivery(配送先), cell(起動したコマンド or null), started_at, tree}。人間の手書き欄なし。
   - (d) **起動条件**= verifier_exit 0 **かつ** 1 行目が `ADVANCE OK:` で始まる **かつ** job.stop_type == NONE。すべて成立し `--cell` があるときだけ、そのコマンドを**そのまま**
     起動する(引数の加工なし・`BOMDD_JOB=<ECO>`・`BOMDD_JOB_JSON=<一時ファイル>`・`BOMDD_WITNESS=<path>` を環境で渡す)。承認は起動先のハーネスに委ねる(入口は迂回フラグを持たない)。
     `--cell` なし= dry(Phase 5 と同じ検証+台帳のみ)。
   - (e) 人間向けの表示(P5-08): 標準出力は **短い 1 行**(`<decision> <ECO> <CODE> → <delivery>`・tree は 12 桁)。40 桁 ×2 は台帳の `verifier_line` にだけ残す。
   - (f) 終了コード= 0 起動した(or dry で ADVANCE)/ 1 STOP(起動せず)/ 2 測定不能(起動せず)。
   - (g) `--selftest`: 一時 git リポで known-good(起動する・ダミー cell が実行された痕跡)/ known-bad 5 腕(古い tree・別 job・FAIL 混入・欠測・stop_type≠NONE)+ job.stop_type≠NONE 腕
     (LEDGER_INCONSISTENT)+ 測定不能腕(witness 不在)で **起動しない**ことを実測(§1-3 の known-bad 常設= 毎回の selftest)。
2. **停止種別 → 配送先の固定表**(bomdd-run 内の定数・F5 の延長・§0.5 の 6 種を写す): NORMATIVE_RULING/CONVERGENCE_LIMIT → `human` / VERIFICATION_FAIL → `factory` /
   BOM_CONTRADICTION → `designer` / PREFLIGHT_HOLD → `process` / LEDGER_INCONSISTENT → `ledger-owner` / MISSING_INPUT → `operator` / NONE → `next`。機械定義の初版(Phase 7 で
   複数 executor へ拡張)。
3. **既存ツール非接触**: `bomdd-job.py`・`bomdd-witness.py`・pre-push hook・self-conformance は変更しない(job の `--json` と witness の 1 行目契約を消費するだけ)。

**採らない**: 承認の迂回(`--dangerously-*` 相当のフラグ・cell の自動承認)/ 複数 job のキュー・複数 executor(Phase 7)/ ruling の取り込み(§1-4・別 ECO)/ 台帳を作業木内に置く
(W5 と同じ自己参照)/ 起動先の出力の解釈(製造セルの契約・入口の責務外)/ 1 行目の短縮を `bomdd-witness.py` 側で行う(入口の表示で足りる— P5-08 は入口側で吸収)/
run 台帳を正本にする(正本は register / order のまま)。

## 2. 影響なし予測(起票段階・反証可能)

起票の diff は台帳系のみ(本 order・register・ECO-062 order §7 現在地・improvements.md)。製造時(候補): 新規 1 ファイル(`bomdd-run.py`)のみ。既存の全検査 C1〜C18 判定不変
(新規 .py は検査対象集合に入らない・C4 kit 非含有)・pre-push witness 不変・`bomdd-job.py`/`bomdd-witness.py` diff 0・製品リポ非波及。

## 3. 受入(製造時の候補)

- **V1**(known-bad 常設): `--selftest` で known-good 1 腕は起動し、known-bad 5+2 腕は**起動しない**(ダミー cell= 痕跡ファイルを書くコマンド・痕跡の有無で判定)。
- **V2**(実 job): 本リポの実 ECO で dry 実行 → 台帳 1 行が機械回収され、`verifier_line` が witness の 1 行目と一致・decision/delivery が表どおり。
- **V3**(自動起動の実測= Phase 6 の出口): 実 ECO で `--cell` に **無害な cell**(例: `python -c "print(...)"` または job ビューを再生成するコマンド)を与え、ADVANCE で起動・
  known-bad receipt に差し替えると起動しない、を同一 job で前後実測。承認は起動先ハーネスの既定どおり(迂回なし)。
- **V4**: self-conformance 全 PASS・CI 緑・窓= `bomdd-run.py`+台帳系。**V5**: 異系統独立検査(Codex)必須(tool)。
- **V6**(人間向け表示): 標準出力 1 行が既定幅(80 桁)に収まる(P5-08)。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-067` の出力を開始 artifact として読んだ〔§0.4〕)

- 分類= 既裁定の適用実装(user DECIDE「A」・起票まで)。baseline `49e3a99`= **confirmed**(HEAD・作業木 clean)/ 次番 067= **confirmed**(register 末尾= 066)/
  Phase 5 の記帳= **confirmed**(§10.6・run 台帳 2 本)/ 既存物の契約= **confirmed**(job `--json`・witness 1 行目 W6/W7 を実読)/ 凍結の非該当= **confirmed**(converge・calibrate 非接触)/
  同一ファイルへの進行中 ECO なし= **confirmed**(新規ファイル・in-progress は ECO-055 のみ)。
- job ビュー(実出力): required_skills= `["calibrate", "preflight"]`(start + instrument-change — affected_refs の新規ファイルも glob `method/tools/*.py` に一致)・
  skills_missing(起票時)= `["calibrate"]`(verified 昇格時の較正 receipt で応答・ECO-065/066 と同じ軌跡。当初「preflight のみ」と予測していたが実出力で訂正)。
- 開始判定: **PROCEED**(起票まで)・override 0。製造は別裁定。

## /converge receipt(起動経路: 自発 — 入口の設計〔§1 の 3 項〕)

- **判定: 収束**(round 軌跡: 4→1→0)。
- DoD: ✔ 起動条件が「1 行目+exit+job.stop_type」の 3 条件 AND で fail-open の入口版を機構で塞ぐ / ✔ receipt パスを ECO から機械導出し R3 型を入口が起こさない /
  ✔ 台帳を機械回収し人間の手書き欄をなくす(P5-10)/ ✔ 承認を迂回しない / ✔ 既存ツール非接触 / ✔ 1 行目の短縮は入口の表示で吸収(P5-08)/ ✔ 「狭い」= 1 job・1 起動先。
- round 1(新規 4 件): ①台帳を `bomdd/runs/` に置くと台帳の追記自体が tree を変え次の verify が STOP する(W5 と同型)→ `.git/bomdd-run/` ②cell の引数を入口が加工すると
  承認の意味が変わる → そのまま起動・環境変数で渡す ③配送先を散文のままにすると入口が STOP の行き先を決められない → 固定表(機械定義の初版)④witness の 1 行目を
  短くする案は ECO-066 の契約変更になる → 入口側の表示で吸収。
- round 2(新規 1 件): 起動条件を exit 0 だけにすると実行基盤の exit 丸め(P5-07)の裏返し(0 の偽装)を測れない → 1 行目と exit の両方を要求。
- round 3: 新規 0。**未収束事項: なし**。

## 記録(起票時)

- register: `filed`(2026-09-11)・baseline `49e3a99`・allowed_paths(起票段階)= 台帳系+`method/tools/bomdd-run.py`(製造裁定で再凍結)。
- ECO-062 §7 現在地= 「Phase 6 開始(裁定 A)・ECO-067 起票済・製造裁定待ち」。EXP-20260910-02 の next trigger= 本 ECO の V3(自動起動の初回)。
- **次の裁定(製造裁定)**: 範囲= §1 の 3 項をそのまま凍結するか・独立検査= Codex(V5)。ECO-055 の register status は別 DECIDE。

## 4. 製造裁定と製造(2026-09-11・user DECIDE「A」— §1 の 3 項をそのまま凍結・独立検査= Codex)

- register `filed → decided`(同日)。affected_refs= `method/tools/bomdd-run.py`(新規)で凍結。allowed_paths= 新規 1+台帳系+検査報告。影響なし予測(製造前・凍結)は register。
- 製造者= Claude Code(claude-fable-5-1・起票者と同一)。独立検査= Codex(異系統・CLI 直接・§3 V5)— verified は検査官の受理側真正判定を §7 に記録してから。

## 5. 製造物(`method/tools/bomdd-run.py`・新規・345 行)

| §1 | 実装 |
|---|---|
| 1(a) job 取得 | `bomdd-job.py` を `importlib` で in-process import し `select([eco], root)` → job レコード(`{value, source}` 欄)。job.stop_type ≠ NONE は receipt 検証の結果に関わらず STOP(配送先= 表) |
| 1(b) receipt 導出 | `bomdd-witness.default_path(git_dir, eco)`= `.git/bomdd-witness/<ECO>.json`。任意パスの引数なし |
| 1(c) 台帳 | `.git/bomdd-run/<ECO>.jsonl` 追記(`--ledger` で作業木外の別パス可・作業木内は `_inside_worktree` で exit 2)。1 行= run_id・eco・receipt・job_state・job_stop_type・verifier_line(1 行目そのまま)・verifier_exit・**code**(witness CODE・製造中に追加)・decision・stop_type(job 語彙)・delivery・cell・cell_exit・started_at・tree |
| 1(d) 起動条件 | `decide()` が ADVANCE を返すのは verifier_exit==0 **かつ** 1 行目 `ADVANCE OK:` **かつ** job.stop_type==NONE のときだけ。`launch()` は `subprocess.run(cell, shell=True, cwd=root, env=…)`(文字列を加工しない)・環境 `BOMDD_JOB` / `BOMDD_JOB_JSON`(job の一時 JSON・終了後に削除)/ `BOMDD_WITNESS`。迂回フラグなし。`--cell` なし= dry |
| 1(e) 表示 | `summary_line()`= `<decision> <ECO> <tag> → <delivery>[ · dry\|launched(exit N)] @<tree 12 桁>`。STOP/UNMEASURABLE では「未起動」を書かない(起動できるのは ADVANCE だけ)。selftest で全腕 80 桁以内を検査 |
| 1(f) 終了コード | ADVANCE 0 / STOP 1 / UNMEASURABLE 2(台帳書込不能・引数不正・作業木内台帳も 2) |
| 1(g) selftest | 一時 git リポ+fixture register/order(bomdd-job の selftest と同型)+実 witness。known-good(痕跡ファイルを書く cell が起動し、環境変数 `ECO-900\|<witness path>` を受け取る)/ dry / known-bad 5(tree・別 job・FAIL・欠測・stop)/ job 停止(ECO-902= 台帳不整合・receipt は有効)/ 測定不能 2(witness 不在・register に無い ECO)/ 台帳の作業木内拒否 / 引数不正 4 / 1 行 80 桁以内 / 配送先表と語彙の 1 対 1 |
| 2 配送先表 | `DELIVERY`(job 語彙 8 → next/human/factory/designer/process/ledger-owner/operator)+`WITNESS_DELIVERY`(witness CODE 15 → 配送先。GATE_FAIL= factory・receipt 欠陥= operator・STOP_TYPE は receipt の stop_type を DELIVERY で引く)。selftest が両表と語彙の集合一致を検査 |
| 3 非接触 | `bomdd-job.py`・`bomdd-witness.py`・`self-conformance.py`・hooks に diff 0(V3・§6) |

- **製造中の実測(正直記載)**: 初回 selftest で **3 件を自己捕捉** — STOP/UNMEASURABLE の 1 行が 80 桁超(83・85)・`WITNESS_DELIVERY` に `STOP_TYPE` 欠落。表示から「not launched」を落とし
  tree を `@12 桁` にして是正・表に STOP_TYPE を追加。V3 実測後に台帳へ `code` 欄を追加(receipt 欠陥の stop_type が job 語彙の `VERIFICATION_FAIL` に写るため、witness の CODE を別欄で残す)。
  手順逸脱: なし(Write・CR 0・検査と commit は別呼び出し)。

## 6. 受入の実測(製造者・2026-09-11)

- **V1**= PASS(`--selftest` exit 0・1 行目 `ADVANCE OK: selftest PASS(…)`・known-good 起動 1 / dry / known-bad 5+job 停止 1+測定不能 2 で起動痕跡なし)。
- **V2**= PASS(実 ECO= ECO-067 自身・dry): 台帳 1 行が機械回収(`verifier_line`= witness の 1 行目そのまま・decision ADVANCE・delivery next・cell null)。
- **V3**= PASS(Phase 6 の出口の初回実測・同一 job で前後): witness を現 tree で produce → `--cell "python -c …痕跡…"` で **起動**(痕跡ファイルに `ECO-067|<witness path>`・cell_exit 0・
  1 行目 `ADVANCE ECO-067 OK → next · launched(exit 0) @a67bba7a1c18`)→ witness の tree 末尾を改変 → 同じ cell で **起動せず**(`STOP ECO-067 TREE_MISMATCH → operator`・痕跡なし・
  exit 1)→ witness 復元 → dry ADVANCE。承認は起動先の既定(本実測の cell は python 1 行・承認なし)。
- **V6**= PASS(1 行 80 桁以内・selftest で全腕検査・実 ECO の 4 行も 45〜60 桁)。
- **V3'**(非接触): `git diff 3c14c83 --stat -- method/tools/bomdd-job.py method/tools/bomdd-witness.py method/tools/self-conformance.py bomdd/hooks`= 0(§7 で再確認)。self-conformance 全 PASS。
- **V4**(CI)・**V5**(Codex)= §7。
