#!/usr/bin/env python3
"""ECO-102 (r3): the measurements behind the order's §0.2, taken by parsing the M-BOMs with PyYAML (not by grep on physical
lines, r1, nor by a regex over quoted items only, r2 - r2's "60 entries" were the quoted items that begin with an ECO id; the
`invariants:` lists also hold unquoted items). Copies of every counted text are written beside this script so that a reader who
cannot open the product repositories can recount.

  python count_records.py <viewtube-repo> <viewprism2-repo> <out-dir>

Counted, per invariant ENTRY (one element of a unit's `invariants:` list) and per ECO BODY (bomdd/eco/ECO-VT-NNN.md):
  measured   measured | 実測 | 測った | 測定
  review     review | round | R<n><a>-F<n> | レビュー | 所見
  untested   not exercised | not covered | not measured | unmeasured | no case | not captured | not yet | 測っていない | 未検査 | 未測定
  ruling     ruling | 裁定 | 利用者の判断
  eco_id     an ECO id anywhere (ECO-VT-NNN / ECO-NNN) ; eco_start = the entry begins with one"""
import io
import os
import re
import sys

import yaml

VT, VP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
VOCAB = {
    "measured": r"measured|実測|測った|測定",
    "review": r"review|round|R[0-9]+[a-z]-F[0-9]+|レビュー|所見",
    "untested": r"not exercised|not covered|not measured|unmeasured|no case|not captured|not yet|測っていない|未検査|未測定",
    "ruling": r"ruling|裁定|利用者の判断",
}


def entries(path):
    d = yaml.safe_load(io.open(path, encoding="utf-8"))
    units = (d.get("mbom") or d)["manufacturing_units"]
    out = []
    for u in units:
        for inv in u.get("invariants") or []:
            out.append((u.get("id", "?"), str(inv)))
    return out


def count(texts, label):
    print(f"{label}: entries {len(texts)}")
    print(f"  begin with an ECO id: {sum(1 for t in texts if re.match(r'ECO-(VT-)?\d+', t))}")
    print(f"  mention an ECO id anywhere: {sum(1 for t in texts if re.search(r'ECO-(VT-)?\d+', t))}")
    for k, p in VOCAB.items():
        print(f"  {k}: {sum(1 for t in texts if re.search(p, t, re.I))}")


def write(name, text):
    io.open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n").write(text)


vt = entries(os.path.join(VT, "bomdd/32-mbom.yaml"))
vp = entries(os.path.join(VP, "bomdd/32-mbom.yaml"))
write("viewtube-32-mbom-invariant-entries.txt", "\n".join(f"[{u}]\n{t}\n" for u, t in vt))
write("viewprism2-32-mbom-invariant-entries.txt", "\n".join(f"[{u}]\n{t}\n" for u, t in vp))
count([t for _, t in vt], "ViewTube 32-mbom")
count([t for _, t in vp], "ViewPrism2 32-mbom")

# The ECO bodies and register entries behind the ViewTube entries that begin with an ECO id.
ids = sorted({re.match(r"ECO-VT-\d+", t).group(0) for _, t in vt if re.match(r"ECO-VT-\d+", t)},
             key=lambda s: int(s.split("-")[-1]))
reg = io.open(os.path.join(VT, "bomdd/process/change-register.yaml"), encoding="utf-8").read()
bodies = {}
for i in ids:
    p = os.path.join(VT, "bomdd/eco", i + ".md")
    bodies[i] = io.open(p, encoding="utf-8").read() if os.path.exists(p) else None
print(f"ViewTube: distinct ECO ids beginning an entry: {len(ids)}; with a body file: {sum(1 for b in bodies.values() if b)}; "
      f"with a register entry: {sum(1 for i in ids if f'  - id: {i}' in reg)}")
for k, p in VOCAB.items():
    print(f"  bodies that carry {k}: {sum(1 for b in bodies.values() if b and re.search(p, b, re.I))} of {len(ids)}")
write("viewtube-eco-ids-of-the-entries.txt", "\n".join(f"{i} body={'yes' if bodies[i] else 'no'} register={'yes' if f'  - id: {i}' in reg else 'no'}" for i in ids) + "\n")

# One body and its register entry as the example the order cites.
ex = "ECO-VT-232"
write("viewtube-eco-vt-232-body.md", bodies[ex] or "")
i0 = reg.index(f"  - id: {ex}\n")
j0 = reg.find("\n  - id: ", i0 + 5)
write("viewtube-register-eco-vt-232.yaml", reg[i0:(len(reg) if j0 < 0 else j0 + 1)])
print("copies: viewtube-32-mbom-invariant-entries.txt viewprism2-32-mbom-invariant-entries.txt viewtube-eco-ids-of-the-entries.txt "
      "viewtube-eco-vt-232-body.md viewtube-register-eco-vt-232.yaml")
