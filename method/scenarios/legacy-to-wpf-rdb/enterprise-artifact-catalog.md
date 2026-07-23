# Version 2.0 大規模Java/JavaFX移行 成果物カタログ

このカタログは、数十万行・複数team・顧客実運用中の案件で作業者に自由設計させないための正本である。各成果物は指定milestoneで受入し、後続Gateでもhashを累積再検査する。

## MIG-00 Program開始可能

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-CHARTER | `bomdd/00-charter.md` | Migration Owner | scope、非scope、停止条件、予算/期限変更権限 |
| ART-PROFILE | `bomdd/migration/migration-profile.json` | Program Manager | Java/JavaFX、規模、顧客数、RDB、mode、ownerを記入 |
| ART-ROLES | `bomdd/migration/responsibility-matrix.md` | Migration Owner | program/Java/WPF/DB/test/security/release/ops/customer roleを実名割当 |
| ART-PROGRAM-GOVERNANCE | `bomdd/migration/program-governance.md` | Program Manager | decision SLA、escalation、会議、変更凍結、workstream規則 |
| ART-CUSTOMER-BOUNDARY | `bomdd/migration/customer-operations-boundary.md` | Customer Acceptance Owner | 顧客、業務時間、停止許容、SLA、規制、連絡経路 |

## MIG-10 現行基準線確定

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-BASELINE | `current-baseline.md` | Java Technical Owner | source/release/config/build ID固定 |
| ART-BUILD-LOG | `evidence/baseline-build.log` | Java Technical Owner | clean buildまたは同一公式binaryの再現 |
| ART-DB-BASELINE | `db-baseline.md` + fixture manifest | DB Custodian | 複製DB、restore、代表値、schema |
| ART-CURRENT-OBS | `current-observation-index.md` + UI manifest | UI Approver | 代表状態、semantic evidence |
| ART-JAVA-BASELINE | `java-runtime-baseline.md` | Java Technical Owner | JDK/JavaFX/Maven/Gradle/plugin/JVM/native/generated/reflection |
| ART-NFR-BASELINE | `nonfunctional-baseline.json` | Acceptance Owner | 起動/UI/DB/batch/memory/CPU/soakの測定値 |
| ART-SECURITY-BASELINE | `security-baseline.md` | Security Owner | authn/authz/audit/secret/cert/crypto/data class |
| ART-OPS-BASELINE | `deployment-operations-baseline.md` | Operations Owner | installer/update/config/profile/端末管理/support/backup |

## MIG-15 技術実現性確認

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-FEASIBILITY-PORTFOLIO | `feasibility-portfolio.json` | WPF Technical Owner | UI/DB/integration/performance/installer/third-party各riskを実測し全件accepted |
| ART-FEASIBILITY-REPORT | `feasibility-report.md` | Program Manager | fatal risk、代替、見積range、inventory継続Go/No-Go |

## MIG-20 全数棚卸し・workstream分割完了

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-MIGRATION-INVENTORY | `plm-intake/migration-inventory.md` | Program Manager | 全repository/artifact |
| ART-SOURCE-MAP | `plm-intake/source-map.md` | Java Technical Owner | source/resource/generated/native/test/buildの所在 |
| ART-CODE-INVENTORY | `code-inventory.json` | Java Technical Owner | module/file/LOC分類、100% disposition |
| ART-FEATURE-INVENTORY | `feature-inventory.md` | Specification Owner | 全顧客業務機能 |
| ART-UI-INVENTORY | `ui-inventory.md` | UI Approver | 全window/dialog/view/state |
| ART-JAVAFX-INVENTORY | `javafx-surface-inventory.md` | Java Technical Owner | FXML/CSS/controller/binding/thread/interop等 |
| ART-DB-OBJECT-INVENTORY | `db-object-inventory.md` | DB Custodian | 全object/permission/use |
| ART-EXTERNAL-INVENTORY | `external-dependency-inventory.md` | Integration Owner | 外部system/file/device/protocol |
| ART-DEPENDENCY-LEDGER | `dependency-replacement-ledger.md` | WPF Technical Owner | Java依存ごとのretain/replace/rewrite/remove、license、owner |
| ART-TEST-INVENTORY | `test-asset-inventory.md` | Acceptance Owner | automated/manual/data/environment |
| ART-CUSTOMER-VARIANTS | `customer-variant-matrix.md` | Customer Acceptance Owner | config/feature/schema/version/端末差 |
| ART-WORKSTREAM-REGISTER | `workstream-register.json` | Program Manager | owner、slice、risk、dependency、interfaceを重複なしで割当 |

## MIG-30 互換契約確定

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-DB-TECH-DECISIONS | DB decision set | DB Custodian | DB semantics確定 |
| ART-REQUIREMENTS / ART-SPEC | BomDD requirements/spec | Specification Owner | 全FUNC/UI/DB/EXT/NFR/SEC trace |
| ART-JAVA-CSHARP-CONTRACT | `java-csharp-semantic-contract.md` | Java/WPF Technical Owner | 言語/runtime差の全項目裁定 |
| ART-JAVAFX-WPF-CONTRACT | `javafx-wpf-interaction-contract.md` | UI/WPF Technical Owner | UI lifecycle/binding/thread/event/style/focus差裁定 |
| ART-DISPLAY-CONTRACT | `display-contract.md` | UI Approver | state/keyboard/IME/accessibility/DPI |
| ART-DB-COMPATIBILITY | `db-compatibility-contract.md` | DB Custodian | read/write/rollback/version skew |
| ART-NFR-CONTRACT | `nonfunctional-acceptance-contract.json` | Acceptance Owner | metricごとのbaseline/limit/load/evidence |
| ART-SECURITY-CONTRACT | `security-acceptance-contract.md` | Security Owner | threat/control/test/residual risk |
| ART-CUSTOMER-ACCEPTANCE | `customer-acceptance-contract.md` | Customer Acceptance Owner | UAT population、signoff、training、support |
| ART-SPEC-RULINGS | `spec-rulings.md` | Specification Owner | preserve/change/legacy defect裁定 |

## MIG-40 Target/Factory設計完了

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-IMPLEMENTATION-DECISIONS | implementation decision set | WPF Technical Owner | .NET/Windows/arch/DI/provider/test |
| ART-TARGET-ARCHITECTURE | `target-architecture.md` | WPF Technical Owner | module/layer/process/thread/data/integration boundaries |
| ART-WORKSTREAM-INTERFACES | `workstream-interface-register.json` | Program Manager | owner/version/consumer/contract test/change rule |
| ART-BUILD-RELEASE-ARCH | `build-release-architecture.md` | Release Owner | CI、branch、merge、sign、SBOM、retention、release train |
| ART-OBSERVABILITY-DESIGN | `observability-design.md` | Operations Owner | log/metric/trace/crash/correlation/PII/runbook |
| ART-SECURITY-DESIGN | `security-design.md` | Security Owner | trust boundary、secret、authz、audit、supply chain |
| ART-EBOM〜ART-TRACE-AUDIT | BomDD設計一式 | WPF/Acceptance Owner | 全trace接続 |

## MIG-50 Migration factory準備完了

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-FACTORY-PLAN | `migration-factory-plan.md` | Program Manager | team、WIP、claim、review、integration cadence、stop rule |
| ART-SLICE-BACKLOG | `slice-backlog.md` | Program Manager | 全slice、workstream、risk、dependency、exit CP |
| ART-CONTRACT-TEST-INDEX | `contract-test-index.md` | Acceptance Owner | interfaceごとのproducer/consumer test |
| ART-TEST-DATA-PLAN | `test-data-plan.md` | DB/Security Owner | anonymization、refresh、retention、secret除外 |
| ART-CI-READINESS | `ci-readiness.json` | Release Owner | clean agent build/test/package/SBOM/sign dry-run |
| ART-WORK-ORDER〜ART-CALIBRATION | oracle/factory input | Acceptance Owner | 正常/変異較正PASS |

## MIG-60 Pilot wave合格

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-PILOT-PORTFOLIO | `pilot-portfolio.json` | Program Manager | UI/DB write/integration/NFR/install各risk-class slice accepted |
| ART-WALKING-SKELETON〜ART-FIRST-CHEAT | first vertical evidence | Workstream Lead | clean build→install→run→DB→UI→observe→uninstall |

## MIG-70 全workstream統合完了

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-WORKSTREAM-SNAPSHOT | `workstream-snapshot.json` | Program Manager | 全slice as-built、blocker 0、status/evidence hash一致 |
| ART-FEATURE-INDEX / ART-AS-BUILT | product index | Acceptance Owner | scope 100% disposition |
| ART-INTEGRATION-RESULT | integration acceptance | Acceptance Owner | contract/system/regression PASS |
| ART-NFR-RESULT | `evidence/nonfunctional-acceptance.json` | Acceptance Owner | 全metric limit内 |
| ART-SECURITY-RESULT | `evidence/security-acceptance.json` | Security Owner | scan/test/risk approval |
| ART-RELEASE-CANDIDATE | `evidence/release-candidate-manifest.json` | Release Owner | binary/config/SBOM/signature/hash固定 |

## MIG-75 Release Candidate受入

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-RC-ACCEPTANCE | `release-candidate-acceptance.json` | Customer Acceptance Owner | 全required discipline accepted |
| ART-CUSTOMER-UAT | `customer-uat-ledger.md` | Customer Acceptance Owner | representative cohort/UAT/signoff |
| ART-INSTALL-UPGRADE | `evidence/install-upgrade-acceptance.md` | Release Owner | clean/upgrade/repair/uninstall/rollback |
| ART-OPS-REHEARSAL | `operations-rehearsal.md` | Operations Owner | alert/crash/support/backup/incident実演 |
| ART-SECURITY-ASSESSMENT | `security-assessment.md` | Security Owner | residual risk署名 |

## MIG-80 段階展開準備完了

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-ROLLOUT-PLAN | `rollout-plan.md` | Migration Owner | cohort順、entry/exit、停止、version skew、offline端末 |
| ART-SUPPORT-READINESS | `support-readiness.md` | Operations Owner | staffing、severity、SLO、war room、KB、training |
| ART-SIGNED-RELEASE | `signed-release-manifest.json` | Release Owner | 配布物、signature、certificate、SBOM、hash |
| ART-CUTOVER-RUNBOOK〜ART-RESTORE-TEST | cutover/rollback/rehearsal | Migration Owner | 別担当者が無介入で再演 |

## MIG-90 本番展開完了

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-COHORT-LEDGER | `cohort-deployment-ledger.json` | Migration Owner | 全in-scope顧客/cohortがGoまたは正式defer |
| ART-GO-NOGO〜ART-CUTOVER-DECISION | 本番証跡 | Migration/DB/Acceptance Owner | cohortごとにsmoke/DB/telemetry/customer確認 |

## MIG-100 安定運用移管完了

| ID | 成果物 | Owner | 完了条件 |
|---|---|---|---|
| ART-STABILIZATION-SCORECARD | `stabilization-scorecard.md` | Operations Owner | 観測期間中SLO、incident、defect、rollback trigger安定 |
| ART-SERVICE-BOM〜ART-LEGACY-DISPOSITION | 運用/旧系処置 | Operations/Migration Owner | support実演、owner移管、顧客coverage、legacy裁定 |

