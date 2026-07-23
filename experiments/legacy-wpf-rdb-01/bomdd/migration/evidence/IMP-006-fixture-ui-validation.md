# IMP-006 Fixture and UI Evidence Validation

Date: 2026-07-19  
Operator: Experiment Operator (Codex)

## Before control

The frozen pre-change tool was run against two isolated copies of the experiment:

| Negative condition | MIG-10 result | Exit |
|---|---|---:|
| `fixtures/` absent, including `fixtures/baseline/traggo.db` | PASS | 0 |
| `OBS-UI-001-timesheet-empty.png` and `OBS-UI-003-calendar-dom.txt` absent | PASS | 0 |

This reproduced the blind spot: the Gate sealed index documents but did not traverse their fixture/UI evidence references.

## Additional defect found

The three files named `*.png` had JPEG/JFIF bytes. Their SHA-256 values were stable, but their extensions did not describe their actual media type. They were renamed to `*.jpg`; bytes were not transcoded.

## Implemented checks

- fixture and retained restore-copy existence and SHA-256
- SQLite header, live read-only `integrity_check`, `foreign_key_check`, and four canonical `SELECT` results
- DB baseline, schema evidence and observation evidence SHA-256
- exact equality between observation-index IDs and UI-manifest IDs
- required state coverage: empty, populated and alternate-view
- screenshot SHA-256, detected media type, matching extension, dimensions and minimum size
- at least one non-screenshot semantic evidence item per observation
- explicit claim-to-evidence-ID links
- manifest presence in accepted artifact evidence, causing the manifest itself to be content-sealed

## Positive and negative controls

| Control | Result |
|---|---|
| central tool selftest with valid generated SQLite/PNG manifests | PASS |
| remove generated baseline fixture | MIG-10 FAIL; missing fixture detected |
| replace generated UI image bytes | MIG-10 FAIL; hash mismatch detected |
| Traggo fixture manifest semantic validation | no problems |
| Traggo UI evidence manifest semantic validation | no problems |
| frozen project selftest | PASS; files unchanged |

Decision: retest evidence is sufficient to reaccept the affected MIG-10 artifact set and request fresh role approvals.

