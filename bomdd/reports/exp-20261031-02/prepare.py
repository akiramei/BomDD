"""EXP-20261031-02 - the staging folders of stage A (definitions sections 4, 7 and 8).

  python prepare.py author <S1..S5> <out>          an author's folder
  python prepare.py audit <S1..S5> <out> <draft>   an auditor's folder: the author's inputs plus the draft under audit
  python prepare.py bind <out> <bindings.json>     the binder's folder (A2): S2-S4, the authority, the harness's extract
  python prepare.py classify <out>                 the classifiers' folder (A3): S2, S4, S5 and the four items
  python prepare.py prompt-check                   every prompt is free of the excluded words (definitions section 4)

The authority is MoviePad 126eae9 by `git archive`, without the method kit and the agent-instruction files (bomdd-kit/,
.claude/, .github/, AGENTS.md, CLAUDE.md, bomdd.lock): they are not the product, and they tell an agent to read elsewhere.
Frozen artefacts are taken from this folder's s1/ .. s5/. Writes only under <out>; prints the SHA-256 of every file written.
"""
import hashlib
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
REPOS = HERE.parents[3]
BOMDD = HERE.parents[2]
PIN = "126eae9"
DROP = ("bomdd-kit/", ".claude/", ".github/", "AGENTS.md", "CLAUDE.md", "bomdd.lock")
ART = {"S1": "10-requirements.yaml", "S2": "domain-model.json", "S3": "screens.json", "S4": "scenarios.json", "S5": "20-spec.md"}
TEMPLATE = {"S1": "10-requirements.yaml", "S5": "20-spec.md"}
TOOLS = ("check_upstream.py", "check_model.py")
EXCLUDED = re.compile(r"(?i)fps|frame.?rate|フレームレート|SetFps|書き出し設定|出力設定|export settings|output settings|"
                      r"MoviePad-Remake|repair|修正履歴|defect|欠陥|EXP-2026|experiment|実験|measure|chain|L4")
STEPS = list(ART)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def authority(out):
    tar = subprocess.run(["git", "-C", str(REPOS / "MoviePad"), "archive", "--format=tar", PIN],
                         capture_output=True, check=True).stdout
    dest = out / "authority"
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        for m in t.getmembers():
            if m.isfile() and not m.name.startswith(DROP) and m.name not in DROP:
                p = dest / m.name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(t.extractfile(m).read())


def frozen(step, out):
    src = HERE / step.lower() / ART[step]
    if not src.is_file():
        sys.exit(f"{step} is not frozen: {src}")
    shutil.copyfile(src, out / ART[step])


def hashes(out):
    n = 0
    for p in sorted(out.rglob("*")):
        if p.is_file():
            n += 1
            if not p.relative_to(out).parts[0] == "authority":
                print(sha(p), p.relative_to(out).as_posix())
    auth = hashlib.sha256()
    for p in sorted((out / "authority").rglob("*")) if (out / "authority").is_dir() else []:
        if p.is_file():
            auth.update(p.relative_to(out).as_posix().encode() + b"\0" + sha(p).encode() + b"\n")
    print(auth.hexdigest(), "authority/ (tree of path and sha256)")
    print(n, "files")


def base(step, out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=False)
    authority(out)
    for prior in STEPS[:STEPS.index(step)]:
        frozen(prior, out)
    if step in TEMPLATE:
        shutil.copyfile(BOMDD / "method" / "templates" / TEMPLATE[step], out / ("template-" + TEMPLATE[step]))
    for t in TOOLS:  # the blind pair (definitions section 12, departure 2): form checks only, no word of what is measured
        shutil.copyfile(HERE / "blind" / t, out / t)
    return out


def author(step, out):
    out = base(step, out)
    shutil.copyfile(HERE / "prompts" / f"author-{step.lower()}.md", out / "prompt.md")
    hashes(out)


def audit(step, out, draft):
    out = base(step, out)
    shutil.copyfile(draft, out / ART[step])
    shutil.copyfile(HERE / "prompts" / f"audit-{step.lower()}.md", out / "prompt.md")
    hashes(out)


def bind(out, extracted):
    """`extracted` = the bindings.json that stage 1's `harness extract` wrote from this authority (its elements and the view
    model paths they read)."""
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=False)
    authority(out)
    for s in ("S2", "S3", "S4"):
        frozen(s, out)
    text = (HERE.parent / "exp-20261030-04" / "definitions.md").read_text(encoding="utf-8")
    schema = text[text.index("## 3. Scenario schema"):text.index("## 5. The mock")]
    (out / "harness-schema.md").write_text(schema, encoding="utf-8", newline="\n")
    shutil.copyfile(extracted, out / "authority-bindings.json")
    shutil.copyfile(HERE / "prompts" / "binder.md", out / "prompt.md")
    hashes(out)


def classify(out):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=False)
    for s in ("S2", "S4", "S5"):
        frozen(s, out)
    items = json.loads((HERE.parent / "exp-20261031-01" / "items.json").read_text(encoding="utf-8"))["items"]
    keep = [{k: i[k] for k in ("id", "file", "before", "after")} for i in items if i["input"] == "in"]
    (out / "items.json").write_text(json.dumps({"items": keep}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                    newline="\n")
    shutil.copyfile(HERE / "prompts" / "classifier.md", out / "prompt.md")
    hashes(out)


def prompt_check():
    """Section 4: author and auditor prompts must not name the excluded words. The binder and the classifiers are told what
    they bind or place, so only the experiment's own words are excluded from theirs."""
    ok = True
    narrow = re.compile(r"(?i)MoviePad-Remake|EXP-2026|experiment|実験|measure|chain|L4|SetFps")
    for p in sorted((HERE / "prompts").glob("*.md")):
        rule = narrow if p.name in ("binder.md", "classifier.md") else EXCLUDED
        hits = sorted({m.group(0) for m in rule.finditer(p.read_text(encoding="utf-8"))})
        ok &= not hits
        print("PASS" if not hits else "FAIL", p.name, hits if hits else "")
    for t in TOOLS:  # departure 2: the tools in an author's or auditor's folder are held to the same rule as its prompt
        hits = sorted({m.group(0) for m in EXCLUDED.finditer((HERE / "blind" / t).read_text(encoding="utf-8"))})
        full = sorted({m.group(0) for m in EXCLUDED.finditer((HERE / t).read_text(encoding="utf-8"))})
        ok &= not hits and bool(full)
        print("PASS" if not hits else "FAIL", "blind/" + t, hits if hits else "",
              "(positive control: the full tool names", full, ")" if full else "FAIL: positive control matched nothing")
    return 0 if ok else 1


if __name__ == "__main__":
    cmd, a = sys.argv[1], sys.argv[2:]
    if cmd == "author":
        author(a[0], a[1])
    elif cmd == "audit":
        audit(a[0], a[1], a[2])
    elif cmd == "bind":
        bind(a[0], a[1])
    elif cmd == "classify":
        classify(a[0])
    elif cmd == "prompt-check":
        sys.exit(prompt_check())
    else:
        sys.exit(f"unknown command {cmd}")
