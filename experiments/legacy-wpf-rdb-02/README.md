# Traggo Web + PostgreSQL → C#/.NET/WPF 移行実証実験

このディレクトリは、`legacy-wpf-rdb`手引きVersion 1.2をclient-server RDBへ適用する第二実験の記録である。第一実験と同じTraggo、同じcommit、同じ対象機能を使い、SQLiteからPostgreSQLへ変わる影響だけを測る。

## 作業者の入口

1. [実験プロトコル](experiment/experiment-protocol.md)を読む。
2. 案件初期化後は`bomdd/migration/guide/onboarding.md`を読む。
3. `migration-workflow.py status`と`next`が示す一つのActionだけを行う。
4. 手引きだけで続行できない場合は、解決前に[介入ログ](experiment/intervention-log.md)へ記録する。

## 固定対象

- 原版: `traggo/server`
- 固定版: `v0.8.3` / `6321119c3c2d55f04e2e4967f6492aabd6067b76`
- RDB: PostgreSQL 16.14、Windows x86-64 portable binaries
- 接続境界: `127.0.0.1:55432`
- 移行先想定: C# / .NET 10 / WPF / Windows x64

取得物、DB実行データ、資格情報は`runtime/`に隔離し、Git管理しない。版、URL、hashは[source-lock.json](experiment/source-lock.json)へ記録する。

実験結果は[experiment-result.md](experiment/experiment-result.md)、一件だけ行った方法改善は[IMP-009](experiment/IMP-009-postgresql-fixture-gate.md)を正本とする。
