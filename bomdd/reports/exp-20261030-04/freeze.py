"""Freeze the certified scenarios (definitions.md section 4, D2).

    python freeze.py <scenarios.json> <certify.json> <scenarios-frozen.json> <freeze.json>
Keeps only the scenarios the harness kept (certified and visiting no ambiguous state), with the states they use;
writes the SHA-256 of the frozen file and the counts. Re-certify the frozen file afterwards: every scenario must be kept.
"""
import hashlib
import json
import pathlib
import sys


def main(src, cert, out, freeze):
    s = json.load(open(src, encoding="utf-8"))
    c = json.load(open(cert, encoding="utf-8"))
    kept = set(c["kept"])
    scen = [x for x in s["scenarios"] if x["id"] in kept]
    used_states = {st[k] for x in scen for st in x["steps"] for k in ("in", "expect")}
    frozen = {"states": [st for st in s["states"] if st["id"] in used_states], "scenarios": scen}
    text = json.dumps(frozen, ensure_ascii=False, indent=1) + "\n"
    pathlib.Path(out).write_text(text, encoding="utf-8", newline="\n")
    failed = {k for k, v in c["certified"].items() if not v}
    reasons = {}
    for r in c["steps"]:
        if not r["Pass"] and r["Scenario"] in failed:
            reasons.setdefault(r["Scenario"], f"#{r['Index']} {r['Action']}: {r['Reason']}")
    info = {
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "written": len(s["scenarios"]),
        "certified": sum(1 for v in c["certified"].values() if v),
        "dropped_failed": reasons,
        "dropped_ambiguous": c["dropped_for_ambiguity"],
        "kept": len(scen),
        "states_declared": len(s["states"]),
        "states_kept": len(frozen["states"]),
        "steps": sum(len(x["steps"]) for x in scen),
        "steps_harness_no": sum(1 for x in scen for st in x["steps"] if st.get("harness") == "no"),
        "setup_ops": {x["id"]: len(x.get("setup", [])) for x in scen},
        "flows": {f: sum(1 for x in scen if x.get("flow") == f) for f in ("main", "alternate")},
    }
    pathlib.Path(freeze).write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in info.items() if k not in ("dropped_failed", "dropped_ambiguous", "setup_ops")}))
    print("dropped (failed):", len(reasons), " dropped (ambiguous):", len(c["dropped_for_ambiguity"]))


if __name__ == "__main__":
    main(*sys.argv[1:5])
