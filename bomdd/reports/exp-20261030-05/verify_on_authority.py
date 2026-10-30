"""Read after the verdict (results.md section 4; descriptive): are the writers' clean flags their errors, or the mock's?

Builds one scenario file for stage 1's harness: stage 1's frozen states (with their predicates) and scenarios, plus every
writer scenario that carries a clean stop flag, given the setup stage 1 used for a scenario starting in the same state.
The harness then executes them on the authority's view model and checks each step's `in` and `expect` predicates, and
reports states whose availability or transitions differ between visits (stage 1's D2).

    python verify_on_authority.py <stage1-frozen.json> <a-frozen.json> <a-flags.json> <b-frozen.json> <b-flags.json> <out.json>
"""
import json
import pathlib
import sys


def load(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def main(s1, a_scen, a_flags, b_scen, b_flags, out):
    stage1 = load(s1)
    setup_by_start = {}
    for sc in stage1["scenarios"]:
        setup_by_start.setdefault(sc["steps"][0]["in"], sc["setup"])
    scenarios = [dict(sc, id="S1-" + sc["id"]) for sc in stage1["scenarios"]]
    for w, scen_p, flags_p in (("A", a_scen, a_flags), ("B", b_scen, b_flags)):
        flagged = {f["at"].split("#")[0] for f in load(flags_p)["clean_stop_flags"]}
        for sc in load(scen_p)["scenarios"]:
            if sc["id"] not in flagged:
                continue
            start = sc["steps"][0]["in"]
            if start not in setup_by_start:
                sys.exit(f"{w}-{sc['id']}: no stage 1 setup for {start}")
            scenarios.append({"id": f"{w}-{sc['id']}", "title": sc["title"], "goal": sc["goal"], "flow": sc["flow"],
                              "setup": setup_by_start[start], "steps": sc["steps"]})
    pathlib.Path(out).write_text(json.dumps({"states": stage1["states"], "scenarios": scenarios}, ensure_ascii=False,
                                            indent=1), encoding="utf-8", newline="\n")
    print("scenarios", len(scenarios), "of which writers'", sum(not s["id"].startswith("S1-") for s in scenarios))


if __name__ == "__main__":
    main(*sys.argv[1:7])
