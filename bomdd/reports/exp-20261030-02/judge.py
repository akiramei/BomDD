"""EXP-20261030-02 - prepare the judge's input and tally its verdicts (definitions.md sections 5-7).

Usage:
  python judge.py prepare <staging-dir> <stage> <Pnn> [<Pnn> ...]
      copies each <staging-dir>/<Pnn>/report.md to reports/<Pnn>.md (a missing or empty report is a no-report, listed),
      relabels the present ones R01... in a shuffled order (judge-map-stage<stage>.json, written before judging), and
      writes judge-input-stage<stage>.md: per R label the item's hit criterion and the report text only.
  python judge.py tally <stage>
      reads verdicts-stage<stage>.json ({"R01": {"verdict": "hit|partial|miss", "quote": "..."}, ...}), maps it back
      through the map and prints one line per package plus the no-reports. Refuses (exit 2) a missing or unknown verdict.
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORTS = HERE / "reports"

# definitions.md section 2, verbatim in meaning (English)
CRITERIA = {
    "D1": "The report names that batch tag assignment has no way to REMOVE (unassign) a tag, OR that there is no surface where "
          "the tag / value is chosen and the assigned / mixed state is shown, behind the assign action.",
    "D2": "The report names that the batch tag action is NOT AVAILABLE IN ORDINARY BROWSING although selection is offered there "
          "(it is available only in the hierarchy layout).",
    "D3": "The report names that there is NO OPERATION TO CREATE (AND NAME) A MANUAL COLLECTION.",
    "D4": "The report names that the requirement's PRE-MERGE PREVIEW OF THE MERGED TAGS and the \"FILES ARE NOT DELETED\" NOTICE "
          "are absent from the organize (merge) tray, or that the requirements text and the tray disagree on them.",
    "D5": "The report names that the CAD text cites a DOCKED TAG-ASSIGN OPERATION / AREA that the mock does not have, or that "
          "this contradicts the immediate row-click assignment.",
    "D6": "The report names that RELINK IS ASSIGNED TO TWO OWNERS - the text hands relink to the repair flow while the review "
          "mock performs relink itself.",
}

VERDICTS = {"hit", "partial", "miss"}


def manifest():
    return json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["packages"]


def prepare(staging, stage, pkgs):
    packages = manifest()
    REPORTS.mkdir(exist_ok=True)
    present, missing = [], []
    for pkg in pkgs:
        src = Path(staging) / pkg / "report.md"
        if src.is_file() and src.stat().st_size > 0:
            (REPORTS / f"{pkg}.md").write_bytes(src.read_bytes())
            present.append(pkg)
        else:
            missing.append(pkg)
    order = present[:]
    random.SystemRandom().shuffle(order)
    labels = {f"R{n:02d}": pkg for n, pkg in enumerate(order, 1)}
    (HERE / f"judge-map-stage{stage}.json").write_text(
        json.dumps({"labels": labels, "no_report": missing}, indent=1) + "\n", encoding="utf-8", newline="\n")
    out = ["# Judge input\n",
           "For each report below: read the criterion, then the report. Verdict = **hit** (the report names that thing at that "
           "granularity), **partial** (it names the area or asks the question without naming the thing), **miss** (neither). "
           "Judge each report on its own; the reports are independent and unrelated to each other's verdicts.\n"]
    for label, pkg in labels.items():
        item = packages[pkg]["item"]
        text = (REPORTS / f"{pkg}.md").read_text(encoding="utf-8")
        out.append(f"\n\n=== {label} ===\n\nCRITERION: {CRITERIA[item]}\n\nREPORT:\n\n{text}\n")
    (HERE / f"judge-input-stage{stage}.md").write_text("".join(out), encoding="utf-8", newline="\n")
    sys.stdout.write(f"present={len(present)} no_report={missing} labels={len(labels)}\n")


def tally(stage):
    packages = manifest()
    m = json.loads((HERE / f"judge-map-stage{stage}.json").read_text(encoding="utf-8"))
    v = json.loads((HERE / f"verdicts-stage{stage}.json").read_text(encoding="utf-8"))
    rows = []
    for label, pkg in m["labels"].items():
        verdict = v.get(label, {}).get("verdict")
        if verdict not in VERDICTS:
            sys.stderr.write(f"UNMEASURABLE: {label} ({pkg}) verdict={verdict!r}\n")
            sys.exit(2)
        p = packages[pkg]
        rows.append((pkg, p["item"], p["state"], p["arm"], label, verdict))
    for pkg in m["no_report"]:
        p = packages[pkg]
        rows.append((pkg, p["item"], p["state"], p["arm"], "-", "no-report(miss)"))
    for r in sorted(rows):
        sys.stdout.write(" ".join(r) + "\n")


if __name__ == "__main__":
    if sys.argv[1] == "prepare":
        prepare(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif sys.argv[1] == "tally":
        tally(sys.argv[2])
    else:
        sys.exit(2)
