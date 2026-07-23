# 実行ログ

## RUN-A / 2026-07-19

| Seq | 現在位置 | Action | 結果 | 証跡・備考 |
|---:|---|---|---|---|
| 001 | 選定前 | OSS 候補を license、RDB、規模、検証幅で比較 | Traggo を採用 | `candidate-selection.md` |
| 002 | 選定前 | 原版を取得し commit を固定 | `v0.8.3` と HEAD が同一 | `source-lock.json` |
| 003 | STEP-001 | シナリオを init | 成功、MIG-00 / STEP-001 | `bomdd/migration/migration-status.json` |
| 004 | STEP-001 | `status` と `next` を実行 | Action は一つ。ただし三成果物の具体的な受入操作は表示されない | INT-002 |
| 005 | MIG-10 先行観測 | 元システム実行環境を確認 | Go と Docker がない | INT-001。まだ Gate 受入には使用しない |
| 006 | MIG-10 先行観測 | 同一 commit の公式 Windows binary を取得 | SHA-256 固定、HTTP 200 | `source-lock.json`、runtime logs |
| 007 | MIG-10 先行観測 | ログイン、タグ、timer、一覧、calendar を操作 | 成功 | `bomdd/migration/evidence/current-ui/` |
| 008 | MIG-10 先行観測 | 停止後 DB を fixture 化 | integrity ok、FK 違反 0 | `fixtures/baseline/traggo.db` |
| 009 | MIG-00 Gate | Charter、profile、roles、承認を受入 | PASS、MIG-10 へ advance | `bomdd/migration/gates/MIG-00-result.json` |
| 010 | MIG-10 Gate | 原版、実行、DB、UI観測を受入 | PASS、MIG-20 へ advance | `bomdd/migration/gates/MIG-10-result.json` |
| 011 | Rev-A | INT-001～004 を手順、例外、template、tool へ還元 | selftest PASS | `method/scenarios/legacy-to-wpf-rdb/` |
| 012 | MIG-10 post-accept QA | PNGを目視し、calendar event が viewport 外と確認 | DOM extract を追加し、証跡の主張を訂正 | `MIG-10-correction-001.md` |
| 013 | Rev-A | advance 後 owner が UNASSIGNED になる欠陥を検出 | Migration Worker の継承と status 表示を追加 | INT-005 |
| 014 | IMP-001 | 凍結工具の自己テストだけをruntime-awareに変更 | exit 1→0、中央テスト0維持、status hash不変 | `improvements/IMP-001-frozen-tool-selftest.md` |
| 015 | IMP-002 | 成果物・証跡・承認証跡のSHA-256封印とGate再照合だけを追加 | 同じ証跡差し替えがPASS/0→FAIL/2、正常MIG-00/10はPASS | `improvements/IMP-002-gate-content-seal.md` |
| 016 | IMP-003 | 受入後変更の正規手順だけを追加 | 変更検出後に通常STEPを停止し、再検査→再受入→全role再承認→置換Gate→元STEP復帰を完走 | `improvements/IMP-003-post-accept-change-workflow.md` |
| 017 | IMP-004 | blocker・例外操作だけをコマンド化 | カタログ検索→登録→停止→安全作業許可→hash付き解消→元STEP復帰を完走。non-blockerも同じ入口で記録 | `improvements/IMP-004-exception-commands.md` |
| 018 | IMP-005 | 技術判断の期限と成果物だけをMIG-30/40/80へ再配置 | MIG-00の8判断を撤去し、期限前記録を拒否、期限Gateで未決定を拒否。旧profileはacceptedのまま期限別成果物へ移行 | `improvements/IMP-005-decision-milestones.md` |
| 019 | IMP-006 | fixtureとUI証跡の検査幅だけを拡大 | fixture/UI実体欠落がPASS/0からFAIL/2へ変化。SQLite実測、画像実形式/寸法、観測ID/状態/semantic evidence/claim対応をmanifestから再検査し、MIG-10を3roleで再受入 | `improvements/IMP-006-fixture-ui-evidence-width.md` |
| 020 | TF-001 primary | 会話履歴なしworkerへpacketと隔離MIG-10案件だけを渡す | 介入0、約7分18秒で2manifest作成、2artifact受入、3role承認、MIG-10 PASS、handoff作成 | `transfer-tests/TF-001/worker-log.md`、`transfer-tests/TF-001/report.md` |
| 021 | TF-001 handoff | 別fresh workerへhandoffだけを渡して現在位置を復元 | milestone/STEP、blocker、nextは正答。future artifact 10件をcurrent Unacceptedと誤認したためtransfer test全体はFAIL | INT-009、`transfer-tests/TF-001/report.md` |
| 022 | IMP-007 | handoffのcurrent/future scopeとGate再開・保存境界だけを変更 | current unaccepted/missing approvals、due付きfuture節、read-only Gate評価、check→advanceを固定。中央selftest PASS | `improvements/IMP-007-handoff-state-scope.md` |
| 023 | TF-002 handoff | TF-001と同じMIG-10 Gate状態を別fresh workerへhandoffだけで再移管 | 9問全正答、介入0、check exit 0、ファイル変更0、advance未実行でPASS | `transfer-tests/TF-002/report.md` |
| 024 | IMP-008 | 実証フィードバック反映版PDFだけを再生成 | Version 1.2、A4 35ページ、outline 34、全ページ画像化・目視PASS。検査中にコードブロック改ページとフッター欠けを検出して生成処理を修正 | `improvements/IMP-008-pdf-regeneration.md` |

先行観測は、環境不足の代替経路が成立するかを確認するために行った。MIG-00 Gate を飛び越えて accepted にはしない。
