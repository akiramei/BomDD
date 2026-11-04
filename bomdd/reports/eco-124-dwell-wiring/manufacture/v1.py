"""ECO-124 V1: the brief agrees with the full view on five registers at one fixed now.

  python -X utf8 v1.py <repos root>

For each register: dwell() once (the user's cache, as the command line), render_brief() on it, and an independent derivation here from
the same result (written apart from the tool's code): open count, over-threshold count, the DECIDE ids (no waiting_on, not paused,
T < days <= T+7), the backlog counts by reason, paused, uncommitted, warnings count. Compares every number and id on the brief's lines;
line count <= 8. TimetableAdv is excluded by the user's ruling.
"""
import datetime as dt
import importlib.util
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
tool = root / "BomDD/method/tools/bomdd-job.py"
spec = importlib.util.spec_from_file_location("bj", tool)
bj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bj)
NOW = dt.datetime(2026, 11, 4, 12, 0, tzinfo=dt.timezone.utc)
REGS = [("BomDD", "bomdd/60-change-register.yaml"), ("ViewTube", "bomdd/process/change-register.yaml"),
        ("ViewPrism2", "bomdd/60-change-register.yaml"), ("BomDD-Plm", "bomdd/60-change-register.yaml"),
        ("MoviePad-Remake", "bomdd/60-change-register.yaml")]
fails = 0
print(f"V1 at now = {NOW.isoformat()}, tool sha256 {__import__('hashlib').sha256(tool.read_bytes()).hexdigest()[:16]}")
for repo, rel in REGS:
    r = bj.dwell(root / repo / rel, 14, NOW, cache_dir=bj.dwell_cache_dir_default())
    lines = bj.render_brief(r).splitlines()
    # independent derivation
    T = r["stale_days"]
    opened = r["open"]
    over = [e for e in opened if e["days"] > T]
    is_paused = r["paused"] is not None
    due = [e for e in over if not is_paused and e["waiting_on"] is None and e["days"] <= T + 7]
    back = {}
    for e in over:
        if e in due:
            continue
        k = "paused" if is_paused else (e["waiting_on"] or "unexplained")
        back[k] = back.get(k, 0) + 1
    problems = []
    if len(lines) > 8:
        problems.append(f"{len(lines)} lines")
    m = re.fullmatch(r"dwell: (\S+) (\S+) — open (\d+), over (\d+) d (\d+)", lines[0])
    if not m or (m[1], m[2], int(m[3]), int(m[4]), int(m[5])) != (repo, rel, len(opened), T, len(over)):
        problems.append(f"header {lines[0]!r}")
    dec = [l for l in lines if l.startswith("DECIDE:")]
    if due:
        ids = re.findall(r"(ECO-[A-Z]*-?\d+) \S+ [\d.]+ d", dec[0]) if dec else []
        n = int(re.search(r"no reason: (\d+) —", dec[0])[1]) if dec else -1
        if n != len(due) or ids != [e["id"] for e in sorted(due, key=lambda e: -e["days"])][:10]:
            problems.append(f"DECIDE {dec} vs {[e['id'] for e in due]}")
    elif dec:
        problems.append(f"DECIDE line without due entries: {dec}")
    bl = [l for l in lines if l.startswith("backlog:")]
    got = dict((k, int(v)) for v, k in [(p.rsplit(" ", 1)[1], p.rsplit(" ", 1)[0]) for p in
                                         bl[0][len("backlog: "):].split(" (a triage")[0].split(" · ")]) if bl and "none" not in bl[0][:14] else {}
    if got != back:
        problems.append(f"backlog {got} vs {back}")
    pl = [l for l in lines if l.startswith("paused:")]
    if bool(pl) != is_paused:
        problems.append("paused line")
    u = r["uncommitted"]
    ul = [l for l in lines if l.startswith("uncommitted:")]
    if not ul or f"dirty {u['dirty_paths']}," not in ul[0] or ul[0].endswith("yes") != u["register_differs_from_head"]:
        problems.append(f"uncommitted {ul}")
    wl = [l for l in lines if l.startswith("warnings:")]
    if (int(wl[0].split()[1]) if wl else 0) != len(r["warnings"]):
        problems.append("warnings")
    fails += bool(problems)
    print(f"{'PASS' if not problems else 'FAIL'} {repo}: {len(lines)} lines; open {len(opened)}, over {len(over)}, DECIDE "
          f"{[e['id'] for e in due] or '-'}, backlog {back or '-'}, paused {'yes' if is_paused else 'no'}, dirty {u['dirty_paths']}, "
          f"warnings {len(r['warnings'])}" + (f" — {problems}" if problems else ""))
    for l in lines:
        print(f"    | {l}")
print(f"V1 {'PASS' if not fails else 'FAIL'} ({len(REGS) - fails}/{len(REGS)})")
sys.exit(1 if fails else 0)
