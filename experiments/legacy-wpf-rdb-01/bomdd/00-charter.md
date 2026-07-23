# Charter — Traggo WPF Migration Experiment

状態: MIG-00 review ready  
固定日: 2026-07-19

## 移行目的

Web ベースの Traggo v0.8.3 を C#/.NET 10 + WPF の Windows desktop application として再実装し、既存 SQLite schema と既存データを継続利用できることを実証する。同時に、`legacy-wpf-rdb` 手引きが作業者を迷わせず進行させるかを観測し、介入を手引きへ還元する。

## 原版

- Repository: `https://github.com/traggo/server.git`
- Tag: `v0.8.3`
- Commit: `6321119c3c2d55f04e2e4967f6492aabd6067b76`
- License: GPL-3.0
- Source lock: `experiment/source-lock.json`

## スコープ

含む:

- SQLite deployment の login、user、tag、device、time span、list、calendar、dashboard、statistics、settings
- 既存 DB の読取り、更新、再読取り、参照整合性
- WPF packaging、隔離環境での cutover/rollback rehearsal
- 手引きの介入記録、改善、transfer test

含まない:

- MySQL/PostgreSQL deployment
- HTTP/GraphQL API の後方互換提供
- browser 固有の responsive/PWA 挙動
- schema 変更、新機能、無関係な refactoring
- 実利用者の本番切替。本実証では fixture の模擬切替を行う

## 固定制約

- DB engine と schema を変えない。
- 移行先から schema migration を実行しない。
- 基準 fixture を直接更新しない。毎回作業コピーを使う。
- 新旧の同時書込みと dual write を行わない。
- 現在 STEP 以外を accepted にしない。
- GPL-3.0 の配布条件を package と Service BOM で検査する。

## 工場構成

- ティア: 最小 1 工場。ただし手引き改訂後に fresh worker の transfer test を別 run として行う
- 作業実行: Experiment Operator (Codex)
- 収束ループ予算: 手引き改訂 3 回。最短化の予算ではない

## 役割と判定者

- Migration / Specification / DB / WPF / UI / Acceptance Owner: Experiment Operator (Codex)
- Migration Worker: Experiment Operator (Codex)
- 完了判定者: Experiment Operator。最終結果を Experiment Sponsor (user) へ提示する
- Go/No-Go 判定者: Experiment Operator。実案件での本番 Go 権限を意味しない
- 単一担当者の自己承認は実験上の制約であり、実案件へ一般化しない

## 参加供給

- 対象リポジトリ: `original/traggo-server`、上記 commit
- コマンド実行ディレクトリ: `C:\Users\akira\source\repos\BomDD`
- 現行 golden: 同一 commit の公式 Windows asset と `fixtures/baseline/traggo.db`
- 作業環境: Codex desktop、.NET 10 SDK、Node.js、SQLite CLI。Go/Docker は初期環境にない
- 作業入口: `experiments/legacy-wpf-rdb-01/README.md`

## 完了の定義

- MIG-00 から MIG-100 の模擬運用移管まで Gate 証跡がある。
- 固定オラクルの未観測差分が 0、未裁定差分と blocker が 0。
- 既存 DB schema が不変で、canonical query、integrity、foreign key 検査が合格する。
- 対象機能が WPF で accepted になり、cutover/rollback を fixture で再演できる。
- 介入ログ全件に改善結果があり、fresh worker transfer test を実施する。
- 納品物は WPF 成果物、`bomdd/`、実験ログ、GPL-3.0 notice/source 条件を含む。

## 実装開始 Gate

| Gate | 判定 | 証跡 |
|---|---|---|
| G0 / MIG-00 | review ready | 本 Charter、profile、responsibility matrix |
| MIG-10～MIG-50 | 未実施 | 各 Gate result を正本とする |
| MIG-60 | 未実施 | walking skeleton と最小 DB/UI comparison |
| MIG-70～MIG-100 | 未実施 | 統合、模擬切替、移管 evidence |

## 未解決事項

MIG-00 の blocker はなし。現行版の実行前提不足と受入操作不足は製品判断ではなく手引き介入 `INT-001`、`INT-002` として記録済み。

