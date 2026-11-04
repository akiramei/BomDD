"""ECO-119 rounds 3 and 4 - known-bad of the new arms: this tree's qualification run against an earlier validator.

A product is scaffolded by bomdd-init.py from this working tree. Its installed process-validator.py is replaced with an earlier
one, and the qualification's OQ then runs once. Expected: exactly the arms that test what that validator did not do FAIL, and every
other N23 arm PASSes. The product is removed afterwards.

- `00f3ae2` (round 2): the six round-3 arms that refuse or report FAIL: N23x, N23x4, N23u, N23y, N23z and N23z2.
  - N23x2 and N23x3, the two merges ruling B allows, PASS, because round 2 also allowed them.
  - N23z3, N23z3b, N23z4 and N23z5 PASS: round 2 judged every commit with HEAD's paths, so it had none of round 3's three defects.
  - Writes out/r3kb.txt.
- `1cd891b` (round 3): the four round-4 arms FAIL: N23z3, N23z3b (R8-3-01), N23z4 (R8-3-02) and N23z5 (R8-3-06). Writes out/r4kb.txt.
- `--letter`: this tree's validator with ruling B's test put back to 1:A's letter. N23x2 and N23x3 FAIL. Writes out/r3kb-letter.txt.

usage: python verify119_r3kb.py 00f3ae2 | 1cd891b | --letter
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
N23_COUNT = 35
EXPECT = {
    "00f3ae2": ({"N23x", "N23x4", "N23u", "N23y", "N23z", "N23z2"}, "r3kb.txt"),
    "1cd891b": ({"N23z3", "N23z3b", "N23z4", "N23z5"}, "r4kb.txt"),
    "--letter": ({"N23x2", "N23x3"}, "r3kb-letter.txt"),
}
ENV = dict(os.environ, GIT_AUTHOR_NAME="eco119-r3kb", GIT_AUTHOR_EMAIL="r3kb@bomdd.invalid",
           GIT_COMMITTER_NAME="eco119-r3kb", GIT_COMMITTER_EMAIL="r3kb@bomdd.invalid")


def _rm_readonly(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


LETTER_NEW = "        if idx_rl not in held:\n"
LETTER_OLD = "        if bd.ruled_layer_at(base) is not None and idx_rl != bd.ruled_layer_at(base):  # ECO-119 r3kb: 1:A's letter\n"


def letter_variant() -> bytes:
    """This tree's validator with ruling B's test put back to the letter of round-2 ruling 1:A (refuse when the result differs
    from the base parent's field)."""
    src = (BOMDD / "method/templates/process-core/tools/process-validator.py").read_text(encoding="utf-8")
    assert src.count(LETTER_NEW) == 1
    return src.replace(LETTER_NEW, LETTER_OLD).encode("utf-8")


def main():
    old = sys.argv[1]
    if old not in EXPECT:
        sys.exit(f"usage: one of {sorted(EXPECT)}")
    letter = old == "--letter"
    expect, out_name = EXPECT[old]
    OUT.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="eco119-r3kb-"))
    lines = ["# known-bad: this tree's qualification against "
             + ("this tree's validator with 1:A's letter in place of ruling B" if letter else f"the validator at {old}")]
    try:
        p = subprocess.run([sys.executable, str(BOMDD / "method/tools/bomdd-init.py"), "R3", "--dir", str(tmp), "--no-gui",
                            "--no-qualify"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
        assert p.returncode == 0, p.stderr
        prod = tmp / "R3"
        src = letter_variant() if letter else subprocess.run(
            ["git", "-C", str(BOMDD), "show", f"{old}:method/templates/process-core/tools/process-validator.py"],
            capture_output=True, check=True).stdout
        (prod / "bomdd/tools/process-validator.py").write_bytes(src)
        j = tmp / "r3.json"
        subprocess.run([sys.executable, str(prod / "bomdd/tools/process-qualification.py"), "--root", str(prod), "--mode", "oq",
                        "--runs", "1", "--json", str(j)], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=ENV)
        cs = [c for c in json.loads(j.read_text(encoding="utf-8"))["oq"] if c["control"].startswith("N23")]
        failed = {c["control"] for c in cs if not c["pass"]}
        for c in cs:
            lines.append(f"[{c['control']}] {'PASS' if c['pass'] else 'FAIL'} - {c['detail'][:160]}")
        ok = failed == expect and len(cs) == N23_COUNT
        lines.append(f"N23 controls {len(cs)}; FAIL {sorted(failed)}; expected FAIL {sorted(expect)}")
        lines.append(f"known-bad: {'as expected' if ok else 'NOT as expected'}")
    finally:
        shutil.rmtree(tmp, onerror=_rm_readonly)
        lines.append(f"throwaway product removed: {not tmp.exists()}")
    (OUT / out_name).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
