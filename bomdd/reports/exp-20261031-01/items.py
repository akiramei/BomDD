"""EXP-20261031-01 - the defect items: every hunk by which a repair after the pin changed the ruled layer (definitions section 3).

Reads MoviePad-Remake by `git diff` only. Writes items.json next to this file.
"""
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3] / "MoviePad-Remake"

# (commit, path, why it is a repair) - the ruled-layer changes between the pin and a2ca41e that their commits call repairs
REPAIRS = [
    ("bbce170", "bomdd/20-spec.md", "G3 round 1 (sixteen findings repaired from the authority)"),
    ("0522643", "bomdd/31-kbom.yaml", "G3 round 2 (friction and minor points repaired from the authority)"),
    ("b06a5bf", "bomdd/20-spec.md", "ECO-003 (a package contradiction the factory blocked on)"),
    ("ec6e549", "bomdd/31-kbom.yaml", "ECO-003 (the K-BOM line b06a5bf meant to correct)"),
]
# Ruled-layer changes in the same window that are not repairs (definitions section 3.2), listed so the window is closed
NOT_REPAIRS = {
    "6e81322": "the E-BOM's first text (its creation, not a change to an earlier statement)",
    "255e6de": "the K-BOM's first text (its creation; the K-BOM items below have this as their before)",
    "24cc6ed": "10-requirements.yaml's authority local_path replaced by an environment variable name; no statement changed",
    "0b50020": "Control Plan row references only (the CP-EXPORT-001 split); no ruled statement changed",
    "31273e7": "ECO-005, the user's re-ruled E-BOM boundary (EXP-20261030-01: feature, both classifiers)",
}
WINDOW = ("22e2213", "a2ca41e")
RULED = ["bomdd/10-requirements.yaml", "bomdd/20-spec.md", "bomdd/30-ebom.yaml", "bomdd/31-kbom.yaml"]


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, check=True, text=True,
                          encoding="utf-8").stdout


def hunks(commit, path):
    text = git("diff", "-U3", f"{commit}~1", commit, "--", path)
    out = []
    for block in re.split(r"(?m)^(?=@@ )", text)[1:]:
        head, _, body = block.partition("\n")
        lines = body.splitlines()
        out.append({"hunk": head.split("@@")[1].strip(),
                    "before": "\n".join(l[1:] for l in lines if l.startswith("-")),
                    "after": "\n".join(l[1:] for l in lines if l.startswith("+"))})
    return out


def main():
    # the window is closed: every commit touching a ruled file in it is a repair or a listed non-repair
    touched = git("log", "--format=%h", f"{WINDOW[0]}..{WINDOW[1]}", "--", *RULED).split()
    known = {c for c, _, _ in REPAIRS} | set(NOT_REPAIRS)
    unknown = [c for c in touched if c[:7] not in known]
    if unknown:
        print("ERROR commits in the window not placed:", unknown)
        return 1
    items = []
    for commit, path, why in REPAIRS:
        for h in hunks(commit, path):
            items.append({"id": f"D{len(items) + 1:02d}", "commit": commit, "file": path, "why": why, **h,
                          "input": "in" if path in ("bomdd/10-requirements.yaml", "bomdd/20-spec.md") else "out"})
    # an input item's before-text must stand in the pinned file (OBS-20261030-04: the defect is in the input before the run)
    for i in items:
        pinned = git("show", f"{WINDOW[0]}:{i['file']}") if i["input"] == "in" else None
        if pinned is not None and any(l.strip() and l not in pinned for l in i["before"].splitlines()):
            print("ERROR", i["id"], "before-text not in the pin")
            return 1
    (HERE / "items.json").write_text(json.dumps({"window": WINDOW, "not_repairs": NOT_REPAIRS, "items": items},
                                                ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    for i in items:
        print(i["id"], i["commit"], i["file"], i["input"], i["hunk"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
