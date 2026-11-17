# ECO-126 — the fresh-context review, round 1 (2026-11-17): the findings as the reviewer wrote them, condensed, and what was done

The reviewer was a fresh context of the producer's equipment (context independence). It read the diff against `59b96bb` and ran
its own fixtures. The numbering is the reviewer's. "Done" is the producer's disposition, written after the round.

## Substance — tools

| # | Finding | Done |
|---|---|---|
| 1 | `loop-count --check` exits 0 on a record with nothing in it | repaired: a record with no round is a gap; arm added |
| 2 | the accepted-report rule fires only for `accepted: yes`; other words pass | repaired: `accepted` must be yes / no / dropped; arm added |
| 3 | a round's set passes with an empty hash | repaired: every hash non-empty; arms added |
| 4 | reactions with no id / round / words, duplicate round numbers, rounds over the limit, reactions with no reply, `fixed` with no drawing line | repaired, except "rounds over the limit", which is shown as an `[over]` line and is not a gap |
| 5 | `handover-stamp`: the log line has no label, and re-stamping the same folder credits old launches to the new stamp | repaired: every stamp has an id written to the log; other stamps' lines are counted apart; arm added. The label stays in the manifest only (declared) |
| 6 | `&` and `^` pass the file-name filter | repaired: names are letters, digits and `. _ - /` only; arm added |
| 7 | malformed log lines are dropped silently | repaired: counted, reported, exit 1; arm added |
| 8 | absolute and parent-relative `--file` accepted | repaired (the same filter); arm added |
| 9 | the started program is not hashed | repaired: the program is stamped and re-checked; arm added |
| 10 | malformed values in the record raise a traceback with exit 1 | repaired: a shape error is `[input]`, exit 2; arms added |
| 11 | a malformed manifest raises a traceback | repaired: `[input]`, exit 2; arm added |

## Substance — text against tools, text against text

| # | Finding | Done |
|---|---|---|
| 12 | the record's format is said to be at the head of `loop-count.py` and is not there | repaired: the head now holds the whole format |
| 13 | a reaction is defined as one thing said to be different, yet kinds are per reply; "そのまま" has no class | repaired: one row per reply at least; the class words are in the skill's tables; `left_as_is` added |
| 14 | nothing tells anyone to run `handover-stamp.py check` or what to do with its exit codes | repaired in the skill |
| 15, 16 | the "complete list" of stops omits the stops inside eco-fix and contradicts R4 / R8 | repaired: the list is "what this route adds"; the others are said to stay as they are |
| 17 | the cost frame is asked for and then used nowhere | repaired: `limits.budget` in the record, shown by the tool; reaching it is a stop |
| 18 | who writes the implementation record and the status note in a looped change is not said | repaired: the route uses eco-fix steps 1-5; the note is "周 N 候補・利用待ち", then "golden 待ち". **A departure from the order's L1, which said steps 1-3.6** |
| 19 | R1-R4 mean two things in the skill | repaired: the skill's acceptance conditions are A1-A4 |
| 20 | "close the bundle" names no status, ruling or decider | repaired: `ruled` / `accept-as-built` / `decided_by: user`, with the evidence split |
| 21 | "an operable part can never rest on a bundle" holds only while the bundle is open | the claim is narrowed in the text (a rule of the text after the bundle is closed; no check) |
| 22 | a `touches_confirmed` entry ruled by something other than the user passes GU7 | repaired in GU7 after the inspector's last round (see `gu7-after-r2.md`) |
| 23 | the scenario table lists three human gates beside "two kinds" | repaired: two kinds, the second in two forms |
| 24 | example 4 of the template lists a ruling the gate could not have required | repaired: the example bundle's ids now overlap it |
| 25 | parts delivered that section 1 did not name (the product entry documents' lines, the README count, the scenario row, the commit note, the skill row, C20 and C6c-e; `eco-file.md` carries a rule, not only a pointer) | recorded as departures in the order's section 4; all inside `allowed_paths` |

## Evidence

| # | Finding | Done |
|---|---|---|
| 26, 27 | `handover-stamp` self-test arms that survive the removal of what they name | repaired: the non-ASCII arm uses a file that exists; arms for a changed second file, a replaced program, a re-stamp. The `sh` launcher is not run by the self-test on Windows (declared; V3 runs it) |
| 28 | `loop-count` self-test arms missing for class, handed_at, set.commit, disposition, lands_on, listed_before_use, the preread rules and the tally | repaired: 23 arms, and the good record's tally lines are checked |
| 29 | V2's lines about reactions compare the tool with literals the script wrote | a note is printed by V2; the stage tables are the part compared with the table |
| 30 | V4's `B.r` failed by construction | V4 was rewritten after the text repair: `B.r` is the route as now worded; the refusals are controls |
| 31 | the ruling-trailer and three-state sentences were not measured | V4 variant C (three states) and `B.r` now measure them |
| 32 | V4: one PASS does not depend on the exit it prints; C13 and C7 are not in the script | left: C13 and C7 are in the self-conformance output; noted in the order |
| 33 | V5's "byte-identical" compares decoded text; one check is a count plus keywords | the label now says what is compared; the count stays, declared |
| 34 | V3's comment says three checks for `sh`, two run | comment corrected |
| 35 | V1 uses a MoviePad commit where the order says HEAD; ViewTube's SHA not recorded | the output now names both commits |
| 36 | no full self-conformance output in the folder | the full run's output is copied into the folder |

## Record

| # | Finding | Done |
|---|---|---|
| 37 | the order says `touches: <id>`; the delivery uses `touches_confirmed` | recorded as a departure (section 4); section 1 is frozen and not rewritten |
| 38 | the order says the log line carries the label | recorded as a departure |
| 39 | "`--check` exits 1 on a gap" said more than the tool did | the tool now does; the text says "the gaps the format names" |

## Out of scope

| # | Finding | Done |
|---|---|---|
| 40 | `method/onboarding/working-with-ai.md` lists the entry skills without `/eco-turn` (not in `allowed_paths`) | not changed; named in the order as a follow-up |
| 41 | GU3 / GU4 do not look at who ruled (pre-existing) | not changed |
| 42 | the working copy of `method/ui-ir-ui-bom.md` is CRLF (the environment; the blob is LF) | checked at staging |
