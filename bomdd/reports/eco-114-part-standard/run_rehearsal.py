"""ECO-114 design evidence: run C1 and A1 (rehearse_part.py) on both products' real BOMs as they are, and on rehearsal-bom.yaml with one change per case.

Usage: python run_rehearsal.py <ViewPrism2 repo> <ViewTube repo> <out file>
Real BOMs by `git show` (ViewPrism2 504921a; ViewTube E/M at c214dec0, control plan at fc35bf1d). Writes one text report.
A case passes when the clause it targets is among the failures reported (other clauses may also fire; they are listed); an allowed
case passes when it gives no failure.
"""
import copy
import json
import subprocess
import sys

import yaml

import rehearse_part as rp


def show(repo, rev, path):
    return yaml.safe_load(subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout.decode("utf-8"))


def unit(b, uid):
    return next(u for u in b["mbom"]["mbom"]["manufacturing_units"] if u["id"] == uid)


def item(b, iid):
    return next(i for i in b["ebom"]["ebom"]["items"] if i["id"] == iid)


def row(b, rid):
    return next(r for r in b["cp"]["control_plan"]["characteristics"] if r["id"] == rid)


def m_eval_b(b):
    b["mbom"]["mbom"]["manufacturing_units"].append({"id": "M-EVAL-B", "ebom_refs": ["E-EVAL-002"], "acceptance_refs": ["CP-EVAL-001"],
        "part_standard": {"provides": [{"id": "PS-M-EVAL-B-P01", "kind": "api", "ruled_ref": "IF-EVAL-002-02"}], "requires": []}})
    unit(b, "M-EVAL-002")["part_standard"]["provides"].append({"id": "PS-M-EVAL-002-P02", "kind": "api", "ruled_ref": "IF-EVAL-002-02"})
    item(b, "E-EVAL-002")["interfaces"]["provides"].append({"id": "IF-EVAL-002-02", "refs": ["OC-1"]})
    row(b, "CP-EVAL-001")["part_standard_refs"] += ["PS-M-EVAL-B-P01", "PS-M-EVAL-002-P02"]


def harness(b, provides=False):
    u = {"id": "M-HARNESS-X", "acceptance_refs": ["CP-NFR-001"],
         "part_standard": {"provides": [], "requires": [{"id": "PS-M-HARNESS-X-R01", "target": "PS-M-EVAL-002-P01"}]}}
    if provides:
        u["part_standard"]["provides"].append({"id": "PS-M-HARNESS-X-P01", "kind": "api", "statement": "a helper"})
        row(b, "CP-NFR-001")["part_standard_refs"] = ["PS-M-HARNESS-X-P01"]
    b["mbom"]["mbom"]["manufacturing_units"].append(u)


def relay(b, target):
    harness(b, provides=True)
    unit(b, "M-HARNESS-X")["part_standard"]["requires"][0]["target"] = target
    unit(b, "M-GRAPH-003")["part_standard"]["requires"].append({"id": "PS-M-GRAPH-003-R03", "target": "PS-M-HARNESS-X-P01"})
    unit(b, "M-GRAPH-003")["depends_on"].append("M-HARNESS-X")


def relay_chain(b):
    harness(b, provides=True)
    b["mbom"]["mbom"]["manufacturing_units"].append({"id": "M-HARNESS-Z", "acceptance_refs": ["CP-NFR-001"], "part_standard": {
        "provides": [{"id": "PS-M-HARNESS-Z-P01", "kind": "api", "statement": "a wrapper"}],
        "requires": [{"id": "PS-M-HARNESS-Z-R01", "target": "PS-M-HARNESS-X-P01"}]}})
    row(b, "CP-NFR-001")["part_standard_refs"].append("PS-M-HARNESS-Z-P01")
    unit(b, "M-GRAPH-003")["part_standard"]["requires"].append({"id": "PS-M-GRAPH-003-R03", "target": "PS-M-HARNESS-Z-P01"})
    unit(b, "M-GRAPH-003")["depends_on"].append("M-HARNESS-Z")


def both_items(b):
    b["ebom"]["ebom"]["items"].append({"id": "E-HASH-006", "depends_on": ["E-DOMAIN-001"], "interfaces": {"requires": ["IF-DOMAIN-001-01"]}})


def graph_edges_only(b):
    item(b, "E-GRAPH-003")["depends_on"] = ["E-DOMAIN-001"]
    item(b, "E-EVAL-002")["graph_edges"] = {"owner": "E-EVAL-002", "consumers": ["E-GRAPH-003"]}


# positive cases (None): the change is allowed and gives no failure
CASES = [
    (None, "a harness with no ebom_refs requires an E-item unit's PS- entry", lambda b: harness(b)),
    (None, "a provider connected only through graph_edges.consumers", graph_edges_only),
    (None, "one unit realizes both the providing and the consuming item (A1 5's exemption)", both_items),
    (None, "a procurement: target with a procurement entry",
     lambda b: unit(b, "M-EVAL-002")["part_standard"]["requires"].append(
         {"id": "PS-M-EVAL-002-R02", "target": "procurement:Microsoft.Extensions.DependencyInjection"})),
    ("A1-4", "a unit with no ebom_refs that takes an E-item unit's PS- is required by an E-item unit (relay)",
     lambda b: relay(b, "PS-M-EVAL-002-P01")),
    ("A1-4", "a unit with no ebom_refs that takes an IF- is required by an E-item unit (relay)", lambda b: relay(b, "IF-EVAL-002-01")),
    ("A1-4", "a relay through two units with no ebom_refs", relay_chain),
    ("A1-1", "a target that names a requires entry (no provides entry)",
     lambda b: unit(b, "M-GRAPH-003")["part_standard"]["requires"][1].update(target="PS-M-EVAL-002-R01")),
    ("A1-3", "a unit with no ebom_refs carries a ruled_ref",
     lambda b: b["mbom"]["mbom"]["manufacturing_units"].append({"id": "M-INFRA-Y", "acceptance_refs": ["CP-NFR-001"],
        "part_standard": {"provides": [{"id": "PS-M-INFRA-Y-P01", "kind": "api", "ruled_ref": "IF-EVAL-002-01"}], "requires": []}})),
    ("P1", "two entries of one unit with the same ID",
     lambda b: unit(b, "M-EVAL-002")["part_standard"]["requires"].append({"id": "PS-M-EVAL-002-P01", "target": "platform:net10.0"})),
    ("C1", "a part_standard_refs naming no provides entry", lambda b: row(b, "CP-NFR-001").update(part_standard_refs=["PS-NONE-P01"])),
    ("C1", "a provides entry listed by no row", lambda b: row(b, "CP-EVAL-001").update(part_standard_refs=[])),
    ("C1", "listed only by a row outside the unit's acceptance_refs",
     lambda b: (row(b, "CP-EVAL-001").update(part_standard_refs=[]), row(b, "CP-GRAPH-002")["part_standard_refs"].append("PS-M-EVAL-002-P01"))),
    ("A1-1", "a requires target naming no entry", lambda b: unit(b, "M-GRAPH-003")["part_standard"]["requires"][1].update(target="IF-NONE-01")),
    ("A1-2", "an IF- realized by no unit (nothing requires it)",
     lambda b: item(b, "E-EVAL-002")["interfaces"]["provides"].append({"id": "IF-EVAL-002-02", "refs": ["OC-1"]})),
    ("A1-2", "an IF- realized by two units (nothing requires it)", m_eval_b),
    ("A1-3", "a ruled_ref naming no IF-", lambda b: unit(b, "M-GRAPH-003")["part_standard"]["provides"][0].update(ruled_ref="IF-NONE-01")),
    ("A1-4", "M-GRAPH-003 requires a PS- entry of M-EVAL-002",
     lambda b: unit(b, "M-GRAPH-003")["part_standard"]["requires"].append({"id": "PS-M-GRAPH-003-R03", "target": "PS-M-EVAL-002-P01"})),
    ("A1-5", "E-GRAPH-003's interfaces.requires with no unit requires",
     lambda b: unit(b, "M-GRAPH-003")["part_standard"]["requires"].pop(1)),
    ("A1-6", "M-GRAPH-003's depends_on naming a unit it does not require", lambda b: unit(b, "M-GRAPH-003")["depends_on"].append("M-SLN-000")),
    ("A1-1", "a procurement: target with no procurement entry",
     lambda b: unit(b, "M-EVAL-002")["part_standard"]["requires"].append({"id": "PS-M-EVAL-002-R02", "target": "procurement:Foo"})),
    ("A1-1", "an IF- required by a unit whose E items do not require it",
     lambda b: unit(b, "M-SLN-000")["part_standard"]["requires"].append({"id": "PS-M-SLN-000-R02", "target": "IF-EVAL-002-01"})),
    ("A1-7", "an interfaces.requires whose provider is not connected", lambda b: item(b, "E-GRAPH-003").update(depends_on=["E-DOMAIN-001"])),
]


def main():
    vp2, vt, path = sys.argv[1:4]
    out = []
    vt_head = subprocess.run(["git", "-C", vt, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    for name, docs in (("ViewPrism2 at 504921a, as it is", [show(vp2, "504921a", f"bomdd/{f}") for f in ("30-ebom.yaml", "32-mbom.yaml", "33-control-plan.yaml")]),
                       (f"ViewTube E/M at {vt_head[:8]}, control plan at fc35bf1d, as it is",
                        [show(vt, "HEAD", "bomdd/30-ebom.yaml"), show(vt, "HEAD", "bomdd/32-mbom.yaml"), show(vt, "fc35bf1d", "bomdd/33-control-plan.yaml")])):
        f = rp.check(*docs)
        out.append(f"== {name}: {len(f)} failures {f[:10]}")
    base = yaml.safe_load(open("rehearsal-bom.yaml", encoding="utf-8"))
    f0 = rp.check(base["ebom"], base["mbom"], base["cp"])
    out.append(f"== rehearsal-bom.yaml unchanged: {len(f0)} failures {f0}")
    again = rp.check(base["ebom"], base["mbom"], base["cp"])
    out.append(f"   run twice, identical: {json.dumps(f0) == json.dumps(again)}")
    for clause, what, change in CASES:
        b = copy.deepcopy(base)
        change(b)
        f = rp.check(b["ebom"], b["mbom"], b["cp"])
        got = sorted({c for c, _, _ in f})
        if clause is None:
            out.append(f"== allowed — {what}: {'NO FAILURE' if not f else 'MISSED'}; clauses {got}")
        else:
            out.append(f"== {clause} — {what}: {'OWN CLAUSE REPORTED' if clause in got else 'MISSED'}; clauses {got}")
        out.extend(f"   - {c} {e}: {t}" for c, e, t in f)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
