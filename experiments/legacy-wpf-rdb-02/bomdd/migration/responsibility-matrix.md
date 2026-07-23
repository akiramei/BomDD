# Migration Responsibility Matrix — EXP-LWR-002

実験では一人のoperatorが複数roleを兼任する。これはclient-server経路の実証を止めないための条件であり、実案件の職務分離を置き換えない。

| Role | Assigned person/team | Decision scope | Substitute | Evidence/approval method |
|---|---|---|---|---|
| Migration Owner | Experiment Operator (Codex) | scope、順序、模擬Go/No-Go | Experiment Sponsor | Gate result |
| Specification Owner | Experiment Operator (Codex) | preserve/change/legacy-defect ruling | Experiment Sponsor | ruling record |
| DB Custodian | Experiment Operator (Codex) | server、role、dump、restore、writer control | Experiment Sponsor | DB evidence approval |
| WPF Technical Owner | Experiment Operator (Codex) | .NET/WPF/data access | Experiment Sponsor | decision record when due |
| UI Approver | Experiment Operator (Codex) | representative current observation | Experiment Sponsor | UI evidence approval |
| Acceptance Owner | Experiment Operator (Codex) | oracle、Gate result | Experiment Sponsor | Gate result |
| Migration Worker | Experiment Operator (Codex) | execute one displayed STEP | none during experiment | handoff record |

Experiment Sponsorはこのタスクの依頼者を指す。
