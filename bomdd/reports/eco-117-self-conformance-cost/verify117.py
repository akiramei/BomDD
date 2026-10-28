"""ECO-117 V1 and V2: the original and the changed self-conformance in throwaway clones of BomDD.

Usage: python verify117.py <bomdd-root> <changed-self-conformance.py> <out-dir>

Clones (fresh `git clone` of <bomdd-root> HEAD, core.hooksPath set so C18 runs as in the repository):
  A  original tool                          --dotnet
  B  changed tool                           --dotnet, then --c9-only with the witness present and absent
  C  changed tool, manifest with no suites  --dotnet and --c9-only (the failing side), witness absent and present
  M1 broken: --c9-only writes the witness   --c9-only
  M2 broken: --c9-only runs the fast tier   --c9-only
Each run has a time bound; progress goes to <out-dir>/progress.txt. Nothing is written to <bomdd-root>.
"""
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT, CHANGED, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
BOUND = 1500  # seconds per run
PROG = OUT / "progress.txt"
TOOL = "method/tools/self-conformance.py"


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with PROG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _rw(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clone(base, name, tool_text=None, empty_suites=False):
    d = base / name
    subprocess.run(["git", "clone", "-q", str(ROOT), str(d)], check=True)
    subprocess.run(["git", "-C", str(d), "config", "core.hooksPath", "bomdd/hooks"], check=True)
    if tool_text is not None:
        (d / TOOL).write_bytes(tool_text.encode("utf-8"))
    if empty_suites:
        (d / "loops/expected-results.yaml").write_bytes(b"suites: []\n")
    return d


def witness(d):
    w = d / ".git" / "bomdd-selfconf-witness"
    return w.read_bytes() if w.exists() else None


def run(d, tag, *flags):
    log(f"start {tag}: {' '.join(flags) or '(default)'}")
    t0 = time.perf_counter()
    try:
        p = subprocess.run([sys.executable, str(d / TOOL), *flags], cwd=d, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=BOUND)
        rc, out = p.returncode, p.stdout + ("\n--- stderr ---\n" + p.stderr if p.stderr else "")
    except subprocess.TimeoutExpired as e:
        rc, out = "TIMEOUT", (e.stdout or "") if isinstance(e.stdout, str) else ""
    secs = time.perf_counter() - t0
    (OUT / f"{tag}.txt").write_text(f"exit={rc} wall={secs:.1f}s\n{out}", encoding="utf-8", newline="\n")
    log(f"end {tag}: exit={rc} {secs:.1f} s")
    return rc, out


def norm(line, d):
    line = line.replace(str(d), "<ROOT>")
    line = re.sub(r"[A-Za-z]:\\[^\s]*?\\Temp\\[^\s;,)\]]*", "<TMP>", line)
    line = re.sub(r"(bomdd-selfconf-[a-z0-9]+-|tmp)[a-z0-9_]{6,}", r"\1*", line)
    return line


def check_lines(out, d):
    return [norm(l, d) for l in out.splitlines() if re.match(r"^\[C\d+b?\] ", l)]


def compare(name, a, b):
    same = a == b
    diff = [f"  - {x}\n  + {y}" for x, y in zip(a, b) if x != y]
    if len(a) != len(b):
        diff.append(f"  length {len(a)} vs {len(b)}")
    return same, diff


src = CHANGED.read_text(encoding="utf-8")
orig = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{TOOL}"], capture_output=True, check=True).stdout.decode("utf-8")
WIT_BLOCK = '        print("[witness] 書出しなし・既存も変更なし(--c9-only は fast tier を実行しない — ECO-117)")\n'
assert src.count(WIT_BLOCK) == 1
m1 = src.replace(WIT_BLOCK, WIT_BLOCK + "        _write_selfconf_witness()  # MUTANT M1\n")
SEL = '    if a.c9_only:\n        checks = [("C9", c9_dotnet)]\n    else:\n'
assert src.count(SEL) == 1
m2 = src.replace(SEL, '    if False:  # MUTANT M2\n        checks = [("C9", c9_dotnet)]\n    else:\n')
m2 = m2.replace("        if a.dotnet:\n            checks.append", "        if a.dotnet or a.c9_only:\n            checks.append")
assert m1 != src and m2 != src

base = Path(tempfile.mkdtemp(prefix="eco117-v-"))
res = {}
try:
    A = clone(base, "A")
    B = clone(base, "B", src)
    C = clone(base, "C", src, empty_suites=True)
    M1 = clone(base, "M1", m1)
    M2 = clone(base, "M2", m2)
    log(f"clones at {base}; HEAD {subprocess.run(['git', '-C', str(A), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}")
    rc_d = subprocess.run([sys.executable, str(B / TOOL), "--c9-only", "--dotnet"], cwd=B, capture_output=True, text=True).returncode
    res["V2(d) --c9-only --dotnet exit"] = rc_d

    with ThreadPoolExecutor(2) as ex:
        fa, fb = ex.submit(run, A, "A-dotnet", "--dotnet"), ex.submit(run, B, "B-dotnet", "--dotnet")
        (ra, oa), (rb, ob) = fa.result(), fb.result()
    with ThreadPoolExecutor(3) as ex:
        fc = ex.submit(run, C, "C-dotnet", "--dotnet")
        w_m1_before = witness(M1)
        fm1 = ex.submit(run, M1, "M1-c9only", "--c9-only")
        fm2 = ex.submit(run, M2, "M2-c9only", "--c9-only")
        (rc, oc), (rm1, om1), (rm2, om2) = fc.result(), fm1.result(), fm2.result()
    w_m1_after = witness(M1)

    wb0 = witness(B)
    rb1, ob1 = run(B, "B-c9only-witness-present", "--c9-only")
    wb1 = witness(B)
    (B / ".git" / "bomdd-selfconf-witness").unlink()
    rb2, ob2 = run(B, "B-c9only-witness-absent", "--c9-only")
    wb2 = witness(B)
    wc0 = witness(C)
    rc1, oc1 = run(C, "C-c9only-witness-absent", "--c9-only")
    wc1 = witness(C)
    dummy = b"0000000000000000000000000000000000000000\nPASS\n"
    (C / ".git" / "bomdd-selfconf-witness").write_bytes(dummy)
    rc2, oc2 = run(C, "C-c9only-witness-present", "--c9-only")
    wc2 = witness(C)

    la, lb = check_lines(oa, A), check_lines(ob, B)
    same, diff = compare("V1", la, lb)
    res["V1 exit codes A/B (--dotnet)"] = (ra, rb)
    res["V1 [Cn] lines A == B"] = (same, len(la), diff[:10])
    time_a = [l for l in oa.splitlines() if l.startswith("[time]")]
    time_b = [l for l in ob.splitlines() if l.startswith("[time]")]
    ids_b = re.findall(r"(C\d+) \d", time_b[0]) if time_b else []
    res["V1 [time] lines A/B"] = (len(time_a), len(time_b))
    res["V1 [time] ids in B"] = ids_b
    res["V1 non-[time] lines only in B"] = sorted(set(norm(l, B) for l in ob.splitlines() if not l.startswith("[time]"))
                                                  - set(norm(l, A) for l in oa.splitlines()))[:10]
    altered = list(lb)
    altered[3] = altered[3].replace("PASS", "FAIL", 1)
    res["V1 control: comparator red on one altered line"] = not compare("ctl", la, altered)[0]

    c9_dotnet_b = [l for l in lb if l.startswith("[C9]")]
    for tag, out, d in (("B present", ob1, B), ("B absent", ob2, B)):
        lc = check_lines(out, d)
        res[f"V2(a) {tag}: only [C9] lines"] = all(l.startswith("[C9]") for l in lc) and bool(lc)
        res[f"V2(a) {tag}: [C9] lines == B --dotnet's"] = lc == c9_dotnet_b
    res["V2(a) B --dotnet [C9] == A --dotnet [C9]"] = c9_dotnet_b == [l for l in la if l.startswith("[C9]")]
    res["V2(b) PASS, witness present: byte-identical"] = (wb0 is not None, wb0 == wb1, (rb1,))
    res["V2(b) PASS, witness absent: stays absent"] = (wb2 is None, (rb2,))
    res["V2(b) FAIL, witness absent: stays absent"] = (wc0 is None and wc1 is None, (rc1,))
    res["V2(b) FAIL, witness present: byte-identical"] = (wc2 == dummy, (rc2,))
    lcd = [l for l in check_lines(oc, C) if l.startswith("[C9]")]
    lc9 = check_lines(oc1, C)
    res["V2(c) failing C9: exit --dotnet / --c9-only"] = (rc, rc1, rc2)
    res["V2(c) failing C9: same [C9] lines"] = (lcd == lc9 == check_lines(oc2, C), lc9[:3])
    res["known-bad M1 (writes witness): told apart by (b)"] = (w_m1_before is None and w_m1_after is not None, rm1)
    other = [l for l in check_lines(om2, M2) if not l.startswith("[C9]")]
    res["known-bad M2 (runs fast tier): told apart by (a)"] = (bool(other), len(other), rm2)
finally:
    shutil.rmtree(base, onexc=_rw)
    log(f"temp removed: {not base.exists()}")
    with (OUT / "results.txt").open("w", encoding="utf-8", newline="\n") as f:
        for k, v in res.items():
            f.write(f"{k}: {v}\n")
    log("results written")
