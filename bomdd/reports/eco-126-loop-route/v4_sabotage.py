#!/usr/bin/env python3
"""v4_sabotage.py — BomDD ECO-126: does v4_route.py go red when a tool it calls returns a wrong exit code?

For each case, v4_route.py is run on variant A only, with one installed tool of the scaffold replaced by a stub that
always exits with a constant code (V4_SABOTAGE). The case passes when v4_route.py exits 1 and the checks named below
are among its FAIL lines. A case in which v4_route.py stays green is a hole: a line of V4 whose verdict does not
depend on that tool's exit code.

Nothing in the BomDD repo is changed except this script's output file. The V4 result itself (v4-output.txt) is not
touched: each run writes to a temp file (V4_OUT).

Run:  PYTHONIOENCODING=utf-8 python bomdd/reports/eco-126-loop-route/v4_sabotage.py
Exit: 0 = every case went red on the expected checks / 1 = a case stayed green or missed a check / 2 = could not run.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
V4 = HERE / "v4_route.py"
OUT = HERE / "v4-sabotage-output.txt"
# (the stub, the checks that must be among the FAIL lines)
CASES = (
    ("loop-count.py=1", "the count always fails", {"K7", "A.d.rec1.count", "A.f"}),
    ("loop-count.py=0", "the count never fails", {"A.d.rec1.ctl"}),
    ("ui-cad-gate.py=1", "the gate always fails", {"K8", "A.b.gate", "A.e.gate"}),
    ("ui-cad-gate.py=0", "the gate never fails", {"A.b.gate.ctl"}),
)
lines, bad = [], []


def emit(s):
    lines.append(s)
    print(s, flush=True)


with tempfile.TemporaryDirectory(prefix="bomdd-v4-sab-") as t:
    base = subprocess.run([sys.executable, str(V4)], capture_output=True, text=True, encoding="utf-8", errors="replace",
                          env=dict(os.environ, V4_ONLY="A", V4_OUT=str(Path(t) / "base.txt"), PYTHONIOENCODING="utf-8"))
    base_fails = sorted(set(re.findall(r"^FAIL (\S+)", base.stdout, re.M)))
    ok = base.returncode == 0 and not base_fails
    emit(("PASS " if ok else "FAIL ") + f"baseline: variant A with no stub — v4_route exit {base.returncode}, FAIL lines {base_fails}")
    if not ok:
        bad.append("baseline")
    for stub, label, want in CASES:
        r = subprocess.run([sys.executable, str(V4)], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=dict(os.environ, V4_ONLY="A", V4_SABOTAGE=stub, V4_OUT=str(Path(t) / "run.txt"),
                                    PYTHONIOENCODING="utf-8"))
        fails = set(re.findall(r"^FAIL (\S+)", r.stdout, re.M))
        ok = r.returncode == 1 and want <= fails
        emit(("PASS " if ok else "FAIL ") + f"{stub} ({label}): v4_route exit {r.returncode}; FAIL lines {sorted(fails)}; "
             f"expected among them {sorted(want)}" + ("" if ok else f"; missing {sorted(want - fails)}"))
        if not ok:
            bad.append(stub)
emit("V4 sabotage: " + ("FAILED " + str(bad) if bad else "every stub turned v4_route red on the checks that read that tool"))
OUT.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
sys.exit(1 if bad else 0)
