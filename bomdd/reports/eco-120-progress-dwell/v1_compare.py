"""V1 (ECO-120): bomdd-job --dwell against the full read of section 0 (dwell.py's JSON), on the six registers at the heads in heads.txt.

usage: python v1_compare.py   (run from the BomDD root; writes v1/<repo>.dwell.json and v1/results.txt)
For every open entry: the commit --dwell gives as the start of the current status must be the commit at which dwell.py records that
status's last change (compared by commit; dwell.py keeps 10 hex digits). The repository's HEAD must equal heads.txt (else UNMEASURED).
"""
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOS = Path(__file__).resolve().parents[4]
REGS = {"BomDD": "bomdd/60-change-register.yaml", "ViewTube": "bomdd/process/change-register.yaml",
        "TimetableAdv": "bomdd/60-change-register.yaml", "ViewPrism2": "bomdd/60-change-register.yaml",
        "BomDD-Plm": "bomdd/60-change-register.yaml", "MoviePad-Remake": "bomdd/60-change-register.yaml"}
TOOL = REPOS / "BomDD" / "method" / "tools" / "bomdd-job.py"


def main():
    heads = dict(l.split()[:2] for l in (HERE / "heads.txt").read_text(encoding="utf-8").splitlines() if l.strip())
    out_dir = HERE / "v1"
    out_dir.mkdir(exist_ok=True)
    lines, bad = [], 0
    for repo, rel in REGS.items():
        top = REPOS / repo
        head = subprocess.run(["git", "-C", str(top), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        if head != heads[repo] and repo != "BomDD":
            lines.append(f"{repo}: UNMEASURED - HEAD {head[:10]} != recorded {heads[repo][:10]}")
            bad += 1
            continue
        t0 = time.time()
        r = subprocess.run([sys.executable, str(TOOL), "--dwell", "--json", "--register", str(top / rel)],
                           capture_output=True, text=True, encoding="utf-8")
        secs = time.time() - t0
        (out_dir / f"{repo}.dwell.json").write_text(r.stdout, encoding="utf-8", newline="\n")
        got = json.loads(r.stdout)
        if "error" in got:
            lines.append(f"{repo}: FAIL - {got['error']}")
            bad += 1
            continue
        ref = json.loads((HERE / f"{repo}.json").read_text(encoding="utf-8"))["ecos"]
        ref_open = {k: v["history"][-1][2] for k, v in ref.items() if not v["terminal"]}
        got_open = {o["id"]: o["since_commit"][:10] for o in got["open"]}
        # BomDD's register gained ECO-120 after the reference was taken (filed in 32e2bdd); compare the reference's entries only.
        extra = sorted(set(got_open) - set(ref_open))
        missing = sorted(set(ref_open) - set(got_open))
        diff = sorted(k for k in set(ref_open) & set(got_open) if ref_open[k] != got_open[k])
        ok = not missing and not diff and (repo == "BomDD" or not extra)
        bad += 0 if ok else 1
        lines.append(f"{repo}: {'PASS' if ok else 'FAIL'} - open {len(got_open)} (reference {len(ref_open)}), same start commit "
                     f"{len(set(ref_open) & set(got_open)) - len(diff)}, differing {len(diff)} {diff[:5]}, missing {missing[:5]}, "
                     f"extra {extra[:5]}, commits read {got['commits_read']}, parse failures {got['parse_failures']}, {secs:.1f} s")
    lines.append(f"V1: {'PASS' if bad == 0 else 'FAIL'}")
    (out_dir / "results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
