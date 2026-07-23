# Migration Charter — Traggo PostgreSQL Second Experiment

状態: MIG-00 review ready  
固定日: 2026-07-19

## 移行目的

Web版Traggo v0.8.3をC#/.NET 10 + WPFへ移す想定で、既存PostgreSQL schemaとデータを継続利用する基準線を作る。第二実験ではMIG-10までを再演し、client-server RDBのdump/restore、資格情報、read-only live検査を作業者が迷わず完了できるかを測る。

## 現行システムの正本

- Repository: `https://github.com/traggo/server.git`
- Tag / commit: `v0.8.3` / `6321119c3c2d55f04e2e4967f6492aabd6067b76`
- 稼働バイナリ: 公式Windows asset。SHA-256は`experiment/source-lock.json`
- DB engine / 接続先区分: PostgreSQL 16.14 / 隔離実験server。本番秘密値は記録しない
- License: GPL-3.0

## 対象

含む:

- login、tag、time span、list、calendarの代表観測
- PostgreSQL schemaと代表データ
- dump、空DBへのrestore、read-only roleによるlive検査
- MIG-00〜MIG-10の手引き・Gate実証

含まない:

- WPF製品完成。第一実験のMIG-20以後で扱う
- MySQL、SQLite、SQL Serverの同時比較
- schema変更、新機能、無関係なrefactoring
- 実利用者の本番DBまたは外部network DB

## 固定制約

- engineとschemaを変更しない。
- 移行先からschema migrationを実行しない。
- 原版Traggoのschema生成は隔離した初回DBだけで許可する。
- Gateはproduction相当DBへ接続せず、dumpから復元したrestore-control DBを使う。
- validator roleはread-onlyとし、資格情報を成果物へ記録しない。
- 新旧同時書込みとdual writeを行わない。
- 現在STEP以外を同時に開始しない。

## 完了判定

- 完了判定者: Experiment Operator (Codex)
- 模擬Go/No-Go判定者: Experiment Operator (Codex)
- DB: dump hash、restore、schema、constraint、index、canonical queryが合格
- 安全: production相当DB非変更、blocker 0、秘密値記録0
- 手引き: 介入と改善が一対一で記録される

## 参加供給

- 作業入口: `bomdd/migration/guide/onboarding.md`
- 対象原版: `original/traggo-server`と`original/release-v0.8.3`
- コマンド実行ディレクトリ: `C:\Users\akira\source\repos\BomDD`
- 現行golden: 公式Windows asset + PostgreSQL隔離server
- fixture: `pg_dump`を`fixtures/baseline/`へ保存し、別DBへrestore
- PostgreSQL binaries/data/secret: Git無視対象`runtime/`

## 未解決事項

| ID | Question | blocker/non-blocker | Owner | Target artifact | Status |
|---|---|---|---|---|---|
| UQ-001 | 現行SQLite専用manifest/GateがPostgreSQLを案内・検査できるか | blocker at MIG-10 | DB Custodian | ART-DB-BASELINE | open until measured |

