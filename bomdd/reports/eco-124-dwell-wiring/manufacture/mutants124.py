"""ECO-124 V2/V3 known-bad: broken copies turn the selftest arms red; the unchanged copies stay green.

  python -X utf8 mutants124.py <BomDD root>

Brief mutants (bomdd-job.py): the copy is imported from a temporary folder and its _dwell_selftest() is called (the dwell arms need no
other file). Hook mutants (dwell-session-hook.py): the copy is placed in a temporary folder next to the unchanged bomdd-job.py and run
with --selftest. Each substitution must occur exactly once in the source (else the mutant is reported NOT APPLIED, not counted).
"""
import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

B = Path(sys.argv[1]).resolve()
JOB = B / "method/tools/bomdd-job.py"
HOOK = B / "method/tools/dwell-session-hook.py"
BRIEF = [
    ("B0 unchanged", None, None),
    ("B1 window end excluded", 'o["days"] <= t + window]', 'o["days"] < t + window]'),
    ("B2 DECIDE ignores the reason", 'due = [o for o in over if o["group"] == "none" and o["days"]', 'due = [o for o in over if o["days"]'),
    ("B3 no cap", 'for o in due[:cap])', 'for o in due)'),
    ("B4 not measured goes silent", 'print(brief_not_measured(err) if err else render_brief(res), end="")',
     'print("" if err else render_brief(res), end="")'),
]
HOOKM = [
    ("H0 unchanged", None, None),
    ("H1 tool failure swallowed", 'return not_measured(f"tool exit {p.returncode}: {tail[0][:160]}")', 'return ""'),
    ("H2 time bound swallowed", 'return not_measured(f"time bound {bound:g} s reached (run bomdd-job --dwell --brief by hand)")', 'return ""'),
    ("H3 unexpected output passed through", 'return not_measured(f"unexpected tool output: {text[:80]!r}")', 'return text'),
    ("H4 input cwd ignored", 'return cwd if isinstance(cwd, str) and cwd and os.path.isdir(cwd) else os.getcwd()', 'return os.getcwd()'),
]


def mutate(src, a, b):
    if a is None:
        return src
    if src.count(a) != 1:
        return None
    return src.replace(a, b)


def main():
    red = applied = 0
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        sys.path.insert(0, str(t))
        src = JOB.read_text(encoding="utf-8")
        for i, (name, a, b) in enumerate(BRIEF):
            m = mutate(src, a, b)
            if m is None:
                print(f"NOT APPLIED {name}")
                continue
            p = t / f"bjm{i}.py"
            p.write_text(m, encoding="utf-8")
            spec = importlib.util.spec_from_file_location(f"bjm{i}", p)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[f"bjm{i}"] = mod
            spec.loader.exec_module(mod)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mod._dwell_selftest()
            out = buf.getvalue()
            lines = [l.strip() for l in out.splitlines() if "124" in l and not l.startswith("bomdd-job dwell selftest PASS")]
            verdict = "PASS" if rc == 0 else ("FAILED" if rc == 1 else "UNMEASURABLE")
            print(f"{name}: dwell selftest {verdict}" + (f" — {lines[0][:150]}" if lines and rc else ""))
            if a is not None:
                applied += 1
                red += rc == 1
            elif rc != 0:
                print("  the unchanged copy is not green")
                red = -99
        hsrc = HOOK.read_text(encoding="utf-8")
        for i, (name, a, b) in enumerate(HOOKM):
            m = mutate(hsrc, a, b)
            if m is None:
                print(f"NOT APPLIED {name}")
                continue
            d = t / f"h{i}"
            d.mkdir()
            shutil.copy2(JOB, d / "bomdd-job.py")
            (d / "dwell-session-hook.py").write_text(m, encoding="utf-8")
            r = subprocess.run([sys.executable, "-X", "utf8", str(d / "dwell-session-hook.py"), "--selftest"], capture_output=True)
            out = r.stdout.decode("utf-8", "replace")
            verdict = "PASS" if r.returncode == 0 else ("FAILED" if r.returncode == 1 else "UNMEASURABLE")
            first = next((l.strip() for l in out.splitlines()[1:]), "")
            print(f"{name}: hook selftest {verdict}" + (f" — {first[:150]}" if r.returncode else ""))
            if a is not None:
                applied += 1
                red += r.returncode == 1
            elif r.returncode != 0:
                print("  the unchanged copy is not green")
                red = -99
    print(f"mutants red {red} of {applied} applied; unchanged copies green: {'yes' if red >= 0 else 'NO'}")
    return 0 if red == applied else 1


if __name__ == "__main__":
    sys.exit(main())
