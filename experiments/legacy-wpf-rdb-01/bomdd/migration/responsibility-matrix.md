# Migration Responsibility Matrix

実験では一人の operator が複数 role を兼任する。これは手引きと技術の実証を止めないための明示的な実験条件であり、実案件の職務分離を置き換えない。

| Role | Assigned person/team | Decision scope | Substitute | Evidence/approval method |
|---|---|---|---|---|
| Migration Owner | Experiment Operator (Codex) | scope、順序、模擬 Go/No-Go | Experiment Sponsor | signed Gate result in repository |
| Specification Owner | Experiment Operator (Codex) | preserve/change/legacy-defect ruling | Experiment Sponsor | spec ruling record |
| DB Custodian | Experiment Operator (Codex) | fixture、backup、integrity、writer control | Experiment Sponsor | DB evidence approval |
| WPF Technical Owner | Experiment Operator (Codex) | .NET/WPF/data access/package decisions | Experiment Sponsor | decision record |
| UI Approver | Experiment Operator (Codex) | display、interaction、golden | Experiment Sponsor | UI comparison evidence |
| Acceptance Owner | Experiment Operator (Codex) | oracle、Control Plan、Gate result | Experiment Sponsor | Gate result |
| Migration Worker | Experiment Operator (Codex) | execute one displayed STEP and preserve evidence | none during Run A | handoff record |

Experiment Sponsor はこのタスクの依頼者を指す。日常の Gate は operator が証跡付きで処理し、最終結果と残存リスクを sponsor へ提示する。

