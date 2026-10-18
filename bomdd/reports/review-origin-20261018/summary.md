# Review-finding origin — ECO-112 / ECO-113 design reviews (measured 2026-10-19)

Findings: **113** (ECO-112 63, ECO-113 50); per-round counts against the receipts: all equal.

## Reviewed versions

| ECO | round | review request (UTC) | version | sha256 (12) | basis |
|---|---|---|---|---|---|
| ECO-112 | L1R1 | 2026-10-18T03:26:53 | versions/ECO-112-L1R1.md | 3a67fb0f43dc | write #27 |
| ECO-112 | L1R2 | 2026-10-18T03:36:56 | versions/ECO-112-L1R2.md | b31f59a8c790 | write #28 |
| ECO-112 | L1R3 | 2026-10-18T03:40:30 | versions/ECO-112-L1R3.md | 3de06ec113b5 | write #29 |
| ECO-112 | L2R1 | 2026-10-18T04:00:14 | versions/ECO-112-L2R1.md | 85f0e65527ed | write #34 |
| ECO-113 | L1R1 | 2026-10-18T04:00:14 | versions/ECO-113-L1R1.md | 2e3ba455e870 | write #35 |
| ECO-112 | L2R2 | 2026-10-18T04:02:05 | versions/ECO-112-L2R2.md | 7fa709bb2399 | write #34 + replay to #38 |
| ECO-112 | L2R3 | 2026-10-18T04:03:15 | versions/ECO-112-L2R3.md | 8cc0d5d993e4 | write #34 + replay to #41 |
| ECO-113 | L1R2 | 2026-10-18T04:11:33 | versions/ECO-113-L1R2.md | 9b67168e27c6 | write #48 |
| ECO-113 | L1R3 | 2026-10-18T04:14:26 | versions/ECO-113-L1R3.md | e0b35a880ab1 | write #48 + replay to #66 |
| ECO-112 | L3R1 | 2026-10-18T04:36:06 | versions/ECO-112-L3R1.md | 068bc2d2b946 | checkpoint 6035726b6a9bc78f@v3 + replay to #77 |
| ECO-112 | L3R2 | 2026-10-18T04:38:31 | versions/ECO-112-L3R2.md | 03fc774bec67 | checkpoint 6035726b6a9bc78f@v3 + replay to #85 |
| ECO-112 | L3R3 | 2026-10-18T04:39:51 | versions/ECO-112-L3R3.md | 635623f21562 | checkpoint 6035726b6a9bc78f@v3 + replay to #91 |
| ECO-112 | L4R1 | 2026-10-18T04:45:17 | versions/ECO-112-L4R1.md | 771cfa069d97 | checkpoint 6035726b6a9bc78f@v4 + replay to #102 |
| ECO-112 | L4R2 | 2026-10-18T04:47:46 | versions/ECO-112-L4R2.md | b16c7aa6e636 | checkpoint 6035726b6a9bc78f@v4 + replay to #109 |
| ECO-113 | L2R1 | 2026-10-18T04:47:46 | versions/ECO-113-L2R1.md | eccfee95d7c8 | write #110 |
| ECO-112 | L4R3 | 2026-10-18T04:48:09 | versions/ECO-112-L4R3.md | 7011242c25dc | checkpoint 6035726b6a9bc78f@v4 + replay to #111 |
| ECO-113 | L2R2 | 2026-10-18T04:52:36 | versions/ECO-113-L2R2.md | 9f9cf4dd38aa | write #110 + replay to #122 |
| ECO-113 | L2R3 | 2026-10-18T04:55:05 | versions/ECO-113-L2R3.md | 1a571a03dead | write #110 + replay to #127 |
| ECO-112 | L5R1 | 2026-10-18T05:43:23 | versions/ECO-112-L5R1.md | d8c78c2700a8 | checkpoint 6035726b6a9bc78f@v5 + replay to #133 |
| ECO-113 | L3R1 | 2026-10-18T05:43:24 | versions/ECO-113-L3R1.md | 86445c863adf | checkpoint 7789ce16d0a36d94@v4 + replay to #138 |
| ECO-112 | L5R2 | 2026-10-18T05:44:30 | versions/ECO-112-L5R2.md | 32a2196dffdd | checkpoint 6035726b6a9bc78f@v5 + replay to #142 |
| ECO-112 | L5R3 | 2026-10-18T05:46:29 | versions/ECO-112-L5R3.md | 507a5cf933bc | checkpoint 6035726b6a9bc78f@v5 + replay to #157 |
| ECO-113 | L3R2 | 2026-10-18T05:46:30 | versions/ECO-113-L3R2.md | 03b147af0781 | checkpoint 7789ce16d0a36d94@v4 + replay to #158 |
| ECO-113 | L3R3 | 2026-10-18T05:47:43 | versions/ECO-113-L3R3.md | 0f75574d4ba8 | checkpoint 7789ce16d0a36d94@v4 + replay to #166 |
| ECO-112 | L5R4 | 2026-10-18T09:19:34 | versions/ECO-112-L5R4.md | a415b0a76d5b | checkpoint 6035726b6a9bc78f@v6 |
| ECO-113 | L4R1 | 2026-10-18T09:20:21 | versions/ECO-113-L4R1.md | dfec80141c57 | checkpoint 7789ce16d0a36d94@v5 + replay to #175 |
| ECO-113 | L4R2 | 2026-10-18T09:21:32 | versions/ECO-113-L4R2.md | be7211fcb6f2 | checkpoint 7789ce16d0a36d94@v5 + replay to #182 |
| ECO-113 | L4R3 | 2026-10-18T09:22:35 | versions/ECO-113-L4R3.md | e8dea94cfd1d | checkpoint 7789ce16d0a36d94@v5 + replay to #185 |
| ECO-113 | L5R1 | 2026-10-18T10:48:05 | versions/ECO-113-L5R1.md | 440f695a6658 | checkpoint 6aec2b20f6061e17@v1 + replay to #227 (shell) |
| ECO-113 | L5R2 | 2026-10-18T10:53:58 | versions/ECO-113-L5R2.md | 0951faff12d8 | checkpoint 6aec2b20f6061e17@v1 + replay to #240 |
| ECO-113 | L5R3 | 2026-10-18T10:56:09 | versions/ECO-113-L5R3.md | c1ead8202572 | checkpoint 6aec2b20f6061e17@v1 + replay to #252 |
| ECO-112 | AR1 | 2026-10-18T12:03:16 | versions/ECO-112-AR1.md | 62fa4da41c46 | git ced3ffc + replay to #355 (shell) |
| ECO-112 | AR2 | 2026-10-18T12:05:20 | versions/ECO-112-AR2.md | 1db015eda5b1 | git ced3ffc + replay to #362 |
| ECO-112 | AR3 | 2026-10-18T12:06:29 | versions/ECO-112-AR3.md | d4483f953849 | git ced3ffc + replay to #366 |
| ECO-112 | A2R1 | 2026-10-18T12:19:08 | versions/ECO-112-A2R1.md | aada5c39bb1c | checkpoint 6035726b6a9bc78f@v9 + replay to #370 |
| ECO-112 | A2R2 | 2026-10-18T12:23:34 | versions/ECO-112-A2R2.md | be511b9fe7c4 | checkpoint 6035726b6a9bc78f@v9 + replay to #376 |
| ECO-112 | A2R3 | 2026-10-18T12:25:21 | versions/ECO-112-A2R3.md | 8357f04c0a3c | checkpoint 6035726b6a9bc78f@v9 + replay to #387 |
| ECO-112 | A2R4 | 2026-10-18T12:59:14 | versions/ECO-112-A2R4.md | fbca47b6ac5c | checkpoint 6035726b6a9bc78f@v10 + replay to #397 |

## Origin time

INITIAL is shown by its basis: a quote found in the first reviewed version, or the finding being reported in the ECO's first round (that round reviewed the first version itself).

| ECO | INITIAL (quote) | INITIAL (first round) | LATER | UNKNOWN | total |
|---|---|---|---|---|---|
| ECO-112 | 5 | 14 | 21 | 23 | 63 |
| ECO-113 | 3 | 9 | 21 | 17 | 50 |
| both | 8 | 23 | 42 | 40 | 113 |

## By loop

| ECO | loop | rounds | findings | INITIAL | LATER | UNKNOWN |
|---|---|---|---|---|---|---|
| ECO-112 | L1 | 3 | 32 | 18 | 3 | 11 |
| ECO-112 | L2 | 3 | 9 | 0 | 4 | 5 |
| ECO-112 | L3 | 3 | 7 | 1 | 1 | 5 |
| ECO-112 | L4 | 3 | 2 | 0 | 1 | 1 |
| ECO-112 | L5 | 4 | 3 | 0 | 2 | 1 |
| ECO-112 | AR | 3 | 5 | 0 | 5 | 0 |
| ECO-112 | A2 | 4 | 5 | 0 | 5 | 0 |
| ECO-113 | L1 | 3 | 21 | 12 | 3 | 6 |
| ECO-113 | L2 | 3 | 14 | 0 | 6 | 8 |
| ECO-113 | L3 | 3 | 9 | 0 | 6 | 3 |
| ECO-113 | L4 | 3 | 2 | 0 | 2 | 0 |
| ECO-113 | L5 | 3 | 4 | 0 | 4 | 0 |

## UNKNOWN, by reason

| reason | findings |
|---|---|
| no usable quote | 22 |
| no quoted text in the finding | 17 |
| quotes disagree | 1 |

## Cause (recorded only) against origin time

| cause | INITIAL | LATER | UNKNOWN | total |
|---|---|---|---|---|
| FIX_CHANGE | 0 | 14 | 2 | 16 |
| EXISTING | 0 | 7 | 2 | 9 |
| UNKNOWN | 31 | 21 | 36 | 88 |

Type DUPLICATION (recorded): 3.

## LATER: where the quoted text first appeared

A reviewed version is the one produced by the repairs after the round before it, so "new in the reporting round's version" means the text came from the repairs just before that round.

| ECO | new in the reporting round's version | in an earlier round's version of the same loop | from an earlier loop |
|---|---|---|---|
| ECO-112 | 11 | 1 | 9 |
| ECO-113 | 10 | 6 | 5 |

## Severity (the reviewer's tag) against origin time

| severity | INITIAL | LATER | UNKNOWN |
|---|---|---|---|
| material | 20 | 13 | 10 |
| minor | 11 | 29 | 30 |
| not stated | 0 | 0 | 0 |

## Limits

- The time measured is the quoted text's appearance in a reviewed version, not the defect's cause.
- A finding with no quote, or whose quotes are paraphrases or cited code, is UNKNOWN; nothing is filled in by reading.
- A quote can match an unrelated occurrence of the same words; the minimum length is 15 characters after normalisation.
- ECO-113's first reviewed version was written from ECO-112's pre-split draft; text carried over reads INITIAL for ECO-113.
- Versions are rebuilt from the session's own records; where a shell command may have changed a document between anchors and the next anchor differs, the versions in between are UNKNOWN.
