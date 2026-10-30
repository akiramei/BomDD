"""EXP-20261030-03 - the deterministic checks and the tally (definitions.md sections 4-8).

Usage:
  python checks.py selftest              synthetic inputs only (touches no package)
  python checks.py run <staging-dir>     layer M on every Tnn/actions.txt, layer T on every Tnn/table.json,
                                         writes flags.json next to this file and prints the tally
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGES = {"T01": ("D1", "pre"), "T02": ("D1", "post"), "T03": ("D2", "pre"), "T04": ("D2", "post"),
            "T05": ("D3", "pre"), "T06": ("D3", "post")}

# layer M (section 4)
PAIRS = [("Assign", "Unassign"), ("Create", "Delete"), ("Create", "Remove"), ("Add", "Remove"), ("Archive", "Restore"),
         ("Archive", "Unarchive"), ("Register", "Unregister")]
PARTNERS = {}
for a, b in PAIRS:
    PARTNERS.setdefault(a, set()).add(b)
    PARTNERS.setdefault(b, set()).add(a)
FILLER = {"Batch", "Request", "Confirm", "Open", "Start", "Cancel", "Close", "Validate", "Toggle"}

# layer T (section 5)
KINDS = {"create", "delete", "assign", "unassign", "add", "remove", "archive", "restore", "update", "navigate", "view", "other"}
PAIRED = {"create", "delete", "assign", "unassign", "add", "remove", "archive", "restore"}
AVAIL = {"enabled", "disabled", "absent", "not_drawn"}
STOP = ("T2", "T3", "T4", "T5")

# matching (section 6): item -> (checks, patterns that must all match)
MATCH_T = {"D1": ({"T2", "T3"}, [r"(?i)assign|付与|付け|外す", r"(?i)tag|タグ"]),
           "D2": ({"T5"}, [r"(?i)tag|タグ"]),
           "D3": ({"T2", "T3", "T4"}, [r"(?i)manual|手動", r"(?i)collection|コレクション"])}
MATCH_M = {"D1": [r"(?i)assign", r"(?i)tag"], "D3": [r"(?i)collection"]}


def split(name):
    return re.findall(r"[A-Z][a-z0-9]*|[a-z0-9]+", name)


def verb_object(name):
    toks = split(name)
    verb = next((t for t in toks if t in PARTNERS), None)
    if verb is None:
        return None, None
    rest = list(toks)
    rest.remove(verb)
    return verb, "".join(t for t in rest if t not in FILLER)


def related(a, b):
    return a == b or bool(a and b and (a in b or b in a))


def layer_m(acts):
    """M1: an action whose verb has partners, with no other action of a partner verb and a related object."""
    parsed = {a: verb_object(a) for a in acts}
    flags = []
    for a, (verb, obj) in parsed.items():
        if verb is None:
            continue
        if not any(b != a and v in PARTNERS[verb] and related(obj, o) for b, (v, o) in parsed.items()):
            flags.append({"check": "M1", "action": a, "verb": verb, "object": obj})
    return flags


def validate(table):
    """Table-level shape is required (else None = no-table); a row failing its fields is dropped and counted."""
    if not isinstance(table, dict) or not all(isinstance(table.get(k), list) for k in ("states", "entities", "operations")):
        return None, None
    dropped = {"states": 0, "entities": 0, "operations": 0}
    states = [s for s in table["states"] if isinstance(s, dict) and isinstance(s.get("id"), str)
              and s.get("selection_possible") in (True, False, None)]
    entities = [e for e in table["entities"] if isinstance(e, dict) and isinstance(e.get("id"), str)]
    ops = []
    for o in table["operations"]:
        ok = (isinstance(o, dict) and isinstance(o.get("id"), str) and o.get("kind") in KINDS
              and (o.get("mock_action") is None or isinstance(o.get("mock_action"), str))
              and isinstance(o.get("text_refs"), list) and isinstance(o.get("owner_surfaces"), list)
              and (o.get("counterpart") is None or isinstance(o.get("counterpart"), str))
              and isinstance(o.get("availability"), dict) and all(v in AVAIL for v in o["availability"].values()))
        if ok:
            ops.append(o)
    dropped["states"] = len(table["states"]) - len(states)
    dropped["entities"] = len(table["entities"]) - len(entities)
    dropped["operations"] = len(table["operations"]) - len(ops)
    return {"states": states, "entities": entities, "operations": ops}, dropped


def layer_t(table, acts):
    acts = set(acts)
    ents = {e["id"]: e for e in table["entities"]}
    by_name = {e.get("name"): e for e in table["entities"]}
    ops = {o["id"]: o for o in table["operations"]}
    sel = [s["id"] for s in table["states"] if s.get("selection_possible") is True]

    def ent(o):
        return ents.get(o.get("entity")) or by_name.get(o.get("entity"))

    def text(o):
        e = ent(o)
        return " ".join(str(x) for x in (o["id"], o.get("label"), o.get("mock_action"), e and e.get("name")) if x)

    def drawn(o):
        return o.get("mock_action") in acts

    flags = []
    for a in sorted(acts - {o.get("mock_action") for o in ops.values()}):
        flags.append({"check": "T1", "key": a, "text": a})
    for o in ops.values():
        key = o.get("mock_action") or o["id"]
        if o["text_refs"] and not drawn(o):
            flags.append({"check": "T2", "key": key, "text": text(o)})
        if o["kind"] in PAIRED:
            c = ops.get(o["counterpart"]) if o["counterpart"] else None
            if c is None or not drawn(c):
                flags.append({"check": "T3", "key": key, "text": text(o)})
        avail = o["availability"]
        if any(avail.get(s) == "enabled" for s in sel) and any(avail.get(s, "not_drawn") in ("absent", "not_drawn") for s in sel):
            flags.append({"check": "T5", "key": key, "text": text(o)})
        if o["kind"] not in ("navigate", "view") and len(o["owner_surfaces"]) > 1:
            flags.append({"check": "T6", "key": key, "text": text(o)})
    for eid, e in ents.items():
        mine = [o for o in ops.values() if ent(o) is e]
        if mine and not any(o["kind"] in ("create", "add") and drawn(o) for o in mine):
            flags.append({"check": "T4", "key": eid, "text": " ".join(str(x) for x in (eid, e.get("name")) if x)})
    return flags


def matches(flag_text, patterns):
    return all(re.search(p, flag_text) for p in patterns)


def item_flags(item, layer, flags):
    if layer == "M":
        pats = MATCH_M.get(item)
        if pats is None:
            return None
        key = "object" if item == "D3" else "action"
        return [f for f in flags if matches(f[key], pats)]
    checks, pats = MATCH_T[item]
    return [f for f in flags if f["check"] in checks and matches(f["text"], pats)]


def tally(results):
    out = {}
    for layer in ("M", "T"):
        rows = {}
        for item in ("D1", "D2", "D3"):
            pre = next(p for p, v in PACKAGES.items() if v == (item, "pre"))
            post = next(p for p, v in PACKAGES.items() if v == (item, "post"))
            got = {}
            for state, pkg in (("pre", pre), ("post", post)):
                r = results[pkg].get(layer)
                got[state] = None if r is None or r.get("flags") is None else item_flags(item, layer, r["flags"])
            if layer == "M" and item not in MATCH_M:
                continue
            caught = bool(got["pre"]) and got["post"] is not None and not got["post"]
            rows[item] = {"pre_matching": got["pre"], "post_matching": got["post"], "caught": caught,
                          "false_alarm_on_post": bool(got["post"])}
        out[layer] = rows
    caught_t = sum(r["caught"] for r in out["T"].values())
    post_stop = {p: sum(1 for f in (results[p].get("T") or {}).get("flags") or [] if f["check"] in STOP)
                 for p, (_, s) in PACKAGES.items() if s == "post"}
    if caught_t >= 2:
        reading = ("usable as a stop" if all(n <= 25 for n in post_stop.values())
                   else "catches, but the stop needs an exception-ruling step of that size")
        reading = f"{caught_t}/3 caught - a prospective G2 stop trial in ViewTube is earned; {reading}"
    elif caught_t == 1:
        reading = "1/3 caught - no claim"
    else:
        reading = "0/3 caught - the table form does not reach these on these inputs"
    out["reading_T"] = reading
    out["post_stop_flags"] = post_stop
    return out


def jaccard(a, b):
    a, b = set(a), set(b)
    return round(len(a & b) / len(a | b), 3) if a | b else None


def run(stage):
    results = {}
    for pkg in PACKAGES:
        acts = [a for a in (stage / pkg / "actions.txt").read_text(encoding="utf-8").splitlines() if a]
        res = {"M": {"flags": layer_m(acts)}}
        tpath = stage / pkg / "table.json"
        if tpath.exists():
            try:
                table, dropped = validate(json.loads(tpath.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                table, dropped = None, None
        else:
            table, dropped = None, None
        res["T"] = ({"flags": None, "no_table": True} if table is None else
                    {"flags": layer_t(table, acts), "dropped": dropped,
                     "rows": {k: len(v) for k, v in table.items()}})
        results[pkg] = res
    summary = tally(results)
    t02, t03 = results["T02"]["T"], results["T03"]["T"]
    if t02.get("flags") is not None and t03.get("flags") is not None:
        summary["reproducibility_T02_T03"] = {
            "flag_jaccard": jaccard([(f["check"], f["key"]) for f in t02["flags"]], [(f["check"], f["key"]) for f in t03["flags"]]),
            "rows": [t02["rows"], t03["rows"]]}
    (HERE / "flags.json").write_text(json.dumps({"packages": results, "summary": summary}, ensure_ascii=False, indent=1) + "\n",
                                     encoding="utf-8", newline="\n")
    for pkg, r in results.items():
        t = r["T"]
        counts = {} if t.get("flags") is None else {c: sum(f["check"] == c for f in t["flags"]) for c in
                                                     ("T1", "T2", "T3", "T4", "T5", "T6")}
        sys.stdout.write(f"{pkg} M1={len(r['M']['flags'])} T={'no-table' if t.get('flags') is None else counts}\n")
    for layer in ("M", "T"):
        for item, row in summary[layer].items():
            sys.stdout.write(f"{layer} {item} caught={row['caught']} pre={len(row['pre_matching'] or [])} "
                             f"post={'n/a' if row['post_matching'] is None else len(row['post_matching'])}\n")
    sys.stdout.write(summary["reading_T"] + "\n")


def selftest():
    """Synthetic inputs (no package): each check fires on a planted case and stays silent on its fixed twin."""
    bad = ["BatchAssignTag", "RequestCollectionDelete", "OpenSettings"]
    good = bad + ["BatchUnassignTag", "CreateManualCollection"]
    assert [f["action"] for f in layer_m(bad)] == ["BatchAssignTag", "RequestCollectionDelete"], layer_m(bad)
    assert layer_m(good) == [], layer_m(good)
    assert verb_object("RequestCollectionDelete") == ("Delete", "Collection")
    states = [{"id": "s1", "selection_possible": True}, {"id": "s2", "selection_possible": True}]
    tag = {"id": "e1", "name": "タグ"}
    coll = {"id": "e2", "name": "手動コレクション"}
    assign = {"id": "op1", "label": "タグを付ける", "entity": "e1", "kind": "assign", "mock_action": "BatchAssignTag",
              "text_refs": ["REQ-1"], "owner_surfaces": ["batch bar"], "counterpart": None,
              "availability": {"s1": "enabled", "s2": "not_drawn"}}
    delete = {"id": "op2", "label": "削除", "entity": "e2", "kind": "delete", "mock_action": "RequestCollectionDelete",
              "text_refs": [], "owner_surfaces": ["sidebar"], "counterpart": None, "availability": {"s1": "enabled", "s2": "enabled"}}
    table_bad = {"states": states, "entities": [tag, coll], "operations": [assign, delete]}
    fb = layer_t(validate(table_bad)[0], bad)
    unassign = dict(assign, id="op3", label="タグを外す", kind="unassign", mock_action="BatchUnassignTag", counterpart="op1",
                    availability={"s1": "enabled", "s2": "enabled"})
    create = dict(delete, id="op4", label="作成", kind="create", mock_action="CreateManualCollection", counterpart="op2")
    table_good = {"states": states, "entities": [tag, coll],
                  "operations": [dict(assign, counterpart="op3", availability={"s1": "enabled", "s2": "enabled"}),
                                 dict(delete, counterpart="op4"), unassign, create]}
    fg = layer_t(validate(table_good)[0], good)
    for item in ("D1", "D2", "D3"):
        assert item_flags(item, "T", fb), (item, fb)
        assert not item_flags(item, "T", fg), (item, fg)
    assert {f["check"] for f in fb} >= {"T1", "T3", "T4", "T5"}, fb
    assert validate({"states": []}) == (None, None)
    t, d = validate({"states": [], "entities": [], "operations": [dict(assign, kind="bogus")]})
    assert t["operations"] == [] and d["operations"] == 1
    sys.stdout.write("selftest PASS\n")


if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]:
        selftest()
    elif sys.argv[1:2] == ["run"] and len(sys.argv) == 3:
        run(Path(sys.argv[2]).resolve())
    else:
        sys.stderr.write(__doc__)
        sys.exit(2)
