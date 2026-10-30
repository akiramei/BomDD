"""Form checker given to the writers (definitions.md section 4): ids and form only, nothing about how the application behaves.

    python check_schema.py [scenarios.json]     # in the folder that holds states.json and actions.json; exit 1 on any error
Errors drop a scenario at the freeze. The counts (10-25 scenarios, 2-10 steps) are a guide and are only reported.
"""
import json
import pathlib
import sys

ENDING = ("Open", "ConfirmExport", "InstallFfmpeg")  # file dialog or external process: they end a scenario


def errors_of(scen, states, actions):
    """{scenario id: [error, ...]} and top-level errors under the key ''."""
    sids = {s["id"] for s in states}
    rows = {(a["id"], a["surface"]) for a in actions}
    ids = {a["id"] for a in actions}
    out = {}
    if not isinstance(scen, dict) or not isinstance(scen.get("scenarios"), list):
        return {"": ['top level must be {"scenarios": [...]}']}
    seen = set()
    for n, s in enumerate(scen["scenarios"]):
        sid = s.get("id") if isinstance(s, dict) else None
        key = sid if isinstance(sid, str) and sid else f"#{n}"
        errs = out.setdefault(key, [])
        if not isinstance(s, dict):
            errs.append("a scenario must be an object")
            continue
        if key in seen:
            errs.append("duplicate scenario id")
        seen.add(key)
        for f in ("title", "goal"):
            if not isinstance(s.get(f), str) or not s[f]:
                errs.append(f"missing {f}")
        if s.get("flow") not in ("main", "alternate"):
            errs.append('flow must be "main" or "alternate"')
        steps = s.get("steps")
        if not isinstance(steps, list) or not steps:
            errs.append("steps must be a non-empty list")
            continue
        for i, st in enumerate(steps):
            if not isinstance(st, dict):
                errs.append(f"step {i}: must be an object")
                continue
            if st.get("in") not in sids:
                errs.append(f"step {i}: in {st.get('in')!r} is not a state id")
            if st.get("action") not in ids:
                errs.append(f"step {i}: action {st.get('action')!r} is not an action id")
            elif (st.get("action"), st.get("surface")) not in rows:
                errs.append(f"step {i}: {st.get('action')} has no element on surface {st.get('surface')!r}")
            if st.get("expect") not in sids and st.get("expect") != "unknown":
                errs.append(f"step {i}: expect {st.get('expect')!r} is neither a state id nor \"unknown\"")
            if st.get("action") in ENDING and i != len(steps) - 1:
                errs.append(f"step {i}: {st['action']} must be the last step")
    return {k: v for k, v in out.items() if v}


def main(path="scenarios.json"):
    here = pathlib.Path(path).resolve().parent
    states = json.loads((here / "states.json").read_text(encoding="utf-8"))
    actions = json.loads((here / "actions.json").read_text(encoding="utf-8"))
    try:
        scen = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print("ERROR", e)
        return 1
    errs = errors_of(scen, states, actions)
    for k, v in errs.items():
        for e in v:
            print("ERROR", k or "(top)", e)
    if isinstance(scen, dict) and isinstance(scen.get("scenarios"), list):
        n = len(scen["scenarios"])
        lens = [len(s.get("steps") or []) for s in scen["scenarios"] if isinstance(s, dict)]
        print(f"scenarios {n} (guide 10-25), steps {sum(lens)}, per scenario {min(lens, default=0)}-{max(lens, default=0)}"
              " (guide 2-10)")
    print("OK" if not errs else f"{sum(len(v) for v in errs.values())} errors")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
