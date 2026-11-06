"""EXP-20261107-02 packages (definitions.md section 3): two bare-control writers B1 and B2, built with EXP-20261107-01's
prepare.py (same sources, CAD and start screen) and this folder's prompt and checker.

    python prepare.py package <staging>     # <staging>/B1, B2, prompt-B1.md, prompt-B2.md, package-sha256-02.txt
    python prepare.py verify <staging>
"""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("prep01", HERE.parent / "exp-20261107-01" / "prepare.py")
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)
WRITERS = ["B1", "B2"]


def package(staging):
    staging = pathlib.Path(staging)
    start = staging / "start-screen.json"
    actions = p1.ACTIONS.read_bytes()
    if p1.sha(actions) != p1.ACTIONS_SHA:
        sys.exit("actions.json changed")
    observations = (p1.json.dumps([{"name": n, "meaning": m} for n, (_, m) in p1.OBSERVATIONS.items()],
                                  ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    files = {
        "sources/README.md": p1.git_show(p1.AUTHORITY, p1.AUTHORITY_COMMIT, "README.md"),
        "sources/README.ja.md": p1.git_show(p1.AUTHORITY, p1.AUTHORITY_COMMIT, "README.ja.md"),
        "sources/10-requirements.yaml": p1.git_show(p1.REMAKE, p1.REMAKE_COMMIT, "bomdd/10-requirements.yaml"),
        "cad/actions.json": actions,
        "cad/observations.json": observations,
        "cad/start-screen.json": start.read_bytes(),
        "check_examples.py": (HERE / "check_examples.py").read_bytes(),
    }
    prompt = (HERE.parent / "exp-20261107-01" / "prompts" / "head-c.md").read_bytes() + \
        (HERE / "prompts" / "common-bare.md").read_bytes()
    lines = []
    for w in WRITERS:
        d = staging / w
        if d.exists():
            sys.exit(f"{d} exists")
        for rel, b in files.items():
            p1.write(d / rel, b)
            lines.append(f"{p1.sha(b)}  {w}/{rel}")
        (d / "out").mkdir()
        p1.write(staging / f"prompt-{w}.md", prompt)
        lines.append(f"{p1.sha(prompt)}  prompt-{w}.md")
    p1.write(staging / "package-sha256-02.txt", ("\n".join(lines) + "\n").encode())
    print("packaged", len(WRITERS), "writers,", len(lines), "hashed files")


def verify(staging):
    staging = pathlib.Path(staging)
    bad = 0
    for line in (staging / "package-sha256-02.txt").read_text().splitlines():
        h, rel = line.split("  ", 1)
        p = staging / rel
        if not p.is_file() or p1.sha(p.read_bytes()) != h:
            print("CHANGED", rel)
            bad += 1
    print("verify:", "OK" if not bad else f"{bad} changed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit({"package": package, "verify": verify}[sys.argv[1]](*sys.argv[2:]) or 0)
