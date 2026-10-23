"""ECO-115 basis: the Control Plan fields an advance decision would read, as the two products write them today (read-only).

Usage: python measure_cp_fields.py <ViewPrism2 repo> <ViewTube repo> <out file>
ViewPrism2 at HEAD; ViewTube at fc35bf1d, its newest control plan revision that parses (HEAD does not; ECO-114 report measurements.txt).
Reads 32-mbom.yaml and 33-control-plan.yaml with `git show`. Writes one text report.
"""
import collections
import subprocess
import sys

import yaml


def show(repo, rev, path):
    out = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout
    return yaml.safe_load(out.decode("utf-8"))


def resolve(repo, rev):
    return subprocess.run(["git", "-C", repo, "rev-parse", rev], capture_output=True, check=True, text=True).stdout.strip()


def survey(out, name, repo, rev):
    rev = resolve(repo, rev)
    cp = show(repo, rev, "bomdd/33-control-plan.yaml")
    rows = (cp.get("control_plan") or cp).get("characteristics") or []
    units = show(repo, rev, "bomdd/32-mbom.yaml")["mbom"]["manufacturing_units"]
    out.append(f"== {name} at {rev}")
    out.append(f"  rows: {len(rows)}")
    approver = collections.Counter(str(r["approver"]) if "approver" in r else "(none)" for r in rows)
    out.append(f"  approver values: {dict(approver.most_common())}")
    closed = {"automated"}
    outside = sum(n for v, n in approver.items() if v not in closed and not v.startswith("human:") and not v.startswith("automated+human:"))
    out.append(f"  rows whose approver is not automated, human:<role> or automated+human:<role> (incl. none): {outside}")
    for field in ("verifies", "on_fail", "when", "level", "status", "retired_by", "known_limits"):
        out.append(f"  rows with {field}: {sum(1 for r in rows if field in r)}")
    out.append(f"  when values: {dict(collections.Counter(str(r['when']) for r in rows if 'when' in r))}")
    out.append(f"  on_fail values: {[r['on_fail'] for r in rows if 'on_fail' in r]}")
    out.append(f"  depth values: {dict(collections.Counter(str(r.get('depth')) for r in rows).most_common())}")
    refs = collections.Counter(ref for u in units for ref in (u.get("acceptance_refs") or []))
    ids = {r["id"] for r in rows}
    out.append(f"  units: {len(units)}; rows named in some unit's acceptance_refs: {len(ids & set(refs))}; "
               f"rows in no unit's acceptance_refs: {len(ids - set(refs))}")
    out.append(f"  rows named by two or more units: {sum(1 for k, n in refs.items() if n >= 2)} (most: {max(refs.values()) if refs else 0})")
    out.append(f"  acceptance_refs IDs with no row: {sorted(set(refs) - ids)}")


def main():
    vp2, vt, path = sys.argv[1:4]
    out = []
    survey(out, "ViewPrism2", vp2, "HEAD")
    survey(out, "ViewTube", vt, "fc35bf1d")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
