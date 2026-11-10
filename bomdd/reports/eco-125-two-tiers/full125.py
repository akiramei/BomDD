#!/usr/bin/env python3
"""ECO-125 V1 and V5: on one tree (the detached worktree of the manufacture commit), a quick run, a full run by the changed
tool, and a full run by the filing tree's tool (92fc3cb) put in its place; then the comparison.

  python full125.py <worktree> <out-dir>

The filing tree's tool is written over method/tools/self-conformance.py inside the worktree for its run and restored by
`git checkout`; so its run sees a tree that differs from the other two by that one file. The witness the full runs write is
in the worktree's own git directory and is removed at the end.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
TOOL = W / "method/tools/self-conformance.py"
FILING = "92fc3cb"
lines = []
fails = 0


def say(s):
    lines.append(s)
    print(s, flush=True)


def git(*a):
    return subprocess.run(["git", "-C", str(W), *a], capture_output=True)


def run(name, *opts):
    t0 = time.time()
    p = subprocess.run([sys.executable, str(TOOL), *opts], capture_output=True, cwd=str(W))
    text = p.stdout.decode("utf-8", "replace").replace("\r\n", "\n")
    (OUT / name).write_bytes(text.encode("utf-8"))
    say(f"{name}: exit {p.returncode}, {time.time() - t0:.0f} s")
    return p.returncode, text


def verdicts(text):
    return [ln for ln in text.splitlines() if re.match(r"^\[C\d+[a-z]?\] ", ln)]


def check(name, ok, detail=""):
    global fails
    fails += 0 if ok else 1
    say(("PASS  " if ok else "FAIL  ") + name + (f" — {detail}" if detail else ""))


head = git("rev-parse", "HEAD").stdout.decode().strip()
say(f"worktree {W} at {head}; the filing tree's tool from {FILING}")
gd = Path(git("rev-parse", "--git-dir").stdout.decode().strip())
gd = gd if gd.is_absolute() else W / gd
witness = gd / "bomdd-selfconf-witness"
try:
    cq, quick = run("quick.txt", "--quick")
    cn, new = run("full-changed-tool.txt")
    wn = witness.read_bytes() if witness.exists() else None
    old_src = git("show", f"{FILING}:method/tools/self-conformance.py").stdout
    TOOL.write_bytes(old_src)
    co, old = run("full-filing-tool.txt")
    wo = witness.read_bytes() if witness.exists() else None
finally:
    git("checkout", "--", "method/tools/self-conformance.py")
    witness.unlink(missing_ok=True)

vq, vn, vo = verdicts(quick), verdicts(new), verdicts(old)
check("all three runs exit 0", (cq, cn, co) == (0, 0, 0), f"quick {cq}, changed {cn}, filing {co}")
check("V1 every [Cn] line of the quick run is byte-identical to the same line of the full run",
      vq == [ln for ln in vn if not ln.startswith("[C11")], f"quick {len(vq)} lines, full {len(vn)} lines")
check("V1 the full run has C11 lines and the quick run has none",
      any(ln.startswith("[C11") for ln in vn) and not any(ln.startswith("[C11") for ln in vq))
check("V5 the full run's [Cn] lines are identical by the changed tool and the filing tree's tool", vn == vo,
      "" if vn == vo else "differing: " + " | ".join(a[:60] for a, b in zip(vn, vo) if a != b)[:300])
strip = lambda t: [ln for ln in t.splitlines() if not ln.startswith("[time]") and not ln.startswith("[env]")]
check("V5 every other line but [time] and [env] is identical too", strip(new) == strip(old))
# the witness names the tree, and the two runs' trees differ by the tool file; compare the result line only
res = lambda w: w.decode("utf-8", "replace").splitlines()[1:2] if w else None
check("V5 both full runs wrote a witness whose result line is PASS", res(wn) == ["PASS"] and res(wo) == ["PASS"],
      f"changed {res(wn)}, filing {res(wo)}")
for name, t in (("changed", new), ("filing", old)):
    m = re.search(r"^\[time\] (.*)$", t, re.M)
    say(f"[time] {name}: {m.group(1) if m else '(none)'}")
say(f"failures: {fails}")
(OUT / "v1-v5.txt").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
sys.exit(1 if fails else 0)
