"""ECO-126 V3 — the launcher really starts a harmless program and logs which build ran.

usage: v3_launcher.py <BomDD root> <scratch dir>
The program is a script that writes a marker file next to itself. Exits 1 if any expectation fails.
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

root, scratch = Path(sys.argv[1]), Path(sys.argv[2])
tool = root / "method" / "tools" / "handover-stamp.py"
bad = []


def expect(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + (" — " + detail if detail else ""))
    if not ok:
        bad.append(label)


def hs(*a):
    return subprocess.run([sys.executable, str(tool), *a], capture_output=True, text=True, encoding="utf-8", errors="replace")


def fresh(name):
    d = scratch / name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    (d / "app.dll").write_bytes(b"the build that was handed over")
    # ends with a bare exit: "start" runs a script under cmd /K, which would otherwise leave a window open
    (d / "prog.cmd").write_text('@echo started> "%~dp0started.txt"\r\n@exit\r\n', encoding="ascii")
    (d / "prog.sh").write_text('#!/bin/sh\necho started > "$(dirname "$0")/started-sh.txt"\n', encoding="ascii", newline="\n")
    os.chmod(d / "prog.sh", 0o755)
    return d


def wait_for(p, seconds=10):
    end = time.time() + seconds
    while time.time() < end and not p.exists():
        time.sleep(0.2)
    return p.exists()


env = {k: v for k, v in os.environ.items() if k != "HANDOVER_NO_START"}
# no pipes: a started program would inherit them and keep this script waiting
QUIET = dict(env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)

# 1. Windows launcher: starts the program, one line, the stamp's hash
if os.name == "nt":
    d = fresh("win")
    s = hs("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "app.dll", "--label", "V3 round 1")
    r = subprocess.run(["cmd", "/c", str(d / "launch.cmd")], **QUIET)
    started = wait_for(d / "started.txt")
    c = hs("check", "--dir", str(d))
    expect("launch.cmd starts the program and logs one line with the stamp's hash",
           s.returncode == 0 and started and c.returncode == 0 and "launches: {count: 1, matching: 1}" in c.stdout,
           f"stamp {s.returncode}, launcher {r.returncode}, started {started}, check {c.returncode}")
    (d / "app.dll").write_bytes(b"a different build")
    subprocess.run(["cmd", "/c", str(d / "launch.cmd")], **QUIET)
    c = hs("check", "--dir", str(d))
    expect("a changed file is reported as a mismatch", c.returncode == 1 and "[mismatch]" in c.stdout and "[changed]" in c.stdout,
           f"check {c.returncode}")
    d = fresh("win-direct")
    hs("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "app.dll", "--label", "V3 direct")
    subprocess.run(["cmd", "/c", str(d / "prog.cmd")], **QUIET)   # bypasses the launcher
    c = hs("check", "--dir", str(d))
    expect("a start that bypasses the launcher is reported as unknown, not as a pass",
           (d / "started.txt").exists() and c.returncode == 3 and "unknown" in c.stdout, f"check {c.returncode}")
else:
    print("SKIP the Windows launcher (not on Windows)")

# 2. POSIX launcher (sh): the first two of the three (start and log; mismatch), where sh exists
sh = shutil.which("sh")
if sh:
    d = fresh("sh")
    hs("stamp", "--dir", str(d), "--program", "prog.sh", "--file", "app.dll", "--label", "V3 sh")
    r = subprocess.run([sh, str(d / "launch.sh")], **QUIET)
    c = hs("check", "--dir", str(d))
    expect("launch.sh starts the program and logs one line with the stamp's hash",
           wait_for(d / "started-sh.txt") and c.returncode == 0 and "launches: {count: 1, matching: 1}" in c.stdout,
           f"launcher {r.returncode}, check {c.returncode}")
    (d / "app.dll").write_bytes(b"a different build")
    subprocess.run([sh, str(d / "launch.sh")], **QUIET)
    c = hs("check", "--dir", str(d))
    expect("sh: a changed file is reported as a mismatch", c.returncode == 1 and "[mismatch]" in c.stdout, f"check {c.returncode}")
else:
    print("SKIP the POSIX launcher (no sh)")

print("V3:", "FAILED " + str(bad) if bad else "all as expected")
sys.exit(1 if bad else 0)
