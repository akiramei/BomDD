"""EXP-20261107-02 freeze and scorer package: EXP-20261107-01's freeze.py with this folder as the target and B1 / B2.

    python freeze.py freeze <staging> <W>
    python freeze.py scorer <staging> <seed>     # <staging>/scorer-02/{W1, W2, sources, prompt.md}; key scorer-key-02.json
"""
import importlib.util
import json
import pathlib
import random
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("frz01", HERE.parent / "exp-20261107-01" / "freeze.py")
f1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f1)
f1.HERE = HERE  # freeze() writes run-<W>/ under this folder


def scorer(staging, seed):
    staging = pathlib.Path(staging)
    order = ["B1", "B2"]
    random.Random(int(seed)).shuffle(order)
    key = dict(zip(["W1", "W2"], order))
    d = staging / "scorer-02"
    if d.exists():
        sys.exit(f"{d} exists")
    for lab, w in key.items():
        run = HERE / f"run-{w}"
        for rel, meta in json.loads((run / "freeze.json").read_text(encoding="utf-8"))["files"].items():
            b = (run / rel).read_bytes()
            if f1.sha(b) != meta["sha256"]:
                sys.exit(f"{w}/{rel} changed since the freeze")
            t = d / lab / rel
            t.parent.mkdir(parents=True, exist_ok=True)
            t.write_bytes(b)
    shutil.copytree(staging / "B1" / "sources", d / "sources")
    prompt = (HERE.parent / "exp-20261107-01" / "prompts" / "scorer.md").read_text(encoding="utf-8")
    prompt = prompt.replace("4 人の書き手", "2 人の書き手").replace("`W1/`〜`W4/`", "`W1/`・`W2/`") \
        .replace('"W2": ..., "W3": ..., "W4": ...}', '"W2": ...}').replace("4 つの設計文書", "2 つの設計文書")
    (d / "prompt.md").write_text(prompt, encoding="utf-8", newline="\n")
    kb = (json.dumps(key, indent=1) + "\n").encode()
    (staging / "scorer-key-02.json").write_bytes(kb)
    print("scorer package ready; key sha256", f1.sha(kb))


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    {"freeze": f1.freeze, "scorer": scorer}[cmd](*args)
