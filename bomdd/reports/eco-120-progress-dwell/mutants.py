"""ECO-120: the --dwell selftest arms against deliberately broken copies of bomdd-job.py (each must turn the dwell selftest red).

usage: python mutants.py   (from the BomDD root; copies go to a temporary directory; writes mutants-results.txt here)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parents[2] / "method" / "tools" / "bomdd-job.py"
MUTANTS = {
    "M1 start = first entry into the status (not the last)": ('iso, _, sha = st_hist[eid][-1]', 'iso, _, sha = [x for x in st_hist[eid] if x[1] == st][0]'),
    "M2 an unparsable commit is skipped silently": ('warnings = [f"読めないコミット', 'warnings = [] and [f"読めないコミット'),
    "M3 untracked files are not counted": ('"--porcelain=v1", "-z", "-uall"', '"--porcelain=v1", "-z", "-uno"'),
    "M4 an invalid waiting_on is not warned": ('if w is not None and not (w in WAITING_VOCAB', 'if False and not (w in WAITING_VOCAB'),
    "M5 a pause does not group the open entries": ('reason = "paused" if paused else (w or "none")', 'reason = w or "none"'),
    "M6 the age uses the modification time only": ('m = max(s.st_mtime, getattr(s, "st_birthtime", None) or s.st_ctime)', 'm = s.st_mtime'),
}


def main():
    src = TOOL.read_text(encoding="utf-8")
    lines = []
    with tempfile.TemporaryDirectory() as td:
        for name, (old, new) in MUTANTS.items():
            if src.count(old) != 1:
                lines.append(f"{name}: UNMEASURED - the anchor occurs {src.count(old)} times")
                continue
            p = Path(td) / "bomdd-job.py"
            p.write_text(src.replace(old, new), encoding="utf-8", newline="\n")
            r = subprocess.run([sys.executable, str(p), "--selftest"], capture_output=True, text=True, encoding="utf-8")
            dwell_line = next((l for l in r.stdout.splitlines() if l.startswith("bomdd-job dwell selftest")), "(no dwell line)")
            red = "FAILED" in dwell_line
            detail = [l.strip() for l in r.stdout.splitlines() if l.startswith("  ")][-3:] if red else []
            lines.append(f"{name}: {'RED (caught)' if red else 'GREEN (missed)'} - exit {r.returncode}; {' | '.join(detail)[:300]}")
    caught = sum("RED" in l for l in lines)
    lines.append(f"caught {caught} of {len(MUTANTS)}")
    (HERE / "mutants-results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
