# worklist implementation decisions

Each line below records one discretionary choice or interpretation made while implementing the CAD.

- A01 (U1): Worklist rows use unpadded “- ID | state | origin | section-date | coordinate — body” fields; normal mode truncates only the body to 72 Unicode code points and uses “…” while --full never truncates it, because fixed padding adds little value to mixed-width Japanese text.
- A02 (U2): Warning text is concise English after the mandated line/code prefix, missing/read errors begin with “error:” and include the path, and usage errors print a one-line “usage:” string; only tokens and prefixes fixed by the CAD are treated as externally exact.
- A03 (U3): Generated output uses UTF-8 with LF newlines, no trailing spaces, one blank line between the five report sections, and one final newline from print.
- A04 (U4): elapsed_ms is floor-rounded monotonic wall-clock milliseconds measured with time.perf_counter from immediately before input reading through parsing, excluding report rendering and stdout I/O.
- A05 (U5): show prints ID, status, origin, body, and section in that order, then every attached source and evidence in input order; a due watch gains ★DUE, duplicate IDs resolve to the first valid occurrence, and absence prints “not found: ID”.
- A06 (U6): With no marker and no migration section, legacy coverage begins with “境界なし・全 legacy 節が未棚卸し”, reports audited as zero, and then uses the normal unaudited count/list.
- A07 (U7): Legacy section titles are truncated to 100 Unicode code points with “…”, while other list text is not truncated except the worklist body governed by U1.
- A08 (U8): Argument handling is strict but non-gating: unknown/repeated flags, extra positionals, show with flags (including --full), and combinations involving --selftest print one-line usage and exit 0; show is recognized only as the first argument, --full may appear before or after the one normal path, and paths beginning with “--” are not representable.
- A09 (U9): A physical blank line terminates continuation attachment; consecutive indented source:, evidence:, and origin: lines without a blank or other visible nonempty line all attach to the preceding valid item.
- A10 (U10): A nonempty unaudited list is introduced by “unaudited(未棚卸し — 要確認): N 節”; an empty list uses the CAD-mandated “unaudited: 0 節”.
- A11 (U11): The worklist has no column-heading row; the mandated native/migrated count line directly precedes item rows.
- A12: Only content belonging to a recognized, non-excluded “## ” section is eligible to become an item or warning; preamble content is ignored because item semantics require a section.
- A13: Section headers must start in column zero exactly with “## ”; headers inside fences, blockquotes, or HTML comments are excluded like tracking examples.
- A14: Fences use conventional Markdown mechanics: an opener has up to three leading spaces and at least three identical backticks or tildes, and a closer uses the same character with at least the opener length; all lines from opener through closer are excluded.
- A15: A line whose first non-whitespace character is “>” is treated as a blockquote and excluded in full, including nested or indented blockquotes.
- A16: HTML comments are removed with multiline state while preserving visible text before and after comment spans; comment-only lines do not themselves break continuation attachment, but an actual blank line does.
- A17: The audit cutoff is the first raw physical line containing “worklist-legacy-audit-cutoff:” followed by a syntactically shaped date, regardless of fences, blockquotes, or comments, matching the raw-text rule; the date value is not used for positional classification.
- A18: Section dates and closed-state dates are syntax-checked only (YYYY-MM-DD, or YYYY-MM for a section), not calendar-validated; the first full-date-or-month textual match wins.
- A19: Tracking IDs use ASCII letters and digits in the coordinate segment because the CAD says English alphanumerics; matching is case-sensitive and the two-digit suffix is exact.
- A20: A bracket bullet is warning-eligible only when it contains a complete syntactically valid tracking ID anywhere; a bracket bullet without such an ID stays silent as required for ordinary Markdown links.
- A21: Each malformed candidate emits one primary warning using precedence W2 unknown first word, then W3 malformed closed marker, W4 watch with a missing or ill-shaped one-digit N/3 value, then W6 for an extra-word watch/open marker or malformed body; a direct unbracketed candidate emits W5.
- A22: W6 covers a valid exact marker followed by a malformed “ID — nonempty body” portion and extra words in an open marker; whitespace around the em dash may be one or more spaces or tabs, while the em dash is mandatory.
- A23: W1 is emitted once at each valid occurrence after the first occurrence of an ID, points to the first line, and all otherwise valid duplicates remain counted because only W2–W6 rows are expressly excluded from item counts.
- A24: A section becomes structured when it contains either a valid item or a malformed bullet that emits W2–W6; duplicate W1 needs no additional classification because both valid rows already make their sections structured.
- A25: watch N/3 accepts exactly one decimal digit as specified, including 0 and 4–9; every N greater than or equal to 3 is due.
- A26: Closed-state via evidence must contain at least one non-whitespace character; everything after “via ” is retained as the marker without interpreting evidence syntax.
- A27: Multiple source or evidence continuation lines are preserved and shown in occurrence order; the last valid “origin: native|migrated” wins, while an unrecognized or empty origin is ignored because output origin is constrained to those two values and no warning is specified.
- A28: Audit position is determined by the legacy section header line relative to the marker or last migration-section header; this gives each whole section one classification even if prose later spans a boundary line.
- A29: Migration fallback uses the last recognized section whose title contains the exact substring “移行残高”, whether structured or legacy, following the title-based definition without adding an item-presence condition.
- A30: File-not-found, other OS read failures, and invalid UTF-8 are all rendered to stdout and return 0 so incidental read errors do not leak Python tracebacks to stderr; only selftest failure returns 1.
- A31: The default path is computed from the resolved script location and relative user paths are left to pathlib to resolve against the current working directory, preserving the cross-platform path contract.
- A32: The selftest is an isolated in-memory positive control and prints only its PASS/FAIL result rather than the five-section normal report; it asserts every required feature and reports failed assertion labels on stdout.