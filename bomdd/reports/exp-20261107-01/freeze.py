"""EXP-20261107-01 freeze and scorer package (definitions.md sections 7 and 10).

    python freeze.py freeze <staging> <W>            # copy <staging>/<W>/examples.json and out/ into run-<W>/ with freeze.json
    python freeze.py scorer <staging> <seed>          # <staging>/scorer/{W1..W4, sources, prompt.md}; key to <staging>/scorer-key.json
    python freeze.py open-key <staging>               # print the key (after the scorer has written scores.json)
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
    for p in sorted([src / "examples.json"] + [p for p in (src / "out").rglob("*") if p.is_file()]):
        if not p.is_file():
            print("missing", p)
            continue
        rel = p.relative_to(src).as_posix()
        b = p.read_bytes()
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / rel).write_bytes(b)
        files[rel] = {"sha256": sha(b), "bytes": len(b)}
    (dest / "freeze.json").write_text(json.dumps({"writer": w, "files": files}, indent=1) + "\n", encoding="utf-8",
                                      newline="\n")
    print(w, len(files), "files frozen")


def scorer(staging, seed):
    staging = pathlib.Path(staging)
    labels = ["W1", "W2", "W3", "W4"]
    order = WRITERS[:]
    random.Random(int(seed)).shuffle(order)
    key = dict(zip(labels, order))
    d = staging / "scorer"
    if d.exists():
        sys.exit(f"{d} exists")
    for lab, w in key.items():
        run = HERE / f"run-{w}"
        frozen = json.loads((run / "freeze.json").read_text(encoding="utf-8"))["files"]
        for rel, meta in frozen.items():  # only the frozen files (departure D2: not the run's results)
            b = (run / rel).read_bytes()
            if sha(b) != meta["sha256"]:
                sys.exit(f"{w}/{rel} changed since the freeze")
            t = d / lab / rel
            t.parent.mkdir(parents=True, exist_ok=True)
            t.write_bytes(b)
    shutil.copytree(staging / "K1" / "sources", d / "sources")
    (d / "prompt.md").write_bytes((HERE / "prompts" / "scorer.md").read_bytes())
    kb = (json.dumps(key, indent=1) + "\n").encode()
    (staging / "scorer-key.json").write_bytes(kb)
    print("scorer package ready; key sha256", sha(kb))


def open_key(staging):
    print((pathlib.Path(staging) / "scorer-key.json").read_text())


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    {"freeze": freeze, "scorer": scorer, "open-key": open_key}[cmd](*args)
