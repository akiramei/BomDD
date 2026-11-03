# Change Order — ECO-121 (distribution of ECO-120 to the existing products: each product's register says why an open ECO waits, in the fixed vocabulary, only where its own records support it)

> Instruction: user, 2026-11-04, "配布 ECO を起票" (file the distribution ECO), after ECO-120 was verified (`32606b4`).
> **Filing only.** Two things are left to the manufacture ruling, as in ECO-075, ECO-081, ECO-107, ECO-109 and ECO-116:
> - which products, and in what order (§1 E);
> - TimetableAdv (§1 E, item 2).
>
> Each part below is labelled **stop** (refuses), **measure** (a number produced and compared) or **none** (text only), as the standing
> caveat of 2026-10-29 asks. Records are English-primary.

## Equipment

- Filing: requested/resolved `claude-opus-5-5`, Claude Code (Claude Agent SDK), provenance **self-reported**.
- Producer: EQ-004.
- Independent inspection: decided at the manufacture ruling. In each product, its own review rule (R8 or its equivalent) applies to its own
  change.

## 0. Survey (basis of the filing; `bomdd/reports/eco-121-dwell-distribution/`, read at BomDD `32606b4`)

ECO-120 changed three BomDD files:
- `bomdd-job.py --dwell`, the view;
- the register template, where `waiting_on` and `paused` are comments;
- playbook §8, one paragraph.

A product has the view today: `python <BomDD>/method/tools/bomdd-job.py --dwell --register <its register>` reads any register. What a
product lacks is the data. No product register has `waiting_on` or `paused`, so every open ECO reads "none" (ECO-120 V7).

**The products' validators accept the keys (measured).** In scratch clones (`git clone --local`; no product repository was written),
`waiting_on` was added to one open entry and a top-level `paused` block to the register, and each product's validators were run before and
after the change (`probe/`):
- ViewPrism2: `validate_bom.py` gave 0 errors and 0 warnings both times.
- ViewTube: `validate_process.py`, `validate_record_language.py` and `validate_record_consistency.py --mode active` exited 0 both times.

Neither product needs a validator change to carry the keys.

**What each register already says about why an open ECO waits** (`survey.py` → `survey.txt`; read with `git show` at the heads below):

- **ViewPrism2** (`82c362ed`; tree clean; up to date with its remote): 24 open of 148.
  - **10: `golden: pending`.** ECO-007, ECO-010, ECO-011, ECO-012, ECO-017 to ECO-021 and ECO-082. The register's own vocabulary
    defines `pending` as "golden 再ウォークスルー/承認 待ち" (waiting for the golden walkthrough or approval), which is
    `human-acceptance`.
  - **13: closed under the legacy convention.** ECO-003, ECO-004, ECO-005, ECO-009, ECO-014, ECO-015 and ECO-022 to ECO-027 and ECO-036.
    - Each is `implemented` with `golden` approved or n/a, and each is before `lifecycle_evidence.applies_from: ECO-061`.
    - The register's own `active_scope.open_eco` names only ECO-007 as open.
    - These entries are not waiting. ECO-120's view counts them as open because its terminal set is fixed (`implemented` is not
      terminal) — a second case of the blind spot ECO-120 declared in round 2 (k).
  - **1: no rule.** ECO-013, `implemented`, golden `round1-fixed` ("later rounds may remain").
- **ViewTube** (`62d2b3e4`; up to date with its remote; its untracked `product/` is not touched): 173 open of 272 (staged 116,
  implemented 57).
  - `blocks_application_golden` on an entry X lists the ECOs whose golden **X blocks**, so an ECO named there waits on X. The key's own
    uses say so (for example ECO-VT-085's handoff: "092 の `blocks_application_golden` は恒久的に空").
    - Reading the lists the other way, and doing the same for `blocks`: **8 open entries are named by an open blocker** (ECO-VT-018 to 021,
      074 to 076, 094) → `eco:<ID>`.
    - The other **165 have no rule.**
  - `blocks_release: true` (25 open entries) says the entry **blocks** a release. It is not a reason the entry waits, so it is not mapped.
  - `next_gate` and `work_authorized` (6 each) are free text. They are not mapped.
  - **A correction to ECO-120's basis.** ECO-120 §0 read the 76 `staged` entries that carry `blocks_application_golden` as "waiting for a
    human's golden". The values say otherwise: 79 of the 92 open entries that carry the key have `[]`, which means the entry blocks
    nobody's golden. Only one open entry has a dated `blocks_application_golden_added_*` key.
    - ECO-120's verdicts do not depend on that sentence: V1 compares start commits, not reasons.
    - The count was a key-name count read as a meaning (playbook §4.4).
- **ViewPrism2's constraints.**
  - Its working copy is CRLF under `core.autocrlf=true`; the probe's edit flipped the ending of the line it touched.
  - Status transitions carry trailers from ECO-061 (E14 to E19). This ECO changes no status.
- **ViewTube's constraints.**
  - Records are in English (eco-file step 4).
  - A new check is under the user's standing gate freeze (ruling "C" on ECO-VT-176), so a vocabulary check in its gates is not added.
  - Its process files are `protected_paths`.
  - Its skills are under `.agents/skills/`.
- **MoviePad-Remake** (`a2ca41ec`; local only; 0 open of 6).
  - It vendors `bomdd-kit/`, pinned by sha256 in `kit-manifest.json`. That includes `method/tools/bomdd-job.py` without `--dwell`.
  - Receiving ECO-120 there means re-pinning the kit, as ECO-116 did, and remaking BomDD's bundle of it when BomDD's records cite the new
    commit.
- **TimetableAdv** (`73b79d47`, its last commit 2026-09-28).
  - It is the case `paused` was made for: 77 open and no commit for 37 days. Its register differs from HEAD by 665 uncommitted lines, and
    2,191 paths are dirty (ECO-120 §0).
  - It is deferred by the user's ruling of 2026-10-13, as in ECO-109 and ECO-116. Not read further.

## 1. Change request (frozen at filing; carried out per product at manufacture)

For each target product, one product-side ECO in that repository, under its own change management, records, gates and language.

### A. The rule each product ECO writes (none: text; its effect is measured by C and §3 V3)

1. **The fields.** An open entry may carry `waiting_on` with one of ECO-120's values:
   - `start-instruction`
   - `human-ruling`
   - `human-acceptance`
   - `independent-inspection`
   - `eco:<ID>`
   - `external`

   A whole-repository stop is declared once at the top of the register as `paused: {reason, resume_when}`. The vocabulary is ECO-120's,
   not widened here; a value a product needs and does not find is recorded as a finding for a BomDD ECO (§1 D).
2. **When it is written.** Each step that ends with the ECO waiting sets the value, and each step that moves the ECO on clears or changes
   it, in the same commit as the status change:
   - eco-file: a filing that waits for the start instruction gets `start-instruction`;
   - eco-fix: its stop sets the reason it stops for;
   - eco-accept, and any move to a terminal status: the field is removed.

   No start date is written (§13); the view derives it.
3. **How the view is run.** The product's change-management names the command. Whether a session's start runs it is the product ECO's
   choice, and the choice is recorded. Running it adds no gate and no `stop_type`.

### B. The open entries at manufacture (measure: rules, not judgment)

1. **A reason is written only where the product's own records support it by a stated rule** (§13: a value is derived, not transcribed
   from memory). The rules this survey found:
   - ViewPrism2: `golden: pending` → `human-acceptance` (10 entries).
   - ViewTube: an entry named in an open entry's `blocks_application_golden` or `blocks` → `eco:<that entry>` (8 entries). Where several
     open blockers name it, the product ECO names one and lists the others in its table.

   The product ECO may add a rule, for example from a ruling or an ECO body that names what the entry waits for. Each rule goes in its
   table with the field it reads. An entry with no rule keeps no reason, and the view shows it as unexplained, which is the true reading.
2. **Entries the product's own records treat as closed** (ViewPrism2's 13) are told apart in one of two ways:
   - a transition the product's change-management allows for that era, with the record it requires;
   - otherwise, listed by id in the product ECO as a known inaccuracy of the view.

   No reason value is used for them; "closed" is not a wait. The product ECO decides which way, records why, and applies converge to the
   choice.
3. **Each product ECO carries a table** of every entry given a `waiting_on`, with its rule and the field the rule reads. The table and the
   register are compared mechanically (§3 V3).

### C. Where the products differ (decided per product at manufacture; converge applied there)

- **ViewPrism2.** The register's line endings are kept: the edit is made on bytes or through git's normalization, and checked with
  `git diff --ignore-cr-at-eol` against an expected line count. Its `active_scope.open_eco` and the view should then agree on what is open;
  the product ECO says how.
- **ViewTube.**
  - No gate is added (freeze). The view's warnings are the only check on the vocabulary.
  - The free keys (`blocks_*`, `next_gate`, `work_authorized`) are kept as they are: they are records, and `waiting_on` is read alongside
    them, not instead of them.
  - Its skills are under `.agents/skills/`.
- **MoviePad-Remake** (if a target). The kit is re-pinned at a BomDD commit that includes ECO-120, with its `check_kit.py` or equivalent.
  It has no open entry, so §1 B is empty there. BomDD's bundle is remade when its records cite the commit.

### D. What this ECO does not change

- BomDD's tool, template and playbook. ECO-120 is verified, and the two blind spots found here are recorded for a later BomDD ECO, not
  repaired here:
  - the fixed terminal set against ViewPrism2's legacy convention;
  - the vocabulary's lack of a value for "blocks a release".
- Product code, tests, BOM files, fixed oracles, CAD, hooks and validators.
- Any product status, except a transition chosen under §1 B 2 by the product's own rules.
- TimetableAdv, unless the manufacture ruling chooses item 2 B below.

### E. For the manufacture ruling

1. **Targets and order.**
   - Proposed: ViewPrism2, then ViewTube. ViewPrism2 is smaller and its rule is the simpler one.
   - MoviePad-Remake: a kit re-pin only. It has no open entry, so its value is low; include it or not.
2. **TimetableAdv.**
   - **A**: not a target. This keeps the deferral of 2026-10-13; its resume condition (EXP-20261013-01) is extended to ECO-120.
   - **B**: one commit that adds only the `paused` block to its register.
     - Benefit: the view stops listing its 77 entries as unexplained.
     - Cost: the commit is made in a tree with 2,191 dirty paths and an uncommitted register, so only those lines may be staged (a partial
       add checked by `git diff --cached`). It also touches a deferred product.

## 2. No-impact prediction (before manufacture; frozen)

- **BomDD side:**
  - At filing: this order, the register and `bomdd/reports/eco-121-dwell-distribution/`.
  - At closure: the closure record. If chosen, a line in `method/improvements.md` for the two BomDD findings of §1 D.
- **Product side:** per product, its register (the new field and entries' values, and any §1 B 2 transition), its change-management, its
  eco-file, eco-fix and eco-accept skills, and its own ECO records. For MoviePad-Remake: `bomdd-kit/` and its manifest.
- **Untouched:** product code, tests, BOM files, fixed oracles, CAD, hooks and validators.

**Declared at filing — what the distribution will not make true:**
- **A backfilled reason looks new.** A reason written at manufacture starts its own clock at that commit. For the backfilled entries the
  view's `waiting_days` will read about 0 while `days` (in the status) reads 30 to 134. This is the rule, not a defect.
- **165 of ViewTube's open entries and 1 of ViewPrism2's (more if the 13 stay) will still read unexplained** unless a rule is found. The
  distribution makes the view say what the records support, not more.
- **The reason can go stale.** The rule of §1 A 2 is text; the view shows a reason's age and warns on a reason left on a terminal entry, and
  V5 reads that, but nothing stops it.

## 3. Acceptance (conditions; frozen at filing)

required_gates: [V1, V2, V3, V4]

**Gated:** V1-V4. **Not a closing condition:** V5.

- **V1 — the rule is in each target product.**
  - Condition: each target product's ECO is applied under its own lifecycle.
  - Its change-management names the field and its vocabulary, `paused`, and the view's command.
  - Its eco-file, eco-fix and eco-accept carry when the field is set and cleared: per file, `waiting_on` 0 → at least 1, counted at the
    base and at the applied commit.
- **V2 — the gates.**
  - Condition: each product commit passes the product's own gates.
  - For BomDD's commits, self-conformance exits 0, observed before each commit, and CI is green, read with the full SHA.
- **V3 — the data match the rules.**
  - Condition: at each target product's applied commit, `bomdd-job.py --dwell --json --register <its register>` gives:
    - no warning about `waiting_on` or `paused`;
    - the set of entries with a `waiting_on`, and each value, equal to the product ECO's table. A script compares the two and is shown to
      fail on a copy of the table with one row removed and one value changed.
  - Every remaining open entry over the threshold without a reason is listed in the product ECO by id, with its class: no rule, or closed
    under an earlier convention.
  - The counts by reason before and after are recorded.
- **V4 — the window.** In each product, the paths changed between its ECO's base and its applied commit are within §2's product side. In
  BomDD, within this ECO's `allowed_paths`.
- **V5 (not a closing condition).** About 14 days after each product's ECO is applied, the view is rerun and three things are recorded:
  - entries whose status moved while `waiting_on` stayed;
  - reasons left on terminal entries;
  - the unexplained count.

  This reads whether the rule of §1 A 2 is being kept.

Conditions are frozen at filing; results go to the closing section.

## /preflight receipt (start path: manual — the user's "配布 ECO を起票" read as the start artifact)

- **Classification**: filing of a distribution ECO (survey; no product change at filing).
- **Baseline `32606b4`**: **confirmed**. It is HEAD, and the tree is clean apart from ECO-119's untracked R8 report, which this filing does
  not touch.
- **Next number 121**: **confirmed**. The last register entry and the last order are ECO-120, and there is no
  `60-change-order-eco-121.md`.
- **ECO-120 verified, CI success** (run 41687693065 on `32606b4`): **confirmed**.
- **The product facts in §0**: **confirmed**. They were read at ViewPrism2 `82c362ed` and ViewTube `62d2b3e4` (both up to date with their
  remotes; ViewTube's untracked `product/` untouched) and at MoviePad-Remake `a2ca41ec`. The validator probe ran on clones.
- **A stale memory, corrected**: a note said ECO-VT-269/270 were unpushed. ViewTube is 0 commits ahead of its remote, so no unpushed
  stack sits under a new ECO-VT.
- **TimetableAdv**: **out of scope** by the deferral of 2026-10-13; not read beyond ECO-120's survey.
- **Start decision**: **PROCEED_WITH_LIMITS**. This is filing only; manufacture waits for the ruling of §1 E.

## Converge receipt (the distribution's form; 起動経路: self-triggered at filing, DoD fixed first)

- 判定: 収束. Round 1 found 9, round 2 found 4 new, round 3 found 0 new.
- DoD:
  - ✔ D1 each product's register can carry the keys without its gates turning red (measured on clones);
  - ✔ D2 no reason is written without a stated rule over the product's own records (§13);
  - ✔ D3 entries the product's records treat as closed are not shown as waits, and no status is invented for them;
  - ✔ D4 the products' constraints are named (ViewTube's gate freeze, English, protected paths; ViewPrism2's trailers and CRLF;
    MoviePad-Remake's kit pin);
  - ✔ D5 each part is labelled stop, measure or none;
  - ✔ D6 TimetableAdv is handled explicitly, not silently;
  - ✔ D7 each gated condition can fail and V3's comparison is shown failing on a broken table.
- round 1 (9):
  - (a) ECO-120's "76 waiting for a golden" taken as the backfill rule → the key's definition read and the lists read the other way: 8
    entries, and a correction recorded;
  - (b) the backfill resets the reason's clock → declared (§2);
  - (c) ViewPrism2's 13 legacy entries shown as stalls → §1 B 2, two ways, no reason value;
  - (d) a vocabulary check in ViewTube's gates → not added (freeze); the view warns;
  - (e) TimetableAdv silent → §1 E 2, A or B with B's cost;
  - (f) MoviePad-Remake's pinned kit → §1 C, a re-pin, its low value stated;
  - (g) whether the validators accept the keys → measured on clones;
  - (h) a reason that rots after the backfill → §1 A 2 ties it to the status change, and V5 measures it;
  - (i) an unpushed ViewTube stack → checked: none.
- round 2 (4 new):
  - (j) `blocks_release` and the free-text keys don't fit the vocabulary → not mapped, and recorded for BomDD (§1 D), not widened here;
  - (k) several open blockers for one entry → one is named and the others listed in the table;
  - (l) ViewPrism2's CRLF working copy → §1 C;
  - (m) ECO-013 (`round1-fixed`) → no rule, stays unexplained.
- round 3 (0 new): the parts checked against D1-D7 and against §0's numbers re-derived from `survey.txt`.
- 未収束事項: none in the form. Left to the manufacture ruling: the targets and order, and TimetableAdv A or B.
