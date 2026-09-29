"""③ 是正行数: ViewTube ECO-VT-178..211 — record-file lines changed by review-response commits.
Read-only. For each ECO: commits mentioning it (subject), split into
  review-response = subject matches round|disposition|dispositioned|corrected|records corrected|R8
  other           = the rest
and sum numstat (added+deleted) over record paths (bomdd/**) vs product paths (src/**, tests/**)."""
import re, subprocess, sys, io, collections
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
PRODUCT = {178,179,180,181,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,209,210,211}

def git(*a):
    return subprocess.run(["git", *a], cwd=VT, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout

raw = git("log", "--since=2026-09-19", "--reverse", "--format=@@%h|%s", "--numstat")
commits = []
cur = None
for line in raw.splitlines():
    if line.startswith("@@"):
        h, s = line[2:].split("|", 1)
        cur = {"h": h, "s": s, "files": []}
        commits.append(cur)
    elif line.strip() and cur is not None:
        parts = line.split("\t")
        if len(parts) == 3:
            a, d, path = parts
            a = 0 if a == "-" else int(a); d = 0 if d == "-" else int(d)
            cur["files"].append((a + d, path))

REVIEW_RE = re.compile(r"round|disposition|corrected|R8\b", re.I)
def bucket(path):
    if path.startswith("bomdd/"):
        if path.endswith((".png", ".json")) and "captures" in path:
            return "capture"
        return "record"
    if path.startswith(("src/", "tests/", "test/")):
        return "product"
    if path.startswith("test-results/"):
        return "evidence"
    return "other"

print("eco | kind | review-resp commits | record lines (review-resp) | record lines (other) | product lines (all) | evidence lines (all) | total commits")
tot = collections.defaultdict(lambda: collections.Counter())
for n in range(178, 212):
    mine = [c for c in commits if re.search(rf"eco-vt-{n}\b", c["s"], re.I)]
    if not mine:
        continue
    kind = "product" if n in PRODUCT else "process"
    rr = [c for c in mine if REVIEW_RE.search(c["s"])]
    def sumb(cs, b):
        return sum(l for c in cs for l, p in c["files"] if bucket(p) == b)
    rec_rr = sumb(rr, "record"); rec_other = sumb(mine, "record") - rec_rr
    prod = sumb(mine, "product"); ev = sumb(mine, "evidence")
    print(f"{n} | {kind} | {len(rr)} | {rec_rr} | {rec_other} | {prod} | {ev} | {len(mine)}")
    t = tot[kind]; t["ecos"] += 1; t["rr_commits"] += len(rr); t["rec_rr"] += rec_rr; t["rec_other"] += rec_other; t["prod"] += prod; t["ev"] += ev; t["commits"] += len(mine)
for k, t in tot.items():
    print(k, dict(t), "record lines per ECO (review-resp):", round(t["rec_rr"] / t["ecos"], 1))
