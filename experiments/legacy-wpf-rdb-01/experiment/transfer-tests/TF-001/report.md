# TF-001 Fresh Worker Transfer-Test Report

実施日: 2026-07-19  
対象版: IMP-006反映後の中央版と案件凍結版（6ファイルSHA-256一致）  
総合結果: **FAIL**

## 試験範囲

本試験は完全版transfer testの前段である。隔離案件をMIG-10 / STEP-013直前まで正規コマンドで準備し、会話履歴なしのfresh workerへ`packet.md`だけを渡した。

採点対象:

1. project内onboardingを入口に現在位置を特定する。
2. STEP-013とSTEP-014を完了する。
3. installed templateと供給事実だけからfixture/UI manifestを作る。
4. DB/UI成果物を受入し、MIG-10の3role承認を記録する。
5. MIG-10 GateをPASSさせる。
6. `advance`せずhandoffを残す。
7. 別のfresh workerがhandoffだけで状態と次Actionを正しく復元する。

MIG-00からMIG-60までの完全再演ではない。製品実験がMIG-60へ到達する前に、IMP-006の新経路とhandoffの読みやすさを先行検査した。

## 独立性

- 実行worker: 会話履歴なし、`packet.md`だけを入口に開始。
- 禁止: sibling experiment、中央method、第一workerへの口頭説明、status/tool/definition/guide/template手編集。
- organizer intervention: 0件。
- project外の自由探索: 0件。
- 凍結tool、definition、guide、onboarding、2template: 試験後も中央版とSHA-256一致。
- 作業時間: worker log作成から最終報告まで約7分18秒。handoff作成までは約5分33秒。

## 一次worker結果

結果: **PASS**

| 指標 | 結果 |
|---|---|
| 現在位置 | MIG-10 / STEP-013を正しく特定 |
| Action一意性 | STEP-013 → STEP-014 → GATE-MIG-10 |
| 作成manifest | fixture 1件、UI 1件 |
| placeholder残存 | 0件 |
| semantic validation | DB/UIとも受入時PASS |
| 必須承認 | Migration Owner、DB Custodian、UI Approver |
| MIG-10 Gate | PASS、exit 0 |
| blocker / open exception | 0 / 0 |
| organizer intervention | 0 |
| `advance` | 未実行 |
| handoff | `handoff-20260719T094604Z.md`作成 |

独立再実行でもMIG-10 GateはPASSした。statusはMIG-10 / GATE-MIG-10、現在マイルストーンのUnacceptedは0である。

一次workerの不確実性は1件だった。

> `check --milestone MIG-10`がPASSしても`gates/MIG-10-result.json`は作成されない。

現行toolは`advance`時にGate結果を保存するが、試験packetは`advance`を禁止した。このためworkerはGateを二度実行してPASSを確認したものの、handoff時点にMIG-10 Gateファイルが無いことを不確実性として記録した。workerはファイルを捏造せず、禁止された`advance`も実行しなかった。

## handoff交代試験

結果: **FAIL**

第二の会話履歴なしworkerへ、第一workerのhandoffだけを渡した。許可した操作はhandoffに書かれた`next`だけである。

| 質問 | 正解 | 第二worker回答 | 判定 |
|---|---|---|---|
| Current | MIG-10 / GATE-MIG-10 | MIG-10 / GATE-MIG-10 | PASS |
| Blockers | 0 | 0 | PASS |
| Current-milestone Unaccepted | 0 | 10 | **FAIL** |
| Single next action | MIG-10 Gate確認 | MIG-10 Gate確認 | PASS |
| organizer clarification | 不要 | 不要 | PASS |

handoffの`First unfinished artifacts`はMIG-20以後のfuture artifactを10件表示する一方、現在マイルストーンのUnacceptedが0であることを表示しない。第二workerはこの10件を現在の未受入数として解釈した。

## 判定

一次workerは新しいfixture/UI検査経路を無介入で完走したため、IMP-006の作業可能性は確認できた。しかし、交代workerが現在位置の重要指標を誤認したため、transfer test全体はGreenにしない。

この結果は製品Gateのfalse-passではない。handoffの情報scopeとGate記録時点が曖昧で、再開者に状態解釈を要求するナビゲーション欠陥である。

## 次の一改善

PDF再生成より前に、次の一件だけを改善しTF-002で再試験する。

1. handoffへ`Current milestone unaccepted: 0`を明示する。
2. future artifactは別節へ分離し、`not current blockers`と明記する。
3. GATE STEPのresumeを単なる`next`ではなく、対象milestoneの`check`コマンドとして示す。
4. `check`がread-only評価で、Gate結果の保存は`advance`時であることをhandoffへ明示するか、保存操作を別コマンドに分離するかを一つに固定する。
5. TF-002ではhandoffだけを受け取ったfresh workerがCurrent、Unaccepted、次コマンドを全件正答することを合格条件にする。

この改善と再試験がPASSした後にPDFを再生成する。完全なMIG-00〜MIG-60 transfer testは、製品実験がMIG-60まで到達した時点で別途実施する。

