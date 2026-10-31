"""EXP-20261031-02 departure 2 - the blind tools give the same form verdicts as the full ones.

  python equiv_blind.py <domain-model.json> <10-requirements.yaml>

Loads the full pair (this folder) and the blind pair (blind/) in turn, runs every form check on the given model and on broken
copies of it and of a small screens / scenarios fixture, and compares the ERROR lists exactly; the counts must be equal apart
from the full tool's frame-rate key. Exit 0 only if every case is equal and every broken case is caught (an arm that raises no
ERROR proves nothing).
"""
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def load_pair(folder):
    for n in ("check_model", "check_upstream"):
        sys.modules.pop(n, None)
    mods = {}
    for n in ("check_model", "check_upstream"):
        spec = importlib.util.spec_from_file_location(n, folder / f"{n}.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules[n] = m
        spec.loader.exec_module(m)
        mods[n] = m
    return mods["check_model"], mods["check_upstream"]


def cp(x):
    return json.loads(json.dumps(x))


def cases(model, req_path):
    a0 = model["entities"][0]["attributes"][0]
    e1 = model["entities"][1]["name"]
    ms = [("model as written", model)]
    for name, edit in [
            ("no entities", lambda m: m.update(entities=[])),
            ("entity without name", lambda m: m["entities"][0].pop("name")),
            ("entity name repeated", lambda m: m["entities"][1].update(name=m["entities"][0]["name"])),
            ("entity without source", lambda m: m["entities"][0].pop("source")),
            ("attribute without initial", lambda m: m["entities"][0]["attributes"][0].pop("initial")),
            ("attribute without set_by", lambda m: m["entities"][0]["attributes"][0].pop("set_by")),
            ("set_by not a list", lambda m: m["entities"][0]["attributes"][0].update(set_by="X")),
            ("unknown REQ in attribute", lambda m: m["entities"][0]["attributes"][0].update(source=["REQ-999"])),
            ("unknown REQ as a string", lambda m: m["entities"][0].update(source="see REQ-998")),
            ("dangling relation", lambda m: m["entities"][0]["relations"].append({"to": "Nope", "kind": "k", "source": []})),
            ("question without text", lambda m: m.setdefault("questions", []).append({"subject": "s", "source": []})),
            ("nameless operation", lambda m: m.setdefault("operations", []).append({"description": "d"}))]:
        m = cp(model); edit(m); ms.append((f"model: {name}", m))
    key = f"{model['entities'][0]['name']}.{a0['name']}"
    op = (a0.get("set_by") or ["Op"])[0]
    screens = {"screens": [{"id": "SCR-1", "name": "n", "authority_view": "V", "elements": [
        {"id": "EL-1", "kind": "input", "shows": [key], "invokes": op, "param": None, "enabled_when": "-"}]}]}
    scen = {"states": [{"id": "ST-1", "screen": "SCR-1", "shows": {key: 1}}],
            "scenarios": [{"id": "UC-1", "title": "t", "requirement": ["REQ-001"], "flow": "main", "steps": [
                {"in": "ST-1", "element": "EL-1", "operation": op, "param": 1, "expect": "unknown"}]}]}
    ss = [("screens as built", screens)]
    for name, edit in [("unknown attribute", lambda s: s["screens"][0]["elements"][0].update(shows=[f"{e1}.nope"])),
                       ("unknown operation", lambda s: s["screens"][0]["elements"][0].update(invokes="Nope")),
                       ("bad kind", lambda s: s["screens"][0]["elements"][0].update(kind="button")),
                       ("missing view", lambda s: s["screens"][0].pop("authority_view")),
                       ("shows not a list", lambda s: s["screens"][0]["elements"][0].update(shows="x"))]:
        s = cp(screens); edit(s); ss.append((f"screens: {name}", s))
    cs = [("scenarios as built", scen)]
    for name, edit in [("state screen", lambda c: c["states"][0].update(screen="SCR-9")),
                       ("state attribute", lambda c: c["states"][0]["shows"].update({"X.y": 1})),
                       ("requirement", lambda c: c["scenarios"][0].update(requirement=["REQ-999"])),
                       ("step expect", lambda c: c["scenarios"][0]["steps"][0].update(expect="ST-9")),
                       ("step element", lambda c: c["scenarios"][0]["steps"][0].update(element="EL-9")),
                       ("flow", lambda c: c["scenarios"][0].update(flow="other")),
                       ("missing param", lambda c: c["scenarios"][0]["steps"][0].pop("param"))]:
        c = cp(scen); edit(c); cs.append((f"scenarios: {name}", c))
    return ms, (screens, ss), (scen, cs)


def run(folder, model, req_path):
    cm, cu = load_pair(folder)
    reqs = cu.req_ids(req_path)
    ms, (screens, ss), (scen, cs) = cases(model, req_path)
    out = {}
    for name, m in ms:
        out[name] = cu.model_errors(m, reqs)
    for name, s in ss:
        out[name] = cu.screens_errors(s, model)
    for name, c in cs:
        out[name] = cu.scenarios_errors(c, screens, model, reqs)
    counts = {k: v for k, v in cm.counts(model).items() if k != "output_frame_rate"}
    return out, counts


def main():
    model = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    full, fc = run(HERE, model, sys.argv[2])
    blind, bc = run(HERE / "blind", model, sys.argv[2])
    ok = fc == bc
    print("PASS" if ok else "FAIL", "counts equal apart from the frame-rate key")
    for name in full:
        same = full[name] == blind[name]
        caught = ("as written" in name or "as built" in name) or bool(full[name])
        ok &= same and caught
        print("PASS" if same and caught else "FAIL", name, len(full[name]), "errors", "" if caught else "(arm not caught)")
    print(len(full), "cases;", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
