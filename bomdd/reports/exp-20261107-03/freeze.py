"""EXP-20261107-03 freeze and scorer package (definitions.md sections 6 and 10).

    python freeze.py freeze <staging> <W>       # copy <staging>/<W>/examples.json and out/ into run-<W>/ with freeze.json
    python freeze.py scorer <staging> <seed>     # <staging>/scorer/{W1..W4, moviepad, targets.md, prompt.md}; key to <staging>/scorer-key.json
"""
import hashlib
import json
import pathlib
import random
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
WRITERS = ["K1", "K2", "C1", "C2"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def freeze(staging, w):
    src = pathlib.Path(staging) / w
    dest = HERE / f"run-{w}"
    if dest.exists():
        sys.exit(f"{dest} exists")
    files = {}
    cands = [src / "examples.json"] + sorted(p for p in (src / "out").rglob("*") if p.is_file())
    for p in cands:
        if not p.is_file():
            print("missing", p)
            continue
        rel = p.relative_to(src).as_posix()
        b = p.read_bytes()
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / rel).write_bytes(b)
        files[rel] = {"sha256": sha(b), "bytes": len(b)}
    extra = sorted(p.relative_to(src).as_posix() for p in src.rglob("*") if p.is_file()
                   and not p.relative_to(src).as_posix().startswith(("moviepad/", "kit/", "out/"))
                   and p.name not in ("examples.json", "check_examples.py"))
    (dest / "freeze.json").write_text(json.dumps({"writer": w, "files": files, "other_files_in_folder": extra}, indent=1)
                                      + "\n", encoding="utf-8", newline="\n")
    print(w, len(files), "files frozen; other files in the folder:", extra)


def scorer(staging, seed):
    staging = pathlib.Path(staging)
    order = WRITERS[:]
    random.Random(int(seed)).shuffle(order)
    key = dict(zip(["W1", "W2", "W3", "W4"], order))
    d = staging / "scorer"
    if d.exists():
        sys.exit(f"{d} exists")
    for lab, w in key.items():
        run = HERE / f"run-{w}"
        for rel, meta in json.loads((run / "freeze.json").read_text(encoding="utf-8"))["files"].items():
            b = (run / rel).read_bytes()
            if sha(b) != meta["sha256"]:
                sys.exit(f"{w}/{rel} changed since the freeze")
            t = d / lab / rel
            t.parent.mkdir(parents=True, exist_ok=True)
            t.write_bytes(b)
    shutil.copytree(staging / "C1" / "moviepad", d / "moviepad")
    (d / "targets.md").write_bytes((HERE / "targets.md").read_bytes())
    (d / "prompt.md").write_bytes((HERE / "prompts" / "scorer.md").read_bytes())
    kb = (json.dumps(key, indent=1) + "\n").encode()
    (staging / "scorer-key.json").write_bytes(kb)
    print("scorer package ready; key sha256", sha(kb))


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    {"freeze": freeze, "scorer": scorer}[cmd](*args)
