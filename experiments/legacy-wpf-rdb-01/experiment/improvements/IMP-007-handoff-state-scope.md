# IMP-007 — handoffの現在状態scopeとGate再開手順を固定する

## 問題

TF-001の一次workerは介入0でMIG-10 GateをPASSした。しかしhandoffだけを受け取った別workerは、`First unfinished artifacts`に列挙された将来成果物10件を現在マイルストーンのUnacceptedと解釈した。正解は0件だった。

一次workerも、`check`がPASSなのに`gates/MIG-10-result.json`が無いことを不確実性として記録した。現行仕様では`check`はread-only、`advance`が再検査・Gate結果保存・次milestone移動を行うが、handoffと`next`がその境界を示していなかった。

## 今回変更するもの

- handoff headerのcurrent-milestone unaccepted件数。
- handoff headerのcurrent-milestone missing approvals件数。
- current、historical inconsistency、future artifactの別scope表示。
- future節の`not current milestone blockers`表記とdue milestone。
- GATE位置のhandoff生成時read-only Gate評価。
- GATE位置の正確な`check --milestone`再開コマンド。
- PASS後の正確な`advance`コマンド。
- `check`はread-only、`advance`が再検査・保存・移動する説明。
- `next`のGATE位置表示を同じ二段コマンドへ統一。

## 今回変更しないもの

- `check`をwrite操作へ変更しない。
- `advance`のGate再検査・保存・移動を分割しない。
- artifact、approval、milestoneの状態遷移を変更しない。
- fixture/UI semantic validationを変更しない。
- PDFを再生成しない。
- client-server RDB実験を開始しない。

## 合格条件

1. GATE-MIG-10 handoffにCurrent Unaccepted 0とMissing approvals 0が明記される。
2. future artifactが別節にあり、現在blockerではないと明記される。
3. handoff生成時のread-only Gate評価がPASSと表示される。
4. Resumeの最初のコマンドが`check --milestone MIG-10`である。
5. PASS後の`advance`と保存境界が明記される。
6. `next`も同じ`check`→`advance`順を一意に表示する。
7. 会話履歴なしworkerがhandoffだけで9問を全正答する。
8. organizer clarification 0、ファイル変更0、`advance`未実行である。
9. 中央・凍結自己テスト、既存MIG-00/10 GateがPASSする。

## 変更前

TF-001 replacement worker:

| 指標 | 結果 |
|---|---|
| milestone / STEP | 正答 |
| blocker | 正答 |
| next Action | 正答 |
| Current Unaccepted | **10と誤答。正解0** |
| clarification | 0。ただし誤認したまま完了 |

handoffにはcurrent件数がなく、future artifact 10件がscopeなしで表示され、Resumeは`next`だけだった。

## 実装

`handoff`は案件で凍結されたmilestone definitionから各artifactのdue milestoneを逆引きする。現在milestoneのrequired artifactだけでcurrent unacceptedを計算し、futureはdue milestone付きの別節へ置く。過去milestoneの未受入が存在する場合はhistorical inconsistencyとしてさらに別節へ出す。

GATE STEPでは`check_gate`をread-onlyで実行してhandoffへ現在評価を表示する。再開は`check --milestone`、PASS後は`advance`の二行に固定する。`next`も同じ順と永続化境界を表示する。

中央selftestへ、GATE-MIG-10 handoffのcurrent/future分離、PASS評価、正確な二コマンド、旧`First unfinished artifacts`節の不在を追加した。

## 変更後

TF-002はTF-001と同じaccepted MIG-10 / GATE-MIG-10状態から作成した。

会話履歴なしworkerはhandoffだけを読み、記載された`Run now`だけを実行した。

| 指標 | 結果 |
|---|---|
| Current milestone / STEP | 正答 |
| Current Unaccepted / missing approvals | 0 / 0、正答 |
| Blockers | 0、正答 |
| Gate | PASS、正答 |
| check persistence | 保存しない、正答 |
| advance semantics | 再検査・保存・次へ移動、正答 |
| future artifact | current failureへ数えない、正答 |
| organizer clarification | 0 |
| file mutation / advance | 0 / 未実行 |

TF-002結果は`transfer-tests/TF-002/report.md`に保存した。

実証案件のMIG-20 / STEP-021 handoffでも、current unaccepted 6件、missing approval 1件と、MIG-30以後のfuture artifactが別節に出ることを確認した。

## 効果判定

合格条件を満たした。交代者は将来backlogを現在Gateの不足へ数えず、Gate評価・保存・移動の境界を設計する必要がない。TF-001の一件だけを変更し、TF-002で同じ状態の誤読が0へ変わった。

## 残る限界

- handoffは先頭10件のfuture artifactだけを表示する。これは現在の不足ではないため作業継続を妨げないが、全件棚卸しはstatus/definitionを使う。
- 完全なMIG-00〜MIG-60 transfer testは、製品実験がMIG-60へ到達後に必要である。
- 実案件でroleが別人の場合のhandoff承認引継は未検証である。

