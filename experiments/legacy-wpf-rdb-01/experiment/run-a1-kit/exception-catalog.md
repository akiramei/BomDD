# 異常時処置集 - legacy-wpf-rdb

問題が起きたら、最も近い ID の既定処置を実行する。原因を自由探索する前に、証跡と変更していない境界を保存する。

## 共通処置

1. 現在の STEP を変更しない。
2. stdout/stderr、スクリーンショット、DB 観測、時刻、対象版を保存する。
3. 本番 DB、基準 fixture、現行ソースを変更していないことを記録する。
4. `templates/exception-record.md` を複製する。
5. 下表の blocker/non-blocker と再開 STEP を適用する。

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
| EX-BASELINE-001 | 現行ソースをビルドできない | blocker | 修正しない。稼働バイナリを原版にするか修復後凍結か裁定 | STEP-012 |
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

## 切替・rollback

| ID | 症状 | 分類 | 既定処置 | 再開 |
|---|---|---|---|---|
| EX-CUTOVER-001 | リハーサルで口頭介入 | non-blocker | 介入を Runbook の STEP/例外へ還元し再リハーサル | STEP-085 |
| EX-CUTOVER-002 | backup を restore できない | blocker | 切替禁止。backup/restore 手順を修復 | STEP-083 |
| EX-CUTOVER-003 | 本番で未記載コマンドが必要 | blocker | 実行前に記録し Owner 裁定。可能なら rollback | STEP-093 |
| EX-CUTOVER-004 | smoke または DB 照合失敗 | blocker | 改善を試みず rollback trigger を適用 | STEP-095 |
| EX-ROLLBACK-001 | rollback 失敗 | blocker | 書込み停止を維持し、事前指定の disaster owner へ escalation | rollback STEP |

