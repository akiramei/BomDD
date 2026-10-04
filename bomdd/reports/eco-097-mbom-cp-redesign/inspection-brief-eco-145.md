# 検査ブリーフ — ViewPrism2 ECO-145 導出の意味の審査(BomDD ECO-097 事前登録 R6・検査官= EQ-002)

- 役割: **inspector(検査官)**・EQ-002(Codex CLI / gpt-5.6-sol)。責任= 統括 AI(claude-fable-5-1)が導出した「テスト → 裁定層の ID の対応」と「M-BOM の行の分類」が、裁定層の文に照らして正しいかの判定。
- 対象リポ: C:\Users\akira\source\repos\ViewPrism2(作業ディレクトリ= リポのルート)。対象= **作業ツリー**(未 commit の変更 8 ファイルを含む。`git rev-parse HEAD` と `git status --short` を開始時と終了時に写す)。
- 禁止(観測可能): ファイルの作成・変更・削除 0・commit 0・テストやビルドの実行は任意(sandbox が NuGet を拒否する場合は読解で判定してよい)。外部 API は呼ばない。
- 読んでよいもの: `bomdd/10-requirements.yaml`・`bomdd/20-spec.md`・`bomdd/30-ebom.yaml`・`bomdd/31-kbom.yaml`・`bomdd/32-mbom.yaml`・`bomdd/33-control-plan.yaml`・`bomdd/cp_results.py`・
  `tests/ViewPrism2.Tests/CpThumb007Tests.cs`・`CpThumb049ExifTests.cs`・`CpThumb144VersionPinTests.cs`・`CpDb006Tests.cs`・`git diff`・`git show HEAD:<上のファイル>`。
- 読まないもの: `bomdd/60-change-order-*.md`・`bomdd/60-change-register.yaml`・`.claude/`・`AGENTS.md`・`CLAUDE.md`・BomDD リポ(製造者の導出記録と結論を見ずに判定する)。
- **報告の正本経路**: 報告ファイルを自分で書かない。最終メッセージ全文をハーネスが保存する。1 行目(任意の `[INFORM / COMPLETE]` の次の最初の非空行)は行頭から `ACCEPT` / `REJECT IA-…` / `UNMEASURABLE <理由>`。

## 審査すること

### A. テスト → 要求の対応(ID ごとに 合 / 否 / 条件付き)

4 つのテストファイルで、メソッドに `[Trait("req", "REQ-NNN")]` が付いている(28 個)。ID ごとに次を判定する:

1. その ID の trait を持つテストは、`bomdd/10-requirements.yaml` のその REQ の **statement が述べること**を本当に検査しているか(テストの本体を読んで判定する。名前だけで判定しない)。
2. その REQ の statement のうち、trait を持つテストが**検査していない部分**は何か(全部を覆う必要はない。覆っていない部分を列挙する)。
3. trait が付いていないテスト 2 本(`解像度取得はフルデコードなしで寸法を返す`・`COLLATE_NOCASEが主要列に付与されている`)に、当てるべき REQ があるか(あれば ID と理由)。
4. 付けるべきでない trait(テストがその REQ を検査していない)があるか。

対象の ID: REQ-003・REQ-004・REQ-010・REQ-028・REQ-040・REQ-085・REQ-104・REQ-105・REQ-106。

### B. Control Plan の行の refs

`bomdd/33-control-plan.yaml` の CP-THUMB-007 と CP-DB-006 の `requirement_refs` / `invariant_refs` について:

5. refs にあるが、その行のテストが検査していない ID はあるか(INV-009 は検査するテストが無いことを製造者が認識済み= 表に「検査なし」と出る。それ以外)。
6. その行のテストが検査しているのに refs に無い裁定層の ID はあるか。
7. `when` / `on_fail` の値は、その行の検査の実態と矛盾しないか。

### C. M-BOM の行の分類

`git diff bomdd/32-mbom.yaml` で、M-THUMB-008 と M-DB-007 の `invariants` 計 6 行が削除されている(M-DB-007 には `manufacturing_decisions` 1 行が追加)。削除された各行について:

8. その行の内容は、裁定層(10・20・30・31)のどこかに**同じ内容で**書かれているか(所在をファイルと行で示す)。裁定層に無い内容が削除で失われていないか。言い換えで意味が狭まった・広がった箇所はあるか。
9. `manufacturing_decisions` の 1 行は、K-BOM(31)の記述と一致するか。

### D. 表(cp_results.py)— 任意

10. `python bomdd/cp_results.py --selftest` を実行できれば結果を写す。ID ごとの区分の定義(docstring と `classify_ruled`)に、検査が届いていない ID が「合格」や「人の承認で検査」に見えてしまう経路があるか(読解でよい)。

## 判定

- **ACCEPT**: A〜C に「否」が無い(条件付き・覆っていない部分の列挙は ACCEPT でよい)。
- **REJECT IA-NN**: 「否」が 1 件以上(誤った trait・裁定層に無い内容の喪失・refs の誤り)。所見ごとに IA-NN・blocking / non-blocking・根拠(ファイル:行)。
- 範囲外の観察は「範囲外の観察」に書き、判定に含めない。

## 報告の様式(最終メッセージ全文)

```
[INFORM / COMPLETE]

ACCEPT            ← または REJECT IA-… / UNMEASURABLE <理由>

- inspector: EQ-002 / Codex CLI / <model>
- 対象: HEAD <sha>+作業ツリー
- commit: 0 / ファイル変更: 0
- 開始時 git status --short: … / 終了時: …
- 読んだファイル一覧: …

## A. ID ごとの判定
| ID | 判定(合/否/条件付き) | 検査している内容 | statement のうち検査していない部分 |

## A-3・A-4 / B / C / D
(項目 3〜10 を 1 つずつ)

## 所見(IA-NN・blocking / non-blocking)

## 範囲外の観察(判定に含めない)
```
