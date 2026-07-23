# 異常時処置集 - legacy-wpf-rdb

問題が起きたら、最も近い ID の既定処置を実行する。原因を自由探索する前に、証跡と変更していない境界を保存する。

## 共通処置

1. 現在の STEP を変更しない。
2. stdout/stderr、スクリーンショット、DB 観測、時刻、対象版を保存する。
3. 本番 DB、基準 fixture、現行ソースを変更していないことを記録する。
4. `exception-catalog --query <症状の語>`で候補を表示し、最も近いIDを確認する。
5. `exception-open`を実行する。工具が例外票を生成し、blocker/non-blocker/defect、owner、既定処置、再開情報をstatusへ登録する。
6. blocker中は`next`に表示された既定処置だけを行う。別作業は責任者が`exception-safe-work`で明示許可したものに限る。
7. 解消証跡を作り、`exception-resolve`を実行する。status JSONを手編集してblockerを消さない。

## 初期化・状態

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-INIT-001 | `bomdd/migration` が既に存在 | blocker | 上書きしない。既存 profile/status の scenario と owner を監査 | STEP-001 |
| EX-INIT-002 | Git 管理外 | blocker | 対象版を固定できる管理方法を Migration Owner が裁定 | STEP-001 |
| EX-STATE-001 | status と成果物が矛盾 | blocker | 成果物を正として read-only 監査し、status 修復票を作る | 現在 STEP |
| EX-STATE-002 | 次 STEP が空欄 | non-blocker | milestone definition の entry/次順を暫定採用 | 現在 STEP |
| EX-DOC-001 | 手順書と milestone definition が矛盾 | blocker | 案件で凍結した milestone definition を優先し ECO 候補化 | 現在 STEP |

## 現行基準線

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-BASELINE-001 | 現行ソースをビルドできない、または必須 toolchain がない | blocker | source/DBを変更しない。同一 commit/tag の公式配布物を URL・hash・version表示・起動結果で照合し、原版採用を Owner が裁定。同一性不明なら toolchain 供給または修復後凍結を依頼 | STEP-012 |
| EX-BASELINE-002 | 現行動作が環境ごとに違う | blocker | 環境差を K-BOM 候補化し、正とする環境を裁定 | STEP-014 |
| EX-BASELINE-003 | 正とする仕様が複数ある | blocker | source map を作り、Specification Owner が優先順位を裁定 | STEP-021 |

## DB

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-DB-001 | 棚卸し接続不可 | blocker | 接続先を変えず DB Custodian へ権限/経路を依頼 | STEP-013 |
| EX-DB-002 | object 参照権限不足 | blocker | 権限を推測せず read-only 棚卸し権限を依頼 | STEP-013 |
| EX-DB-003 | 用途不明 object | non-blocker | `unknown` として残し、削除/変更しない | STEP-024 |
| EX-DB-004 | 新旧 query 結果が違う | blocker | 入力、順序、NULL、日時、collation、transaction を別々に比較 | STEP-034 |
| EX-DB-005 | 読取り試験で DB が変化 | blocker | 接続停止、作業コピー破棄、基準 fixture から再複製 | STEP-053 |
| EX-DB-006 | transaction 途中の部分更新 | blocker | 製造 miss として当該 slice へ戻す。本番使用禁止 | STEP-073 |
| EX-DB-007 | deadlock/timeout | blocker | retry で隠さず graph、timeout、transaction 範囲を証跡化 | STEP-073 |
| EX-DB-008 | 現行と新系が同時書込み | blocker | 両方の書込みを停止し、DB Custodian が正本 writer を裁定 | STEP-084 |
| EX-DB-009 | schema 変更が必要 | blocker | 本移行から分離し ECO + migration oracle を起票 | MIG-30 |

## WPF/UI

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-WPF-001 | UI が固まる | blocker | UI thread の同期 I/O と長時間処理を計測し当該 slice へ戻す | STEP-072 |
| EX-WPF-002 | binding error | blocker | binding trace を保存し、表示契約と ViewModel property を突合 | STEP-072 |
| EX-WPF-003 | close/cancel 中に例外 | blocker | cancellation と lifetime を Control Plan に追加 | STEP-072 |
| EX-WPF-004 | DPI/resize で要素欠落 | blocker | screenshot と display contract を比較し UI slice へ戻す | STEP-072 |
| EX-WPF-005 | 現行と見た目が違う | non-blocker または blocker | 必須要素/意味/状態か装飾差かを UI Approver が裁定 | STEP-064 |
| EX-WPF-006 | 大量データで遅い | blocker | 件数、query 時間、materialize、render を分離計測 | STEP-072 |

## Java/JavaFX・実現性

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-JAVA-001 | JDK/JavaFX/build pluginを再現できない | blocker | version、repository、wrapper、native依存、配布物hashを保存しJava Technical Ownerへ供給を依頼 | STEP-012 |
| EX-JAVA-002 | reflection/proxy/annotation/serializationの意味がC#へ一意に写らない | blocker | 代表入力と現行出力を固定しsemantic contractを裁定 | STEP-036 |
| EX-JAVA-003 | JavaFX thread/binding/window lifecycleをWPFで再現できない | blocker | 最難関UIの実証へ戻りfallbackを比較 | STEP-016 |
| EX-FEAS-001 | 七risk classの一つがfailまたは未実証 | blocker | 全数設計を止め、限定実証、fallback、accepted-risk権限を裁定 | STEP-016 |
| EX-FEAS-002 | third-party代替のlicense/security/supportが不明 | blocker | 採用せずdependency ledgerとsecurity reviewを完成 | STEP-016 |

## 規模・workstream

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-SCALE-001 | code/module/customer variantに未分類・未割当がある | blocker | 集計ruleを保存し、ownerと一sliceへ割当。件数をゼロへ手修正しない | STEP-026 |
| EX-SCALE-002 | sliceがprofile上限を超える | blocker | end-to-end acceptanceを保ったままslice分割しregisterを再受入 | STEP-026 |
| EX-WS-001 | workstream依存が循環する | blocker | interface producer/consumerと統合順を再分割 | STEP-047 |
| EX-WS-002 | 同じsliceを複数workerが変更した | blocker | 両作業を停止しclaim/evidence/commitを保存、leadが正しいclaimを裁定 | 現在slice |
| EX-WS-003 | workerが離脱しclaimが残った | non-blocker | leadまたはclaimantが`slice-release`を証跡付きで実行 | 現在slice |
| EX-WS-004 | interface契約またはhashが変更された | blocker | producerと全consumerを受入後変更の対象にしcontract testを再実行 | STEP-047 |
| EX-WS-005 | claimantしかreviewerがいない | blocker | 独立reviewer/delegateを割当。自己受入で先へ進めない | 現在slice |

## 仕様・差分

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-SPEC-001 | 現行動作が担当者の期待と違う | blocker | preserve/change-approved/legacy-defect を裁定 | STEP-032 |
| EX-SPEC-002 | 期待値が資料にない | blocker | 観測を証拠化し Specification Owner が暫定契約を裁定 | STEP-032 |
| EX-SPEC-003 | 既存不具合の疑い | defect | 移行内で修正せず CAPA/ECO 候補化 | STEP-032 |
| EX-DIFF-001 | 差分を分類できない | blocker | spec/bom/oracle/manufacturing/legacy/harness の順に戻り先を調査 | STEP-065 |

## 検査・Gate

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-ORACLE-001 | 変異個体を落とせない | blocker | オラクルを修復し再較正。製造を開始しない | STEP-054 |
| EX-ORACLE-002 | 正常個体を落とす | blocker | equality/normalization/tolerance と fixture を監査 | STEP-054 |
| EX-GATE-001 | ファイルはあるが証跡なし | blocker | status を `accepted` にせず証跡を作る | 現在 STEP |
| EX-GATE-002 | 人間承認者不在 | blocker | 代理承認せず責任者表に従い割当を依頼 | 現在 STEP |
| EX-GATE-003 | JSONは存在するがplaceholder、zero sample、open resultが残る | blocker | content validationの最初のFAILを一件だけ直し、参照証跡を`--evidence`へ含める | 現在 STEP |
| EX-GATE-004 | accepted JSON内の参照証跡だけが変更された | blocker | 受入後変更を開き、参照元成果物と証跡をまとめて再検査・再承認 | 現在 STEP |

## Security・Release・顧客受入

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-SEC-001 | credential/secret/certificateが成果物やlogへ露出 | blocker | 配布・試験を停止し漏えい処置、secret rotation、証跡redactionと再検査をSecurity Ownerが裁定 | 現在 STEP |
| EX-SEC-002 | vulnerability/権限/監査差分が受入閾値を超える | blocker | 同一RCを隔離しsecurity contractへ戻る | STEP-078 |
| EX-RC-001 | UAT/運用/security中にRCを再buildした | blocker | 新RC hashとしてMIG-70の回帰とMIG-75全受入をやり直す | MIG-70 |
| EX-RC-002 | install/upgradeだけ別artifactで試験した | blocker | signed/promotion chainを破棄せず、同一RC artifactで試験を再実行 | STEP-077 |
| EX-REL-001 | 署名またはSBOM hash検証失敗 | blocker | releaseを配布せず、sign/build provenanceをRelease Ownerが調査 | STEP-085 |
| EX-UAT-001 | 顧客variantがUAT scopeから漏れた | blocker | customer matrixへ戻り代表または全数UATを追加 | STEP-076 |
| EX-COHORT-001 | 観測窓内にrollback閾値へ到達 | blocker | 次cohortを開始せず当該cohortのRollback Runbookを実行 | STEP-095 |
| EX-COHORT-002 | 顧客を理由・期限・ownerなしでdeferした | blocker | cohortを未完了へ戻し顧客合意と期限を記録 | STEP-095 |
| EX-OPS-001 | support/monitoring担当がRunbookを再演できない | blocker | 口頭補助を記録しRunbookへ還元、別担当で再演 | STEP-077 |

## 切替・rollback

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-CUTOVER-001 | リハーサルで口頭介入 | non-blocker | 介入を Runbook の STEP/例外へ還元し再リハーサル | STEP-085 |
| EX-CUTOVER-002 | backup を restore できない | blocker | 切替禁止。backup/restore 手順を修復 | STEP-083 |
| EX-CUTOVER-003 | 本番で未記載コマンドが必要 | blocker | 実行前に記録し Owner 裁定。可能なら rollback | STEP-093 |
| EX-CUTOVER-004 | smoke または DB 照合失敗 | blocker | 改善を試みず rollback trigger を適用 | STEP-095 |
| EX-ROLLBACK-001 | rollback 失敗 | blocker | 書込み停止を維持し、事前指定の disaster owner へ escalation | rollback STEP |
