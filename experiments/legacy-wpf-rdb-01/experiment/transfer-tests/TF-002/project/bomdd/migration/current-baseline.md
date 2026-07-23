# Current System Baseline

Frozen: 2026-07-19  
Owner: Experiment Operator (Codex)

## Source and build

| Item | Frozen value | Evidence |
|---|---|---|
| Repository | `https://github.com/traggo/server.git` | `experiment/source-lock.json` |
| Commit/tag/branch | `6321119c3c2d55f04e2e4967f6492aabd6067b76` / `v0.8.3` / `master` | `experiment/source-lock.json` |
| Dirty state | clean; Git printed only an inaccessible user-global ignore warning | `bomdd/migration/evidence/baseline-build.log` |
| Source build | not run: Go and Docker absent; no source repair performed | `bomdd/migration/exceptions/EX-BASELINE-001-20260719.md` |
| Executable origin | official Windows amd64 release asset for the identical tag/commit | `bomdd/migration/evidence/baseline-build.log` |
| Artifact hash | ZIP `a7cac6...cd8b7`; EXE `1bef82...4d0b4` | `experiment/source-lock.json` |
| Configuration version | release `.env.sample` SHA-256 `55cbf1...96c9e`; secrets excluded | `bomdd/migration/evidence/baseline-build.log` |
| Startup result | local port 3030, HTTP 200, login and representative operations pass | `bomdd/migration/evidence/baseline-build.log` |

Known generation: GraphQL Go and TypeScript generation exists in Makefile. It is part of the frozen source lineage but is not rerun because the official release asset is the accepted execution original.

## Runtime environment

| Item | Value | Evidence |
|---|---|---|
| OS/architecture | Windows, win-x64, OS build 10.0.26200 | `bomdd/migration/evidence/environment-inventory.md` |
| Original runtime | self-contained `traggo.exe` v0.8.3 | `bomdd/migration/evidence/baseline-build.log` |
| Database | SQLite file, engine observed with SQLite CLI 3.49.1 | `bomdd/migration/db-baseline.md` |
| Original config | process-scoped `TRAGGO_*`; values containing credentials are not frozen | `bomdd/migration/evidence/baseline-build.log` |
| Target toolchain | .NET SDK 10.0.100 and WPF runtime 10.0.x | `bomdd/migration/evidence/environment-inventory.md` |

## Current behavior observations

The complete index is `bomdd/migration/current-observation-index.md`.

| Observation ID | Use case | Result | DB observation | Evidence |
|---|---|---|---|---|
| OBS-CURRENT-001 | login and empty list | navigation and list UI displayed | default user/device created | `OBS-UI-001-timesheet-empty.jpg` |
| OBS-CURRENT-002 | tag + start/stop timer + list | `project:experiment`, six-second span | one tag definition, span, span tag | `OBS-UI-002-timesheet-list.jpg` |
| OBS-CURRENT-003 | calendar | span appears in current week | same canonical span | `OBS-UI-003-timesheet-calendar.jpg` plus calendar DOM extract |

## Unresolved questions

No MIG-10 blocker. Dashboard/error/concurrency observations are required before those feature slices, and will be enumerated at MIG-20 then contracted at MIG-30.
