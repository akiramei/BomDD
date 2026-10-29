"""ECO-119 V2 and V3 - the qualification's E13 arms (V2) and nothing else moving (V3).

A product is scaffolded by bomdd-init.py from this working tree (after) and from a clone of the commit before manufacture
(before); the qualification runs on each (--mode full --runs 2, as self-conformance's C11). V2: the N23 controls of "after",
each with its verdict line. V3: every control present in both runs has the same verdict and detail; the controls only in "after"
are listed; "before" has no E13 control. Writes <this folder>/out/v2.txt and v3.txt; temporary folders removed.

usage: python verify119_v2v3.py <commit before manufacture>
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
BOMDD = HERE.parents[2]
OUT = HERE / "out"
ENV = dict(os.environ, GIT_AUTHOR_NAME="eco119-v2", GIT_AUTHOR_EMAIL="v2@bomdd.invalid",
           GIT_COMMITTER_NAME="eco119-v2", GIT_COMMITTER_EMAIL="v2@bomdd.invalid")


def _rm_readonly(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def qualify(method_root: Path, tmp: Path, name: str) -> dict:
    p = subprocess.run([sys.executable, str(method_root / "method/tools/bomdd-init.py"), name, "--dir", str(tmp), "--no-gui",
                        "--no-qualify"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    assert p.returncode == 0, p.stderr
    prod = tmp / name
    j = tmp / f"{name}.json"
    subprocess.run([sys.executable, str(prod / "bomdd/tools/process-qualification.py"), "--root", str(prod), "--json", str(j)],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV, timeout=1500)
    return json.loads(j.read_text(encoding="utf-8"))


def main():
    before_rev = sys.argv[1]
    OUT.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="eco119-v2v3-"))
    try:
        clone = tmp / "before-src"
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(BOMDD), str(clone)], check=True)
        subprocess.run(["git", "-C", str(clone), "checkout", "-q", before_rev], check=True)
        after = qualify(BOMDD, tmp, "After")
        before = qualify(clone, tmp, "Before")
        ctl = lambda r: {c["control"]: c for c in r["iq"] + r["oq"]}
        a, b = ctl(after), ctl(before)
        n23 = [c for k, c in a.items() if k.startswith("N23")]
        v2 = ["# V2 - the qualification's E13 arms (a fresh scaffold of this tree; --runs 2)",
              f"disposition {after['disposition']}, runs identical {after['runs_identical']}, controls {len(a)}"]
        v2 += [f"[{c['control']}] {'PASS' if c['pass'] else 'FAIL'} {c['expected']} - {c['detail']}" for c in n23]
        ok2 = after["disposition"] == "PASS" and after["runs_identical"] is True and len(n23) == 15 and all(c["pass"] for c in n23)
        v2.append(f"V2: {'PASS' if ok2 else 'FAIL'} ({len(n23)} N23 controls)")
        common = sorted(set(a) & set(b))
        diff = [k for k in common if (a[k]["pass"], a[k]["detail"]) != (b[k]["pass"], b[k]["detail"])]
        only_after = sorted(set(a) - set(b))
        only_before = sorted(set(b) - set(a))
        v3 = ["# V3 - nothing else moves (before = a scaffold of " + before_rev + ", after = this tree)",
              f"before: disposition {before['disposition']}, controls {len(b)}; after: disposition {after['disposition']}, controls {len(a)}",
              f"controls in both: {len(common)}; verdict or detail different: {diff or 'none'}",
              f"only after: {only_after}", f"only before: {only_before or 'none'}",
              f"E13 in before's output: {any('E13' in json.dumps(c, ensure_ascii=False) for c in b.values())}"]
        ok3 = (before["disposition"] == "PASS" and not diff and not only_before
               and all(k.startswith("N23") for k in only_after) and not any("E13" in json.dumps(c, ensure_ascii=False) for c in b.values()))
        v3.append(f"V3: {'PASS' if ok3 else 'FAIL'}")
        (OUT / "v2.txt").write_text("\n".join(v2) + "\n", encoding="utf-8", newline="\n")
        (OUT / "v3.txt").write_text("\n".join(v3) + "\n", encoding="utf-8", newline="\n")
        print("\n".join(v2 + [""] + v3))
    finally:
        shutil.rmtree(tmp, onerror=_rm_readonly)
        print(f"temporary folders removed: {not tmp.exists()}")


if __name__ == "__main__":
    main()
