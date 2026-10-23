"""ECO-114 acceptance V1 (the text) and V2's field-name check (the rehearsal reads the manufactured templates' field names), read-only.

Usage (from the repository root): python -B bomdd/reports/eco-114-part-standard/manufacture/check_v1_v2.py <out file>
Prints nothing; writes one report whose last line is "V1 PASS"/"V1 FAIL" and "V2-fields PASS"/"V2-fields FAIL". Each check names what it read.
"""
import re
import sys

import yaml

PB = "method/bomdd-playbook-v1.md"
T30, T32, T33 = "method/templates/30-ebom.yaml", "method/templates/32-mbom.yaml", "method/templates/33-control-plan.yaml"
P3 = "method/prompts/phase3-design.md"


def read(p):
    return open(p, encoding="utf-8").read()


def main():
    out, ok = [], {"V1": True, "V2-fields": True}

    def check(group, name, cond, detail=""):
        ok[group] &= bool(cond)
        out.append(f"[{'PASS' if cond else 'FAIL'}] {group} {name}{(' — ' + detail) if detail else ''}")

    pb, t30, t32, t33, p3 = (read(p) for p in (PB, T30, T32, T33, P3))
    # canonical places, once each
    for head, rules in (("**外向きの約束(candidate・ECO-114)**", "P2"), ("**部品規格(candidate・ECO-114)**", "P1 P3 P4 C1 A2"),
                        ("**Phase 3 の順序と担当(candidate・ECO-114)**", "O1 O2 O4"), ("**A1 構造の解決**", "O3 A1")):
        check("V1", f"canonical place for {rules} appears once in the playbook", pb.count(head) == 1, f"{head!r} x{pb.count(head)}")
    for label in ("**P1 形**", "**P3 約束を足す・変える**", "**P4 導出に残るもの**", "**C1 行が規格を検査する**", "**A2 単位をまとめて測る行**"):
        check("V1", f"§4.5 部品規格 states {label}", pb.count(label) == 1)
    a1 = pb[pb.index("**A1 構造の解決**"):] if "**A1 構造の解決**" in pb else ""   # a missing heading is a FAIL, not a crash
    check("V1", "G3 states A1's seven clauses", a1 and all(f"\n{n}. " in a1[:4000] for n in range(1, 8)))
    check("V1", "G3's question gains the unit-alone question", "単独に受け入れられるか" in pb)
    check("V1", "§9 roles table carries O4's split", "| 設計者(ユーザー+設計AI) | Phase 0–2, Phase 3 の手順 1–3" in pb and "| 統括 AI | M-BOM・Control Plan・Routing を導出するとき" in pb)
    check("V1", "§4.5 M-BOM line names part_standard", "製造単位ごとに `part_standard`" in pb)
    # copies match the canonical text
    start = pb.find("**Phase 3 の順序と担当(candidate・ECO-114)**")
    end = pb.find("**製造成立性**", start) if start >= 0 else -1
    section = pb[start:end] if start >= 0 and end > start else ""   # only §4.6's item (a first run matched a "3. K-BOM" elsewhere — an instrument defect)
    order_pb = re.findall(r"^(\d)\. (E-BOM|FMEA と沈黙掃討|K-BOM|M-BOM|Control Plan|Routing と作業指示書)", section, re.M)
    order_p3 = re.findall(r"^(\d)\. \*\*(E-BOM|FMEA|K-BOM|M-BOM|Control Plan|Routing)", p3, re.M)
    check("V1", "the prompt's step order equals §4.6's (copy)", [n for n, _ in order_pb] == [n for n, _ in order_p3] == list("123456")
          and [s.split()[0] for _, s in order_pb] == [s.split()[0] for _, s in order_p3], f"playbook {order_pb} / prompt {order_p3}")
    check("V1", "the prompt names the owners (設計者 1-3, 統括 AI 4-6) and points at §4.6",
          "手順 1〜3 = 設計者" in p3 and "手順 4〜6 = 統括 AI" in p3 and "playbook §4.6「Phase 3 の順序と担当」" in p3)
    check("V1", "the prompt's G3 runs A1 and C1 first and asks the unit-alone question", "A1 構造の解決" in p3 and "単独に受け入れられるか" in p3)
    check("V1", "32's four-class comment carries P4's extension (copy)", "P4 の拡張の写し" in t32 and "interface_contract の扱いを" in t32)
    # template fields with comments naming the canonical place
    for path, text, needles in ((T30, t30, ["interfaces:", "IF-<NAME>-01", "refs:", "boundary:", "playbook §4.1「外向きの約束」"]),
                                (T32, t32, ["part_standard:", "provides:", "requires:", "ruled_ref:", "form:", "target:", "playbook §4.5「部品規格」",
                                            "assembly:", "assembly_reason:", "ebom_ref:", "playbook §4.6"]),
                                (T33, t33, ["part_standard_refs:", "playbook §4.5「部品規格」C1"])):
        missing = [n for n in needles if n not in text]
        check("V1", f"{path} carries the fields and the place comments", not missing, f"missing {missing}" if missing else "")
    # V2's field names: the templates parse and the paths the rehearsal reads exist in them
    d30, d32, d33 = (yaml.safe_load(t) for t in (t30, t32, t33))
    item = d30["ebom"]["items"][0]
    unit = d32["mbom"]["manufacturing_units"][0]
    row = d33["control_plan"]["characteristics"][0]
    probes = {
        "30 items[0].interfaces.provides[0].{id,refs,boundary}": lambda: {"id", "refs", "boundary"} <= set(item["interfaces"]["provides"][0]),
        "30 items[0].interfaces.requires": lambda: "requires" in item["interfaces"],
        "32 units[0].part_standard.provides[0].{id,kind,ruled_ref,form}": lambda: {"id", "kind", "ruled_ref", "form"} <= set(unit["part_standard"]["provides"][0]),
        "32 units[0].part_standard.requires[0].{id,target}": lambda: {"id", "target"} <= set(unit["part_standard"]["requires"][0]),
        "32 mbom.assembly.{acceptance_refs,assembly_reason}": lambda: {"acceptance_refs", "assembly_reason"} <= set(d32["mbom"]["assembly"]),
        "32 fmea[0].ebom_ref": lambda: "ebom_ref" in d32["fmea"][0],
        "32 procurement at the top level": lambda: "procurement" in d32,
        "33 characteristics[0].part_standard_refs": lambda: "part_standard_refs" in row,
    }
    for name, probe in probes.items():
        try:
            cond = probe()
        except (KeyError, IndexError, TypeError):   # a missing path is a FAIL, not a crash
            cond = False
        check("V2-fields", name, cond)
    rehearsal = read("bomdd/reports/eco-114-part-standard/rehearse_part.py")
    used = ["\"part_standard\"", "\"provides\"", "\"requires\"", "\"target\"", "\"ruled_ref\"", "\"interfaces\"", "\"part_standard_refs\"",
            "\"acceptance_refs\"", "\"procurement\"", "\"depends_on\"", "\"graph_edges\"", "\"consumers\"", "\"ebom_refs\""]
    check("V2-fields", "the rehearsal script reads exactly these field names", all(u in rehearsal for u in used))
    out.append(f"V1 {'PASS' if ok['V1'] else 'FAIL'}")
    out.append(f"V2-fields {'PASS' if ok['V2-fields'] else 'FAIL'}")
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
