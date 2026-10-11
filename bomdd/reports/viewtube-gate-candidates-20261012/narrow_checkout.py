"""Candidate (b): the change-impact block's copy of the index, full vs narrowed.

In a throwaway clone (nothing written to ViewTube): stage a protected change, then for each of
several staged states run the hook's non-equipment change-impact step
    python <TMP>/bomdd/tools/validate_change_impact.py --root <clone> --prospective-index --quiet
once from a full `git checkout-index --all` copy and once from a copy of only bomdd/tools/ and
bomdd/process/change-impact-policy.yaml, and compare exit code and output. Also times both copies."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
NARROW = ["bomdd/tools", "bomdd/process/change-impact-policy.yaml"]
REQUIRED = ["bomdd/process/change-impact-policy.yaml", "bomdd/tools/validate_change_impact.py",
            "bomdd/tools/selftest_change_impact.py"]


def git(repo, *args, data=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True, check=True)


def copy(repo, narrow):
    tmp = Path(tempfile.mkdtemp(prefix="impact-"))
    t0 = time.perf_counter()
    if narrow:
        listed = git(repo, "ls-files", "-z", "--", *NARROW).stdout
        subprocess.run(["git", "-C", str(repo), "checkout-index", "-z", "--stdin", f"--prefix={tmp}/"],
                       input=listed, check=True)
    else:
        git(repo, "checkout-index", "--all", f"--prefix={tmp}/")
    return tmp, time.perf_counter() - t0


def run(repo, tmp):
    present = all((tmp / r).is_file() for r in REQUIRED)
    done = subprocess.run([sys.executable, str(tmp / "bomdd/tools/validate_change_impact.py"),
                           "--root", str(repo), "--prospective-index"], cwd=repo, capture_output=True)
    return present, done.returncode, done.stdout, done.stderr


base = Path(tempfile.mkdtemp(prefix="narrow-"))
clone = base / "clone"
try:
    subprocess.run(["git", "clone", "-q", "--shared", "-c", "core.autocrlf=false", str(VT), str(clone)], check=True)
    print("clone at", git(clone, "rev-parse", "HEAD").stdout.decode().strip())
    states = []
    # 1 a record commit: the register and an ECO body
    reg = clone / "bomdd/process/change-register.yaml"
    reg.write_bytes(reg.read_bytes() + b"# narrow\n")
    git(clone, "add", "bomdd/process/change-register.yaml")
    states.append("register staged")
    # 2 + a UI product file
    view = next((clone / "src/ViewTube.App").rglob("*.cs"))
    view.write_bytes(view.read_bytes() + b"\n// narrow\n")
    git(clone, "add", str(view.relative_to(clone)).replace("\\", "/"))
    states.append("register + a src/ViewTube.App file staged")
    # 3 + a change-impact manifest broken on purpose (known-bad)
    manifests = sorted((clone / "bomdd/process/change-impact").glob("*.yaml"))
    bad = manifests[-1]
    bad.write_bytes(bad.read_bytes().replace(b"unresolved_required_consumers: 0", b"unresolved_required_consumers: 7", 1))
    git(clone, "add", str(bad.relative_to(clone)).replace("\\", "/"))
    states.append(f"+ {bad.name} with unresolved_required_consumers 7 (known-bad)")
    results = {}
    for label in states:
        pass
    # run each state cumulatively: re-run after each staging step is not possible retroactively,
    # so run all comparisons on the final state and on the first two by resetting step by step.
    for step, label in reversed(list(enumerate(states))):
        out = {}
        for narrow in (False, True):
            tmp, took = copy(clone, narrow)
            try:
                out[narrow] = run(clone, tmp) + (took,)
            finally:
                t0 = time.perf_counter()
                shutil.rmtree(tmp, ignore_errors=True)
                out[narrow] = out[narrow] + (time.perf_counter() - t0,)
        same = out[False][:4] == out[True][:4]
        print(f"[{'SAME' if same else 'DIFFERENT'}] {label}: rc full={out[False][1]} narrow={out[True][1]} "
              f"| copy full {out[False][4]:.1f}s + rm {out[False][5]:.1f}s, narrow {out[True][4]:.2f}s + rm {out[True][5]:.2f}s "
              f"| last line {(out[False][2].decode('utf-8','replace').strip().splitlines() or [''])[-1][:90]}")
        # undo the last staging step
        if step == 2:
            git(clone, "checkout", "--", str(bad.relative_to(clone)).replace("\\", "/"))
            git(clone, "reset", "-q", "--", str(bad.relative_to(clone)).replace("\\", "/"))
            git(clone, "checkout", "--", str(bad.relative_to(clone)).replace("\\", "/"))
        if step == 1:
            p = str(view.relative_to(clone)).replace("\\", "/")
            git(clone, "reset", "-q", "--", p)
            git(clone, "checkout", "--", p)
    full_size = sum(1 for _ in git(clone, "ls-files").stdout.splitlines())
    narrow_size = sum(1 for _ in git(clone, "ls-files", "--", *NARROW).stdout.splitlines())
    print(f"files copied: full {full_size}, narrow {narrow_size}")
finally:
    shutil.rmtree(base, ignore_errors=True)
