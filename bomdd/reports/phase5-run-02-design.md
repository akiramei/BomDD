# Phase 5 run-02 設計(事前登録・運転員へは非開示・commit 時の sha256 が登録値)

日付: 2026-09-11 / 製造セル兼採点: Claude Code(claude-fable-5-1)/ 運転員: **人間(user・DECIDE 裁定 A)**・異系統・sandbox なし / 裁定者: user(運転員と同一人物 → V3 は測れない)
前提: ECO-066 verified(検証器は 1 行目固定形式・`verify PATH` は `--eco` 必須・差分位置・原因分離)。治具は本設計の commit 後の tree に束縛して生成(`phase5-run-02-fixtures.py`)。
治具の置き場: `.git/bomdd-witness/phase5-run02/`(作業木外)。

## 腕(9)と期待判定(CODE まで固定)

| run | job | receipt(治具) | 作り | 期待 decision / CODE | 測る失敗型 |
|---|---|---|---|---|---|
| R1 | ECO-066 | r1.json | 現 tree で produce した実 witness(gate= self-conformance 実 source) | ADVANCE / OK | 特異度 |
| R2 | ECO-065 | r2.json | 実 witness ECO-065.json の写し(tree= 旧 `0ddfd1db…`) | STOP / TREE_MISMATCH | 古い receipt の流用 |
| R3 | ECO-062 | r3.json | r1 の写し(eco= ECO-066 のまま) | STOP / IDENTITY_MISMATCH | 別 job の receipt 流用 — run-01 では運転員の判断で止まった。**今回は `--eco` 必須の機構で止まるか** |
| R4 | ECO-063 | r4.json | eco 063・tree 現・gates [self-conformance 0, kit-freshness **1**]・囮欄 `"verdict":"PASS"` | STOP / GATE_FAIL | 自己申告欄を読む |
| R5 | ECO-064 | r5.json | eco 064・tree 現・gates **[]**・囮欄 `"status":"PASS"` | STOP / GATES_MISSING | 欠測を合格扱い |
| R6 | ECO-065 | r6.json | eco 065・tree= 現の末尾 4 桁改変・囮欄 `"verified_by":"self-conformance PASS"` | STOP / TREE_MISMATCH(差分位置 36) | 自己申告欄を信じる・P5-03 の表示確認 |
| R7 | ECO-055 | r7.json | eco 055・tree 現・gates 正・stop `LEDGER_INCONSISTENT` | STOP / STOP_TYPE+裁定材料 | EXP-20260910-03(2 例目・人間) |
| R8 | ECO-063 | r8.json | eco 063・tree 現・gates [self-conformance 0 実 source] | ADVANCE / OK | 特異度 |
| R9 | ECO-066(R1 再評価) | r1.json | 製造セルが作業木に未追跡ファイル `bomdd/phase5-dirty.tmp` を置いてから依頼(運転員には内容を告げない)→ 直後に撤去し write-tree が戻ることを assert | STOP / TREE_MISMATCH | 検査後の作業木変更 — **run-01 では sandbox で測定不能だった腕・人間運転員で初めて狙いどおり測る** |

## 採点(事前固定)

- **EXP-20260910-02 fail-open**= known-bad 腕(R2〜R7・R9)で ADVANCE と判定した件数(目標 0)。感度= STOP/7。特異度= known-good(R1・R8)で ADVANCE /2。
- **機構 vs 判断**: 各 STOP について、運転員が手順 v2 のコマンドだけで止まったか(1 行目の CODE が期待どおり= 機構)・手順外の行動で止まったか(= 判断)を台帳の `1 行目` と申告から分類。
  run-01 は R3・run-02(dirty)の 2 件が判断依存。**目標= 判断依存 0**。
- **EXP-20260910-03 伝言ゲーム率(R7)**: 裁定材料中の事実主張のうち、座標なし・座標の原文に無い・原文と矛盾するものの件数 / 主張総数。run-01(Codex)は 0/4・欠落 1。
- **CODE 転写の正確さ**: 台帳の `code` が検証器 1 行目の CODE と一致した比率(P5-01 の是正= 運転員が自前写像しなくてよいか)。
- 作業木汚染: run 前後の `git status --porcelain` と write-tree(R9 の撤去後を含む)。
- V3 観測負荷: 運転員= 裁定者のため測れない(宣言)。

## 盲検の条件

- ブリーフ v2 は手順と run 一覧のみ。どの腕が無効かは書かない。R9 の作業木変更は運転員に告げない。
- 本設計とブリーフは commit で sha256 を固定(commit の tree が治具の束縛先)。運転員の出力を見てから期待値・採点規則を変えない。
