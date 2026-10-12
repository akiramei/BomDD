#!/usr/bin/env python3
"""ECO-105 same-verdict check on the failing side, with the subprocess calls of C11 and C11b replaced by a fake.

Run as: python equiv105.py <original self-conformance.py> <repaired self-conformance.py>
For each scenario, both versions run c11_process_core() with the same fake; the printed lines, the FAILURES list and any
exception must be identical. The fake answers each command at once, so a scenario takes milliseconds."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOOD = {"runs_identical": True, "disposition": "PASS", "iq": [{"control": "IQ-03", "pass": True}],
        "oq": [{"control": "OQ-01", "pass": True}]}
IQ_ONLY_FAIL = {"iq": [{"control": "IQ-03", "pass": False}]}


def make_fake(scenario: str):
    def fake(args, **kwargs):
        text = " ".join(str(item) for item in args)
        rc, out, err = 0, "", ""
        if "bomdd-init.py" in text:
            name = args[args.index(next(a for a in args if str(a).endswith("bomdd-init.py"))) + 1]
            target = Path(args[args.index("--dir") + 1]) / name
            (target / "bomdd" / "tools").mkdir(parents=True, exist_ok=True)
            profile = {"register": "bomdd/change-register.yaml", "states": ["staged", "applied"], "initial": "staged",
                       "trailers": {"fix": "F", "accept": "A"}, "protected_paths": ["src/"]}
            (target / "bomdd" / "process-profile.yaml").write_text(json.dumps(profile), encoding="utf-8")
            (target / "AGENTS.md").write_text("bomdd/change-register.yaml\n", encoding="utf-8")
            if name == "AdaptSmoke" and scenario == "c11b-init-fails":
                rc, err = 1, "adapt init failed"
            if name == "ProcCoreSmoke" and scenario == "c11-init-fails":
                rc, err = 1, "core init failed"
        elif "process-qualification.py" in text:
            json_path = Path(args[args.index("--json") + 1])
            adapted = "AdaptSmoke" in text
            if "--mode" in args:
                json_path.write_text(json.dumps(IQ_ONLY_FAIL), encoding="utf-8")
                rc = 1
            elif adapted and scenario == "c11b-qualification-fails":
                json_path.write_text(json.dumps({**GOOD, "oq": [{"control": "OQ-07", "pass": False}]}), encoding="utf-8")
                rc = 1
            elif not adapted and scenario == "both-fail":
                json_path.write_text(json.dumps({**GOOD, "runs_identical": False}), encoding="utf-8")
                rc = 1
            elif adapted and scenario == "both-fail":
                json_path.write_text(json.dumps({**GOOD, "oq": [{"control": "OQ-09", "pass": False}]}), encoding="utf-8")
                rc = 1
            elif adapted and scenario == "c11b-raises":
                raise RuntimeError("adapted runner exploded")
            else:
                json_path.write_text(json.dumps(GOOD), encoding="utf-8")
        return subprocess.CompletedProcess(args, rc, out, err)
    return fake


def run_version(path: Path, scenario: str):
    spec = importlib.util.spec_from_file_location(f"sc_{abs(hash((str(path), scenario)))}", path)
    module = importlib.util.module_from_spec(spec)
    saved = sys.argv
    sys.argv = ["self-conformance.py"]
    try:
        spec.loader.exec_module(module)
    finally:
        sys.argv = saved
    module.run = make_fake(scenario)
    buffer = io.StringIO()
    error = None
    with contextlib.redirect_stdout(buffer):
        try:
            module.c11_process_core()
        except Exception as exc:  # noqa: BLE001 - the exception itself is what is compared
            error = f"{type(exc).__name__}: {exc}"
    lines = [line for line in buffer.getvalue().splitlines()]
    return lines, list(module.FAILURES), error


original, repaired = Path(sys.argv[1]), Path(sys.argv[2])
scenarios = ["all-pass", "c11-init-fails", "c11b-init-fails", "c11b-qualification-fails", "both-fail", "c11b-raises"]
same_all = True
for scenario in scenarios:
    a, b = run_version(original, scenario), run_version(repaired, scenario)
    same = a == b
    same_all &= same
    print(f"{scenario:26} {'SAME' if same else 'DIFFERENT'}  lines={len(a[0])} failures={len(a[1])} "
          f"exception={a[2]!r}")
    if not same:
        print("   original:", a)
        print("   repaired:", b)
print(f"RESULT {'SAME' if same_all else 'DIFFERENT'} ({len(scenarios)} scenarios)")
raise SystemExit(0 if same_all else 1)
