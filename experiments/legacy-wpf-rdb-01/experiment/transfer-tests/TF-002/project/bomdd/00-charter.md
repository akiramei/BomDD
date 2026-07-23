# Migration Charter — TransferFixture

状態: accepted test fixture  
作成日: 2026-07-19

このファイルは `legacy-wpf-rdb` 専用である。山括弧の指示を案件値へ置き換え、該当しない項目は削除せず理由付き `not-applicable` とする。

## 移行目的

Traggoの凍結証跡を用いたtransfer testで、既存SQLiteと現行UI観測を迷わずMIG-10へ受入できることを確認する。

## 現行システムの正本

- Repository / 保管場所: Traggo transfer fixture
- Branch / tag / commit / build ID: v0.8.3 / 6321119c
- 稼働バイナリ ID と hash: frozen in current-baseline.md
- 現行 DB engine / 接続先区分: SQLite synthetic fixture
- License / 配布制約: GPL-3.0; experiment only

## 対象

含む:

- login、timer、list、calendarの代表観測
- ListとCalendar
- synthetic SQLite fixture

含まない:

- WPF実装とMIG-20以後。今回の試験範囲外。

## 固定制約

- 既存 RDB engine、既存データ、原則として既存 schema を継続利用する。
- 初期移行では schema を変更しない。必要時は別 ECO とする。
- 基準 fixture を直接更新せず、作業コピーを使う。
- 新旧を無設計で同時書込みさせず、書込み主体を一つにする。
- 移行と無関係な refactoring と新機能追加を行わない。
- 現在 STEP 以外を同時に開始しない。

## 完了判定

- 完了判定者: TF-001 Assigned Team
- 切替 Go/No-Go 判定者: TF-001 Assigned Team
- 対象機能: accepted または承認済み差分
- DB: schema 不変、integrity、参照整合性、canonical query、backup/restore 合格
- UI: 表示・操作契約と固定オラクル合格
- 運用: cutover、rollback、smoke、handover の実演合格
- 残存条件: blocker 0、未裁定差分 0、証跡なし accepted 0

## 参加供給

- 作業入口: `bomdd/migration/guide/onboarding.md`
- 対象リポジトリと固定版: TF-001 isolated project / Traggo v0.8.3 evidence
- コマンド実行ディレクトリ: packet.mdのProject root
- 現行 golden の起動方法または提供者: 保存済みUI証跡を使用
- 匿名化 DB fixture の提供方法: project/fixtures/baseline/traggo.db
- 開発環境の提供方法または責任者: TF-001 Assigned Team

## 未解決事項

| ID | Question | blocker/non-blocker | Owner | Target artifact | Status |
|---|---|---|---|---|---|
| UQ-001 | none — reviewed by TF-001 Assigned Team | non-blocker | TF-001 Assigned Team | this charter | closed |
