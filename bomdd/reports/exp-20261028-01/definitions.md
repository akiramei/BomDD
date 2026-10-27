# EXP-20261028-01 outcome baseline - definitions (frozen before counting, 2026-10-28)

Written before `baseline.py` counted anything. Rules are not changed while counting; a rule that proves unworkable is
recorded under "Departures" at the end, with what was done instead.

## Scope

- **Repositories (read-only):** BomDD (method), ViewTube, ViewPrism2, MoviePad-Remake. Every file read is under each
  repository's `bomdd/` (ViewTube also its register at `bomdd/process/change-register.yaml` and the review files under
  `test-results/` that its register names); every git call carries a `bomdd/` pathspec or reads commit messages only.
  `ViewTube/product/` is never listed or read.
- **Window:** every ECO whose filing date is 2026-10-01 or later. Filing date = BomDD and MoviePad-Remake: the register's
  `date`; ViewTube and ViewPrism2 (no date in the register): the committer date, in the commit's own offset (+09:00), of the
  first commit that added the ECO's order file (`git log --diff-filter=A -- <file>`). Not UTC: ECO-VT-218 was committed
  2026-10-01 08:16 +09:00, which is 09-30 in UTC. Every status stays in the window (staged, implemented, superseded).
- **Order file / record text:** BomDD, ViewPrism2, MoviePad-Remake `bomdd/60-change-order-eco-NNN.md`; ViewTube
  `bomdd/eco/ECO-VT-NNN.md` plus its register entry (rendered as YAML text).
- **Commits attributed to an ECO:** a commit whose trailer names the id (`BomDD-ECO-<Kind>: <id>`), or whose subject scope
  names it: `type(eco-NNN...)`, `type(ECO-VT-NNN)`, `eco(NNN)`, `eco(NNN/MMM)`, `eco(NNN-MMM)` (the `/` list and the `-`
  range are expanded), `起票(eco-NNN)`, `eco-NNN:`. Case is normalised. Only commits reachable from HEAD.

## Metrics (one rule each)

1. **Independent review rounds (R8 or equivalent).** Source: ViewTube `bomdd/eco/ECO-VT-NNN-independent-review.md`; if absent, the register entry's `evidence.review_round_N` blocks (`verdict` field), else the review files `review<NNN>r<K>*.md` the entry names; BomDD / ViewPrism2 / MoviePad-Remake the order file with every converge-receipt section removed (a heading containing `収束 receipt`, `Converge receipt` or `Convergence receipt`, to the next heading of the same or a higher level); BomDD only, if the order holds no round, the subjects of the ECO's commits. Rule: a round starts at a heading line or a bold lead (`**...`) containing `round N`, `Round N`, `inspection rN`, or a `### X.Y rN(` heading, or an inline `rN **ACCEPT|REJECT**`; a marker with a number at or below the current round continues the current round (so `Round 1 — dispositions` and `Round 1 findings` inside round 2 do not open rounds); in a ViewTube review file, text before the first marker that carries a verdict is round 1, and a file with no marker is one round. Commit-subject fallback: each `rN ... ACCEPT|REJECT` (or `rN→rM ACCEPT`, giving rM) in a subject of `独立検査`/`inspection`. Verdict = the first of `PASS WITH FINDINGS | ACCEPT | REJECT | PASS | FAIL | NOT FIT` on the marker line, else on the round's first line containing `verdict|Verdict|VERDICT|Result|判定`; mapped PASS/PASS WITH FINDINGS -> ACCEPT, FAIL/NOT FIT -> REJECT. A round in an order file ends at the next heading of the same or a higher level (a heading marker) or at the next heading (a bold-lead marker); a ViewTube review file is read whole. Findings per round = an explicit count on the marker or verdict line (`N findings`, or the sum of `substance N, evidence N, record N`, or for a ViewTube register block's `findings` field the sum of the numbers after `ブロッキング|重大|軽微|blocking|material|minor|major`), else `0` when the round states `no finding`/`findings none`/`所見なし`/`findings: none`, else the distinct finding ids (`IA-NN`, `RNNN[a-z]-FN`, `RNNN-N-NN`, `R8-N-NN`, `VPNNN-XN`, bare `FN`) on heading lines or bold leads of the round, with `IA-NN to IA-MM` expanded; ids already counted in an earlier round of the same ECO are not counted again (bare `FN` excepted, as round-local); no count and no ids -> `unknown:NO_FINDING_COUNT`. BomDD ECO with no round anywhere and register `inspector` absent or `none` -> 0 rounds (`none_declared`); any other ECO with no round -> `unknown:NO_R8_RECORD`.
2. **Converge rounds.** Source: the converge-receipt sections of the order file / ViewTube body (headings as in 1). Rule: each line in them carrying a chain `N→M[→K...]` or `N -> M [-> K]` that also contains `軌跡`, `trajectory`, `round` or `findings` gives one trajectory (the first chain on the line; at most one per loop heading or `判定` line); the outcome is the last judgement token in the receipt, a token counting only right after `判定`, `verdict`, `judgement`, `outcome` or `ended` (within 20 characters): `未収束`/`unconverged`/`not converged` -> `cutoff` (the receipt sits in a filed ECO, so the design went on unconverged, i.e. was adopted by cut-off), `収束`/`converged` (not preceded by 未/un/not) -> `converged`. No receipt -> `none` (not unknown). Receipt with no judgement token -> `unknown:NO_CONVERGE_VERDICT`.
3. **Fix commits.** Source: git commit messages. Rule: commits attributed to the ECO that carry `BomDD-ECO-Fix: <id>`, or whose subject type is `fix`, `file+fix` or `manufacture` (the last only when the message names the id), or (BomDD's Japanese `eco(...)` dialect) whose subject text before the first ` — ` contains `製造`, `是正` or `処置`. Count per ECO; rework = count - 1 when count >= 1. Note: ViewTube uses `fix(` for every step of its fix phase (implemented marks and R8 repairs alike), so its count > 1 overstates rework in a way the other repositories do not.
4. **Human rulings.** Source: the order file / ViewTube body and the ECO's accept commit message; ViewTube also every `words` / `instruction_words` / `answers` value in the register entry (a dict of words counts each value). Rule: a quoted string `"..."` (1-60 chars) or `「...」` (1-80 chars) within 40 characters after `user`, `user's`, `利用者`, `maintainer`, `maintainer's` or `DECIDE`, plus unquoted `N:X` sequences right after `user 裁定` / `user ruling` / `user DECIDE`; distinct after NFKC normalisation and whitespace removal. Lower bound: the same answer ("A") given on two occasions counts once. **Golden returns:** lines of the same sources matching (`golden|gate ?②|gate 2|application golden|real-machine|実機`) together with (`差し戻|returned|sent back|rejected|REJECT|不合格|not approved|did not approve|invalidated|やり直`), counted; `n/a` when the sources never mention golden / gate ② / gate 2 or say `golden n/a`, `no golden gate`, `There is no golden`, `No golden`.
5. **Known defects carried at acceptance.** Applies when the status is applied or verified, else `n/a:NOT_ACCEPTED`. Source: order file / ViewTube body and register entry, and the accept commit message. Rule: distinct ids of the ECO's own number (`KD-<n>-N`, `VP<n>-XN`) anywhere; else distinct `R8-N-NN` ids on lines containing `known defect`; else the number (digit or English number word) directly before `(low |minor )?known defects?` in the accept commit message, then in the order; `No known defect`/`no known defects` -> 0; else `unknown:NO_KD_STATEMENT`.
6. **Escapes.** Source: in the same repository, the order files / ViewTube bodies and review files of ECOs with a higher number (filed later), the repository's `bomdd/51-cheat-log.md`, and BomDD `method/improvements.md` (OBS records for all four repositories; a product id must have its product name, `ViewTube` / `ViewPrism2` / `MoviePad-Remake`, on the same line; a BomDD id must not be preceded within 15 characters by a product name). Structured first: ViewTube register `corrective_of: <id>` in other entries (ViewPrism2's `reattributed_by` was read before counting and is a BOM re-attribution, not a defect, so it is not used). Rule: a line containing the exact id (word boundary) and one of `origin|caused|introduced|regression|escaped|due to|起因|由来|混入|退行|回帰`; count distinct citing records (the citing ECO id, the cheat-log section id, or the OBS id on the line, else the file and line). The ECO's own files and the register are excluded. Every citing line is written to `baseline.json` for audit. Known false-positive class: "no regression" style lines.
7. **Elapsed time.** Rule: hours from the filing commit (first commit adding the order file) to the closing commit = the earliest attributed commit with trailer `BomDD-ECO-Accept: <id>`, or subject `accept(<id>)` or `eco(<ids>): accept`, or `record(<id>): verified|applied`; fallback: the earliest attributed or not attributed commit whose subject contains the id and `verified` or `applied`, tagged `CLOSE_BY_SUBJECT_FALLBACK`. Status not applied/verified -> `unknown:NOT_CLOSED` (`unknown:SUPERSEDED` for superseded).
8. **Receiving runs.** Applies to ViewPrism2 ECO-148, ViewTube ECO-VT-270 and ECO-VT-271, MoviePad-Remake ECO-004 (the ECOs that introduced or changed a receiving step); every other ECO `n/a`. Source: `bomdd/50-as-built.yaml` and git. Rule: count of As-Built entries with `work_ref: <id>`; each one's time = the commit `receive(<id>): <entry id> ...`, else the `measurement.run_dir` stamp (UTC), else `unknown:NO_TIMESTAMP`.

## Reason codes

`NO_R8_RECORD`, `NO_FINDING_COUNT`, `NO_VERDICT_TOKEN`, `NO_CONVERGE_VERDICT`, `NO_KD_STATEMENT`, `NOT_CLOSED`, `SUPERSEDED`,
`NO_FILING_COMMIT`, `NO_TIMESTAMP`, `NOT_ACCEPTED` (n/a), `CLOSE_BY_SUBJECT_FALLBACK` (a tag, the value is kept).
`n/a` and `none` are values (the metric does not apply / nothing exists) and are tallied apart from `unknown`.

## Departures

Recorded while counting, in the order found; each is marked in `baseline.py` with its label. The rule text above is
left as frozen; where a departure applies, the departure governs.

- **D1 (metric 1, round markers).** As written, any heading or bold lead containing `round N` opened a round, so
  passing mentions opened false rounds (ECO-115's "the repairs after loop 4 round 2" opened round 2 before r1; ECO-112,
  ECO-113, ECO-099, ECO-108, ECO-116, ECO-VT-250, ECO-VT-262, ViewPrism2 ECO-148 likewise). Now: a heading counts when
  its phrase is not `loop N round M`; a bold lead counts only when `round N` lies inside the bold text, within 25
  characters of its start, with no `loop` / `converge` before it.
- **D2 (metric 1, verdict).** ViewTube files put the verdict under a `## Verdict` heading with the token on the next
  line (`**FAIL.**`); a verdict heading without a token now takes the token from the next non-empty line.
- **D3 (metric 1, finding ids).** ViewTube findings also appear as table rows (`| R260-F1 | ...`) and as `R260-N1`,
  `R2-1` (ECO-VT-245 round 2); those id forms and table-row ids are counted (bare `F` ids in table rows round-local).
- **D4 (metric 1, Japanese rounds).** ViewTube ECO-VT-234 to 246 head rounds `第 N 回`; such a heading is a marker.
- **D5 (metric 1, Japanese count).** `所見が N 件` on a marker or verdict line is an explicit count.
- **D6 (metric 6, escapes).** Line-level co-occurrence of the id with the keyword list was unworkable: every
  candidate in the first run (about 33 lines over 22 ECOs) read as a false positive on inspection, and the two escapes
  the narrowed rule finds (ECO-VT-220, ECO-VT-232) were not among them — `由来` naming an
  ECO's source (ECO-096: "由来: ECO-092 §4"), the inspection range name `是正確認+回帰`, "original", OBS lines that only
  list ECOs. Now the escape word must point at the id: `introduced|caused|broken|broke|
  regressed|regression|escaped|origin(ated) by|in|at|since|from|with|of <= 40 chars <id>`, `since <id>'s
  acceptance|application|fix|repair|change|manufacture`, `<id>('s) ... introduced|caused|broke|regressed`, `<id>` then
  within 15 characters `起因|混入|退行|で壊|が壊|由来の欠陥`; after the ECO-098 spot-check also `<id> の(記載の)誤り`,
  `<id> (の記載)を訂正|の訂正`, and `corrects|an error in|a defect of <id>`. Recall is not measured (see spot-check).
- **D7 (metric 4, golden returns).** The rejection words matched quarantine lines (`self_golden: invalidated,
  blocked_by ECO-VT-213` is a wait for a tool, not a return) and inspection `REJECT`s; BomDD's lines were rule text
  about products. Now: BomDD is `n/a` (the method repository has no golden step of its own); the words are
  `差し戻|sent back|was returned|returned it|returned the|golden failed|golden failure|golden (was) rejected|
  golden returned|rejected at/the golden|not approved|did not approve|承認しな|やり直し`, and the line must also name
  the user or maintainer.
- **D8 (metric 5, precedence).** For MoviePad-Remake ECO-004 the R8 ids on known-defect lines gave 3 (one id was a
  departure, two were a range `R8-2-01 to R8-2-04`), while the acceptance says four. Now: own `KD-` ids, then the accept
  commit's number phrase, then R8 ids on known-defect lines with `R8-a-b to R8-a-c` expanded, then the order's number
  phrase. **D8b:** `VP<n>-XN` ids are finding ids (VP147-F1 was a repaired finding), so they count only on lines
  containing `known defect`.
- **D9 (metric 4, rulings).** A quote whose text between the attribution and the quote names another ECO or reads as
  content (`ECO-`, `says`, `typically`, `e.g.`, `for a`, `such as`) is not counted (ECO-VT-270: "rework: bind or narrow
  the row", ECO-VT-269's "2:a", "the one canonical full-suite run"). A rule dropping `N:X` fragments of a longer answer
  was tried and withdrawn: in ECO-115 the fragment "2:A" is a ruling of its own.
- **D11 (metric 1, commit-subject fallback).** A subject whose scope names several ECOs (`eco(091/093/094): ECO-091
  独立検査 r1 ACCEPT ...`) credited ECO-091's round to ECO-093 and ECO-094; such subjects are no longer read for rounds.
- **D10 (metric 2, trajectory).** The first chain on a line could be a partial (ECO-VT-270 round 2: "of round 1's 15 →
  7"). Now per loop (heading inside the receipt) the chain on a `軌跡`/`trajectory` line wins, else the longest chain.
