[INFORM / COMPLETE]
REJECT IA-14 IA-15

1. FAIL (blocking) — IA-12 is repaired, but IA-13 remains incomplete and the copy-drift common cause remains for other I2 rules.
2. PASS — Both diff ranges stay within `diff_audit.allowed_paths`; unchanged manufactured files retain their blobs; all four rehearsals exit 0 and are byte-identical; real-data results are unchanged; IA-01–IA-11 remain resolved; V1/V2 passes 123/123 and the `11982a4` control fails 121/123 on the two bounds-rule copies.
3. FAIL (blocking) — All 47 README SHA-256 entries match committed bytes and the diff/register history agrees, but §12, the register, and `repair-r4/README.md` overstate the red-first runner and common-cause repair.

## Findings

### IA-14 — blocking — the red-first runner accepts the wrong historical setup

Location: `repair-r4/redfirst_all.py:46-59,104-107`; order `bomdd/60-change-order-eco-115.md:627-631`; `repair-r4/README.md:5,18-20`.

Evidence: `decision_control()` requires the expected misses to be present but does not reject additional misses or otherwise identify the staged revision. A throwaway probe requested the r2 control for `2aa2d7d` while deliberately making `git_show()` stage `35961c3` instead. It returned:

```text
PASSED_BROKEN_SETUP exit 1; 14 MISSED; expected missing none; expected lines absent none
```

Thus a wrong setup passes as the r2 control merely because its larger failure set contains the three required r2 prefixes. By contrast, removing the shared parser from the C5 setup was correctly rejected with `ModuleNotFoundError`; setup verification is therefore partial.

Direction: declare the complete expected failure set for each historical revision and require exact agreement, while also rejecting unexpected stderr/setup failures and proving the staged revision’s identity.

### IA-15 — blocking — the copy-drift common cause remains for other I2 domains

Location: order `bomdd/60-change-order-eco-115.md:110-129,620-623`; playbook `method/bomdd-playbook-v1.md:207-219`; template `method/templates/33-control-plan.yaml:21-25,38-41,51`; V1 `manufacture/check_v1_v2.py:133-135,167-191`.

Evidence: the bounds rule now has a playbook-derived canonical sentence and checked copies. Other closed I2 values remain independently repeated in the order, playbook, template comments, and hard-coded V1 lists. In an external scratch copy, I changed only the template’s `approver` copy from:

```text
automated | human:<role> | automated+human:<role>
```

to the same text plus `| maintainer`. V1/V2 still exited 0 at 123/123 because it checks required substrings and does not reject the extra value. This reproduces the same class as IA-12: a template copy departs from the canonical I2 rule while V1 remains green.

Direction: derive every copied closed vocabulary from its canonical playbook text, or enforce exact parsed sets with negative arms for added and removed values.

## Run record

- Start HEAD: `460dc6b4f0bd3127f4766be25e5b99009acfe0ee`
- End HEAD: `460dc6b4f0bd3127f4766be25e5b99009acfe0ee`
- Start/end BomDD status: empty.
- End ViewPrism2 and MoviePad-Remake statuses: empty.
- Repair-only range: 18 changed paths, all allowed.
- All-repairs range: 45 changed paths, all allowed.
- Current V1/V2: exit 0, 123/123.
- `11982a4` control: exit 1, 121/123, failing both stale bounds copies.
- Four rehearsals: exit 0 and byte-identical to their committed outputs.
- Current red-first runner: reports 5/5 signatures, but its evidence is disqualified by IA-14.
- README hashes: 47/47 match.

## Preflight receipt

Classification: bug-fix/continuation inspection. Target specimen, prior failures, expected behavior, current work state, and acceptance target were confirmed from the brief, order, register, and r1–r4 reports. Decision: PROCEED. Overrides: none.

## Calibration receipt

- Bounds-copy repair: observed and qualified within the tested sentence and `11982a4` control.
- IA-13 repair claim: observed but evidence not qualified because IA-14 permits a wrong revision to pass.
- Common-cause removal claim: observed but evidence not qualified because IA-15 demonstrates another unchecked I2 copy.
- Regression claim for IA-01–IA-11: observed and qualified within the fixed revisions and four permitted rehearsals.
- Instrument defects: IA-14 and IA-15.
- Battery: Q1–Q7 asked; Q8 NA; Q9–Q11 asked.
- Detection limits: no shipped product integration, non-git delivery, remote CI, or exhaustive setup-mutation set was tested.

## Out of range observations

- `git diff --check` reports historical trailing whitespace in `inspection-r4.md:58`; it does not affect this verdict.
- Sibling status checks emitted global-ignore permission warnings but returned no status entries.

## Not examined

- V4 self-conformance and remote CI.
- The older v1 rehearsal and basis-only measurement scripts.
- Product behavior beyond the fixed revisions used by the four rehearsals.
- Mechanical enforcement after distribution.

Reasoning effort: not exposed to the inspector.

human_action: none for this inspection. Execution: COMPLETE — r5 repair confirmation and regression inspection finished; under §12, the REJECT returns ECO-115 to human disposition.