#!/usr/bin/env python3
"""bom-structure-check — the machine part of G3's A1 structure resolution and of the part-standard check C1 (ECO-118)

Playbook section 4.6 (G3) asks the orchestrating AI to re-check, before the dry run, section 4.5's C1 and the A1 structure
resolution, reading the E-BOM, the M-BOM and the Control Plan only. Until ECO-118 that was a reading; this tool runs it.

Reads bomdd/30-ebom.yaml, bomdd/32-mbom.yaml and bomdd/33-control-plan.yaml of a product (--root, default .) from one
source: the working tree (default), the git index (--index) or a commit (--rev <commit>). Strict YAML (a duplicate key is
UNMEASURABLE). Nothing else is read.

Rules applied (RULE_SET):
  A1-1  every `requires` target of a unit with part_standard resolves (PS- to an existing provides item; IF- to the one
        unit of A1-2, from a unit without ebom_refs or one whose E items provide or require it; procurement:<package> to
        the M-BOM's top-level procurement; platform:<name> as written; anything else fails)
  A1-2  every IF- is realised by exactly one unit (ebom_refs holds the providing E item, part_standard.provides holds an
        item with that ruled_ref). Lazy: an IF- whose providing item is in units without part_standard only is skipped
  A1-3  every ruled_ref names an IF- provided by one of its unit's E items
  A1-4  a unit with E items targets a PS- only of a unit sharing an E item with it or of a unit without ebom_refs, and
        not of a unit without ebom_refs that requires - directly or through other units without ebom_refs - an IF- or a
        PS- across an E-item boundary (the relay case of section 4.5 P4). Units without ebom_refs may require anything (P4)
  A1-5  for every E-BOM interfaces.requires, a unit realising the consumer item has a requires targeting the IF-; skipped
        when one unit realises both items, or when no unit realising the consumer has part_standard (lazy)
  A1-6  a non-empty depends_on equals the set of units its unit's resolved requires point to
  P1-id provides ids are PS-<UNIT>-Pnn, requires ids PS-<UNIT>-Rnn, unique within the unit across both lists
  C1-a  every part_standard_refs id of a Control Plan row names an existing provides item
  C1-b  every provides item is named by at least one row listed in its unit's acceptance_refs
Left out: retired E items (lineage.superseded_by), mbom.retired_units and any other list than manufacturing_units, and
template placeholders (an id containing "<NAME>", as in method/templates/30, 32 and 33) - only while no other unit has a
part_standard; once one has, a placeholder is checked like any id. A1-1 also refuses a requires on the unit's own provides
item (P1: another unit's item); A1-2 reads ids beginning IF- only.
Shape (UNMEASURABLE, never a silently dropped entry): an id appearing twice among E items, units or Control Plan rows; an id
or a reference that is not a non-empty string; a part_standard that is not a mapping of provides/requires only.

NOT CLAIMED (declared): A1-7 (an IF- provider connected to its consumer as section 4.1 says - a reading of meaning);
whether a Control Plan row measures the item it names (section 4.5 limit); anything about the code (a unit that calls
another without a requires is invisible).

Verdicts and exit codes (a caller cannot read "nothing to check" as a pass by the exit code):
  0 PASS            no finding, and at least one unit has part_standard
  1 FAIL            at least one finding
  2 UNMEASURABLE    a file missing, unparsable, or of an unknown shape; git failing
  3 NOT-APPLICABLE  no finding and no unit has part_standard (the lazy rule): nothing was checked
A rule whose population is 0 on a PASS is named on the population line ("not exercised").

--receipt <path>  writes a JSON receipt made by the tool alone (schema bom-structure-receipt/1): the source (for --rev the
                  commit and tree; for the working tree and the index, HEAD and each file's blob id at HEAD), the SHA-256 and
                  git blob id of each input as read, the tool's own SHA-256 and RULE_SET (a hand-kept constant; the tool's
                  hash covers it), the counts, the population and the rules not exercised, the verdict, the exit code and the
                  UTC end time (not verifiable afterwards). The text output does not change.
--selftest        built-in fixtures through the same functions: a known-good BOM and a mutated copy per rule.
--write-fixture <name> <dir>   writes a selftest fixture's three files under <dir>/bomdd/ (for the process-core
                  qualification's E12 arms - one copy of the fixtures).

usage: python bom-structure-check.py [--root DIR] [--index | --rev COMMIT] [--receipt PATH]
       python bom-structure-check.py --selftest
       python bom-structure-check.py --write-fixture NAME DIR
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("bom-structure-check: UNMEASURABLE - PyYAML is required (pip install pyyaml)")
    sys.exit(2)

RULE_SET = "A1:1-6;A1-4:relay;P1:id;C1:a,b"
RULE_IDS = ["A1-1", "A1-2", "A1-3", "A1-4", "A1-5", "A1-6", "P1-id", "C1-a", "C1-b"]
FILES = {"ebom": "bomdd/30-ebom.yaml", "mbom": "bomdd/32-mbom.yaml", "cp": "bomdd/33-control-plan.yaml"}
PLACEHOLDER_TOKEN = "<NAME>"
EXIT = {"PASS": 0, "FAIL": 1, "UNMEASURABLE": 2, "NOT-APPLICABLE": 3}


class Unmeasurable(Exception):
    pass


# --- strict YAML ---------------------------------------------------------------------------------------------------
class _StrictLoader(yaml.SafeLoader):
    pass


def _strict_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        if key_node.tag == "tag:yaml.org,2002:merge":
            continue  # a merge key (<<) is YAML's own override, not a duplicate; SafeLoader flattens it below
        key = loader.construct_object(key_node, deep=True)
        if key in seen:
            raise yaml.YAMLError(f"duplicate key '{key}' (line {key_node.start_mark.line + 1})")
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _strict_mapping)


# --- reading -------------------------------------------------------------------------------------------------------
def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    except OSError as e:
        raise Unmeasurable(f"git cannot run: {e}")


def read_sources(root: Path, source: str, rev: str | None) -> tuple[dict, dict]:
    """Return ({key: bytes or None}, source info). A missing file is None (UNMEASURABLE later); git failing raises."""
    info: dict = {"kind": source}
    if source == "rev":
        c = _git(root, "rev-parse", "--verify", "-q", f"{rev}^{{commit}}")
        t = _git(root, "rev-parse", "--verify", "-q", f"{rev}^{{tree}}")
        if c.returncode != 0 or t.returncode != 0:
            raise Unmeasurable(f"--rev {rev} does not resolve to a commit in {root}")
        info["commit"] = c.stdout.decode().strip()
        info["tree"] = t.stdout.decode().strip()
    elif source == "index":
        if _git(root, "rev-parse", "--git-dir").returncode != 0:
            raise Unmeasurable(f"{root} is not a git repository (--index)")
    if source != "rev":
        # the version a worktree or index read sits on (R8-1-08): HEAD, and each file's blob there, so a receipt can say
        # whether what it read is what HEAD holds (null outside a git repository or before the first commit)
        h = _git(root, "rev-parse", "--verify", "-q", "HEAD")
        info["head"] = h.stdout.decode().strip() if h.returncode == 0 else None
        info["head_blobs"] = {}
        for key, rel in FILES.items():
            hb = _git(root, "rev-parse", "--verify", "-q", f"HEAD:{rel}") if info["head"] else None
            info["head_blobs"][key] = hb.stdout.decode().strip() if hb is not None and hb.returncode == 0 else None
    data: dict = {}
    for key, rel in FILES.items():
        if source == "worktree":
            p = root / rel
            data[key] = p.read_bytes() if p.is_file() else None
        else:
            spec = f":{rel}" if source == "index" else f"{info['commit']}:{rel}"
            p = _git(root, "cat-file", "-e", spec)
            if p.returncode != 0:
                data[key] = None
                continue
            b = _git(root, "cat-file", "blob", spec)
            if b.returncode != 0:
                raise Unmeasurable(f"git cannot read {spec}: {b.stderr.decode(errors='replace').strip()}")
            data[key] = b.stdout
    return data, info


def _load(key: str, raw: bytes | None):
    if raw is None:
        raise Unmeasurable(f"{FILES[key]} is missing")
    try:
        return yaml.load(raw.decode("utf-8"), Loader=_StrictLoader)
    except (yaml.YAMLError, UnicodeDecodeError) as e:
        raise Unmeasurable(f"{FILES[key]} does not parse: {str(e).splitlines()[0]}")


def _list(v, where: str) -> list:
    if v is None:
        return []
    if not isinstance(v, list):
        raise Unmeasurable(f"{where} is not a list")
    return v


def _map(v, where: str) -> dict:
    if not isinstance(v, dict):
        raise Unmeasurable(f"{where} is not a mapping")
    return v


def _ids(entries: list, where: str) -> list[dict]:
    out = []
    for i, e in enumerate(entries):
        e = _map(e, f"{where}[{i}]")
        if not isinstance(e.get("id"), str) or not e["id"]:
            raise Unmeasurable(f"{where}[{i}] has no id")
        out.append(e)
    return out


def _placeholder(i: str) -> bool:
    return PLACEHOLDER_TOKEN in i


def _strs(v, where: str) -> list[str]:
    """A list of non-empty strings (ids and refs); anything else is an unknown shape."""
    out = _list(v, where)
    if not all(isinstance(s, str) and s for s in out):
        raise Unmeasurable(f"{where} holds something other than a non-empty string")
    return list(out)


def _unique(entries: list[dict], where: str) -> None:
    seen = set()
    for e in entries:
        if e["id"] in seen:
            raise Unmeasurable(f"{where}: id {e['id']} appears twice (an earlier entry would be dropped unchecked)")
        seen.add(e["id"])


def _ps_entries(v, where: str, required: tuple[str, ...]) -> list[dict]:
    out = []
    for i, e in enumerate(_list(v, where)):
        e = _map(e, f"{where}[{i}]")
        for k in required:
            if not (isinstance(e.get(k), str) and e[k]):
                raise Unmeasurable(f"{where}[{i}].{k} is not a non-empty string")
        if "ruled_ref" in e and e["ruled_ref"] is not None and not isinstance(e["ruled_ref"], str):
            raise Unmeasurable(f"{where}[{i}].ruled_ref is not a string")
        out.append(e)
    return out


def build_model(docs: dict) -> dict:
    """Shape the three documents into the lists the rules read. An unknown shape raises Unmeasurable: a duplicate id, an id or
    a reference that is not a non-empty string, a part_standard that is not a mapping of provides/requires only (R8-1-02/04/05).
    Placeholders (an id containing <NAME>) are left out only while the BOM is still the template - no other unit has a
    part_standard; once one has, a placeholder is checked like any id (R8-1-11)."""
    ebom = _map(_map(docs["ebom"], FILES["ebom"]).get("ebom"), "ebom")
    mdoc = _map(docs["mbom"], FILES["mbom"])
    mbom = _map(mdoc.get("mbom"), "mbom")
    cpd = _map(_map(docs["cp"], FILES["cp"]).get("control_plan"), "control_plan")
    if "items" not in ebom or "manufacturing_units" not in mbom or "characteristics" not in cpd:
        raise Unmeasurable("ebom.items, mbom.manufacturing_units or control_plan.characteristics is absent")
    raw_items = _ids(_list(ebom["items"], "ebom.items"), "ebom.items")
    raw_units = _ids(_list(mbom["manufacturing_units"], "mbom.manufacturing_units"), "mbom.manufacturing_units")
    raw_rows = _ids(_list(cpd["characteristics"], "control_plan.characteristics"), "control_plan.characteristics")
    _unique(raw_items, "ebom.items")
    _unique(raw_units, "mbom.manufacturing_units")
    _unique(raw_rows, "control_plan.characteristics")
    template = not any(u.get("part_standard") is not None and not _placeholder(u["id"]) for u in raw_units)
    skip = (lambda i: _placeholder(i)) if template else (lambda i: False)
    placeholders = 0
    items = {}
    for it in raw_items:
        if skip(it["id"]):
            placeholders += 1
            continue
        lineage = it.get("lineage") or {}
        if isinstance(lineage, dict) and lineage.get("superseded_by"):
            continue
        intf = _map(it.get("interfaces") or {}, f"{it['id']}.interfaces")
        provides = _ps_entries(intf.get("provides"), f"{it['id']}.interfaces.provides", ("id",))
        items[it["id"]] = {"provides": [p["id"] for p in provides],
                           "requires": _strs(intf.get("requires"), f"{it['id']}.interfaces.requires")}
    units = {}
    for u in raw_units:
        if skip(u["id"]):
            placeholders += 1
            continue
        uid = u["id"]
        rec = {"ebom_refs": _strs(u.get("ebom_refs"), f"{uid}.ebom_refs"),
               "depends_on": _strs(u.get("depends_on"), f"{uid}.depends_on"),
               "acceptance_refs": _strs(u.get("acceptance_refs"), f"{uid}.acceptance_refs"),
               "ps": None}
        ps = u.get("part_standard")
        if ps is not None:
            ps = _map(ps, f"{uid}.part_standard")
            unknown = sorted(set(ps) - {"provides", "requires"})
            if unknown:
                raise Unmeasurable(f"{uid}.part_standard has keys other than provides/requires: {unknown}")
            rec["ps"] = {"provides": _ps_entries(ps.get("provides"), f"{uid}.part_standard.provides", ("id",)),
                         "requires": _ps_entries(ps.get("requires"), f"{uid}.part_standard.requires", ("id", "target"))}
        units[uid] = rec
    procurement = set()
    for i, p in enumerate(_list(mdoc.get("procurement"), "procurement")):
        p = _map(p, f"procurement[{i}]")
        if isinstance(p.get("package"), str):
            procurement.add(p["package"])
    rows = {}
    for r in raw_rows:
        if skip(r["id"]):
            placeholders += 1
            continue
        rows[r["id"]] = _strs(r.get("part_standard_refs"), f"{r['id']}.part_standard_refs")
    return {"items": items, "units": units, "procurement": procurement, "rows": rows, "placeholders": placeholders}


# --- the rules (one function each; each returns a list of (rule id, subject, target, why)) -------------------------
def _index(m: dict) -> dict:
    units, items = m["units"], m["items"]
    e_provides: dict[str, list[str]] = {}
    for iid, it in items.items():
        for p in it["provides"]:
            e_provides.setdefault(p, []).append(iid)
    ps_units = {uid: u for uid, u in units.items() if u["ps"]}
    provides_owner = {}
    for uid, u in ps_units.items():
        for p in u["ps"]["provides"]:
            provides_owner[p.get("id")] = uid

    def candidates(if_id):
        return [uid for uid, u in units.items() if set(u["ebom_refs"]) & set(e_provides.get(if_id, []))]

    def realisers(if_id):
        return [uid for uid in candidates(if_id) if units[uid]["ps"]
                and any(p.get("ruled_ref") == if_id for p in units[uid]["ps"]["provides"])]

    return {"e_provides": e_provides, "ps_units": ps_units, "provides_owner": provides_owner,
            "candidates": candidates, "realisers": realisers}


def _resolve(m: dict, ix: dict, uid: str, target) -> tuple[str | None, str | None]:
    """(resolved unit or '' for an external target, None) or (None, why it does not resolve)."""
    units, items = m["units"], m["items"]
    if not isinstance(target, str):
        return None, "target is not a string"
    if target.startswith("PS-"):
        owner = ix["provides_owner"].get(target)
        if owner == uid:
            return None, "the unit's own provides item (P1: a requires targets another unit's item)"
        return (owner, None) if owner else (None, "no provides item has this id")
    if target.startswith("IF-"):
        r = ix["realisers"](target)
        mine = units[uid]["ebom_refs"]
        side = (not mine) or any(target in items.get(e, {}).get("requires", []) or target in items.get(e, {}).get("provides", [])
                                 for e in mine)
        if len(r) != 1:
            return None, f"realised by {len(r)} units {r}"
        if not side:
            return None, "none of the unit's E items provides or requires it"
        return r[0], None
    if target.startswith("procurement:"):
        pkg = target[len("procurement:"):]
        return ("", None) if pkg in m["procurement"] else (None, "no top-level procurement entry has this package")
    if target.startswith("platform:"):
        return "", None
    return None, "of no known kind (PS-, IF-, procurement:, platform:)"


def rule_1(m, ix):
    out = []
    for uid, u in ix["ps_units"].items():
        for q in u["ps"]["requires"]:
            _, why = _resolve(m, ix, uid, q.get("target"))
            if why:
                out.append(("A1-1", f"{uid} {q.get('id')}", str(q.get("target")), f"does not resolve: {why}"))
    return out


def rule_2(m, ix):
    out = []
    if not ix["ps_units"]:
        return out
    for if_id in sorted(i for i in ix["e_provides"] if i.startswith("IF-")):  # §4.6: every IF- (R8-1-09)
        cands = ix["candidates"](if_id)
        if cands and not any(m["units"][c]["ps"] for c in cands):
            continue  # lazy: realised only by units without part_standard
        r = ix["realisers"](if_id)
        if len(r) != 1:
            out.append(("A1-2", if_id, ",".join(r) or "-", f"realised by {len(r)} units (exactly one required)"))
    return out


def rule_3(m, ix):
    out = []
    for uid, u in ix["ps_units"].items():
        mine = set(u["ebom_refs"])
        for p in u["ps"]["provides"]:
            rr = p.get("ruled_ref")
            if rr is not None and not (mine & set(ix["e_provides"].get(rr, []))):
                out.append(("A1-3", f"{uid} {p.get('id')}", str(rr), "ruled_ref is not an IF- provided by the unit's E items"))
    return out


def _relay_crossing(m, ix, start: str, mine: set[str]) -> str | None:
    """From a unit without ebom_refs, follow requires through units without ebom_refs; return the first target that
    crosses an E-item boundary for a unit whose E items are `mine` (None if none)."""
    units, items = m["units"], m["items"]
    seen, stack = set(), [start]
    while stack:
        w = stack.pop()
        if w in seen:
            continue
        seen.add(w)
        if not units[w]["ps"]:
            continue
        for q in units[w]["ps"]["requires"]:
            t = q.get("target")
            if not isinstance(t, str):
                continue
            if t.startswith("IF-"):
                if not any(t in items.get(e, {}).get("provides", []) or t in items.get(e, {}).get("requires", []) for e in mine):
                    return f"{w} {q.get('id')} -> {t}"
            elif t.startswith("PS-"):
                x = ix["provides_owner"].get(t)
                if x is None:
                    continue
                xe = set(units[x]["ebom_refs"])
                if xe:
                    if not (xe & mine):
                        return f"{w} {q.get('id')} -> {t} of {x}"
                else:
                    stack.append(x)
    return None


def rule_4(m, ix):
    out = []
    units = m["units"]
    for uid, u in ix["ps_units"].items():
        mine = set(u["ebom_refs"])
        if not mine:
            continue  # P4: a unit without ebom_refs may require any item
        for q in u["ps"]["requires"]:
            t = q.get("target")
            if not (isinstance(t, str) and t.startswith("PS-")):
                continue
            owner = ix["provides_owner"].get(t)
            if owner is None or owner == uid:
                continue
            oe = set(units[owner]["ebom_refs"])
            if oe:
                if not (mine & oe):
                    out.append(("A1-4", f"{uid} {q.get('id')}", f"{t} of {owner}",
                                "the units share no E item (an E-to-E boundary must be an IF-)"))
            else:
                via = _relay_crossing(m, ix, owner, mine)
                if via:
                    out.append(("A1-4", f"{uid} {q.get('id')}", f"{t} of {owner}",
                                f"relays across an E-item boundary through a unit without ebom_refs ({via})"))
    return out


def rule_5_population(m, ix) -> list[tuple[str, str, list[str]]]:
    """(consumer E item, IF-, consumer units) for each E-BOM requires the rule applies to."""
    units, items = m["units"], m["items"]
    pop = []
    for consumer, it in items.items():
        for if_id in it["requires"]:
            cu = [uid for uid, u in units.items() if consumer in u["ebom_refs"]]
            providers = set(ix["e_provides"].get(if_id, []))
            if any(providers & set(units[c]["ebom_refs"]) for c in cu):
                continue  # one unit realises both items
            if not any(units[c]["ps"] for c in cu):
                continue  # lazy
            pop.append((consumer, if_id, cu))
    return pop


def rule_5(m, ix):
    out = []
    for consumer, if_id, cu in rule_5_population(m, ix):
        has = any(q.get("target") == if_id for c in cu if m["units"][c]["ps"] for q in m["units"][c]["ps"]["requires"])
        if not has:
            out.append(("A1-5", f"E item {consumer}", if_id,
                        f"no unit realising it ({','.join(cu)}) has a requires targeting the IF-"))
    return out


def rule_6(m, ix):
    out = []
    for uid, u in ix["ps_units"].items():
        dep = set(u["depends_on"])
        if not dep:
            continue
        resolved = set()
        for q in u["ps"]["requires"]:
            r, why = _resolve(m, ix, uid, q.get("target"))
            if r:
                resolved.add(r)
        if dep != resolved:
            out.append(("A1-6", uid, ",".join(sorted(dep)),
                        f"depends_on != units its requires resolve to ({','.join(sorted(resolved)) or '-'})"))
    return out


def rule_p1(m, ix):
    out = []
    for uid, u in ix["ps_units"].items():
        seen = set()
        for kind, letter in (("provides", "P"), ("requires", "R")):
            pat = re.compile(rf"^PS-{re.escape(uid)}-{letter}\d{{2}}$")
            for e in u["ps"][kind]:
                i = e.get("id")
                if not isinstance(i, str) or not pat.match(i):
                    out.append(("P1-id", uid, str(i), f"a {kind} id is not of the form PS-{uid}-{letter}nn"))
                if i in seen:
                    out.append(("P1-id", uid, str(i), "the id is not unique within the unit"))
                seen.add(i)
    return out


def rule_c1a(m, ix):
    out = []
    for rid, refs in m["rows"].items():
        for ref in refs:
            if ref not in ix["provides_owner"]:
                out.append(("C1-a", rid, str(ref), "part_standard_refs names no existing provides item"))
    return out


def rule_c1b(m, ix):
    out = []
    for uid, u in ix["ps_units"].items():
        for p in u["ps"]["provides"]:
            pid = p.get("id")
            if not any(pid in m["rows"].get(r, []) for r in u["acceptance_refs"]):
                out.append(("C1-b", f"{uid} {pid}", ",".join(u["acceptance_refs"]) or "-",
                            "no row in the unit's acceptance_refs names the provides item"))
    return out


RULES = [rule_p1, rule_1, rule_2, rule_3, rule_4, rule_5, rule_6, rule_c1a, rule_c1b]


def check(docs: dict) -> dict:
    """The verdict on three parsed documents. Unmeasurable propagates."""
    m = build_model(docs)
    ix = _index(m)
    findings = []
    for rule in RULES:
        findings += rule(m, ix)
    ps_units = ix["ps_units"]
    population = {
        "units": len(m["units"]),
        "units_with_part_standard": len(ps_units),
        "if_items": sum(1 for i in ix["e_provides"] if i.startswith("IF-")),
        "ps_requires": sum(len(u["ps"]["requires"]) for u in ps_units.values()),
        "ps_provides": sum(len(u["ps"]["provides"]) for u in ps_units.values()),
        "ebom_requires_checked": len(rule_5_population(m, ix)),
        "cp_rows": len(m["rows"]),
        "placeholders_skipped": m["placeholders"],
    }
    if findings:
        verdict = "FAIL"
    elif not ps_units and not population["ebom_requires_checked"]:
        verdict = "NOT-APPLICABLE"
    else:
        verdict = "PASS"
    rule_pop = {"A1-1": population["ps_requires"], "A1-2": population["if_items"], "A1-3": population["ps_provides"],
                "A1-4": population["ps_requires"], "A1-5": population["ebom_requires_checked"],
                "A1-6": sum(1 for u in ps_units.values() if u["depends_on"]), "P1-id": population["ps_provides"] + population["ps_requires"],
                "C1-a": sum(len(r) for r in m["rows"].values()), "C1-b": population["ps_provides"]}
    counts = {r: sum(1 for f in findings if f[0] == r) for r in RULE_IDS}
    return {"verdict": verdict, "findings": findings, "population": population, "counts": counts,
            "not_exercised": [r for r in RULE_IDS if rule_pop[r] == 0] if ps_units else []}


def render(result: dict | None, error: str | None) -> list[str]:
    if error is not None:
        return [f"verdict: UNMEASURABLE - {error}"]
    lines = [f"[{r}] {s} -> {t}: {why}" for r, s, t, why in result["findings"]]
    p = result["population"]
    pl = " ".join(f"{k}={v}" for k, v in p.items())
    if result["not_exercised"]:
        pl += " not_exercised=" + ",".join(result["not_exercised"])
    lines.append(f"population: {pl}")
    lines.append("counts: " + " ".join(f"{r}={n}" for r, n in result["counts"].items()))
    v = result["verdict"]
    note = {"PASS": "the BOM files' structure resolves (A1-7, a row's measuring and the code are not claimed)",
            "FAIL": f"{len(result['findings'])} finding(s)",
            "NOT-APPLICABLE": "no unit has part_standard - nothing was checked (the lazy rule); this is not a pass"}[v]
    lines.append(f"verdict: {v} - {note}")
    return lines


def run(root: Path, source: str, rev: str | None) -> tuple[dict | None, str | None, dict, dict]:
    raw: dict = {k: None for k in FILES}
    info: dict = {"kind": source}
    try:
        raw, info = read_sources(root, source, rev)
        docs = {k: _load(k, raw[k]) for k in FILES}
        return check(docs), None, raw, info
    except Unmeasurable as e:
        return None, str(e), raw, info


def _blob_id(b: bytes) -> str:
    """git's blob id of these bytes (comparable with HEAD's blobs in source.head_blobs)."""
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def write_receipt(path: Path, root: Path, result: dict | None, error: str | None, raw: dict, info: dict) -> None:
    verdict = "UNMEASURABLE" if error is not None else result["verdict"]
    receipt = {
        "schema": "bom-structure-receipt/1",
        "root": str(root.resolve()),
        "source": info,
        "inputs": {k: {"path": FILES[k],
                       "sha256": hashlib.sha256(raw[k]).hexdigest() if raw.get(k) is not None else None,
                       "git_blob": _blob_id(raw[k]) if raw.get(k) is not None else None}
                   for k in FILES},
        "tool": {"sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "rule_set": RULE_SET},
        "counts": dict(result["counts"]) if result else {},
        "population": dict(result["population"]) if result else {},
        "not_exercised": list(result["not_exercised"]) if result else [],
        "verdict": verdict,
        "exit_code": EXIT[verdict],
        "error": error,
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


# --- selftest fixtures (also the qualification's, through --write-fixture) ----------------------------------------
def _good() -> dict:
    """Two E items (A provides IF-A-01; B provides IF-B-01 and requires IF-A-01), units M-A, M-B (part standards) and
    M-JIG (no ebom_refs) whose item is required by M-A. Every rule has a population."""
    ebom = {"ebom": {"items": [
        {"id": "E-A-001", "interfaces": {"provides": [{"id": "IF-A-01"}], "requires": []}},
        {"id": "E-B-001", "interfaces": {"provides": [{"id": "IF-B-01"}], "requires": ["IF-A-01"]}},
    ]}}
    mbom = {"mbom": {"manufacturing_units": [
        {"id": "M-A-001", "ebom_refs": ["E-A-001"], "acceptance_refs": ["CP-A-001"], "depends_on": ["M-JIG-001"],
         "part_standard": {"provides": [{"id": "PS-M-A-001-P01", "kind": "api", "ruled_ref": "IF-A-01"}],
                           "requires": [{"id": "PS-M-A-001-R01", "target": "PS-M-JIG-001-P01"},
                                        {"id": "PS-M-A-001-R02", "target": "procurement:pkg-x"}]}},
        {"id": "M-B-001", "ebom_refs": ["E-B-001"], "acceptance_refs": ["CP-B-001"], "depends_on": ["M-A-001"],
         "part_standard": {"provides": [{"id": "PS-M-B-001-P01", "kind": "api", "ruled_ref": "IF-B-01"}],
                           "requires": [{"id": "PS-M-B-001-R01", "target": "IF-A-01"},
                                        {"id": "PS-M-B-001-R02", "target": "platform:dotnet"}]}},
        {"id": "M-JIG-001", "ebom_refs": [], "acceptance_refs": ["CP-JIG-001"], "depends_on": [],
         "part_standard": {"provides": [{"id": "PS-M-JIG-001-P01", "kind": "process", "statement": "a helper"}],
                           "requires": []}},
    ]}, "procurement": [{"package": "pkg-x"}]}
    cp = {"control_plan": {"characteristics": [
        {"id": "CP-A-001", "part_standard_refs": ["PS-M-A-001-P01"]},
        {"id": "CP-B-001", "part_standard_refs": ["PS-M-B-001-P01"]},
        {"id": "CP-JIG-001", "part_standard_refs": ["PS-M-JIG-001-P01"]},
    ]}}
    return {"ebom": ebom, "mbom": mbom, "cp": cp}


def _unit(d, uid):
    return next(u for u in d["mbom"]["mbom"]["manufacturing_units"] if u["id"] == uid)


def _mut(fn):
    d = _good()
    fn(d)
    return d


def _relay(d):
    # M-JIG-001 now requires IF-B-01 (E-B's promise, which E-A neither provides nor requires): M-A reaching it relays
    _unit(d, "M-JIG-001")["part_standard"]["requires"] = [{"id": "PS-M-JIG-001-R01", "target": "IF-B-01"}]


def _rule4_direct(d):
    # M-A targets M-B's PS item: two units with E items sharing none (M-A also depends on M-B for A1-6 to stay equal)
    a = _unit(d, "M-A-001")
    a["part_standard"]["requires"].append({"id": "PS-M-A-001-R03", "target": "PS-M-B-001-P01"})
    a["depends_on"] = ["M-JIG-001", "M-B-001"]


def _template() -> dict:
    """The kit templates' shape: placeholder ids only (and a unit without part_standard)."""
    d = _good()
    for it in d["ebom"]["ebom"]["items"]:
        it["id"] = it["id"].replace("A-001", "<NAME>-001").replace("B-001", "<NAME>-002")
    d["mbom"]["mbom"]["manufacturing_units"] = [
        {"id": "M-<NAME>-001", "ebom_refs": ["E-<NAME>-001"], "part_standard": {"provides": [{"id": "PS-M-<NAME>-001-P01", "ruled_ref": "IF-<NAME>-01"}], "requires": []}},
        {"id": "M-HARNESS-001", "ebom_refs": [], "acceptance_refs": []}]
    d["cp"]["control_plan"]["characteristics"] = [{"id": "CP-<NAME>-001", "part_standard_refs": []}]
    return d


def _no_ps() -> dict:
    d = _good()
    for u in d["mbom"]["mbom"]["manufacturing_units"]:
        u.pop("part_standard")
    for r in d["cp"]["control_plan"]["characteristics"]:
        r["part_standard_refs"] = []
    return d


# name -> (documents, expected verdict, expected counts of findings per rule (others 0))
def fixtures() -> dict:
    return {
        "good": (_good(), "PASS", {}),
        "a1-1-ps-missing": (_mut(lambda d: _unit(d, "M-A-001")["part_standard"]["requires"][0].update(target="PS-M-JIG-001-P09")), "FAIL", {"A1-1": 1, "A1-6": 1}),
        "a1-1-procurement": (_mut(lambda d: _unit(d, "M-A-001")["part_standard"]["requires"][1].update(target="procurement:pkg-y")), "FAIL", {"A1-1": 1}),
        "a1-1-if-side": (_mut(lambda d: _unit(d, "M-A-001")["part_standard"]["requires"][1].update(target="IF-B-01")), "FAIL", {"A1-1": 1}),
        "a1-1-kind": (_mut(lambda d: _unit(d, "M-B-001")["part_standard"]["requires"][1].update(target="nuget:x")), "FAIL", {"A1-1": 1}),
        "a1-2-none": (_mut(lambda d: _unit(d, "M-B-001")["part_standard"]["provides"][0].update(ruled_ref=None, statement="x")), "FAIL", {"A1-2": 1}),
        "a1-3": (_mut(lambda d: _unit(d, "M-JIG-001")["part_standard"]["provides"][0].update(ruled_ref="IF-B-01")), "FAIL", {"A1-3": 1}),
        "a1-4-direct": (_mut(_rule4_direct), "FAIL", {"A1-4": 1}),
        "a1-4-relay": (_mut(_relay), "FAIL", {"A1-4": 1}),
        "a1-5": (_mut(lambda d: (_unit(d, "M-B-001")["part_standard"]["requires"].pop(0), _unit(d, "M-B-001").update(depends_on=[]))), "FAIL", {"A1-5": 1}),
        "a1-6": (_mut(lambda d: _unit(d, "M-B-001").update(depends_on=["M-A-001", "M-JIG-001"])), "FAIL", {"A1-6": 1}),
        "p1-form": (_mut(lambda d: (_unit(d, "M-JIG-001")["part_standard"]["provides"][0].update(id="PS-M-JIG-001-X01"),
                                    d["cp"]["control_plan"]["characteristics"][2].update(part_standard_refs=["PS-M-JIG-001-X01"]),
                                    _unit(d, "M-A-001")["part_standard"]["requires"][0].update(target="PS-M-JIG-001-X01"))), "FAIL", {"P1-id": 1}),
        "p1-unique": (_mut(lambda d: _unit(d, "M-B-001")["part_standard"]["requires"][1].update(id="PS-M-B-001-R01")), "FAIL", {"P1-id": 1}),
        "c1-a": (_mut(lambda d: d["cp"]["control_plan"]["characteristics"][0]["part_standard_refs"].append("PS-M-A-001-P07")), "FAIL", {"C1-a": 1}),
        "c1-b": (_mut(lambda d: _unit(d, "M-JIG-001").update(acceptance_refs=["CP-A-001"])), "FAIL", {"C1-b": 1}),
        "not-applicable": (_no_ps(), "NOT-APPLICABLE", {}),
        "template": (_template(), "NOT-APPLICABLE", {}),
        # R8-1-10: a requires on the unit's own provides item; R8-1-09: a provides id that is not IF- is not rule 2's
        "a1-1-self": (_mut(lambda d: (_unit(d, "M-JIG-001")["part_standard"]["requires"].append({"id": "PS-M-JIG-001-R01", "target": "PS-M-JIG-001-P01"}))), "FAIL", {"A1-1": 1}),
        "a1-2-not-if": (_mut(lambda d: d["ebom"]["ebom"]["items"][0]["interfaces"]["provides"].append({"id": "OC-1"})), "PASS", {}),
        # R8-1-11: a placeholder among real part-standard units is checked like any id (here P1 and C1-b fail on it)
        "placeholder-among-real": (_mut(lambda d: d["mbom"]["mbom"]["manufacturing_units"].append(
            {"id": "M-<NAME>-009", "ebom_refs": [], "part_standard": {"provides": [{"id": "PS-X-P01", "statement": "x"}], "requires": []}})),
            "FAIL", {"P1-id": 1, "C1-b": 1}),
        # R8-1-02, R8-1-04, R8-1-05: unknown shapes are UNMEASURABLE, never a silently dropped entry
        "dup-item": (_mut(lambda d: d["ebom"]["ebom"]["items"].append(copy.deepcopy(d["ebom"]["ebom"]["items"][1]))), "UNMEASURABLE", {}),
        "dup-unit": (_mut(lambda d: d["mbom"]["mbom"]["manufacturing_units"].insert(0, {"id": "M-A-001", "ebom_refs": []})), "UNMEASURABLE", {}),
        "dup-row": (_mut(lambda d: d["cp"]["control_plan"]["characteristics"].insert(0, {"id": "CP-A-001", "part_standard_refs": ["PS-M-A-001-P99"]})), "UNMEASURABLE", {}),
        "type-provides-no-id": (_mut(lambda d: d["ebom"]["ebom"]["items"][0]["interfaces"]["provides"].append({"refs": []})), "UNMEASURABLE", {}),
        "type-ebom-refs": (_mut(lambda d: _unit(d, "M-A-001").update(ebom_refs=[{"id": "E-A-001"}])), "UNMEASURABLE", {}),
        "type-ps-refs": (_mut(lambda d: d["cp"]["control_plan"]["characteristics"][0].update(part_standard_refs=[{"id": "x"}])), "UNMEASURABLE", {}),
        "ps-unknown-key": (_mut(lambda d: _unit(d, "M-JIG-001")["part_standard"].update(provide=[{"id": "BAD-ID"}])), "UNMEASURABLE", {}),
        # not a selftest arm (the same as a1-4-direct): the qualification's failing BOM, by --write-fixture
        "fail": (_mut(_rule4_direct), "FAIL", {"A1-4": 1}),
    }


def _dump(d: dict) -> dict:
    return {k: yaml.safe_dump(d[k], sort_keys=False, allow_unicode=True).encode("utf-8") for k in FILES}


def selftest() -> int:
    arms = []
    for name, (docs, verdict, expect) in fixtures().items():
        if name == "fail":
            continue  # a copy of a1-4-direct kept for --write-fixture; not counted twice (R8-1-12)
        raw = _dump(docs)
        try:
            res = check({k: _load(k, raw[k]) for k in FILES})
            got_v, got_c = res["verdict"], {r: n for r, n in res["counts"].items() if n}
        except Unmeasurable as e:
            got_v, got_c = "UNMEASURABLE", {}
            if verdict == "UNMEASURABLE":
                expect = got_c
                print(f"       ({name}: {e})")
        arms.append((name, got_v == verdict and got_c == expect, f"verdict {got_v} counts {got_c}"))
    # broken arms: a duplicate key, a missing file, an unknown shape -> UNMEASURABLE
    good = _dump(_good())
    for name, raw in (("broken-duplicate-key", dict(good, mbom=good["mbom"] + b"mbom: {}\n")),
                      ("broken-missing-file", dict(good, cp=None)),
                      ("broken-shape", dict(good, cp=b"control_plan: {depth_ladder: []}\n"))):
        try:
            check({k: _load(k, raw[k]) for k in FILES})
            arms.append((name, False, "no UNMEASURABLE"))
        except Unmeasurable as e:
            arms.append((name, True, f"UNMEASURABLE ({e})"))
    # a merge key (<<, as TimetableAdv's E-BOM uses) parses and is not a duplicate
    merged = dict(good, ebom=good["ebom"].replace(b"  - id: E-A-001\n", b"  - <<: {lineage: {}}\n    id: E-A-001\n", 1))
    try:
        res = check({k: _load(k, merged[k]) for k in FILES})
        arms.append(("merge-key", merged["ebom"] != good["ebom"] and res["verdict"] == "PASS", f"verdict {res['verdict']}"))
    except Unmeasurable as e:
        arms.append(("merge-key", False, f"UNMEASURABLE ({e})"))
    # the exit codes as a caller sees them: the tool run as a process on fixtures it writes (R8-1-12 - not a constant
    # compared with itself)
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="bom-structure-selftest-"))
    try:
        got = {}
        for name, want in (("good", 0), ("fail", 1), ("not-applicable", 3), ("good", 2)):
            d = tmp / f"{name}-{want}"
            write_fixture(name, d)
            if want == 2:
                (d / FILES["mbom"]).write_bytes(b"mbom: [\n")
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--root", str(d)], capture_output=True)
            got[f"{name}->{want}"] = p.returncode
        arms.append(("exit-codes", all(v == int(k.split("->")[1]) for k, v in got.items()), str(got)))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    bad = [a for a in arms if not a[1]]
    for name, ok, detail in arms:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {detail}")
    print(f"bom-structure-check selftest: {len(arms) - len(bad)}/{len(arms)} arms as expected")
    return 0 if not bad else 1


def write_fixture(name: str, dest: Path) -> int:
    fx = fixtures()
    if name not in fx:
        print(f"bom-structure-check: no fixture '{name}' ({', '.join(fx)})", file=sys.stderr)
        return 2
    raw = _dump(fx[name][0])
    for k, rel in FILES.items():
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw[k])
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="BomDD G3 A1 rules 1-6 and C1 on a product's BOM files (ECO-118)")
    ap.add_argument("--root", default=".", help="the product root (default: .)")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--index", action="store_true", help="read the three files from the git index")
    src.add_argument("--rev", help="read the three files from a commit")
    ap.add_argument("--receipt", help="write a JSON receipt to this path")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write-fixture", nargs=2, metavar=("NAME", "DIR"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.write_fixture:
        return write_fixture(a.write_fixture[0], Path(a.write_fixture[1]))
    root = Path(a.root)
    source = "index" if a.index else "rev" if a.rev else "worktree"
    result, error, raw, info = run(root, source, a.rev)
    print(f"bom-structure-check: ({source}{' ' + info.get('commit', '')[:12] if source == 'rev' else ''}) rules {RULE_SET}")
    for line in render(result, error):
        print(line)
    if a.receipt:
        write_receipt(Path(a.receipt), root, result, error, raw, info)
    return EXIT["UNMEASURABLE" if error is not None else result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
