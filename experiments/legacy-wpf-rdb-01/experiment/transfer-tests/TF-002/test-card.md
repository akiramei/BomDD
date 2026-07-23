# TF-002 Handoff Transfer Test Card

対象: INT-009修正後のhandoffだけを受け取る会話履歴なしworker  
比較元: TF-001と同じaccepted MIG-10 / GATE-MIG-10状態

## workerへ渡すもの

`project/bomdd/migration/handoffs/handoff-20260719T100155Z.md`だけを入口として指定する。

許可:

- handoff本文を読む。
- `Run now`に記載された完全一致の`check --milestone MIG-10`だけを実行する。

禁止:

- packet、source facts、第一worker log、中央method、sibling experimentを読む。
- `advance`を実行する。
- ファイルを変更する。
- organizerへ質問する。ただしhandoffだけでは一意に答えられない場合は質問数を記録してよい。

## 合格条件

| 問い | 正解 |
|---|---|
| Current milestone / STEP | MIG-10 / GATE-MIG-10 |
| Current milestone unaccepted | 0 |
| Current milestone missing approvals | 0 |
| Blockers | 0 |
| Gate evaluation | PASS |
| `check`の副作用 | read-only、Gate結果ファイルを保存しない |
| Gate結果を保存する操作 | PASS後の`advance`。再検査して保存後に次へ進む |
| future artifactの扱い | current blocker/unacceptedへ数えない |
| organizer clarification | 0 |

一項目でも誤答した場合はTF-002 FAILとする。Green/Yellowや条件付きPASSは使わない。

