# Customer Acceptance Contract

## Representative population

| UAT cohort | Represents customers/versions/devices | Required workflows | Data/environment | Witness | Entry | Exit/signoff |
|---|---|---|---|---|---|---|
| UAT-001 | | | | | | |

## Acceptance dimensions

| Dimension | Required evidence | Approver | Failure action |
|---|---|---|---|
| Business workflow parity | FUNC oracle and witnessed script | Customer Acceptance Owner | return slice |
| UI/keyboard/accessibility | display contract comparison | UI Approver | return UI slice |
| Performance/volume | NFR result | Acceptance Owner | block RC |
| Install/update/config | clean and existing device results | Release Owner | block RC |
| Security/audit | security assessment | Security Owner | block RC |
| Operations/support | alert/incident/backup rehearsal | Operations Owner | block rollout |
| Training/help/release notes | approved material and attendance | Customer Acceptance Owner | block cohort |

Silence is not acceptance. Every required cohort needs a named witness, date, result, and evidence hash.

