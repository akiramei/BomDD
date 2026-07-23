# 実験プロトコル EXP-LWR-002

状態: 完了  
開始日: 2026-07-19  
開始時手引き: `legacy-wpf-rdb` Version 1.2  
改善後手引き: `legacy-wpf-rdb` Version 1.3

## 1. 仮説

同一製品のSQLite配置をPostgreSQL配置へ替えても、作業者は手引き、manifest template、Gate出力だけでclient-server RDBの基準線を作り、dump/restoreとlive read-only検査を完了できる。

## 2. 今回の評価対象

1. PostgreSQL基準線: 同一commitのTraggoをPostgreSQLで起動し、代表データをdump/restoreできるか。
2. 手引き: 作業者が接続・資格情報・restore-control・検査方法を設計せず、MIG-10 Gateまで進めるか。
3. Gate: dumpの存在/hashだけでなく、復元DBのschemaと代表値を毎回再検査できるか。

WPF製品の完成は第一実験の継続課題であり、この第二実験単独の合格主張に含めない。

## 3. 固定条件

- Traggo `v0.8.3`、commit `6321119c3c2d55f04e2e4967f6492aabd6067b76`。
- PostgreSQL 16.14 Windows x86-64 binaries、SHA-256をsource lockへ固定。
- serverは`127.0.0.1:55432`だけで待受け、実験終了時に停止する。
- production相当DB、restore-control DB、validator roleを分ける。
- パスワードは`runtime/`内の無視対象ファイルまたはプロセス環境だけに置き、成果物へ記録しない。
- Gateはproduction相当DBへ接続せず、restore-control DBをread-only roleで検査する。
- 自動migrationは原版Traggoによる初回schema生成だけに限定し、移行先WPFからは実行しない。
- 第一実験と同じ一人operator条件を使う。実案件での自己承認を推奨しない。

## 4. 観測指標

| ID | 指標 | 合格方向 |
|---|---|---|
| MET-01 | `status`/`next`のAction数 | 常に1 |
| MET-02 | 手引き外介入 | 0へ近づく |
| MET-03 | Gate false-pass/false-fail | 0 |
| MET-04 | dump bytes/hash | 毎回一致 |
| MET-05 | restore | 空DBへ成功 |
| MET-06 | schema/constraint/index | 期待値と一致 |
| MET-07 | canonical query | すべて一致 |
| MET-08 | credential非記録 | 成果物内に秘密値0 |
| MET-09 | production非変更 | Gate前後で代表値不変 |

## 5. 実験順序

1. 現行Version 1.2を変更せず案件を初期化する。
2. PostgreSQLと原版Traggoを起動し、基準データを作る。
3. dumpを空のrestore-control DBへ復元する。
4. 現行templateにclient-server事実を記録し、最初に止まる箇所を介入ログへ残す。
5. その一件だけをtemplate、tool、runbookへ還元する。
6. 正常manifest、dump欠落、DB値差替え、write可能roleの負例を測る。
7. MIG-00〜MIG-10を受入し、handoffと実験結果を保存する。

## 6. 完了条件

- PostgreSQL dump、schema、restore log、canonical query結果が証跡化される。
- MIG-10 Gateがrestore-control DBをlive検査してPASSする。
- dump欠落、restore DB差分、資格情報不足、write可能接続のいずれかをGateがFAILにする。
- production相当DBをGateが変更しない。
- 介入と改善が一対一で記録される。
- 中央/凍結selftestと第一実験のMIG-00/10に退行がない。
