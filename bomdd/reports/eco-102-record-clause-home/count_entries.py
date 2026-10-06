#!/usr/bin/env python3
"""ECO-102 (r2): count the ViewTube M-BOM's invariant ENTRIES by the record kinds, and copy every entry in full.

An entry is one list item under a manufacturing unit's `invariants:` - a line matching `^    - '` and every following line
until the next line that is indented by 4 spaces or fewer and is not blank (the next item or the next key). Independent
inspection r1 (IA-02) found r1's copy carried the first physical line of each entry only, while r1's counts were over every
physical line of the file; the counts here are per entry and the copy is complete, so a reader can recount from the copy.

  python count_entries.py <32-mbom.yaml> <copy-path>"""
import io
import re
import sys

src, out = sys.argv[1], sys.argv[2]
lines = io.open(src, encoding="utf-8").read().split("\n")
entries, cur = [], None
for line in lines:
    if re.match(r"^    - '", line):
        if cur:
            entries.append(cur)
        cur = [line]
    elif cur is not None:
        if line.strip() and re.match(r"^ {0,4}\S", line):
            entries.append(cur)
            cur = None
        else:
            cur.append(line)
if cur:
    entries.append(cur)
texts = ["\n".join(e) for e in entries]
io.open(out, "w", encoding="utf-8", newline="\n").write("\n".join(texts) + "\n")

KINDS = [
    ("begin with an ECO id", r"^    - 'ECO-VT-"),
    ("mention a measurement (measured)", r"measured"),
    ("mention a review, a round or a finding id", r"review|R[0-9]+[a-z]-F[0-9]+|round"),
    ("carry a not-exercised / not-covered note", r"not exercised|not covered|not measured|unmeasured|no case|not captured|not yet"),
    ("mention a ruling", r"ruling"),
]
print(f"entries: {len(texts)} (physical lines in the entries: {sum(len(e) for e in entries)}); copy: {out.split('/')[-1]}")
for name, pattern in KINDS:
    n = sum(1 for t in texts if re.search(pattern, t, re.I | re.M))
    print(f"  entries that {name}: {n}")
