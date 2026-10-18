"""ECO-112 V6 under the user's exception ruling (2026-10-18, "A"): the change set is the commits attributed to ECO-112 only.

Usage: python -B diff_window.py <repo> <baseline> <head> [--control-include <sha>]   (prints the evidence as Markdown; exit 0 = every
       check holds). --control-include attributes that commit to ECO-112 on purpose: the positive control, which must exit 1.

Attribution is by the commit subject's tag, "(eco-112)" or another "(eco-NNN)"; a commit with no tag is reported and fails the run.
Checks:
  C1 every commit in baseline..head is attributed; the excluded set is exactly the commits of other ECOs (listed with their reason).
  C2 an excluded commit touches no ECO-112 allowed path except the shared register, and there only adds lines inside its own ECO's entry;
     the ECO-112 register entry is byte-identical before and after it.
  C3 no ECO-112 commit touches a path an excluded commit introduced, and those paths are unchanged from the excluded commit to head.
  C4 every path changed by an ECO-112 commit is inside the register's ECO-112 diff_audit.allowed_paths (V6).
  C5 the net diff baseline..head, with the excluded commits' own entry removed from the register, changes only ECO-112's paths and,
     in the register, only the ECO-112 entry.
"""
import re
import subprocess
import sys

REPO, BASE, HEAD = sys.argv[1], sys.argv[2], sys.argv[3]
CONTROL = sys.argv[5] if len(sys.argv) == 6 and sys.argv[4] == "--control-include" else None
ECO = "ECO-112"
REG = "bomdd/60-change-register.yaml"
TAG_RE = re.compile(r"\((eco-\d{3})\)")


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
        return None, lines
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("  - id: ")), len(lines))
    while end > start + 1 and lines[end - 1] == "":   # the last entry of the file: the trailing newline is not part of it
        end -= 1
    return (start, end), lines


def allowed_paths(rev):
    reg = git("show", f"{rev}:{REG}")
    span, lines = entry(reg, ECO)
    blk = "\n".join(lines[span[0]:span[1]])
    m = re.search(r"allowed_paths: \[([^\]]*)\]", blk)
    return [p.strip() for p in m.group(1).split(",")]


def inside(path, allowed):
    return any(path == a or (a.endswith("/") and path.startswith(a)) for a in allowed)


out, bad = [], []
commits = [ln.split(" ", 1) for ln in git("log", "--reverse", "--format=%H %s", f"{BASE}..{HEAD}").splitlines()]
allowed = allowed_paths(HEAD)
own, excluded = [], []
out.append(f"# ECO-112 diff window under the exception ruling — `{BASE}..{HEAD[:12]}`\n")
out.append(f"ECO-112 `diff_audit.allowed_paths` (register at `{HEAD[:12]}`): " + ", ".join(f"`{a}`" for a in allowed) + "\n")
out.append("| commit | attributed to | paths changed |\n|---|---|---|")
for sha, subj in commits:
    tags = TAG_RE.findall(subj)
    files = [ln.split("\t", 1)[1] for ln in git("diff-tree", "--no-commit-id", "-r", "--name-status", sha).splitlines()]
    who = tags[0].upper() if len(set(tags)) == 1 else None
    if CONTROL and sha.startswith(CONTROL):
        who = ECO
    if who is None:
        bad.append(f"C1: {sha[:7]} has no single ECO tag: {subj[:60]}")
    (own if who == ECO else excluded).append((sha, subj, files, who))
    out.append(f"| `{sha[:7]}` | {who or '?'} | {len(files)} |")

out.append("\n## Excluded commits (C1) and why\n")
for sha, subj, files, who in excluded:
    out.append(f"- `{sha[:7]}` — {who}: {subj[:100]}… — another ECO's filing, outside ECO-112's manufacture (user ruling 2026-10-18 \"A\").")

out.append("\n## C2 — the excluded commits against ECO-112's paths and register entry\n")
for sha, subj, files, who in excluded:
    shared = [f for f in files if inside(f, allowed)]
    out.append(f"- `{sha[:7]}`: paths inside ECO-112's allowed paths: {shared or 'none'}")
    if any(f != REG for f in shared):
        bad.append(f"C2: {sha[:7]} touches ECO-112 paths {shared}")
    if REG in files:
        before, after = git("show", f"{sha}^:{REG}"), git("show", f"{sha}:{REG}")
        sb, lb = entry(before, ECO)
        sa, la = entry(after, ECO)
        same = lb[sb[0]:sb[1]] == la[sa[0]:sa[1]]
        diff = git("diff", "-U0", f"{sha}^", sha, "--", REG)
        removed = [l for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
        hunks = [tuple(int(x or 1) for x in m.groups()) for m in re.finditer(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff, re.M)]
        own_span, _ = entry(after, who)
        within = all(own_span and own_span[0] + 1 <= s and s + n - 1 <= own_span[1] for s, n in hunks)
        out.append(f"  - register: removed lines {len(removed)}; added hunks {hunks} inside {who}'s entry (lines {own_span[0] + 1}-{own_span[1]}): "
                   f"{within}; ECO-112 entry byte-identical before/after: {same}")
        if removed or not within or not same:
            bad.append(f"C2: {sha[:7]} register change is not confined to its own entry")

out.append("\n## C3 — paths the excluded commits introduced, after them\n")
for sha, subj, files, who in excluded:
    theirs = [f for f in files if f != REG]
    touched_by_own = sorted({f for _, _, fs, _ in own for f in fs} & set(theirs))
    later = git("diff", "--name-only", sha, HEAD, "--", *theirs).split() if theirs else []
    out.append(f"- `{sha[:7]}`: {len(theirs)} paths; touched by an ECO-112 commit: {touched_by_own or 'none'}; changed between `{sha[:7]}` and head: {later or 'none'}")
    if touched_by_own or later:
        bad.append(f"C3: {sha[:7]} paths touched later: {touched_by_own or later}")

out.append("\n## C4 — the ECO-112 change set, enumerated (V6)\n")
changed = {}
for sha, subj, files, who in own:
    for f in files:
        changed.setdefault(f, []).append(sha[:7])
for f in sorted(changed):
    ok = inside(f, allowed)
    out.append(f"- `{f}` — {', '.join(changed[f])}" + ("" if ok else " **OUTSIDE**"))
    if not ok:
        bad.append(f"C4: {f} outside allowed_paths")
out.append(f"\nECO-112 commits: {len(own)} ({', '.join(f'`{s[:7]}`' for s, _, _, _ in own)}); paths: {len(changed)}.")

out.append("\n## C5 — the net diff without the excluded commits' own entries\n")
net = [ln.split("\t", 1) for ln in git("diff", "--name-status", BASE, HEAD).splitlines()]
excl_paths = {f for _, _, fs, _ in excluded for f in fs if f != REG}
net_paths = sorted(p for _, p in net if p not in excl_paths)
outside = [p for p in net_paths if not inside(p, allowed)]
reg_b, reg_h = git("show", f"{BASE}:{REG}"), git("show", f"{HEAD}:{REG}")
lines_h = reg_h.split("\n")
for _, _, _, who in excluded:
    sp, lines_h = entry("\n".join(lines_h), who)
    if sp:
        lines_h = lines_h[:sp[0]] + lines_h[sp[1]:]
sb, lb = entry(reg_b, ECO)
sh, lh = entry("\n".join(lines_h), ECO)
rest_b = lb if sb is None else lb[:sb[0]] + lb[sb[1]:]   # the baseline may predate the ECO-112 entry (it is added by the filing)
rest_same = rest_b == lh[:sh[0]] + lh[sh[1]:]
out.append(f"- net paths (excluded commits' own paths removed): {len(net_paths)}; outside ECO-112's allowed paths: {outside or 'none'}")
out.append(f"- register with the excluded ECOs' entries removed: everything outside the ECO-112 entry equals the baseline: {rest_same}")
if outside or not rest_same:
    bad.append(f"C5: net diff outside ECO-112: {outside} / register rest same {rest_same}")

out.append("\n## Result\n")
out.append("**PASS** — every check holds." if not bad else "**FAIL**\n" + "\n".join(f"- {b}" for b in bad))
sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
sys.exit(1 if bad else 0)
