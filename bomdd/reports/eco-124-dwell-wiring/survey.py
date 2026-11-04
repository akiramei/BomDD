"""ECO-124 filing basis: what a session-start summary of the dwell view would show, per repository, and what it costs.

  python -X utf8 survey.py <repos root>

Read-only on the repositories (the dwell cache in the user's cache directory is used and updated, as the command line does). For each
register: the full text output's line count, the time of a warm command-line run (wall clock, the cache already filled), and from
--json: open entries, over the threshold (14 days), unexplained over it, crossed the threshold within the last 7 days (14 < days <= 21)
without a reason, paused, warnings, dirty paths.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

REGS = [("BomDD", "bomdd/60-change-register.yaml"), ("ViewTube", "bomdd/process/change-register.yaml"),
        ("ViewPrism2", "bomdd/60-change-register.yaml"), ("BomDD-Plm", "bomdd/60-change-register.yaml"),
        ("MoviePad-Remake", "bomdd/60-change-register.yaml"), ("TimetableAdv", "bomdd/60-change-register.yaml")]
root = Path(sys.argv[1]).resolve()
tool = root / "BomDD/method/tools/bomdd-job.py"
for repo, rel in REGS:
    top = root / repo
    if not (top / rel).exists():
        print(f"{repo}: no register at {rel}")
        continue
    subprocess.run([sys.executable, "-X", "utf8", str(tool), "--dwell", "--register", rel, "--json"], cwd=top, capture_output=True)  # fill
    t = time.perf_counter()
    txt = subprocess.run([sys.executable, "-X", "utf8", str(tool), "--dwell", "--register", rel], cwd=top, capture_output=True)
    warm = time.perf_counter() - t
    j = json.loads(subprocess.run([sys.executable, "-X", "utf8", str(tool), "--dwell", "--register", rel, "--json"], cwd=top,
                                  capture_output=True).stdout)
    if "error" in j:
        print(f"{repo}: not measured: {j['error']}")
        continue
    o = j["open"]
    over = [e for e in o if e["over_threshold"]]
    unex = [e for e in over if e["group"] == "none"]
    crossed = [e for e in unex if e["days"] <= j["stale_days"] + 7]
    print(f"{repo}: text {len(txt.stdout.decode('utf-8', 'replace').splitlines())} lines, warm {warm:.2f} s; open {len(o)}, over 14 d "
          f"{len(over)}, unexplained {len(unex)}, crossed in the last 7 days unexplained {len(crossed)} "
          f"({', '.join(e['id'] for e in crossed) or '-'}); paused {'yes' if j['paused'] else 'no'}; warnings {len(j['warnings'])}; "
          f"dirty {j['uncommitted']['dirty_paths']}")
