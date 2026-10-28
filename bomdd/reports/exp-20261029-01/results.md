# EXP-20261029-01 — results: how much of a derived layer a program could reproduce, and where the defects fell

Definitions fixed before classifying: [definitions.md](definitions.md) (one departure, D1: the sample). Items: `items.py` →
[items.md](items.md) (120 items, MoviePad-Remake `d3683d6`). Classifier 1 (the designer): `classifier1.py` → `classifier-1.json`.
Classifier 2 (a fresh-context agent, blind to classifier 1): `classifier-2.json`. Defects: [defects.json](defects.json) (mapped after
both classifications were fixed). Tables: `compare.py` → `summary.json`. The A1 check: `a1_check.py`.

## 1. What a program could reproduce

| Kind | n | Classifier 1 R/C/C+/J | Classifier 2 R/C/C+/J | Agree | R or C for both |
|---|---|---|---|---|---|
| acceptance-refs | 8 | 0/8/0/0 | 0/7/0/1 | 7 | 7 |
| cp-row-partition | 15 | 0/13/0/2 | 1/13/0/1 | 13 | 13 |
| cp-links | 15 | 0/13/2/0 | 0/12/0/3 | 11 | 11 |
| cp-policy | 15 | 0/11/0/4 | 0/14/0/1 | 12 | 11 |
| provides-api | 8 | 0/0/2/6 | 0/0/0/8 | 6 | 0 |
| cp-method | 15 | 0/1/0/14 | 0/0/0/15 | 14 | 0 |
| provides-process | 1 | 0/0/0/1 | 0/0/0/1 | 1 | 0 |
| unit-partition | 8 | 0/8/0/0 | 0/4/0/4 | 4 | 4 — no claim |
| dependencies | 8 | 4/3/0/1 | 3/2/0/3 | 5 | 5 — no claim |
| provides-file | 2 | 0/2/0/0 | 0/1/0/1 | 1 | 1 — no claim |
| manufacturing-decision | 18 | 0/3/0/15 | 0/6/4/8 | 9 | 2 — no claim |
| assembly-refs | 1 | 0/1/0/0 | 0/0/0/1 | 0 | 0 — no claim |
| routing-step | 6 | 4/1/0/1 | 1/3/0/2 | 2 | 4 — no claim |
| **all** | **120** | **8/64/4/44** | **5/62/4/49** | **85** | **58** |

(U was used by neither. "No claim": the classifiers disagree on more than a third of the kind's items — definitions §6.3.)

- **The island under today's inputs** (R or C for both classifiers): **58 of 120**. Almost all of it is already a rule in waiting
  (C), not a rule (R): R for both is 4 items (three empty dependency lists and one routing step).
- **Where the two agree it is mechanical**: the Control Plan's bookkeeping — which rows exist, what they link to, when they run,
  which unit lists them (acceptance-refs, cp-row-partition, cp-links, cp-policy: 42 of 53 for both).
- **Where the two agree it is judgment**: the C# forms of the external promises (provides-api, 0 of 8 mechanical for either) and the
  test design of every row (cp-method, 0 of 15 for both). Both classifiers found that each form carries behaviour the specification does
  not state (for example a 16/9 aspect fallback, "no change" returns the same instance), read from the authority or chosen.
- **The input-field question** (C+: what one more field in the ruled layer would make mechanical): 4 items each, **no overlap**.
  Classifier 1 named a typed operation model per interface and an invariant-to-operation map; classifier 2 named ffmpeg facts for
  the K-BOM and three specification clauses. The experiment gives no stable answer to "which fields would an intermediate model need".
- Caveat (classifier 2's reading 3): the E-BOM's `acceptance_refs`, the specification's "CP that checks it" column and its trace
  table were treated as ruled input, though some were back-filled from the derived layer. This inflates C in the Control Plan
  kinds; neither classifier discounted it.

## 2. Where the defects fell

25 findings, 22 mapped to items (31 item hits; the mapping of findings to items had one rater, the designer). By class of the hit item: classifier 1 **J 26**, C 3, C+ 1, R 1; classifier 2
**J 24**, C 5, C+ 2.

- **The G3 dry runs** (a fresh AI given only the package, asked what it would need to know; three rounds before manufacture) named
  19 findings that map to items (22 item hits: 11 forms, 9 manufacturing decisions, 2 rows' test design; J for 20 and 18 of the 22
  hits by the two classifiers). The records say all but one were repaired "from the authority" — knowledge of the reference product,
  not a rule (the other, from the specification).
- **The sealed mutant sets** (oracle v2 to v5) added cases to four rows' test design (cp-method, J for both).
- **The one finding a tool made** before this experiment: the test plan's stage check split CP-EXPORT-001 so each row runs at one
  stage (cp-row-partition, C).
- **A latent one found here.** The written structure check A1 (kit playbook §4.6, rules 1-7) is applied by reading; no tool runs it.
  `a1_check.py` runs rules 1-6 and finds, at `d3683d6`, **6 failures of rule 4** (a unit requires another unit's part-standard item
  across E items — an E-to-E boundary must go through the ruled interface) and **6 of rule 5** (an E-level requirement with no
  requires targeting its interface); at the first M-BOM (`64912a4`) 13 and 14. They sat through the three G3 rounds, five ECOs and two
  R8 rounds; the first M-BOM's commit says "A1 structure checked" and names four of the checks, not rules 4 and 5. One of them is not
  only a form: M-OUTPUT-SETTINGS-001 depends on M-DOCUMENT-001 (to reuse `Even()`), a dependency the E-BOM does not have — under kit
  §4.5 P3 that returns to the human.

## 3. Reading (fixed in definitions §6 before counting)

- **No kind is a generator candidate.** The four kinds both classifiers call mostly mechanical carry one recorded finding (TP-1),
  found by a tool that already checks it. The recorded defects fell on judgment (J), and the judgment was repaired with knowledge
  of the reference product.
- **The result supports checking before generating.** Items mechanical for both classifiers drew 3 of the 31 hits: CP-EXPORT-001's
  row split (TP-1, found by a tool that already checks it), the copy command's fixed arguments (G3-1e) and M-PROBE-001's dependency
  (one of the latent A1 failures, on an item a written check covers that no tool runs; the other two A1 items are J for at least
  one classifier). A generator for M-PROBE-001's dependency would have produced the right value; so would running the written
  check, at the cost of `a1_check.py` (115 lines, seconds to run), which also catches the A1 failures on the judged items.
- Not claimed: a rate for other products (one product, one designer, one forward run); that the classifications are right (two
  classifiers agreed on 85 of 120, and six kinds give no claim); that G3's unnamed findings (about nine of round 1's sixteen) fall
  the same way.

## 4. Other rule conflicts noted by classifier 2 (not mapped as defects; MoviePad-Remake untouched)

- CP-MEDIA-TOOLS-001's `requirement_refs` copy the E item's refs, which the Control Plan template says not to do; the specification's
  trace table puts REQ-019 on CP-EXPORT-001.
- MD/M-DOCUMENT-001/1 restates a specification clause, which kit §4.5 ① says not to repeat.
- ROUTE-READ's input list leaves out `34-routing.yaml`, which kit §4.6's manufacturing package includes.
