#!/usr/bin/env python3
"""ECO-116 survey: where each product stands against ECO-115's advance decision as verified (BomDD ef1506a). Read only (git show at each HEAD).

  python -B survey.py <BomDD root> <output file> <product checkout> ...

Per product, at its HEAD: ECO-115's I3a structure and I2 checks on its M-BOM and Control Plan (rehearse_decision_v2.i3a, the rules as the
method states them), counted by route with each defect listed; the work order's frozen-revision line and bounds line (I1, I2); the newest
As-Built entry's fields the decision reads (frozen_commit, delivered, work_ref, the three refs' form, decision records); and whether the product
vendors the method's templates (a bomdd-kit copy that a distribution would also have to update).
"""
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

args = sys.argv[1:]
# --work-order <product name>=<repo-relative path>: where that product keeps the work order carrying the frozen-revision and bounds lines
# (converge round 1 L1R1-01: a product ECO may name a home other than bomdd/40-work-order.md); repeatable
wo_home = {}
while "--work-order" in args:
    i = args.index("--work-order")
    k, v = args[i + 1].split("=", 1)
    wo_home[k] = v
    del args[i:i + 2]
root, out_path, products = args[0], args[1], args[2:]
# converge round 3 L1R3-02: a --work-order key that names no surveyed product is an error, not a silent fall-back to the default path
unknown = sorted(set(wo_home) - {Path(p).name for p in products})
if unknown:
    sys.exit(f"survey.py: --work-order names no surveyed product: {', '.join(unknown)}")
sys.path.insert(0, str(Path(root) / "bomdd/reports/eco-115-advance-decision"))
import rehearse_decision_v2 as rd  # noqa: E402


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    return p.stdout.decode("utf-8", errors="replace") if p.returncode == 0 else None


lines = [f"ECO-116 survey at BomDD {git(root, 'rev-parse', '--short', 'HEAD').strip()} (ECO-115 verified ef1506a)"]
for repo in products:
    name = Path(repo).name
    head = git(repo, "rev-parse", "--short", "HEAD").strip()
    lines.append(f"\n== {name} at {head}")
    files = (git(repo, "ls-files") or "").split("\n")
    show = {k: git(repo, "show", f"HEAD:{p}") for k, p in
            (("mbom", "bomdd/32-mbom.yaml"), ("cp", "bomdd/33-control-plan.yaml"), ("wo", wo_home.get(name, "bomdd/40-work-order.md")), ("ab", "bomdd/50-as-built.yaml"))}
    defects, units, assembly, by_id, mapping = rd.i3a(show["mbom"] or "", show["cp"] or "")
    routes = Counter(r for r, _ in defects)
    lines.append(f"   I3a/I2 on the M-BOM and Control Plan: {len(defects)} defects {dict(sorted(routes.items()))}")
    kinds = Counter(re.sub(r"\b(CP|M|E|PS|REQ)-[A-Z0-9-]+\b", "<id>", t) for _, t in defects)
    for k, n in sorted(kinds.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"     {n:3d} x {k}")
    if units is not None:
        named = sorted({r for u in units for r in (u.get("acceptance_refs") or [])} | set((assembly or {}).get("acceptance_refs") or []))
        lines.append(f"   units {len(units)}, rows in the Control Plan {len(by_id)}, rows named {len(named)}, check_mapping "
                     f"{'present' if mapping else 'absent'}")
    wo = show["wo"] or ""
    fr = rd.frozen_revision(wo)
    home = wo_home.get(name, "bomdd/40-work-order.md")   # a local, so the f-string below runs on Python before 3.12 (round 2, L1R2-05)
    lines.append(f"   work order ({home}): frozen-revision line {'value ' + repr(fr) if fr else 'without a single valued line'}; bounds line "
                 f"{'absent' if not rd.BOUNDS_ANY.findall(wo) else ('within I2' if rd.bounds_defect(wo) is None else 'outside I2')}")
    try:
        entries = [e for e in (yaml.safe_load(show["ab"] or "") or {}).get("as_built") or [] if isinstance(e, dict)]
    except yaml.YAMLError:
        entries = None
    if not entries:
        lines.append(f"   As-Built: {'does not parse' if entries is None else 'no entry'}")
    else:
        e = entries[-1]
        refs = {k: bool(rd.REF.fullmatch(str(e.get(k, "")))) for k in ("work_order_ref", "mbom_ref", "control_plan_ref")}
        recs = [x for x in e.get("test_evidence_refs") or [] if isinstance(x, dict)]
        lines.append(f"   As-Built newest entry {e.get('id')}: frozen_commit {'yes' if e.get('frozen_commit') else 'no'}; delivered "
                     f"{'yes' if rd.delivered_ok(e.get('delivered')) else 'no'}; work_ref {'yes' if e.get('work_ref') else 'no'}; refs in I2 form "
                     f"{sum(refs.values())}/3; test_evidence_refs {len(recs)} (source: decision {sum(1 for x in recs if x.get('source') == 'decision')})")
    kit = sorted({f.split("/method/")[0] for f in files if "/method/templates/" in f})
    lines.append(f"   vendored method templates: {', '.join(kit) if kit else 'none'}")
Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
sys.stdout.reconfigure(encoding="utf-8")
print("\n".join(lines))
