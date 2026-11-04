"""ECO-122 V1 — the same answer on five real registers, four ways, at one fixed moment.

  python -X utf8 v1.py <old tool .py> <new tool .py> <work dir> <repos root>

<old tool> is method/tools/bomdd-job.py of 9e926be (ECO-120's tool), <new tool> the changed one. Both are copied into <work dir> as
importable modules (bj_old, bj_new) so the dwell read's worker processes can import them. For each register, at one fixed `now`:
  A  ECO-120's tool                       dwell(reg, 14, now)
  B  the new tool without a cache         dwell(reg, 14, now)
  C  the new tool with an empty cache     dwell(reg, 14, now, cache_dir=<work dir>/cache)
  D  the new tool again with that cache   (the same call)
Text = render_dwell(result); JSON = json.dumps(result, ensure_ascii=False, indent=2) (the command's own serialisation).
PASS when A, B, C and D are byte-identical in both forms, C parses every distinct blob and D parses 0. Read-only on the repositories.
"""
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REGS = [("BomDD", "bomdd/60-change-register.yaml"), ("ViewTube", "bomdd/process/change-register.yaml"),
        ("ViewPrism2", "bomdd/60-change-register.yaml"), ("BomDD-Plm", "bomdd/60-change-register.yaml"),
        ("MoviePad-Remake", "bomdd/60-change-register.yaml")]
NOW = dt.datetime(2026, 11, 4, 12, 0, tzinfo=dt.timezone.utc)


def main():
    old, new, work, root = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(old, work / "bj_old.py")
    shutil.copyfile(new, work / "bj_new.py")
    sys.path.insert(0, str(work))
    import bj_old
    import bj_new
    print(f"now (fixed) {NOW.isoformat()}; old tool sha256 {hashlib.sha256(old.read_bytes()).hexdigest()[:16]}, "
          f"new tool sha256 {hashlib.sha256(new.read_bytes()).hexdigest()[:16]}")
    ok_all = True
    for repo, rel in REGS:
        top = root / repo
        reg = top / rel
        head = subprocess.check_output(["git", "-C", str(top), "rev-parse", "HEAD"], text=True).strip()
        shas = subprocess.check_output(["git", "-C", str(top), "log", "--format=%H", "--", rel], text=True).split()
        chk = subprocess.run(["git", "-C", str(top), "cat-file", "--batch-check"], input="".join(f"{s}:{rel}\n" for s in shas),
                             capture_output=True, text=True).stdout.splitlines()
        distinct = len({l.split()[0] for l in chk if " blob " in l})
        cdir = work / "cache" / repo
        shutil.rmtree(cdir, ignore_errors=True)
        res = {"A": bj_old.dwell(reg, 14, NOW), "B": bj_new.dwell(reg, 14, NOW)}
        sc, sd = {}, {}
        res["C"] = bj_new.dwell(reg, 14, NOW, cache_dir=cdir, stats=sc)
        res["D"] = bj_new.dwell(reg, 14, NOW, cache_dir=cdir, stats=sd)
        text = {k: bj_new.render_dwell(v).encode("utf-8") for k, v in res.items()}
        js = {k: json.dumps(v, ensure_ascii=False, indent=2).encode("utf-8") for k, v in res.items()}
        same_t = len(set(text.values())) == 1
        same_j = len(set(js.values())) == 1
        counts = sc.get("parsed") == distinct and sd.get("parsed") == 0 and sd.get("hits") == len([l for l in chk if " blob " in l])
        ok = same_t and same_j and counts
        ok_all &= ok
        print(f"{repo} @ {head[:10]}: commits {len(shas)}, distinct blobs {distinct}, open {len(res['A']['open'])}; "
              f"text identical {same_t} (sha256 {hashlib.sha256(text['A']).hexdigest()[:16]}), "
              f"json identical {same_j} (sha256 {hashlib.sha256(js['A']).hexdigest()[:16]}); "
              f"cold parsed {sc.get('parsed')} hits {sc.get('hits')}, warm parsed {sd.get('parsed')} hits {sd.get('hits')} -> "
              f"{'PASS' if ok else 'FAIL'}")
    # a control: the comparison tells a one-byte difference apart
    t = bytearray(text["A"])
    t[0] ^= 1
    print(f"control: one altered byte told apart: {bytes(t) != text['A']}")
    print(f"V1 {'PASS' if ok_all else 'FAIL'}")


if __name__ == "__main__":
    main()
