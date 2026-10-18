# ECO-112 loop 3 — inventory of the selftest calls that `--brief` affects (design evidence)

Ruling: user, 2026-10-18, "A" (third loop), on the condition that the common cause of the loop-2 findings L2R2-2 and L2R3-1 (existing arms listed
from memory) is removed before review resumes: (1) extract mechanically every existing test and call site that adding `--brief` affects;
(2) check the extraction against the existing tests and repair what the list missed; (3) check that each test passes or fails for the reason it
was meant to; (4) record the result as design evidence, then resume review.

## What was measured

- **Tool measured:** `method/tools/bomdd-run.py` at `3a9de06`, sha256 `b028bc534e0e24299d7f868bf1283c83c44f52ae08df2fda5cd5d4524a23d0e7`
  (also in the JSON's `source_sha256`).
- **Instrument:** `arm_inventory.py` (this directory), run as `python -B arm_inventory.py <bomdd-run.py> out` on Windows 11, CPython 3.13.
  - Step 1 (static): `ast` over `_selftest_body`; every `call(...)` whose argv can contain `"--cell"` — a list literal, a loop over a tuple of list
    literals, or a builder expression (`arm()`).
  - Step 2 (dynamic + cross-check): the whole selftest run once with `run` wrapped; every invocation logged (caller line, arm name, argv with paths
    normalised, exit, first output line); static sites compared with dynamic calls.
  - Step 3 (mutation, one call at a time): for each dynamic call with `--cell` and no `--brief`, the whole selftest re-run with only that call
    answering as ECO-112's new rule would (`UNMEASURABLE ARG_ERROR: --cell requires --brief`, exit 2). The selftest's own failure list was read;
    failures appended between this call and the next are this call's own check. **OWN** = its own check noticed; **MASKED** = its own check passed
    although the call failed for the new rule's reason; **CRASH** = the selftest raised.
- **Instrument calibration:** the unmutated run under the instrument passes (`ADVANCE OK: selftest PASS…`, 73 calls). A first attempt ran the
  instrument with `python -I`, which hid the user site-packages (PyYAML) and made every call `MISSING_INPUT`; that run was discarded (every arm
  CRASH, baseline red) and is not part of this evidence.

## Results (`summary.txt`, `arm-inventory.json`)

- **Static ↔ dynamic: 12 call sites, 56 calls with `--cell`, no gap** (`static_not_executed: []`, `dynamic_not_in_static: []`).
  Per site (selftest line: static sites → dynamic calls): 552 builder → 17; 583 → 1; 640 (`rep_arm`) → 12; 677 → 1; 682 → 1; 689 → 1;
  709 loop 10 → 10; 723 loop 3 → 3; 732 → 5 (loop over ECO strings); 742 → 1; 748 → 1; 758 loop 3 → 3.
- **Mutation: 56 calls → OWN 29, MASKED 26, CRASH 1.**
  - MASKED (their own check passes when the call fails for the new rule's reason): the arm `kb-no-eco` (552); `stale` (677); `dirtarget` (682);
    all 10 `rep-arg` calls with `--cell` (709); the 3 `ind-arg` calls (723); the 5 `kb-eco-syntax` calls (732); `kb-ledger-unwritable` (742);
    `kb-ledger-inside` (748); 3 of the argument arms (758: `["--cell", x]`, `["ECO-900", "--cell"]`, the duplicated value). They check only that the
    first line starts with `UNMEASURABLE ARG_ERROR` / `UNMEASURABLE`, or read the ledger's last decision, which a refused call does not write.
  - CRASH: the `IA-01` cell-exit-7 call (689) — its report file is never written and a later `unlink` raises; the selftest goes red, but not through
    the call's own check.
- **A defect that exists today (found by the instrument, before any change):** `kb-ledger-unwritable` (742) and `kb-ledger-inside` (748) pass
  **for another reason at baseline** — their first line is `--cell には --executor EQ-NNN が必須`, because the calls lack `--executor` and the
  executor check (ECO-072) fires before the ledger checks they were written for. Their own reasons (an unwritable ledger, a ledger inside the
  worktree) are not exercised.

## What the design takes from this (ECO-112 §1-3)

1. Every one of the 56 calls is listed by site; each gains a valid `--brief` (a fixture brief where `--report` is set, `none` elsewhere), so that each
   refusal keeps coming from its own check.
2. The `--brief` requirement is checked after every existing argument check, so a missing `--brief` never hides another argument error.
3. Every arm that expects a refusal asserts its own reason (the code or message fragment in the first line), not only the verdict prefix.
4. The two arms that pass for another reason today get `--executor`, so their own reason fires.
5. Acceptance (V3) runs `arm_inventory_v2.py` on the manufactured tool: the cross-check has no gap, and with **every** `--cell` call answering in turn
   as the brief rule would (refused first, no ledger record), 0 MASKED and 0 CRASH. v2 differs from v1 only in its targets (every `--cell` call, with or
   without `--brief`; review finding L3R1-1: v1's targets — calls without `--brief` — would be empty after manufacture, so V3 could not go red).
   On the tool measured here no call has `--brief`, so v2's targets equal v1's 56. v2's fake refusal is the marker
   `UNMEASURABLE ARG_ERROR(INSTRUMENT_MUTATION): …`, which no real bomdd-run message contains (grep over `method/tools/*.py`: 0), so an arm whose own
   reason is the brief rule is not satisfied by it (review finding L3R2-1; v1's line was worded like the rule itself).
   **A baseline that is not clean is never a pass** (user condition, 2026-10-18; review L3R3-2): v2 first runs the unmutated selftest, and if its exit is
   not 0, it raised, or it recorded any failure, v2 writes `verdict: UNMEASURABLE_BASELINE`, runs no mutation, and exits 2. v2's own exit is 0 only for
   PASS (no gap, every target OWN), 1 for FAIL. **Guard checked with a known-bad input** (2026-10-18): v2 run under `python -I` (which hides PyYAML and
   turns the baseline red, as in the discarded first run) → `UNMEASURABLE_BASELINE … no mutation was run`, exit 2.
6. The cell-exit-7 arm's `unlink` of its report is guarded, so a refused call is reported by the arm's own check instead of crashing the selftest
   (review finding L3R1-2).

## Files

| file | sha256 |
|---|---|
| `arm_inventory.py` | `c2cec1d80005b39278c95aa002056ae73b48bb5659336c095d545e87a19fb649` |
| `arm-inventory.json` | `bac000ad6f4482e826e013988acb86afaca1501c8f2657dd0ed875cef6e66bb5` |
| `summary.txt` (LF; see the note below) | `d21f266ce8a0f607196bb2c2f28f2fc12b20de925a5debdac0dcd434601dc0b6` |
| `arm_inventory_v2.py` (the V3 instrument; not yet run) | `7abaa22324ccd7b07ce73c317142938b1fbc5777653519edc77b74073ee2e6e1` |

Note (2026-10-18, after the filing commit): `summary.txt` was first written with CRLF line ends (a redirected `print` on Windows), and the filing
commit recorded the CRLF bytes' sha256 (`5e67d902…`) while the repository's `eol=lf` rule committed LF. The file was normalised to LF and the table
now gives the committed bytes' sha256. The content is otherwise unchanged (`git diff` of the file is empty).
