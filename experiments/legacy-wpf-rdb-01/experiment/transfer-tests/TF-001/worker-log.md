# TF-001 Worker Log

## Scope and identity

- Entry point: `packet.md`.
- Project root: `C:\Users\akira\source\repos\BomDD\experiments\legacy-wpf-rdb-01\experiment\transfer-tests\TF-001\project`.
- Assigned synthetic approver name: `TF-001 Assigned Team`.
- Intervention count: 0.

## Commands and results

1. Command: `Get-Content -Raw -LiteralPath '...\TF-001\packet.md'` (working directory `C:\Users\akira\source\repos\BomDD`).
   Result: exit 0. Established the bounded goal, allowed sources and changes, prohibited changes, assigned approver name, logging rules, and requested completion report.
2. Command: `rg --files '...\TF-001\project'; Get-ChildItem -LiteralPath '...\TF-001' -Force | Select-Object Name,Length,Mode`.
   Result: exit 0. Confirmed the project contains `bomdd/migration/migration-status.json`, the frozen workflow tool, onboarding/runbook/templates and MIG-10 evidence inputs; confirmed `packet.md`, `source-facts.md`, and the `project` directory beside this log. No sibling experiment or central method file was inspected.
3. Command: `Get-Content -Raw -LiteralPath '...\project\bomdd\migration\guide\onboarding.md'; Get-Content -Raw -LiteralPath '...\TF-001\source-facts.md'` (working directory: Project root).
   Result: exit 0. Read the onboarding entry and supplied source facts in full.
4. Command: `python bomdd/migration/tools/migration-workflow.py status --project-root '...\TF-001\project'; python bomdd/migration/tools/migration-workflow.py next --project-root '...\TF-001\project'`.
   Result: exit 0. Scenario `legacy-wpf-rdb`; last passed `MIG-00`; current `MIG-10`; current STEP `STEP-013`; owner `TF-001 Assigned Team`; blockers/open exceptions 0; unaccepted `ART-DB-BASELINE` and `ART-CURRENT-OBS`; current action `DB 基準線を作る`; next `STEP-014 現行観測を固定する`.
5. Command: `rg -n --hidden "MIG-10|STEP-013|STEP-014|accept-artifact|approve|handoff" bomdd/migration/guide/migration-runbook.md; Get-Content ... migration-profile.json; Get-Content ... responsibility-matrix.md; Get-ChildItem ... .templates; Get-Content ... baseline-fixture-manifest.json; Get-Content ... current-ui-evidence-manifest.json`.
   Result: exit 0. Located the relevant runbook sections; confirmed all MIG-10 roles map to `TF-001 Assigned Team`; read both installed templates and confirmed their required `REPLACE-*` fields.
6. Command: `$lines = Get-Content ... migration-runbook.md; $lines[70..205]; $lines[322..404]`.
   Result: exit 0. Read the daily start/end workflow, artifact/approval sealing rules, mandatory manifest checks, and complete STEP-013/STEP-014 instructions. Required order: manifest creation, Gate recheck, artifact acceptance with manifest evidence, required approvals, Gate check, and normal handoff.
7. Command: `Get-Content -Raw -LiteralPath '...\TF-001\worker-log.md'`.
   Result: exit 0. Re-read this log after an administrative patch context mismatch; no project artifact or workflow state was affected.
8. Command: `Test-Path ... baseline-fixture-manifest.json; Copy-Item ... .templates/baseline-fixture-manifest.json ... evidence/baseline-fixture-manifest.json; Get-FileHash ...`.
   Result: exit 0. Destination did not exist (`False`); copied the installed template into the evidence directory and computed its initial SHA-256.
9. Command: `Get-Content -Raw ... baseline-fixture-manifest.json | ConvertFrom-Json | Out-Null; python ... check --milestone MIG-10`.
   Result: exit 0. The new baseline manifest parsed as JSON. Gate remained FAIL only because both artifacts were still `present` with empty accepted-evidence lists and the three required approvals were absent; exception seals and zero-blocker checks passed. Tool directed staying at STEP-013.
10. Command: `python ... complete-step ... --evidence bomdd/migration/evidence/baseline-fixture-manifest.json; python ... status ...`.
   Result: exit 0. Completed STEP-013 and advanced exactly one STEP to STEP-014. Current action became `現行観測を固定する`; blockers/open exceptions remained 0; both MIG-10 artifacts remained unaccepted as expected.
11. Command: `Get-Content -Raw -LiteralPath 'bomdd/migration/current-observation-index.md'`.
   Result: exit 0. Confirmed exactly three required IDs, their empty/populated/alternate-view states, evidence paths, screenshot hashes, and the requirement that the manifest seal every screenshot and semantic evidence file.
12. Command: `Test-Path ... current-ui-evidence-manifest.json; Copy-Item ... .templates/current-ui-evidence-manifest.json ... evidence/current-ui-evidence-manifest.json; Get-FileHash ...`.
   Result: exit 0. Destination did not exist (`False`); copied the installed template into the evidence directory and computed its initial SHA-256.
13. Command: `Get-Content -Raw ... current-ui-evidence-manifest.json | ConvertFrom-Json | Out-Null; rg -n "REPLACE-" ... both manifests; python ... check --milestone MIG-10`.
   Result: exit 0. UI manifest parsed as JSON; placeholder search returned no matches. Gate remained FAIL only for the still-unaccepted two artifacts and absent three approvals; exception seals and zero-blocker checks passed. Tool directed staying at STEP-014.
14. Command: `python ... complete-step ... --evidence bomdd/migration/evidence/current-ui-evidence-manifest.json; python ... status ...; python ... next ...`.
   Result: exit 0. Completed STEP-014 and moved to `GATE-MIG-10`. Status/next showed no blockers or open exceptions, two unaccepted artifacts, Gate action, and `advance` only after PASS.
15. Command: `Get-Content -Raw ... TF-001-MIG-10-preparation-review.md; python ... accept-artifact --help; python ... approve --help`.
   Result: exit 0. Confirmed organizer-prepared source scope and that the fresh worker must create/validate manifests, accept both artifacts, record three approvals, pass MIG-10, and hand off. Confirmed each acceptance/approval command takes one evidence path.
16. Command: `python ... accept-artifact ... --artifact ART-DB-BASELINE --evidence bomdd/migration/evidence/baseline-fixture-manifest.json`.
   Result: exit 0. Frozen tool accepted `ART-DB-BASELINE`, which validated and sealed the DB semantic manifest and its referenced evidence.
17. Command: `python ... accept-artifact ... --artifact ART-CURRENT-OBS --evidence bomdd/migration/evidence/current-ui-evidence-manifest.json`.
   Result: exit 0. Frozen tool accepted `ART-CURRENT-OBS`, which validated and sealed the UI semantic manifest and its referenced evidence.
18. Command: three `python ... approve` invocations for roles `Migration Owner`, `DB Custodian`, and `UI Approver`, each with approver `TF-001 Assigned Team` and its new role-specific evidence file.
   Result: exit 0. Frozen tool recorded all three required MIG-10 approvals.
19. Command: `python ... check --project-root '...\TF-001\project' --milestone MIG-10`.
   Result: exit 0. `MIG-10 現行基準線確定: PASS`; all four required artifacts, all three approvals, exception seals, and zero-active-blocker checks passed.
20. Command: `python ... handoff --project-root '...\TF-001\project'`.
   Result: exit 0. Wrote normal workflow handoff `bomdd/migration/handoffs/handoff-20260719T094604Z.md`.
21. Command: `python ... status ...; Get-Content ... handoff-20260719T094604Z.md; Get-Content ... gates/MIG-10-result.json; Get-ChildItem ... approval files; Get-Item ... created files`.
   Result: mixed. Status succeeded and confirmed current `MIG-10` / `GATE-MIG-10`, blockers 0, open exceptions 0, unaccepted 0, and no advance. Handoff read succeeded and contains the required resume command. All three new approval files and both manifests/handoff were present. Attempts to read/list `gates/MIG-10-result.json` failed because `check` does not create that file before `advance`; no file was fabricated.
22. Command: `Get-ChildItem ... bomdd/migration/gates; Get-ChildItem ... bomdd/migration/handoffs`.
   Result: exit 0. Gates contains only the pre-existing `MIG-00-result.json`; handoffs contains the new `handoff-20260719T094604Z.md`.
23. Command: `python bomdd/migration/tools/migration-workflow.py check ...; git status --short -- '...\TF-001'` from repository root.
   Result: the relative Python path failed because the working directory was intentionally outside Project root; scoped Git status reported the organizer's entire TF-001 directory as untracked and therefore was not useful for per-file attribution. No workflow state changed.
24. Command: absolute frozen-tool path `check --milestone MIG-10`; absolute frozen-tool path `status`.
   Result: exit 0. Final Gate result remained PASS. Final position remained `MIG-10` / `GATE-MIG-10`, with blockers 0, open exceptions 0, unaccepted 0, and `Next: advance Gate PASS 後に次のマイルストーンへ進む`. `advance` was not run.

## File actions

- Created `bomdd/migration/evidence/baseline-fixture-manifest.json` from the installed `.templates` file, then replaced its placeholders using only the DB fixture values and four canonical queries in `source-facts.md`.
- Created `bomdd/migration/evidence/current-ui-evidence-manifest.json` from the installed `.templates` file, enumerated the three index observations, and added each supplied screenshot/semantic evidence item and its separately supported supplied claim.
- Created new role-specific local approval evidence for Migration Owner, DB Custodian, and UI Approver after both artifacts were accepted.
- Created `bomdd/migration/handoffs/handoff-20260719T094604Z.md` with the frozen tool.
- Created this `worker-log.md` beside the packet.

## Document sections used

- `packet.md`: Goal; Observation rules; Completion report.
- `onboarding.md`: sections 1 (safety card), 2 (run `status` and `next` without reinitializing), 3 (status interpretation), 5 (MIG-10 STEP-013/014 template paths), 6 (complete-step and re-check status), 8 (handoff), and 9 (onboarding completion conditions).
- `source-facts.md`: DB fixture fields and canonical queries; UI observation fields and claims.
- `migration-runbook.md`: sections 1.1 (daily start), 1.2 (daily end), 2 (role separation), 3.1-3.2 (milestone/Gate and sealing workflow), 5 STEP-013, and 5 STEP-014.
- `migration-profile.json` and `responsibility-matrix.md`: owner assignments and MIG-10 approval authority.
- `.templates/baseline-fixture-manifest.json` and `.templates/current-ui-evidence-manifest.json`: exact manifest shapes to fill.
- `current-observation-index.md`: complete observation ID set, required state mapping, evidence closure, and index-to-manifest requirement.
- `TF-001-MIG-10-preparation-review.md`: organizer-prepared boundary and the remaining fresh-worker tasks.

## Uncertainties

- Whether `check --milestone MIG-10` should also create `bomdd/migration/gates/MIG-10-result.json`. Final inspection showed no MIG-10 Gate file. This does not block the packet: the frozen tool returned PASS twice, onboarding/runbook require `check` PASS followed by `advance`, and the packet explicitly prohibits `advance`. The worker therefore did not fabricate a Gate file or run `advance`.

## Interventions

- None.

## Completion

- Result: PASS.
- Final position: `MIG-10` / `GATE-MIG-10`.
- MIG-10 Gate: PASS.
- Intervention count: 0.
- Exact replacement-worker command from the handoff: `python C:\Users\akira\source\repos\BomDD\experiments\legacy-wpf-rdb-01\experiment\transfer-tests\TF-001\project\bomdd\migration\tools\migration-workflow.py next --project-root C:\Users\akira\source\repos\BomDD\experiments\legacy-wpf-rdb-01\experiment\transfer-tests\TF-001\project`
