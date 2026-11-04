"""ECO-123 V3 — the new selftest arms can fail.

  python -X utf8 mutants123.py <tool .py> <ECO-122 mutants.py> <work dir>

Copies of the changed tool, each run with --selftest from <work dir> (outside the repository: the existing job arms also fail there for
want of the activation map, as in ECO-120 and ECO-122, so only the named lines are read):
  unchanged  control: the dwell selftest PASS; no "ECO-123" line among the job selftest's failures
  M1-M4      ECO-122's broken copies (substitutions imported from its mutants.py): M1 and M3 must turn the dwell selftest FAILED naming
             the key-follows-source arm and the amend arm; M2 and M4 must not be PASS
  OLD-RE     CLOSE_HEAD_RE without Closure: the job selftest's failures must name an "ECO-123" English-heading arm
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

tool, m122, work = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
work.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location("m122", m122)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
src = tool.read_text(encoding="utf-8")
OLD_A = "(?:クローズ|Closure)[^\\n]*verified"
OLD_B = "クローズ[^\\n]*verified"
copies = [("unchanged", None, None), *[(n, a, b) for n, _, a, b in mod.MUTANTS], ("OLD-RE", OLD_A, OLD_B)]


def section(lines, head):
    i = next((k for k, l in enumerate(lines) if l.startswith(head)), None)
    if i is None:
        return None, []
    rest = []
    for l in lines[i + 1:]:
        if l.startswith("bomdd-job "):
            break
        rest.append(l.strip())
    return lines[i], rest


ok = True
for name, a, b in copies:
    if a is not None and src.count(a) != 1:
        print(f"{name}: NOT BUILT ({src.count(a)} matches)")
        ok = False
        continue
    m = work / f"c_{name}.py"
    m.write_text(src if a is None else src.replace(a, b), encoding="utf-8", newline="\n")
    p = subprocess.run([sys.executable, "-X", "utf8", str(m), "--selftest"], cwd=work, capture_output=True, text=True, encoding="utf-8")
    lines = p.stdout.splitlines()
    jh, jf = section(lines, "bomdd-job selftest")
    dh, df = section(lines, "bomdd-job dwell selftest")
    j123 = [l for l in jf if "ECO-123" in l]
    dstate = "PASS" if dh and " PASS" in dh else ("FAILED" if dh and "FAILED" in dh else (dh or "missing")[:50])
    named = [l for l in df if "key-follows-source" in l or "amend" in l]
    if name == "unchanged":
        good = dstate == "PASS" and not j123
    elif name == "M1":
        good = dstate == "FAILED" and any("key-follows-source" in l for l in df)
    elif name == "M3":
        good = dstate == "FAILED" and any("cache amend" in l for l in df)
    elif name in ("M2", "M4"):
        good = dstate != "PASS"
    else:
        good = bool(j123)
    ok &= good
    print(f"{name}: dwell selftest {dstate}; named new cache arms {named[:3]}; job ECO-123 failures {j123[:2]} -> "
          f"{'as expected' if good else 'NOT AS EXPECTED'}")
print(f"V3 {'PASS' if ok else 'FAIL'}")
