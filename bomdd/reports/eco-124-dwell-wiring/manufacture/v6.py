"""ECO-124 V6: nothing else moves; the hook's time on ViewTube.

  python -X utf8 v6.py <repos root> <old tool path>

(1) The filing tree's tool (97cb6c1, passed as a path) and the changed tool, in-process at one fixed now on the five registers:
    render_dwell text and the dwell() JSON byte-identical (the --dwell full view and --json).
(2) Command line, run from BomDD with each tool: --all --json, --all, ECO-119 --json, ECO-124 --json byte-identical.
(3) bomdd-job --selftest, bomdd-run --selftest and dwell-session-hook --selftest exit codes.
(4) The hook on ViewTube with a warm cache: three runs, wall clock.
The old tool is passed inside a detached worktree of 97cb6c1: the tool reads the activation map next to itself, and a copy placed
elsewhere reads none (the first run, with a copy in the scratchpad, differed in (2) for that reason only — required_skills unknown).
(The dwell read starts worker processes on large histories; under Windows' spawn they import this file, hence the main guard.)
"""
import datetime as dt
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

NOW = dt.datetime(2026, 11, 4, 12, 0, tzinfo=dt.timezone.utc)
REGS = [("BomDD", "bomdd/60-change-register.yaml"), ("ViewTube", "bomdd/process/change-register.yaml"),
        ("ViewPrism2", "bomdd/60-change-register.yaml"), ("BomDD-Plm", "bomdd/60-change-register.yaml"),
        ("MoviePad-Remake", "bomdd/60-change-register.yaml")]


def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m   # the worker processes pickle functions by module name
    spec.loader.exec_module(m)
    return m


def main():
    root = Path(sys.argv[1]).resolve()
    old_path = Path(sys.argv[2]).resolve()
    B = root / "BomDD"
    new_path = B / "method/tools/bomdd-job.py"
    old, new = load("bj_old", old_path), load("bj_new", new_path)
    fails = 0
    print("(1) --dwell full view and JSON, old (filing tree) vs new, now fixed, no cache")
    for repo, rel in REGS:
        ro = old.dwell(root / repo / rel, 14, NOW, workers=1, cache_dir=None)
        rn = new.dwell(root / repo / rel, 14, NOW, workers=1, cache_dir=None)
        same_t = old.render_dwell(ro) == new.render_dwell(rn)
        same_j = json.dumps(ro, ensure_ascii=False, indent=2) == json.dumps(rn, ensure_ascii=False, indent=2)
        fails += not (same_t and same_j)
        print(f"  {'PASS' if same_t and same_j else 'FAIL'} {repo}: text {'identical' if same_t else 'DIFFERS'}, "
              f"json {'identical' if same_j else 'DIFFERS'}")

    print("(2) command line from BomDD")
    for args in (["--all", "--json"], ["--all"], ["ECO-119", "--json"], ["ECO-124", "--json"]):
        outs = [subprocess.run([sys.executable, "-X", "utf8", str(p), *args], cwd=B, capture_output=True).stdout
                for p in (old_path, new_path)]
        fails += outs[0] != outs[1]
        print(f"  {'PASS' if outs[0] == outs[1] else 'FAIL'} {' '.join(args)}: {len(outs[0])} bytes, "
              f"{'identical' if outs[0] == outs[1] else 'DIFFERS'}")

    print("(3) selftests")
    for label, cmd in (("bomdd-job --selftest", [str(new_path), "--selftest"]),
                       ("bomdd-run --selftest", [str(B / "method/tools/bomdd-run.py"), "--selftest"]),
                       ("dwell-session-hook --selftest", [str(B / "method/tools/dwell-session-hook.py"), "--selftest"])):
        rc = subprocess.run([sys.executable, "-X", "utf8", *cmd], cwd=B, capture_output=True).returncode
        fails += rc != 0
        print(f"  {'PASS' if rc == 0 else 'FAIL'} {label}: exit {rc}")

    print("(4) the hook on ViewTube, warm cache, wall clock")
    hook = B / "method/tools/dwell-session-hook.py"
    inp = json.dumps({"cwd": str(root / "ViewTube"), "hook_event_name": "SessionStart", "source": "startup"}).encode()
    subprocess.run([sys.executable, "-X", "utf8", str(hook)], input=inp, capture_output=True)   # fill
    ts = []
    for _ in range(3):
        t = time.perf_counter()
        r = subprocess.run([sys.executable, "-X", "utf8", str(hook)], input=inp, capture_output=True)
        ts.append(time.perf_counter() - t)
        fails += not (r.returncode == 0 and r.stdout.decode("utf-8").startswith("dwell: ViewTube "))
    ok = max(ts) < 3
    fails += not ok
    print(f"  {'PASS' if ok else 'FAIL'} runs {', '.join(f'{x:.2f}' for x in ts)} s (bound for the gate: 3 s)")
    print(f"V6 (measured part) {'PASS' if not fails else 'FAIL'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
