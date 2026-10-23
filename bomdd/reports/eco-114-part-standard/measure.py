"""ECO-114 basis: how the two products' BOMs state part standards and connections today (read-only).

Usage: python measure.py <ViewPrism2 repo> <ViewTube repo> <out file>
Reads bomdd/30-ebom.yaml, 32-mbom.yaml and 33-control-plan.yaml at each repo's HEAD (git show, not the working tree),
and for ViewTube's control plan also each of its last 40 revisions. Writes one text report; prints nothing else.
"""
import collections
import subprocess
import sys

import yaml


def show(repo, rev, path):
    return subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout.decode("utf-8")


def head(repo):
    return subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, check=True, text=True, encoding="utf-8").stdout.strip()


def parse(text):
    try:
        return yaml.safe_load(text), None
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        return None, f"line {mark.line + 1}, column {mark.column + 1}" if mark else str(e).splitlines()[0]


def mbom(out, repo, rev):
    data, err = parse(show(repo, rev, "bomdd/32-mbom.yaml"))
    if err:
        out.append(f"  M-BOM: does not parse ({err})")
        return
    units = data["mbom"]["manufacturing_units"]
    ic = [u for u in units if u.get("interface_contract")]
    keys = collections.Counter()
    for u in ic:
        if isinstance(u["interface_contract"], dict):
            keys.update(u["interface_contract"].keys())
    exact = {k: keys[k] for k in ("provides", "requires", "signature") if keys[k]}
    out.append(f"  M-BOM units: {len(units)}; with interface_contract: {len(ic)}; "
               f"non-dict interface_contract: {sum(1 for u in ic if not isinstance(u['interface_contract'], dict))}")
    out.append(f"  M-BOM interface_contract keys named provides/requires/signature: {exact or 'none'}"
               f"; units with signature: {[u['id'] for u in ic if isinstance(u['interface_contract'], dict) and 'signature' in u['interface_contract']]}")
    out.append(f"  M-BOM interface_contract distinct keys: {len(keys)}; most common: {keys.most_common(8)}")
    out.append(f"  M-BOM units with non-empty depends_on: {sum(1 for u in units if u.get('depends_on'))}; "
               f"with non-empty acceptance_refs: {sum(1 for u in units if u.get('acceptance_refs'))}")


def ebom(out, repo, rev):
    data, err = parse(show(repo, rev, "bomdd/30-ebom.yaml"))
    if err:
        out.append(f"  E-BOM: does not parse ({err})")
        return
    items = data["ebom"]["items"]
    ge = [i for i in items if isinstance(i.get("graph_edges"), dict) and (i["graph_edges"].get("owner") or i["graph_edges"].get("consumers"))]
    keys = collections.Counter(k for i in items for k in i.keys())
    out.append(f"  E-BOM items: {len(items)}; with non-empty depends_on: {sum(1 for i in items if i.get('depends_on'))}; "
               f"with graph_edges owner/consumers: {len(ge)}")
    out.append(f"  E-BOM item keys named provides/requires/interface*/signature: "
               f"{ {k: v for k, v in keys.items() if k in ('provides', 'requires', 'signature') or k.startswith('interface')} or 'none'}")


def cp(out, repo, rev):
    text = show(repo, rev, "bomdd/33-control-plan.yaml")
    data, err = parse(text)
    out.append(f"  control plan mentions of 'interface' (case-insensitive, raw text): {text.lower().count('interface')}")
    if err:
        out.append(f"  control plan: does not parse as YAML ({err})")
        return
    rows = (data.get("control_plan") or data).get("characteristics") or []
    fields = collections.Counter(k for r in rows for k in r.keys())
    out.append(f"  control plan rows: {len(rows)}; rows with on_fail: {fields['on_fail']}; with when: {fields['when']}; "
               f"with requirement_refs: {fields['requirement_refs']}; with invariant_refs: {fields['invariant_refs']}")
    out.append(f"  approver automated: {sum(1 for r in rows if str(r.get('approver', '')).startswith('automated'))}; "
               f"depth exactly G: {sum(1 for r in rows if str(r.get('depth')) == 'G')}")


def history(out, repo, n=40):
    revs = subprocess.run(["git", "-C", repo, "log", f"-{n}", "--format=%h", "--", "bomdd/33-control-plan.yaml"],
                          capture_output=True, check=True, text=True, encoding="utf-8").stdout.split()
    results = [(r, parse(show(repo, r, "bomdd/33-control-plan.yaml"))[1]) for r in revs]
    ok = [r for r, e in results if e is None]
    out.append(f"  control plan revisions checked (newest first): {len(results)}; parse: {len(ok)}; do not parse: {len(results) - len(ok)}")
    out.append(f"  newest {results[0][0]}: {results[0][1] or 'parses'}; oldest checked {results[-1][0]}: {results[-1][1] or 'parses'}")
    for (newer, e_newer), (older, e_older) in zip(results, results[1:]):
        if e_newer is not None and e_older is None:
            subject = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%cs %s", newer],
                                     capture_output=True, check=True, text=True, encoding="utf-8").stdout.strip()
            out.append(f"  stops parsing at {newer} (previous revision {older} parses): {subject[:160]}")
    if ok:
        newest_ok = next(i for i, (_, e) in enumerate(results) if e is None)
        out.append(f"  revisions newer than the newest parsing one ({results[newest_ok][0]}): {newest_ok}, of which parse: "
                   f"{sum(1 for _, e in results[:newest_ok] if e is None)}")


def main():
    vp2, vt, path = sys.argv[1:4]
    out = []
    for name, repo in (("ViewPrism2", vp2), ("ViewTube", vt)):
        rev = head(repo)
        out.append(f"== {name} at {rev}")
        ebom(out, repo, rev)
        mbom(out, repo, rev)
        cp(out, repo, rev)
        if name == "ViewTube":
            history(out, repo)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
