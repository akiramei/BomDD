"""ECO-114 / ECO-115 basis: every structural shape the two products' BOMs (and the templates' own examples) take, read-only.

Usage: python shapes.py <BomDD repo> <ViewPrism2 repo> <ViewTube repo> <out file>
ViewPrism2 at HEAD; ViewTube's E-BOM and M-BOM at HEAD and its control plan at fc35bf1d (HEAD does not parse); the templates from the BomDD
working tree. Enumerates: units by ebom_refs count, E items by realizing-unit count, units with empty acceptance_refs, rows by naming-unit count,
E-item connections by depends_on / graph_edges.consumers, M-BOM depends_on, row field forms, control plan header keys, retired rows.
"""
import collections
import subprocess
import sys

import yaml


def show(repo, rev, path):
    if rev is None:
        return yaml.safe_load(open(f"{repo}/{path}", encoding="utf-8"))
    out = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout
    return yaml.safe_load(out.decode("utf-8"))


def form(v):
    if v is None:
        return "absent"
    if isinstance(v, dict):
        return "map(" + ",".join(sorted(map(str, v))) + ")"
    if isinstance(v, list):
        return f"list[{len(v)}]"
    return "scalar"


def survey(out, name, ebom, mbom, cp):
    items = ebom["ebom"]["items"]
    units = mbom["mbom"]["manufacturing_units"]
    rows = (cp.get("control_plan") or cp).get("characteristics") or []
    out.append(f"== {name}")
    out.append(f"  E items {len(items)}; M units {len(units)}; CP rows {len(rows)}; M-BOM top keys {sorted(mbom['mbom'])}")
    by_refs = collections.Counter(min(len(u.get("ebom_refs") or []), 2) for u in units)
    out.append(f"  units by ebom_refs count (0/1/2+): {by_refs.get(0, 0)}/{by_refs.get(1, 0)}/{by_refs.get(2, 0)}; "
               f"with 0: {[u['id'] for u in units if not u.get('ebom_refs')]}")
    realized = collections.Counter(r for u in units for r in (u.get("ebom_refs") or []))
    by_real = collections.Counter(min(realized.get(i["id"], 0), 2) for i in items)
    out.append(f"  E items by realizing-unit count (0/1/2+): {by_real.get(0, 0)}/{by_real.get(1, 0)}/{by_real.get(2, 0)}; "
               f"with 0: {[i['id'] for i in items if not realized.get(i['id'])]}")
    out.append(f"  unit ebom_refs naming no E item: {sorted({r for r in realized if r not in {i['id'] for i in items}})}")
    out.append(f"  units with empty acceptance_refs: {[u['id'] for u in units if not u.get('acceptance_refs')]}")
    named = collections.Counter(r for u in units for r in (u.get("acceptance_refs") or []))
    by_named = collections.Counter(min(named.get(r["id"], 0), 2) for r in rows)
    out.append(f"  CP rows by naming-unit count (0/1/2+): {by_named.get(0, 0)}/{by_named.get(1, 0)}/{by_named.get(2, 0)}")
    dep = {(i["id"], d) for i in items for d in (i.get("depends_on") or [])}
    ge = {(c, i["id"]) for i in items if isinstance(i.get("graph_edges"), dict) for c in (i["graph_edges"].get("consumers") or [])}
    out.append(f"  E connections: depends_on edges {len(dep)}; graph_edges consumer edges (consumer, holder) {len(ge)}; "
               f"in both {len(dep & ge)}; items with non-empty consumers {sum(1 for i in items if isinstance(i.get('graph_edges'), dict) and i['graph_edges'].get('consumers'))}")
    out.append(f"  M-BOM units with non-empty depends_on: {sum(1 for u in units if u.get('depends_on'))}")
    for field in ("approver", "when", "on_fail", "status", "verifies", "level"):
        out.append(f"  row {field} forms: {dict(collections.Counter(form(r.get(field)) for r in rows))}")
    header = sorted(k for k in (cp.get("control_plan") or cp) if k != "characteristics")
    out.append(f"  control plan header keys: {header}")
    out.append(f"  retired rows: {[r['id'] for r in rows if r.get('status') == 'retired']}; named by a unit: "
               f"{[r['id'] for r in rows if r.get('status') == 'retired' and named.get(r['id'])]}")


def main():
    bomdd, vp2, vt, path = sys.argv[1:5]
    out = []
    survey(out, "ViewPrism2 at HEAD " + subprocess.run(["git", "-C", vp2, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           show(vp2, "HEAD", "bomdd/30-ebom.yaml"), show(vp2, "HEAD", "bomdd/32-mbom.yaml"), show(vp2, "HEAD", "bomdd/33-control-plan.yaml"))
    survey(out, "ViewTube E/M at HEAD " + subprocess.run(["git", "-C", vt, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
           + ", control plan at fc35bf1d",
           show(vt, "HEAD", "bomdd/30-ebom.yaml"), show(vt, "HEAD", "bomdd/32-mbom.yaml"), show(vt, "fc35bf1d", "bomdd/33-control-plan.yaml"))
    survey(out, "templates (BomDD working tree)", show(bomdd, None, "method/templates/30-ebom.yaml"),
           show(bomdd, None, "method/templates/32-mbom.yaml"), show(bomdd, None, "method/templates/33-control-plan.yaml"))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
