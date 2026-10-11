"""Working-tree-only perturbations of the clone (the index is never touched).

usage: python perturb.py REPO {a|b|c|d} {apply|restore}
  a  untracked test-results/zz-probe/note.md holding ECO-VT-175's machinery-claim sentence
  b  delete the review evidence file ECO-VT-006 cites (tracked; deletion left unstaged)
  c  in the WORKING-TREE register only, rename ECO-VT-007's `change_class:` key
  d  rewrite the WORKING-TREE copy of the staged register with CRLF (content otherwise identical)
"""
import shutil
import subprocess
import sys
from pathlib import Path

root, case, action = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
REG = root / "bomdd/process/change-register.yaml"
SAVE = root.parent / f"saved-register-{case}.yaml"


def git(*a):
    subprocess.run(["git", *a], cwd=root, check=True)


if case == "a":
    d = root / "test-results/zz-probe"
    if action == "apply":
        d.mkdir(parents=True, exist_ok=True)
        (d / "note.md").write_text("A note: the caller never reads returncode.\n", encoding="utf-8")
    else:
        shutil.rmtree(d)
elif case == "b":
    p = "bomdd/eco/ECO-VT-006-independent-review-post-vector.md"
    if action == "apply":
        (root / p).unlink()
    else:
        git("checkout", "--", p)
elif case in ("c", "d"):
    if action == "apply":
        data = REG.read_bytes()
        SAVE.write_bytes(data)
        if case == "c":
            marker = b"  - id: ECO-VT-007\n"
            start = data.index(marker)
            pos = data.index(b"    change_class:", start)
            data = data[:pos] + b"    change_klass:" + data[pos + len(b"    change_class:"):]
        else:
            data = data.replace(b"\n", b"\r\n")
        REG.write_bytes(data)
    else:
        REG.write_bytes(SAVE.read_bytes())
        SAVE.unlink()
print(case, action, "done; git status:")
print(subprocess.run(["git", "status", "--short", "-uall"], cwd=root, capture_output=True,
                     text=True).stdout)
