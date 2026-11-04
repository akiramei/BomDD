# ECO-123 filing basis — the job view's closure-heading rule over every ECO

Read-only, at BomDD `825d9a1` (2026-11-04). The selftest's blind spots are measured in ECO-122's
`bomdd/reports/eco-122-dwell-cache/manufacture/mutants_selftest.txt` and not repeated here.

| File | What it is |
|---|---|
| `heading_survey.py` | For each register entry with an order: the stop the closure rule alone gives with the current `CLOSE_HEAD_RE` and with `(?:クローズ\|Closure)`; the entries that change, the headings only the new rule matches, and what the orders still not `NONE` hold. |
| `heading_survey.txt` | Its output: 71 not `NONE` now, 59 with the new rule; the 12 that change are ECO-105 to 111, 116 to 118, 120 and 121; the 59 are 30 without a closure heading, 27 without `verified`, two in another title. |
