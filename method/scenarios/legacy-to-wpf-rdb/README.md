# Legacy to WPF/RDB Migration Kit

顧客が実運用する数十万行規模の **Java + JavaFX** システムを **C#/.NET + WPF** へ再実装し、既存 RDB を継続利用する案件専用の BomDD 移行キットである。

> **初めて参加する人は、ほかの資料より先に [はじめに - 移行オンボーディング](onboarding.md) を開く。**

通常の新規開発では使用しない。`bomdd-init`、新規開発チェックリスト、通常の Phase 0-7 に本キットのコマンドや成果物を追加しない。

## 対象

- 既存実装と稼働中の振る舞いがある。
- 移行先は C#/.NET + WPF である。
- 既存の RDB、既存データ、原則として既存スキーマを継続利用する。
- 最小コスト、最短期間より、作業者が迷わず作業を継続できることを優先する。
- 複数repository/module/team/customerをProgram Gate、workstream、slice、customer cohortで管理する。

対象外:

- 原版のない新規開発。
- Web、モバイル、Avalonia など WPF 以外への移行。
- DB エンジンの同時移行。
- 初回からの全面的なスキーマ再設計。
- 移行と同時に行う大規模リファクタリング。

## 正本

1. 初参加者の入口: [onboarding.md](onboarding.md)
2. 実行手順: [migration-runbook.md](migration-runbook.md)
3. マイルストーンと Gate: [milestone-definition.json](milestone-definition.json)
4. 異常時処置: [exception-catalog.md](exception-catalog.md)
5. 案件の現在位置: 対象リポジトリの `bomdd/migration/migration-status.json`
6. Gate の証拠: 対象リポジトリの `bomdd/migration/gates/MIG-*-result.json`
7. 大規模案件の成果物一覧: [enterprise-artifact-catalog.md](enterprise-artifact-catalog.md)
8. Version 1.3からの差分根拠: [enterprise-gap-analysis.md](enterprise-gap-analysis.md)
9. Version 2.0受入記録: [validation/version-2.0-acceptance.md](validation/version-2.0-acceptance.md)
10. 変更点: [release-notes-2.0.md](release-notes-2.0.md)

説明と機械判定が矛盾した場合は、案件で凍結した `milestone-definition.json` と Gate 結果を優先し、矛盾自体を例外 `EX-DOC-001` として記録する。

## 明示的な有効化

対象リポジトリに対してだけ、次を実行する。

```powershell
python method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py init `
  --project-root C:\path\to\LegacyMigration `
  --product ExampleProduct
```

既定では既存ファイルを上書きしない。`bomdd/migration/` がすでに存在する場合は停止する。

## 日常コマンド

初期化後は案件に凍結された工具を使う。

```powershell
python bomdd/migration/tools/migration-workflow.py status --project-root C:\path\to\LegacyMigration
python bomdd/migration/tools/migration-workflow.py next --project-root C:\path\to\LegacyMigration
python bomdd/migration/tools/migration-workflow.py complete-step --project-root C:\path\to\LegacyMigration --evidence bomdd/path/to/evidence
python bomdd/migration/tools/migration-workflow.py accept-artifact --project-root C:\path\to\LegacyMigration --artifact ART-ID --evidence bomdd/path/to/evidence
python bomdd/migration/tools/migration-workflow.py approve --project-root C:\path\to\LegacyMigration --role "Migration Owner" --approver "Assigned Name" --evidence bomdd/path/to/approval.md
python bomdd/migration/tools/migration-workflow.py seal-milestone --project-root C:\path\to\LegacyMigration --milestone MIG-00 --reviewer "Assigned Name" --review-evidence bomdd/path/to/review.md
python bomdd/migration/tools/migration-workflow.py check --project-root C:\path\to\LegacyMigration
python bomdd/migration/tools/migration-workflow.py advance --project-root C:\path\to\LegacyMigration
python bomdd/migration/tools/migration-workflow.py handoff --project-root C:\path\to\LegacyMigration
```

MIG-50以後の実装担当者はProgram全体の`next`ではなく、次のscenario専用コマンドを使う。

```powershell
python bomdd/migration/tools/migration-workflow.py workstream-status --project-root C:\path\to\LegacyMigration --workstream WS-ID
python bomdd/migration/tools/migration-workflow.py slice-claim --project-root C:\path\to\LegacyMigration --workstream WS-ID --slice SLICE-ID --worker "Assigned Name" --evidence bomdd/path/to/claim.md
python bomdd/migration/tools/migration-workflow.py slice-transition --project-root C:\path\to\LegacyMigration --workstream WS-ID --slice SLICE-ID --to manufacturing --actor "Assigned Name" --evidence bomdd/path/to/evidence.md
```

状態飛越し、claimなし、worker WIP超過、claimant自身による統合以後の受入、証跡hash変更を工具が拒否する。離脱は`slice-release`、局所blockerは`slice-block`/`slice-unblock`、MIG-70集約は`workstream-snapshot`を使う。

コマンドは `bomdd/migration/migration-profile.json` の `scenario.id` が `legacy-wpf-rdb` でない場合、何も変更せず終了する。

`accept-artifact` と `approve` は対象ファイルの SHA-256 を自動記録し、`check` は現在内容を再計算する。受入後の内容変更は同じパスでも Gate FAIL になる。`seal-milestone` はhash導入前に受入済みだったmilestoneの一回限りの移行用であり、明示的な再レビュー証跡なしには実行しない。

MIG-10では`baseline-fixture-manifest.json`と`current-ui-evidence-manifest.json`をaccepted evidenceに含める。Gateは索引だけでなく、SQLiteのfixture/restore copy/integrity/FK/代表SELECT、またはPostgreSQLのcustom dump/read-only復元DB/version/constraint/index/live schema/代表SELECT、さらにUI観測IDと状態網羅、画像のhash/実形式/寸法、非画像証跡、主張との対応を再検査する。engine別テンプレートは案件の`bomdd/migration/.templates/`にだけ配布され、通常新規開発には現れない。

受入後に変更が必要になった場合は、`check --milestone MIG-ID` が示す最初の不一致ファイルから `change-open` を開始する。その後は `next` が `change-retest`、`change-accept`、必要人数分の `change-approve`、`change-close` を一つずつ指示する。変更中は通常の STEP、受入、承認、advance を工具が停止する。

問題発生時はstatusを手編集せず、まず`exception-catalog --query <症状の語>`でIDを絞り、`exception-open`で登録する。blocker中は工具が通常操作を拒否する。解消後は`exception-resolve`で新しい解消証跡を封印する。blocker中に別作業を許可する場合だけ、責任者が`exception-safe-work`を実行する。

技術判断はMIG-00に集めない。MIG-15で最難関を実証し、`decision-status`と`next`に従い、DB semanticsはMIG-30、WPF実装方式はMIG-40、packaging/cohort/supportはMIG-80で一件ずつ`decision-record`する。期限前の記録、owner不一致、案件外URLだけの証跡、未決定成果物の受入を工具が拒否する。

handoffは現在milestoneの未受入・未承認とfuture artifactを別節にする。`Future artifacts (not current milestone blockers)`を現在の不足へ数えない。GATE位置では`check --milestone`が再開コマンドである。`check`はread-only、`advance`は再検査・Gate結果保存・次milestone移動を行う。

旧版ですでにprofileへ技術判断を記録した案件は、新しい凍結tool、milestone definition、guideを配布した後、一度だけ`adopt-decision-layout --reviewer <NAME> --review-evidence <LOCAL_REVIEW>`を実行する。accepted profileは変更せず、案件内証跡がある判断だけを新成果物へ移し、URLのみの判断は期限milestoneでの再確認対象にする。

## スキルを同梱しない理由

初回版では AI スキルを設置しない。まず手順書、テンプレート、状態/Gate コマンドを第三者移管テストにかけ、同じ介入が繰り返された箇所だけを後続 ECO でスキル化する。通常開発への入口増加と、未実証の判断自動化を避けるためである。

## PDF

配布版: [legacy-to-wpf-rdb-migration-runbook.pdf](../../../output/pdf/legacy-to-wpf-rdb-migration-runbook.pdf)

正本はMarkdown Version 2.0である。配布PDFは2026-07-20生成、A4・48ページで、Part 1にオンボーディング全文、Part 2に規範手順を収録する。全ページをPNG化し、表・コード枠・Part境界・最終ページを検査済みである。案件の現在位置はPDFではなく、案件内の`bomdd/migration/migration-status.json`と`bomdd/migration/workstreams/*/status.json`で確認する。
