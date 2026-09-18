[INFORM / COMPLETE]
ACCEPT — IA-07 の是正を確認し、指定された5項目すべてで退行なしと判定します。

- range: 是正確認＋回帰（指定項目1〜5のみ）
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol / r1〜r3と同系統・別セッション
- 対象 revision: `5c593ab4d2f89bef7ae8c099f5d20eded3f7008e`
- commit: 0
- リポ内ファイル書込み: 0
- 外部 API: 呼び出しなし
- `jev_qual_0*.py`: 実行なし
- human_action: none
- execution: COMPLETE — 指定範囲の検査を完了

開始時 `git status --short`:

```text
（出力なし）
```

終了時 `git status --short`:

```text
（出力なし）
```

| 項目 | 観測 | 判定 |
|---|---|---|
| 1 / 差分限定 | `c5ea61d..5c593ab...` は3ファイルのみ。order §5.3が9行追加、r3報告が71行追加、registerは`allowed_paths`へのr4報告パス追加と対応コメント変更を含む物理1行の置換。テンプレ・スクリプト・JSONL・READMEの差分は0。 | **PASS（IA-07解消）** |
| 2 / IA-06維持 | README冒頭に旧3ファイルは16桁接頭辞、03b以降は64桁との注記あり。対象revisionの全行解析で `results.jsonl` 78/78、`results-02.jsonl` 150/150、`results-03.jsonl` 27/27が小文字16進16桁、`results-03b.jsonl` 27/27が64桁。解析エラー・形式不一致は0。 | **PASS（退行なし）** |
| 3 / §3不変 | `git diff --unified=0 0e50b2f 5c593ab... -- bomdd/60-change-order-eco-080.md` に§3のhunkなし。両revisionから抽出した§3は各8行で完全一致。 | **PASS（退行なし）** |
| 4 / 窓 | `0e50b2f..5c593ab...` は13ファイル・754 insertions / 4 deletions。13/13が指定allowed_paths内、範囲外パス0。playbook、`change-management.md`、`acceptance-evidence.md`、既存orderの差分なし。 | **PASS（退行なし）** |
| 5 / テンプレ維持 | `git diff a3c95ee 5c593ab... -- method/templates/60-change-order.md` は空。両revisionの内容ハッシュも同一（`aa3d89ff02a1ece1c166106bbff6bd3281ff8db7`）。二部形5行とUNMEASURABLE要件は不変。 | **PASS（退行なし）** |

## 較正 receipt

### 査定した主張と判定

- 「IA-07の原因だった差分限定条件が是正された」: **observed × 適格**。実差分はブリーフが許容する受理側記録を含む3ファイルだけ。
- 「IA-06とr2/r3でPASSだった指定回帰項目に退行がない」: **observed × 適格**。JSONL全282行、§3、窓、テンプレ不変を対象revisionから直接測定。
- 「対象revisionを本roundの受入根拠としてACCEPTできる」: **observed × 適格（指定された5項目の範囲内）**。

### 計器欠陥

- 判定に影響する計器欠陥: なし。
- 大容量文書の一括表示で切詰めが発生したため、対象節を個別に再取得した。欠測を判定へ使用していない。

### battery

| 問い | 記録 |
|---|---|
| Q1 | asked — ブリーフの限定条件を実際のパス差分・行差分と照合 |
| Q2 | NA — known-good/known-badによる常設計器の較正は今回の範囲外 |
| Q3 | asked — 5項目を独立判定 |
| Q4 | asked — README・JSONL・§3・テンプレを対象revisionから直接取得 |
| Q5 | asked — 欠測、解析エラー、形式不一致をPASSに算入せず |
| Q6 | asked — 測定結果を観測後に次の判定へ進行 |
| Q7 | NA — 常設検査器の健全性主張ではない |
| Q8 | NA — 予防ゲート・免除は範囲外 |
| Q9 | asked — 対象と基準revisionをfull SHAへ解決 |
| Q10 | asked — 下記の検出力限界を宣言 |
| Q11 | asked — 16桁の旧3ファイルと64桁の03bを別クラスで全行測定 |

### 検出力の限界

- `state_sha256` は桁数と小文字16進形式を測定した。元のstateから値を再計算して接頭辞・完全SHA-256の真正性までは確認していない。
- 外部API原応答との一致やJevの再実行は測定していない。
- IA-01〜IA-05の境界探索、CI、self-conformance、ECO-080全体の再受入は今回の指定範囲外。
- `allowed_paths` はパス所属を検査したもので、範囲内全ファイルの意味内容を再監査したものではない。

## 範囲外の観察

- なし。