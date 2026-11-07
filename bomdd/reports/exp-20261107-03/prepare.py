"""EXP-20261107-03 packages (definitions.md sections 3-4).

    python prepare.py package <staging>     # <staging>/K1 K2 C1 C2, prompt-<W>.md, package-sha256.txt
    python prepare.py verify <staging>

Reads MoviePad by `git archive` only; copies BehaviorForge's files, never writes there.
"""
import hashlib
import io
import pathlib
import subprocess
import sys
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
REPOS = HERE.parents[3]
AUTHORITY = REPOS / "MoviePad"
AUTHORITY_COMMIT = "126eae9"
KIT = REPOS / "BehaviorForge"
WRITERS = {"K1": "k", "K2": "k", "C1": "c", "C2": "c"}
# BomDD management material, left out of the original (definitions section 3)
EXCLUDE_DIRS = ("bomdd/", "bomdd-kit/", ".claude/")
EXCLUDE_FILES = {"bomdd.lock", "AGENTS.md", "CLAUDE.md", "docs/golden-checklist-p1.ja.md",
                 "docs/windows-verification-p1.ja.md", "docs/windows-verification-p1-report.ja.md"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write(p, b):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)


def original():
    tar = subprocess.run(["git", "-C", str(AUTHORITY), "archive", "--format=tar", AUTHORITY_COMMIT],
                         capture_output=True, check=True).stdout
    out, left = {}, []
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        for m in t.getmembers():
            if not m.isfile():
                continue
            if m.name.startswith(EXCLUDE_DIRS) or m.name in EXCLUDE_FILES:
                left.append(m.name)
                continue
            out[m.name] = t.extractfile(m).read()
    missing = EXCLUDE_FILES - set(left)
    if missing:
        sys.exit(f"excluded files not found in the archive: {sorted(missing)}")
    return out, left


def kit_files():
    files = sorted(p for p in KIT.rglob("*") if p.is_file() and ".git" not in p.relative_to(KIT).parts)
    return {f"kit/{p.relative_to(KIT).as_posix()}": p.read_bytes() for p in files}


def package(staging):
    staging = pathlib.Path(staging)
    orig, left = original()
    kit = kit_files()
    if len(kit) != 18:
        sys.exit(f"kit has {len(kit)} files, 18 expected")
    common = (HERE / "prompts" / "common.md").read_bytes()
    base = {f"moviepad/{k}": v for k, v in orig.items()}
    base["check_examples.py"] = (HERE / "check_examples.py").read_bytes()
    lines = []
    for w, arm in WRITERS.items():
        d = staging / w
        if d.exists():
            sys.exit(f"{d} exists")
        mine = dict(base, **(kit if arm == "k" else {}))
        for rel, b in mine.items():
            write(d / rel, b)
            lines.append(f"{sha(b)}  {w}/{rel}")
        (d / "out").mkdir()
        prompt = (HERE / "prompts" / f"head-{arm}.md").read_bytes() + common
        write(staging / f"prompt-{w}.md", prompt)
        lines.append(f"{sha(prompt)}  prompt-{w}.md")
    write(staging / "package-sha256.txt", ("\n".join(lines) + "\n").encode())
    print("original files", len(orig), "left out", len(left), "; kit files", len(kit), "; hashed", len(lines))


def verify(staging):
    staging = pathlib.Path(staging)
    bad = 0
    for line in (staging / "package-sha256.txt").read_text().splitlines():
        h, rel = line.split("  ", 1)
        p = staging / rel
        if not p.is_file() or sha(p.read_bytes()) != h:
            print("CHANGED", rel)
            bad += 1
    print("verify:", "OK" if not bad else f"{bad} changed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit({"package": package, "verify": verify}[sys.argv[1]](*sys.argv[2:]) or 0)
