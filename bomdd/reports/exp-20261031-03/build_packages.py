"""EXP-20261031-03 step 3 (definitions section 4.3): build the transcribers' folders. Each holds exactly the package.

    python build_packages.py <staging>     # writes <staging>/t1 and <staging>/t2 and prints their hashes as JSON
"""
import hashlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
S02 = HERE.parent / "exp-20261031-02"
PACKAGE = {"prompt.md": HERE / "transcriber" / "prompt.md", "form.md": HERE / "form.md",
           "form_check.py": HERE / "form_check.py", "rule.md": HERE / "transcriber" / "rule.md",
           "slots.json": HERE / "transcriber" / "slots.json", "s2/domain-model.json": S02 / "s2" / "domain-model.json",
           "s3/screens.json": S02 / "s3" / "screens.json"}


def main():
    staging = pathlib.Path(sys.argv[1]).resolve()
    out = {}
    for t in ("t1", "t2"):
        d = staging / t
        d.mkdir(parents=True, exist_ok=False)
        for rel, src in PACKAGE.items():
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, d / rel)
        out[t] = {rel: hashlib.sha256((d / rel).read_bytes()).hexdigest()
                  for rel in sorted(str(p.relative_to(d)).replace("\\", "/") for p in d.rglob("*") if p.is_file())}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
