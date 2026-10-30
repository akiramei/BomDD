"""The walk (definitions.md section 7): W1 walk, W2 surface, W3 transition (stop), W4 reverse coverage (measure).

    python walk.py selftest
    python walk.py clean <mock.html> <scenarios-frozen.json>                       # flags on one mock
    python walk.py run <mock.html> <scenarios-frozen.json> <mutants-dir> <mutants.json> <flags.json>
Deterministic; reads the mock's data-ui-* attributes only (labels and element order are never read).
"""
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

STOP = ("W1", "W2", "W3")


class _P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.states, self.cur, self.order = {}, None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and "data-ui-state" in a:
            self.cur = a["data-ui-state"]
            self.states.setdefault(self.cur, {})
            self.order.append(("state", self.cur))
        elif self.cur is not None and "data-ui-action" in a:
            self.states[self.cur][a["data-ui-action"]] = {
                "surface": a.get("data-ui-surface", ""), "enabled": a.get("data-ui-enabled") == "true",
                "goto": a.get("data-ui-goto", "unknown")}
            self.order.append((self.cur, a["data-ui-action"]))

    def handle_endtag(self, tag):
        if tag == "section":
            self.cur = None


def parse(text):
    p = _P()
    p.feed(text)
    return p.states, p.order


def labels(text):
    """(state, action) -> label text. Used only to check that a mutant is one change; the walk never reads labels."""
    out = {}
    for state, body in re.findall(r'<section data-ui-state="([^"]*)">(.*?)</section>', text, re.S):
        for aid, lab in re.findall(r'data-ui-action="([^"]*)"[^>]*>([^<]*)</button>', body):
            out[(state, aid)] = lab
    return out


def steps_of(scen):
    for s in scen["scenarios"]:
        for i, st in enumerate(s["steps"]):
            yield s["id"], i, st
            if st.get("harness") == "no":
                break


def walk(states, scen):
    flags = []
    for sid, i, st in steps_of(scen):
        where = f"{sid}#{i}"
        sec = states.get(st["in"])
        el = None if sec is None else sec.get(st["action"])
        if sec is None:
            flags.append({"check": "W1", "at": where, "why": f"no state {st['in']}"})
            continue
        if el is None:
            flags.append({"check": "W1", "at": where, "why": f"no {st['action']} in {st['in']}"})
            continue
        if not el["enabled"]:
            flags.append({"check": "W1", "at": where, "why": f"{st['action']} disabled in {st['in']}"})
            continue
        if el["surface"] != st["surface"]:
            flags.append({"check": "W2", "at": where, "why": f"{st['action']} on {el['surface']}, step says {st['surface']}"})
        g = el["goto"]
        if g not in ("unknown", "-") and st.get("harness") != "no" and st["expect"] not in g.split():
            flags.append({"check": "W3", "at": where, "why": f"{st['action']} goes to [{g}], step expects {st['expect']}"})
    used = {(st["in"], st["action"]) for _, _, st in steps_of(scen)}
    for state, acts in states.items():
        for aid, el in acts.items():
            if el["enabled"] and (state, aid) not in used:
                flags.append({"check": "W4", "at": f"{state}/{aid}", "why": "enabled, used by no step"})
    return flags


def used_pairs(scen):
    return {(st["in"], st["action"]) for _, _, st in steps_of(scen)}


def coverage(states, scen, known_actions=None):
    enabled = {(s, a) for s, acts in states.items() for a, el in acts.items() if el["enabled"]}
    used = used_pairs(scen) & enabled
    ids_used = {a for _, a in used_pairs(scen)}
    out = {"pairs_used": len(used), "pairs_enabled": len(enabled)}
    if known_actions is not None:
        out.update(actions_used=len(ids_used & set(known_actions)), actions_known=len(known_actions))
    return out


def diff(clean, mut):
    """(state, action, attr) tuples that differ, and the action ids they touch."""
    d = set()
    for s in set(clean) | set(mut):
        a, b = clean.get(s), mut.get(s)
        if a is None or b is None:
            for aid in (a or b or {}):
                d.add((s, aid, "state"))
            continue
        for aid in set(a) | set(b):
            x, y = a.get(aid), b.get(aid)
            if x is None or y is None:
                d.add((s, aid, "presence"))
            else:
                for k in ("surface", "enabled", "goto"):
                    if x[k] != y[k]:
                        d.add((s, aid, k))
    return d


def run(mock_path, scen_path, mut_dir, mut_json, out_path):
    clean_text = pathlib.Path(mock_path).read_text(encoding="utf-8")
    clean, clean_order = parse(clean_text)
    scen = json.load(open(scen_path, encoding="utf-8"))
    base = walk(clean, scen)
    if any(f["check"] in STOP for f in base):
        sys.exit(f"clean mock has stop flags: {[f for f in base if f['check'] in STOP]}")
    base_w4 = {f["at"] for f in base if f["check"] == "W4"}
    used = used_pairs(scen)
    rows = []
    for m in json.load(open(mut_json, encoding="utf-8")):
        text = (pathlib.Path(mut_dir) / m["file"]).read_text(encoding="utf-8")
        st, order = parse(text)
        d = diff(clean, st)
        ids = {aid for _, aid, _ in d}
        lab_a, lab_b = labels(clean_text), labels(text)
        label_ids = {k[1] for k in set(lab_a) & set(lab_b) if lab_a[k] != lab_b[k]}
        if m["class"] == "f":
            # one equivalent change: one action's label, or a reorder, or one added element
            one_change = len(ids | label_ids) == 1 or (not ids and not label_ids and order != clean_order)
        else:
            one_change = len(ids) == 1
        inside = any((s, aid) in used for s, aid, _ in d)
        fl = walk(st, scen)
        stop = [f for f in fl if f["check"] in STOP]
        new_w4 = [f for f in fl if f["check"] == "W4" and f["at"] not in base_w4]
        rows.append({"id": m["id"], "class": m["class"], "one_change": one_change, "touched": sorted(ids),
                     "diff": sorted("/".join(t) for t in d), "inside": inside, "caught": bool(stop),
                     "stop_flags": stop, "new_w4": new_w4})
    tally = {}
    for r in rows:
        t = tally.setdefault(r["class"], {"n": 0, "inside": 0, "inside_caught": 0, "outside": 0, "outside_caught": 0,
                                          "not_one_change": 0})
        t["n"] += 1
        t["not_one_change"] += 0 if r["one_change"] else 1
        k = "inside" if r["inside"] else "outside"
        t[k] += 1
        t[k + "_caught"] += 1 if r["caught"] else 0
    out = {"clean_flags": base, "coverage": coverage(clean, scen), "mutants": rows, "tally": tally}
    pathlib.Path(out_path).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in sorted(tally):
        print(c, tally[c])
    print("coverage", out["coverage"])


def selftest():
    mock = """<section data-ui-state="s1">
      <button data-ui-action="Go" data-ui-surface="P" data-ui-enabled="true" data-ui-goto="s2">Go</button>
      <button data-ui-action="Back" data-ui-surface="P" data-ui-enabled="false" data-ui-goto="-">Back</button>
      <button data-ui-action="Spare" data-ui-surface="P" data-ui-enabled="true" data-ui-goto="s1">Spare</button>
    </section><section data-ui-state="s2">
      <button data-ui-action="Back" data-ui-surface="P" data-ui-enabled="true" data-ui-goto="s1">Back</button>
      <button data-ui-action="Load" data-ui-surface="Q" data-ui-enabled="true" data-ui-goto="unknown">Load</button>
    </section>"""
    scen = {"scenarios": [{"id": "x", "steps": [
        {"in": "s1", "action": "Go", "surface": "P", "expect": "s2"},
        {"in": "s2", "action": "Back", "surface": "P", "expect": "s1"},
        {"in": "s1", "action": "Go", "surface": "P", "expect": "s2"},
        {"in": "s2", "action": "Load", "surface": "Q", "expect": "s2", "harness": "no"},
        {"in": "s2", "action": "Ghost", "surface": "Q", "expect": "s2"}]}]}
    clean, order = parse(mock)
    fails = 0

    def check(name, fires, silent):
        nonlocal fails
        ok = fires and silent
        fails += 0 if ok else 1
        print(f"  {'PASS' if ok else 'FAIL'} {name} (fires={fires}, silent twin={silent})")

    base = walk(clean, scen)
    stop0 = [f for f in base if f["check"] in STOP]
    check("steps after harness:no are not walked", True, stop0 == [])

    def flags_for(m):
        return {f["check"] for f in walk(parse(m)[0], scen) if f["check"] in STOP}
    check("W1 missing action", "W1" in flags_for(mock.replace('data-ui-action="Back" data-ui-surface="P" data-ui-enabled="true"',
                                                              'data-ui-action="Back2" data-ui-surface="P" data-ui-enabled="true"')), stop0 == [])
    check("W1 disabled action", "W1" in flags_for(mock.replace('data-ui-enabled="true" data-ui-goto="s2"',
                                                               'data-ui-enabled="false" data-ui-goto="s2"')), stop0 == [])
    check("W1 missing state", "W1" in flags_for(mock.replace('data-ui-state="s2"', 'data-ui-state="s9"')), stop0 == [])
    check("W2 surface", flags_for(mock.replace('data-ui-action="Go" data-ui-surface="P"', 'data-ui-action="Go" data-ui-surface="R"')) == {"W2"},
          stop0 == [])
    check("W3 transition", flags_for(mock.replace('data-ui-goto="s2"', 'data-ui-goto="s1"')) == {"W3"}, stop0 == [])
    check("W3 skipped on unknown and on harness:no",
          flags_for(mock.replace('data-ui-action="Load" data-ui-surface="Q" data-ui-enabled="true" data-ui-goto="unknown"',
                                 'data-ui-action="Load" data-ui-surface="Q" data-ui-enabled="true" data-ui-goto="s1"')) == set(), True)
    relabel = mock.replace(">Go<", ">Proceed<")
    reorder = mock.replace(
        '<button data-ui-action="Go" data-ui-surface="P" data-ui-enabled="true" data-ui-goto="s2">Go</button>\n'
        '      <button data-ui-action="Back" data-ui-surface="P" data-ui-enabled="false" data-ui-goto="-">Back</button>',
        '<button data-ui-action="Back" data-ui-surface="P" data-ui-enabled="false" data-ui-goto="-">Back</button>\n'
        '      <button data-ui-action="Go" data-ui-surface="P" data-ui-enabled="true" data-ui-goto="s2">Go</button>')
    check("labels and order are not read", flags_for(relabel) == set() and flags_for(reorder) == set(), reorder != mock)
    w4 = {f["at"] for f in base if f["check"] == "W4"}
    check("W4 reverse coverage", "s1/Spare" in w4, "s1/Go" not in w4)
    cv = coverage(clean, scen)
    check("coverage counts enabled pairs", cv == {"pairs_used": 3, "pairs_enabled": 4}, True)
    d = diff(clean, parse(mock.replace('data-ui-goto="s2"', 'data-ui-goto="s1"'))[0])
    check("diff names the touched action", {a for _, a, _ in d} == {"Go"}, diff(clean, parse(reorder)[0]) == set())
    print("selftest PASS" if fails == 0 else f"selftest FAIL ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "clean":
        st, _ = parse(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
        sc = json.load(open(sys.argv[3], encoding="utf-8"))
        fl = walk(st, sc)
        for f in fl:
            if f["check"] in STOP:
                print(f)
        print({c: sum(1 for f in fl if f["check"] == c) for c in ("W1", "W2", "W3", "W4")}, coverage(st, sc))
        sys.exit(1 if any(f["check"] in STOP for f in fl) else 0)
    if cmd == "run":
        run(*sys.argv[2:7])
        sys.exit(0)
    sys.exit(__doc__)
