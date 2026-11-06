"""EXP-20261107-01 comparison (definitions.md section 7): a writer's examples.json against the harness's observations.

    python compare.py run <examples.json> <observed.json> <out.json>
    python compare.py selftest
Deterministic. Numbers hold within 0.0005, booleans by equality.
"""
import json
import pathlib
import sys

PATH = {"undo_enabled": "CanUndo", "redo_enabled": "CanRedo", "split_enabled": "CanSplit",
        "merge_enabled": "CanDeleteBoundary", "trim_in_enabled": "CanSetTrimIn", "trim_out_enabled": "CanSetTrimOut",
        "region_count": "RegionCount", "trim_start": "TrimStart", "trim_end": "TrimEnd", "output_length": "OutputLength",
        "playhead": "Playhead", "selected_start": "SelectedRegion.Start", "selected_end": "SelectedRegion.End",
        "selected_speed": "SelectedRegion.Speed", "selected_volume_percent": "VolumeText", "out_fps": "OutFps",
        "out_width": "OutW", "out_height": "OutH", "unsaved": "Edited"}
TOL = 0.0005


def is_preset(a):
    return a.startswith("ApplySpeedPreset:") or a.startswith("ApplyVolumePreset:")


def is_out(a):
    return a.startswith("Scale:") or a.startswith("SetFps:")


def is_doc_edit(a):
    return a in ("Split", "DeleteSelectedBoundary", "SetTrimIn", "SetTrimOut") or is_preset(a)


def place(obs, actions):
    """The fact a fail is placed at, from the presses up to and including the step (definitions section 7)."""
    last = actions[-1] if actions else None
    undo_redo = last in ("Undo", "Redo")
    if obs in ("undo_enabled", "redo_enabled"):
        if last is None:
            return "other"
        if obs == "redo_enabled" and is_doc_edit(last) and "Undo" in actions[:-1]:
            return "F2"
        if is_out(last):
            return "F6"
        if is_preset(last):
            return "F8"
        if last in ("SetTrimIn", "SetTrimOut"):
            return "F9"
        return "F1"
    if obs in ("out_fps", "out_width", "out_height"):
        return "F6" if undo_redo else "other"
    if obs == "playhead":
        return "F7" if undo_redo else "other"
    if obs == "unsaved":
        return "F10" if undo_redo else "other"
    if obs.startswith("selected_"):
        return "F5"
    if obs in ("region_count", "trim_start", "trim_end", "output_length"):
        return "F3" if undo_redo else "other"
    return "other"


def holds(expected, actual):
    if actual is None or actual.startswith("error"):
        return False
    if isinstance(expected, bool):
        return actual == ("True" if expected else "False")
    try:
        return abs(float(actual) - float(expected)) <= TOL
    except ValueError:
        return False


def compare(examples, observed):
    runs = {r["id"]: r for r in observed["runs"]}
    out = {"assertions": [], "examples": [], "summary": {}}
    for ex in examples["examples"]:
        run = runs[ex["id"]]
        by_k = {s["k"]: s for s in run["steps"]}
        stopped = run["stopped"]
        kind = None
        if stopped:
            kind = "raised" if "exception" in stopped or "setup" in stopped else (
                "not-executed" if "not executed" in stopped else "pressed-unavailable")
        out["examples"].append({"id": ex["id"], "stopped": stopped, "kind": kind})
        k, actions = 0, []
        for i, st in enumerate(ex["steps"]):
            if st.get("action"):
                k += 1
                actions.append(st["action"])
            for obs, val in (st.get("expect") or {}).items():
                a = {"example": ex["id"], "step": i + 1, "k": k, "obs": obs, "expected": val}
                if k not in by_k:
                    a.update(outcome="not run", actual=None)
                else:
                    actual = by_k[k]["values"][PATH[obs]]
                    ok = holds(val, actual)
                    a.update(outcome="hold" if ok else "fail", actual=actual)
                    if not ok:
                        a["fact"] = place(obs, actions)
                out["assertions"].append(a)
    A = out["assertions"]
    s = out["summary"]
    s["examples"] = len(examples["examples"])
    s["asserted"] = len(A)
    for o in ("hold", "fail", "not run"):
        s[o] = sum(a["outcome"] == o for a in A)
    run_n = s["hold"] + s["fail"]
    s["fail_share"] = round(s["fail"] / run_n, 4) if run_n else None
    s["unresolved"] = sum(len(st.get("unresolved") or []) for ex in examples["examples"] for st in ex["steps"])
    for kind in ("pressed-unavailable", "raised", "not-executed"):
        s[kind] = sum(e["kind"] == kind for e in out["examples"])
    facts = {}
    for a in A:
        if a["outcome"] == "fail":
            facts[a["fact"]] = facts.get(a["fact"], 0) + 1
    s["fails_by_fact"] = dict(sorted(facts.items()))
    return out


def main_run(ex_p, obs_p, out_p):
    ex = json.loads(pathlib.Path(ex_p).read_text(encoding="utf-8"))
    obs = json.loads(pathlib.Path(obs_p).read_text(encoding="utf-8"))
    res = compare(ex, obs)
    pathlib.Path(out_p).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(res["summary"], ensure_ascii=False))


def selftest():
    def vals(**kw):
        base = {p: "0" for p in PATH.values()}
        base.update({"CanUndo": "False", "CanRedo": "False", "Edited": "False", "VolumeText": "100"})
        base.update({PATH[k]: v for k, v in kw.items()})
        return base
    observed = {"runs": [
        {"id": "E1", "stopped": None, "steps": [{"k": 0, "values": vals(region_count="4")},
                                                {"k": 1, "values": vals(region_count="5", undo_enabled="True")}]},
        {"id": "E2", "stopped": "step 2: Redo disabled", "steps": [{"k": 0, "values": vals()},
                                                                   {"k": 1, "values": vals(undo_enabled="True")}]},
        {"id": "E3", "stopped": "step 1: exception: boom", "steps": [{"k": 0, "values": vals()}]},
        {"id": "E4", "stopped": None, "steps": [{"k": 0, "values": vals()}, {"k": 1, "values": vals(out_fps="60")},
                                                {"k": 2, "values": vals(out_fps="60", playhead="20.0002")}]},
    ]}
    examples = {"examples": [
        {"id": "E1", "steps": [{"action": None, "expect": {"region_count": 4}},                      # hold
                               {"action": "Split", "expect": {"region_count": 5, "undo_enabled": True,  # hold, hold
                                                              "redo_enabled": True},                 # fail -> F1
                                "unresolved": ["playhead"]}]},
        {"id": "E2", "steps": [{"action": "ApplySpeedPreset:1", "expect": {"undo_enabled": False}},  # fail -> F8
                               {"action": "Redo", "expect": {"redo_enabled": False}}]},              # not run
        {"id": "E3", "steps": [{"action": "Split", "expect": {"region_count": 5}}]},                 # not run (raised)
        {"id": "E4", "steps": [{"action": "SetFps:60", "expect": {"out_fps": 60}},                   # hold
                               {"action": "Undo", "expect": {"out_fps": 30, "playhead": 20}}]},      # fail F6, hold (tol)
    ]}
    r = compare(examples, observed)
    got = [(a["example"], a["obs"], a["outcome"], a.get("fact")) for a in r["assertions"]]
    want = [("E1", "region_count", "hold", None), ("E1", "region_count", "hold", None), ("E1", "undo_enabled", "hold", None),
            ("E1", "redo_enabled", "fail", "F1"), ("E2", "undo_enabled", "fail", "F8"), ("E2", "redo_enabled", "not run", None),
            ("E3", "region_count", "not run", None), ("E4", "out_fps", "hold", None), ("E4", "out_fps", "fail", "F6"),
            ("E4", "playhead", "hold", None)]
    cases = [("outcomes and placements", got == want)]
    kinds = {e["id"]: e["kind"] for e in r["examples"]}
    cases.append(("pressed-unavailable / raised / clean", kinds == {"E1": None, "E2": "pressed-unavailable", "E3": "raised",
                                                                    "E4": None}))
    s = r["summary"]
    cases.append(("summary counts", (s["asserted"], s["hold"], s["fail"], s["not run"], s["unresolved"]) == (10, 5, 3, 2, 1)))
    # placement rules, each with a twin that must not be placed there
    P = [("redo F2", place("redo_enabled", ["Split", "Undo", "Split"]), "F2"),
         ("redo twin (no undo before)", place("redo_enabled", ["Split"]), "F1"),
         ("out F6", place("out_width", ["Scale:0.5", "Undo"]), "F6"),
         ("out twin (not after undo)", place("out_width", ["Scale:0.5"]), "other"),
         ("undo F6", place("undo_enabled", ["SetFps:24"]), "F6"),
         ("undo F9", place("undo_enabled", ["SetTrimIn"]), "F9"),
         ("playhead F7", place("playhead", ["Split", "Undo"]), "F7"),
         ("playhead twin", place("playhead", ["StepForward"]), "other"),
         ("unsaved F10", place("unsaved", ["Split", "Undo"]), "F10"),
         ("unsaved twin", place("unsaved", ["Split"]), "other"),
         ("selected F5", place("selected_start", ["Split"]), "F5"),
         ("doc F3", place("region_count", ["Split", "Undo"]), "F3"),
         ("doc twin", place("region_count", ["Split"]), "other"),
         ("start other", place("undo_enabled", []), "other")]
    cases += [(n, g == w) for n, g, w in P]
    for n, ok in cases:
        print("PASS" if ok else "FAIL", n)
    bad = sum(not ok for _, ok in cases)
    print("selftest", "PASS" if not bad else f"FAIL ({bad})", len(cases), "cases")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main_run(*sys.argv[2:5]) or 0)
