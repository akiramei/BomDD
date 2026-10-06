# ECO-VT-229 - independent fresh-context review

One round, by a reviewer started with no context from the manufacturer's session. Read-only in the repository; everything it executed
ran in a scratch copy (`git archive HEAD` plus the working-tree runner). **[RAN]** = a command was run and its output quoted;
**[REASONED]** = read from the files only. Summarised here by the manufacturer.

## Round 1 - 2026-10-06 - PASS WITH FINDINGS (no blocking; two major)

Reviewed state: HEAD `2bb5574f` with the uncommitted repair of `tools/run-supervised-tests.ps1` written by the first `impl229.py`
(the parameter, its guard, the argument pair with its comment).

- **R229a-F1, MAJOR [RAN].** The manufacturer had run `selftest_supervised_tests.py --argument-contract-only` without `--result`,
  and the tool's default output path is ECO-VT-061's committed evidence file
  (`test-results/eco-vt-061-sandbox-mtp-routing/argument-contract-result.json`): its `runId` had become `ad-hoc`, the static list 11
  instead of 6, the control inventory hash changed, a post-seal block added. Reproduced in scratch. Not in the ECO's scope.
- **R229a-F2, MAJOR [REASONED].** The Control Plan read-across accepted under ECO-VT-215 says, for every watchdog, timeout or
  ceiling over inspection equipment: decide on a sign of progress the equipment's own output gives, keep a wall-time backstop, and
  qualify both cuts with controls made from outside. This repair is the wall-time ceiling only, on the manufacturer's proposed
  default that the user accepted; the progress-sign form was available (prepare-run writes a diagnostic log that grows per listed
  node); and the body's "a stalled listing still stops" had no control. The runner's own listing of the parameter end to end was
  also unchecked.
- **R229a-F3, MINOR [RAN].** `supervisor-report.json` records `ceilingSeconds` and `idleSeconds` (ECO-VT-215) but not the
  discovery limit; additive keys are safe (finalize-run and validate read named keys only).
- **R229a-F4, MINOR [RAN].** The self-test's static checks do not assert the runner passes `--discovery-timeout-seconds`; a
  regression that drops the argument surfaces only as a preparation failure on the next full run (fail-closed, loud).
- **R229a-F5, MINOR [RAN].** The body's claim about the installed-asset pins is verified (hash domain git-blob = sha256 of
  `git show HEAD:<target>`; the supervisor's pin equals the blob at `fe4c65ee`, the two disposition pins the blob at `2fdf48de`;
  broken by `7af96469`, ECO-VT-220, which records nothing about pins). `qualify_process_transplant.py` would FAIL on them, but the
  hooks run it only when specific policy or tool files are staged. ECO-VT-215 named ECO-VT-176 (staged) as the owner of pin
  mismatches; the body did not.
- **R229a-F6, MINOR [RAN].** Units mixed in the body: 1072 and 1060 are node counts (1071 and about 1059 tests).
- R229a-F7, INFO [REASONED]: at any limit a stalled listing ends the same way - the child is killed, exit 1, the runner throws
  outside its try/catch, nothing sealed, the run directory holds the diagnostic log only; the 900 s ceiling does not cover
  preparation. Pre-existing. R229a-F8, INFO [RAN]: `[int]` binding rounds `1.9`, as the existing parameters do.

### What the reviewer verified

- [RAN] The diff is exactly the three hunks; `impl229.py` reproduces it. `Parser::ParseFile` gives 0 errors. The argument array with
  the trailing comma before comment lines is valid and evaluates to 12 elements ending `--discovery-timeout-seconds | 120`.
- [RAN] The guard: `0` and `-5` throw `DiscoveryTimeoutSeconds must be at least 1.`; `abc` is refused by binding; omitted, the
  default reaches the executable check. The self-test's argument contract passes 11/11 in scratch.
- [RAN] The body's numbers against the two cut runs' diagnostic logs (1054 and 1060 nodes), the last completed inventory (1072
  nodes, 1071 tests, 11.9 s) and `probe-before.txt`. Line references in the body are correct. No document states the 15 s limit,
  so no documentation sentence is needed.
- [REASONED] The two cut runs of ECO-VT-228 consumed no retest attempt (the reservation comes after the listing). R3: nothing in
  the runner's diff is outside the ECO; the out-of-scope mutation was F1 only.

### Not verified by the reviewer

- The repaired runner against the real executable (a full run or a lowered-limit control) - route policy; the manufacturer's.
- `qualify_process_transplant.py` was not executed; its FAIL on the pins is read from its code.
- Whether 120 s is sufficient on other machines; only this machine's 11.9 to 15.4 s listings exist.

### Disposition (the manufacturer, 2026-10-06)

- **F1: restored** from HEAD (`git checkout`); the self-test re-run with `--result` into this ECO's record directory
  (`selftest-argument-contract.json`). The overwritten file is not in the commit.
- **F2: recorded, and the cut-side control added.** The form is the one the user ruled (the stated default of the question answered
  「A」); the body says the progress-sign form of the read-across was not taken and remains a candidate. The control
  (`cut-control-after.txt`): the repaired runner with `-DiscoveryTimeoutSeconds 1` stops in the preparation with
  `timed out after 1 seconds` after 2 s and 44 nodes, nothing sealed - which also shows the parameter wired through the runner.
- **F3: repaired** (`discoveryTimeoutSeconds` in the report, one additive line; `impl229.py` revised).
- **F4: accepted and recorded** - the self-test file is not in this ECO's scope, and the failure mode is fail-closed.
- **F5, F6: the body corrected** (`record229.py`). F7, F8: recorded; no change.
