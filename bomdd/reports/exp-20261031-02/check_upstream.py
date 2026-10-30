"""EXP-20261031-02 - the form check of stage A's artefacts and the chain count A1 (definitions sections 6 and 7).

  python check_upstream.py model <domain-model.json> <10-requirements.yaml>
  python check_upstream.py screens <screens.json> <domain-model.json>
  python check_upstream.py scenarios <scenarios.json> <screens.json> <domain-model.json> <10-requirements.yaml>
  python check_upstream.py chain <domain-model.json> <screens.json> <scenarios.json>      (A1; prints JSON)
  python check_upstream.py selftest

The form checks print ERROR lines (the author fixes them) and exit 1 if there are any. The model's form is EXP-20261031-01's
(`check_model.py`, imported from this folder), with the cited ids taken from the requirements only (the spec is written last);
an optional top-level `operations` list names operations that set nothing. Judges nothing about the content.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_model  # noqa: E402  (copied next to this file in every folder that needs it)

REQ = re.compile(r"\bREQ-\d{3}\b")
KINDS = ("display", "input", "command")


def load(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def req_ids(req_path):
    return set(REQ.findall(pathlib.Path(req_path).read_text(encoding="utf-8")))


def attrs_of(model):
    return {f"{e['name']}.{a['name']}": a for e in model.get("entities", []) for a in e.get("attributes", [])}


def ops_of(model):
    ops = {o for a in attrs_of(model).values() for o in (a.get("set_by") or [])}
    ops |= {o.get("name") for o in model.get("operations", []) if isinstance(o, dict)}
    return ops


def model_errors(model, reqs):
    errs = check_model.errors_of(model, reqs)
    for o in model.get("operations", []):
        if not isinstance(o, dict) or not o.get("name"):
            errs.append(f"operations: an entry without a name: {json.dumps(o, ensure_ascii=False)[:80]}")
    return errs


def screens_errors(screens, model):
    errs, ids = [], set()
    attrs, ops = attrs_of(model), ops_of(model)
    if not isinstance(screens.get("screens"), list) or not screens["screens"]:
        return ["screens: a non-empty list is required"]
    for s in screens["screens"]:
        sid = s.get("id")
        for key in ("id", "name", "authority_view", "elements"):
            if key not in s or (key != "elements" and not s.get(key)):
                errs.append(f"{sid}: '{key}' missing or empty")
        if sid in ids:
            errs.append(f"{sid}: id repeated")
        ids.add(sid)
        for el in s.get("elements", []):
            eid = el.get("id")
            for key in ("id", "kind", "shows", "invokes", "param", "enabled_when"):
                if key not in el:
                    errs.append(f"{sid}/{eid}: '{key}' missing")
            if eid in ids:
                errs.append(f"{sid}/{eid}: id repeated")
            ids.add(eid)
            if el.get("kind") not in KINDS:
                errs.append(f"{eid}: kind must be one of {KINDS}")
            if not isinstance(el.get("shows", []), list):
                errs.append(f"{eid}: shows must be a list")
            for k in el.get("shows") or []:
                if k not in attrs:
                    errs.append(f"{eid}: shows {k}, which is not an attribute of the model")
            if el.get("invokes") is not None and el.get("invokes") not in ops:
                errs.append(f"{eid}: invokes {el.get('invokes')}, which is not an operation of the model")
    return errs


def elements_of(screens):
    return {el["id"]: el for s in screens.get("screens", []) for el in s.get("elements", []) if "id" in el}


def scenarios_errors(scen, screens, model, reqs):
    errs = []
    attrs, ops = attrs_of(model), ops_of(model)
    scr_ids = {s.get("id") for s in screens.get("screens", [])}
    els = elements_of(screens)
    if not isinstance(scen.get("states"), list) or not scen["states"]:
        return ["states: a non-empty list is required"]
    if not isinstance(scen.get("scenarios"), list) or not scen["scenarios"]:
        return ["scenarios: a non-empty list is required"]
    st_ids = set()
    for st in scen["states"]:
        sid = st.get("id")
        for key in ("id", "screen", "shows"):
            if key not in st:
                errs.append(f"{sid}: '{key}' missing")
        if sid in st_ids:
            errs.append(f"{sid}: state id repeated")
        st_ids.add(sid)
        if st.get("screen") not in scr_ids:
            errs.append(f"{sid}: screen {st.get('screen')} is not in screens.json")
        if not isinstance(st.get("shows", {}), dict):
            errs.append(f"{sid}: shows must be an object")
            continue
        for k in st.get("shows", {}):
            if k not in attrs:
                errs.append(f"{sid}: shows {k}, which is not an attribute of the model")
    uc_ids = set()
    for uc in scen["scenarios"]:
        uid = uc.get("id")
        for key in ("id", "title", "requirement", "flow", "steps"):
            if key not in uc:
                errs.append(f"{uid}: '{key}' missing")
        if uid in uc_ids:
            errs.append(f"{uid}: scenario id repeated")
        uc_ids.add(uid)
        if uc.get("flow") not in ("main", "alternate"):
            errs.append(f"{uid}: flow must be main or alternate")
        for r in uc.get("requirement") or []:
            if r not in reqs:
                errs.append(f"{uid}: requirement {r} is not in 10-requirements.yaml")
        for i, step in enumerate(uc.get("steps") or []):
            w = f"{uid}#{i}"
            for key in ("in", "element", "operation", "param", "expect"):
                if key not in step:
                    errs.append(f"{w}: '{key}' missing")
            if step.get("in") not in st_ids:
                errs.append(f"{w}: in {step.get('in')} is not a state")
            if step.get("expect") != "unknown" and step.get("expect") not in st_ids:
                errs.append(f"{w}: expect {step.get('expect')} is neither a state nor \"unknown\"")
            if step.get("operation") not in ops:
                errs.append(f"{w}: operation {step.get('operation')} is not an operation of the model")
            el = els.get(step.get("element"))
            if el is None:
                errs.append(f"{w}: element {step.get('element')} is not in screens.json")
            elif el.get("invokes") != step.get("operation"):
                errs.append(f"{w}: element {step.get('element')} invokes {el.get('invokes')}, not {step.get('operation')}")
    return errs


def chain(model, screens, scen):
    attrs = attrs_of(model)
    els = elements_of(screens)
    states = {st["id"]: st for st in scen.get("states", []) if "id" in st}
    steps = [s for uc in scen.get("scenarios", []) for s in uc.get("steps") or []]
    shown = {k for el in els.values() for k in el.get("shows") or []}
    stated = {k for st in states.values() for k in (st.get("shows") or {})}
    rows = []
    for key, a in attrs.items():
        ops = set(a.get("set_by") or [])
        if not ops:
            continue
        setting = [s for s in steps if s.get("operation") in ops]
        checked = [s for s in setting
                   if s.get("expect") in states and key in (states[s["expect"]].get("shows") or {})
                   and str(states[s["expect"]]["shows"][key]).strip().lower() != "unknown"]
        rows.append({"attribute": key, "L1_displayed": key in shown, "L2_stated": key in stated,
                     "L3_set": bool(setting), "L4_checked": bool(checked), "setting_steps": len(setting),
                     "checked_steps": len(checked)})
    links = ("L1_displayed", "L2_stated", "L3_set", "L4_checked")
    fps = check_model.counts(model)["output_frame_rate"]
    return {"n_settable": len(rows), **{l: sum(r[l] for r in rows) for l in links},
            "k_all_four": sum(all(r[l] for l in links) for r in rows),
            "steps": len(steps), "steps_expect_unknown": sum(1 for s in steps if s.get("expect") == "unknown"),
            "frame_rate_rule_selects": fps,
            "frame_rate_rows": [r for r in rows if r["attribute"] in fps],
            "rows": rows}


def selftest():
    reqs = {"REQ-001"}
    model = {"entities": [{"name": "OutputSettings", "description": "output", "source": ["REQ-001"], "relations": [],
                           "attributes": [{"name": "fps", "description": "output frame rate", "type": "double",
                                           "initial": "source fps", "set_by": ["SetFps"], "source": ["REQ-001"]},
                                          {"name": "width", "description": "output width", "type": "int",
                                           "initial": "source width", "set_by": ["SetWidth"], "source": ["REQ-001"]}]}],
             "operations": [{"name": "Open"}], "questions": []}
    screens = {"screens": [{"id": "SCR-1", "name": "Export", "authority_view": "ExportDialogView", "elements": [
        {"id": "EL-1", "kind": "input", "shows": ["OutputSettings.fps"], "invokes": "SetFps", "param": None, "enabled_when": "-"},
        {"id": "EL-2", "kind": "input", "shows": [], "invokes": "SetWidth", "param": None, "enabled_when": "-"}]}]}
    scen = {"states": [{"id": "ST-1", "screen": "SCR-1", "shows": {"OutputSettings.fps": 30}},
                       {"id": "ST-2", "screen": "SCR-1", "shows": {"OutputSettings.fps": 24, "OutputSettings.width": "unknown"}}],
            "scenarios": [{"id": "UC-1", "title": "t", "requirement": ["REQ-001"], "flow": "main", "steps": [
                {"in": "ST-1", "element": "EL-1", "operation": "SetFps", "param": 24, "expect": "ST-2"},
                {"in": "ST-2", "element": "EL-2", "operation": "SetWidth", "param": 640, "expect": "unknown"}]}]}
    cp = lambda x: json.loads(json.dumps(x))
    cases = []
    cases.append(("model good", model_errors(model, reqs), False))
    m = cp(model); m["entities"][0]["source"] = ["REQ-099"]; cases.append(("model unknown req", model_errors(m, reqs), True))
    m = cp(model); m["operations"] = [{}]; cases.append(("model nameless operation", model_errors(m, reqs), True))
    cases.append(("screens good", screens_errors(screens, model), False))
    s = cp(screens); s["screens"][0]["elements"][0]["shows"] = ["OutputSettings.nope"]
    cases.append(("screens unknown attribute", screens_errors(s, model), True))
    s = cp(screens); s["screens"][0]["elements"][0]["invokes"] = "Nope"
    cases.append(("screens unknown operation", screens_errors(s, model), True))
    s = cp(screens); s["screens"][0]["elements"][1]["id"] = "EL-1"
    cases.append(("screens repeated id", screens_errors(s, model), True))
    s = cp(screens); s["screens"][0]["elements"][0]["kind"] = "button"
    cases.append(("screens bad kind", screens_errors(s, model), True))
    s = cp(screens); del s["screens"][0]["authority_view"]
    cases.append(("screens missing key", screens_errors(s, model), True))
    cases.append(("scenarios good", scenarios_errors(scen, screens, model, reqs), False))
    for name, edit in [("state screen", lambda c: c["states"][0].update(screen="SCR-9")),
                       ("state attribute", lambda c: c["states"][0]["shows"].update({"X.y": 1})),
                       ("requirement", lambda c: c["scenarios"][0].update(requirement=["REQ-002"])),
                       ("step in", lambda c: c["scenarios"][0]["steps"][0].update({"in": "ST-9"})),
                       ("step expect", lambda c: c["scenarios"][0]["steps"][0].update(expect="ST-9")),
                       ("step operation", lambda c: c["scenarios"][0]["steps"][0].update(operation="Open")),
                       ("step element", lambda c: c["scenarios"][0]["steps"][0].update(element="EL-9")),
                       ("flow", lambda c: c["scenarios"][0].update(flow="other")),
                       ("missing param", lambda c: c["scenarios"][0]["steps"][0].pop("param"))]:
        c = cp(scen); edit(c); cases.append((f"scenarios bad {name}", scenarios_errors(c, screens, model, reqs), True))
    ok = True
    for name, errs, want in cases:
        good = bool(errs) == want
        ok &= good
        print("PASS" if good else "FAIL", name, len(errs))
    a1 = chain(model, screens, scen)
    rows = {r["attribute"]: r for r in a1["rows"]}
    expect = {"OutputSettings.fps": (True, True, True, True), "OutputSettings.width": (False, True, True, False)}
    for k, want in expect.items():
        got = tuple(rows[k][l] for l in ("L1_displayed", "L2_stated", "L3_set", "L4_checked"))
        ok &= got == want
        print("PASS" if got == want else "FAIL", "chain", k, got)
    good = (a1["n_settable"], a1["k_all_four"], a1["steps_expect_unknown"], a1["frame_rate_rule_selects"]) == \
        (2, 1, 1, ["OutputSettings.fps"])
    ok &= good
    print("PASS" if good else "FAIL", "chain totals", a1["n_settable"], a1["k_all_four"], a1["steps_expect_unknown"],
          a1["frame_rate_rule_selects"])
    # a state that shows the attribute as "unknown" does not check it
    c = cp(scen); c["states"][1]["shows"]["OutputSettings.fps"] = "unknown"
    r = {x["attribute"]: x for x in chain(model, screens, c)["rows"]}["OutputSettings.fps"]
    ok &= r["L4_checked"] is False
    print("PASS" if r["L4_checked"] is False else "FAIL", "chain: unknown value is not checked")
    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def report(errs, extra=None):
    for e in errs:
        print("ERROR", e)
    if not errs:
        print("form OK" + (f" {extra}" if extra else ""))
    return 1 if errs else 0


def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "selftest":
        return selftest()
    if cmd == "model":
        model = load(args[0])
        errs = model_errors(model, req_ids(args[1]))
        return report(errs, json.dumps(check_model.counts(model), ensure_ascii=False) if not errs else None)
    if cmd == "screens":
        return report(screens_errors(load(args[0]), load(args[1])))
    if cmd == "scenarios":
        return report(scenarios_errors(load(args[0]), load(args[1]), load(args[2]), req_ids(args[3])))
    if cmd == "chain":
        print(json.dumps(chain(load(args[0]), load(args[1]), load(args[2])), ensure_ascii=False, indent=1))
        return 0
    sys.exit(f"unknown command {cmd}")


if __name__ == "__main__":
    sys.exit(main())
