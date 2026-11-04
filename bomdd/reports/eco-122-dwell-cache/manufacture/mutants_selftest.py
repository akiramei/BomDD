"""ECO-122 closure check: do the selftest's own cache arms (the nested `--selftest`, not v23.py) catch M1-M4?

  python -X utf8 mutants_selftest.py <tool .py> <work dir>

Builds the same four broken copies as mutants.py, runs each copy's `--selftest` from <work dir> and reads only the dwell selftest's
line (copies outside the repository also fail the existing arms for want of the activation map, as in ECO-120). Records, per mutant,
whether the dwell selftest went red and which cache arms it named. Not a closing condition of the order; a check of the instrument.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mutants", here / "mutants.py")
mut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mut)

tool, work = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
work.mkdir(parents=True, exist_ok=True)
src = tool.read_text(encoding="utf-8")
for label, a, b in [("unchanged", None, None)] + [(n, a, b) for n, _, a, b in mut.MUTANTS]:
    text = src if a is None else src.replace(a, b)
    if a is not None and src.count(a) != 1:
        print(f"{label}: NOT BUILT")
        continue
    m = work / f"st_{label}.py"
    m.write_text(text, encoding="utf-8", newline="\n")
    p = subprocess.run([sys.executable, "-X", "utf8", str(m), "--selftest"], cwd=work, capture_output=True, text=True, encoding="utf-8")
    lines = p.stdout.splitlines()
    i = next((k for k, l in enumerate(lines) if l.startswith("bomdd-job dwell selftest")), None)
    if i is None:
        print(f"{label}: dwell selftest line not found")
        continue
    head = lines[i]
    cache = [l.strip() for l in lines[i + 1:] if l.strip().startswith("cache ")]
    state = "PASS" if " PASS" in head else ("FAILED" if "FAILED" in head else head[:60])
    print(f"{label}: dwell selftest {state}; cache arms named: {cache if cache else 'none'}")
