"""Time each check of BomDD's self-conformance.py in the order main() runs them, and the subprocesses each starts.
Read-only apart from what self-conformance itself writes (its witness file is written only by main(), not here)."""
import importlib.util
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\akira\source\repos\BomDD")
spec = importlib.util.spec_from_file_location("selfconf", ROOT / "method/tools/self-conformance.py")
sc = importlib.util.module_from_spec(spec)
sys.argv = ["self-conformance.py"]
spec.loader.exec_module(sc)

calls = []
real_run = subprocess.run


def timed(*args, **kwargs):
    started = time.perf_counter()
    try:
        return real_run(*args, **kwargs)
    finally:
        command = args[0] if args else kwargs.get("args")
        calls.append((time.perf_counter() - started, " ".join(Path(str(c)).name if i < 2 else str(c) for i, c in enumerate(command[:4]))))


subprocess.run = timed
sc.subprocess.run = timed
rows = []
total_start = time.perf_counter()
for name in ["c1_yaml", "c2_json", "c3_register", "c4_scaffold", "c5_fail_closed", "c6_gate_mutation", "c7_readme",
             "c8_hygiene", "c10_schema_drift", "c11_process_core", "c12_entry_refs", "c13_link_integrity",
             "c14_kit_freshness", "c15_deprecated_refs", "c16_converge_receipt", "c17_calibrate_receipt",
             "c18_prepush_witness"]:
    calls.clear()
    started = time.perf_counter()
    getattr(sc, name)()
    elapsed = time.perf_counter() - started
    slowest = sorted(calls, reverse=True)[:3]
    rows.append((elapsed, name, len(calls), sum(dt for dt, _ in calls), slowest))
total = time.perf_counter() - total_start
print(f"total {total:.1f} s, failures {len(sc.FAILURES)}")
for elapsed, name, count, sub, slowest in rows:
    print(f"{elapsed:7.1f} s  {name:22} {count:4} subprocesses {sub:6.1f} s; slowest: " +
          "; ".join(f"{dt:.1f}s {cmd[:70]}" for dt, cmd in slowest))
