"""ECO-114 acceptance V1 (the text, clause by clause) and V2's field-name check (the rehearsal reads the manufactured templates' field names), read-only.

Usage (from a tree's root):
    python -B check_v1_v2.py <out file>               # V1 and V2-fields on the tree; last lines "V1 PASS|FAIL", "V2-fields PASS|FAIL"
    python -B check_v1_v2.py --mutations <out file>   # for every clause: remove it from its file in memory and expect V1 to FAIL for that rule
V1 (repaired after inspection r1's IA-03): each rule's clauses (the order's section 1) must be present in its canonical text, and each copy must hold
its canonical text's clauses. Texts are compared with line breaks and their indentation removed. A missing heading or path is a FAIL, not a crash.
"""
import re
import sys

import yaml

PB = "method/bomdd-playbook-v1.md"
T30, T32, T33 = "method/templates/30-ebom.yaml", "method/templates/32-mbom.yaml", "method/templates/33-control-plan.yaml"
P3 = "method/prompts/phase3-design.md"

HEAD = {
    "P2": ("**外向きの約束(candidate・ECO-114)**", "- **迷った境界の最小 BDR"),
    "部品規格": ("**部品規格(candidate・ECO-114)**", "### 4.6"),
    "O": ("**Phase 3 の順序と担当(candidate・ECO-114)**", "**ゲート G3"),
    "G3": ("**ゲート G3", "### 4.7"),
}

# (rule, where, clause): where = a canonical section key above, or a copy ("prompt", "table9", "t32")
CLAUSES = [
    ("P2", "P2", "別の E 品目、または製品の外の利用者が当てにするもの"),
    ("P2", "P2", "E 品目の境界だけで決まり、製造単位の分け方では決まらない"),
    ("P2", "P2", "`interfaces.provides` に置く `IF-<ITEM>-NN`"),
    ("P2", "P2", "`refs`(境界やその振る舞いを述べる仕様 §2 / §3 の ID"),
    ("P2", "P2", "`boundary`(それらの ID が述べていないことだけ"),
    ("P2", "P2", "参照した ID が述べていることを言い直さない"),
    ("P2", "P2", "`interfaces.requires` にその `IF-` を挙げ"),
    ("P2", "P2", "`graph_edges.consumers` が利用側を挙げる"),
    ("P2", "P2", "`IF-` として繰り返さない"),
    ("P2", "P2", "どの製造単位も実現しない E 品目"),
    ("P2", "P2", "導出層は `IF-` を足さない・落とさない・言い換えない"),
    ("P1", "部品規格", "`provides` と `requires` の 2 つの一覧"),
    ("P1", "部品規格", "`provides` は `PS-<UNIT>-Pnn`"),   # the bare ID form occurs twice in the section; a first mutation run missed it
    ("P1", "部品規格", "`requires` は `PS-<UNIT>-Rnn`"),
    ("P1", "部品規格", "`api` | `data` | `event` | `file` | `process`"),
    ("P1", "部品規格", "`ruled_ref: IF-…`"),
    ("P1", "部品規格", "`form`(裁定が抽象的にしか述べていないとき"),
    ("P1", "部品規格", "`requires` の項目は `id` と `target` を持つ"),
    ("P1", "部品規格", "`procurement:<package>`・`platform:<name>`"),
    ("P1", "部品規格", "`display_contract.refs` に残し"),
    ("P1", "部品規格", "単位をまたいで共通の書き方"),
    ("P3", "部品規格", "それは上の「人へ戻す 3 種」の「新しい約束」で、人へ戻す"),
    ("P3", "部品規格", "約束を変えない"),
    ("P4", "部品規格", "`statement` 付きの `provides` として書く"),
    ("P4", "部品規格", "`IF-` を実現しない"),
    ("P4", "部品規格", "E 品目の間の境界を中継しない"),
    ("P4", "部品規格", "P4 の拡張: これは上の 4 分類を部品規格に広げたもの"),
    ("C1", "部品規格", "`part_standard_refs` に挙げ"),
    ("C1", "部品規格", "免除はない"),
    ("C1", "部品規格", "その行の `known_limits` に項目の ID を付けて書く"),
    ("C1", "部品規格", "実在する `provides` の項目を指す"),
    ("C1", "部品規格", "行がその項目を**測っているか**は意味の判断"),
    ("A2", "部品規格", "`mbom.assembly.acceptance_refs` に、複数の単位をまとめて測る Control Plan の行を挙げる"),
    ("A2", "部品規格", "空にするなら `assembly_reason` を書く"),
    ("A2", "部品規格", "固定オラクル(41)は Control Plan の行ではなく"),
    ("O1", "O", "1. E-BOM — 部品分けと外向きの約束"),
    ("O1", "O", "4. M-BOM — 製造単位とその部品規格"),
    ("O1", "O", "5. Control Plan — 統括 AI"),
    ("O1", "O", "6. Routing と作業指示書 — 統括 AI"),
    ("O1", "O", "固定オラクルと探索プローブは従来どおり設計者側"),
    ("O2", "O", "手順 4 で各単位の項目がそろっていること"),
    ("O2", "O", "手順 5 で §4.5 の C1 を確かめる"),
    ("O4", "O", "Phase 3 の手順 1–3 と固定オラクル・探索プローブ"),
    ("O4", "O", "Phase 3 の手順 4–6、ECO での導出のやり直し"),
    ("O4", "O", "担当は工程の手順でなく層で決まる"),
    ("O4", "O", "見てよいもの・見てはならないものは設計者と同じ"),
    ("O3", "G3", "単独に受け入れられるか"),
    ("A1", "G3", "節 1・3・4・6 は `part_standard` を持つ単位に"),
    ("A1", "G3", "`platform:<name>` は書かれたとおりに受ける"),
    ("A1", "G3", "ちょうど 1 つの単位が実現する"),
    ("A1", "G3", "その単位の E 品目のどれかの `IF-` を指す"),
    ("A1", "G3", "§4.5 P4: 中継しない"),
    ("A1", "G3", "1 つの単位が両方の品目を実現する場合を除く"),
    ("A1", "G3", "空でなければ、その `requires` が解決する単位の集合に等しい"),
    ("A1", "G3", "提供側が §4.1 のとおり利用側とつながっている"),
    # copies
    ("O1", "prompt", "手順 1〜3 = 設計者"),
    ("O1", "prompt", "手順 4〜6 = 統括 AI"),
    ("O1", "prompt", "固定オラクルと探索プローブ = 設計者側"),
    ("O3", "prompt", "単独に受け入れられるか"),
    ("A1", "prompt", "A1 構造の解決"),
    ("O4", "table9", "Phase 3 の手順 1–3 と固定オラクル・探索プローブ"),
    ("O4", "table9", "Phase 3 の手順 4–6、ECO での導出のやり直し"),
    ("P4", "t32", "4 分類を部品規格に広げ"),
    ("P4", "t32", "P4 の拡張の写し"),
]


def norm(text):
    return re.sub(r"[ \t]*\n[ \t#]*", "", text)


def section(pb, key):
    start, end = HEAD[key]
    i = pb.find(start)
    j = pb.find(end, i + 1) if i >= 0 else -1
    return pb[i:j] if i >= 0 and j > i else ""


def texts(files):
    pb = files[PB]
    rows = [l for l in pb.splitlines() if l.startswith("| 設計者(ユーザー+設計AI)") or l.startswith("| 統括 AI")]
    t = {k: section(pb, k) for k in HEAD}
    t["prompt"] = files[P3]
    t["table9"] = "\n".join(rows)
    t["t32"] = files[T32]
    return t


def v1(files, out):
    pb, t30, t32, t33, p3 = (files[p] for p in (PB, T30, T32, T33, P3))
    failed = set()

    def check(rule, name, cond):
        if not cond:
            failed.add(rule)
        out.append(f"[{'PASS' if cond else 'FAIL'}] V1 {rule} {name}")

    for key, (head, _) in HEAD.items():
        check(key, f"canonical heading {head!r} once", pb.count(head) == 1)
    t = texts(files)
    for rule, where, clause in CLAUSES:
        check(rule, f"{where}: {clause}", norm(clause) in norm(t[where]))
    # O1 copy: the prompt's step order equals the canonical order
    order_pb = re.findall(r"^(\d)\. (E-BOM|FMEA|K-BOM|M-BOM|Control Plan|Routing)", t["O"], re.M)
    order_p3 = re.findall(r"^(\d)\. \*\*(E-BOM|FMEA|K-BOM|M-BOM|Control Plan|Routing)", p3, re.M)
    check("O1", "the prompt's step order equals the canonical order", order_pb == order_p3 and [n for n, _ in order_pb] == list("123456"))
    # O4 copy: the 統括 AI row has the designer row's may-see / must-not-see
    rows = t["table9"].splitlines()
    check("O4", "§9: two rows, the orchestrating AI's columns 3-4 equal the designer's",
          len(rows) == 2 and [c.strip() for c in rows[0].split("|")[3:5]] == [c.strip() for c in rows[1].split("|")[3:5]])
    for path, text, needles in ((T30, t30, ["interfaces:", "IF-<NAME>-01", "refs:", "boundary:", "playbook §4.1「外向きの約束」"]),
                                (T32, t32, ["part_standard:", "provides:", "requires:", "ruled_ref:", "form:", "target:", "playbook §4.5「部品規格」",
                                            "assembly:", "assembly_reason:", "ebom_ref:", "playbook §4.6"]),
                                (T33, t33, ["part_standard_refs:", "playbook §4.5「部品規格」C1"])):
        missing = [n for n in needles if n not in text]
        check("fields", f"{path} carries the fields and the place comments{(' — missing ' + str(missing)) if missing else ''}", not missing)
    return failed


def v2_fields(files, out):
    ok = True
    try:
        d30, d32, d33 = (yaml.safe_load(files[p]) for p in (T30, T32, T33))
        item, unit, row = d30["ebom"]["items"][0], d32["mbom"]["manufacturing_units"][0], d33["control_plan"]["characteristics"][0]
    except Exception:
        out.append("[FAIL] V2-fields the templates parse and have their first item / unit / row")
        return False
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
            cond = bool(probe())
        except (KeyError, IndexError, TypeError):
            cond = False
        ok &= cond
        out.append(f"[{'PASS' if cond else 'FAIL'}] V2-fields {name}")
    return ok


def load():
    return {p: open(p, encoding="utf-8").read() for p in (PB, T30, T32, T33, P3)}


def mutations(path):
    files, out, missed = load(), [], 0
    targets = {"P2": PB, "部品規格": PB, "O": PB, "G3": PB, "prompt": P3, "table9": PB, "t32": T32}
    for rule, where, clause in CLAUSES:
        f = targets[where]
        mutated = dict(files)
        base = files[f]
        if where in HEAD:
            sec = section(base, where)
            mutated[f] = base.replace(sec, norm_remove(sec, clause)) if sec else base
        elif where == "table9":
            mutated[f] = "\n".join(norm_remove(l, clause) if (l.startswith("| 設計者") or l.startswith("| 統括 AI")) else l for l in base.splitlines())
        else:
            mutated[f] = norm_remove(base, clause)
        changed = mutated[f] != base
        failed = v1(mutated, [])
        hit = changed and rule in failed
        missed += not hit
        out.append(f"{'CAUGHT' if hit else 'MISSED'} {rule} {where}: {clause}{'' if changed else ' (clause not found to remove)'}; V1 failed rules {sorted(failed)}")
    out.append(f"mutations: {len(CLAUSES)}; caught: {len(CLAUSES) - missed}; missed: {missed}")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")


def norm_remove(text, clause):
    """Remove the clause's first occurrence even when the text breaks it across lines (the same normalisation the check uses)."""
    pattern = r"[ \t]*\n?[ \t#]*".join(re.escape(ch) for ch in norm(clause))
    return re.sub(pattern, "", text, count=1)


def main():
    if sys.argv[1] == "--mutations":
        mutations(sys.argv[2])
        return
    files, out = load(), []
    failed = v1(files, out)
    ok2 = v2_fields(files, out)
    out.append(f"V1 {'PASS' if not failed else 'FAIL'}" + (f" (rules {sorted(failed)})" if failed else ""))
    out.append(f"V2-fields {'PASS' if ok2 else 'FAIL'}")
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
