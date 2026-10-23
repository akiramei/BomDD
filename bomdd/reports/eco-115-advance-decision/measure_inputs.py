"""ECO-115 basis: which of the two products' M-BOM units and Control Plan rows fall outside the decision's closed values (I2), read-only.

Usage: python measure_inputs.py <ViewPrism2 repo> <ViewTube repo> <out file>
Same revisions as measure_cp_fields.py (ViewPrism2 HEAD, ViewTube fc35bf1d). The closed values checked are ECO-115 I2 as filed:
approver automated | human:<role> | automated+human:<role>; when absent, one value or a list from acceptance, dependency-update;
on_fail keys red, unmeasurable with values product-fix, instrument-recovery, control-plan-fix; status absent or retired.
"""
import subprocess
import sys

import yaml

OCCASIONS = {"acceptance", "dependency-update"}
ROUTES = {"product-fix", "instrument-recovery", "control-plan-fix"}


def show(repo, rev, path):
    out = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout
    return yaml.safe_load(out.decode("utf-8"))


def outside(row):
    why = []
    a = row.get("approver")
    if not (a == "automated" or (isinstance(a, str) and (a.startswith("human:") or a.startswith("automated+human:")))):
        why.append("approver")
    w = row.get("when")
    if w is not None and not ((isinstance(w, str) and w in OCCASIONS) or (isinstance(w, list) and w and set(w) <= OCCASIONS)):
        why.append("when")
    f = row.get("on_fail")
    if f is not None and not (isinstance(f, dict) and set(f) <= {"red", "unmeasurable"} and set(f.values()) <= ROUTES):
        why.append("on_fail")
    if row.get("status") not in (None, "retired"):
        why.append("status")
    return why


def survey(out, name, repo, rev):
    cp = show(repo, rev, "bomdd/33-control-plan.yaml")
    rows = {r["id"]: r for r in (cp.get("control_plan") or cp).get("characteristics") or []}
    mbom = show(repo, rev, "bomdd/32-mbom.yaml")["mbom"]
    units = mbom["manufacturing_units"]
    named = sorted({ref for u in units for ref in (u.get("acceptance_refs") or [])})
    bad = {rid: outside(rows[rid]) for rid in named if rid in rows and outside(rows[rid])}
    reasons = {}
    for why in bad.values():
        for w in why:
            reasons[w] = reasons.get(w, 0) + 1
    out.append(f"== {name} at {rev}")
    out.append(f"  units: {len(units)}; units with empty acceptance_refs: {[u['id'] for u in units if not u.get('acceptance_refs')]}")
    out.append(f"  mbom keys: {sorted(mbom.keys())}")
    out.append(f"  rows named by some unit: {len(named)}; of them outside I2: {len(bad)}; by field: {reasons}")
    out.append(f"  named rows that are retired: {[r for r in named if rows.get(r, {}).get('status') == 'retired']}")
    out.append(f"  units whose named rows are all within I2: {sum(1 for u in units if u.get('acceptance_refs') and not any(r in bad for r in u['acceptance_refs']))}")


def main():
    vp2, vt, path = sys.argv[1:4]
    out = []
    survey(out, "ViewPrism2", vp2, subprocess.run(["git", "-C", vp2, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
    survey(out, "ViewTube", vt, "fc35bf1d")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
