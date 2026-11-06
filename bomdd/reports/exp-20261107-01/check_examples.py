"""Check the form of examples.json (EXP-20261107-01 definitions section 5). Values are never checked.

    python check_examples.py examples.json
Prints OK or one ERROR line per problem; exit 1 on any ERROR.
"""
import json
import re
import sys

ALLOWED = re.compile(r"^(Undo|Redo|Split|DeleteSelectedBoundary|SetTrimIn|SetTrimOut|ToStart|ToEnd|StepBack|StepForward"
                     r"|ApplySpeedPreset:(0\.25|0\.5|1|1\.5|2|3|4)|ApplyVolumePreset:(0|50|100|150)"
                     r"|Scale:(1|0\.75|0\.5)|SetFps:(source|24|30|60|120))$")
BOOL_OBS = {"undo_enabled", "redo_enabled", "split_enabled", "merge_enabled", "trim_in_enabled", "trim_out_enabled", "unsaved"}
NUM_OBS = {"region_count", "trim_start", "trim_end", "output_length", "playhead", "selected_start", "selected_end",
           "selected_speed", "selected_volume_percent", "out_fps", "out_width", "out_height"}
OBS = BOOL_OBS | NUM_OBS


def check(doc):
    errs = []
    if not isinstance(doc, dict) or set(doc) != {"examples"} or not isinstance(doc["examples"], list):
        return ['top level must be {"examples": [...]}']
    exs = doc["examples"]
    if not 3 <= len(exs) <= 30:
        errs.append(f"{len(exs)} examples (3-30 allowed)")
    ids = set()
    for n, ex in enumerate(exs):
        where = f"example {n + 1}"
        if not isinstance(ex, dict):
            errs.append(f"{where}: not an object")
            continue
        extra = set(ex) - {"id", "title", "basis", "steps"}
        if extra:
            errs.append(f"{where}: unknown keys {sorted(extra)}")
        for k in ("id", "title", "basis"):
            if not isinstance(ex.get(k), str) or not ex.get(k).strip():
                errs.append(f"{where}: '{k}' must be a non-empty string")
        if isinstance(ex.get("id"), str):
            where = ex["id"]
            if ex["id"] in ids:
                errs.append(f"{where}: duplicate id")
            ids.add(ex["id"])
        steps = ex.get("steps")
        if not isinstance(steps, list) or not 1 <= len(steps) <= 15:
            errs.append(f"{where}: 'steps' must be a list of 1-15 steps")
            continue
        for i, st in enumerate(steps):
            sw = f"{where} step {i + 1}"
            if not isinstance(st, dict):
                errs.append(f"{sw}: not an object")
                continue
            extra = set(st) - {"action", "expect", "unresolved"}
            if extra:
                errs.append(f"{sw}: unknown keys {sorted(extra)}")
            if "action" not in st:
                errs.append(f"{sw}: 'action' is required (null only on the first step)")
            a = st.get("action")
            if a is None:
                if i != 0:
                    errs.append(f"{sw}: action null is allowed only on the first step")
            elif not isinstance(a, str) or not ALLOWED.match(a):
                errs.append(f"{sw}: action {a!r} is not an allowed action")
            exp = st.get("expect", {})
            if not isinstance(exp, dict):
                errs.append(f"{sw}: 'expect' must be an object")
                exp = {}
            for o, v in exp.items():
                if o not in OBS:
                    errs.append(f"{sw}: unknown observation {o!r}")
                elif o in BOOL_OBS and not isinstance(v, bool):
                    errs.append(f"{sw}: {o} must be true or false")
                elif o in NUM_OBS and (isinstance(v, bool) or not isinstance(v, (int, float))):
                    errs.append(f"{sw}: {o} must be a number")
                elif o in NUM_OBS and round(v, 3) != v:
                    errs.append(f"{sw}: {o} has more than 3 decimals")
            unr = st.get("unresolved", [])
            if not isinstance(unr, list) or not all(isinstance(u, str) for u in unr):
                errs.append(f"{sw}: 'unresolved' must be a list of observation names")
                unr = []
            for u in unr:
                if u not in OBS:
                    errs.append(f"{sw}: unknown observation {u!r} in unresolved")
                if u in exp:
                    errs.append(f"{sw}: {u} is both expected and unresolved")
    return errs


def main(path):
    try:
        doc = json.loads(open(path, encoding="utf-8").read())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read {path}: {e}")
        return 1
    errs = check(doc)
    for e in errs:
        print("ERROR:", e)
    if not errs:
        print(f"OK: {len(doc['examples'])} examples")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
