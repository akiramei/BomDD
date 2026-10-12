"""Re-run the gate of ViewTube's repair commit e912e5d8 (111 minutes on 2026-10-12) with timing.

Nothing is written to ViewTube. In a throwaway clone the parent 5fd5394e is checked out and the
e912e5d8 tree is staged over it, which is the state the real `git commit` saw. The pre-commit hook
then runs under `bash -x` with a timestamped, line-numbered PS4, and every Python it starts loads
site/sitecustomize.py, which logs process starts, subprocess.run calls and exits. Then commit-msg
runs with e912e5d8's own message. Raw output goes to out/ next to this script.

The hooks are run directly, as hook_profile.py did: ViewTube sets core.hooksPath=bomdd/hooks, so
git runs these same files with no wrapper in between.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
PARENT = "5fd5394e5192fc772c2ee68603060741875915c3"
REPAIR = "e912e5d8f2888c212f38597168a0169f7a52f0b6"
HARNESS_SHA = "983075a64bc053a26cf043e4ff953093bfca54366afbcaae88e77620a2b7c808"


def git(clone, *args):
    return subprocess.run(["git", "-C", str(clone), *args], check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout


OUT.mkdir(exist_ok=True)
base = Path(tempfile.mkdtemp(prefix="gate-equip-"))
clone = base / "clone"
log = OUT / "timer-log.jsonl"
log.unlink(missing_ok=True)
try:
    subprocess.run(["git", "clone", "-q", "--shared", "-c", "core.autocrlf=false", str(VT), str(clone)],
                   check=True)
    git(clone, "checkout", "-q", "-b", "gate-equip", PARENT)
    git(clone, "checkout", REPAIR, "--", ".")
    staged = git(clone, "diff", "--cached", "--name-status")
    expected = git(clone, "diff", "--name-status", PARENT, REPAIR)
    assert staged == expected, "staged set differs from the repair commit"
    tree = git(clone, "write-tree").strip()
    assert tree == git(clone, "rev-parse", f"{REPAIR}^{{tree}}").strip(), "index tree differs"
    harness = clone / "bomdd/tools/selftest_ui_manufacturing.py"
    assert hashlib.sha256(harness.read_bytes()).hexdigest() == HARNESS_SHA, "harness bytes differ"
    hook = clone / "bomdd/hooks/pre-commit"
    assert hook.read_bytes() == subprocess.run(["git", "-C", str(clone), "show", f"{REPAIR}:bomdd/hooks/pre-commit"],
                                               check=True, capture_output=True).stdout, "hook differs"
    (OUT / "setup.txt").write_text(
        f"clone HEAD {PARENT}\nindex tree {tree} (= {REPAIR}^{{tree}})\n"
        f"selftest_ui_manufacturing.py sha256 {HARNESS_SHA}\nstaged:\n{staged}", encoding="utf-8")
    print(f"clone ready at {base}; staged:\n{staged}", flush=True)

    env = {**os.environ,
           "PS4": "+ ${EPOCHREALTIME} ${LINENO} ",
           "PYTHONPATH": str(HERE / "site"),
           "GATE_TIMER_LOG": str(log)}
    check = subprocess.run([sys.executable, "-c", "import sys; print('sitecustomize' in sys.modules)"],
                           env=env, capture_output=True, text=True)
    assert check.stdout.strip() == "True", "timing probe not loaded"
    log.unlink(missing_ok=True)

    started = time.time()
    with open(OUT / "pre-commit.stdout", "wb") as out, open(OUT / "pre-commit.trace", "wb") as err:
        pre = subprocess.run(["bash", "-x", "bomdd/hooks/pre-commit"], cwd=clone, env=env, stdout=out, stderr=err)
    pre_end = time.time()
    print(f"pre-commit rc={pre.returncode} {pre_end - started:.1f}s", flush=True)

    msg = base / "COMMIT_EDITMSG"
    msg.write_bytes(subprocess.run(["git", "-C", str(clone), "log", "-1", "--format=%B", REPAIR],
                                   check=True, capture_output=True).stdout)
    with open(OUT / "commit-msg.stdout", "wb") as out, open(OUT / "commit-msg.trace", "wb") as err:
        cm = subprocess.run(["bash", "-x", "bomdd/hooks/commit-msg", str(msg)], cwd=clone, env=env,
                            stdout=out, stderr=err)
    end = time.time()
    print(f"commit-msg rc={cm.returncode} {end - pre_end:.1f}s", flush=True)
    (OUT / "summary.txt").write_text(
        f"started {started:.3f}\npre-commit rc={pre.returncode} {pre_end - started:.1f}s\n"
        f"commit-msg rc={cm.returncode} {end - pre_end:.1f}s\ntotal {end - started:.1f}s\n", encoding="utf-8")
finally:
    shutil.rmtree(base, ignore_errors=True)
