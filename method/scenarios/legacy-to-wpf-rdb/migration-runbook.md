# 実運用 Java/JavaFX システムから C#/.NET + WPF への BomDD 標準移行作業手順書

対象シナリオ: 顧客が実運用する大規模 Java/JavaFX システムを、既存 RDB を継続利用して再実装  
シナリオ ID: `legacy-wpf-rdb`  
版: 2.0  
状態: enterprise release candidate

---

## はじめに - 初参加者の入口

初めて本移行へ参加する人は、先に [移行オンボーディング](onboarding.md) を実行する。

オンボーディングで行うこと:

1. 安全カードを読む。
2. `migration-status.json` の有無を確認する。
3. `status` と `next` で現在位置と今回の Action を一つに決める。
4. 自分の role と裁定先を確認する。
5. 現在 STEP の成果物と証跡保存先を開く。

30分以内に Action が一つに決まらない場合は作業を開始せず、`EX-STATE-001` または `EX-STATE-002` を使う。

## 0. この手順書の約束

この手順書は、最小コストや最短期間を狙うものではない。多少遠回りでも、作業者が現在位置、次の作業、完了条件、失敗時の戻り先を成果物から判断し、手を動かし続けられることを優先する。

想定規模は、数十万行、複数repository/module、複数チーム、複数顧客・利用拠点である。小規模PoCの成功を本番移行の成功とはみなさない。Program Gate、workstream、slice、顧客cohortの四階層を別々に管理する。

最上位規則:

> 最短経路を探さない。指定された標準経路を、成果物が受入されるまで一段ずつ進む。

この手順書では以下を意図的に受け入れる。

- 全件棚卸しを行う。
- 同じ性質を異なる検査で重複確認する。
- 実装前に仕様、BOM、検査を作る。
- 一機能ずつ閉じ、まとめ実装を避ける。
- 新旧比較と切替リハーサルを繰り返す。
- 不明点を推測で最適化しない。
- 移行とリファクタリングを分離する。

### 0.1 完了の言い方

「完全移行」ではなく、次のように表現する。

> 定義済み Control Plan、固定オラクル、DB 保全検査、UI 承認および切替後観測の範囲で blocker 差分がなく、未観測差分ゼロである。

### 0.2 この手順書を使わない場合

次に一つでも該当する場合、本手順書を開始せず、通常の新規開発または別シナリオを使う。

- 原版となる既存システムがない。
- 移行先が WPF ではない。
- 既存 RDB を継続利用しない。
- DB エンジン移行が主目的である。
- 既存データを破棄できる。

---

## 1. 作業者が毎回見る場所

対象プロジェクトの次のファイルを、作業開始時に必ず開く。

```text
bomdd/migration/migration-status.json
```

現在位置は次で決まる。

```text
現在位置 = 最後に通過したマイルストーン + 現在の STEP + 最初の未受入成果物
```

時間、消化工数、実装済み画面数、主観的な進捗率は、マイルストーン通過の根拠にしない。

### 1.1 毎日の開始手順

1. Program ManagerまたはMIG-50以前の担当者は`migration-workflow.py status`、MIG-50以後の実装担当者は`workstream-status --workstream <WS-ID>`を実行する。
2. `Scenario` が `legacy-wpf-rdb` であることを確認する。
3. `Last passed` と `Current` を読む。
4. `Blockers` を確認する。
5. Program作業はblockerがなければ`next`を実行する。実装担当者は自分がclaimしたsliceだけを開く。
6. Program作業は表示されたSTEPだけ、実装担当者は現在slice stateの次の一状態だけを開始する。
7. Program作業は`complete-step`、slice作業は`slice-transition`へ証跡を渡す。
8. `status`または`workstream-status`で一段だけ進んだことを確認する。
9. 別 STEP を「ついでに」開始しない。

### 1.2 毎日の終了手順

1. 作成・更新した成果物を保存する。
2. 検査ログを `bomdd/migration/evidence/` に保存する。
3. 完了した成果物ごとに `accept-artifact --artifact <ID> --evidence <証跡>` を実行する。
4. blocker と non-blocker を分類する。
5. 必須成果物の受入後、指定 role が `approve` を実行する。
6. `migration-status.json` を手編集しない。STEP と状態は上記コマンドで更新する。
7. `migration-workflow.py handoff` を実行する。
8. 引継票の`Current milestone unaccepted artifacts`を確認する。`Future artifacts`は現在Gateの不足ではない。
9. 引継票に再開コマンドがあることを確認して終了する。

現在STEPが`GATE-MIG-*`の場合、`next`とhandoffは対象milestoneを指定した`check`を再開コマンドとして示す。`check`はread-only評価でありGate結果ファイルを保存しない。PASS後の`advance`が同じGateを再検査し、結果を`gates/`へ保存して次milestoneへ進む。したがって、`check`だけ実行して中断したhandoffに現在Gateの結果ファイルが無いのは正常である。

### 1.3 状態語彙

成果物の状態は次だけを使う。

| 状態 | 意味 |
|---|---|
| `missing` | 必須成果物が存在しない |
| `present` | ファイルはあるが必須欄が未確認 |
| `complete` | 必須欄が埋まっている |
| `connected` | REQ/BOM/Control Plan/証跡へ接続済み |
| `verified` | 検査済み |
| `accepted` | 指定承認者が受入済み |
| `not-applicable` | 理由、裁定者、裁定証跡を記録して対象外 |

独自語彙、`almost-done`、`mostly-complete`、`conditional-green` は使わない。

---

## 2. 役割と判断の分離

作業者に案件固有の設計判断をさせない。判断は開始時に責任者へ割り当て、作業者は裁定結果を成果物へ転記する。

| 役割 | 決めること | 作業者が困ったときの出力 |
|---|---|---|
| Migration Owner | スコープ、予算、顧客影響、移行順、最終 Go/No-Go | blocker 決定票 |
| Program Manager | Program Gate、workstream依存、WIP、統合日程 | program status、依存調整票 |
| Specification Owner | 現行動作を維持・変更・既存不具合のどれにするか | 仕様裁定票 |
| Java Technical Owner | Java/JDK/JavaFX/build/言語意味論の現行解釈 | Java技術裁定票 |
| DB Custodian | DB 複製、権限、バックアップ、整合性、書込み主体 | DB 例外票 |
| WPF Technical Owner | .NET/WPF/DI/ログ/DB アクセス/target architecture | 技術決定票 |
| Integration Owner | 外部連携、workstream間interfaceとversion | interface裁定票 |
| UI Approver | 表示契約、操作、アクセシビリティ、golden | UI 承認記録 |
| Acceptance Owner | 固定オラクル、Control Plan、Gate 結果 | Gate 結果 |
| Security Owner | 認証、認可、秘密、署名、脆弱性受入 | security裁定票 |
| Release Owner | build、package、署名、install、update、promotion | release manifest |
| Operations Owner | 監視、運用、障害、backup/restore、hypercare | 運用受入記録 |
| Customer Acceptance Owner | 顧客UAT、業務停止、cohort受入 | 顧客受入記録 |
| Migration Worker | 指定 STEP の実行と証跡保存 | 成果物、例外票、引継票 |

責任者が未指定の項目は `MIG-00` の blocker である。作業者が代行して決めてはならない。

---

## 3. 進行モデル

### 3.1 全体マイルストーン

| ID | 到達状態 | 主な受入成果物 |
|---|---|---|
| `MIG-00` | Program開始可能 | 規模、顧客保護境界、RACI、Program統制 |
| `MIG-10` | 現行基準線確定 | Java/JavaFX/build/RDB/UI/NFR/security/operations基準線 |
| `MIG-15` | 技術実現性確認 | 最難関UI、DB R/W、連携、NFR、install、security、third-partyの実証 |
| `MIG-20` | 全数棚卸し・workstream分割完了 | code/機能/UI/DB/連携/test/依存/customer variant、workstream register |
| `MIG-30` | 互換契約確定 | Java/C#、JavaFX/WPF、DB、NFR、security、顧客受入契約 |
| `MIG-40` | Target/Factory設計完了 | target/interface/build/release/observability/securityとBomDD設計 |
| `MIG-50` | Migration factory準備完了 | slice、claim、contract test、test data、CI、oracle、Work Order |
| `MIG-60` | Pilot wave合格 | 全risk classを代表する複数sliceのclean installからAs-Built |
| `MIG-70` | 全workstream統合完了 | 全slice as-built、統合/NFR/security回帰、RC manifest |
| `MIG-75` | Release Candidate受入 | 同一RCによる顧客UAT、install/upgrade、運用、security、accessibility |
| `MIG-80` | 段階展開準備完了 | signed release、cohort/support、cutover/rollback、restore再演 |
| `MIG-90` | 本番段階展開完了 | cohort別Go/rollback、smoke、DB/telemetry/顧客照合 |
| `MIG-100` | 安定運用移管完了 | cohort別SLO、incident、Service BOM、運用実演、旧系処置 |

詳細な必須成果物と承認条件は `milestone-definition.json` を正本とする。

### 3.2 Gate の判定

成果物は次の四条件をすべて満たしたときだけ受入できる。

1. **Present**: 指定パスに存在する。
2. **Complete**: 必須欄が埋まり、未解決事項が分類されている。
3. **Connected**: 要求、BOM、検査、証跡へ接続されている。
4. **Verified**: 検査結果と承認者が記録されている。

Gate は Green/Yellow/Red の三状態だけを使う。

成果物と承認の記録は次の順で行う。工具は現在マイルストーン以外の成果物受入と、未受入成果物がある状態での承認を拒否する。

```powershell
python bomdd/migration/tools/migration-workflow.py accept-artifact `
  --project-root C:\path\to\TargetProject `
  --artifact ART-ID `
  --evidence bomdd/migration/evidence/review.md

python bomdd/migration/tools/migration-workflow.py approve `
  --project-root C:\path\to\TargetProject `
  --role "Migration Owner" `
  --approver "Assigned Name" `
  --evidence bomdd/migration/evidence/approval.md
```

`accept-artifact` は成果物本体と全証跡、`approve` は承認証跡の SHA-256 をstatusへ封印する。Gateは毎回現在のSHA-256を再計算する。ファイル名とパスが同じでも内容が変わればRedである。

MIG-10のDB基準線と現行UI観測は、索引文書の存在だけでは受入できない。次のmanifestを成果物の`--evidence`に必ず含める。Gateはsealされたmanifestから実体をたどり、毎回再検査する。

| 成果物 | 必須manifest | Gateが実体に対して再検査するもの |
|---|---|---|
| `ART-DB-BASELINE` | `evidence/baseline-fixture-manifest.json` | 共通: fixture/schema/観測のhashと代表SELECT。SQLite: restore copy/header/integrity/FK。PostgreSQL: custom dump catalog、read-only復元DB、version/constraint/index、live schema hash |
| `ART-CURRENT-OBS` | `evidence/current-ui-evidence-manifest.json` | 索引とのID一致、状態網羅、画像hash/実形式/拡張子/寸法、非画像証跡、主張と証跡ID |

manifestに新しいhashを書けば済むわけではない。manifest自身がaccepted evidenceとしてsealされるため、manifestまたは配下の実体を変えた場合も受入後変更の正規手順を使う。

Version 2.0のJSON成果物は、存在だけでは受入できない。profileの規模・全owner、NFRのsample、実現性risk class、未分類ゼロのcode inventory、循環のないworkstream/slice、NFR閾値、interface契約hash、CI全check、pilot risk class、全slice snapshot、RC全check、signed artifact/SBOM、全cohortの受入または正式deferを工具が内容検査する。JSONが参照する証跡は同じ`accept-artifact`の`--evidence`へ列挙しなければならない。

禁止:

- hash mismatchを解消するためだけに再受入・再封印する。
- 変更理由、再検査、承認を残さずacceptedファイルを更新する。
- 改変後の内容を過去の承認日で封印する。

hash導入前の受入済みmilestoneだけ、全内容の再レビュー後に次を一度実行する。

```powershell
python bomdd/migration/tools/migration-workflow.py seal-milestone `
  --project-root C:\path\to\TargetProject `
  --milestone MIG-00 `
  --reviewer "Assigned Name" `
  --review-evidence bomdd/migration/evidence/content-seal-review.md
```

通常作業では`seal-milestone`を使わない。

### 受入後変更の正規手順

受入済み成果物またはその証跡を変更する場合、直接の`accept-artifact`や`seal-milestone`では復旧しない。変更対象が過去milestoneでも、次の一本道を使う。工具は通常の現在位置を保存して一時停止し、完了後に同じSTEPへ戻す。

1. 変更理由を一文に固定する。変更をすでに検出した場合は、`check --milestone MIG-ID`の`[next]`に表示された最初の不一致ファイルを使う。
2. `change-open`を実行する。工具が影響する成果物をsealから逆引きし、変更票を`bomdd/migration/changes/`へ作り、旧承認と旧Gateをsupersededにする。共有証跡なら、それをsealしていた成果物をまとめて対象にする。
3. 対象を修正し、milestoneで要求される回帰・再検査を行う。結果を新しい証跡ファイルへ保存する。
4. `change-retest`で再検査証跡を封印する。
5. reviewerが変更内容と再検査結果を確認し、`change-accept`で影響成果物をまとめて再受入する。
6. `next`が示すroleごとに、新しい承認証跡で`change-approve`を実行する。旧承認証跡を再利用しない。
7. `change-close`を実行する。置換GateがPASSしたときだけ変更を閉じ、元の通常STEPへ戻る。FAILなら変更を開いたまま`next`へ戻る。

開始コマンド:

```powershell
python bomdd/migration/tools/migration-workflow.py change-open `
  --project-root C:\path\to\TargetProject `
  --milestone MIG-10 `
  --changed-file bomdd/migration/current-baseline.md `
  --reason "原版の識別情報を訂正する"
```

開始後は、コマンドを暗記せず毎回これを実行する。

```powershell
python bomdd/migration/tools/migration-workflow.py next --project-root C:\path\to\TargetProject
```

状態遷移と必要入力は次のとおりである。

| 状態 | `next`が指示するコマンド | 必須入力 | 完了条件 |
|---|---|---|---|
| `opened` | `change-retest` | 新しい回帰・再検査証跡 | 証跡hashを記録 |
| `retested` | `change-accept` | reviewer名、再受入レビュー証跡 | 影響成果物を新hashでaccepted |
| `reaccepted` / `approving` | `change-approve` | 指示されたrole、承認者、新しい承認証跡 | milestoneの全必須roleが再承認 |
| `approved` | `change-close` | なし | 置換Gate PASS、履歴保存、通常STEP再開 |

変更中に`complete-step`、`accept-artifact`、通常の`approve`、`seal-milestone`、`advance`を実行すると、工具は何も進めず`next`へ戻す。理由票、旧受入、旧承認、旧Gate、再検査、新受入、新承認、置換Gateはstatusと`bomdd/migration/gates/`に連鎖して残る。

| 色 | 条件 | 行動 |
|---|---|---|
| Green | 必須成果物 accepted、blocker 0 | `advance` で次へ進む |
| Yellow | non-blocker のみ、既定処置あり | 既定処置を記録して進む |
| Red | blocker、必須成果物不足、検査失敗 | 指定された戻り STEP へ移動 |

---

## 4. MIG-00 移行開始可能

目的: 作業中に発生する判断を、作業者から責任者と既定値へ移す。

### STEP-001 シナリオを有効化する

入力:

- 対象リポジトリの絶対パス
- プロダクト名

作業:

1. `migration-workflow.py init` を実行する。
2. `bomdd/migration/` が生成されたことを確認する。
3. `migration-profile.json` の `scenario.id` が `legacy-wpf-rdb` であることを確認する。

失敗時:

- 既存 `bomdd/migration/` がある: 上書きせず `EX-INIT-001`。
- 対象が Git 管理外: `EX-INIT-002`。

### STEP-002 移行憲章を確定する

`bomdd/00-charter.md` に次を記載する。

- 移行の目的。
- 対象業務、対象画面、対象外。
- 現行システムの正本となる版。
- Java source LOC、repository/module/screen/customer/active user数。
- 営業時間、繁忙、停止許容、SLA/SLO、規制、顧客version分布。
- 既存 RDB と既存データを継続利用する制約。
- 初期移行ではスキーマを変更しない方針。
- 移行と無関係なリファクタリングを行わない方針。
- 完了判定者。
- 切替 Go/No-Go 判定者。
- Program Gate、workstream、顧客cohortの運用規則。

### STEP-003 移行プロファイルを埋める

`migration-profile.json`では、Java/JDK/JavaFX/build system、規模、RDB、顧客停止許容、変更しない制約、slice/WIP上限、全14roleを固定する。`responsibility-matrix.md`、`program-governance.md`、`customer-operations-boundary.md`も同時に完成させる。.NET、Windows、構造、DI、DB provider/semantics、テスト、配布方式をMIG-00で選ばない。判断に必要な現行観測、棚卸し、仕様がまだないためである。

技術判断は次の成果物と期限に分ける。作業者は期限前に埋めず、`decision-record`が現在milestoneとownerを検査する。

| 期限 | 成果物 | 判断 |
|---|---|---|
| MIG-30 / STEP-030 | `decisions/MIG-30-db-technical-decisions.json` | DB transaction、NULL、日時、照合、timeout等 |
| MIG-40 / STEP-040 | `decisions/MIG-40-implementation-decisions.json` | .NET、Windows、構造、DI、DB provider、テスト入口 |
| MIG-80 / STEP-080 | `decisions/MIG-80-deployment-decisions.json` | packaging、signing、install、update |

MIG-00では三ファイルが`open`でも正常である。具体的な値は期限のSTEPで責任ownerが決め、作業者は選ばない。

旧版ですでに`migration-profile.json`へ八判断を書いた案件は、accepted profileを編集しない。新しいtool、`milestone-definition.json`、guideを案件へ凍結した後、Migration Ownerのローカルレビュー証跡を用意して一度だけ実行する。

```powershell
python bomdd/migration/tools/migration-workflow.py adopt-decision-layout `
  --project-root C:\path\to\TargetProject `
  --reviewer "Migration Ownerの割当名" `
  --review-evidence bomdd/migration/evidence/decision-layout-upgrade.md
```

案件内に存在する証跡ファイルとassigned ownerを持つ判断だけを期限別成果物へ移す。URLだけ、証跡欠落、owner未割当の判断は`open`へ戻し、期限のSTEPで`decision-record`する。通常milestone/STEPは変更しない。

### STEP-004 Gate を確認する

`migration-workflow.py check --milestone MIG-00` を実行する。Red の場合、表示された不足成果物を作る。Green になるまで MIG-10 へ進まない。

---

## 5. MIG-10 現行基準線確定

目的: 移行中に比較対象が動かないよう、原版と環境を固定する。

### STEP-011 現行版を凍結する

記録するもの:

- リポジトリ URL、commit、tag、branch。
- dirty 状態。
- ビルド生成物 hash。
- 設定ファイルの版。ただし秘密値は記録しない。
- 既知の生成工程。

未コミット変更を含む個体を基準線にする場合、パッチ hash と承認者が必要である。

### STEP-012 現行ビルドを再現する

クリーンな作業場所でビルドし、以下を保存する。

- 実行したコマンド。
- SDK、compiler、依存、OS 情報。
- stdout、stderr、終了コード。
- 成果物 hash。
- 起動確認結果。

ビルド不能でも推測修正しない。`EX-BASELINE-001` とし、稼働バイナリを原版にするか、現行版を修復してから凍結するかを Migration Owner が裁定する。

ビルド前提がない場合の順序は固定する。

1. source、DB、設定を変更せず `EX-BASELINE-001` を作る。
2. fixed commit と同じ tag/build ID の公式配布物があるか確認する。
3. 公式配布物がある場合、URL、hash、version/commit 表示、起動結果を証跡化し、原版採用を Owner が裁定する。
4. 同一性を証明できる公式配布物がない場合だけ、toolchain 供給または現行版修復の裁定を求める。
5. 近い版、非公式 build、worker が修正した source で代用しない。

### STEP-013 DB 基準線を作る

本番 DB を変更しない。DB Custodian が次を用意する。

- 読み取り専用棚卸し接続。
- 検証用の匿名化複製 DB。
- 複製元時点、DB engine/version、schema hash。
- table/view/trigger/stored procedure/index/sequence/permission 一覧。
- backup と restore の手順。

fixture はコピーまたは別の復元検査DBを使い、温存した基準 fixture や本番DBに検査や新アプリを直接接続しない。

作成順序を固定する。

1. `migration-profile.json`の`constraints.database_engine`を見る。SQLiteなら`.templates/baseline-fixture-manifest.json`、PostgreSQLなら`.templates/baseline-fixture-postgresql-manifest.json`を`evidence/baseline-fixture-manifest.json`へコピーする。他engineなら作業を止める。
2. SQLiteは基準fixtureと別のrestore control copyを保存する。PostgreSQLはcustom-format dumpを空の専用restore control DBへ復元する。本番DB名をconnectionへ書かない。
3. PostgreSQLでは専用validatorをSCRAM等の現行認証で作り、restore control DBのSELECTだけを許可し、`default_transaction_read_only=on`にする。本番DBへのCONNECTを許可しない。
4. DB基準線、schema evidence、復元観測、観測証跡のpath/hashを記録する。
5. `canonical_queries`へ、移行後も一致すべき代表`SELECT`と期待行を最低1件記録する。書込みSQL、複数文、末尾`;`は使わない。
6. PostgreSQLでは`psql`、`pg_dump`、`pg_restore`を案件内の固定pathへ置いてhashを記録し、passwordはmanifestへ書かず`credential_env`で指定した環境変数へ実行時だけ設定する。
7. `check --milestone MIG-10`を実行する。SQLiteはintegrity/FK/代表値、PostgreSQLはdump catalog/read-only/version/constraint/index/live schema/代表値がPASSするまで受入しない。
8. `ART-DB-BASELINE`の`accept-artifact`ではmanifestを`--evidence`に含める。

### STEP-014 現行観測を固定する

主要ユースケースについて次を保存する。

- 入力。
- 操作手順。
- 表示結果。
- DB の観測結果。
- ログ、外部連携結果。
- スクリーンショット。
- 実行日時と実行個体。

個人情報、秘密情報は匿名化する。匿名化規則自体を成果物として保存する。

画像だけで業務上の主張を証明しない。作成順序を固定する。

1. 空状態、代表データあり、別viewの最低3状態を観測する。該当しない状態はUI Approverの裁定証跡を残してcoverage policyを変更する。
2. 各観測にスクリーンショットを最低1枚保存する。拡張子は実形式と一致させる。
3. 各観測にDOM/accessibility tree/DB観測/execution log等の非画像証跡を最低1件保存する。
4. `.templates/current-ui-evidence-manifest.json`を`evidence/current-ui-evidence-manifest.json`へコピーする。
5. `current-observation-index.md`の全`OBS-CURRENT-*`をmanifestへ列挙し、各主張の`supported_by`へ証跡IDを記録する。
6. `check --milestone MIG-10`でID、状態、hash、実形式、寸法、主張対応がPASSするまで受入しない。
7. `ART-CURRENT-OBS`の`accept-artifact`ではmanifestを`--evidence`に含める。MIG-10はUI Approverの承認も必要とする。

#### Java/NFR/security/operations基準線も同じSTEPで閉じる

- `java-runtime-baseline.md`: JDK/JRE、JavaFX、Maven/Gradle、plugin/repository、JVM option、module path/classpath、native、起動・配布構造を実コマンドとhashで固定する。
- `nonfunctional-baseline.json`: 固定environment/dataset/workloadでcold/warm start、UI input、DB roundtrip、batch、memory/soakを複数sample測定する。全metricの実測証跡を`--evidence`へ含める。
- `security-baseline.md`: authn/authz、role、secret、certificate、crypto、audit、network、dependency/SBOM、既知riskを記録する。
- `deployment-operations-baseline.md`: install/update/config/log/monitoring/support/backup/restore/incident/端末管理の現行手順とownerを記録する。

Java、DB、UI、NFR、security、operationsの基準版が同じsource/release/customer環境を指していることを確認する。異なる版を混ぜる場合は差分と裁定を記録する。

### 旧案件へmanifest検査を導入する

すでにMIG-10を通過した案件では、hashだけを追加したりstatusを手編集したりしない。新しい凍結tool、definition、guide、2テンプレートを配置し、manifestを記入した後、次の一つの変更でDB/UI成果物をまとめて開く。

```powershell
python bomdd/migration/tools/migration-workflow.py change-open `
  --project-root C:\path\to\TargetProject `
  --milestone MIG-10 `
  --changed-file bomdd/migration/db-baseline.md `
  --changed-file bomdd/migration/current-observation-index.md `
  --reason "fixtureとUI証跡の実体検査を導入する"
```

`change-retest`後、`change-accept`の`--evidence`へ2manifestと再受入レビューをすべて渡す。続いてMigration Owner、DB Custodian、UI Approverが新しい証跡で再承認し、`change-close`で置換MIG-10 Gateを通す。工具は通常位置を保存し、完了後に同じSTEPへ戻す。

---

## 5A. MIG-15 技術実現性確認

目的: 全数設計や量産を始める前に、失敗すればProgramを止める技術リスクを実測する。実証コードは製品実装として再利用しなくてよい。

### STEP-015 代表リスクを固定する

`feasibility-portfolio.json`の七risk classを削除しない。各classについて現行の最難関または本番影響最大の参照先、実行owner、失敗時fallback、時間箱を記入する。簡単な一覧画面だけを代表に選ばない。

### STEP-016 隔離環境で実証する

- 複雑JavaFX UIをWPFで再現し、thread、binding、focus、DPI、IME、virtualizationを観測する。
- productionではない復元DBでread、transaction write、rollback、現行読取り互換性を観測する。
- 代表外部連携、認証・証明書、third-party代替、cold start、memory soakを実測する。
- clean Windows環境でinstall、署名検証、起動、update/rollback候補を試す。

### STEP-017 Go/No-Goを裁定する

各itemを`pass`または`accepted-risk`にする。`accepted-risk`には回避策、残存影響、owner、期限を`feasibility-report.md`へ記録する。一件でも`open`/`fail`なら`go_no_go`を`go`にせず、ProgramをMIG-15に留める。

---

## 6. MIG-20 全数棚卸し・workstream分割完了

目的: 移行対象を全数化し、「知らなかったため漏れた」を減らす。

### STEP-021 成果物インベントリを作る

既存の `method/onboarding/existing-project-migration.md` に従い、次を作る。

- `bomdd/plm-intake/migration-inventory.md`
- `bomdd/plm-intake/source-map.md`

Action 語彙は `reference/copy/summarize/split/not-exported` だけを使う。

同じsource commitから`code-inventory.json`を機械集計する。production/test Java、FXML、CSS、resource/i18n、generated、native、build/deployを分類し、module ownerと処置を付ける。`unclassified_files`と`unclassified_loc`がゼロになるまで受入しない。

### STEP-022 機能台帳を作る

画面メニューではなく、利用者が完了できる仕事を単位にする。各機能に `FUNC-*` ID を振り、次を記録する。

- 利用者と目的。
- 起点と終了条件。
- 読み書きする DB entity。
- 呼び出す外部連携。
- 正常、空、入力不正、権限不足、競合、外部障害。
- 現行テストと証跡。

### STEP-023 UI 台帳を作る

全 window/dialog/tab/menu について次を記録する。

- `UI-*` ID。
- 開き方、閉じ方。
- 必須表示要素。
- 入力と validation。
- enabled/disabled/selected/loading/error/empty 状態。
- keyboard、focus、shortcut。
- resize、DPI、大量件数時の挙動。

### STEP-024 DB 台帳を作る

DDL の写しだけで終えない。各 entity/field に業務上の意味を記録し、用途不明は `unknown` とする。用途を推測して削除しない。

### STEP-025 外部依存台帳を作る

ファイル、プリンタ、メール、OS、COM、DLL、API、共有フォルダ、タスクスケジューラ、認証、証明書、環境変数、レジストリを全数化する。

Java library、JavaFX control、JNA/JNI、report/export、licenseは`dependency-replacement-ledger.md`へretain/replace/wrap/remove、候補、license/security、実証参照、ownerを記録する。既存test assetとcustomer別configuration/plugin/帳票/権限差は`test-asset-inventory.md`と`customer-variant-matrix.md`へ分離する。

### STEP-026 不明点を分類する

- 移行結果を一意に決められない: blocker。
- 保守性や見た目の改善だけに影響する: non-blocker。
- 現行不具合の疑い: defect candidate。

不明点を空欄のまま残さない。全項目を`workstream-register.json`の一workstreamと一sliceへ割り当てる。sliceはprofileの最大person-days以下、IDは全体で一意、leadとreviewerは別人、依存は循環なしとする。Program Managerは未割当ゼロとworkstream間依存を承認する。

---

## 7. MIG-30 現行契約復元完了

目的: 旧技術の構造でなく、WPF でも守るべき挙動を仕様化する。

### STEP-030 DB互換性の技術判断を固定する

MIG-10のDB基準線とMIG-20のDB台帳を入力に、DB Custodianが`DEC-DB-SEMANTICS`を決める。推測や一般論で埋めない。観測結果を案件内の証跡ファイルに保存してから実行する。

```powershell
python bomdd/migration/tools/migration-workflow.py decision-record `
  --project-root C:\path\to\TargetProject `
  --set DECSET-DB-COMPATIBILITY `
  --decision DEC-DB-SEMANTICS `
  --decider "DB Custodianの割当名" `
  --status decided `
  --value "観測から決めたtransaction、NULL、日時、照合、timeout規則" `
  --evidence bomdd/migration/evidence/DEC-DB-SEMANTICS.md
```

`next`が成果物受入を指示したら、DB Custodianのレビュー証跡を付けて`ART-DB-TECH-DECISIONS`を受入する。未決定、owner不一致、証跡なし、証跡hash差は受入とSTEP完了を拒否する。

### STEP-031 要求と仕様を復元する

次の順で記録する。

1. 利用者が達成する結果。
2. 業務規則。
3. 状態遷移。
4. 入出力。
5. エラー契約。
6. 権限。
7. 同時実行。
8. 性能・可用性・監査。

旧クラス名、旧 GUI widget 名、旧 ORM API を要求にしない。それらが契約である場合だけ K-BOM または M-BOM に残す。

### STEP-032 現行差異を裁定する

観測した動作を次の三つに分類する。

| 分類 | 扱い |
|---|---|
| `preserve` | 新システムでも維持し、固定オラクルへ入れる |
| `change-approved` | 変更要求と新期待値を記録する |
| `legacy-defect` | CAPA/ECO を別起票し、移行と混ぜない |

分類不能は blocker である。

### STEP-033 UI 表示・操作契約を作る

pixel-exact を既定にしない。必須表示要素、意味、状態、操作可能性、focus、keyboard、承認者を固定する。見た目の知覚判断は golden と人間承認を使う。

### STEP-034 DB Compatibility Contract を作る

テンプレート `db-compatibility-contract.md` を使い、少なくとも次を固定する。

- schema を変更しない範囲。
- 新旧が読む/書く entity と field。
- 主キー、採番、NULL、default、precision、collation、timezone。
- transaction 境界、isolation、lock、retry、timeout。
- trigger、stored procedure、view の副作用。
- 現行が書いたデータを新系が読む互換性。
- 新系が書いたデータを現行が読む互換性。
- 書込み主体と切替境界。
- 件数、キー集合、重要値、履歴、業務不変条件の比較方法。

### STEP-035 マルチリーダー監査を行う

仕様から独立に要求、不変条件、受入深さを抽出し、読みの差を台帳化する。指摘を自動採用せず、本文照合後に Specification Owner が裁定する。

### STEP-036 言語・UI・NFR・security・顧客契約を固定する

`java-csharp-semantic-contract.md`のnull/exception/equality/generics/collection/decimal/date-time/thread/cancel/serialization/encoding/regex/reflection/lifecycleと、`javafx-wpf-interaction-contract.md`のApplication Thread/Dispatcher、Property/Binding、Observable collection、FXML/XAML、event、focus/IME、modal、Task/async、virtualization、WebView/print/tray、accessibility/DPI/i18n、shutdownを全行裁定する。

同時に`nonfunctional-acceptance-contract.json`へMIG-10の実測から数値閾値、workload、dataset、必要証跡を固定し、`security-acceptance-contract.md`と`customer-acceptance-contract.md`へ合否、owner、例外権限を記録する。一般的な「同等」「十分高速」は合格条件にしない。

---

## 8. MIG-40 Target/Factory設計完了

目的: 実装前に部品、製造単位、知識、検査、工程を接続する。

### STEP-040 WPF実装の技術判断を固定する

MIG-30で復元した仕様を入力に、次の順で責任ownerが判断する。

1. `DEC-DOTNET` — .NET lineとservicing。
2. `DEC-WINDOWS` — 対応WindowsとCPU。
3. `DEC-ARCH` — View/ViewModel/Application/Domain/Persistence境界。
4. `DEC-DI` — DI、設定、ログ、例外処理。
5. `DEC-DB-PROVIDER` — providerとdata access方式。
6. `DEC-TEST` — unit、integration、UI、acceptance入口。

毎回`next`が表示する`decision-record`を一件ずつ実行する。六件を同時編集しない。全件決定後、WPF Technical OwnerとAcceptance Ownerのレビュー証跡で`ART-IMPLEMENTATION-DECISIONS`を受入してからSTEP-041へ進む。

### STEP-041 E-BOM を作る

論理部品を core/surface に分類する。

- core: 業務規則、状態遷移、計算、validation。
- surface: WPF 表示、RDB 文法・provider、OS、ファイル、印刷、外部 API。

各 item に requirement refs、acceptance refs、依存、owner、consumer を記録する。

### STEP-042 K-BOM を作る

作業者や AI が暗黙に選びそうな外部知識を記録する。

- WPF binding、command、validation、Dispatcher、async の規則。
- UI thread をブロックしない規則。
- DB provider の型変換、parameter、transaction、timeout。
- 日時、文字列、NULL、decimal の変換規則。
- デザイン token、keyboard、accessibility。
- configuration、logging、およびpackaging検査の要求。packaging製品、署名、installer、update方式の最終判断はSTEP-080まで行わない。

### STEP-043 M-BOM を作る

既定の製造境界:

```text
WPF View
  -> ViewModel / Presentation State
  -> Application Use Case
  -> Domain Rules
  -> Persistence Port
  -> RDB Adapter
```

案件が別構造を採用する場合、Technical Owner の決定記録が必要である。View または ViewModel から connection、SQL、transaction を直接所有しない。

### STEP-044 Control Plan を作る

| 対象 | 既定の検査 |
|---|---|
| core | unit、境界値、状態遷移、反例 |
| DB | 複製 DB への実接続、読書き、transaction、不変条件 |
| UI 構造 | 必須要素、状態、操作シナリオ |
| UI 知覚 | golden + UI Approver |
| 外部連携 | execution L2/L3 |
| 性能 | 実行環境固定の測定 |
| 配布 | クリーン環境 install/start/update/uninstall |

文字列の存在だけを検査する L0 を既定にしない。高リスク検査治具には negative control を用意し、壊した個体を落とせることを較正する。

### STEP-045 Routing を固定する

一機能の標準工程は変更しない。

```text
現行観測
-> 要求/仕様
-> E/M/K-BOM
-> Control Plan
-> WPF 実装
-> 自己受入
-> 新旧比較
-> 差分帰属
-> As-Built
```

### STEP-046 トレース監査を行う

最低限次が双方向にたどれることを確認する。

```text
REQ -> Spec -> E-BOM -> M-BOM -> Control Plan -> Routing -> As-Built
DB schema intent -> DB entity/field -> E-BOM -> M-BOM persistence -> Control Plan
UI source -> Display Contract -> E-BOM -> Control Plan
```

stop finding が 0 になるまで実装を開始しない。

### STEP-047 並行製造の境界を凍結する

`target-architecture.md`、`workstream-interface-register.json`、`build-release-architecture.md`、`observability-design.md`、`security-design.md`を完成させる。interfaceごとにproducer、consumer、version、契約file/hash、contract tests、変更承認者を記録する。workstream間でsource fileまたはDB transaction ownerが重複する場合は、分割を直してからMIG-40 Gateを通す。

---

## 9. MIG-50 Migration factory準備完了

目的: コードを書く前に、入力、期待値、検査、戻り先を固定する。

### STEP-051 移行スライスを固定順で並べる

原則順序:

1. アプリ起動と設定読込み。
2. DB 接続と死活確認。
3. 読取り専用の一覧。
4. 読取り専用の詳細。
5. 単一 record の登録。
6. 更新。
7. 削除または無効化。
8. transaction を伴う操作。
9. error/cancel/retry。
10. batch、大量データ、外部連携。
11. 管理機能。
12. 性能、長時間動作、障害復旧。
13. 配布と切替。

依存上この順を変更する場合、Migration Owner の裁定記録を付ける。

### STEP-052 固定オラクルを作る

期待値の出所を `requirement/approved-current-behavior/approved-change` のいずれかにする。現行コードをそのまま期待値生成器にして自己一致させない。

### STEP-053 DB fixture と保全オラクルを作る

最低限の検査行:

- 新系が現行 fixture を損失なく読める。
- 読取りで DB が変更されない。
- 新系の書込み結果が契約どおりである。
- rollback 後に基準 fixture と一致する。
- transaction 途中失敗で部分更新が残らない。
- retry により二重登録されない。
- 現行と新系の query 結果が等価規則内で一致する。

### STEP-054 オラクルを較正する

正常個体を通し、事前に作った変異個体を落とす。検査が沈黙している場合、製造を開始しない。

### STEP-055 Work Order を凍結する

作業者または製造 AI へ渡す情報:

- Spec、E/K/M-BOM、Control Plan、Routing、Work Order。
- WPF/RDB の観測契約。
- 自己受入コマンド。
- 変更可能パス。
- ずる報告形式。

渡さない情報:

- 固定オラクル実装と fixture の秘密期待値。
- 他工場の成果。
- 前回の差分とコーチング履歴。

### STEP-056 Factoryをclean環境で起動する

`migration-factory-plan.md`、`contract-test-index.md`、`test-data-plan.md`を完成させ、clean agentでrestore/build/test/publish/install-smoke/SBOM/sign verify dry-runを実行する。全結果と証跡を`ci-readiness.json`へ記録する。

MIG-20でacceptedになったregisterから状態ファイルを生成する。

```powershell
python bomdd/migration/tools/migration-workflow.py workstream-init `
  --project-root C:\path\to\TargetProject
```

各leadは自workstreamのsliceを`planned -> ready`へ一つずつ進め、入力、interface version、test data、oracle、変更可能範囲が揃った証跡を付ける。status JSONを手編集しない。

---

## 10. MIG-60 Pilot wave合格

目的: 全面移行前に、startup/config、複雑UI、DB read、DB transaction write、外部連携、NFR、install/update、security、operationsを代表する複数sliceで製造工程を一周する。一つの簡単なread-only画面だけでは合格しない。

### STEP-061 WPF walking skeleton を作る

最低限を構築する。

- アプリ起動。
- 設定読込み。
- DI composition root。
- ログ。
- global exception handling。
- View/ViewModel/Application/Persistence の境界。
- build と test の入口。

業務機能をまとめて作らない。

### STEP-062 DB 読取りを実装する

複製 DB へ読み取り専用で接続する。parameter、timeout、cancellation、型変換、resource disposal を検査する。UI thread で同期 DB I/O を行わない。

### STEP-063 一覧画面を実装する

最低限の状態:

- loading。
- normal。
- empty。
- error。
- cancel。
- window close during load。

大量件数が対象なら virtualization と応答性を測る。

### STEP-064 新旧比較を行う

比較するもの:

- record の集合と並び。
- 表示項目と意味。
- NULL/空文字/日時/数値の表現。
- error と empty の区別。
- 操作可能性と focus。
- 実行時間と UI freeze。

### STEP-065 差分を帰属する

| 帰属 | 戻り先 |
|---|---|
| `spec_omission` | MIG-30 |
| `bom_sync_gap` | MIG-40 |
| `oracle_gap` | MIG-50 |
| `manufacturing_miss` | 現在の Work Order |
| `legacy_defect` | CAPA/ECO |
| `approved_difference` | 裁定記録を追加して継続 |
| `harness_bug` | オラクルを修復・再較正 |

### STEP-066 As-Built を記録する

commit、artifact hash、SDK、依存、コマンド、検査結果、差分、ずる、承認者を記録する。

各代表risk classを`pilot-portfolio.json`へ一度ずつ対応付け、clean install証跡と独立approverを記録する。全itemと`aggregate_result`が`pass`になるまで量産へ進まない。

---

## 11. MIG-70 全workstream統合完了

目的: 全スライスを同じ工程で閉じ、部分的な「終わったつもり」を防ぐ。

### STEP-071 一スライスずつ移行する

各workerはleadが`ready`にしたsliceを一件だけclaimする。profileのWIP上限を工具が検査する。

```powershell
python bomdd/migration/tools/migration-workflow.py slice-claim `
  --project-root C:\path\to\TargetProject `
  --workstream WS-ID --slice SLICE-ID --worker "Assigned Name" `
  --evidence bomdd/migration/evidence/SLICE-ID-claim.md
```

次の状態を一段ずつ通す。

```text
planned
-> ready
-> claimed
-> manufacturing
-> self-accepted
-> integrated
-> compared
-> accepted
-> as-built
```

状態の飛び越し、別workerのslice編集、claimなしの実装、claimant自身による統合以後の承認は禁止する。`slice-transition --to <NEXT> --actor <NAME> --evidence <FILE>`を使う。離脱時は`slice-release`で`ready`へ戻す。局所問題は`slice-block`で当該sliceだけを止め、解決証跡を`slice-unblock`へ渡す。

### STEP-072 WPF 固有検査を行う

該当する全画面で確認する。

- binding error がログにない。
- command の二重実行を防ぐ。
- async 中の close/cancel が安全。
- UI thread を長時間ブロックしない。
- validation と error message が表示される。
- focus、keyboard、shortcut が契約どおり。
- DPI、font、window resize で必須要素が失われない。
- 大量データで virtualization が機能する。
- unhandled exception でデータ破損しない。

### STEP-073 DB 書込み検査を行う

書込み機能ごとに確認する。

- transaction の開始・commit・rollback 範囲。
- optimistic/pessimistic concurrency の契約。
- timeout、deadlock、retry。
- identity/sequence/generated value。
- trigger と stored procedure の副作用。
- 同一操作の再送で二重更新しないこと。
- 新系書込み後の現行読取り互換性。

### STEP-074 全回帰を実行する

- 既存固定オラクル全行。
- 変更行。
- DB 保全オラクル。
- UI 表示契約。
- 性能と長時間動作。
- install/起動。

結果はスライス別だけでなく、統合個体の As-Built にも保存する。

#### MIG-70完了前に残差をゼロまたは裁定済みにする

`unknown`、未分類差分、blocker、証跡なしの`accepted`が一件でもあればMIG-75へ進まない。全workstreamが閉じたら次を実行し、registerと各statusのhash、slice/as-built/blocker数を`workstream-snapshot.json`へ固定する。

```powershell
python bomdd/migration/tools/migration-workflow.py workstream-snapshot `
  --project-root C:\path\to\TargetProject
```

統合個体に対するfunctional、NFR、security回帰とrelease candidate manifestは同一source commit/artifact hashを参照させる。

---

## 11A. MIG-75 Release Candidate受入

目的: 技術チーム内で合格した個体を、変更せず顧客・運用・security・releaseの全視点で受け入れる。

### STEP-075 Release Candidateを一意に固定する

`release-candidate-acceptance.json`のrelease manifest path/hashをMIG-70のRCへ一致させる。以降の全試験は同じRCを使い、再buildした場合はMIG-70の受入後変更からやり直す。

### STEP-076 顧客UATを実行する

顧客variantと重要業務シナリオを`customer-uat-ledger.md`へ列挙し、顧客受入者、結果、差分、証跡を記録する。開発者による代理確認だけで合格にしない。

### STEP-077 Install/upgradeと運用を再演する

clean端末と既存版導入済み端末でinstall/upgrade/config保持/uninstall/rollbackを実行する。Operations Ownerが監視、ログ採取、障害起票、backup/restore入口、support escalationを`operations-rehearsal.md`どおり実演する。

### STEP-078 Securityとaccessibilityを受入する

認証、認可、秘密、署名、SBOM、脆弱性、監査ログ、keyboard/focus/reader/DPI/contrastを契約どおり検査し、例外は期限とowner付きで裁定する。

### STEP-079 RC受入を閉じる

七つの`RC-*` checkへ証跡を対応付け、全て`pass`、`aggregate_result=pass`にする。Customer Acceptance、Security、Release、Operations、Acceptance、UIの各ownerが同じRC hashを承認する。

---

## 12. MIG-80 段階展開準備完了

目的: 本番で初めて知る作業をなくし、戻せる状態を証明する。

### STEP-080 配布の技術判断を固定する

MIG-75で受入済みの同一RCを入力に、Release Ownerが`DEC-PACKAGING`、Migration Ownerが`DEC-ROLLOUT`、Operations Ownerが`DEC-SUPPORT`を決める。MIG-40では配布検査の枠だけをControl Planへ置き、製品、署名、installer、update、cohort順、停止条件、hypercare体制はここで固定する。

`next`が表示する`decision-record`を実行し、`ART-DEPLOYMENT-DECISIONS`を受入する。成果物受入後だけSTEP-081へ進む。

### STEP-081 Cutover Runbook を完成させる

各手順に実行者、開始条件、コマンド、期待結果、証跡、timeout、失敗時処置を記載する。

`rollout-plan.md`にはcanaryから全顧客までのcohort、対象数、開始条件、観測窓、SLO、stop/rollback閾値、customer communicationを記載する。`support-readiness.md`にはseverity、連絡経路、当番、既知問題、診断採取、legacy fallback期限を記載する。

### STEP-082 Rollback Runbook を完成させる

rollback trigger を数値または観測事実で定義する。「問題があれば戻す」と書かない。

### STEP-083 backup/restore を実測する

backup 成功だけでは足りない。隔離環境へ restore し、DB 保全オラクルを実行する。

### STEP-084 同時書込みを防ぐ

既定:

- 検証中: 新系は複製 DB に接続する。
- 本番切替前: 現行の新規書込みを停止する。
- 切替中: 書込み主体は一つだけにする。
- 二重書込み: 原則禁止。採用には専用設計、冪等性、照合、rollback の Control Plan が必要。

### STEP-085 切替リハーサルを行う

本番と同じ順序、同じ役割、同じ Runbook で行う。所要時間は判断材料にするが、手順の省略には使わない。

リハーサル中の口頭指示は介入として記録し、Runbook へ還元する。

Release Ownerは受入済みRCからpromoteしたartifactのpath/hash/size、署名検証、SBOM hash、証明書、build証跡を`signed-release-manifest.json`へ記録する。署名対象を再buildしない。別担当者がRunbook、rollback、restore、署名検証を先頭から再演できるまでMIG-80を通さない。

---

## 13. MIG-90 本番段階展開完了

目的: cohortごとに書込み主体を安全に切り替え、DB、telemetry、利用者影響を確認してから次cohortへ進む。

### STEP-091 Go/No-Go を記録する

口頭だけで開始しない。cohortごとに承認者、対象顧客/device、時刻、signed release hash、backup ID、rollback deadlineを記録する。前cohortの観測窓が閉じる前に次cohortを開始しない。

### STEP-092 書込みを停止し backup する

現行の業務停止を確認してから backup する。停止確認と backup 完了を別の証跡にする。

### STEP-093 新系を配置する

Runbook のコマンドだけを使う。本番中の場当たり的な設定変更は `EX-CUTOVER-003` として記録する。

### STEP-094 smoke と DB 整合性を確認する

最低限:

- 起動、認証、設定。
- 代表的な読取り。
- 管理された一件の書込み。
- 件数、キー、重要値、履歴、不変条件。
- ログ、監視、外部連携。

### STEP-095 Go/rollback を裁定する

rollback trigger に一つでも該当すれば、作業者は改善を試みず Rollback Runbook を開始する。例外的に継続する権限は Migration Owner だけが持ち、理由と時刻を記録する。

各cohortを`accepted`、`rolled-back`、または期限・owner・顧客合意付き`deferred`へ閉じる。`cohort-deployment-ledger.json`の顧客数をscopeと照合し、全in-scope顧客がacceptedまたは正式deferred、`aggregate_result=pass`になるまでMIG-100へ進まない。

---

## 14. MIG-100 安定運用移管完了

目的: 移行チームの記憶に依存せず、運用・保守・再検査を可能にする。

### STEP-101 安定化期間を観測する

チャーターで決めた期間、次を観測する。

- error/warning 件数。
- DB timeout/deadlock/concurrency conflict。
- UI freeze、起動失敗。
- 主要操作の性能。
- 問い合わせと業務差分。
- rollback trigger の発生有無。

### STEP-102 Service BOM を完成させる

外部依存や環境変更から、影響部品、再検査、交換/再製造判断を逆引きできるようにする。

### STEP-103 運用引継を行う

運用担当者が次を実演する。

- install/update。
- 設定確認。
- ログ採取。
- DB 接続確認。
- backup/restore 入口。
- 障害票作成。
- Service BOM からの再検査選択。

説明を聞いたことではなく、実演証跡を合格条件にする。

### STEP-104 旧系の処置を裁定する

即時削除しない。保管期間、起動禁止、秘密情報、ライセンス、ソース、build 環境、復旧目的を裁定し、Service BOM または廃止記録へ残す。

---

## 15. 例外が起きたとき

問題発生時に自由形式で調査を始めず、status JSONも手編集しない。観測証跡を保存した後、カタログを検索する。

```powershell
python bomdd/migration/tools/migration-workflow.py exception-catalog `
  --project-root C:\path\to\TargetProject `
  --query "接続"
```

最も近いIDを一つ選び、次を実行する。三境界は`unchanged`、`changed`、`unknown`のいずれかを事実どおり指定する。`unknown`を推測で`unchanged`にしない。

```powershell
python bomdd/migration/tools/migration-workflow.py exception-open `
  --project-root C:\path\to\TargetProject `
  --catalog-id EX-DB-001 `
  --symptom "read-only棚卸し接続がtimeoutした" `
  --evidence bomdd/migration/evidence/EX-DB-001-observation.md `
  --production-db unchanged `
  --baseline-fixture unchanged `
  --current-source unchanged
```

工具が次を自動実行する。

- `bomdd/migration/exceptions/<発生ID>-open.md`を生成し、発生milestone/STEP、分類、owner、証跡hash、三境界、既定処置を固定する。
- カタログ分類が`non-blocker または blocker`なら、安全側のblockerにする。
- 三境界に`changed`または`unknown`があり、元分類がblocker以外ならblockerへ格上げする。
- blockerをstatusへ登録する。通常STEP、通常受入・承認、受入後変更、seal、advanceは解消まで拒否する。
- 通常の現在位置を変更しない。カタログの再開欄は解消後のフォロー先として表示し、STEPを自動的に飛ばさない。

登録後は毎回`next`を実行する。表示された既定処置を実施し、新しい解消証跡を作る。完了したら、`next`に表示された発生IDをそのまま使う。

```powershell
python bomdd/migration/tools/migration-workflow.py exception-resolve `
  --project-root C:\path\to\TargetProject `
  --exception EX-DB-001-<timestamp> `
  --resolver "責任者表の割当名" `
  --resolution "承認済みread-only経路を復旧し、棚卸しquery成功を確認した" `
  --evidence bomdd/migration/evidence/EX-DB-001-resolution.md
```

解消時はopen記録と観測証跡のhashを再照合する。内容変更または証跡欠落があればblockerを解除しない。成功時は別の`-resolved.md`を生成し、open記録を上書きせず、元の通常STEPを再表示する。

Gateはopen記録、観測証跡、安全作業記録、解消記録、解消証跡を継続的に再照合する。解消後に内容が変わった場合もGateはFAILし、`next`は`EX-STATE-001`の登録を指示する。

blocker中の別作業は既定で禁止する。責任者が影響しない一作業を明示できる場合だけ、次で許可する。

```powershell
python bomdd/migration/tools/migration-workflow.py exception-safe-work `
  --project-root C:\path\to\TargetProject `
  --exception EX-DB-001-<timestamp> `
  --work "凍結済みschema資料のread-onlyレビュー" `
  --authorizer "DB Custodianの割当名" `
  --evidence bomdd/migration/evidence/EX-DB-001-safe-work-approval.md
```

non-blockerとdefectも`exception-open`で記録する。Gateをblockしないが、`next`は最初の未解消例外の既定処置を先に表示する。処置または外部ECO/CAPAへの引渡しを証跡化し、`exception-resolve`で閉じる。

---

## 16. 禁止事項

- 移行中に現行コードを「ついでに」修正する。
- 現行 DB の用途不明 object を削除する。
- 本番 DB で自動テストする。
- 新旧アプリを無設計で同時書込みさせる。
- 基準 fixture を直接更新する。
- 仕様裁定なしに現行差分をバグまたは改善と決める。
- Control Plan より先に実装を完成扱いする。
- 証跡なしで成果物を `accepted` にする。
- Gate Red のまま次のマイルストーンへ進む。
- 作業終了時に次の STEP を空欄にする。
- `bomdd-init` や通常新規開発へ本シナリオのコマンドを設置する。

---

## 17. 手順書自体の受入

本手順書は、作成者以外の担当者による transfer test を行う。

1. freshなProgram Manager、workstream lead、Migration Worker、reviewer、Release/Operations役へ、本キット、役割別入口、記入済み例だけを渡す。
2. 模擬的な複数repository/module/customer datasetでMIG-00からMIG-100まで実行する。少なくとも二workstream、三slice、二worker、二cohortを使う。
3. claim競合、WIP超過、interface hash変更、局所blocker、worker離脱、受入後変更、RC再build、cohort rollbackのnegative controlを実行し、工具が誤進行を拒否することを確認する。
4. 作成者による口頭介入を全件記録する。
5. 各介入を`手順不足/成果物不足/既定値不足/例外処置不足/工具不足/担当者誤読`に分類する。
6. 手順書、テンプレート、コマンドへ一件ずつ還元し、同じ介入が消えたことを別のfresh担当者で再試験する。
7. 本番Programへの適用は、全Gateのpositive path、全negative control、PDFとMarkdown一致、実案件固有RACI/閾値/顧客cohortのレビュー後に承認する。

同じ工具介入が独立した三回で再現した場合、シナリオ専用スキルへの昇格を検討する。スキルは通常新規開発へ設置しない。

---

## 18. 参照

- 既存 BomDD 導入: `method/onboarding/existing-project-migration.md`
- 既存移行チェック: `method/onboarding/migration-checklist.md`
- TraceLink 規則: `method/contracts/traceability-rules.md`
- DB schema intent: `method/templates/db/schema-intent.md`
- Control Plan: `method/templates/33-control-plan.yaml`
- Routing: `method/templates/34-routing.yaml`
- Migration Oracle: `method/templates/62-migration-oracle.md`
- Diff Audit: `method/templates/63-diff-audit.md`
- Service BOM: `method/templates/53-service-bom.yaml`
