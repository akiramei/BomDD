"""ECO-115 design evidence: the advance decision (I3a, I3b, D1, D2, D4) applied as the order states it, so its rules meet real data by execution.

Evidence only; the method does not ship it (ECO-115 M1). decide() takes the work order's text as issued (read at the entry's work_order_ref, not
from the delivery; its one line '対象 BOM tag/commit' names the frozen revision as a 40-hex commit), the M-BOM and Control Plan as text at that
revision at the paths of the entry's mbom_ref / control_plan_ref (I1), the delivery's copies at the same paths (None = absent; I3a compares them
byte for byte), the As-Built entry as a mapping, and the evidence base directory.
The output is a mapping; json.dumps(..., sort_keys=True) of it is byte-identical for the same inputs.
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
RECORD_FIELDS = ("cp_ref", "evidence_path", "evidence_sha256", "format", "measured_on", "observed_at")


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
    """The one field I1 reads from the work order (40-work-order.md:5), or None."""
    found = FROZEN_LINE.findall(work_order_text or "")
    return found[0] if len(found) == 1 else None


def i3a(mbom_text, cp_text, delivered_texts=None, work_order_text=None, entry=None):
    """Input check before running anything. Returns (defects, units, assembly, rows_by_id, mapping).
    work_order_text and entry None: the freeze checks are not made (library use by the drivers' record builder only)."""
    mbom_doc, e1 = parse(mbom_text, "bom-fix", "M-BOM")
    cp_doc, e2 = parse(cp_text, "control-plan-fix", "Control Plan")
    defects = [e for e in (e1, e2) if e]
    if work_order_text is not None:
        entry = entry or {}
        wref = REF.fullmatch(str(entry.get("work_order_ref", "")))
        dcommit = (entry.get("delivered") or {}).get("commit")
        if not wref:
            defects.append(("record-fix", "the entry has no work_order_ref '<path>@<40-hex commit>'"))
        elif dcommit and wref.group(2) == dcommit:
            defects.append(("record-fix", "work_order_ref names the delivered commit; the work order is read as issued, not from the delivery"))
        rev = frozen_revision(work_order_text)
        if rev is None:
            defects.append(("work-order-fix", "the work order has no single '対象 BOM tag/commit' line"))
        elif not HEX40.fullmatch(rev):
            defects.append(("work-order-fix", f"the frozen revision {rev!r} is not a 40-hex commit ID"))
        else:
            for key in ("mbom_ref", "control_plan_ref"):
                m = REF.fullmatch(str(entry.get(key, "")))
                if not m or m.group(2) != rev:
                    defects.append(("record-fix", f"the entry's {key} does not name the work order's revision"))
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
        and set(m["outcomes"].values()) <= OUTCOMES for m in mapping.values())
    if not ok:
        defects.append(("control-plan-fix", "check_mapping absent or outside I2"))
    return defects, units, assembly, by_id, mapping


def delivered_ok(d):
    return isinstance(d, dict) and (set(d) == {"commit", "tree"} or set(d) == {"content_sha256"}) and all(isinstance(v, str) and v for v in d.values())


def read_checks(path, fmt, mapping):
    """{row id: [outcome]} or a reason string for D1 test 1. Only the xunit-v3 format is implemented here."""
    m = mapping[fmt]
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
        for tr in t.iter("trait"):
            if tr.get("name") == m["row_key"] and tr.get("value"):
                checks.setdefault(tr.get("value"), []).append(m["outcomes"][term])
    if total == 0:
        return "evidence holds no check"
    return checks


def decide(work_order_text, mbom_text, cp_text, entry, base, delivered_texts):
    defects, units, assembly, by_id, mapping = i3a(mbom_text, cp_text, delivered_texts, work_order_text, entry)
    if defects:
        return {"result": "input-defect", "stage": "I3a", "defects": sorted(defects)}
    named = sorted({r for u in units for r in u["acceptance_refs"]} | set(assembly["acceptance_refs"]))
    counted = [r for r in named if approver_parts(by_id[r]["approver"])[0]]
    human = sorted(r for r in named if approver_parts(by_id[r]["approver"])[1])
    unnamed = sorted(r for r in by_id if r not in named)
    delivered = entry.get("delivered")
    records = [x for x in entry.get("test_evidence_refs") or [] if x.get("source") == "decision"]
    defects = []
    if not delivered_ok(delivered):
        defects.append(("record-fix", f"delivered {delivered!r} missing or outside I2"))
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
            cache[key] = (digest, read_checks(path, rec["format"], mapping) if digest else "evidence unreadable (OSError)")
        digest, checks = cache[key]
        if digest is None or isinstance(checks, str):
            cat, test = "unmeasurable", f"1: {checks}"
        elif digest != rec["evidence_sha256"]:
            cat, test = "unmeasurable", "1: sha256 differs"
        elif rec["measured_on"] != delivered:
            cat, test = "unmeasurable", "1: measured_on is not delivered"
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
