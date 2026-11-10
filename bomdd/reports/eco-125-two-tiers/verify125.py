#!/usr/bin/env python3
"""ECO-125 V2, V3, V4 and the two known-bad copies, measured in a detached worktree of the manufacture commit.

  python verify125.py <worktree> <out-file>

The worktree is made by the caller (`git worktree add --detach <worktree> <commit>`) outside the repository; this script
creates and deletes one local branch there (v125-tmp, tracking main) so that an upstream exists, edits files only inside the
worktree and restores them, and writes <out-file>. It never pushes: the hook is run directly with one ref line on its input.
"""
import hashlib
import re
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
TOOL = W / "method/tools/self-conformance.py"
lines = []
fails = 0


def say(s):
    lines.append(s)
    print(s, flush=True)


def git(*a, **kw):
    return subprocess.run(["git", "-C", str(W), *a], capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def quick(tool=TOOL):
    t0 = time.time()
    p = subprocess.run([sys.executable, str(tool), "--quick"], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(W))
    return p.returncode, p.stdout, time.time() - t0


def check(name, ok, detail=""):
    global fails
    fails += 0 if ok else 1
    say(("PASS  " if ok else "FAIL  ") + name + (f" — {detail}" if detail else ""))


def notice(out):
    m = re.search(r"^\[quick\] C11 inputs changed: (.*)$", out, re.M)
    return m.group(1) if m else "(no notice line)"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


head = git("rev-parse", "HEAD").stdout.strip()
say(f"worktree {W} at {head}")
r = git("checkout", "-q", "-b", "v125-tmp", "--track", "main")
assert r.returncode == 0, r.stderr
gd = Path(git("rev-parse", "--git-dir").stdout.strip())
gd = gd if gd.is_absolute() else W / gd
witness = gd / "bomdd-selfconf-witness"
witness.unlink(missing_ok=True)
REG = W / "bomdd/60-change-register.yaml"
try:
    # V2a: no witness -> a quick pass leaves none, and the hook refuses
    code, out, sec = quick()
    check("V2a quick passes on the clean worktree", code == 0 and "(quick) passed" in out, f"exit {code}, {sec:.1f} s")
    check("V2a a quick pass leaves no witness", not witness.exists())
    hook = subprocess.run(["sh", "bomdd/hooks/pre-push"], input=f"refs/heads/v125-tmp {head} refs/heads/v125-tmp {'0' * 40}\n",
                          capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(W))
    check("V2a the pre-push hook refuses that tree with no witness", hook.returncode == 1, f"exit {hook.returncode}")
    # V2b: an existing witness is left byte-identical by a quick pass and by a quick failure
    witness.write_bytes(b"0000000000000000000000000000000000000000\nPASS\n")
    before = sha(witness)
    code, out, _ = quick()
    check("V2b a quick pass leaves an existing witness byte-identical", code == 0 and sha(witness) == before)
    orig = REG.read_bytes()
    REG.write_bytes(orig + b"  - id: [broken\n")
    code, out, _ = quick()
    REG.write_bytes(orig)
    check("V3 a register that does not parse makes the quick run exit 1 with its own FAILED line",
          code == 1 and "self-conformance (quick) FAILED" in out, f"exit {code}")
    check("V2b a quick failure leaves an existing witness byte-identical", sha(witness) == before)
    # V3: the notice
    _, out, _ = quick()
    check("V3 notice on the clean worktree is no", notice(out) == "no", notice(out))
    probe = W / "method/templates/process-core/eco125-probe.txt"
    probe.write_text("x\n", encoding="utf-8")
    _, out, _ = quick()
    probe.unlink()
    check("V3 notice with a new file under method/templates/process-core is yes", notice(out).startswith("yes"), notice(out))
    rec = W / "bomdd/60-change-order-eco-125.md"
    rb = rec.read_bytes()
    rec.write_bytes(rb + b"\nrecord-only change\n")
    _, out, _ = quick()
    rec.write_bytes(rb)
    check("V3 notice with a record-only change is no", notice(out) == "no", notice(out))
    imp = W / "method/improvements.md"
    ib = imp.read_bytes()
    imp.write_bytes(ib + b"\nrecord-only change\n")
    _, out, _ = quick()
    imp.write_bytes(ib)
    check("V3 notice with a change to method/improvements.md alone is no", notice(out) == "no", notice(out))
    # V4: time, three runs
    secs = []
    for _ in range(3):
        code, out, sec = quick()
        secs.append(sec)
    check("V4 three quick runs each within 60 s", max(secs) <= 60, " / ".join(f"{s:.1f} s" for s in secs))
    good_ids = sorted(set(re.findall(r"^\[(C\d+[a-z]?)\]", out, re.M)))
    say("quick run's check ids: " + " ".join(good_ids))
    check("V1 (part) the quick run has no C11 line", not any(i.startswith("C11") for i in good_ids))
    # known-bad 1: a copy whose quick mode writes the witness
    src = TOOL.read_text(encoding="utf-8")
    a = '        print("self-conformance (quick) passed'
    assert src.count(a) == 1
    m1 = W / "method/tools/self-conformance-m1.py"
    m1.write_text(src.replace(a, "        _write_selfconf_witness()\n" + a), encoding="utf-8")
    witness.unlink(missing_ok=True)
    code, out, _ = quick(m1)
    m1.unlink()
    check("known-bad 1 (quick writes the witness) is caught by V2a's condition", witness.exists(),
          "the witness appeared" if witness.exists() else "no witness: the condition did not see it")
    witness.unlink(missing_ok=True)
    # known-bad 2: a copy whose quick mode drops another check
    b = 'checks = [c for c in checks if c[0] != "C11"]'
    assert src.count(b) == 1
    m2 = W / "method/tools/self-conformance-m2.py"
    m2.write_text(src.replace(b, 'checks = [c for c in checks if c[0] not in ("C11", "C3")]'), encoding="utf-8")
    code, out, _ = quick(m2)
    m2.unlink()
    bad_ids = sorted(set(re.findall(r"^\[(C\d+[a-z]?)\]", out, re.M)))
    check("known-bad 2 (quick drops C3) is caught by comparing the check ids", bad_ids != good_ids,
          "missing: " + " ".join(sorted(set(good_ids) - set(bad_ids))))
    # V3: no upstream
    git("checkout", "-q", "--detach")
    _, out, _ = quick()
    check("V3 notice with no upstream is not determined", notice(out).startswith("not determined"), notice(out))
finally:
    git("checkout", "-q", "--detach")
    git("branch", "-D", "v125-tmp")
    witness.unlink(missing_ok=True)
st = git("status", "--short").stdout.strip()
check("the worktree is clean at the end", st == "", st or "clean")
say(f"failures: {fails}")
OUT.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
sys.exit(1 if fails else 0)
