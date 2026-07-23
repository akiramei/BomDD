# Migration Charter — {{PRODUCT}}

状態: draft  
作成日: {{DATE}}

このファイルは `legacy-wpf-rdb` 専用である。山括弧の指示を案件値へ置き換え、該当しない項目は削除せず理由付き `not-applicable` とする。

## 移行目的

<既存システムを C#/.NET + WPF へ移行する目的と、成功後の利用状態を 1～3 行で記載>

## 現行システムの正本

- Repository / 保管場所: <値>
- Branch / tag / commit / build ID: <値>
- 稼働バイナリ ID と hash: <値>
- 現行 DB engine / 接続先区分: <値。本番秘密値は記載しない>
- License / 配布制約: <値>

## 規模と顧客影響

- Java source概算LOC: <値>
- repository / module / screen: <値>/<値>/<値>
- 稼働顧客 / active user: <値>/<値>
- 営業時間、繁忙時間、停止許容: <値>
- SLA/SLO、規制、監査、データ区分: <値>
- 現行version分布とoffline端末: <値>

## 対象

含む:

- <対象業務>
- <対象画面>
- <対象 DB と既存データ>

含まない:

- <対象外と理由>

## 固定制約

- 既存 RDB engine、既存データ、原則として既存 schema を継続利用する。
- 初期移行では schema を変更しない。必要時は別 ECO とする。
- 基準 fixture を直接更新せず、作業コピーを使う。
- 新旧を無設計で同時書込みさせず、書込み主体を一つにする。
- 移行と無関係な refactoring と新機能追加を行わない。
- Program担当者は現在のglobal STEP以外を開始しない。製造workerは`workstream-register.json`にあり、工具でclaimした一つのsliceだけを並行実行する。
- 顧客向け新機能、現行保守修正、移行変更を同じ変更票に混ぜない。
- 本番切替はcohort単位とし、全顧客一斉切替を既定にしない。

## 完了判定

- 完了判定者: <責任者表の割当名>
- 切替 Go/No-Go 判定者: <責任者表の割当名>
- 対象機能: accepted または承認済み差分
- DB: schema 不変、integrity、参照整合性、canonical query、backup/restore 合格
- UI: 表示・操作契約と固定オラクル合格
- 運用: cutover、rollback、smoke、handover の実演合格
- 残存条件: blocker 0、未裁定差分 0、証跡なし accepted 0
- Program: 全workstream/slice as-built、未所有interface 0、未裁定customer variant 0
- Release: clean端末install/upgrade/repair/uninstall、SBOM、署名、security、NFR合格
- Customer: representative UAT、training、support rehearsal、cohort signoff合格

## 参加供給

- 作業入口: `bomdd/migration/guide/onboarding.md`
- 対象リポジトリと固定版: <値>
- コマンド実行ディレクトリ: <絶対パス>
- 現行 golden の起動方法または提供者: <値>
- 匿名化 DB fixture の提供方法: <値>
- 開発環境の提供方法または責任者: <値>

## 未解決事項

| ID | Question | blocker/non-blocker | Owner | Target artifact | Status |
|---|---|---|---|---|---|
| UQ-001 | <なければ `none — reviewed by <owner>`> | <値> | <値> | <値> | <値> |
