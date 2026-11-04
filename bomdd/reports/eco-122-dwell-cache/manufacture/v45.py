"""ECO-122 V4 (nothing else moves) and V5 (time), by the command line.

  python -X utf8 v45.py <BomDD repo> <old method/ dir> <repos root>

<old method/ dir> holds 9e926be's method/ (git archive, so no worktree is written into BomDD's git directory).
  V4a  bomdd-job.py --all --json, ECO-119 --json and --all in BomDD: byte-identical from the old and the changed tool
  V4b  bomdd-job.py --selftest and bomdd-run.py --selftest exit 0 (changed tree)
  V4c  for each of the five repositories: `git status --porcelain=v1 -uall` and a listing of its git directory (path, size, mtime;
       git's own `index` and `logs/` excluded) are identical before and after a cold run of `--dwell --json` with the default cache
       directory (BOMDD_DWELL_CACHE_DIR unset; that register's cache file deleted first); the cache file is then outside the repository
  V5   ViewTube's register: three cold runs (cache file deleted before each) and three warm runs, wall clock; cold within 60 s, warm 5 s
"""
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

REGS = [("BomDD", "bomdd/60-change-register.yaml"), ("ViewTube", "bomdd/process/change-register.yaml"),
        ("ViewPrism2", "bomdd/60-change-register.yaml"), ("BomDD-Plm", "bomdd/60-change-register.yaml"),
        ("MoviePad-Remake", "bomdd/60-change-register.yaml")]


def main():
    bomdd, old, root = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
    new_tool, old_tool = bomdd / "method/tools/bomdd-job.py", old / "tools/bomdd-job.py"
    env = {k: v for k, v in os.environ.items() if k != "BOMDD_DWELL_CACHE_DIR"}
    sys.path.insert(0, str(bomdd / "method/tools"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("bj", new_tool)
    bj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bj)
    ok = {}

    def run(tool, args, cwd):
        return subprocess.run([sys.executable, "-X", "utf8", str(tool), *args], cwd=cwd, capture_output=True, env=env)

    # V4a
    good = True
    for args in (["--all", "--json"], ["ECO-119", "--json"], ["--all"]):
        a, b = run(old_tool, args, bomdd), run(new_tool, args, bomdd)
        same = a.stdout == b.stdout and a.returncode == b.returncode == 0
        good &= same
        print(f"V4a {' '.join(args)}: old {len(a.stdout)} bytes sha256 {hashlib.sha256(a.stdout).hexdigest()[:16]}, "
              f"new {len(b.stdout)} bytes sha256 {hashlib.sha256(b.stdout).hexdigest()[:16]} -> {'identical' if same else 'DIFFERENT'}")
    ok["V4a"] = good
    # V4b
    r1 = run(new_tool, ["--selftest"], bomdd)
    r2 = run(bomdd / "method/tools/bomdd-run.py", ["--selftest"], bomdd)
    print(f"V4b bomdd-job --selftest exit {r1.returncode}; bomdd-run --selftest exit {r2.returncode}")
    print("    " + "\n    ".join(l[:160] for l in r1.stdout.decode("utf-8", "replace").splitlines()))
    print("    " + "\n    ".join(l[:160] for l in r2.stdout.decode("utf-8", "replace").splitlines()[-3:]))
    ok["V4b"] = r1.returncode == 0 and r2.returncode == 0

    # V4c
    def state(top):
        st = subprocess.run(["git", "-C", str(top), "status", "--porcelain=v1", "-uall"], capture_output=True).stdout
        gd = Path(subprocess.check_output(["git", "-C", str(top), "rev-parse", "--absolute-git-dir"], text=True).strip())
        rows = []
        for d, dirs, files in os.walk(gd):
            rd = Path(d).relative_to(gd).as_posix()
            if rd == "logs" or rd.startswith("logs/"):
                continue
            for f in files:
                rp = f if rd == "." else f"{rd}/{f}"
                if rp == "index":
                    continue
                s = (Path(d) / f).stat()
                rows.append((rp, s.st_size, s.st_mtime_ns))
        return st, sorted(rows)

    good = True
    cdir = bj.dwell_cache_dir_default()
    for repo, rel in REGS:
        top = root / repo
        cfile = bj._dwell_cache_path(cdir, top, rel)
        if cfile.exists():
            cfile.unlink()
        s0, l0 = state(top)
        p = run(new_tool, ["--dwell", "--register", rel, "--json"], top)
        s1, l1 = state(top)
        err = p.stderr.decode("utf-8", "replace").strip().splitlines()
        inside = str(cfile.resolve()).lower().startswith(str(top.resolve()).lower())
        same = s0 == s1 and l0 == l1 and p.returncode == 0 and cfile.exists() and not inside
        good &= same
        print(f"V4c {repo}: status {'same' if s0 == s1 else 'CHANGED'} ({len(s0.splitlines())} lines), git dir {'same' if l0 == l1 else 'CHANGED'} "
              f"({len(l0)} files); cache {err[-1] if err else '(no line)'}; cache file outside the repository {not inside} -> "
              f"{'PASS' if same else 'FAIL'}")
        if l0 != l1:
            print("    changed: " + ", ".join(sorted({r[0] for r in set(l0) ^ set(l1)})[:10]))
    ok["V4c"] = good

    # V5
    vt, vrel = root / "ViewTube", "bomdd/process/change-register.yaml"
    cfile = bj._dwell_cache_path(cdir, vt, vrel)
    cold, warm = [], []
    for _ in range(3):
        if cfile.exists():
            cfile.unlink()
        t = time.perf_counter()
        p = run(new_tool, ["--dwell", "--register", vrel], vt)
        cold.append((time.perf_counter() - t, p.stderr.decode("utf-8", "replace").strip().splitlines()[-1]))
    for _ in range(3):
        t = time.perf_counter()
        p = run(new_tool, ["--dwell", "--register", vrel], vt)
        warm.append((time.perf_counter() - t, p.stderr.decode("utf-8", "replace").strip().splitlines()[-1]))
    for label, xs in (("cold", cold), ("warm", warm)):
        for s, line in xs:
            print(f"V5 {label}: {s:.2f} s — {line.split(', file')[0]}")
    print(f"V5 cache file {cfile.stat().st_size / 1e6:.1f} MB")
    ok["V5 time"] = max(s for s, _ in cold) <= 60 and max(s for s, _ in warm) <= 5
    print("; ".join(f"{k} {'PASS' if v else 'FAIL'}" for k, v in ok.items()))


if __name__ == "__main__":
    main()
