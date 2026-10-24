"""ECO-115 design evidence: run the decision (rehearse_decision_v2.py) on ViewPrism2's real BOM and stored results, and on synthetic known-bad inputs.

Usage: python -B run_rehearsal_v2.py <ViewPrism2 repo> <out file>
v2: the freeze is constructed at 504921a's parent (not 504921a itself), the ancestry checks run on ViewPrism2's git, and the evidence names
its measured unit (the stored results name none; R1b stamps a copy, ASSUMED).
Real data: ViewPrism2's 32-mbom.yaml and 33-control-plan.yaml at 504921a by `git show` (read-only), and the stored test results kept here as
vp2-cp-results.xml.gz (the bytes of tests/ViewPrism2.Tests/TestResults/cp-results.xml, finished 2026-10-13T21:06+09:00; 504921a was
committed 2026-10-13T21:15+09:00, so the results were measured before that commit and the commit they ran on is not known).
Synthetic: a small M-BOM, Control Plan and xUnit file, one change per case, each with its expected outcome.
Works in a temporary directory; writes one text report. Also counts R-050 (a)/(b) in unit/CP pairs on the records the real run writes.
"""
import copy
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile

import yaml

import rehearse_decision_v2 as rd

HERE = os.path.dirname(os.path.abspath(__file__))
REV = "504921a33e7beb68ce2112817b01a44b664a82f7"
TREE = "31da53784ed10633eb4d9c6e0963398725e9e0f8"
PARENT = "b63897a4bbcd86c978ae8133ae658014d7184f21"  # 504921a^
ISSUED_VP2 = "f697a82cc36867b42d623809c8e1cbae12d35412"  # 504921a^^ (ECO-147's filing), taken as the work order's issue commit
DELIVERED = {"commit": REV, "tree": TREE}
IDENTITY = r"MEASURED_ON (?P<commit>[0-9a-f]{40}) (?P<tree>[0-9a-f]{40})"
MAPPING = {"xunit-v3": {"row_key": "cp", "outcomes": {"Pass": "passed", "Fail": "failed", "Skip": "skipped", "NotRun": "not-run"},
                        "identity": IDENTITY}}


def dump(doc):
    return yaml.safe_dump(doc, allow_unicode=True, sort_keys=False)


def show(repo, path, rev=REV):
    return subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout.decode("utf-8")


def migrate(mbom, cp):
    """The copy's edits, each listed: approver forms into I2, the on_fail key, check_mapping, assembly, units with no acceptance_refs dropped."""
    mbom, cp, edits = copy.deepcopy(mbom), copy.deepcopy(cp), []
    forms = {"maintainer": "human:maintainer", "automated+maintainer": "automated+human:maintainer",
             "factory self-acceptance(最終確認は maintainer)": "automated+human:maintainer"}
    for r in cp["control_plan"]["characteristics"]:
        a = r.get("approver")
        if a in forms:
            r["approver"] = forms[a]
            edits.append(f"{r['id']} approver {a!r} -> {forms[a]!r}")
        elif a is None:
            r["approver"] = "automated"
            edits.append(f"{r['id']} approver absent -> 'automated' (assumed)")
        f = r.get("on_fail")
        if isinstance(f, dict) and "dependency-update" in f:
            del f["dependency-update"]
            edits.append(f"{r['id']} on_fail key 'dependency-update' removed")
    cp["control_plan"]["check_mapping"] = MAPPING
    edits.append("check_mapping added (xunit-v3, trait cp)")
    mbom["mbom"]["assembly"] = {"acceptance_refs": [], "assembly_reason": "rehearsal: no end-to-end harness row chosen"}
    edits.append("mbom.assembly added (empty, with assembly_reason)")
    dropped = [u["id"] for u in mbom["mbom"]["manufacturing_units"] if not u.get("acceptance_refs")]
    mbom["mbom"]["manufacturing_units"] = [u for u in mbom["mbom"]["manufacturing_units"] if u.get("acceptance_refs")]
    edits.append(f"units with empty acceptance_refs dropped: {dropped}")
    return mbom, cp, edits


def records(mbom, cp, evidence, sha):
    _, units, assembly, by_id, _ = rd.i3a(dump(mbom), dump(cp))
    named = sorted({r for u in units for r in u["acceptance_refs"]} | set(assembly["acceptance_refs"]))
    return [{"source": "decision", "cp_ref": r, "evidence_path": evidence, "evidence_sha256": sha, "format": "xunit-v3",
             "observed_at": "2026-10-24T00:00:00Z"}
            for r in named if rd.approver_parts(by_id[r]["approver"])[0]]


def r050(mbom, d):
    rows = d.get("rows", {})
    pairs = [(u["id"], r) for u in mbom["mbom"]["manufacturing_units"] for r in (u.get("acceptance_refs") or [])]
    without = [p for p in pairs if rows.get(p[1], {}).get("result") != "pass"]
    return {"pairs": len(pairs), "a_pairs_without_pass": len(without), "of_which_human_only_rows": sum(1 for p in without if p[1] not in rows),
            "b_non_pass_rows": sum(1 for v in rows.values() if v["result"] != "pass")}


def summary(name, d, out):
    out.append(f"== {name}: {d['result']}" + (f" ({d['stage']})" if "stage" in d else ""))
    if "defects" in d:
        kinds = {}
        for route, _ in d["defects"]:
            kinds[route] = kinds.get(route, 0) + 1
        out.append(f"   defects {len(d['defects'])} by route {kinds}")
        out.extend(f"   - [{route}] {text}" for route, text in d["defects"])
    if "rows" in d:
        by = {}
        for r, v in sorted(d["rows"].items()):
            by.setdefault(f"{v['category']} (test {v['test']})", []).append(r)
        for k, v in sorted(by.items()):
            out.append(f"   {k}: {len(v)}" + (f" {v}" if len(v) <= 12 else ""))
        out.append(f"   not decided: human part {len(d['not_decided']['human_part'])}, named by no unit {len(d['not_decided']['named_by_no_unit'])}")


# ---- synthetic inputs -------------------------------------------------------------------------------------------------------------------

def stamp(unit):
    return f"<!-- MEASURED_ON {unit['commit']} {unit['tree']} -->"


def xml(tests, units=None):
    """tests: [(result term, [cp ids])] -> xUnit v3 bytes; units: the measured units the file names (default: the delivered one)."""
    body = "".join(f'<test name="t{i}" result="{res}"><traits>' + "".join(f'<trait name="cp" value="{c}"/>' for c in cps) + "</traits></test>"
                   for i, (res, cps) in enumerate(tests))
    stamps = "".join(stamp(u) for u in ([DELIVERED] if units is None else units))
    return f'<?xml version="1.0"?>{stamps}<assemblies><assembly name="x" total="{len(tests)}">{body}</assembly></assemblies>'.encode()


BASE_TESTS = [("Pass", ["CP-A"]), ("Pass", ["CP-B"]), ("Pass", ["CP-SHARED"]), ("Pass", ["CP-MIX"]), ("Pass", ["CP-E2E"])]


def base():
    mbom = {"mbom": {"assembly": {"acceptance_refs": ["CP-E2E"]}, "manufacturing_units": [
        {"id": "M-A", "acceptance_refs": ["CP-A", "CP-SHARED", "CP-HUMAN"]},
        {"id": "M-B", "acceptance_refs": ["CP-B", "CP-SHARED", "CP-MIX"]}]}}
    cp = {"control_plan": {"check_mapping": copy.deepcopy(MAPPING), "characteristics": [
        {"id": r, "approver": a} for r, a in (("CP-A", "automated"), ("CP-B", "automated"), ("CP-SHARED", "automated"),
                                              ("CP-HUMAN", "human:maintainer"), ("CP-MIX", "automated+human:maintainer"), ("CP-E2E", "automated"),
                                              ("CP-UNNAMED", "automated"))]}}
    return mbom, cp, list(BASE_TESTS)


def row(cp, rid):
    return next(r for r in cp["control_plan"]["characteristics"] if r["id"] == rid)


FROZEN = "1" * 40          # synthetic frozen revision
ISSUED = "2" * 40          # synthetic commit at which the work order was issued
WO = f"# Work Order\n- 対象 BOM tag/commit: {FROZEN}\n- Routing ref: `bomdd/34-routing.yaml`\n"


LATER = "4" * 40           # synthetic commit after the work order's issue, before the delivery
OTHER = "5" * 40           # synthetic commit on another line of history
EARLY = "8" * 40           # synthetic commit before the freeze, with an older BOM
HISTORY = [EARLY, FROZEN, ISSUED, LATER, REV]
TAGS = {"bom-x": FROZEN, "bom-late": LATER, "bom-back": EARLY}


def stub_resolve(rev):
    return rev if rev in HISTORY or rev == OTHER else TAGS.get(rev)


# round 1 L4E1-5: the synthetic cases run with git (a stub history FROZEN < ISSUED < LATER < REV, OTHER outside it), so the base case
# exercises the ancestry rules; git=None is its own case (input-defect, L8)
GIT_STUB = {"resolve": stub_resolve,
            "is_ancestor": lambda a, b: a in HISTORY and b in HISTORY and HISTORY.index(a) <= HISTORY.index(b),
            "tree": lambda c: TREE if c == REV else ("6" * 40 if c in HISTORY else None),
            "show": lambda c, path: f"{path} at the synthetic BOM" if c in HISTORY else None}
# round 2 L4E2-1: in the stub every commit of HISTORY holds the same BOM except EARLY (an older one); run_case overrides show for that


def stub_with(early_differs):
    if not early_differs:
        return GIT_STUB
    return dict(GIT_STUB, show=lambda c, path: f"{path} at an older BOM" if c == EARLY else GIT_STUB["show"](c, path))


def frozen_entry(rev, recs, issued=ISSUED):
    return {"work_order_ref": f"bomdd/40-work-order.md@{issued}", "mbom_ref": f"bomdd/32-mbom.yaml@{rev}",
            "control_plan_ref": f"bomdd/33-control-plan.yaml@{rev}", "delivered": dict(DELIVERED), "test_evidence_refs": recs,
            "frozen_commit": rev if len(rev) == 40 else FROZEN}


def run_case(td, change):
    mbom, cp, tests = base()
    ctx = {"mbom_text": None, "cp_text": None, "delivered_texts": None, "entry_edit": None, "evidence": None, "wo_text": None, "no_file": False, "no_git": False, "early_differs": True}
    change(mbom, cp, tests, ctx)
    ev = ctx["evidence"] if ctx["evidence"] is not None else xml(tests)
    path = os.path.join(td, "ev.xml")
    if os.path.exists(path):
        os.remove(path)
    if not ctx["no_file"]:
        open(path, "wb").write(ev)
    mt, ct = ctx["mbom_text"] or dump(mbom), ctx["cp_text"] or dump(cp)
    try:
        recs = records(mbom, cp, "ev.xml", "none" if ctx["no_file"] else hashlib.sha256(ev).hexdigest())
    except Exception:
        recs = []
    entry = frozen_entry(FROZEN, recs)
    if ctx["entry_edit"]:
        ctx["entry_edit"](entry)
    wo = ctx["wo_text"] if ctx["wo_text"] is not None else WO
    return rd.decide(wo, mt, ct, entry, td, ctx["delivered_texts"] or (mt, ct), None if ctx["no_git"] else stub_with(ctx["early_differs"]))


def setv(**kw):
    def f(m, c, t, ctx):
        ctx.update(kw)
    return f


def add_test(res, cps):
    return lambda m, c, t, ctx: t.append((res, cps))


def rec(rid, **kw):
    def edit(entry):
        for x in entry["test_evidence_refs"]:
            if x["cp_ref"] == rid:
                x.update(kw)
    return lambda m, c, t, ctx: ctx.update(entry_edit=edit)


CASES = [
    ("base", lambda m, c, t, ctx: None, ("advances", None)),
    ("I3a Control Plan unparsable", setv(cp_text="control_plan: [unclosed"), ("input-defect", "Control Plan does not parse")),
    ("I3a M-BOM unparsable", setv(mbom_text="mbom: {unclosed"), ("input-defect", "M-BOM does not parse")),
    ("I3a delivered Control Plan differs", lambda m, c, t, ctx: ctx.update(delivered_texts=(dump(m), dump(c) + "# edited\n")),
     ("input-defect", "delivery's Control Plan differs")),
    ("I3a delivered M-BOM differs", lambda m, c, t, ctx: ctx.update(delivered_texts=(dump(m) + "# edited\n", dump(c))),
     ("input-defect", "delivery's M-BOM differs")),
    ("I3a delivery without its Control Plan", lambda m, c, t, ctx: ctx.update(delivered_texts=(dump(m), None)),
     ("input-defect", "delivery has no Control Plan")),
    ("I3a work order without the frozen-revision line", setv(wo_text="# Work Order\n- 対象 BOM tag/commit:\n"),
     ("input-defect", "no single '対象 BOM tag/commit' line")),
    ("I3a work order with two frozen-revision lines", setv(wo_text=WO + f"- 対象 BOM tag/commit: {FROZEN}\n"),
     ("input-defect", "no single '対象 BOM tag/commit' line")),
    ("I3a frozen revision given as a tag git cannot resolve", setv(wo_text="- 対象 BOM tag/commit: v1.2\n"), ("input-defect", "cannot be resolved to a commit")),
    ("I3a (v2) frozen revision given as a tag that resolves to frozen_commit, in backticks", setv(wo_text="- 対象 BOM tag/commit: `bom-x`\n"),
     ("advances", None)),
    ("I3a (v2) git unavailable, with a row approver outside I2: both listed (round 2 L4E2-3)", lambda m, c, t, ctx: (ctx.update(no_git=True), row(c, "CP-A").update(approver="maintainer")),
     ("input-defect", "approver 'maintainer' outside I2")),
    ("I3a (v2) git unavailable", setv(no_git=True), ("input-defect", "git is not available")),
    ("I3a (v2) frozen_commit on another line of history (multi-reason: implied by freeze <= issue)",
     lambda m, c, t, ctx: ctx.update(wo_text=f"- 対象 BOM tag/commit: {OTHER}\n", entry_edit=lambda e: e.update(
         frozen_commit=OTHER, mbom_ref=f"bomdd/32-mbom.yaml@{OTHER}", control_plan_ref=f"bomdd/33-control-plan.yaml@{OTHER}")),
     ("input-defect", "the freeze must precede the issue")),
    ("I3a (v2) the freeze after the issue (a tag moved to a later commit before receipt)",
     lambda m, c, t, ctx: ctx.update(wo_text="- 対象 BOM tag/commit: bom-late\n", entry_edit=lambda e: e.update(
         frozen_commit=LATER, mbom_ref=f"bomdd/32-mbom.yaml@{LATER}", control_plan_ref=f"bomdd/33-control-plan.yaml@{LATER}")),
     ("input-defect", "the freeze must precede the issue")),
    ("I3a (v2) a tag moved back to a commit with an older BOM (round 2 L4E2-1)",
     lambda m, c, t, ctx: ctx.update(wo_text="- 対象 BOM tag/commit: bom-back\n", entry_edit=lambda e: e.update(
         frozen_commit=EARLY, mbom_ref=f"bomdd/32-mbom.yaml@{EARLY}", control_plan_ref=f"bomdd/33-control-plan.yaml@{EARLY}")),
     ("input-defect", "the BOM changed between the freeze and the issue")),
    ("I3a (v2) a freeze before the issue with the same BOM advances",
     lambda m, c, t, ctx: ctx.update(early_differs=False, wo_text="- 対象 BOM tag/commit: bom-back\n", entry_edit=lambda e: e.update(
         frozen_commit=EARLY, mbom_ref=f"bomdd/32-mbom.yaml@{EARLY}", control_plan_ref=f"bomdd/33-control-plan.yaml@{EARLY}")),
     ("advances", None)),
    ("I3a (v2) the work order's commit outside the delivered history",
     lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.update(work_order_ref=f"bomdd/40-work-order.md@{OTHER}")),
     ("input-defect", "the work order's commit is not an ancestor of the delivered commit")),
    ("I3a (v2) delivered.tree is not the delivered commit's tree", lambda m, c, t, ctx: ctx.update(
        entry_edit=lambda e: e.update(delivered={"commit": REV, "tree": "7" * 40})), ("input-defect", "delivered.tree is not the delivered commit's tree")),
    ("I3a (v2) a line format whose row_key lacks the group outcome", lambda m, c, t, ctx: c["control_plan"]["check_mapping"].update(
        line={"row_key": r"(?P<row>\S+)", "outcomes": {"PASS": "passed"}, "identity": IDENTITY}), ("input-defect", "check_mapping")),
    ("I3a entry's control_plan_ref naming another revision",
     lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.update(control_plan_ref="bomdd/33-control-plan.yaml@" + "3" * 40)),
     ("input-defect", "control_plan_ref does not name frozen_commit")),
    ("I3a entry's mbom_ref naming another revision",
     lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.update(mbom_ref="bomdd/32-mbom.yaml@" + "3" * 40)),
     ("input-defect", "mbom_ref does not name frozen_commit")),
    ("I3a no work_order_ref", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.pop("work_order_ref")), ("input-defect", "no work_order_ref")),
    ("I3a (v2) no frozen_commit in the entry", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.pop("frozen_commit")),
     ("input-defect", "no frozen_commit")),
    ("I3a (v2) the frozen revision is the delivered commit, line and refs agreeing (multi-reason: implied by freeze <= issue)",
     lambda m, c, t, ctx: ctx.update(wo_text=f"- 対象 BOM tag/commit: {REV}\n", entry_edit=lambda e: e.update(
         frozen_commit=REV, mbom_ref=f"bomdd/32-mbom.yaml@{REV}", control_plan_ref=f"bomdd/33-control-plan.yaml@{REV}")),
     ("input-defect", "the freeze must precede the issue")),
    ("I3a work order read from the delivered commit",
     lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.update(work_order_ref=f"bomdd/40-work-order.md@{REV}")),
     ("input-defect", "work_order_ref names the delivered commit")),
    ("I3a duplicate unit ID", lambda m, c, t, ctx: m["mbom"]["manufacturing_units"].append({"id": "M-A", "acceptance_refs": ["CP-A"]}),
     ("input-defect", "duplicate unit IDs")),
    ("I3a duplicate row ID", lambda m, c, t, ctx: c["control_plan"]["characteristics"].append({"id": "CP-A", "approver": "automated"}),
     ("input-defect", "duplicate row IDs")),
    ("I3a unit with empty acceptance_refs", lambda m, c, t, ctx: m["mbom"]["manufacturing_units"].append({"id": "M-C", "acceptance_refs": []}),
     ("input-defect", "unit M-C has empty acceptance_refs")),
    ("I3a assembly absent", lambda m, c, t, ctx: m["mbom"].pop("assembly"), ("input-defect", "assembly.acceptance_refs absent")),
    ("I3a assembly empty without reason", lambda m, c, t, ctx: m["mbom"].update(assembly={"acceptance_refs": []}),
     ("input-defect", "empty without assembly_reason")),
    ("I3a no row named", lambda m, c, t, ctx: m["mbom"].update(manufacturing_units=[], assembly={"acceptance_refs": [], "assembly_reason": "x"}),
     ("input-defect", "no row is named")),
    ("I3a named row missing", lambda m, c, t, ctx: m["mbom"]["manufacturing_units"][0]["acceptance_refs"].append("CP-NONE"),
     ("input-defect", "named row CP-NONE does not exist")),
    ("I3a named row retired", lambda m, c, t, ctx: row(c, "CP-A").update(status="retired"), ("input-defect", "named row CP-A is retired")),
    ("I3a status draft", lambda m, c, t, ctx: row(c, "CP-A").update(status="draft"), ("input-defect", "status 'draft' outside I2")),
    ("I3a approver maintainer", lambda m, c, t, ctx: row(c, "CP-A").update(approver="maintainer"), ("input-defect", "approver 'maintainer' outside I2")),
    ("I3a approver absent", lambda m, c, t, ctx: row(c, "CP-A").pop("approver"), ("input-defect", "approver None outside I2")),
    ("I3a on_fail key dependency-update", lambda m, c, t, ctx: row(c, "CP-A").update(on_fail={"red": "product-fix", "dependency-update": "human-approval"}),
     ("input-defect", "on_fail")),
    ("I3a on_fail value human-approval", lambda m, c, t, ctx: row(c, "CP-A").update(on_fail={"red": "human-approval"}), ("input-defect", "on_fail")),
    ("I3a check_mapping absent", lambda m, c, t, ctx: c["control_plan"].pop("check_mapping"), ("input-defect", "check_mapping")),
    ("I3a outcomes value outside the four", lambda m, c, t, ctx: c["control_plan"]["check_mapping"]["xunit-v3"]["outcomes"].update(Error="error"),
     ("input-defect", "check_mapping")),
    ("I3a (v2) a format without identity", lambda m, c, t, ctx: c["control_plan"]["check_mapping"]["xunit-v3"].pop("identity"),
     ("input-defect", "check_mapping")),
    ("I3a (v2) an identity without the group tree", lambda m, c, t, ctx: c["control_plan"]["check_mapping"]["xunit-v3"].update(
        identity=r"MEASURED_ON (?P<commit>[0-9a-f]{40})"), ("input-defect", "check_mapping")),
    ("I3a no delivered", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.pop("delivered")), ("input-defect", "delivered None")),
    ("I3a malformed delivered", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.update(delivered={"commit": REV})), ("input-defect", "delivered")),
    ("I3b counted row with no record", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e["test_evidence_refs"].pop(0)),
     ("input-defect", "has 0 decision records")),
    ("I3b two records for one row", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e["test_evidence_refs"].append(dict(e["test_evidence_refs"][0]))),
     ("input-defect", "has 2 decision records")),
    ("I3b record without evidence_sha256", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e["test_evidence_refs"][0].pop("evidence_sha256")),
     ("input-defect", "lacks I3b's fields")),
    ("I3b record format not in check_mapping", rec("CP-A", format="trx"), ("input-defect", "format 'trx' not in check_mapping")),
    ("I3b record for a row not counted", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e["test_evidence_refs"].append(
        dict(e["test_evidence_refs"][0], cp_ref="CP-HUMAN"))), ("input-defect", "CP-HUMAN, which is not counted")),
    ("D1-1 unreadable evidence", setv(evidence=b"<not xml"), ("holds", ("CP-A", "unmeasurable", "1: evidence unreadable (ParseError)"))),
    ("D1-1 the instrument wrote no evidence file (sha256 'none')", setv(no_file=True),
     ("holds", ("CP-A", "unmeasurable", "1: evidence unreadable (OSError)"))),
    ("D1-1 changed sha256", rec("CP-A", evidence_sha256="0" * 64), ("holds", ("CP-A", "unmeasurable", "1: sha256 differs"))),
    ("D1-1 (v2) the evidence measured another unit", lambda m, c, t, ctx: ctx.update(evidence=xml(t, [{"commit": "3" * 40, "tree": TREE}])),
     ("holds", ("CP-A", "unmeasurable", "1: the evidence measured another unit than delivered"))),
    ("D1-1 (v2) the evidence names no measured unit", lambda m, c, t, ctx: ctx.update(evidence=xml(t, [])),
     ("holds", ("CP-A", "unmeasurable", "1: the evidence does not name what it measured"))),
    ("D1-1 (v2) the evidence names two measured units", lambda m, c, t, ctx: ctx.update(evidence=xml(t, [DELIVERED, {"commit": "3" * 40, "tree": TREE}])),
     ("holds", ("CP-A", "unmeasurable", "1: the evidence names more than one measured unit"))),
    ("D1-1 evidence with no checks", setv(evidence=xml([])), ("holds", ("CP-A", "unmeasurable", "1: evidence holds no check"))),
    ("D1-1 (v2) a failed check no row owns (no cp trait)", add_test("Fail", []),
     ("holds", ("CP-A", "unmeasurable", "1: the evidence reports a failure no counted row owns", "control-plan-fix"))),
    ("D1-1 (v2) a failed check of a row named by no unit", add_test("Fail", ["CP-UNNAMED"]),
     ("holds", ("CP-B", "unmeasurable", "1: the evidence reports a failure no counted row owns", "control-plan-fix"))),
    ("D1-1 unmapped outcome term", add_test("Inconclusive", ["CP-A"]), ("holds", ("CP-A", "unmeasurable", "1: outcome term 'Inconclusive' not in check_mapping"))),
    ("D1-2 failed check", add_test("Fail", ["CP-A"]), ("holds", ("CP-A", "violation", "2"))),
    ("D1-3 all checks skipped", lambda m, c, t, ctx: t.__setitem__(0, ("Skip", ["CP-A"])), ("holds", ("CP-A", "unmeasurable", "3"))),
    ("D1-4 no check for a row", lambda m, c, t, ctx: t.pop(0), ("holds", ("CP-A", "no-check", "4"))),
    ("D2 on_fail route used", lambda m, c, t, ctx: (row(c, "CP-A").update(on_fail={"red": "control-plan-fix"}), t.append(("Fail", ["CP-A"]))),
     ("holds", ("CP-A", "violation", "2", "control-plan-fix"))),
    ("D0 mixed row decided by its automated part (no check)", lambda m, c, t, ctx: t.pop(3), ("holds", ("CP-MIX", "no-check", "4"))),
    ("D2 assembly row with a failed check", add_test("Fail", ["CP-E2E"]), ("holds", ("CP-E2E", "violation", "2"))),
    ("D2 shared row, one failed check", add_test("Fail", ["CP-SHARED"]), ("holds", ("CP-SHARED", "violation", "2"))),
    ("D2 every named row human", lambda m, c, t, ctx: [r.update(approver="human:maintainer") for r in c["control_plan"]["characteristics"]],
     ("advances", None)),
    ("D0 a source: phase5 record is not read", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e["test_evidence_refs"].append(
        {"source": "phase5", "cp_ref": "CP-HUMAN", "result": "fail"})), ("advances", None)),
]

OUTSIDE = [
    ("factory PASS added to the delivery", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.update(factory_report="PASS"))),
    ("the self-acceptance log changed", lambda m, c, t, ctx: ctx.update(entry_edit=lambda e: e.update(self_acceptance="26/26 green -> 0/26"))),
    ("the rest of the work order changed", setv(wo_text=WO + "## 目的\nanything else\n")),
    ("a row's when changed", lambda m, c, t, ctx: row(c, "CP-A").update(when=["dependency-update"])),
    ("a row's depth changed", lambda m, c, t, ctx: row(c, "CP-A").update(depth="G")),
    ("a row's verifies changed", lambda m, c, t, ctx: row(c, "CP-A").update(verifies=["M-B"])),
    ("a row's characteristic changed", lambda m, c, t, ctx: row(c, "CP-A").update(characteristic="anything")),
]


def check(d, expected):
    result, detail = expected
    if d["result"] != result:
        return False
    if detail is None:
        return True
    if isinstance(detail, str):
        return any(detail in text for _, text in d.get("defects", []))
    rid, cat, test, *route = detail
    v = d.get("rows", {}).get(rid, {})
    return v.get("category") == cat and v.get("test") == test and (not route or v.get("route") == route[0])


def main():
    vp2, path = sys.argv[1:3]
    out = []
    raw = gzip.open(os.path.join(HERE, "vp2-cp-results.xml.gz")).read()
    sha = hashlib.sha256(raw).hexdigest()
    out.append(f"stored results sha256 {sha} ({len(raw)} bytes)")
    with tempfile.TemporaryDirectory() as td:
        open(os.path.join(td, "cp-results.xml"), "wb").write(raw)
        mtext, ctext = show(vp2, "bomdd/32-mbom.yaml"), show(vp2, "bomdd/33-control-plan.yaml")
        # constructed (neither product's work order has the line; measure_freeze.py). v2: the frozen revision and the work order's issue are
        # both f697a82 (ECO-147's filing; the freeze may equal the issue but not follow it — round 1 L4E1-3: v1's freeze at 504921a and the
        # first v2 freeze at b63897a each followed the issue), and the delivery is 504921a. The M-BOM and the Control Plan are the same blobs at
        # f697a82 and 504921a (asserted below), so the delivered copies are byte-equal by the data, not by construction.
        wo = f"- 対象 BOM tag/commit: {ISSUED_VP2}\n"

        def run_git(*args):
            return subprocess.run(["git", "-C", vp2, *args], capture_output=True)

        gitcb = {"resolve": lambda rev: (lambda p: p.stdout.decode().strip() if p.returncode == 0 else None)(
                     run_git("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")),
                 "is_ancestor": lambda a, b: run_git("merge-base", "--is-ancestor", a, b).returncode == 0,
                 "tree": lambda c: (lambda p: p.stdout.decode().strip() if p.returncode == 0 else None)(run_git("rev-parse", f"{c}^{{tree}}")),
                 "show": lambda c, path: (lambda p: p.stdout.decode("utf-8") if p.returncode == 0 else None)(run_git("show", f"{c}:{path}"))}
        mtext_f, ctext_f = show(vp2, "bomdd/32-mbom.yaml", ISSUED_VP2), show(vp2, "bomdd/33-control-plan.yaml", ISSUED_VP2)
        assert (mtext_f, ctext_f) == (mtext, ctext), "the BOM differs between f697a82 and 504921a"
        d0 = rd.decide(wo, mtext, ctext, frozen_entry(ISSUED_VP2, [], ISSUED_VP2), td, (mtext, ctext), gitcb)
        summary("R0 ViewPrism2 at 504921a as it is", d0, out)
        m1, c1, edits = migrate(yaml.safe_load(mtext), yaml.safe_load(ctext))
        mt1, ct1 = dump(m1), dump(c1)
        out.append("== R1 edits of the migrated copy:")
        out.extend(f"   - {e}" for e in edits)
        d1 = rd.decide(wo, mt1, ct1, frozen_entry(ISSUED_VP2, records(m1, c1, "cp-results.xml", sha), ISSUED_VP2), td, (mt1, ct1), gitcb)
        summary("R1a migrated copy, the stored results as they are (they name no measured unit)", d1, out)
        # v2: the measured unit is read from the evidence (check_mapping identity). The stored results name none; R1b appends an XML comment
        # naming 504921a, as an instrument stamping its run would — ASSUMED, design evidence only (the results were measured before 504921a).
        stamped = raw + ("\n" + stamp(DELIVERED) + "\n").encode()
        open(os.path.join(td, "cp-results-assumed.xml"), "wb").write(stamped)
        e2 = frozen_entry(ISSUED_VP2, records(m1, c1, "cp-results-assumed.xml", hashlib.sha256(stamped).hexdigest()), ISSUED_VP2)
        d2 = rd.decide(wo, mt1, ct1, e2, td, (mt1, ct1), gitcb)
        summary("R1b migrated copy, the results stamped as measured on 504921a ASSUMED (design evidence only; not what the data show)", d2, out)
        out.append(f"   R-050 on R1b's records, in unit/CP pairs: {r050(m1, d2)}")
        again = rd.decide(wo, mt1, ct1, e2, td, (mt1, ct1), gitcb)
        out.append(f"   R1b run twice, byte-identical JSON: {json.dumps(d2, sort_keys=True) == json.dumps(again, sort_keys=True)}")
        out.append("== synthetic cases (expected outcome; OK when the decision gives it)")
        base_out = None
        ok_all = True
        for name, change, expected in CASES:
            d = run_case(td, change)
            ok = check(d, expected)
            ok_all &= ok
            if name == "base":
                base_out = json.dumps(d, sort_keys=True)
            shown = d.get("defects") or {k: v for k, v in d.get("rows", {}).items() if v["category"] != "pass"}
            out.append(f"   {'OK    ' if ok else 'MISSED'} {name}: {d['result']} {json.dumps(shown, ensure_ascii=False, sort_keys=True)[:200]}")
        for name, change in OUTSIDE:
            d = run_case(td, change)
            same = json.dumps(d, sort_keys=True) == base_out
            ok_all &= same
            out.append(f"   {'OK    ' if same else 'MISSED'} outside I1, {name}: output {'byte-identical to base' if same else 'CHANGED'}")
        out.append(f"== all synthetic cases as expected: {ok_all}")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
