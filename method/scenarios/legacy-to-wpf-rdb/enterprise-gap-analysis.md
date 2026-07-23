# Version 1.3 → 大規模Java/JavaFX実運用案件 ギャップ監査

監査日: 2026-07-20  
対象: 数十万行、複数チーム、複数顧客が実運用中のJava/JavaFX + RDBシステムを.NET/C# + WPFへ移行する案件

## 判定

Version 1.3は、成果物Gate、証跡seal、例外処置、受入後変更、SQLite/PostgreSQLの基準線、限定handoffに強い。一方、現在の実証はMIG-10までであり、大規模案件に必要なprogram統制、Java/JavaFX意味差、複数workstream、顧客受入、段階展開、運用移管が機械Gateになっていない。

したがってVersion 1.3をそのまま本番移行標準にはしない。以下をVersion 2.0の必須成果物とGateへ昇格する。

## 必須ギャップ

| ID | 領域 | Version 1.3の不足 | 追加する成果物/Gate | 期限 |
|---|---|---|---|---|
| GAP-001 | 規模宣言 | LOC、module数、画面数、顧客数、利用者数をGateしない | `program-profile.json`、規模閾値、適用mode | MIG-00 |
| GAP-002 | program統制 | 単一owner中心で、workstream lead、release、security、operations、customerの責任がない | program RACI、代理、decision SLA、escalation tree | MIG-00 |
| GAP-003 | 顧客保護 | 顧客業務時間、停止許容、SLA、規制、データ区分が開始条件でない | customer/operations boundary | MIG-00 |
| GAP-004 | 現行build | Maven/Gradle、JDK、JavaFX、annotation processor、native library、JVM optionを凍結しない | Java build/runtime baseline | MIG-10 |
| GAP-005 | 非機能基準線 | 起動、UI応答、memory、CPU、DB round-trip、batch時間を固定しない | NFR baseline manifest | MIG-10 |
| GAP-006 | security基準線 | 認証、認可、監査、秘密、暗号、証明書、権限境界を固定しない | security baseline | MIG-10 |
| GAP-007 | 配布/運用基準線 | installer、update、端末管理、config、user profile、support手順を固定しない | deployment/operations baseline | MIG-10 |
| GAP-008 | 技術実現性 | 全設計後までWPF/DB/installerの致命的障害が分からない | high-risk feasibility portfolio | MIG-15 |
| GAP-009 | source全数性 | source-mapがLOC/module/resource/generated/reflection/nativeを集計しない | machine-readable code inventory | MIG-20 |
| GAP-010 | JavaFX全数性 | FXML、CSS、controller、binding、Task/Service、WebView、Swing interop等を数えない | JavaFX surface inventory | MIG-20 |
| GAP-011 | third-party置換 | Java library/pluginからNuGet/.NET/自作への置換ownerとlicenseがない | dependency replacement ledger | MIG-20 |
| GAP-012 | 顧客差分 | customer別config、feature flag、schema差、version skewを数えない | customer variant matrix | MIG-20 |
| GAP-013 | test資産 | JUnit/UI test/manual test/test dataの再利用・置換方針がない | test asset inventory | MIG-20 |
| GAP-014 | Java/C#意味差 | null、例外、generics、collection、decimal、time、thread、serializationの契約がない | Java→C# semantic contract | MIG-30 |
| GAP-015 | JavaFX/WPF意味差 | Application Thread/Dispatcher、Property/Binding、FXML/XAML、CSS/style、event/focus差を裁定しない | JavaFX→WPF interaction contract | MIG-30 |
| GAP-016 | 非機能契約 | baselineから許容劣化、負荷、soak、leak、accessibility目標を決めない | NFR acceptance contract | MIG-30 |
| GAP-017 | security契約 | threat、authz parity、audit、secret、supply chain、vulnerabilityの受入条件がない | security acceptance contract | MIG-30 |
| GAP-018 | 並行開発 | workstream境界、owner、依存、interface freeze、WIP、merge順がない | workstream register/dependency graph | MIG-40 |
| GAP-019 | build/release factory | CI agent、reproducible build、signing、SBOM、artifact retention、branch/release trainがない | build/release architecture | MIG-40 |
| GAP-020 | 観測可能性 | log、metric、trace、crash dump、correlation、PII除外の設計がない | observability design | MIG-40 |
| GAP-021 | workstream状態 | feature statusが手書きで、複数team集約・不正遷移・重複claimを検査しない | program-control tool + sealed workstream manifest | MIG-50〜70 |
| GAP-022 | pilot wave | 一スライスだけでは高リスクsurfaceを代表しない | risk-class別pilot portfolio | MIG-60 |
| GAP-023 | release candidate | customer UAT、security、performance、installer、upgrade、support rehearsalの独立Gateがない | MIG-75 Release Candidate Gate | MIG-75 |
| GAP-024 | 段階展開 | 一回の切替を前提とし、顧客cohort、version skew、offline端末、rollback windowを扱わない | rollout ledger/cohort runbook | MIG-80〜90 |
| GAP-025 | support/hypercare | severity、SLO、staffing、war room、telemetry threshold、legacy fallbackが不足 | support readiness + stabilization scorecard | MIG-80〜100 |
| GAP-026 | 完全移管試験 | fresh worker試験がMIG-10限定 | 複数roleでMIG-00〜MIG-60、その後MIG-75/80 rehearsal | 手引き受入 |

## Version 2.0の進行モデル

| Milestone | 到達状態 | 大規模案件で追加する判断 |
|---|---|---|
| MIG-00 | program開始可能 | 顧客保護境界、規模、RACI、承認分離 |
| MIG-10 | 現行基準線確定 | Java/JavaFX/build/security/NFR/deploymentを凍結 |
| MIG-15 | 技術実現性確認 | 最難関UI、DB provider、installer、性能、third-partyをspikeで実測 |
| MIG-20 | 全数棚卸し・workstream分割完了 | source/JavaFX/test/dependency/customer variantを100%分類 |
| MIG-30 | 互換契約確定 | Java/C#、JavaFX/WPF、DB、NFR、security、customer acceptance |
| MIG-40 | target/factory設計完了 | architecture、CI/release、observability、workstream interface |
| MIG-50 | migration factory準備完了 | oracle、test data、contract test、team onboarding、claim可能状態 |
| MIG-60 | pilot wave合格 | risk-classを代表する複数slice、clean install、運用観測 |
| MIG-70 | 全workstream統合完了 | 全slice as-built、回帰、NFR/security、残差裁定 |
| MIG-75 | Release Candidate受入 | customer UAT、operations/security/support承認 |
| MIG-80 | 段階展開準備完了 | cohort、署名、配布、backup/restore、rollback、support rehearsal |
| MIG-90 | 本番展開完了 | cohort単位のGo/rollback、全顧客ledger、DB/telemetry照合 |
| MIG-100 | 安定運用移管完了 | SLO安定、support引継、legacy処置、残存risk owner |

## 手引き完成条件

1. 上記26ギャップが、説明だけでなく必須成果物または機械検査へ割り当てられている。
2. 作業者が自分のworkstreamとclaim済みsliceを`status`コマンドで特定できる。
3. 同じsliceを二teamが同時に製造できない。
4. program Gateは全workstreamの状態、証跡hash、blocker、interface versionを集約する。
5. Java/JavaFX固有の移植判断を自由設計せず、mapping matrixを上から埋められる。
6. 顧客本番接続、配布、署名、cohort切替は通常製造commandから分離される。
7. freshな複数roleがMIG-00〜MIG-60を無介入で実行する。
8. MIG-75/80のrelease/cutover rehearsalを別環境で再演する。
9. 配布PDFを全ページ検査し、Markdown正本と同じVersionにする。

