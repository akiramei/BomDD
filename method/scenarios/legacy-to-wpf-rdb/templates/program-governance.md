# Migration Program Governance

## Cadence and records

| Event | Fixed cadence/trigger | Required attendees | Input | Output artifact | Decision SLA |
|---|---|---|---|---|---|
| Program Gate | milestone completion | required approvers | accepted artifacts | Gate result | before advance |
| Workstream integration | REPLACE | Leads, Release, Acceptance | claimed slice status | integration log | REPLACE |
| Interface change | proposed change | producer/consumer owners | interface evidence | versioned ruling | REPLACE |
| Customer change | scope/behavior/outage change | Migration/Customer owners | impact evidence | customer ruling | REPLACE |
| Production incident | severity threshold | Operations bridge | telemetry | incident record | REPLACE |

## Escalation tree

| Severity | Objective trigger | First owner | Escalate after | Escalation owner | Work allowed while open |
|---|---|---|---|---|---|
| S0 | safety/security/data loss or production corruption | REPLACE | immediate | REPLACE | stop all writes |
| S1 | critical path blocked or rollback unavailable | REPLACE | REPLACE | REPLACE | authorized safe work only |
| S2 | one workstream blocked | REPLACE | REPLACE | REPLACE | unaffected claimed slices |
| S3 | non-blocking discrepancy | REPLACE | REPLACE | REPLACE | continue with exception |

## Change lanes

| Lane | Allowed content | Branch/repository | Approval | Release destination |
|---|---|---|---|---|
| LEGACY-FIX | production Java maintenance only | REPLACE | Java/Operations | current production |
| MIGRATION | behavior-preserving WPF migration only | REPLACE | Workstream/WPF/Acceptance | migration RC |
| NEW-FEATURE | approved new capability | REPLACE | Product/customer change control | separately scheduled |

Never merge lanes without a traceable change record and regression scope.

## Workstream rules

- One slice has one workstream and one active claimant.
- WIP is limited by `migration-profile.json`.
- Shared interface changes require producer and every registered consumer approval.
- A worker does not approve their own final acceptance.
- Integration branch accepts only self-accepted slices with evidence.
- Program Manager may reorder slices only with dependency and customer impact evidence.

## Stop conditions

- Production data changed by a migration test.
- Required rollback cannot be completed inside the approved window.
- Unknown customer variant or unsupported client version reaches a rollout cohort.
- Signing identity, SBOM, security acceptance, or release hash is missing.
- Program status and workstream status disagree.

