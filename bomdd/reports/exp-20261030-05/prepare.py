"""The writer's vocabulary for stage 2 (definitions.md section 3), from EXP-20261030-04's frozen run.

    python prepare.py check                 # apply the name rule to the mock's states; exit 1 unless the names are unique
    python prepare.py package <out-dir>     # states.json, actions.json and the requirement sources for the writer
States: the 27 that have a section in exp-04's clean mock, named by exp-04's names with the availability terms removed and
the undo / redo terms said as history. Actions: id, surface, label per element of exp-04's bindings.json (no conditions).
"""
import collections
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
EXP04 = HERE.parent / "exp-20261030-04"
DROP = {"分割可", "結合可", "In 可", "Out 可"}
AS_HISTORY = {"取り消し可": "直前の編集あり", "やり直し可": "取り消した編集あり"}
SOURCES = [  # (repository folder, commit, path, file name for the writer)
    ("MoviePad", "126eae9", "README.md", "README.md"),
    ("MoviePad", "126eae9", "README.ja.md", "README.ja.md"),
    ("MoviePad-Remake", "a2ca41e", "bomdd/10-requirements.yaml", "10-requirements.yaml"),
]


def rename(name):
    head, sep, tail = name.partition("): ")
    if not sep:
        return name
    terms = [AS_HISTORY.get(t, t) for t in tail.split("・") if t not in DROP]
    return head + ")" + (": " + "・".join(terms) if terms else "")


def states():
    frozen = json.loads((EXP04 / "run" / "scenarios-frozen.json").read_text(encoding="utf-8"))
    sections = set(re.findall(r'data-ui-state="([^"]+)"', (EXP04 / "run" / "mock.html").read_text(encoding="utf-8")))
    return [{"id": s["id"], "name": rename(s["name"])} for s in frozen["states"] if s["id"] in sections]


def actions():
    b = json.loads((EXP04 / "bindings.json").read_text(encoding="utf-8"))
    seen, out = set(), []
    for e in b["Elements"]:
        key = (e["Id"], e["Surface"], e["Label"])
        if key not in seen:
            seen.add(key)
            out.append({"id": e["Id"], "surface": e["Surface"], "label": e["Label"]})
    return out


def check():
    st = states()
    dup = [n for n, c in collections.Counter(s["name"] for s in st).items() if c > 1]
    print(f"states {len(st)} unique names {len(st) - sum(collections.Counter(s['name'] for s in st)[d] - 1 for d in dup)}")
    for d in dup:
        print("  duplicate:", d)
    return 1 if dup else 0


def package(out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "states.json").write_text(json.dumps(states(), ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    (out / "actions.json").write_text(json.dumps(actions(), ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    repos = HERE.parents[3]
    for repo, commit, path, name in SOURCES:
        data = subprocess.run(["git", "-C", str(repos / repo), "show", f"{commit}:{path}"], capture_output=True, check=True).stdout
        (out / name).write_bytes(data)
    print("packaged", sorted(p.name for p in out.iterdir()))


if __name__ == "__main__":
    sys.exit(check() if sys.argv[1] == "check" else package(sys.argv[2]))
