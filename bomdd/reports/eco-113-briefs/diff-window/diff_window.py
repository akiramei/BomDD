"""ECO-113 V8 under the user's exception ruling (2026-10-24, "2:a" — ECO-112's method, ECO-112 order §8): the change set is ECO-113's commits only.

Usage: python -B diff_window.py <repo> <baseline> <head> [--control-include <sha>]   (prints the evidence as Markdown; exit 0 = every
       check holds). --control-include attributes that commit to ECO-113 on purpose: the positive control, which must exit 1.

The window baseline..head (the register's diff_audit.baseline f2d91d4) holds three kinds of commit:
  - ECO-113's own (subject tag "(eco-113)"): its filing 3c7781c, its manufacture and its records;
  - ECO-112's (tag "(eco-112)"): manufactured first by ECO-112's rule M1 (ECO-113 is built on ECO-112's verified tools);
  - three untagged record commits made between ECO-112's verification and ECO-113's manufacture, named below with their reasons.
Checks:
  C1 every commit is ECO-113's or one of the excluded kinds; an untagged commit not named below fails the run.
  C2 no excluded commit touches ECO-113's own records (its order, bomdd/reports/eco-113-*), and each leaves the register's ECO-113 entry
     byte-identical.
  C3 every excluded commit precedes ECO-113's first commit after its filing (the manufacture): ECO-112's changes to the shared tools are the
     manufacture's input, fixed in the order's §4, not part of ECO-113's change; the tools at that input equal the bytes §4 names.
  C4 every path changed by an ECO-113 commit is inside the register's ECO-113 diff_audit.allowed_paths (V8); the change set is enumerated.
  C5 the net diff from the last excluded commit to head is exactly the union of ECO-113's commits after it, and inside the allowed paths.
"""
import hashlib
import re
import subprocess
import sys

REPO, BASE, HEAD = sys.argv[1], sys.argv[2], sys.argv[3]
CONTROL = sys.argv[5] if len(sys.argv) == 6 and sys.argv[4] == "--control-include" else None
ECO, TAG = "ECO-113", "eco-113"
REG = "bomdd/60-change-register.yaml"
OWN_RECORDS = ("bomdd/60-change-order-eco-113.md", "bomdd/reports/eco-113-")
TAG_RE = re.compile(r"\((eco-\d{3})\)")
RECORD_COMMITS = {   # untagged commits in the window, excluded by the ruling, with their reasons
    "597e842": "measurement record of ECO-112/113's review rounds (bomdd/reports/session-effort-20261018/, review-origin-20261018/) — no ECO's change",
    "7a107bf": "OBS-20261019-01's hook feasibility experiment (bomdd/reports/obs-20261019-01-hook-experiment/, improvements.md) — on hold, no ECO",
    "2271102": "OBS-20261019-01's design premises (the same folder, improvements.md) — on hold, no ECO",
}
INPUT_TOOLS = {"method/tools/bomdd-run.py": "69e849630f90", "method/tools/bomdd-job.py": "823eafd97d6f",
               "method/templates/product-profile/operator-layer.md": "589082d8dc48"}   # order §4 "Inputs fixed"


def git(*a, binary=False):
    r = subprocess.run(["git", "-C", REPO, *a], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(a)} failed: {r.stderr.decode(errors='replace')}")
    return r.stdout if binary else r.stdout.decode("utf-8")


def entry(text, eco):
    """The register entry block of eco: from its '  - id: ECO-NNN' line to the next entry line (exclusive)."""
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if l == f"  - id: {eco}"), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("  - id: ")), len(lines))
    while end > start + 1 and lines[end - 1] == "":
        end -= 1
    return lines[start:end]


def allowed_paths(rev):
    blk = "\n".join(entry(git("show", f"{rev}:{REG}"), ECO))
    m = re.search(r"allowed_paths: \[([^\]]*)\]", blk)
    return [p.strip() for p in m.group(1).split(",")]


def inside(path, allowed):
    return any(path == a or (a.endswith("/") and path.startswith(a)) for a in allowed)


def files_of(sha):
    return [ln.split("\t")[-1] for ln in git("diff-tree", "--no-commit-id", "-r", "--name-status", sha).splitlines()]


out, bad = [], []
commits = [ln.split(" ", 1) for ln in git("log", "--reverse", "--format=%H %s", f"{BASE}..{HEAD}").splitlines()]
allowed = allowed_paths(HEAD)
seq = []   # (sha, subj, files, kind, reason)
out.append(f"# ECO-113 diff window under the exception ruling — `{BASE}..{HEAD[:12]}`\n")
out.append(f"ECO-113 `diff_audit.allowed_paths` (register at `{HEAD[:12]}`): " + ", ".join(f"`{a}`" for a in allowed) + "\n")
out.append("| # | commit | attributed to | paths changed |\n|---|---|---|---|")
for i, (sha, subj) in enumerate(commits, 1):
    tags = set(TAG_RE.findall(subj))
    if CONTROL and sha.startswith(CONTROL):
        kind, reason = "own", "positive control: counted as ECO-113 on purpose"
    elif tags == {TAG}:
        kind, reason = "own", ""
    elif tags == {"eco-112"}:
        kind, reason = "excluded", "ECO-112's commit — manufactured first by ECO-112 M1; ECO-113 is built on its verified tools"
    elif not tags and sha[:7] in RECORD_COMMITS:
        kind, reason = "excluded", RECORD_COMMITS[sha[:7]]
    else:
        kind, reason = None, ""
        bad.append(f"C1: {sha[:7]} is not attributable: {subj[:60]}")
    fs = files_of(sha)
    seq.append((sha, subj, fs, kind, reason))
    out.append(f"| {i} | `{sha[:7]}` | {'ECO-113' if kind == 'own' else ('excluded' if kind else '?')} | {len(fs)} |")
own = [s for s in seq if s[3] == "own"]
excluded = [s for s in seq if s[3] == "excluded"]

out.append("\n## C1 — excluded commits and why\n")
for sha, subj, fs, _, reason in excluded:
    out.append(f"- `{sha[:7]}` — {reason}. ({subj[:70]}…)")

out.append("\n## C2 — the excluded commits against ECO-113's own records and register entry\n")
for sha, subj, fs, _, _ in excluded:
    hit = [f for f in fs if f == OWN_RECORDS[0] or f.startswith(OWN_RECORDS[1])]
    same = True
    if REG in fs:
        same = entry(git("show", f"{sha}^:{REG}"), ECO) == entry(git("show", f"{sha}:{REG}"), ECO)
    out.append(f"- `{sha[:7]}`: ECO-113 records touched: {hit or 'none'}; ECO-113 register entry byte-identical: {same}")
    if hit or not same:
        bad.append(f"C2: {sha[:7]} touches ECO-113's records {hit} / entry same {same}")

out.append("\n## C3 — the excluded commits precede ECO-113's manufacture; the manufacture's input\n")
idx = {s[0]: i for i, s in enumerate(seq)}
filing = own[0] if own else None
after_filing = [s for s in own[1:]]
first_mf = idx[after_filing[0][0]] if after_filing else len(seq)
late = [s[0][:7] for s in excluded if idx[s[0]] > first_mf]
out.append(f"- ECO-113's filing: `{filing[0][:7] if filing else '-'}`; first ECO-113 commit after it: "
           f"`{after_filing[0][0][:7] if after_filing else '-'}`; excluded commits after that: {late or 'none'}")
if late:
    bad.append(f"C3: excluded commits after ECO-113's manufacture began: {late}")
last_ex = max((idx[s[0]] for s in excluded), default=None)
input_rev = seq[last_ex][0] if last_ex is not None else BASE
for path, want in INPUT_TOOLS.items():
    got = hashlib.sha256(git("show", f"{input_rev}:{path}", binary=True)).hexdigest()[:12]
    out.append(f"- `{path}` at the input `{input_rev[:7]}`: `{got}` (order §4: `{want}`) — {'equal' if got == want else '**DIFFERENT**'}")
    if got != want:
        bad.append(f"C3: {path} at {input_rev[:7]} is {got}, §4 names {want}")

out.append("\n## C4 — the ECO-113 change set, enumerated (V8)\n")
changed = {}
for sha, _, fs, _, _ in own:
    for f in fs:
        changed.setdefault(f, []).append(sha[:7])
for f in sorted(changed):
    ok = inside(f, allowed)
    out.append(f"- `{f}` — {', '.join(changed[f])}" + ("" if ok else " **OUTSIDE**"))
    if not ok:
        bad.append(f"C4: {f} outside allowed_paths")
out.append(f"\nECO-113 commits: {len(own)} ({', '.join(f'`{s[0][:7]}`' for s in own)}); paths: {len(changed)}.")

out.append("\n## C5 — the net diff from the manufacture's input to head\n")
net = sorted(ln.split("\t")[-1] for ln in git("diff", "--name-status", input_rev, HEAD).splitlines())
union = sorted({f for s in own if idx[s[0]] > (last_ex if last_ex is not None else -1) for f in s[2]})
outside = [p for p in net if not inside(p, allowed)]
out.append(f"- `{input_rev[:7]}..{HEAD[:7]}`: {len(net)} paths; equal to the union of ECO-113's commits after the input: {net == union}; "
           f"outside the allowed paths: {outside or 'none'}")
if net != union or outside:
    bad.append(f"C5: net {net} vs union {union} / outside {outside}")

out.append("\n## Result\n")
out.append("**PASS** — every check holds." if not bad else "**FAIL**\n" + "\n".join(f"- {b}" for b in bad))
sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
sys.exit(1 if bad else 0)
