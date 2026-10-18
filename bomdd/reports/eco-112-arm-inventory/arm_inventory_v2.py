"""ECO-112 V3 instrument (v2 of arm_inventory.py). Differs from v1 in: targets (every --cell call), the marker line, and a baseline guard.

v1 header follows. ECO-112 loop 3, steps 1-3: inventory of the bomdd-run selftest's `--cell` call sites, and a per-call mutation test.

Usage: python -B arm_inventory.py <path to bomdd-run.py> <out dir>

Step 1 (static): parse the selftest with ast; every `call(...)` site whose argv can contain "--cell" (a list literal, a loop over
         a tuple of list literals, or a builder expression).
Step 2 (dynamic + cross-check): run the selftest once with `run` wrapped; log every invocation (caller line, arm name, argv
         with paths normalised, rc, first output line). Compare static sites with dynamic calls.
Step 3 (mutation, one call at a time): for each dynamic call that has --cell and no --brief, re-run the whole selftest with only
         that call answering as ECO-112's new rule would ("--cell requires --brief" -> ARG_ERROR, exit 2). The selftest's own
         failure list is captured; failures appended between this call and the next call are this call's own check.
         OWN = its own check noticed; MASKED = its own check passed although the call failed for the new rule's reason.
"""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SRC = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
# v2 (review L3R2-1): a marker no real bomdd-run message contains, so an arm whose own reason is the brief rule is not satisfied by it.
MUT_LINE = "UNMEASURABLE ARG_ERROR(INSTRUMENT_MUTATION): refused by the inventory instrument"


def static_sites():
    tree = ast.parse(SRC.read_text(encoding="utf-8"))
    body = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_selftest_body")
    parents = {}
    for p in ast.walk(body):
        for c in ast.iter_child_nodes(p):
            parents[c] = p

    def has_cell(node):
        return any(isinstance(x, ast.Constant) and x.value == "--cell" for x in ast.walk(node))

    sites = []
    for n in ast.walk(body):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "call" and n.args):
            continue
        a = n.args[0]
        if isinstance(a, ast.List):
            sites.append({"call_line": n.lineno, "kind": "list", "site_lines": [a.lineno], "cell_sites": int(has_cell(a))})
        elif isinstance(a, ast.Name):
            p, loop = parents.get(n), None
            while p is not None:
                if isinstance(p, ast.For) and isinstance(p.target, ast.Name) and p.target.id == a.id:
                    loop = p
                    break
                p = parents.get(p)
            if loop is not None and isinstance(loop.iter, (ast.Tuple, ast.List)):
                elts = [e for e in loop.iter.elts if isinstance(e, ast.List)]
                sites.append({"call_line": n.lineno, "kind": "loop", "site_lines": [e.lineno for e in elts],
                              "cell_sites": sum(has_cell(e) for e in elts), "loop_elements": len(elts)})
            else:
                sites.append({"call_line": n.lineno, "kind": "name", "site_lines": [], "cell_sites": None})
        else:
            sites.append({"call_line": n.lineno, "kind": "builder", "site_lines": [a.lineno], "cell_sites": int(has_cell(a))})
    return sites


def load():
    spec = importlib.util.spec_from_file_location("bomdd_run_under_test", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(argv):
    out, prev = [], None
    for a in argv:
        s = str(a)
        if prev == "--cell":
            s = "<cell>"
        elif prev == "--ledger" or ("\\" in s or (len(s) > 2 and s[1] == ":")):
            s = "<path>" if prev != "--cell" else s
        out.append(s)
        prev = str(a)
    return out


def run_selftest(mutate_index=None):
    mod = load()
    orig = mod.run
    log = []
    state = {"fails": None}

    def wrapped(argv, root, emit=None):
        f_call = sys._getframe(1)
        caller = f_call.f_back
        fr = caller
        while fr is not None and fr.f_code.co_name != "_selftest_body":
            fr = fr.f_back
        if fr is not None and state["fails"] is None:
            state["fails"] = fr.f_locals.get("fails")
        idx = len(log)
        rec = {"idx": idx, "func": caller.f_code.co_name, "caller_line": caller.f_lineno,
               "arm": caller.f_locals.get("name") if caller.f_code.co_name in ("arm", "rep_arm", "r11") else None,
               "argv": norm(argv), "has_cell": "--cell" in argv, "has_brief": "--brief" in argv,
               "fails_at_entry": len(state["fails"]) if state["fails"] is not None else None}
        if mutate_index == idx:
            lines = [MUT_LINE]
            for ln in lines:
                (emit or print)(ln)
            rc, first = 2, MUT_LINE
        else:
            captured = []

            def tee(ln):
                captured.append(ln)
                (emit or print)(ln)
            rc = orig(argv, root, tee)
            first = captured[0] if captured else None
        rec.update(rc=rc, first_line=first)
        log.append(rec)
        return rc

    mod.run = wrapped
    buf = io.StringIO()
    crash = None
    with contextlib.redirect_stdout(buf):
        try:
            rc = mod.selftest()
        except Exception as e:  # a crash is a red selftest, recorded as such
            import traceback
            rc, crash = "crash", f"{e.__class__.__name__}: {e} :: " + traceback.format_exc()[-1500:]
    fails = list(state["fails"] or [])
    return {"rc": rc, "crash": crash, "report_first_line": buf.getvalue().splitlines()[0] if buf.getvalue() else None,
            "fails": fails, "log": log}


def main():
    src_sha = hashlib.sha256(SRC.read_bytes()).hexdigest()
    sites = static_sites()
    base = run_selftest()
    # v2 (user condition 2026-10-18, review L3R3-2): a baseline that is not clean makes the mutation result unmeasurable, never a pass.
    if base["rc"] != 0 or base["crash"] or base["fails"]:
        (OUT / "arm-inventory.json").write_text(json.dumps({"source": str(SRC), "source_sha256": src_sha, "verdict": "UNMEASURABLE_BASELINE",
            "baseline": {"rc": base["rc"], "crash": base["crash"], "fails": base["fails"],
                         "report_first_line": base["report_first_line"]}}, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        print("UNMEASURABLE_BASELINE: the unmutated selftest is not clean; no mutation was run", flush=True)
        sys.exit(2)
    calls = base["log"]
    # step 2: cross-check
    dyn_by_line = {}
    for c in calls:
        if c["has_cell"]:
            dyn_by_line.setdefault(c["caller_line"], []).append(c["idx"])
    static_cell_lines = {s["call_line"]: s for s in sites if s["cell_sites"]}
    cross = {"static_call_lines_with_cell": sorted(static_cell_lines),
             "dynamic_call_lines_with_cell": sorted(dyn_by_line),
             "static_not_executed": sorted(set(static_cell_lines) - set(dyn_by_line)),
             "dynamic_not_in_static": sorted(set(dyn_by_line) - set(static_cell_lines)),
             "per_line": {str(l): {"static_cell_sites": static_cell_lines.get(l, {}).get("cell_sites"),
                                   "kind": static_cell_lines.get(l, {}).get("kind"),
                                   "dynamic_calls": len(dyn_by_line.get(l, []))}
                          for l in sorted(set(static_cell_lines) | set(dyn_by_line))}}
    # step 3: one mutation per affected call
    # v2 (ECO-112 V3): every --cell call is a target, with or without --brief; the call answers as the brief rule would
    # (refused first, no ledger record), so a call still MASKED means its own check cannot tell that refusal from its own.
    targets = [c["idx"] for c in calls if c["has_cell"]]
    results = []
    for k in targets:
        r = run_selftest(mutate_index=k)
        log = r["log"]
        entry = [c["fails_at_entry"] for c in log]
        start = entry[k] if k < len(entry) else None
        end = entry[k + 1] if k + 1 < len(entry) else len(r["fails"])
        own = r["fails"][start:end] if start is not None else []
        results.append({"idx": k, "caller_line": calls[k]["caller_line"], "func": calls[k]["func"], "arm": calls[k]["arm"],
                        "argv": calls[k]["argv"], "baseline_rc": calls[k]["rc"], "baseline_first_line": calls[k]["first_line"],
                        "selftest_rc": r["rc"], "crash": r["crash"], "own_fails": own,
                        "other_fails": len(r["fails"]) - len(own),
                        "verdict": "CRASH" if r["crash"] else ("OWN" if own else "MASKED")})
        print(f"{k}/{targets[-1]} line {calls[k]['caller_line']} -> {results[-1]['verdict']}", flush=True)
    data = {"source": str(SRC), "source_sha256": src_sha, "static_sites": sites, "baseline": {"rc": base["rc"],
            "report_first_line": base["report_first_line"], "calls": calls}, "cross_check": cross, "mutation": results}
    (OUT / "arm-inventory.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    from collections import Counter
    v = "PASS" if (all(r["verdict"] == "OWN" for r in results) and results
                   and not cross["static_not_executed"] and not cross["dynamic_not_in_static"]) else "FAIL"
    print("SUMMARY", json.dumps({"verdict": v, "calls": len(calls), "cell_calls": sum(c["has_cell"] for c in calls), "targets": len(targets),
                                "verdicts": Counter(r["verdict"] for r in results), "cross": {k: cross[k] for k in
                                ("static_not_executed", "dynamic_not_in_static")}}, ensure_ascii=False))
    sys.exit(0 if v == "PASS" else 1)


main()
