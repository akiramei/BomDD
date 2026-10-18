# Independent inspection brief r1 — BomDD ECO-112 (gates read by the promotion decision; the factory brief kept) — inspector EQ-002

- **Role: inspector.** EQ-002 (Codex CLI). Responsibility: judge whether the manufactured tools and documents implement the order's rules, and whether the
  acceptance evidence shows what the order claims. Range of this round: **境界探索** (boundary exploration — where the rules can be read wrongly, fail open,
  or be stronger in the record than in the code).
- **Target:** BomDD commit `f2d91d4e4eb523ef9970d71e38f2e8a651408770` (the manufacture commit). Report `git rev-parse HEAD` at start and at end (they must be equal; otherwise UNMEASURABLE).
- **Observable prohibitions:** no file in the repository created, changed or deleted (`git status --short` empty at the end), no commit, no network.
  You MAY run, with `python -B`: `method/tools/bomdd-run.py --selftest`, `method/tools/bomdd-job.py --selftest`, `method/tools/bomdd-witness.py --selftest`
  (they use their own temp directories), and small throwaway probes of your own in a temp directory outside the repository.
  Re-running the V3 instrument (`bomdd/reports/eco-112-arm-inventory/arm_inventory_v2.py`) takes about 45 minutes; do it only if you doubt the recorded result.
- **Read:** the order `bomdd/60-change-order-eco-112.md` (the rule register §1, the acceptance §3, the manufacture record §4); the register entry ECO-112 in
  `bomdd/60-change-register.yaml`; the diff `git diff 19243e5c08d7bc11c23d1163e656beb798efdd8e..f2d91d4e4eb523ef9970d71e38f2e8a651408770`; `method/tools/bomdd-run.py` (header R12-R14, `git_common_dir`, `store_brief`,
  `committed_copies`, `decide`, `run`, `summary_line`, the selftest); `method/tools/bomdd-job.py` (header (7), `resolve_required_gates`, `project`, the G2
  arms); `method/templates/60-change-register.yaml`; `method/templates/product-profile/operator-layer.md` §6.1 and adapter A1;
  `bomdd/reports/eco-112-arm-inventory/` (the design evidence and the V3 instrument) and `bomdd/reports/eco-112-arm-inventory/manufacture/` (the manufacture evidence).
- **Report path:** do not write the report yourself; your final message is saved by the harness. Its first non-empty line (after an optional
  `[INFORM / COMPLETE]`) starts with `ACCEPT`, `REJECT` (followed by the finding IDs) or `UNMEASURABLE <reason>`.

## What to check (each item: PASS / FAIL with evidence; a FAIL is blocking or non-blocking)

1. **Scope.** `git diff --stat 19243e5c08d7bc11c23d1163e656beb798efdd8e..f2d91d4e4eb523ef9970d71e38f2e8a651408770` stays inside the order §2's paths; `git diff 19243e5c08d7bc11c23d1163e656beb798efdd8e..f2d91d4e4eb523ef9970d71e38f2e8a651408770 -- method/tools/bomdd-witness.py` is empty.
2. **G1-G5 against the code.** The order line rule (column 0, outside fences and HTML comments, exactly one), the equality of the register field and the
   line as sets, the shape checks, the projection (`required_gates` with its source); the promotion check only in state verified, its order (R11, then
   GATES_UNDECLARED, then REQUIRED_GATE_MISSING by exact name), what the decision record carries, and that only declared exits are read (G4).
3. **B1-B5 against the code.** `--brief` required with `--cell` and refused without it, `none` with `--report` refused, these checks after every existing
   argument check; the store written only after ADVANCE for a launching invocation and before the decision record; the CR refusal; the existing-file
   re-hash; temp file + `os.replace` and the accept-if-it-now-matches rule; the re-read; `BOMDD_BRIEF`; at promotion, only 64-hex names, re-hash, ignored
   left-overs listed, copies looked up in the tree the decision binds under `bomdd/reports/`, `brief_copies` recorded.
4. **O1.** `entry_code` separate from the witness `code`; each new code tagged in the first line; lines within 80 columns.
5. **T1-T6.** Every `--cell` call of the selftest carries a valid `--brief`; refusal arms check a reason unique to themselves (T2); the two arms named in
   T3 reach their own reasons and the `unlink` is guarded; each new rule has an arm that goes red for its own reason (the manufacture evidence records rule
   mutations); the selftest keeps the shape T5 requires.
6. **The acceptance evidence.** V1-V3 as recorded in §4 and in `bomdd/reports/eco-112-arm-inventory/manufacture/`: do the recorded runs show what V1-V3 require?
   V3's pinned-instrument run on the manufactured tool is still running at this commit; its result is not in this round (say so in "Not checked").
7. **Boundary exploration (the main work of this round).** Look for inputs where the new rules read wrongly or fail open, for example: an empty list,
   whitespace or case variants in IDs, duplicate gate names in the witness, a `required_gates:` line inside an indented block or a quote, a brief that is a
   directory or a symlink, a store directory that is a file, `bomdd/reports/` absent from the tree, a blob with the same size and other bytes, many files
   under `bomdd/reports/`, a linked worktree, a relative `--brief` path, a brief outside the repository, a cell that deletes its own stored brief.
8. **Records.** The order's §4 and the register entry claim nothing that the code or the evidence does not show; the declared limits (L1-L9) are honest.

## Report format (your final message, in full)

```
[INFORM / COMPLETE]

ACCEPT            ← or REJECT IA-01, IA-02, … / UNMEASURABLE <reason>

- inspector: EQ-002 / Codex CLI / <model>
- HEAD at start / at end: <sha> / <sha>
- commits: 0 / files changed: 0
- selftests run: bomdd-run <first line>, bomdd-job <first line>, bomdd-witness <first line>

## Items
| # | item | verdict | evidence (file:line, command and the key output) |

## Findings (IA-01, IA-02, …)
- each: blocking / non-blocking, where, what is wrong, a suggested repair

## Not checked (limits)
```
