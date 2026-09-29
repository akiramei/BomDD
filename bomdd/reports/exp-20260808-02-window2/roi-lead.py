import re, subprocess, sys, io
from pathlib import Path
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
log = subprocess.run(["git", "log", "--since=2026-09-19", "--format=%h|%ci|%s", "--reverse"], cwd=VT,
                     capture_output=True, text=True, encoding="utf-8").stdout
rows = []
for line in log.splitlines():
    h, ci, s = line.split("|", 2)
    rows.append((h, datetime.fromisoformat(ci.strip()), s))
PRODUCT = {178,179,180,181,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,209,210,211}
print("eco | kind | filed(first commit) | implemented/applied commit | lead-h | commits")
leads = {"product": [], "process": []}
for n in range(178, 212):
    mine = [r for r in rows if re.search(rf"eco-vt-{n}\b", r[2], re.I)]
    if not mine:
        continue
    first = mine[0]
    strict = [r for r in mine if re.match(rf"^(fix|record|accept)\(eco-vt-{n}\)", r[2], re.I) and re.search(r"\b(implemented|applied|accepted)\b", r[2], re.I)]
    impl = strict[0] if strict else None
    kind = "product" if n in PRODUCT else "process"
    lead = round((impl[1] - first[1]).total_seconds() / 3600, 1) if impl else None
    if lead is not None:
        leads[kind].append(lead)
    print(f"{n} | {kind} | {first[0]} {first[1]:%m-%d %H:%M} | {(impl[0] + ' ' + impl[1].strftime('%m-%d %H:%M') + ' ' + impl[2][:60]) if impl else '-'} | {lead if lead is not None else '-'} | {len(mine)}")
for k, v in leads.items():
    v.sort()
    if v:
        print(f"{k}: n={len(v)} median={v[len(v)//2]} min={v[0]} max={v[-1]} mean={sum(v)/len(v):.1f}")
