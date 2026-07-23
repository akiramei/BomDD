# Version 2.0 Acceptance Record

Date: 2026-07-20  
Scope: `legacy-wpf-rdb` scenario kit  
Decision: Ready to start a controlled enterprise migration program; not a substitute for project-specific MIG-00 through MIG-100 approval

## Intended use

This release is the distribution baseline for a customer-operated, hundreds-of-thousands-of-lines Java/JavaFX system migrating to C#/.NET/WPF while retaining its RDB. It may be installed only by explicit scenario initialization in the target repository. It is not installed into normal BomDD new-development projects.

## Acceptance summary

| Area | Verification | Result |
|---|---|---|
| Entry | Role-specific onboarding selects Program or workstream path in 30 minutes | PASS by document inspection |
| Program position | Twelve ordered milestones from MIG-00 through MIG-100, including MIG-15 and MIG-75 | PASS by definition/heading audit |
| Artifact coverage | 72 scenario templates plus milestone artifact/owner/completion catalog | PASS |
| Basic content | Empty files and unresolved `UNASSIGNED`, `REPLACE`, `TBD`, `TODO`, template expressions and common angle instructions are rejected | PASS automated positive/negative controls |
| Semantic content | Profile, NFR, feasibility, code inventory, workstream, interface, CI, pilot, snapshot, RC, signed release and cohort ledgers are structurally checked | PASS automated positive/negative controls |
| Evidence integrity | Accepted artifact/evidence, approval, exception, decision, slice evidence and snapshot hashes are rechecked | PASS mutation controls |
| Accepted change | Open, retest, reaccept, all-role reapproval, replacement Gate, resume | PASS automated control |
| Exceptions | Catalog, global blocker, authorized safe work, resolution and sealed history | PASS automated control |
| Parallel factory | Two workstreams, three slices, two workers, WIP=1, ordered transitions and independent review | PASS automated simulation |
| Local recovery | Slice block/unblock and claim release/reclaim | PASS automated simulation |
| Aggregate | All-slice as-built snapshot with register/status/evidence integrity | PASS automated simulation |
| Frozen distribution | Copied project-local tool resolves only copied guide/definition/templates and performs read-only selftest | PASS |
| PDF | A4, 48 pages, onboarding + runbook, text extraction with zero replacement glyphs, all-page PNG render and visual inspection | PASS |

Automated command:

```powershell
python method/scenarios/legacy-to-wpf-rdb/tools/migration-workflow.py --selftest
```

Final result on 2026-07-20: `selftest: PASS`.

## Negative controls exercised

- Incomplete MIG-00 and unresolved enterprise profile.
- Direct reacceptance, direct reapproval and reseal bypass.
- Missing DB fixture and changed UI evidence bytes.
- Global blocker allowing no normal STEP work.
- Accepted charter/profile mutation.
- Future technical decision recorded before its due milestone.
- Decision evidence mutation detected by a later Gate.
- Second claim exceeding worker WIP limit.
- Slice transition while a local blocker is open.
- Claim release and reassignment.
- Slice evidence mutation after acceptance.
- Pilot aggregate result changed back to `open`.

## Technology translation basis

The contracts intentionally require explicit treatment of the JavaFX Application Thread versus the WPF Dispatcher, JavaFX property/binding semantics versus WPF data binding/dependency properties, FXML/CSS versus XAML/resources, lifecycle/cancellation, large-control virtualization, accessibility and deployment. These are based on the official [OpenJFX Platform](https://openjfx.io/javadoc/24/javafx.graphics/javafx/application/Platform.html), [OpenJFX binding](https://openjfx.io/javadoc/21/javafx.base/javafx/beans/binding/package-summary.html), [OpenJFX FXML](https://openjfx.io/javadoc/25/javafx.fxml/javafx/fxml/package-summary.html), [WPF threading](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/advanced/threading-model), [WPF data binding](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/data/) and [WPF deployment](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/app-development/deploying-a-wpf-application-wpf) documentation.

## Release boundary

The kit itself is ready to be handed to a project and used from MIG-00. It does not grant production cutover approval to a project. A real project must supply its own source/build/RDB/customer evidence and pass all Gates. In particular:

- MIG-15 must demonstrate the real system's seven risk classes.
- MIG-60 must pass a multi-risk pilot portfolio, not one easy screen.
- MIG-70 must close every registered slice and integrated regression.
- MIG-75 must accept one unchanged RC with customer, operations, security, release and UI owners.
- MIG-80 must rehearse signed cohort deployment and rollback/restore.
- MIG-90 must close every in-scope customer as accepted or formally deferred.
- MIG-100 must meet the full stabilization window and operations handover.

A fresh multi-role human transfer rehearsal through MIG-100 remains a mandatory project adoption exercise. The automated simulation proves control behavior; it does not claim that a real customer system has already been migrated.

## Distribution files

- `onboarding.md` — first page for every participant.
- `migration-runbook.md` — normative execution sequence.
- `milestone-definition.json` — machine Gate definition.
- `enterprise-artifact-catalog.md` — artifact/owner/completion lookup.
- `exception-catalog.md` — fixed exception and recovery paths.
- `tools/migration-workflow.py` — scenario-local workflow and selftest.
- `output/pdf/legacy-to-wpf-rdb-migration-runbook.pdf` — printable distribution copy.
