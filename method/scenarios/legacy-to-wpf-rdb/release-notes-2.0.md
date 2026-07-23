# Version 2.0 Release Notes

Version 2.0 changes the kit from a small controlled migration draft into an enterprise program baseline for an operating Java/JavaFX product.

## Major changes

- Adds MIG-15 technical feasibility and MIG-75 unchanged Release Candidate acceptance.
- Expands completion from one minimal slice to workstreams, all slices, customer cohorts and stabilization.
- Adds Java/JDK/JavaFX/build, NFR, security, operations, dependency, test asset and customer variant baselines.
- Adds Java-to-C# and JavaFX-to-WPF semantic/interaction contracts.
- Adds target architecture, versioned workstream interfaces, CI/test-data/contract-test factory design.
- Adds risk-class pilot, integrated NFR/security acceptance, customer UAT, signed release, support and cohort rollout.
- Adds role separation for Program, Java, WPF, DB, integration, UI, acceptance, security, release, operations and customer owners.
- Adds scenario-local workstream/slice commands with claim, WIP, ordered state, independent review, local blocker and snapshot enforcement.
- Extends Gate checks from file existence/hash to placeholder and critical JSON content validation.
- Extends the exception catalog for Java, feasibility, scale, workstream, security, RC, release, UAT, cohort and operations failures.

## Compatibility

Version 1.3 project status and artifacts are evidence, not proof of Version 2.0 Gate completion. Do not replace a frozen project kit and edit accepted status manually. Review the Version 2.0 milestone delta, use the accepted-change workflow for affected prior artifacts, add the new milestones and approvals under Migration Owner control, and retain every superseded Gate.

## Adoption decision

Use Version 2.0 for new Java/JavaFX-to-WPF migration programs. Existing migration programs must perform a controlled scenario upgrade. Normal new-development projects must not initialize this kit.
