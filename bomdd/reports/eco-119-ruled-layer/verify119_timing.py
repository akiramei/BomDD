"""ECO-119 round 5 - E13's cost at 150 profile versions (R8-4-07), this tree's validator against round 4's (9f586b8).

A product is scaffolded by bomdd-init.py from this working tree. The field is added with since = the HEAD it is added on, then 150
profile commits follow (a comment line changed each time, hooks skipped for the set-up), with a ruled change every tenth. On that
history the same four operations are timed with each validator installed in turn (the validator file is swapped, nothing else):
a hooked commit touching no ruled path, a hooked commit with a ruled change under an open ECO, a hooked merge of a branch with a
ruled change, and `--mode validate`. Each operation is undone after timing (reset), so both validators see the same history.
Writes out/timing.txt; the product is removed.

usage: python verify119_timing.py
"""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
BOMDD = HERE.parents[2]
OUT = HERE / "out"
VERSIONS = 150
ENV = dict(os.environ, GIT_AUTHOR_NAME="eco119-t", GIT_AUTHOR_EMAIL="t@bomdd.invalid",
           GIT_COMMITTER_NAME="eco119-t", GIT_COMMITTER_EMAIL="t@bomdd.invalid")
SPEC, REG, PROF = "bomdd/20-spec.md", "bomdd/60-change-register.yaml", "bomdd/process-profile.yaml"


def _rm_readonly(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def main():
    OUT.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="eco119-timing-"))
    lines = [f"# E13 timing at {VERSIONS} profile versions (R8-4-07)"]
    try:
        p = subprocess.run([sys.executable, str(BOMDD / "method/tools/bomdd-init.py"), "T", "--dir", str(tmp), "--no-gui",
                            "--no-qualify"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
        assert p.returncode == 0, p.stderr
        prod = tmp / "T"
        g = lambda *a: subprocess.run(["git", "-C", str(prod), *a], capture_output=True, text=True, encoding="utf-8",
                                      errors="replace", env=ENV)
        w = lambda rel, text: (prod / rel).parent.mkdir(parents=True, exist_ok=True) or (prod / rel).write_text(
            text, encoding="utf-8", newline="\n")
        vp = prod / "bomdd/tools/process-validator.py"
        ours = vp.read_text(encoding="utf-8")
        r4 = subprocess.run(["git", "-C", str(BOMDD), "show", "9f586b8:method/templates/process-core/tools/process-validator.py"],
                            capture_output=True, text=True, encoding="utf-8", check=True).stdout
        # set-up (hooks skipped): spec, an open ECO whose order cites the spec, the field since the HEAD
        w(SPEC, "# spec\nline 2\n")
        w(REG, "changes:\n  - id: ECO-1\n    title: timing\n    status: staged\n")
        w("bomdd/60-change-order-eco-1.md", f"# ECO-1\n## Sources read\n- {SPEC}:1-2\n")
        g("add", "-A")
        g("commit", "-q", "--no-verify", "-m", "set-up: spec and ECO-1")
        since = g("rev-parse", "HEAD").stdout.strip()
        base_prof = (prod / PROF).read_text(encoding="utf-8")
        prof_with = base_prof + f"\nruled_layer:\n  since: {since}\n  paths: [{SPEC}, bomdd/adr]\n"
        w(PROF, prof_with)
        g("add", "-A")
        g("commit", "-q", "--no-verify", "-m", "equipment: the field")
        for i in range(VERSIONS):
            w(PROF, prof_with + f"# version {i}\n")
            if i % 10 == 0:
                w(SPEC, f"# spec\nline 2 v{i}\n")
            g("add", "-A")
            g("commit", "-q", "--no-verify", "-m", f"equipment: profile version {i}", "-m", "BomDD-ECO-Ruling: ECO-1")
        g("checkout", "-q", "-b", "side")
        w(SPEC, "# spec\nline 2 on side\n")
        g("add", "-A")
        g("commit", "-q", "--no-verify", "-m", "side: ruled change", "-m", "BomDD-ECO-Ruling: ECO-1")
        g("checkout", "-q", "-")
        n = len(g("rev-list", "HEAD", "--", PROF).stdout.split())
        lines.append(f"profile versions on HEAD's line: {n}; commits: {len(g('rev-list', 'HEAD').stdout.split())}")

        def timed(label, *args):
            t0 = time.perf_counter()
            r = g(*args)
            dt = time.perf_counter() - t0
            return dt, r.returncode

        for name, src in (("round 4 (9f586b8)", r4), ("round 5 (this tree)", ours)):
            vp.write_text(src, encoding="utf-8", newline="\n")
            g("update-index", "--assume-unchanged", "bomdd/tools/process-validator.py")
            res = []
            w("bomdd/notes.md", f"notes {name}\n")
            g("add", "bomdd/notes.md")
            res.append(("non-ruled commit",) + timed("", "commit", "-q", "-m", "notes"))
            g("reset", "-q", "--hard", "HEAD~1")
            w(SPEC, f"# spec\nline 2 {name}\n")
            g("add", SPEC)
            res.append(("ruled commit",) + timed("", "commit", "-q", "-m", "spec", "-m", "BomDD-ECO-Ruling: ECO-1"))
            g("reset", "-q", "--hard", "HEAD~1")
            # liveness of the measured path: the same change without the trailer must be refused by E13
            w(SPEC, f"# spec\nline 2 {name} no trailer\n")
            g("add", SPEC)
            t0 = time.perf_counter()
            r = g("commit", "-q", "-m", "spec without a trailer")
            res.append(("ruled commit without trailer", time.perf_counter() - t0,
                        f"{r.returncode}, E13 {'shown' if '[E13]' in r.stdout + r.stderr else 'NOT shown'}"))
            if r.returncode == 0:
                g("reset", "-q", "--hard", "HEAD~1")
            g("reset", "-q", "--hard")
            res.append(("merge",) + timed("", "merge", "-q", "--no-ff", "side", "-m", "merge side", "-m",
                                          "BomDD-ECO-Ruling: ECO-1"))
            g("reset", "-q", "--hard", "HEAD~1")
            t0 = time.perf_counter()
            v = subprocess.run([sys.executable, str(vp), "--mode", "validate", "--root", str(prod)], capture_output=True,
                               text=True, encoding="utf-8", errors="replace", env=ENV)
            res.append(("validate", time.perf_counter() - t0, v.returncode))
            g("update-index", "--no-assume-unchanged", "bomdd/tools/process-validator.py")
            lines.append(f"{name}: " + "; ".join(f"{k} {dt:.1f} s (exit {rc})" for k, dt, rc in res))
        vp.write_text(ours, encoding="utf-8", newline="\n")
    finally:
        shutil.rmtree(tmp, onerror=_rm_readonly)
        lines.append(f"throwaway product removed: {not tmp.exists()}")
    (OUT / "timing.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
