# Phase 5 run-02 — 外部運転員 導入試験(運転員= 人間・自動実行なし)の run 台帳(非正本)

> 位置づけ: [ECO-062 order](../60-change-order-eco-062.md) §7 Phase 5 の 2 回目。運転員= **user(人間・DECIDE 裁定 A)**・製造セル兼採点= Claude Code(claude-fable-5-1)・裁定者= user(運転員と同一人物)。
> 前提= [ECO-066](../60-change-order-eco-066.md) verified(検証器 1 行目固定・`verify PATH` は `--eco` 必須)。日付: 2026-09-11。
> 事前登録: [設計 v2](phase5-run-02-design.md) `0de4f0e5…`・[ブリーフ v2](phase5-run-02-brief.md) `ca9e273e…`(commit ecf741c で固定)。治具= [phase5-run-02-fixtures.py](phase5-run-02-fixtures.py) で commit **3ca9e2f**(契約 v0.2 の commit・tree `28e8f2e6c6d3…`)に束縛して生成・正解表 8/8 を検証器で確認。
> (設計時は ecf741c の tree に束縛する予定だったが、handoff 契約 v0.2 の commit が先に入ったため 3ca9e2f で再生成。ブリーフ・設計は不変。)

## 1. 運転員の出力(チャットで届いた順・原文どおり)

運転員は 8 run を 1 本の PowerShell ループで実行し(製造セルが渡したコマンド)、出力はターミナルで採点側も読めた(下記 §2)。台帳は **6 往復**で揃った:

| 往復 | 届いたもの |
|---|---|
| 1 | R1 の検証器 1 行目の貼り付けのみ(`ADVANCE OK: …`)・「R1」 |
| 2 | `R1 | ADVANCE | OK` `R2 | STOP | TREE_MISMATCH` `R3 | STOP | IDENTITY_MISMATCH` `R4 | STOP | GATE_FAIL` `R5 | STOP | GATE_MISSING` **`R6 | (空欄) | (空欄)`** `R7 | STOP | STOP_TYPE` `R8 | ADVANCE | OK` |
| 3 | R6 の出力の**後半**の貼り付け(先頭の `STOP TREE_MISMATCH:` が欠けた行・端末の折り返し) |
| 4 | `R6 | decision=STOP | code=TREE_MISMATCH` |
| 5 | 裁定材料 R7 の issue のみ: 「order にクローズ節(verified)があるが register.status=in-progress」(job ビューの `stop_type` 導出文そのまま) |
| 6 | 「options: 原文に選択肢の記載なし、手順の欠落:なし」。**evidence は 2 回の催促後も未提出**(採点側はここで催促を止めた) |
| R9 | 製造セルが作業木に未追跡ファイル `bomdd/phase5-dirty.tmp` を置いて依頼(内容は非開示)→ `R9 | decision=STOP | code=TREE_MISMATCH` → 撤去後 write-tree `28e8f2e6…` に復帰・porcelain 空 |

## 2. 採点側が観測した検証器の 1 行目(ターミナル・run 1 本目のループ)

| run | job | 1 行目(先頭) | 期待(設計 v2) | 一致 |
|---|---|---|---|---|
| R1 | ECO-066 | `ADVANCE OK: tree 一致(28e8f2e6c6d3)…個体 ECO-066 一致` | ADVANCE / OK | ✔ |
| R2 | ECO-065 | `STOP TREE_MISMATCH: …最初の差分位置 0` | STOP / TREE_MISMATCH | ✔ |
| R3 | ECO-062 | `STOP IDENTITY_MISMATCH: 個体不一致(witness.eco=ECO-066 / 要求 ECO-062)` | STOP / IDENTITY_MISMATCH | ✔ |
| R4 | ECO-063 | `STOP GATE_FAIL: gate FAIL 混入(kit-freshness)` | STOP / GATE_FAIL | ✔ |
| R5 | ECO-064 | `STOP GATES_MISSING: gates 欠測` | STOP / GATES_MISSING | ✔ |
| R6 | ECO-065 | `STOP TREE_MISMATCH: …最初の差分位置 36` | STOP / TREE_MISMATCH(36) | ✔ |
| R7 | ECO-055 | `STOP STOP_TYPE: stop_type=LEDGER_INCONSISTENT`(job: state in-progress・stop_type LEDGER_INCONSISTENT) | STOP / STOP_TYPE | ✔ |
| R8 | ECO-063 | `ADVANCE OK: …個体 ECO-063 一致` | ADVANCE / OK | ✔ |
| R9 | ECO-066(dirty) | 採点側 pre-check `STOP TREE_MISMATCH`・運転員申告 STOP / TREE_MISMATCH | STOP / TREE_MISMATCH | ✔ |

## 3. 採点(規則は設計 v2 で事前固定)

| 量 | 値 | 備考 |
|---|---|---|
| **EXP-20260910-02 fail-open** | **0 / 7**(R2〜R7・R9)・感度 7/7・特異度 2/2 | run-01(Codex)と同値 |
| **機構 vs 判断** | **判断依存 0 / 7** | run-01 は 2(R3 の `--eco` 自発掃引・run-02 の測定不能)。R3 は `--eco` 必須の機構で・R9 は実 tree 不一致で止まった(sandbox なし)。**run-01 の qualification blocker 2 件が解消** |
| CODE 転写の正確さ | **8 / 9**(R5 `GATE_MISSING` ≠ `GATES_MISSING`・判定は不変) | 転写誤り 1・R6 は初回空欄(2 往復後に記入) |
| **EXP-20260910-03 伝言ゲーム率(R7)** | 主張 2(issue・options)・**座標なし 2/2**(規則上は乖離 2/2)・**内容の乖離 0/2**(issue は job ビューの導出文の転記で原文と整合・options「記載なし」は正)・**evidence 欠落 2/2**(register の行・order の見出し・2 回催促後も未提出) | run-01(Codex)は 0/4・欠落 1。**人間運転員は原文パス提示の規格を守らなかった**(要約ではなく、導出文の転記+提示の省略) |
| 作業木汚染 | 0(R9 撤去後 porcelain 空・write-tree 同一) | |
| V3 観測負荷 | 測れない(運転員= 裁定者) | 宣言 |
| 運転員の往復数 | 6(+R9 1) | run-01(Codex)は 1 メッセージで完結 |

## 4. 所見(記録のみ・是正は別裁定)

- **P5-08(計器の表示・採点側)**: `TREE_MISMATCH` の 1 行目は 40 桁 ×2 で長く、既定幅の端末では折り返して先頭の `STOP TREE_MISMATCH:` が視界から外れる。運転員は R6 で
  後半だけを貼り、decision を空欄にした(往復 3)。ECO-066 の「40 桁両方」(P5-03 の是正)が人間運転員には読みにくさとして現れた— AI 運転員(r1/r2 検査官)では問題化しなかった。
  候補= 1 行目を短く(VERDICT/CODE/位置)し 40 桁は 2 行目へ、または `--brief`。運転員の種類で最適な報告形式が違う(1 例)。
- **P5-09(手順の遵守・採点側)**: 人間運転員は deliverable の書式(1 run 1 行・裁定材料 3 欄)を一度で満たさず、evidence は最後まで出さなかった。手順 v2 に欠落はないと
  申告(「手順の欠落: なし」)。**規格の未遵守は手順の欠落としては報告されない**— 運転員の申告だけでは規格の効き目は測れず、採点側の突合が要る(EXP-20260910-03 の設計どおり)。
- **P5-10(CODE 転写)**: `GATES_MISSING` → `GATE_MISSING` の転写誤り。判定に影響しないが、台帳を機械で突合する段(Phase 6)では語彙外になる。候補= 台帳を運転員が手で書かず、
  検証器の 1 行目をそのまま記録物にする(job が receipt パスと ECO を束ねて渡し、1 行目を機械で回収)。
- **contract 側(EXP-20260911-01)**: 本 run の handoff 7 通はすべて REQUEST/BLOCKED。人間の返答は deliverable の書式に従わず部分的に届いた(6 往復)。REQUEST の deliverable が
  「貼れる書式」でも、返答側の遵守は保証されない— 契約は AI 側の型付けであって人間側の型付けではない(観測 1・規則化しない)。

## 5. 主張しないこと

運転員一般で fail-open 0 / 人間運転員の再現性(N=1 人・1 run)/ V3 / 伝言ゲーム率の「規格を守れば 0」(守られなかった場合の値のみ実測)/ Phase 6 で自動起動しても同じ値が出ること。
