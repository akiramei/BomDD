"""ECO-114 under the user's exception ruling (2026-10-24, "1:A" on inspection r1's IA-01 — ECO-113's method): the change set is ECO-114's commits only.
(Copied from bomdd/reports/eco-113-briefs/diff-window/diff_window.py; the constants, this docstring and the removal of ECO-113's ECO-112 branch differ.)

Usage: python -B diff_window.py <repo> <baseline> <head> [--control-include <sha>]   (prints the evidence as Markdown; exit 0 = every
       check holds). --control-include attributes that commit to ECO-114 on purpose: the positive control, which must exit 1.

The window baseline..head (the register's diff_audit.baseline be96698) holds two kinds of commit:
  - ECO-114's own (subject tag "(eco-114)"): its filing 25bea38, its manufacture, its records and its repairs;
  - one untagged record commit made between ECO-114's filing and its manufacture (afabdb1, ECO-115's held draft), named below with its reason.
Checks:
  C1 every commit is ECO-114's or the named record commit; an untagged commit not named below fails the run.
  C2 no excluded commit touches ECO-114's own records (its order, bomdd/reports/eco-114-*), and each leaves the register's ECO-114 entry
     byte-identical.
  C3 every excluded commit precedes ECO-114's first commit after its filing (the manufacture), and the method files at the manufacture's input
     equal the bytes §4 names (the excluded commit changed none of them).
  C4 every path changed by an ECO-114 commit is inside the register's ECO-114 diff_audit.allowed_paths (V8); the change set is enumerated.
  C5 the net diff from the last excluded commit to head is exactly the union of ECO-114's commits after it, and inside the allowed paths.
"""
import hashlib
import re
import subprocess
import sys

REPO, BASE, HEAD = sys.argv[1], sys.argv[2], sys.argv[3]
CONTROL = sys.argv[5] if len(sys.argv) == 6 and sys.argv[4] == "--control-include" else None
ECO, TAG = "ECO-114", "eco-114"
REG = "bomdd/60-change-register.yaml"
OWN_RECORDS = ("bomdd/60-change-order-eco-114.md", "bomdd/reports/eco-114-")
TAG_RE = re.compile(r"\((eco-\d{3})\)")
RECORD_COMMITS = {   # untagged commits in the window, excluded by the ruling, with their reasons
    "afabdb1": "ECO-115's held design draft kept as a record (bomdd/reports/eco-115-advance-decision/) - not filed, no ECO's change",
}
INPUT_TOOLS = {"method/bomdd-playbook-v1.md": "eb52d1200143", "method/templates/30-ebom.yaml": "b203de2c40f2",
               "method/templates/32-mbom.yaml": "9d5a58b4466f", "method/templates/33-control-plan.yaml": "838ee238911e",
               "method/prompts/phase3-design.md": "efbfbb76e75f"}   # order section 4 "Inputs fixed" (the files at the filing commit 25bea38)   # order §4 "Inputs fixed"


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
out.append(f"# ECO-114 diff window under the exception ruling — `{BASE}..{HEAD[:12]}`\n")
out.append(f"ECO-114 `diff_audit.allowed_paths` (register at `{HEAD[:12]}`): " + ", ".join(f"`{a}`" for a in allowed) + "\n")
out.append("| # | commit | attributed to | paths changed |\n|---|---|---|---|")
for i, (sha, subj) in enumerate(commits, 1):
    tags = set(TAG_RE.findall(subj))
    if CONTROL and sha.startswith(CONTROL):
        kind, reason = "own", "positive control: counted as ECO-114 on purpose"
    elif tags == {TAG}:
        kind, reason = "own", ""
    elif not tags and sha[:7] in RECORD_COMMITS:
        kind, reason = "excluded", RECORD_COMMITS[sha[:7]]
    else:
        kind, reason = None, ""
        bad.append(f"C1: {sha[:7]} is not attributable: {subj[:60]}")
    fs = files_of(sha)
    seq.append((sha, subj, fs, kind, reason))
    out.append(f"| {i} | `{sha[:7]}` | {'ECO-114' if kind == 'own' else ('excluded' if kind else '?')} | {len(fs)} |")
own = [s for s in seq if s[3] == "own"]
excluded = [s for s in seq if s[3] == "excluded"]

out.append("\n## C1 — excluded commits and why\n")
for sha, subj, fs, _, reason in excluded:
    out.append(f"- `{sha[:7]}` — {reason}. ({subj[:70]}…)")

out.append("\n## C2 — the excluded commits against ECO-114's own records and register entry\n")
for sha, subj, fs, _, _ in excluded:
    hit = [f for f in fs if f == OWN_RECORDS[0] or f.startswith(OWN_RECORDS[1])]
    same = True
    if REG in fs:
        same = entry(git("show", f"{sha}^:{REG}"), ECO) == entry(git("show", f"{sha}:{REG}"), ECO)
    out.append(f"- `{sha[:7]}`: ECO-114 records touched: {hit or 'none'}; ECO-114 register entry byte-identical: {same}")
    if hit or not same:
        bad.append(f"C2: {sha[:7]} touches ECO-114's records {hit} / entry same {same}")

out.append("\n## C3 — the excluded commits precede ECO-114's manufacture; the manufacture's input\n")
idx = {s[0]: i for i, s in enumerate(seq)}
filing = own[0] if own else None
after_filing = [s for s in own[1:]]
first_mf = idx[after_filing[0][0]] if after_filing else len(seq)
late = [s[0][:7] for s in excluded if idx[s[0]] > first_mf]
out.append(f"- ECO-114's filing: `{filing[0][:7] if filing else '-'}`; first ECO-114 commit after it: "
           f"`{after_filing[0][0][:7] if after_filing else '-'}`; excluded commits after that: {late or 'none'}")
if late:
    bad.append(f"C3: excluded commits after ECO-114's manufacture began: {late}")
last_ex = max((idx[s[0]] for s in excluded), default=None)
input_rev = seq[last_ex][0] if last_ex is not None else BASE
for path, want in INPUT_TOOLS.items():
    got = hashlib.sha256(git("show", f"{input_rev}:{path}", binary=True)).hexdigest()[:12]
    out.append(f"- `{path}` at the input `{input_rev[:7]}`: `{got}` (order §4: `{want}`) — {'equal' if got == want else '**DIFFERENT**'}")
    if got != want:
        bad.append(f"C3: {path} at {input_rev[:7]} is {got}, §4 names {want}")

out.append("\n## C4 — the ECO-114 change set, enumerated (V8)\n")
changed = {}
for sha, _, fs, _, _ in own:
    for f in fs:
        changed.setdefault(f, []).append(sha[:7])
for f in sorted(changed):
    ok = inside(f, allowed)
    out.append(f"- `{f}` — {', '.join(changed[f])}" + ("" if ok else " **OUTSIDE**"))
    if not ok:
        bad.append(f"C4: {f} outside allowed_paths")
out.append(f"\nECO-114 commits: {len(own)} ({', '.join(f'`{s[0][:7]}`' for s in own)}); paths: {len(changed)}.")

out.append("\n## C5 — the net diff from the manufacture's input to head\n")
net = sorted(ln.split("\t")[-1] for ln in git("diff", "--name-status", input_rev, HEAD).splitlines())
union = sorted({f for s in own if idx[s[0]] > (last_ex if last_ex is not None else -1) for f in s[2]})
outside = [p for p in net if not inside(p, allowed)]
out.append(f"- `{input_rev[:7]}..{HEAD[:7]}`: {len(net)} paths; equal to the union of ECO-114's commits after the input: {net == union}; "
           f"outside the allowed paths: {outside or 'none'}")
if net != union or outside:
    bad.append(f"C5: net {net} vs union {union} / outside {outside}")

out.append("\n## Result\n")
out.append("**PASS** — every check holds." if not bad else "**FAIL**\n" + "\n".join(f"- {b}" for b in bad))
sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
sys.exit(1 if bad else 0)
