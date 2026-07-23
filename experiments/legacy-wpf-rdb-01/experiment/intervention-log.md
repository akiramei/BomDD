# 手引き介入ログ

手引き・`status`・`next` だけでは作業を一意に継続できなかった時点で、解決前に記録する。

| ID | Run/Step | 観測 | 作業継続に必要だった介入 | 分類 | 影響 | 改善状態 |
|---|---|---|---|---|---|---|
| INT-001 | RUN-A1 / MIG-10 先行観測 | PC に Go と Docker がなく、現行版の標準 build/run が不能。既存 EX-BASELINE-001 はあったが代替物の同一性確認順が不足 | Git tag と release asset 定義を調べ、同一 commit の公式 Windows binary を選定 | 例外処置不足 | 作業者が実行方式と同一性条件を設計する必要がある | adopted in Rev-A: STEP-012 と EX-BASELINE-001 に固定順を追加 |
| INT-002 | RUN-A1 / STEP-001-004 | 三成果物を accepted にする方法が手引きにも command help にもない | 工具 source の selftest を読み、status の artifact/evidence/approval 構造を発見 | 工具不足・手順不足 | Gate 操作のために内部実装の自由探索が必要 | adopted in Rev-A: `accept-artifact` と `approve` |
| INT-003 | RUN-A1 / STEP-002 | init が生成した Charter に `Claude Code` など移行案件と無関係な新規開発文言が残る | 実験 Charter として全面記入し直した | 成果物不足 | 記入者が残す項目を判断する必要がある | adopted in Rev-A: scenario-specific `migration-charter.md` |
| INT-004 | RUN-A1 / STEP-001-004 | `next` は次 STEP を表示するが、STEP 完了を記録する command がないため `status` は STEP-001 のまま | status JSON の current/next を手で更新 | 工具不足 | 現在位置の正本が実作業に追従しない | adopted in Rev-A: `complete-step --evidence` と step history |
| INT-005 | RUN-A1 / MIG-10→20 | `advance` が current owner を `UNASSIGNED` に戻し、`status` も owner を表示しない | status を手修正 | 工具不足 | 作業者が自分の担当かを状態表示から確認できない | adopted in Rev-A: profile の Migration Worker を継承して表示 |
| INT-006 | IMP-002後 / MIG-10受入後変更 | Gateはhash mismatchを検出するが、`next`はMIG-20 / STEP-021の通常作業を指し続け、過去MIG-10の復旧入口がない | 工具内部を読んで再受入方法を設計する必要があった | 工具不足・手順不足 | 作業者が旧承認・旧Gateの扱いと戻り先を判断しなければならない | adopted in IMP-003: `change-open`から`change-close`までの強制状態遷移 |
| INT-007 | IMP-003後 / blocker操作 | 例外票templateとカタログはあるが、登録・分類・blocker追加・安全作業・解消・status解除を手で行う必要があり、`exception-open`はinvalid choice | statusと例外票を手編集する操作設計が必要 | 工具不足・手順不足 | 現在位置とGate停止条件を壊す危険があり、解消証跡なしでもblockerを消せる | adopted in IMP-004: catalog/open/safe-work/resolveコマンドと例外seal検査 |
| INT-008 | MIG-00 / STEP-003とIMP-004後のGate監査 | Runbookは現行観測・棚卸し・仕様復元前に8技術判断を全決定するよう要求する一方、Gateは8件すべてopenでもPASSした | 実験者が先行調査して全判断をprofileへ書いた | 判断時期・Gate不足 | 情報不足時の早すぎる選定か、未決定のまま依存工程へ進むかの二択になる | adopted in IMP-005: MIG-30/40/80の期限別成果物、decision-record、累積Gate検査 |
| INT-009 | TF-001 / GATE-MIG-10 handoff | 一次workerは介入0でGate PASSしたが、handoffだけを受け取った別workerがfuture artifact 10件をcurrent-milestone Unacceptedと解釈した。`check` PASS時点のMIG-10 Gate fileも無く、記録時点に不確実性が残った | organizer介入は要求されなかったが、独立採点で正解0に対し10と判定 | 工具不足・手順不足 | 交代者が現在Gateの不足と将来backlogを区別するために状態scopeとGate保存時点を推測する | adopted in IMP-007: current/future分離、Gate check/advance境界、TF-002 fresh worker全9問正答・介入0 |

## 改善判定欄

各項目は `adopted`、`deferred`、`rejected` のいずれかと、変更先・検証結果を追記する。Run A1 の凍結資料は `experiment/run-a1-kit/` に保存し、正本と Run A2 の凍結資料で改善を検証する。
