# Migration Program Responsibility Matrix

| Role | Assigned person/team | Decision scope | Substitute | Evidence/approval method |
|---|---|---|---|---|
| Migration Owner | UNASSIGNED | Scope, funding boundary, program stop, final Go/No-Go | UNASSIGNED | Signed program Gate |
| Program Manager | UNASSIGNED | Milestone plan, workstream dependency, WIP, escalation | UNASSIGNED | Program status and handoff |
| Specification Owner | UNASSIGNED | Preserve/change/legacy-defect rulings | UNASSIGNED | Spec ruling record |
| Java Technical Owner | UNASSIGNED | Java/JVM/JavaFX/build/current implementation semantics | UNASSIGNED | Baseline and mapping approval |
| WPF Technical Owner | UNASSIGNED | .NET/WPF/target architecture/data access | UNASSIGNED | Decision record |
| DB Custodian | UNASSIGNED | DB copy, permission, backup, integrity, writer control | UNASSIGNED | DB evidence approval |
| Integration Owner | UNASSIGNED | External systems, files, devices, protocol contracts | UNASSIGNED | Integration contract approval |
| UI Approver | UNASSIGNED | Display, interaction, accessibility, golden | UNASSIGNED | UI approval evidence |
| Acceptance Owner | UNASSIGNED | Oracle, test strategy, Control Plan, Gate result | UNASSIGNED | Acceptance evidence |
| Security Owner | UNASSIGNED | Authn/authz, audit, secrets, crypto, supply chain, risk | UNASSIGNED | Security acceptance |
| Release Owner | UNASSIGNED | CI, artifact, SBOM, signing, installer, update | UNASSIGNED | Release manifest |
| Operations Owner | UNASSIGNED | Monitoring, support, incident, backup, service handover | UNASSIGNED | Operations rehearsal |
| Customer Acceptance Owner | UNASSIGNED | UAT population, customer communication, signoff, training | UNASSIGNED | Customer acceptance ledger |
| Migration Worker | UNASSIGNED | Execute one claimed slice and preserve evidence | UNASSIGNED | Workstream status and handoff |

## Workstream roles

各workstreamは`workstream-register.json`でLead、Reviewer、Acceptance delegateを実名割当する。Leadは複数workstreamを兼務してよいが、同じsliceのWorkerとReviewerを兼務しない。

## Separation rules

- `Migration Owner`と`Customer Acceptance Owner`は本番Go/No-Goで同一人物にしない。
- `Migration Worker`は自分が製造したsliceの`UI Approver`または`Acceptance Owner`として最終承認しない。
- `Release Owner`と`Security Owner`は署名鍵・例外riskの単独承認を兼務しない。
- `DB Custodian`以外に本番writer権限を付与しない。
- 代理行使は事前割当されたSubstituteだけが行い、証跡に代理理由を残す。

Completion rule: `UNASSIGNED` is zero and separation violations are zero before MIG-00 approval.
