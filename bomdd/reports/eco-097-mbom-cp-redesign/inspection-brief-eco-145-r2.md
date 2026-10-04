# 検査ブリーフ r2 — ViewPrism2 ECO-145 導出の意味の審査(是正確認+回帰・検査官= EQ-002)

- 役割: **inspector(検査官)**・EQ-002(Codex CLI / gpt-5.6-sol)。対象リポ: C:\Users\akira\source\repos\ViewPrism2(作業ディレクトリ= リポのルート)。対象= **作業ツリー**(未 commit の 8 ファイル)。
- 前回(r1): REJECT IA-01(blocking: `破損キャッシュは削除して再生成する` の REQ-106 trait は statement と対応しない)。non-blocking= `COLLATE_NOCASEが主要列に付与されている` は REQ-010 と REQ-014 に対応・CP-DB-006 の refs に REQ-014 が無い。範囲外の観察= CP-DB-006 の characteristic が「REQ-003〜005」のまま。
- 禁止・読んでよいもの・読まないもの・報告の正本経路は r1 と同じ(ファイルの作成・変更・削除 0・commit 0。`bomdd/60-change-order-*.md`・`bomdd/60-change-register.yaml`・`.claude/`・`AGENTS.md`・`CLAUDE.md`・BomDD リポは読まない。
  最終メッセージ全文をハーネスが保存する。1 行目〔任意の `[INFORM / COMPLETE]` の次の最初の非空行〕は行頭から `ACCEPT` / `REJECT IA-…` / `UNMEASURABLE <理由>`)。

## 本 round の範囲

1. **IA-01 の是正確認**: `tests/ViewPrism2.Tests/CpThumb007Tests.cs` の `破損キャッシュは削除して再生成する` の trait が REQ-040 だけになっていること。`bomdd/33-control-plan.yaml` の CP-THUMB-007 の該当 vector の対応が REQ-040 に改められていること。
   是正後、REQ-106 の trait を持つテストは `壊れたJpgはNullでキャッシュ記録なし_FMEA012` の 1 本になる — REQ-106 の判定(合 / 否 / 条件付き)を付け直す。
2. **non-blocking の是正確認**: `COLLATE_NOCASEが主要列に付与されている` に REQ-010 と REQ-014 の trait・CP-DB-006 の `requirement_refs` に REQ-014・characteristic の文言。REQ-014 の判定(合 / 否 / 条件付き)を新しく付ける。
3. **回帰**: r1 で 合 / 条件付き とした他の ID(REQ-003・004・010・028・040・085・104・105)の trait が r1 から変わっていないこと(REQ-010 は COLLATE のテストが加わった分を含めて判定を確認)。M-BOM(32)が r1 から変わっていないこと。
4. **是正が新しい誤りを入れていないこと**: 付けるべきでない trait・refs の誤りが新しく生じていないか。

r1 と同じく、判定は `bomdd/10-requirements.yaml` の statement を基準にする。新しい境界探索は「範囲外の観察」に書く(判定に含めない)。

## 判定

- **ACCEPT**: 1〜4 に「否」が無い。
- **REJECT IA-NN**: 「否」が 1 件以上。所見ごとに IA-NN・blocking / non-blocking・根拠(ファイル:行)。

## 報告の様式(最終メッセージ全文)

```
[INFORM / COMPLETE]

ACCEPT            ← または REJECT IA-… / UNMEASURABLE <理由>

- range: 是正確認+回帰
- inspector: EQ-002 / Codex CLI / <model>
- 対象: HEAD <sha>+作業ツリー
- commit: 0 / ファイル変更: 0
- 開始時 git status --short: … / 終了時: …
- 読んだファイル一覧: …

## 判定概要
| 項目 | 判定 | 観測 |
(1〜4 を 1 行ずつ)

## ID ごとの判定(r1 → r2)
| ID | r1 | r2 | 変化の理由 |

## 所見(あれば IA-NN)

## 範囲外の観察(判定に含めない)
```
