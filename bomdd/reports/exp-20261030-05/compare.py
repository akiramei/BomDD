"""Stage 2's freeze, placement and tally (definitions.md sections 4-6). The walk itself is stage 1's walk.py, unchanged.

    python compare.py selftest
    python compare.py freeze <written.json> <package-dir> <frozen.json> <freeze.json>
    python compare.py clean <mock.html> <frozen.json>                                   # stop flags on the clean mock
    python compare.py run <mock.html> <frozen.json> <mutants-dir> <mutants.json> <stage1-flags.json> <flags.json>
Categories, in order: caught (a key on the mutant not on the clean mock), outside (no counted step uses the change),
agreeing (a clean key at a step using the change is gone), masked (every counted step using it already has a clean key),
other. A key is (check, at). A counted step's (in, action) is present and enabled on the clean mock.
"""
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "exp-20261030-04"))
sys.path.insert(0, str(HERE))
import walk as W  # noqa: E402  stage 1's walk, unchanged
import check_schema  # noqa: E402

ORDER = ("caught", "outside", "agreeing", "masked", "other")


def walk(states, scen):
    """Stage 1's walk with its own section 7 applied: W3 is not checked when the step's expect is "unknown" (walk.py skips
    only an unknown goto; stage 1 had no unknown expect, so its results are unaffected - departure D2)."""
    expect = {f"{sid}#{i}": st["expect"] for sid, i, st in W.steps_of(scen)}
    return [f for f in W.walk(states, scen) if not (f["check"] == "W3" and expect.get(f["at"]) == "unknown")]


def keys(flags):
    return {(f["check"], f["at"]) for f in flags if f["check"] in W.STOP}


def counted_steps(clean, scen):
    out = []
    for sid, i, st in W.steps_of(scen):
        el = clean.get(st["in"], {}).get(st["action"])
        if el is not None and el["enabled"]:
            out.append((f"{sid}#{i}", st))
    return out


def coverage(clean, scen, n_actions):
    enabled = {(s, a) for s, acts in clean.items() for a, el in acts.items() if el["enabled"]}
    used = {(st["in"], st["action"]) for _, st in counted_steps(clean, scen)}
    return {"pairs_used": len(used), "pairs_enabled": len(enabled),
            "actions_used": len({a for _, a in used}), "actions_known": n_actions}


def place(clean, mut, scen):
    """(category, detail) for one a-e mutant."""
    c_keys, m_keys = keys(walk(clean, scen)), keys(walk(mut, scen))
    if m_keys - c_keys:
        return "caught", sorted(m_keys - c_keys)
    changed = {(s, a) for s, a, _ in W.diff(clean, mut)}
    using = [(at, st) for at, st in counted_steps(clean, scen) if (st["in"], st["action"]) in changed]
    if not using:
        return "outside", []
    at_using = {at for at, _ in using}
    gone = sorted(k for k in c_keys - m_keys if k[1] in at_using)
    if gone:
        return "agreeing", gone
    if all(any(k[1] == at for k in c_keys) for at in at_using):
        return "masked", sorted(k for k in c_keys if k[1] in at_using)
    return "other", sorted(at_using)


def freeze(written, pkg, frozen, record):
    pkg = pathlib.Path(pkg)
    states = json.loads((pkg / "states.json").read_text(encoding="utf-8"))
    actions = json.loads((pkg / "actions.json").read_text(encoding="utf-8"))
    scen = json.loads(pathlib.Path(written).read_text(encoding="utf-8"))
    errs = check_schema.errors_of(scen, states, actions)
    if "" in errs:
        sys.exit(f"top level: {errs['']}")
    kept, dropped = [], {}
    for n, s in enumerate(scen["scenarios"]):
        key = s.get("id") if isinstance(s, dict) and s.get("id") else f"#{n}"
        if key in errs:
            dropped[key] = errs[key]
            continue
        for st in s["steps"]:
            if st["action"] in check_schema.ENDING:
                st["harness"] = "no"
        kept.append(s)
    text = json.dumps({"scenarios": kept}, ensure_ascii=False, indent=1)
    pathlib.Path(frozen).write_text(text, encoding="utf-8", newline="\n")
    steps = [st for s in kept for st in s["steps"]]
    rec = {"sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "written": len(scen["scenarios"]),
           "dropped": dropped, "kept": len(kept), "steps": len(steps),
           "expect_unknown": sum(st["expect"] == "unknown" for st in steps),
           "harness_no": sum(st.get("harness") == "no" for st in steps),
           "flows": {f: sum(s["flow"] == f for s in kept) for f in ("main", "alternate")}}
    pathlib.Path(record).write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(rec, ensure_ascii=False))


def run(mock_path, frozen, mut_dir, mut_json, stage1_flags, out_path):
    clean, _ = W.parse(pathlib.Path(mock_path).read_text(encoding="utf-8"))
    scen = json.loads(pathlib.Path(frozen).read_text(encoding="utf-8"))
    base = walk(clean, scen)
    s1 = {r["id"]: r["inside"] for r in json.loads(pathlib.Path(stage1_flags).read_text(encoding="utf-8"))["mutants"]}
    bindings = json.loads((HERE.parent / "exp-20261030-04" / "bindings.json").read_text(encoding="utf-8"))
    n_actions = len({e["Id"] for e in bindings["Elements"]})  # 44, as stage 1 (CancelExport is in no mock state)
    rows, tally, f_alarms = [], {}, []
    for m in json.loads(pathlib.Path(mut_json).read_text(encoding="utf-8")):
        mut, _ = W.parse((pathlib.Path(mut_dir) / m["file"]).read_text(encoding="utf-8"))
        row = {"id": m["id"], "class": m["class"], "stage1_inside": s1[m["id"]]}
        if m["class"] == "f":
            new = sorted(keys(walk(mut, scen)) - keys(base))
            row["false_alarm"] = new
            f_alarms += [m["id"]] * bool(new)
        else:
            cat, detail = place(clean, mut, scen)
            row.update(category=cat, detail=detail)
            t = tally.setdefault(m["class"], dict.fromkeys(ORDER, 0))
            t[cat] += 1
        rows.append(row)
    total = {c: sum(t[c] for t in tally.values()) for c in ORDER}
    by_check = {c: sum(f["check"] == c for f in base) for c in ("W1", "W2", "W3")}
    out = {"clean_stop_flags": [f for f in base if f["check"] in W.STOP], "clean_by_check": by_check,
           "w4_clean": sum(f["check"] == "W4" for f in base), "coverage": coverage(clean, scen, n_actions),
           "steps_walked": sum(1 for _ in W.steps_of(scen)), "steps_counted": len(counted_steps(clean, scen)),
           "mutants": rows, "tally": tally, "total": total, "f_false_alarms": f_alarms}
    pathlib.Path(out_path).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print("clean stop flags", by_check, "coverage", out["coverage"], "counted", out["steps_counted"], "/", out["steps_walked"])
    for c in sorted(tally):
        print(c, tally[c])
    print("total", total, "f false alarms", f_alarms)


def selftest():
    def el(action, surface, enabled, goto):
        return (f'<button data-ui-action="{action}" data-ui-surface="{surface}" '
                f'data-ui-enabled="{"true" if enabled else "false"}" data-ui-goto="{goto}">x</button>')

    def mock(rows):
        out = []
        for state, els in rows.items():
            out.append(f'<section data-ui-state="{state}">' + "".join(el(*e) for e in els) + "</section>")
        return "\n".join(out)

    base = {"s1": [("Go", "P", True, "s2"), ("Off", "P", False, "-"), ("Spare", "P", True, "s1")],
            "s2": [("Back", "P", True, "s1"), ("Next", "P", True, "s3")],
            "s3": [("Back", "P", True, "s2")]}
    scen = {"scenarios": [{"id": "U1", "steps": [
        {"in": "s1", "action": "Go", "surface": "P", "expect": "s2"},     # right
        {"in": "s2", "action": "Back", "surface": "P", "expect": "s3"},   # wrong expect: clean W3 at U1#1
        {"in": "s1", "action": "Off", "surface": "P", "expect": "s1"},    # disabled on clean: W1, not counted
        {"in": "s2", "action": "Next", "surface": "P", "expect": "s3"}]}]}  # right

    def variant(state, action, **change):
        rows = {s: [tuple(e) for e in els] for s, els in base.items()}
        rows[state] = [(a, change.get("surface", s), change.get("enabled", en), change.get("goto", g))
                       if a == action else (a, s, en, g) for a, s, en, g in rows[state]]
        return W.parse(mock(rows))[0]

    clean = W.parse(mock(base))[0]
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want
        fails += 0 if ok else 1
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else f": got {got!r}, want {want!r}"))

    check("clean keys are the planted two", sorted(keys(walk(clean, scen))), [("W1", "U1#2"), ("W3", "U1#1")])
    check("counted steps leave out the disabled pair", [a for a, _ in counted_steps(clean, scen)], ["U1#0", "U1#1", "U1#3"])
    check("caught: a right step's pair disabled", place(clean, variant("s1", "Go", enabled=False), scen)[0], "caught")
    check("caught twin: the same change at a pair no step uses is outside",
          place(clean, variant("s1", "Spare", enabled=False), scen)[0], "outside")
    check("outside: a pair used only by an uncounted step", place(clean, variant("s1", "Off", goto="s2"), scen)[0],
          "outside")
    check("agreeing: the goto changed to the step's wrong expect", place(clean, variant("s2", "Back", goto="s3"), scen),
          ("agreeing", [("W3", "U1#1")]))
    check("masked: the goto changed to a third state at a step already flagged",
          place(clean, variant("s2", "Back", goto="s2"), scen), ("masked", [("W3", "U1#1")]))
    check("masked twin: the same change at a right step is caught", place(clean, variant("s2", "Next", goto="s2"), scen)[0],
          "caught")
    check("other: a change the walk cannot read at a right step (goto set still holds the expect)",
          place(clean, variant("s2", "Next", goto="s3 s1"), scen)[0], "other")
    f_ok = keys(walk(variant("s1", "Spare", surface="Q"), scen)) - keys(walk(clean, scen))
    check("f twin: a change at an unused element raises no new key", sorted(f_ok), [])
    f_bad = keys(walk(variant("s1", "Go", surface="Q"), scen)) - keys(walk(clean, scen))
    check("f false alarm: a change the walk reads at a used element raises a new key", sorted(f_bad), [("W2", "U1#0")])
    unk = {"scenarios": [{"id": "U2", "steps": [{"in": "s1", "action": "Go", "surface": "P", "expect": "unknown"}]}]}
    check("W3 not read on an unknown expect (stage 1 section 7)", sorted(keys(walk(clean, unk))), [])
    check("unknown-expect twin: stage 1's walk.py alone flags it", sorted(keys(W.walk(clean, unk))), [("W3", "U2#0")])
    print("selftest", "PASS" if not fails else f"FAIL ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "freeze":
        freeze(*sys.argv[2:6])
    elif cmd == "clean":
        cl, _ = W.parse(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
        for f in walk(cl, json.loads(pathlib.Path(sys.argv[3]).read_text(encoding="utf-8"))):
            if f["check"] in W.STOP:
                print(f["check"], f["at"], f["why"])
    else:
        run(*sys.argv[2:8])
