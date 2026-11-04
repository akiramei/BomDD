"""ECO-122 filing basis: the costs of a dwell run that are not YAML parsing, on one register.

  python -X utf8 costs.py <register path> <single-file snapshot json>

Read-only on the repository. Times, three runs each: the history listing (git log), the blob ids (cat-file --batch-check), the
uncommitted-work scan (git status, as ECO-120 P4), and loading one JSON file that holds every blob's snapshot (the form ECO-122
proposes). The JSON file is made by prototype.py's per-blob cache merged into one file (merge in this script's --merge mode).
"""
import json
import subprocess
import sys
import time
from pathlib import Path


def t(label, fn):
    xs = []
    for _ in range(3):
        a = time.perf_counter()
        fn()
        xs.append(time.perf_counter() - a)
    print(f"{label}: " + ", ".join(f"{x:.2f}" for x in xs) + " s")


if sys.argv[1] == "--merge":
    src, dst = Path(sys.argv[2]), Path(sys.argv[3])
    d = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in src.glob("*.json")}
    dst.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print(f"merged {len(d)} snapshots, {dst.stat().st_size / 1e6:.1f} MB")
    sys.exit(0)

reg = Path(sys.argv[1]).resolve()
one = Path(sys.argv[2])
top = subprocess.check_output(["git", "-C", str(reg.parent), "rev-parse", "--show-toplevel"], text=True).strip()
rel = reg.relative_to(Path(top).resolve()).as_posix()
log = subprocess.check_output(["git", "-C", top, "log", "--reverse", "--format=%H %cI", "--", rel], text=True).split("\n")
shas = [l.split()[0] for l in log if l.strip()]
print(f"{rel}: {len(shas)} commits")
chk = subprocess.run(["git", "-C", top, "cat-file", "--batch-check"], input="".join(f"{h}:{rel}\n" for h in shas),
                     capture_output=True, text=True).stdout.splitlines()
sizes = [int(l.split()[2]) for l in chk if " blob " in l]
print(f"blobs {len(sizes)}, total {sum(sizes) / 1e6:.0f} MB, largest {max(sizes) / 1e6:.1f} MB, distinct {len(set(l.split()[0] for l in chk))}")
week = subprocess.check_output(["git", "-C", top, "log", "--since=7.days", "--format=%H", "--", rel], text=True).split()
print(f"commits in the last 7 days: {len(week)}")
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "method/tools"))
import yaml  # noqa: E402
head_blob = subprocess.check_output(["git", "-C", top, "show", f"HEAD:{rel}"])
xs = []
for _ in range(3):
    a = time.perf_counter()
    yaml.load(head_blob, Loader=yaml.CSafeLoader)
    xs.append(time.perf_counter() - a)
print(f"parse HEAD blob ({len(head_blob) / 1e6:.1f} MB, CSafeLoader): " + ", ".join(f"{x:.2f}" for x in xs)
      + f" s -> {len(head_blob) / 1e6 / min(xs):.0f} MB/s; all blobs at that rate: {sum(sizes) / 1e6 / (len(head_blob) / 1e6 / min(xs)):.0f} s serial")
t("git log", lambda: subprocess.check_output(["git", "-C", top, "log", "--reverse", "--format=%H %cI", "--", rel]))
t("batch-check", lambda: subprocess.run(["git", "-C", top, "cat-file", "--batch-check"],
                                        input="".join(f"{h}:{rel}\n" for h in shas), capture_output=True, text=True))
t("git status -uall", lambda: subprocess.check_output(["git", "-C", top, "status", "--porcelain=v1", "-z", "-uall"]))
t("load one json", lambda: json.loads(one.read_text(encoding="utf-8")))
