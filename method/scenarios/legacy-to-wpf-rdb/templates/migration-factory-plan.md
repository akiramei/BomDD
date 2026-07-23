# Migration Factory Plan

## Workstream operating rules

| Rule | Fixed value |
|---|---|
| Work assignment | `slice-claim` only |
| Worker WIP | profile value, default 1 |
| Review independence | claimant != final reviewer |
| Integration cadence | REPLACE |
| Mainline quality | build, contract, DB, UI and analyzer Green |
| Interface change | producer + all consumers approve |
| Blocker handling | exception command, unrelated safe work only |
| Evidence storage | project-relative, hash-sealed |

## Team onboarding packet

Each workstream receives only: program onboarding, frozen tool/definition, workstream register entry, relevant contracts/BOM/Control Plan, fixture access procedure, claim command, acceptance command, and escalation path.

## Definition of Ready

- Slice exists in register and dependencies are accepted.
- Requirements/spec/BOM/Control Plan/oracle refs resolve.
- Test data and environment are available.
- Interface versions are fixed.
- No open blocker.

## Definition of Done

- Self-tests, contract tests, DB preservation, UI comparison and NFR checks pass as applicable.
- Difference and cheat logs are complete.
- Reviewer accepts evidence.
- As-Built and interface consumption are updated.
- Claim is released only after `as-built`.

