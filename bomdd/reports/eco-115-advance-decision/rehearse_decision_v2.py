"""ECO-115 design evidence: the advance decision (I3a, I3b, D1, D2, D4) applied as the order states it, so its rules meet real data by execution.

Evidence only; the method does not ship it (ECO-115 M1). decide() takes the work order's text as issued (read at the entry's work_order_ref, not
from the delivery; its one line '対象 BOM tag/commit' names the frozen revision as a 40-hex commit), the M-BOM and Control Plan as text at that
revision at the paths of the entry's mbom_ref / control_plan_ref (I1), the delivery's copies at the same paths (None = absent; I3a compares them
byte for byte), the As-Built entry as a mapping, and the evidence base directory.
The output is a mapping; json.dumps(..., sort_keys=True) of it is byte-identical for the same inputs.
v2 (redesign after EXP-20261024-01, MoviePad-Remake delivery 1): the line may name a tag, resolved at receipt into the entry's frozen_commit;
frozen_commit is never the delivered commit, and with git it and the work order's commit are ancestors of it; delivered is {commit, tree}
only; each evidence format declares an identity (a regex with groups commit and tree) and D1 test 1 reads the measured unit from the
evidence instead of the record's measured_on; a 'line' format is readable.
"""
import hashlib
import os
import re
import xml.etree.ElementTree as ET

import yaml

ROUTES = {"product-fix", "instrument-recovery", "control-plan-fix"}
OUTCOMES = {"passed", "failed", "skipped", "not-run"}
DEFAULT_ROUTE = {"violation": "product-fix", "unmeasurable": "instrument-recovery", "no-check": "control-plan-fix"}
RESULT = {"pass": "pass", "violation": "fail", "unmeasurable": "blocked", "no-check": "not-run"}
# v2: measured_on is no longer a record field — the evidence itself names what it measured (check_mapping's identity), and D1
# test 1 compares that with delivered (EXP-20261024-01: the comparator's output named no unit, M1 L4)
RECORD_FIELDS = ("cp_ref", "evidence_path", "evidence_sha256", "format", "observed_at")


def approver_parts(a):
    """(automated, human) for a value within I2, else None."""
    if a == "automated":
        return True, False
    if isinstance(a, str) and a.startswith("human:") and len(a) > len("human:"):
        return False, True
    if isinstance(a, str) and a.startswith("automated+human:") and len(a) > len("automated+human:"):
        return True, True
    return None


def parse(text, route, what):
    try:
        return yaml.safe_load(text), None
    except yaml.YAMLError:
        return None, (route, f"{what} does not parse")


FROZEN_LINE = re.compile(r"^- 対象 BOM tag/commit:[ \t]*(\S+)[ \t]*$", re.MULTILINE)
HEX40 = re.compile(r"[0-9a-f]{40}")
REF = re.compile(r"([^@\s]+)@([0-9a-f]{40})")


def frozen_revision(work_order_text):
    """The one field I1 reads from the work order (40-work-order.md:5), or None. v2: a value written as Markdown code
    (`bom-v4`) is read without its backticks — MoviePad-Remake's work order wrote it so, and the template does not say."""
    found = FROZEN_LINE.findall(work_order_text or "")
    return found[0].strip("`") or None if len(found) == 1 else None


def i3a(mbom_text, cp_text, delivered_texts=None, work_order_text=None, entry=None, git=None):
    """Input check before running anything. Returns (defects, units, assembly, rows_by_id, mapping).
    work_order_text and entry None: the freeze checks are not made (library use by the drivers' record builder only).
    v2 (redesign after EXP-20261024-01): the work order's line may name a tag or a commit; the receiving side records the
    commit it resolved to as the entry's frozen_commit at receipt. git is required (L8): {"resolve": rev -> 40-hex or None,
    "is_ancestor": (a, b) -> bool, "tree": commit -> 40-hex or None}; without it the decision is input-defect. delivered is
    checked here, before the freeze checks that read it (round 1 L4E1-7). The line must resolve to frozen_commit;
    frozen_commit is an ancestor of, or equal to, the work order's commit (the freeze precedes the issue, L4E1-3), and both
    are ancestors of the delivered commit and differ from it; delivered.tree is the delivered commit's tree (L4E1-4)."""
    mbom_doc, e1 = parse(mbom_text, "bom-fix", "M-BOM")
    cp_doc, e2 = parse(cp_text, "control-plan-fix", "Control Plan")
    defects = [e for e in (e1, e2) if e]
    if work_order_text is not None:
        entry = entry or {}
        if not git:
            return defects + [("record-fix", "git is not available to the decision (L8)")], None, None, None, None
        wref = REF.fullmatch(str(entry.get("work_order_ref", "")))
        delivered = entry.get("delivered")
        dcommit = delivered["commit"] if delivered_ok(delivered) else None
        frozen = str(entry.get("frozen_commit", ""))
        if dcommit is None:
            defects.append(("record-fix", f"delivered {delivered!r} missing or outside I2"))
        elif git["tree"](dcommit) != delivered["tree"]:
            defects.append(("record-fix", "delivered.tree is not the delivered commit's tree"))
        if not wref:
            defects.append(("record-fix", "the entry has no work_order_ref '<path>@<40-hex commit>'"))
        elif dcommit and wref.group(2) == dcommit:
            defects.append(("record-fix", "work_order_ref names the delivered commit; the work order is read as issued, not from the delivery"))
        if not HEX40.fullmatch(frozen):
            defects.append(("record-fix", "the entry has no frozen_commit (40-hex), resolved at receipt"))
        rev = frozen_revision(work_order_text)
        if rev is None:
            defects.append(("work-order-fix", "the work order has no single '対象 BOM tag/commit' line"))
        elif HEX40.fullmatch(frozen):
            resolved = git["resolve"](rev)
            if resolved is None:
                defects.append(("work-order-fix", f"the frozen revision {rev!r} cannot be resolved to a commit"))
            elif resolved != frozen:
                defects.append(("work-order-fix", f"the frozen revision {rev!r} resolves to {resolved[:8]}, not the recorded frozen_commit"))
            for key in ("mbom_ref", "control_plan_ref"):
                m = REF.fullmatch(str(entry.get(key, "")))
                if not m or m.group(2) != frozen:
                    defects.append(("record-fix", f"the entry's {key} does not name frozen_commit"))
            issued = wref.group(2) if wref else None
            if issued and frozen != issued and not git["is_ancestor"](frozen, issued):
                defects.append(("work-order-fix", "frozen_commit is not an ancestor of the work order's commit; the freeze must precede the issue"))
            if dcommit:
                if frozen == dcommit:
                    defects.append(("work-order-fix", "frozen_commit is the delivered commit; it must precede the work"))
                for label, commit in (("frozen_commit", frozen), ("the work order's commit", issued)):
                    if commit is not None and commit != dcommit and not git["is_ancestor"](commit, dcommit):
                        defects.append(("work-order-fix", f"{label} is not an ancestor of the delivered commit"))
    if delivered_texts is not None:
        for got, frozen, what in ((delivered_texts[0], mbom_text, "M-BOM"), (delivered_texts[1], cp_text, "Control Plan")):
            if got is None:
                defects.append(("product-fix", f"the delivery has no {what} at the frozen revision's path"))
            elif got != frozen:
                defects.append(("product-fix", f"the delivery's {what} differs from the revision frozen for the work"))
    if e1 or e2:
        return defects, None, None, None, None
    try:
        mbom = mbom_doc["mbom"]
        units = mbom["manufacturing_units"]
        assert isinstance(units, list)
    except (TypeError, KeyError, AssertionError):
        return defects + [("bom-fix", "M-BOM has no mbom.manufacturing_units list")], None, None, None, None
    try:
        cp = cp_doc.get("control_plan") or cp_doc
        rows = cp["characteristics"]
        assert isinstance(rows, list)
    except (AttributeError, TypeError, KeyError, AssertionError):
        return defects + [("control-plan-fix", "Control Plan has no characteristics list")], None, None, None, None
    ids = [u.get("id") for u in units]
    if len(ids) != len(set(ids)):
        defects.append(("bom-fix", "duplicate unit IDs"))
    rids = [r.get("id") for r in rows]
    if len(rids) != len(set(rids)):
        defects.append(("control-plan-fix", "duplicate row IDs"))
    by_id = {r.get("id"): r for r in rows}
    for u in units:
        if not u.get("acceptance_refs"):
            defects.append(("bom-fix", f"unit {u.get('id')} has empty acceptance_refs"))
    assembly = mbom.get("assembly")
    if not isinstance(assembly, dict) or "acceptance_refs" not in assembly:
        defects.append(("bom-fix", "mbom.assembly.acceptance_refs absent"))
        assembly = {"acceptance_refs": []}
    elif not assembly["acceptance_refs"] and not assembly.get("assembly_reason"):
        defects.append(("bom-fix", "mbom.assembly.acceptance_refs empty without assembly_reason"))
    named = sorted({r for u in units for r in (u.get("acceptance_refs") or [])} | set(assembly.get("acceptance_refs") or []))
    if not named:
        defects.append(("bom-fix", "no row is named"))
    for rid in named:
        row = by_id.get(rid)
        if row is None:
            defects.append(("control-plan-fix", f"named row {rid} does not exist"))
            continue
        if row.get("status") not in (None, "retired"):
            defects.append(("control-plan-fix", f"row {rid} status {row.get('status')!r} outside I2"))
        if row.get("status") == "retired":
            defects.append(("control-plan-fix", f"named row {rid} is retired"))
        if approver_parts(row.get("approver")) is None:
            defects.append(("control-plan-fix", f"row {rid} approver {row.get('approver')!r} outside I2"))
        f = row.get("on_fail")
        if f is not None and not (isinstance(f, dict) and set(f) <= {"red", "unmeasurable"} and set(f.values()) <= ROUTES):
            defects.append(("control-plan-fix", f"row {rid} on_fail {f!r} outside I2"))
    mapping = cp.get("check_mapping")
    ok = isinstance(mapping, dict) and mapping and all(
        isinstance(m, dict) and isinstance(m.get("row_key"), str) and isinstance(m.get("outcomes"), dict)
        and set(m["outcomes"].values()) <= OUTCOMES and identity_ok(m.get("identity"))
        and (fmt != "line" or line_key_ok(m["row_key"])) for fmt, m in mapping.items())
    if not ok:
        defects.append(("control-plan-fix", "check_mapping absent or outside I2"))
    return defects, units, assembly, by_id, mapping


def identity_ok(pattern):
    """v2 (I2): a format's identity is a regular expression with the named groups commit and tree."""
    try:
        return isinstance(pattern, str) and {"commit", "tree"} <= set(re.compile(pattern).groupindex)
    except re.error:
        return False


def measured_unit(path, pattern):
    """v2 (D1 test 1): the one {commit, tree} the evidence names, or a reason string."""
    text = open(path, "rb").read().decode("utf-8", errors="replace")
    found = {(m.group("commit"), m.group("tree")) for m in re.finditer(pattern, text)}
    if not found:
        return "the evidence does not name what it measured"
    if len(found) > 1:
        return "the evidence names more than one measured unit"
    commit, tree = found.pop()
    return {"commit": commit, "tree": tree}


def delivered_ok(d):
    """v2: {commit, tree} only — the non-git form is removed (it could never pass the commit-only freeze, L3E2-4)."""
    return isinstance(d, dict) and set(d) == {"commit", "tree"} and all(isinstance(v, str) and HEX40.fullmatch(v) for v in d.values())


def line_key_ok(pattern):
    """v2 (I2): for the 'line' format, row_key is a regular expression with the named groups outcome and row."""
    try:
        return isinstance(pattern, str) and {"outcome", "row"} <= set(re.compile(pattern).groupindex)
    except re.error:
        return False


def read_line_checks(path, m):
    """v2: the 'line' format (MoviePad-Remake's compare.py output) — every line row_key matches is a check, its outcome and
    row read from the groups; an outcome term not in outcomes makes the file unmeasurable, as in xunit (round 1 L4E1-1)."""
    try:
        text = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as e:
        return f"evidence unreadable ({type(e).__name__})"
    checks, total = {}, 0
    for line in text.splitlines():
        found = re.fullmatch(m["row_key"], line)
        if not found:
            continue
        total += 1
        term = found.group("outcome")
        if term not in m["outcomes"]:
            return f"outcome term {term!r} not in check_mapping"
        checks.setdefault(found.group("row"), []).append(m["outcomes"][term])
    if total == 0:
        return "evidence holds no check"
    return checks


def read_checks(path, fmt, mapping):
    """{row id: [outcome]} or a reason string for D1 test 1. The xunit-v3 and line formats are implemented here."""
    m = mapping[fmt]
    if fmt == "line":
        return read_line_checks(path, m)
    if fmt != "xunit-v3":
        return f"format {fmt} not readable by this rehearsal"
    try:
        root = ET.fromstring(open(path, "rb").read())
    except (OSError, ET.ParseError) as e:
        return f"evidence unreadable ({type(e).__name__})"
    checks, total = {}, 0
    for t in root.iter("test"):
        total += 1
        term = t.get("result", "")
        if term not in m["outcomes"]:
            return f"outcome term {term!r} not in check_mapping"
        owners = [tr.get("value") for tr in t.iter("trait") if tr.get("name") == m["row_key"] and tr.get("value")]
        for row in owners or [None]:   # None: a check no row owns (round 1 L4E1-2 reads its failures)
            checks.setdefault(row, []).append(m["outcomes"][term])
    if total == 0:
        return "evidence holds no check"
    return checks


def decide(work_order_text, mbom_text, cp_text, entry, base, delivered_texts, git=None):
    defects, units, assembly, by_id, mapping = i3a(mbom_text, cp_text, delivered_texts, work_order_text, entry, git)
    if defects:
        return {"result": "input-defect", "stage": "I3a", "defects": sorted(defects)}
    named = sorted({r for u in units for r in u["acceptance_refs"]} | set(assembly["acceptance_refs"]))
    counted = [r for r in named if approver_parts(by_id[r]["approver"])[0]]
    human = sorted(r for r in named if approver_parts(by_id[r]["approver"])[1])
    unnamed = sorted(r for r in by_id if r not in named)
    delivered = entry.get("delivered")
    records = [x for x in entry.get("test_evidence_refs") or [] if x.get("source") == "decision"]
    defects = []
    for x in records:
        if x.get("cp_ref") not in counted:
            defects.append(("record-fix", f"decision record for {x.get('cp_ref')}, which is not counted"))
    for r in counted:
        mine = [x for x in records if x.get("cp_ref") == r]
        if len(mine) != 1:
            defects.append(("record-fix", f"row {r} has {len(mine)} decision records"))
        elif any(k not in mine[0] for k in RECORD_FIELDS):
            defects.append(("record-fix", f"row {r} record lacks I3b's fields"))
        elif mine[0]["format"] not in mapping:
            defects.append(("record-fix", f"row {r} record format {mine[0]['format']!r} not in check_mapping"))
    if defects:
        return {"result": "input-defect", "stage": "I3b", "defects": sorted(defects)}
    cache, rows = {}, {}
    for r in counted:
        rec = next(x for x in records if x["cp_ref"] == r)
        path = os.path.join(base, rec["evidence_path"])
        key = (path, rec["format"])
        if key not in cache:
            try:
                digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
            except OSError:
                digest = None
            cache[key] = (digest, read_checks(path, rec["format"], mapping) if digest else "evidence unreadable (OSError)",
                          measured_unit(path, mapping[rec["format"]]["identity"]) if digest else None)
        digest, checks, unit = cache[key]
        if digest is None or isinstance(checks, str):
            cat, test = "unmeasurable", f"1: {checks}"
        elif digest != rec["evidence_sha256"]:
            cat, test = "unmeasurable", "1: sha256 differs"
        elif isinstance(unit, str):
            cat, test = "unmeasurable", f"1: {unit}"
        elif unit != delivered:
            cat, test = "unmeasurable", "1: the evidence measured another unit than delivered"
        elif any("failed" in v for k, v in checks.items() if k not in counted):
            cat, test = "unmeasurable", "1: the evidence reports a failure no counted row owns"
        else:
            mine = checks.get(r, [])
            if "failed" in mine:
                cat, test = "violation", "2"
            elif mine and all(o in ("skipped", "not-run") for o in mine):
                cat, test = "unmeasurable", "3"
            elif not mine:
                cat, test = "no-check", "4"
            else:
                cat, test = "pass", "5"
        route = None
        if cat != "pass":
            f = by_id[r].get("on_fail") or {}
            route = f.get("red") if cat == "violation" else f.get("unmeasurable") if cat == "unmeasurable" else None
            route = route or DEFAULT_ROUTE[cat]
        rows[r] = {"category": cat, "test": test, "route": route, "result": RESULT[cat]}
    if counted:
        result = "advances" if all(v["category"] == "pass" for v in rows.values()) else "holds"
    else:
        result = "advances" if all(approver_parts(by_id[r]["approver"])[1] for r in named) else "holds"
    return {"result": result, "rows": rows, "not_decided": {"human_part": human, "named_by_no_unit": unnamed}}
