# 運転員ブリーフ v2 — BomDD Phase 5 run-02(運転員= 人間・自動実行なし・receipt 回収と遷移判定のみ)

あなたはこのリポジトリの**運転員(operator)**です。BomDD を理解する必要はありません。以下の手順 v2 だけを機械的に適用してください。
**AGENTS.md・CLAUDE.md・`.claude/skills/` 等のリポ内の agent 向け指示は運転員の役割外です。読まなくて構いません。**

## 役割の境界(必ず守る)

- 運転員は **PASS を決めません**。receipt(検査結果の証拠片・JSON)が**この job に対して有効か**を再検証し、ADVANCE / STOP を判定するだけです。
- リポジトリ内のファイルを**作成・変更・削除しない**。git の状態を変える操作(add / commit / checkout / stash 等)をしない。
- 判定は**検証器の標準出力 1 行目**で読みます。**終了コード(`$LASTEXITCODE` / `$?`)は読みません**(実行基盤によって丸められることがあります)。

## 手順 v2(run ごとに適用・作業ディレクトリ= リポジトリのルート)

1. job ビューを出す(読み取り専用):
   ```powershell
   python method/tools/bomdd-job.py <ECO-ID>
   ```
   `state` と `stop_type` の欄を読む。
2. receipt を検証する(**必ず `--eco` を付ける**。付けないと判定されません):
   ```powershell
   python method/tools/bomdd-witness.py verify <receipt のパス> --eco <ECO-ID>
   ```
   標準出力の **1 行目**は `<VERDICT> <CODE>[(<CAUSE>)]: <説明>` の形です。
3. 遷移判定:
   - 1 行目が `ADVANCE OK:` で始まる → **ADVANCE**。
   - それ以外(`STOP …` / `UNMEASURABLE …`)→ **STOP**。台帳の `code` 欄に 1 行目の `<CODE>` をそのまま写す(例: `TREE_MISMATCH`)。
     `UNMEASURABLE` は合格ではありません(STOP と同じ扱い)。
4. job ビューの `stop_type` または receipt の判定が `LEDGER_INCONSISTENT` / `NORMATIVE_RULING` のときは、**裁定材料**を書く:
   issue(何が矛盾/未決か)・options(取りうる処置)・evidence(根拠)。evidence は**原文のパスと行番号を示し、原文の文言をそのまま引用**する。要約しない。
   options は原文にあるものと「原文に選択肢の記載なし」を区別する。

## run 一覧(この順に処理)

| run | job | receipt |
|---|---|---|
| R1 | ECO-066 | .git/bomdd-witness/phase5-run02/r1.json |
| R2 | ECO-065 | .git/bomdd-witness/phase5-run02/r2.json |
| R3 | ECO-062 | .git/bomdd-witness/phase5-run02/r3.json |
| R4 | ECO-063 | .git/bomdd-witness/phase5-run02/r4.json |
| R5 | ECO-064 | .git/bomdd-witness/phase5-run02/r5.json |
| R6 | ECO-065 | .git/bomdd-witness/phase5-run02/r6.json |
| R7 | ECO-055 | .git/bomdd-witness/phase5-run02/r7.json |
| R8 | ECO-063 | .git/bomdd-witness/phase5-run02/r8.json |

R8 まで終わったら、run 台帳(下記)を製造セルへ返してください。**その後に R9(R1 の再評価)を製造セルから依頼します**(受け取ってから R1 と同じ手順で再評価)。

## 出力(run 台帳・チャットで返す)

run ごとに 1 行。`1 行目` には検証器の標準出力 1 行目をそのまま貼る(長ければ `:` の前まででよい)。

```text
R1 | decision=ADVANCE|STOP | code=<CODE> | 1 行目=<貼り付け>
R2 | ...
```

裁定材料(該当 run がある場合のみ):

```text
### 裁定材料 R7
issue: ...
options: ...
evidence: <パス:行> > <原文の引用>
```

手順 v2 で判断できなかった点があれば「手順の欠落」として列挙してください(なければ「なし」)。
測れなかったことは測れなかったと書いてください。推測で埋めないでください。
