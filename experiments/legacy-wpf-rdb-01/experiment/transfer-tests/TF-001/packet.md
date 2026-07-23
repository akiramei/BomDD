# TF-001 Fresh Worker Transfer-Test Packet

You are the fresh migration worker. Use only this packet, `source-facts.md`, and files under the Project root. Do not inspect sibling experiments or central method sources. Do not use prior conversation context.

Project root:

```text
C:\Users\akira\source\repos\BomDD\experiments\legacy-wpf-rdb-01\experiment\transfer-tests\TF-001\project
```

Assigned role name for every synthetic approval in this isolated test:

```text
TF-001 Assigned Team
```

## Goal

Starting from the project’s own onboarding entry, complete only the remaining MIG-10 work:

1. determine the current position with the frozen tool;
2. complete STEP-013 and STEP-014;
3. create both semantic manifests from the installed `.templates` files using the supplied facts;
4. accept the two remaining artifacts;
5. record all required MIG-10 approvals with new local evidence;
6. make `check --milestone MIG-10` PASS;
7. do not run `advance`;
8. create a normal workflow handoff.

## Observation rules

- Record every command, its result, every document section used, and every uncertainty in `worker-log.md` beside this packet.
- If you cannot decide the next action from the packet/onboarding/runbook/tool output within five minutes, append an intervention request to `worker-log.md` before asking the organizer.
- Do not edit `migration-status.json`, the frozen tool, definition, guide, or template files.
- Do not modify fixture, restore copy, screenshots, DOM, schema, DB observation, baseline, or observation index.
- You may create manifests, review/approval evidence, command logs and the tool-generated handoff/status/Gate records.
- Treat this as an isolated synthetic test; no production system exists.

## Completion report

When finished, report:

- PASS or BLOCKED;
- final milestone and STEP;
- MIG-10 Gate result;
- intervention count;
- uncertainties encountered;
- files created;
- the exact next command a replacement worker should run.

