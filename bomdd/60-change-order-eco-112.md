# Change Order — ECO-112 (the operator layer's two connection gaps: check results read by the promotion decision, and the factory brief kept and re-fetchable)

> Ruling: user, 2026-10-18, "1:A 2:A 3:A" on the evaluation of an external proposal ("AI製造と外部ワークフロー制御の分離").
> The proposal's skeleton (the AI manufactures and reports; something outside decides from the ledger whether to advance) is the operator layer
> BomDD built and ran in ECO-062 to ECO-074. The three real needs each map to one missing line in that layer.
>
> Conditions the user added to the completion conditions (verbatim in substance):
> - ① Not only the mapping between control-plan row IDs and checkers: **the check results must actually be read by the advance decision**, and that is an acceptance condition.
> - ② Besides the factory brief's SHA-256, **keep a reference from which the original content can be re-fetched**.
> - Design convergence is judged by the default rule (two consecutive rounds with zero new findings). **No manufacture while unconverged.**
> - **No new workflow engine, no LLM wiki, no context access control.** Use the existing operator layer and fill only the gaps found.
>
> Split ruling: user, 2026-10-18, "B" after the first design loop ended unconverged at its limit (15→11→6; material 11→7→2; item ③ produced most
> findings, the two round-3 material ones from a hand-made mutex). Item ③ (in-flight runs, duplicate launches) moved to **ECO-113**, designed
> independently and in parallel, not deferred. ①② continue "as connections to the existing contract" under the default convergence rule; the
> split relaxes neither ECO's convergence rule; manufacture of each starts after its own design converges.
> Second loop: rounds counted afresh with the default limit of 3, because the scope changed (as in ECO-111's narrowing). Loops 3-5 are extensions
> ruled by the user (each with its conditions, recorded in the receipt). Loop 5 (this text): each rule has one canonical place (§1's rule register) and
> is referred to elsewhere by its ID; the parts of V1 and V2 observable only after the promotion decision moved to closure (V7, V8).
>
> Records are English-primary.

## Equipment

- Filing and design: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- producer: EQ-004
- inspector: EQ-002
- Converge round reviewer: a fresh context of the same model (context independence), read-only, resumed each round.
- Independent inspection: EQ-002 (Codex), because the change is machine behaviour in the promotion decision (precedent: ECO-062, ECO-072 to ECO-074).

## 0. Basis (measured at baseline `3a9de06`)

- **Gap ① — the promotion decision does not read which checks were run.** `bomdd-run.py` decides ADVANCE when the witness verifies
  (every declared gate's declared exit is 0), the job's stop type is NONE and, for a launch, independence holds (R3, R9). Nothing compares the
  witness's gate names with the checks the ECO declared: a witness holding one gate `self-conformance=0` advances an ECO whose acceptance lists
  V1 to V4. The gate name is a free string (`bomdd-witness.py:103-114`, `:373-388`). No tool under `method/tools/` reads a control plan
  (grep: 0 hits). Verified promotion is decided by a dry run with the job in state verified (R11, `bomdd-run.py:216`); R11's inspection check
  is at `:246-248`.
- **Gap ② — the brief is not kept.** The run ledger's decision record holds the worktree tree and the cell command
  (`bomdd-run.py:185-188`); the cell record holds the report's sha256 (R10, `:283-290`). The brief a cell reads is not hashed or kept.
  Briefs are kept outside the worktree at launch time, because an untracked brief inside it changes the tree and the witness stops with TREE_MISMATCH
  (ECO-102 lesson).
- **Open ECOs at baseline:** ECO-079 (implemented) only. No register entry has `required_gates`.

## 1. Change request — the rule register

**Each rule below is the canonical text of that rule; every other section of this order refers to it by its ID and does not restate it**
(user ruling "1:A", 2026-10-18: the common cause of the loop-4 findings was one rule written in several places). Groups: **G** gates read by the
promotion decision (user condition ①), **B** the brief (user condition ②), **O** output, **T** selftests, **M** manufacture.

### G — check results read by the promotion decision (Gap ① in §0)

- **G1 — the declared set.** A register entry may carry `required_gates: [ID, ...]`: the check IDs whose results the promotion decision must read
  (control-plan row IDs `CP-*` in a product; the order's acceptance IDs `V*` and `inspection` in this repository). The order carries the same list on
  exactly one line that starts with `required_gates:` at column 0, outside fenced blocks and HTML comments (the fence and comment handling bomdd-job
  already uses for the equipment lines, `bomdd-job.py:73-79`). The order is the ruling record and the register field is its machine copy. Changing the
  set after filing means changing the order's line, with the ruling that changes the acceptance written next to it, and the register field together.
  The register template (`method/templates/60-change-register.yaml`) documents the field.
- **G2 — bomdd-job's projection.** bomdd-job projects `required_gates` with its source coordinate; absent in both → `null`, source `none`. Any of these
  → `LEDGER_INCONSISTENT` (ledger-derivable): not a list of non-empty strings; a duplicate ID; more than one G1 line in the order; the order's line
  absent or unparsable while the field is present, or the reverse; the two lists not equal as sets.
- **G3 — the promotion check.** Only when the job's state is verified (the promotion decision; R11's anchor), after the witness verifies ADVANCE, `decide()`
  applies, in this order: (1) R11 unchanged — an inspector declared and no `inspection` gate → `STOP INSPECTION_MISSING`; (2) the field absent or empty
  → `UNMEASURABLE`, code `GATES_UNDECLARED`; (3) every ID of the set (`inspection` included) must equal, as an exact string, the name of a gate in the
  witness, else `UNMEASURABLE`, code `REQUIRED_GATE_MISSING`, naming the IDs. Codes (2) and (3): stop type `MISSING_INPUT`, delivery operator.
  A red gate is refused by the witness as today (every gate must exit 0); gates beyond the set are allowed. The decision record carries
  `required_gates` and the matched gate names. In other states the set is not checked, so factory and inspection cells launch before their gates exist.
- **G4 — what "read" means.** The decision reads each required gate's **declared** exit in the witness and does not re-run the check (witness W2, limit
  (2)); re-measurement stays the acceptance side's duty. A control-plan row keeps `fixture` and `oracle` as its mapping to the checker; the only new
  convention is that the row's witness gate is named by the row's `id`.
- **G5 — operator-layer.md.** The core gets the description convention only (a gate is named by its check row ID; the register's `required_gates`, equal
  to the order's line, lists them; an absent field is not a pass). The sentence that a mechanism reads them goes to the adapter A1 (the core claims no
  mechanism, §7).

### B — the brief kept and re-fetchable (Gap ② in §0)

- **B1 — the option.** `--brief PATH|none` is required with `--cell` and refused without it (`ARG_ERROR` either way); `none` with `--report` →
  `ARG_ERROR` (a reporting cell is an inspection or factory cell and has a brief); `none` alone declares a cell with no brief and is recorded.
  These checks run **after every existing argument check**, so a missing or misplaced `--brief` never hides another argument error.
- **B2 — the store.** `<git-common-dir>/bomdd-run/briefs/<ECO>/<sha256>`: one directory per ECO, one file per distinct brief named by its sha256
  (64 lowercase hex); one store per clone whatever `--ledger` says and whichever worktree runs; outside every worktree. It is written only after
  `decide()` returns ADVANCE for a launching invocation, before the decision record and before the cell starts; a refused invocation stores nothing.
  Steps: read the bytes; a brief containing `\r` → `BRIEF_NOT_LF` (the repository declares `* text=auto eol=lf`, so a CRLF brief would be committed
  as other bytes); compute sha256; an existing store file is re-hashed and must match; otherwise write a `.tmp-<random>` file in the same directory and
  `os.replace` it to the final name; a failed replace is accepted if the final name now exists and re-hashes to its name; re-read the stored file and
  compare. Any failure → the decision becomes `UNMEASURABLE` before the decision record is written (code `BRIEF_UNREADABLE`, `BRIEF_NOT_LF` or
  `BRIEF_STORE_FAILED`, stop type `MISSING_INPUT`, delivery operator), and nothing launches.
- **B3 — the record.** The decision record carries `brief: {path, sha256, size, store_ref}`; `store_ref` is the stored file's path, the reference from
  which the original bytes are re-fetched on this clone. The cell receives `BOMDD_BRIEF` = that path. The store directory's 64-hex files are the set of
  briefs launched for the ECO on this clone (no index file).
- **B4 — the committed copy, checked at promotion.** When the job's state is verified, after G3, `decide()` lists the ECO's store directory, takes only
  64-hex names and re-hashes each (bytes not matching the name → `BRIEF_STORE_FAILED`); other entries (left-over `.tmp-*`) are ignored and listed in the
  decision record. Every stored brief must exist in the tree the decision binds (the witness-verified worktree tree, `rec.tree`) under `bomdd/reports/`
  with the same sha256 — found with `git ls-tree -r <tree> -- bomdd/reports/`, read with `git cat-file blob`. Otherwise `UNMEASURABLE`, code
  `BRIEF_NOT_COMMITTED` (naming the sha256 prefixes); a store directory that cannot be listed → `BRIEF_STORE_FAILED`; stop type `MISSING_INPUT`,
  delivery operator. The decision record gets `brief_copies: [{sha256, path, tree}]`. **The lasting reference is `{sha256, path}`**; `tree` only binds
  the pair to this decision (an unreferenced tree object can be pruned). The decision record is clone-local, so **at closure the order's closure section
  (the canonical record) copies the `{sha256, path}` pairs** — for every ECO whose cells ran with a brief.
- **B5 — the command.** The command string is not altered (R5).

### O — output

- **O1 — codes and the first line.** The codes from G3 and B (`GATES_UNDECLARED`, `REQUIRED_GATE_MISSING`, `BRIEF_*`) go in a field of their own,
  `entry_code`; the existing `code` keeps the witness code. The first output line (R7) gets a tag per new code (as `INSPECTION_MISSING` has,
  `bomdd-run.py:345-363`), so it never reads as the witness's `OK`.

### T — selftests (derived from the recorded inventory, not from memory)

**Evidence:** [`bomdd/reports/eco-112-arm-inventory/`](reports/eco-112-arm-inventory/README.md) — an `ast` extraction of every selftest call that can
carry `--cell`, the dynamic log of one selftest run, their cross-check, and a one-call-at-a-time mutation, measured on `bomdd-run.py` at `3a9de06`
(sha256 `b028bc53…`): **12 call sites, 56 calls with `--cell`, no gap; 29 calls noticed by their own check, 26 MASKED, 1 CRASH**; two existing
arms (`kb-ledger-unwritable`, `kb-ledger-inside`) pass today for another reason (their calls lack `--executor`, so the ECO-072 executor check refuses them first).

- **T1 — the 56 calls.** Each of the 56 calls, by site (the evidence lists them), gains a valid `--brief`: a fixture brief where `--report` is set (the R10
  report arms, `stale`, `dirtarget`, the cell-exit arm, the `rep-arg` loop), `none` elsewhere. Dry invocations get no `--brief`.
- **T2 — own reasons.** Every arm that expects a refusal asserts its own reason in the first line (and, where it reads the ledger, that a record for this
  call exists), not only the verdict prefix. Where a code is shared by several reasons (`ARG_ERROR`), the arm checks a message fragment unique to its own
  reason; a code alone suffices only where it names the reason (`BRIEF_NOT_LF`, `REQUIRED_GATE_MISSING`, …).
- **T3 — existing defects repaired.** The two arms that pass for another reason today get `--executor`, so their own reasons fire; the cell-exit-7 arm's
  `unlink` of its report is guarded (`missing_ok=True`, `bomdd-run.py:693`), so a refused call is reported by that arm's own check, not by a crash.
- **T4 — new arms.** Each of G1-G3, B1-B4 and O1 gets a known-bad arm that goes red for that rule's own reason (the observations are listed in §3 V1 and
  V2). The selftest fixtures (ECO-900 to ECO-905) are given `required_gates` (register and order line) where their state is verified.
- **T5 — the shape the V3 instrument reads** is a constraint on the manufactured selftest: (a) the body stays in a function named `_selftest_body`;
  (b) every invocation goes through its local helper `call`, each argv written as a list literal (or a loop over a tuple of list literals, or the `arm()`
  builder) containing `"--cell"` literally where it launches — no argv held in, or concatenated from, another variable; (c) new arms are added inside
  `_selftest_body` (directly or through `arm()`/`rep_arm()`); (d) failures are appended to its local list `fails`; (e) no real message contains
  `INSTRUMENT_MUTATION`. An instrument crash or a static/dynamic gap caused by a change of shape is **cannot measure**, not a pass, and is resolved by
  restoring the shape, not by editing the instrument.
- **T6 — the V3 instrument's scope.** It sees in-process `call(...)` invocations inside `_selftest_body`; a launch from a thread or a child process is
  outside it.

### M — manufacture

- **M1 — order.** ECO-112 is manufactured first, then ECO-113 (ECO-113's order refers to this rule); ECO-113 rebases its manufacture on ECO-112's
  verified head. So V3 is measured on a selftest that ECO-113's arms have not yet changed; ECO-113's acceptance covers its own arms. Both change
  `bomdd-run.py`, `bomdd-job.py` and `operator-layer.md`.

### Declared limits (each refers to the rule it limits)

- **L1 (G4):** declared exits, not re-measured ones. Whether a `required_gates` set is the right set is the filer's and the inspector's judgement.
- **L2 (G1, G2):** a change of the set after filing is not detected mechanically — bomdd-job checks that the order and the register agree, not that they
  still say what they said at filing; a change to both without a ruling is caught only by reading the order's history (inspection, diff audit).
- **L3 (G3):** ECO-079 (open, no field) stops with `GATES_UNDECLARED` at its promotion until its owner writes the field and the order's line.
- **L4 (B2, B4):** the store is clone-local; on another clone B4 sees an empty store and checks nothing. A brief deleted from the store by hand is outside
  the trust boundary (like deleting the witness, ECO-046).
- **L5 (B2):** on Windows, `os.replace` onto a store file another invocation holds open can fail; B2's accept-if-it-now-matches covers the same-bytes
  case, and anything else fails closed. This is the one place where ①② meet concurrency, which is ECO-113's.
- **L6 (B5):** whether the cell actually read the declared brief is not proven by the record.
- **L7 (T1-T5):** the bomdd-run and bomdd-job selftests are not run in CI (CI runs the witness selftest); they are run locally and recorded (V3).
- **L8:** in-flight runs and duplicate launches are ECO-113's.
- **L9 (B4):** the closure section's copy of the `{sha256, path}` pairs is a closure duty that no tool checks; after ECO-112 (whose V8 checks it once), it is
  practice, not a mechanism. If it is skipped, the pairs stay only in the clone-local decision record.

### Not changed

- `bomdd-witness.py`, `self-conformance.py`, hooks, `.github`, the playbook, skills, `.claude/skills`, the control-plan template.
- Machine distribution to product repositories (EXP-20260914-01 stays suspended). Products get the register-template comment (G1) and the
  operator-layer text (G5) through the kit as usual.
- No scheduler, workflow engine, LLM wiki or context access control (user condition).

## 2. No-impact prediction (before manufacture; frozen at filing)

- **The diff:** `method/tools/bomdd-run.py`, `method/tools/bomdd-job.py`, `method/templates/60-change-register.yaml`,
  `method/templates/product-profile/operator-layer.md`, `method/improvements.md`, this order, the register, and `bomdd/reports/eco-112-*/`
  (briefs and reports).
- **Not touched:** `method/tools/bomdd-witness.py`, `method/tools/self-conformance.py`, hooks, `.github`, the playbook, skills, `.claude/skills`,
  `method/templates/33-control-plan.yaml`.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, inspection]

**Gated** (read by the promotion decision under G3): V1, V2, V3, and V5 as the gate `inspection` (R11). **Checked at closure** (observable only after the
promotion decision): V4, V6, V7, V8. Each item below lists what is observed and what passes; the mechanism is the cited rule's.

- **V1 — G1-G3 and O1, selftest arms** (user condition ①): condition =
  (a) verified job, set `[V1, V2]`, gates V1=0 and V2=0 → ADVANCE;
  (b) gates V1=0 only → exit 2, `REQUIRED_GATE_MISSING` naming V2, and the decision record lists required and matched;
  (c) field absent → `GATES_UNDECLARED`; (d) a gate named `v2` → V2 missing;
  (e) a job not in state verified, V2 missing → the cell launches;
  (f) an inspector declared, `inspection` in the set, no `inspection` gate → `STOP INSPECTION_MISSING`, exit 1;
  (g) no inspector declared, `inspection` in the set, no such gate → `REQUIRED_GATE_MISSING`;
  (h) bomdd-job: the order's line and the register field differ, one is missing, or the order has two such lines → `LEDGER_INCONSISTENT`; a line inside
      a fence or an HTML comment is not read;
  (i) regression: gates V1=0, V2=1 → `STOP GATE_FAIL`;
  (j) each new code's first line carries its own tag, and the record's `code` still holds the witness code.
- **V2 — B1-B4, selftest arms and the re-fetch before promotion** (user condition ②): condition =
  (a) the decision record's sha256 equals the brief's; `store_ref` exists and its bytes equal the brief;
  (b) an existing store file with other bytes → `BRIEF_STORE_FAILED`; a missing brief → `BRIEF_UNREADABLE`; a CRLF brief → `BRIEF_NOT_LF`;
  (c) `--cell` without `--brief`, `--brief` without `--cell`, and `--brief none` with `--report` → `ARG_ERROR`, each with its own message fragment;
      `--brief none` without `--report` recorded as none; an invocation with both a bad `--report` path and no `--brief` → `ARG_ERROR` with the
      `--report` message fragment, not the `--brief` one (B1's ordering);
  (d) a refused launch (job STOP, witness STOP, INDEPENDENCE_FAIL) leaves the store empty; two worktrees (or two `--ledger` values) store into the same place;
  (e) at promotion: a stored brief with no copy in the bound tree → `BRIEF_NOT_COMMITTED`; a copy at `HEAD` but deleted or changed in the worktree →
      `BRIEF_NOT_COMMITTED`; a copy in the bound tree → passes and `brief_copies` names its path and tree; a store file whose bytes do not match its
      name → `BRIEF_STORE_FAILED`; a left-over `.tmp-*` file is ignored and listed;
  (f) **real cells, before promotion:** the independent-inspection cells for this ECO run with `--brief`, and each brief re-fetched from its `store_ref`
      has the sha256 the ledger records.
- **V3 — T1-T6:** condition = the existing selftests of bomdd-run, bomdd-job and bomdd-witness pass (run locally and recorded);
  `git diff -- method/tools/bomdd-witness.py` is empty; the V3 instrument `bomdd/reports/eco-112-arm-inventory/arm_inventory_v2.py`
  (sha256 `7abaa223…`, fixed at filing), run on the manufactured `bomdd-run.py`, **exits 0 (PASS)** — which requires its unmutated baseline to be clean
  (a baseline that is not clean exits 2 and is never a pass; user condition) — with no static/dynamic gap and, with every `--cell` call answering in turn
  as the brief rule would, 0 MASKED and 0 CRASH; the two arms of T3 show their own reasons in their first lines.
- **V4 (closure)**: condition = self-conformance exits 0, observed before each commit; CI green on each pushed revision.
- **V5**: condition = independent inspection by EQ-002, ranges 境界探索 then 是正確認+回帰; ACCEPT, as the gate `inspection` (R11).
- **V6 (closure)**: condition = inside the diff window, only the paths in §2.
- **V7 (closure; V1's real run)**: condition = ECO-112's verified promotion was decided by bomdd-run (dry) under G3, and that decision record lists
  V1, V2, V3 and `inspection` as matched.
- **V8 (closure; V2's real run)**: condition = that same promotion decision passed B4 for every brief in ECO-112's store, and, as B4 requires, the closure
  section of this order lists their `{sha256, path}` pairs, each pair checked against the committed file.

## 4. Manufacture (2026-10-18, user "1:A": manufacture approved)

**Inputs fixed** (sha256 prefixes; `git show <rev>:<path>`):
- the design: this order at `d762270` (`5b9e89cb5e0a`), filed and converged; the register entry at `d762270`;
- the tools at the filing baseline `3a9de06`: `bomdd-run.py` `b028bc534e0e`, `bomdd-job.py` `b17fc26ffb12`, `bomdd-witness.py` unchanged;
  the templates `60-change-register.yaml` `d011a2ad9760`, `product-profile/operator-layer.md` `8647981f35bb`;
- the V3 instrument `bomdd/reports/eco-112-arm-inventory/arm_inventory_v2.py` `7abaa22324cc` (fixed at filing).
- **ECO-113's undecided changes are not mixed in**: its draft order was moved outside the worktree before manufacture started and stays there; no
  ECO-113 rule (lock, journal, Job Object, `RUN_IN_FLIGHT`) is in this diff.

**What changed, by rule:** `bomdd-job.py` — G2 (`resolve_required_gates`, the `required_gates` field, header (7)); `bomdd-run.py` — G3 and G4 in `decide()`
after R11 (header R12), B1 in `run()` after every existing argument check, B2/B3 (`store_brief`, `BOMDD_BRIEF`), B4 (`committed_copies`, after G3),
B5 (the command is passed unaltered as before), O1 (`entry_code`, the first-line tag; header R14), T1-T4 in the selftest; the register template — G1's
comment; operator-layer.md — G5 (core §6.1, adapter A1).

**Acceptance measured before the manufacture commit** (evidence: `bomdd/reports/eco-112-arm-inventory/manufacture/`):
- **V1 (G1-G3, O1) — PASS (selftest arms).** bomdd-run: `g3-all-matched`, `g3-missing` (first line `REQUIRED_GATE_MISSING(V2)`, `code` still `OK`),
  `g3-undeclared`, `g3-case`, `g3-no-inspector-inspection`, `g3-regression-gate-fail`, `g3-not-verified-launches`; R11 first (`insp-verified-gate-missing`).
  bomdd-job: nine G2 arms (equal / differ / field missing / line missing / two lines / unparsable / duplicate / not strings / both absent; lines inside a
  fence, an HTML comment or mid-line are not read).
- **V2 (B1-B4) — selftest arms PASS:** `b-store` (sha256, size, `store_ref` bytes, `BOMDD_BRIEF`), `b-none-recorded`, `b-fail` × 3
  (`BRIEF_STORE_FAILED`, `BRIEF_UNREADABLE`, `BRIEF_NOT_LF`), `b-arg` × 4 (no `--brief`; `--brief` without `--cell`; `none` with `--report`; the two-fault
  call answering with the `--report` reason), `b-refused-stores-nothing` (witness STOP, job STOP, INDEPENDENCE_FAIL), `b-other-ledger-same-store`,
  `b-worktree-same-store`, `b-promotion-not-committed`, `b-promotion-copy` (`brief_copies`, the ignored `.tmp-left`), `b-promotion-head-only`,
  `b-promotion-store-mismatch`. V2(f), the real cells, is observed with the independent inspection.
- **Rule mutations (T4's "red for its own reason"), 4/4 detected:** G3 switched off → 16 failures naming `g3-`; B4 switched off → 7 naming
  `b-promotion`; the CR refusal off → `BRIEF_NOT_LF`; the `--brief` check moved before the other argument checks → the two-fault arm. (The first attempt
  at the last one inserted the check after the `--report` checks, so it was no mutation; corrected and re-run.)
- **V3 — the existing selftests PASS:** bomdd-run (`ADVANCE OK: selftest PASS…`), bomdd-job, bomdd-witness; `git diff -- method/tools/bomdd-witness.py`
  empty. **The pinned instrument's run on the manufactured `bomdd-run.py` is still running** (91 targets, about 2-3 hours); its result is recorded in a
  later commit, before the promotion decision.
- **Found during manufacture (recorded, not in this ECO's design):** OBS-20261018-01 — bomdd-job finds an order's closure only under a Japanese heading
  (クローズ), so the English-primary ECO-110 and ECO-111 already project as `LEDGER_INCONSISTENT` at `3a9de06`. This order's closure heading therefore
  carries クローズ, so that its own promotion (V7) is not stopped by that reader.

## 収束 receipt (converge self-application)

### Loop 1 (before the split; ①②③ together)

- **判定: 未収束** (round 軌跡: 15→11→6; material 11→7→2). Limit of 3 rounds reached. User ruling "B": split ③ to ECO-113; continue ①② here.
- Round findings in brief: round 1 lock placement, ordering, pid reuse, grandchildren, dry runs, over-claim, freeze, own set, store locality, exits,
  core vs adapter, wording, arms, limits; round 2 the set blocking inspection cells, the git-history freeze, unreleasable states, worktree tree,
  `--by`, the brief's lasting home, lock contents, POSIX session, freeze location, option combinations, `--brief none`; round 3 two stale-mutex
  breakers, two stuck states, journal write failures, freeze after filing (R3-4), the order of R11 and the set check (R3-5), locating the order's
  line (R3-6). R3-1 to R3-3 went to ECO-113; R3-4 to R3-6 are repaired in this text (declared limit, 1-1.3 order, 1-1.1 line rule).
- Changes for the split: the in-flight journal no longer exists here, so the committed-copy check reads a per-ECO store directory instead (1-2.2, 1-2.4).

### Loop 2 (①② only)

- **判定: 未収束** (round 軌跡: 4→2→3; material 1→0→1). Limit of 3 rounds reached. **No manufacture and no filing commit** until the user rules.
  The round-3 findings are **not repaired** in this text (a repair would start round 4).
- **起動経路**: 自発, continued under the user's split ruling "B".
- **Round reviewer**: the same fresh context as loop 1, resumed; read-only; it confirmed the cited lines (`bomdd-run.py:216, :246-248, :345-363, :413-420, :434, :456`;
  `bomdd-job.py:73-79`; `bomdd-witness.py:171-184`).
- **DoD:** ✔ D1 (results read by the promotion decision, R11 order fixed, real run in the acceptance); ✘ D2 (the lasting reference is recorded only in the
  clone-local ledger and names a tree that may become unreachable, L2R3-3); ✔ D4; ✔ D5 (the post-filing change is declared, not anchored);
  ✘ D6 (existing ARG_ERROR arms would pass for the new rule's reason, L2R3-1); ✔ D7; ✘ D8 (`--brief` without `--cell` unspecified, L2R3-2); ✔ D9.
- **周回:**
  - **Round 1, 4 (1 material).** L2R1-1 the committed copy differs under `eol=lf` and a staged copy counted; L2R1-2 a refused launch stored a brief that
    then blocked promotion; L2R1-3 left-over temp files, unchecked store bytes, `os.replace` on Windows; L2R1-4 the new codes overwrote the witness
    code and the first line read `OK`.
  - **Round 2, 2 (minor).** L2R2-1 the check read `HEAD`, not the bound tree, and recorded no location; L2R2-2 existing `--cell` arms turn `ARG_ERROR`.
  - **Round 3, 3 (1 material).** L2R3-1 the list of arms gaining `--brief` left out the arms that expect `ARG_ERROR`/`UNMEASURABLE`, so they would pass
    for the new rule's reason and hide regressions in their own checks; L2R3-2 `--brief` without `--cell`; L2R3-3 the tree id in `brief_copies` is
    not a lasting reference (`{sha256, path}` is) and the record is clone-local.
- **Where the findings come from:** the last finding about the mechanism itself was L2R1 (round 1). Rounds 2-3 found how the selftest arms and the
  record are specified. L2R2-2 and L2R3-1 share one cause: the existing arms were listed from memory, not enumerated from the code — a derivation
  that can be done mechanically (every `--cell` invocation in the selftest).
- **未収束事項:** L2R3-1 to L2R3-3 (unrepaired).

### Loop 3 (user ruling "A": extension, after removing the common cause first)

- **The common cause removed before review** (user's steps 1-4): the selftest calls that `--brief` affects were extracted mechanically and checked by
  mutation; the evidence is recorded in `bomdd/reports/eco-112-arm-inventory/` (12 sites, 56 calls, no gap; 29 OWN / 26 MASKED / 1 CRASH; two existing
  arms passing for another reason today). §1-3 is now derived from that evidence, and V3 re-runs the instrument on the manufactured tool.
- L2R3-1 → §1-3.1, 1-3.3, 1-3.4 and V3; L2R3-2 → §1-3.2; L2R3-3 → §1-2.4 (`{sha256, path}` as the lasting reference, copied into the closure section).

- **Round 1, 2 (1 material).** L3R1-1 V3 could not go red: the instrument's targets (calls without `--brief`) would be empty after manufacture, and
  literally dropping `--brief` would let each refusal come from its own check and read as MASKED → a V3 instrument (`arm_inventory_v2.py`, every `--cell`
  call a target, the same fake refusal) is fixed now with its hash. L3R1-2 the one CRASH (an unguarded `unlink`) → guarded, and V3 requires 0 CRASH.
  The reviewer confirmed the evidence: hashes, the 56/73 counts by reading the code, the caller-line attribution, and the 742/748 claim.

- **Round 2, 2 (1 material).** L3R2-1 v2's fake refusal was worded like the brief rule itself, so the new rule's own arm could only read MASKED →
  the marker `ARG_ERROR(INSTRUMENT_MUTATION)` (no real message contains it), v2 re-hashed `9af0a259…`. L3R2-2 V3 depends on the selftest's shape →
  §1-3.7 states the four couplings as constraints, and a crash or gap from a change of shape is "cannot measure".

- **Round 3, 3 (minor) — not repaired** (a repair would start a fourth loop, which only the user can authorize). L3R3-1 §1-3.4 lets an `ARG_ERROR`
  arm check the shared code, which the marker also carries (loud, not fail-open); L3R3-2 V3 does not require the instrument's own unmutated run to be
  clean, so a failure already in a call's window would read OWN (a fail-open path); L3R3-3 the shape constraints bind only ECO-112's arms — if ECO-113 is
  manufactured first, its concurrency arms (threads, child processes) could leave V3 unable to measure or silently exclude calls.
- **判定: 未収束** (round 軌跡: 2→2→3; material 1→1→0). Limit of 3 rounds reached. **No manufacture and no filing commit** until the user rules.
- **What removing the common cause did:** the findings about which existing arms are affected stopped (round 1 confirmed the 56/73 counts and the
  742/748 claim from the code). All seven loop-3 findings are about the V3 instrument that the removal introduced (its targets, its marker, its shape,
  its baseline) — a new surface, not the old cause.
- **DoD:** ✔ D1; ✔ D2; ✔ D4; ✔ D5; ✘ D6 (L3R3-1, L3R3-2); ✔ D7; ✔ D8; ✘ D9 (L3R3-3's undeclared exclusion).
- **未収束事項:** L3R3-1 to L3R3-3 (unrepaired).

### Loop 4 (user ruling "1:A", 2026-10-18: extension; review limited to the unresolved findings and the existing DoD; no unbounded new instruments)

- Repairs: L3R3-1 → §1-3.4 (a unique message fragment where the code is shared); L3R3-2 → the V3 instrument refuses a dirty baseline (exit 2, no
  mutation; the user's mandatory condition), checked with a known-bad input, re-hashed `7abaa223…`, and V3 requires exit 0; L3R3-3 → §1-3.8 (scope
  declared; ECO-112 is manufactured first). No new instrument: the existing v2 was edited.

- **Round 1, 1 (material).** L4R1-1 "ECO-112 first" was stated in §1-3.8 but contradicted by the shared-file bullets of both orders and by ECO-113's
  `required_gates` note → both orders now state ECO-112 first. The reviewer confirmed L3R3-1, L3R3-2 (the guard's exit paths) and L3R3-3's scope part.

- **Round 2, 0.** The reviewer confirmed L4R1-1 repaired in both orders (no open-order wording left; ECO-113 §1-8 matches §1-3.7/§1-3.8) and no
  ECO-112 DoD item false.

- **Round 3, 1 (material) — not repaired** (a repair would start a fifth loop). L4R3-1: V1's and V2's real-run parts ("the promotion decision lists all
  four IDs as matched", "the promotion decision passes the committed-copy check") can be observed only by the promotion decision that reads the gates
  `V1` and `V2`; declaring those gates passed in the witness beforehand is a declared pass for something not yet measured. V4 (CI) and V6 (the diff
  window) already have the right treatment — out of `required_gates`, checked at closure — and V1's and V2's promotion-time parts did not get it.
  The reviewer confirmed that the basis citations, the evidence hashes, the manufacture order, V3's scope and the baseline guard still hold.
- **判定: 未収束** (round 軌跡: 1→0→1; material 1→0→1). Limit of 3 rounds reached. **No manufacture and no filing commit** until the user rules.
- **DoD:** ✔ D1; ✔ D2; ✔ D4; ✔ D5; ✔ D6; ✔ D7; ✘ D8 (L4R3-1: a gate declared before it can be observed); ✘ D9 (the same, as an over-claim).
- **未収束事項:** L4R3-1 (unrepaired). Suggested repair (not applied): split V1 and V2 into a gated part (the selftest arms, and for V2 the store
  re-fetch before promotion) and a closure-time part (what the promotion decision records), the latter out of `required_gates` like V4 and V6.

### Loop 5 (user ruling "1:A", 2026-10-18: extension, after removing the duplicated rules first)

- **Common cause removed before review (user condition):** one rule written in several places. §1 is now a rule register (G1-G5, B1-B5, O1, T1-T6,
  M1); each rule's text appears once, and the limits, the acceptance and the shared-file note refer to rule IDs. The acceptance keeps every observation
  and pass condition it had. No new mechanism or instrument; the DoD is unchanged.
- **Where the old section numbers went** (the loop 1-4 records above use them): 1-1.1→G1, 1-1.2→G2, 1-1.3→G3, 1-1.4→G4, 1-1.5→G5, 1-2.1→B1,
  1-2.2→B2, 1-2.3→B3, 1-2.4→B4, 1-2.5→O1, 1-2.6→B5 and L6, 1-3.1→T1, 1-3.2 and 1-3.3→B1, 1-3.4→T2, 1-3.5→T3, 1-3.6→T4, 1-3.7→T5,
  1-3.8→T6 and M1.
- **L4R3-1 repaired (user condition):** V1's and V2's parts that only the promotion decision can show moved to closure as V7 and V8, outside
  `required_gates`, like V4 and V6; V2 keeps its pre-promotion re-fetch of the real briefs as V2(f).
- **Classification of new findings (user condition):** each finding is recorded as one of — **existing design defect** / **inconsistency from duplicated
  text** / **new defect from the consolidation**.

- **Round 1, 2 (1 material).** L5R1-1 [new defect from the consolidation] the general rule that the closure section copies the `{sha256, path}` pairs
  (old 1-2.4, the L2R3-3 repair) was dropped from B4 and survived only in V8 → restored in B4, and V8 now checks it for ECO-112. L5R1-2 [existing
  design defect] B1's ordering had no observation → V2(c) gains an arm wrong in two ways at once. The reviewer found no other rule or observation lost.
- **Round 2, 1 (material).** L5R2-1 [existing design defect; present since loop 3's 1-2.4] B4's closure copy has no anchor for later ECOs → declared as
  L9 (a closure duty no tool checks), without adding a mechanism (user condition). Also, without a finding: §0's basis bullets renamed `Gap ①`/`Gap ②`,
  since they shared the IDs G1/G2 with the register (ECO-113's reviewer found the same clash there, L3R1-4). The loop cannot reach two rounds of zero
  any more (2→1→?); round 3 is run for the trajectory.
- **Round 3, 0.** L5R2-1 resolved as declared practice (L9); the rename left no broken reference (every remaining G1/G2 is a register rule; ECO-113's
  references to ECO-112 T5, T6, M1 and G3 still hold); no DoD item false.
- **判定: 未収束** (round 軌跡: 2→1→0; material 1→1→0). Limit of 3 rounds reached; the last round has zero, one round short of two consecutive zeros.
  **No open finding.** **No manufacture and no filing commit** until the user rules.
- **Classes in this loop:** new defect from the consolidation 1 (L5R1-1, a general rule dropped); existing design defect 2 (L5R1-2, L5R2-1);
  inconsistency from duplicated text 0.
- **DoD:** ✔ D1; ✔ D2; ✔ D4; ✔ D5 (B4's closure copy declared as practice, L9); ✔ D6; ✔ D7; ✔ D8; ✔ D9.
- **未収束事項:** none open; convergence lacks one round of zero.
- **Round 4, 0** (user ruling "1:A", 2026-10-18: one extra round on the same design version, text unchanged — §0-§3 byte-for-byte as in round 3, file
  sha256 `a415b0a7…` with only the receipt's round-3 lines added; zero findings confirm convergence under the default rule, any finding returns to the
  normal unconverged handling). The reviewer re-read the whole order and re-checked G1-G5, B1-B5, O1, T1-T6, M1, the gated/closure split and L1-L9
  against the acceptance; no DoD item false.
- **判定: 収束** (rounds 3 and 4: two consecutive rounds with zero new findings). **起動経路**: 自発, under the user's rulings recorded above.
  Round reviewer for every loop: one fresh context of the same model, resumed each round, read-only (context independence; not the independent
  inspection, which is V5).
- **未収束事項:** none.
