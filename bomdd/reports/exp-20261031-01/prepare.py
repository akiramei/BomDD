"""EXP-20261031-01 - packages for the derivers (part 1) and the writers (part 2), and the precondition check (definitions 4, 7, 8).

  python prepare.py derive <out>                    the deriver's folder: requirements and spec at the pin, check_model.py, prompt
  python prepare.py write <out> <domain-model.json> the writer's folder: EXP-20261030-05's package plus the domain model and prompt
  python prepare.py classify <out> <model-A> <model-B> the classifiers' folder: both models, the input items, the pinned texts
  python prepare.py prompt-diff                     the part 2 prompt differs from EXP-20261030-05's by the one added line only

Reads MoviePad-Remake by `git show` only. Writes only under <out>.
"""
import difflib
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPOS = HERE.parents[3]
EXP05 = HERE.parent / "exp-20261030-05"
PIN = "22e2213"  # MoviePad-Remake: G2 passed; before the E-BOM (6e81322) and any manufacture
SOURCES = [("bomdd/10-requirements.yaml", "10-requirements.yaml"), ("bomdd/20-spec.md", "20-spec.md")]
ADDED = "  - `domain-model.json` — MoviePad の中核(編集と書き出し)のドメインモデル(実体・属性・初期値・属性を変える操作・関係)"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hashes(out):
    for p in sorted(out.iterdir()):
        if p.is_file():
            print(sha(p), p.name)


def derive(out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=False)
    for path, name in SOURCES:
        data = subprocess.run(["git", "-C", str(REPOS / "MoviePad-Remake"), "show", f"{PIN}:{path}"],
                              capture_output=True, check=True).stdout
        (out / name).write_bytes(data)
    shutil.copy(HERE / "check_model.py", out / "check_model.py")
    shutil.copy(HERE / "deriver" / "prompt.md", out / "prompt.md")
    hashes(out)


def prompt_diff():
    old = (EXP05 / "writer" / "prompt.md").read_text(encoding="utf-8").splitlines()
    new = (HERE / "writer" / "prompt.md").read_text(encoding="utf-8").splitlines()
    changed = [l for l in difflib.ndiff(old, new) if l[:2] in ("- ", "+ ")]
    ok = changed == ["+ " + ADDED]
    print("PASS" if ok else "FAIL", "part 2 prompt = EXP-20261030-05's + one line", changed if not ok else "")
    return 0 if ok else 1


def write(out, model):
    if prompt_diff():
        return 1
    out = pathlib.Path(out)
    subprocess.run([sys.executable, str(EXP05 / "prepare.py"), "package", str(out)], check=True)
    shutil.copy(model, out / "domain-model.json")
    shutil.copy(HERE / "writer" / "prompt.md", out / "prompt.md")
    shutil.copy(EXP05 / "check_schema.py", out / "check_schema.py")
    hashes(out)
    return 0


def classify(out, model_a, model_b):
    out = pathlib.Path(out)
    derive(out / "_pin")
    for name in ("10-requirements.yaml", "20-spec.md"):
        shutil.move(str(out / "_pin" / name), out / name)
    shutil.rmtree(out / "_pin")
    items = json.loads((HERE / "items.json").read_text(encoding="utf-8"))["items"]
    keep = [{k: i[k] for k in ("id", "file", "before", "after")} for i in items if i["input"] == "in"]
    (out / "items.json").write_text(json.dumps({"items": keep}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                    newline="\n")
    shutil.copy(model_a, out / "model-A.json")
    shutil.copy(model_b, out / "model-B.json")
    shutil.copy(HERE / "classifier" / "prompt.md", out / "prompt.md")
    hashes(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    sys.exit(derive(sys.argv[2]) if cmd == "derive" else write(sys.argv[2], sys.argv[3]) if cmd == "write"
             else classify(sys.argv[2], sys.argv[3], sys.argv[4]) if cmd == "classify" else prompt_diff())
