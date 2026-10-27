"""Derive ECO-VT-270's Control Plan approver changes from the parsed file at two commits (no typed counts).
python -B cp_approver_diff.py <repo> <before> <after>"""
import subprocess
import sys
from collections import Counter

import yaml

repo, before, after = sys.argv[1:4]


def rows(rev):
    text = subprocess.run(["git", "-C", repo, "show", f"{rev}:bomdd/33-control-plan.yaml"], capture_output=True, check=True).stdout
    doc = yaml.safe_load(text.decode("utf-8"))
    out = {}

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("id"), str) and x["id"].startswith("CP-") and "approver" in x:
                out[x["id"]] = x
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(doc)
    return out


a, b = rows(before), rows(after)
changes = Counter()
for rid in sorted(set(a) | set(b)):
    pa, pb = a.get(rid, {}).get("approver"), b.get(rid, {}).get("approver")
    if pa != pb:
        changes[f"{pa} -> {pb}"] += 1
kl = sum(1 for rid in b if b[rid].get("known_limits") != a.get(rid, {}).get("known_limits"))
print("rows with approver:", len(a), "->", len(b))
for k, v in sorted(changes.items()):
    print(f"  {v:3d}  {k}")
print("approver changes:", sum(changes.values()), "; known_limits changed:", kl)
