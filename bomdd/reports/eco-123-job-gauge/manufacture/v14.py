"""ECO-123 V1, V2 and V4 — the job view on every entry, the selftest's lines, and nothing else moving.

  python -X utf8 v14.py <BomDD repo> <old method/ dir> <work dir> <repos root>

<old method/ dir> is the filing tree's method/ (git archive a968c51 method), so the old tool runs with its own activation map and no
worktree is written into BomDD's git directory.
  V1  for every register entry, `bomdd-job.py <ID> --json` (cwd BomDD) from the old and the changed tool: identical bytes except the 12
      named in the order; for those the only differing field is stop_type, LEDGER_INCONSISTENT -> NONE
  V2  the changed tool's --selftest: exit 0, and its lines name the four English-heading arms and the two new cache arms
  V4  --all --json and --all byte-identical; --dwell on BomDD's and ViewTube's registers in-process at one fixed now, no cache, text and
      JSON byte-identical between the tools; _dwell_cache_key() equal; bomdd-run.py --selftest exit 0
"""
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

TWELVE = {"ECO-105", "ECO-106", "ECO-107", "ECO-108", "ECO-109", "ECO-110", "ECO-111", "ECO-116", "ECO-117", "ECO-118", "ECO-120", "ECO-121"}
NOW = dt.datetime(2026, 11, 4, 12, 0, tzinfo=dt.timezone.utc)


def main():
    bomdd, old, work, root = (Path(a).resolve() for a in sys.argv[1:5])
    new_tool, old_tool = bomdd / "method/tools/bomdd-job.py", old / "tools/bomdd-job.py"
    print(f"old tool sha256 {hashlib.sha256(old_tool.read_bytes()).hexdigest()[:16]}, new {hashlib.sha256(new_tool.read_bytes()).hexdigest()[:16]}")

    def cli(tool, *args):
        return subprocess.run([sys.executable, "-X", "utf8", str(tool), *args], cwd=bomdd, capture_output=True)

    ok = {}
    import yaml
    ids = [e["id"] for e in yaml.safe_load((bomdd / "bomdd/60-change-register.yaml").read_text(encoding="utf-8"))["changes"]]
    same, changed, bad = 0, [], []
    for i in ids:
        a, b = cli(old_tool, i, "--json"), cli(new_tool, i, "--json")
        if a.stdout == b.stdout:
            same += 1
            if i in TWELVE:
                bad.append(f"{i}: unchanged but named")
            continue
        ja, jb = json.loads(a.stdout)["jobs"][0], json.loads(b.stdout)["jobs"][0]
        diff = sorted(k for k in set(ja) | set(jb) if ja.get(k) != jb.get(k))
        va, vb = ja["stop_type"]["value"], jb["stop_type"]["value"]
        changed.append(i)
        if i not in TWELVE or diff != ["stop_type"] or (va, vb) != ("LEDGER_INCONSISTENT", "NONE"):
            bad.append(f"{i}: fields {diff}, stop {va} -> {vb}")
    print(f"V1 entries {len(ids)}: identical {same}, changed {len(changed)} ({', '.join(changed)}); unexpected: {bad or 'none'}")
    ok["V1"] = not bad and set(changed) == TWELVE

    st = cli(new_tool, "--selftest")
    out = st.stdout.decode("utf-8", "replace")
    need = ["verified 台帳= NONE", "implemented 台帳= 不整合", "verified 語なしはクローズでない", "fence 内無視", "版キーが source に追従",
            "amend で消えた版を残さない"]
    missing = [n for n in need if n not in out]
    print(f"V2 bomdd-job --selftest exit {st.returncode}; arms named {len(need) - len(missing)}/{len(need)}; missing {missing or 'none'}")
    for l in out.splitlines():
        print("    " + l[:150])
    ok["V2"] = st.returncode == 0 and not missing

    good = True
    for args in (["--all", "--json"], ["--all"]):
        a, b = cli(old_tool, *args), cli(new_tool, *args)
        s = a.stdout == b.stdout and a.returncode == b.returncode == 0
        good &= s
        print(f"V4 {' '.join(args)}: {len(a.stdout)} / {len(b.stdout)} bytes -> {'identical' if s else 'DIFFERENT'}")
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(old_tool, work / "bj_o123.py")
    shutil.copyfile(new_tool, work / "bj_n123.py")
    sys.path.insert(0, str(work))
    import bj_o123
    import bj_n123
    for repo, rel in (("BomDD", "bomdd/60-change-register.yaml"), ("ViewTube", "bomdd/process/change-register.yaml")):
        reg = root / repo / rel
        ra, rb = bj_o123.dwell(reg, 14, NOW), bj_n123.dwell(reg, 14, NOW)
        t = bj_o123.render_dwell(ra).encode() == bj_n123.render_dwell(rb).encode()
        j = json.dumps(ra, ensure_ascii=False, indent=2).encode() == json.dumps(rb, ensure_ascii=False, indent=2).encode()
        good &= t and j
        print(f"V4 --dwell {repo}: text identical {t}, json identical {j} (open {len(ra['open'])})")
    k = bj_o123._dwell_cache_key() == bj_n123._dwell_cache_key()
    good &= k
    print(f"V4 cache key equal: {k}")
    r = subprocess.run([sys.executable, "-X", "utf8", str(bomdd / "method/tools/bomdd-run.py"), "--selftest"], cwd=bomdd, capture_output=True)
    print(f"V4 bomdd-run --selftest exit {r.returncode}")
    ok["V4"] = good and r.returncode == 0
    print("; ".join(f"{k} {'PASS' if v else 'FAIL'}" for k, v in ok.items()))


if __name__ == "__main__":
    main()
