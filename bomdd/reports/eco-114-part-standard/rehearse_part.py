"""ECO-114 design evidence: C1 and A1 applied as the order states them, so the rules meet real BOMs by execution.

Evidence only; the method does not ship it (ECO-114 M1). Library use (run_rehearsal.py) or:
    python rehearse_part.py <30-ebom.yaml> <32-mbom.yaml> <33-control-plan.yaml>
prints the failures as JSON (sorted; the same inputs give the same bytes). A failure is (clause, entry, text).
"""
import json
import sys

import yaml


def check(ebom_doc, mbom_doc, cp_doc):
    items = {i["id"]: i for i in ebom_doc["ebom"]["items"]}
    units = mbom_doc["mbom"]["manufacturing_units"]
    rows = {r["id"]: r for r in (cp_doc.get("control_plan") or cp_doc).get("characteristics") or []}
    by_unit = {u["id"]: u for u in units}
    refs = {u["id"]: set(u.get("ebom_refs") or []) for u in units}
    std = {u["id"]: u["part_standard"] for u in units if u.get("part_standard")}
    procurement = {p.get("package") for p in mbom_doc.get("procurement") or []}
    fails = []
    provides = {e["id"]: uid for uid, s in std.items() for e in s.get("provides") or []}
    ifs = {e["id"]: iid for iid, i in items.items() for e in (i.get("interfaces") or {}).get("provides") or []}
    realizers = {f: [uid for uid, s in std.items() for e in s.get("provides") or []
                     if e.get("ruled_ref") == f and ifs[f] in refs[uid]] for f in ifs}

    # units with no ebom_refs that take an IF- or an E-item unit's PS-, directly or through other such units
    # (A1 4: an E-item unit may not take their PS- entries)
    takes_from_items = {uid for uid, s in std.items() if not refs[uid] and any(
        e.get("target", "").startswith("IF-") or (e.get("target") in provides and refs[provides[e["target"]]])
        for e in s.get("requires") or [])}
    grown = True
    while grown:
        more = {uid for uid, s in std.items() if not refs[uid] and uid not in takes_from_items and any(
            e.get("target") in provides and provides[e["target"]] in takes_from_items for e in s.get("requires") or [])}
        takes_from_items |= more
        grown = bool(more)

    def e_requires(iid):
        return {x.get("target", x) if isinstance(x, dict) else x for x in (items[iid].get("interfaces") or {}).get("requires") or []}

    # clause 2: every IF- in the E-BOM is realized by exactly one unit
    for f, iid in sorted(ifs.items()):
        if len(realizers[f]) != 1:
            fails.append(("A1-2", f, f"realized by {len(realizers[f])} units"))
    for uid, s in sorted(std.items()):
        ids = [e["id"] for e in (s.get("provides") or []) + (s.get("requires") or [])]
        if len(ids) != len(set(ids)):
            fails.append(("P1", uid, "entry IDs not unique"))
        for e in s.get("provides") or []:
            if "ruled_ref" in e:  # clause 3
                if e["ruled_ref"] not in ifs or ifs[e["ruled_ref"]] not in refs[uid]:
                    fails.append(("A1-3", e["id"], f"ruled_ref {e['ruled_ref']} is not an IF- of the unit's E items"))
        resolved = set()
        for e in s.get("requires") or []:
            t = e.get("target", "")
            if t.startswith("procurement:"):
                if t[len("procurement:"):] not in procurement:
                    fails.append(("A1-1", e["id"], f"{t} has no procurement entry"))
            elif t.startswith("platform:"):
                pass
            elif t.startswith("IF-"):
                if t not in ifs:
                    fails.append(("A1-1", e["id"], f"{t} names no IF-"))
                    continue
                if len(realizers[t]) == 1:
                    resolved.add(realizers[t][0])
                else:
                    fails.append(("A1-1", e["id"], f"{t} does not resolve to one unit"))
                if refs[uid] and ifs[t] not in refs[uid] and not any(t in e_requires(i) for i in refs[uid]):
                    fails.append(("A1-1", e["id"], f"{t} is not required by any of the unit's E items"))
            elif t in provides:
                p = provides[t]
                resolved.add(p)
                if refs[uid] and refs[p] and not (refs[uid] & refs[p]):  # clause 4
                    fails.append(("A1-4", e["id"], f"{t} crosses E items without a ruling"))
                if refs[uid] and not refs[p] and p in takes_from_items:
                    fails.append(("A1-4", e["id"], f"{t}: relays through {p}, a unit with no ebom_refs that takes from E items"))
            else:
                fails.append(("A1-1", e["id"], f"target {t!r} names no entry"))
        if by_unit[uid].get("depends_on") and set(by_unit[uid]["depends_on"]) != resolved:  # clause 6 (a non-empty list)
            fails.append(("A1-6", uid, f"depends_on {sorted(by_unit[uid].get('depends_on') or [])} != resolved {sorted(resolved)}"))
    # clause 5 and 7: E-BOM interfaces.requires
    for iid, i in sorted(items.items()):
        for f in sorted(e_requires(iid)):
            if f not in ifs:
                fails.append(("A1-7", iid, f"interfaces.requires {f} names no IF-"))
                continue
            prov = ifs[f]
            ge = items[prov].get("graph_edges") or {}
            if prov not in (i.get("depends_on") or []) and iid not in (ge.get("consumers") or []):
                fails.append(("A1-7", iid, f"{f}: {prov} is not connected to {iid}"))
            cons = [uid for uid in std if iid in refs[uid]]
            if not cons:
                continue  # no consuming unit has a standard yet (lazy rule)
            if any(prov in refs[uid] for uid in cons):
                continue  # one unit realizes both items
            if not any(e.get("target") == f for uid in cons for e in std[uid].get("requires") or []):
                fails.append(("A1-5", iid, f"no unit realizing {iid} requires {f}"))
    # C1: every provides entry listed by a row in its unit's acceptance_refs; part_standard_refs name existing entries
    for uid, s in sorted(std.items()):
        acc = set(by_unit[uid].get("acceptance_refs") or [])
        for e in s.get("provides") or []:
            listing = [rid for rid, r in rows.items() if e["id"] in (r.get("part_standard_refs") or [])]
            if not listing:
                fails.append(("C1", e["id"], "listed by no row"))
            elif not acc & set(listing):
                fails.append(("C1", e["id"], f"listed only by rows outside {uid}'s acceptance_refs: {sorted(listing)}"))
    for rid, r in sorted(rows.items()):
        for ref in r.get("part_standard_refs") or []:
            if ref not in provides:
                fails.append(("C1", rid, f"part_standard_refs {ref} names no provides entry"))
    return sorted(set(fails))


def main():
    docs = [yaml.safe_load(open(p, encoding="utf-8")) for p in sys.argv[1:4]]
    print(json.dumps(check(*docs), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
