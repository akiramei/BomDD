# 実験プロトコル EXP-LWR-001

状態: 実行中  
開始日: 2026-07-19  
対象手引き: `legacy-wpf-rdb` initial operational release

## 1. 仮説

案件固有の判断を開始時の決定と成果物 Gate に移せば、作業者は最短経路を考えなくても、現在位置と次の一作業を特定し、Web OSS を C#/.NET + WPF へ移行できる。

## 2. 二つの評価対象

1. 製品: 固定した Traggo の対象範囲が、既存 SQLite schema とデータを保った WPF アプリとして受入できるか。
2. 手引き: 作業者が口頭説明や自由探索なしで、成果物 Gate を一段ずつ通過できるか。

製品が完成しても、未記録の介入に依存した場合は手引きの実証成功とはしない。

## 3. 固定条件

- 原版は `v0.8.3` と同一の commit `6321119c3c2d55f04e2e4967f6492aabd6067b76`。
- SQLite 配置を対象とし、MySQL/PostgreSQL 対応は初回実証の対象外。
- DB engine と既存 schema を変更しない。自動 migration を移行先から実行しない。
- 基準 DB を直接更新せず、試験ごとにコピーする。
- Web/GraphQL transport は WPF の in-process application boundary に置き換える。
- 実験中の役割は単一の Experiment Operator に集約する。実案件での自己承認を推奨するものではない。
- GPL-3.0 の著作権表示、ライセンス本文、対応するソース提供条件を配布成果物に維持する。

## 4. 対象機能

含む:

- ログインとユーザー管理
- タグ定義
- time span の開始、停止、作成、編集、削除
- 一覧とカレンダー
- dashboard、range、集計
- user settings と device token 管理
- 既存 SQLite の読取り、更新、参照整合性

含まない:

- MySQL/PostgreSQL deployment
- HTTP/GraphQL API の後方互換提供
- Web browser 固有の responsive/PWA 挙動
- Linux/Docker server deployment
- 新機能追加と schema 改変

## 5. 観測指標

| ID | 指標 | 記録方法 | 合格方向 |
|---|---|---|---|
| MET-01 | Action 一意性 | `status`/`next` 後に候補作業数を記録 | 常に 1 |
| MET-02 | 介入件数 | 介入ログを分類別集計 | 改訂ごとに減少 |
| MET-03 | 自由探索 | 手引き外のファイル・Web検索をした理由を記録 | 0 に近づく |
| MET-04 | 手戻り | accepted 後に成果物を戻した回数 | 0 |
| MET-05 | Gate 誤判定 | false-pass / false-fail を記録 | 0 |
| MET-06 | DB 保全 | schema、integrity、foreign key、canonical query | 全合格 |
| MET-07 | 機能差分 | 固定オラクルと差分台帳 | 未裁定 0 |
| MET-08 | 再開可能性 | handoff だけで再開できるか | 再質問 0 |

時間と費用は記録しても最適化対象にしない。

## 6. 実験の段階

1. Run A1: initial operational release を MIG-00 から MIG-10 まで適用し、入口・基準線・状態操作の介入を記録する。
2. 改訂 A: 作業継続を妨げたナビゲーション、受入、例外、Charter を直ちに工具と資料へ還元する。
3. Run A2: 改訂 A を MIG-20 から MIG-60 まで適用し、同じ問題の再発と新しい介入を記録する。
4. 改訂 B: MIG-60 までのフィードバックを還元する。
5. Run B: 改訂版で MIG-70 から MIG-100 まで進める。
6. Transfer test: fresh な担当者が MIG-00 から MIG-60 を再演する。

TF-001は完全再演前の限定preflightとして、IMP-006反映後のMIG-10 / STEP-013からGateとhandoff交代までを検査する。TF-001のPASSだけで上記6を完了扱いにしない。完全再演は製品実験がMIG-60へ到達した後に行う。

Run A1 の凍結資料は `experiment/run-a1-kit/` に保存する。途中改訂を許すのは、目的が同じ障害を後続全工程で反復することではなく、介入を減らした経路を続けて検証することだからである。

同種の工具介入が独立した三回で再現するまでは、専用スキルを作らない。

## 7. 完了条件

- MIG-00 から MIG-100 まで Gate 証跡が残る。
- 対象機能が accepted または理由付きの裁定済み差分になる。
- 基準 fixture を WPF で開き、同じ schema のまま read/write/再読取りが合格する。
- cutover と rollback を隔離環境で再演できる。
- 介入ログの全件に、採用・延期・棄却の改善結果が付く。
- fresh worker の transfer test 結果が残る。
