#!/usr/bin/env python3
"""ECO-116 manufacture, ViewPrism2 ECO-148 §4: compare ViewPrism2's receiving instrument with BomDD's verified rehearsal (ECO-115, ef1506a).
Read only. The product does not import this; this script imports both.

  python -B viewprism2-compare.py <ViewPrism2 checkout> [<As-Built entry id to compare>] [<output file>]

A. D1/D2/D4 on synthetic cases: the tool's decide against rehearse_decision_v2.decide (library mode: no freeze checks), per row category,
   D1 number, route, result, and the overall result.
B. D5: every arm of rehearse_sequence.py (ARMS + the MoviePad real arms + BOUND_ARMS) through the tool's read_sequence: convergence, control,
   the signal set, the candidate, the measured-hold count.
C. The real entry (when an id is given): the reference's decide (with git) on the entry's frozen BOM, work order and committed evidence,
   against the entry's recorded advance_decision.
Exit 1 when any comparison differs.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "eco-115-advance-decision"))
import rehearse_decision_v2 as ref  # noqa: E402
import rehearse_sequence as refseq  # noqa: E402

vp = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("vp_rd", vp / "bomdd/receive_delivery.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
lines, bad = [], 0


def note(ok, text):
    global bad
    bad += not ok
    lines.append(("SAME " if ok else "DIFF ") + text)


# ---------------------------------------------------------------- A
P = [("t1", "Pass", ["CP-A"], None), ("t2", "Pass", ["CP-B"], None), ("t3", "Pass", ["CP-X"], None)]
C1, T1 = "a" * 40, "b" * 40
CASES = [
    ("all pass", P, (C1, T1), None),
    ("stamp absent", P, None, None),
    ("stamp names another commit", P, ("c" * 40, T1), None),
    ("a failure on CP-A", P[1:] + [("t1", "Fail", ["CP-A"], None)], (C1, T1), None),
    ("a failure on two rows", P + [("t8", "Fail", ["CP-A", "CP-B"], None)], (C1, T1), None),
    ("an ownerless failure (no trait)", P + [("t7", "Fail", [], None)], (C1, T1), None),
    ("an ownerless failure (a human-only row)", P + [("t6", "Fail", ["CP-H"], None)], (C1, T1), None),
    ("only skipped on CP-A", [("t1", "Skip", ["CP-A"], None)] + P[1:], (C1, T1), None),
    ("no test on CP-A", P[1:], (C1, T1), None),
    ("an outcome word outside outcomes", P + [("t5", "Weird", ["CP-A"], None)], (C1, T1), None),
    ("on_fail unlike the defaults", [("t1", "Fail", ["CP-A"], None), ("t2", "Skip", ["CP-B"], None)], (C1, T1),
     [{"id": "CP-A", "approver": "automated", "on_fail": {"red": "control-plan-fix", "unmeasurable": "product-fix"}},
      {"id": "CP-B", "approver": "automated+human:maintainer", "on_fail": {"unmeasurable": "product-fix"}},
      {"id": "CP-H", "approver": "human:maintainer"}, {"id": "CP-X", "approver": "automated"}]),
]
with tempfile.TemporaryDirectory() as tmp:
    for name, tests, stamp, rows in CASES:
        mb, cp = tool._bom(rows=rows)
        data = tool._xml(tests, stamp)
        Path(tmp, "e.xml").write_bytes(data)
        d, units, asm, by_id, mp = tool.i3a(mb, cp, None, None, {}, None)
        _, counted = tool.counted_rows(units, asm, by_id)
        recs = [{"source": "decision", "cp_ref": r, "evidence_path": "e.xml", "evidence_sha256": hashlib.sha256(data).hexdigest(),
                 "format": "xunit-v3", "observed_at": "t"} for r in counted]
        mine = tool.decide(units, asm, by_id, mp, {"commit": C1, "tree": T1}, [dict(x) for x in recs], lambda p: data)
        entry = {"delivered": {"commit": C1, "tree": T1}, "test_evidence_refs": [dict(x) for x in recs]}
        theirs = ref.decide(None, mb.decode(), cp.decode(), entry, tmp, None)

        def norm(r):
            return r["result"], {k: (v["category"], v["test"].split(":")[0], v["route"], v["result"]) for k, v in (r.get("rows") or {}).items()}
        note(norm(mine) == norm(theirs), f"A {name}: tool {norm(mine)} / reference {norm(theirs)}")

# ---------------------------------------------------------------- B
cases = [(refseq.B, *a) for a in refseq.ARMS + refseq.real_moviepad()] + [(refseq.work_bounds(line), *a) for line, *a in refseq.BOUND_ARMS]
for bounds, name, decisions, *_ in cases:
    r = refseq.read_sequence(bounds, decisions)
    m = tool.read_sequence(bounds, decisions)
    a = (r["convergence"], r["control"], sorted({s[0] for s in r["signals"]}), r["ruling_layer_candidate"], r["holds_measured"])
    b = (m["convergence"], m["control"], sorted({s[0] for s in m["signals"]}), m["ruling_layer_candidate"], m["holds_measured"])
    note(a == b, f"B {name}: tool {b} / reference {a}")
tb = [tool.parse_bounds(line) or dict(tool.DEFAULT_BOUNDS) for line, *_ in refseq.BOUND_ARMS]
rb = [refseq.work_bounds(line) for line, *_ in refseq.BOUND_ARMS]
note(tb == rb, f"B bounds lines: tool {tb} / reference {rb}")

# ---------------------------------------------------------------- C
if len(sys.argv) > 2 and sys.argv[2] != "-":
    eid = sys.argv[2]
    doc = yaml.safe_load((vp / "bomdd/50-as-built.yaml").read_bytes())
    e = [x for x in doc["as_built"] if x["id"] == eid][0]

    def g(*a):
        p = subprocess.run(["git", "-C", str(vp), *a], capture_output=True)
        return p.stdout.decode("utf-8") if p.returncode == 0 else None
    git = {"resolve": lambda rev: (g("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}") or "").strip() or None,
           "is_ancestor": lambda a, b: subprocess.run(["git", "-C", str(vp), "merge-base", "--is-ancestor", a, b]).returncode == 0,
           "tree": lambda c: (g("rev-parse", "--verify", "--quiet", f"{c}^{{tree}}") or "").strip() or None,
           "show": lambda c, path: g("show", f"{c}:{path}")}
    path, issue = e["work_order_ref"].split("@")
    fz = e["frozen_commit"]
    d = e["delivered"]["commit"]
    theirs = ref.decide(git["show"](issue, path), git["show"](fz, tool.MBOM), git["show"](fz, tool.CP),
                        {**e, "test_evidence_refs": [dict(x) for x in e.get("test_evidence_refs") or []]}, str(vp),
                        (git["show"](d, tool.MBOM), git["show"](d, tool.CP)), git)
    ad = e["advance_decision"]
    a = (theirs["result"], {k: (v["category"], v["test"].split(":")[0], v["route"]) for k, v in (theirs.get("rows") or {}).items()})
    b = (ad["result"], {k: (v["category"], str(v["test"]).split(":")[0], v["route"]) for k, v in (ad.get("rows") or {}).items()})
    note(a == b, f"C {eid}: tool {b[0]} ({len(b[1])} rows) / reference {a[0]} ({len(a[1])} rows); rows equal: {a[1] == b[1]}"
         + ("" if a == b else f"; reference defects {theirs.get('defects')}"))
lines.append(f"comparisons: {len(lines)}; differing: {bad}")
text = "\n".join(lines) + "\n"
sys.stdout.reconfigure(encoding="utf-8")
print(text, end="")
if len(sys.argv) > 3:
    Path(sys.argv[3]).write_bytes(text.encode("utf-8"))
sys.exit(1 if bad else 0)
