# 第二実験の対象選定

選定日: 2026-07-19

## 選択

第一実験と同じ`traggo/server` v0.8.3をPostgreSQL配置で使う。

## 理由

第二実験の目的はclient-server RDBで手引きとGateが作業を止めずに機能するかの測定である。製品まで変更すると、業務機能、UI、実装言語、規模、RDB方式が同時に変わり、どの差が介入を生んだか分からなくなる。同一commitのTraggoは`postgres` dialectを原版に含むため、SQLiteだけをPostgreSQLへ置換して次を単独で測れる。

- ファイルコピーではなくdump/restoreを使うfixture。
- host、port、database、role、credentialを持つ接続境界。
- production DBではなくrestore-control DBへ接続するlive Gate検査。
- read-only validator role。
- PostgreSQLのschema、constraint、index、canonical query検査。

## 採用しなかった経路

| 経路 | 判断 |
|---|---|
| 別OSS + PostgreSQL | 製品差とRDB差が混ざるため延期 |
| Traggo + MySQL | PostgreSQLと同じ目的を持つため、先に一系統だけ実証 |
| Podman container | Windows側に稼働Podman machine/WSL distributionがなく、環境構築差が増える |
| SQL Server LocalDB | Traggo原版がdialectを持たず、client-server運用境界の検査にも不足 |

