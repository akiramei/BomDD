#!/usr/bin/env python3
"""ECO-115 acceptance V1 (the text) and V2 (the decision reads only its inputs) on a BomDD tree. Read only.

  python -B check_v1_v2.py <BomDD root> <ViewPrism2> <MoviePad-Remake> <scratch directory>

V1, from the order's section 3: playbook 4.4's item "前進の判定" states each of I0-I4 and D0-D5 once (as a bold label in the item);
section 1's flow and 6.1 carry one line each naming it; the on_fail sentence of 4.4's per-ID-table item names it and no longer lists a
value outside I2; each template field of M1 carries a comment naming it; I2's values appear in the template comments as in I2.
V2: (a) every field the rehearsal scripts read is in the manufactured templates (parsed, by key path); (b) the rehearsals re-run on the
real records at their fixed commits and on the synthetic cases give the stored outputs byte for byte.
Prints one line per check and a summary; exit 0 only when every check passes.
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml

root, vp2, mpr, scratch = (Path(a).resolve() for a in sys.argv[1:5])
HERE = root / "bomdd/reports/eco-115-advance-decision"
NAME = "前進の判定"
results = []


def check(label, ok, detail=""):
    results.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'} {label}{(' - ' + detail) if detail and not ok else ''}")


def read(rel):
    p = root / rel
    return p.read_text(encoding="utf-8") if p.is_file() else ""


# ---- V1: the playbook
book = read("method/bomdd-playbook-v1.md")
lines = book.splitlines()


def section(start, stop):
    out, inside = [], False
    for line in lines:
        if line.startswith(start):
            inside = True
            continue
        if inside and re.match(stop, line):
            break
        if inside:
            out.append(line)
    return out


s44 = section("### 4.4 ", r"^### ")
item, inside = [], False
for line in s44:
    if line.startswith(f"- **{NAME}"):
        inside = True
    elif inside and line.startswith("- "):
        break
    if inside:
        item.append(line)
check("V1 4.4 has the item 前進の判定", item, "no top-level bullet starting '- **前進の判定' in 4.4")
text = "\n".join(item)
for rid in ["I0", "I1", "I2", "I3a", "I3b", "I4", "D0", "D1", "D2", "D3", "D4", "D5"]:
    n = len(re.findall(rf"\*\*{rid}[ (（]", text))
    check(f"V1 {rid} stated once in the item", n == 1, f"{n} labels")
# Clause by clause (ECO-114's inspection r1, IA-03: a label check passes while a rule's content is missing). Each rule's segment runs from its
# label to the next label (D5 to the limits bullet); line breaks with their indent are removed before matching. A token is a clause of the order's
# section 1 as the item states it — identifiers and values verbatim, the rest in the item's words. Presence only: whether the item's words say
# what the order's clause says is the independent inspection's (V3), not this check's.
CLAUSES = {
    "I0": ["Phase 4 と Phase 5 の間", "固定オラクルと golden を走らせる前", "**Phase 5 へ進むか**", "自動の部分だけ", "Phase 5 に残り", "(D4)"],
    "I1": ["`- 対象 BOM tag/commit: <revision>`", "Phase 3 の手順 6", "`frozen_commit`", "**発行されたとおりに**", "`work_order_ref`", "`mbom_ref`",
           "`control_plan_ref`", "比べるだけで読まない", "D0〜D4 が作業指示書から読むのはその 1 行だけ", "`- 前進の判定の上限: holds <n>, decisions <m>`",
           "作業の最初の発行", "`work_ref`", "`routes_done`", "`row_changes`", "`acceptance_refs`", "`mbom.assembly.acceptance_refs`",
           "`assembly_reason`", "`check_mapping`", "`id`・`status`・`approver`・`on_fail`", "`source: decision`", "`identity`",
           "納品の M-BOM と Control Plan の写し", "祖先関係", "工場の報告と自己受入", "`when`・`depth`・`verifies`・`characteristic`・`oracle`・`evidence_output_ref`",
           "ECO-088", "`when` は別の機会に"],
    "I2": ["上限の行(D5)", "1 以上 999 以下の 10 進の整数", "`xunit-v3`", "`line`", "`outcome` と `row`", "持ち主でない検査", "`commit` と `tree`", "40 桁の 16 進", "バッククォートは値に含めない"],
    "I3a": ["上限の行が I2 の内", "git が使える", "`delivered` が I2 の内", "その `commit` の木", "納品のコミットとは別のコミット", "`frozen_commit` を持つ", "1 本あり",
            "その値が `frozen_commit` に解決する", "`mbom_ref` と `control_plan_ref` が `frozen_commit` を名指す", "固定が発行に先立つ",
            "バイト単位で等しい", "古い BOM へ戻されたタグを捕まえる", "納品のコミットの祖先である", "読める", "写しの無い納品は等しくない",
            "一意", "空でない `acceptance_refs`", "`assembly_reason`", "少なくとも 1 行", "`retired` でない", "I1 の 1〜2 の値はどれも I2 の内",
            "`input-defect`", "振り分け先(D2)", "何も走らせない"],
    "I3b": ["ちょうど 1 つの判定の記録", "数えない行を名指す判定の記録は無い", "`cp_ref`", "`evidence_path`", "`evidence_sha256`", "`format`", "`observed_at`",
            "`check_mapping` が挙げる形式", "`input-defect`", "行の区分は計算しない"],
    "I4": ["`source: decision`", "数える行ごとに 1 つ", "`result`(D4)", "`identity`", "記録には書かない", "同じ証拠ファイル", "`evidence_sha256: none`",
           "測定系復旧", "`source: phase5`", "1 度だけ判定する"],
    "D0": ["統括 AI", "工場とは別の文脈", "`delivered` を固める", "**数える行**", "`automated` を含む", "自動の部分だけ", "`delivered` に走らせる",
           "I3b・D1・D2", "`advance_decision`", "決めた D1 の番号", "決めなかった行", "`assembly` にも無い行"],
    "D1": ["最初に当てはまるもの", "読めない", "検査を 1 つも持たない", "`outcomes` に無い結果語", "sha256 が記録と違う", "2 つ以上見つける",
           "`delivered` 以外を見つける", "数える行のどれも持ち主でない検査", "`violation`", "`skipped` か `not-run`", "`no-check`",
           "`passed` に対応し、`failed` に対応するものが無い"],
    "D2": ["`advances`", "`holds`", "人の部分を持つ", "`on_fail`", "`violation` → product-fix", "`unmeasurable` → instrument-recovery",
           "`no-check` → control-plan-fix", "bom-fix", "work-order-fix", "record-fix", "写しが固定した版と違う納品", "1 度だけ決める",
           "`on_fail` にかかわらず control-plan-fix"],
    "D3": ["設計者側が走らせる", "**新しい納品**", "改めて判定する", "同じ納品は再び判定しない", "「2:A」", "別の道は無い", "ECO-108 / ECO-111",
           "配布の時点で製品ごとに決める", "承認者への入力のまま"],
    "D4": ["`advance_decision`", "`pass` → `pass`", "`violation` → `fail`", "`unmeasurable` → `blocked`", "`no-check` → `not-run`", "R-050", "ECO-088",
           "R-050 (b)", "名前つきの抑止"],
    "D5": ["`work_ref`", "工程の ECO は同じ作業を続け", "**台帳**", "`advance_decision.sequence`", "**収束**", "**管理**", "**回数は収束の入力にだけなる**",
           "`nothing-measured`", "**どの行も測らなかった**", "`<row>:<category>`", "`<route>:<message>`", "**`routes_done`**", "**`row_changes`**",
           "`removed`・`added`・`renamed`", "状態を新しい行へ引き継ぐ", "`converged`", "`open`", "`bound-reached`", "既定 3", "既定 5",
           "**作業の最初の発行**", "外れた行は上限を上げない", "C6", "上限を作業の中から上げない", "§8.5", "進めずに止める", "§13 の人の処置待ち", "ECO-108 / ECO-111",
           "回数でなく管理の読み", "C1 残る", "C2 戻る", "C3 退行", "C4 自分の部品が続けて落ちる", "C5 行の集合", "C6 上限が変わった",
           "*振り分けは済んだが原因が消えない*", "*振り分けが済んでいない*", "*記録なし*", "振り分け先でなく区分を読む", "自分の原因のもとで変えた行",
           "納品が進んだときも", "`in-control`", "`signals`", "**管理の点検**", "工程 ECO", "AGENTS.md 規律 1", "宣言した既定を当てる",
           "**新しい約束**", "**新しい機能**", "**導出できない**", "候補として機械で印", "OBS-20260922-01", "blocker 報告", "点検の所見"],
    "limits": ["`Error → passed`", "REQ / INV", "2 つの製品", "納品 2 回", "`evidence_sha256` は後の", "同じ BOM のバイトのコミットへ戻したタグは通し", "depth G",
               "git を要し", "D5 は原因を D2 が名づけるとおりに見る", "検査を定義し直して消しただけ", "新しい `work_ref`", "3 回・5 回",
               "遅延にしない", "配布は別の ECO"],
}
ORDER = ["I0", "I1", "I2", "I3a", "I3b", "I4", "D0", "D1", "D2", "D3", "D4", "D5"]


def segments(item_lines):
    joined = re.sub(r"\n\s*", "", "\n".join(item_lines))
    marks = [(m.start(), m.group(1)) for m in re.finditer(r"\*\*(I0|I1|I2|I3a|I3b|I4|D0|D1|D2|D3|D4|D5)[ (（]", joined)]
    lim = joined.find("- 限界:")
    out = {}
    for k, (pos, rid) in enumerate(marks):
        end = marks[k + 1][0] if k + 1 < len(marks) else (lim if lim > pos else len(joined))
        out.setdefault(rid, joined[pos:end])
    out["limits"] = joined[lim:] if lim >= 0 else ""
    return out


segs = segments(item)
for rid, tokens in CLAUSES.items():
    missing = [t for t in tokens if t not in segs.get(rid, "")]
    check(f"V1 {rid}: {len(tokens)} clauses in its segment", not missing, f"missing {missing}")
I2_VALUES = ["`automated` | `human:<role>` | `automated+human:<role>`", "`product-fix`", "`instrument-recovery`", "`control-plan-fix`",
             "`retired`", "`row_key`", "`outcomes`", "`identity`", "`passed`", "`failed`", "`skipped`", "`not-run`",
             "`<path>@<40-hex commit>`", "`{commit, tree}`"]
for v in I2_VALUES:
    check(f"V1 the item states I2's {v}", v in text)
flow = section("## 1. ", r"^## ")
check("V1 section 1 carries one line naming it", sum(NAME in l for l in flow) == 1, f"{sum(NAME in l for l in flow)} lines")
s61 = section("### 6.1 ", r"^### ")
check("V1 6.1 carries one line naming it", sum(NAME in l for l in s61) == 1, f"{sum(NAME in l for l in s61)} lines")
onfail = [l for l in s44 if "落ちたときの振り分け(`on_fail`" in l]
check("V1 the on_fail sentence names the item", onfail and NAME in onfail[0])
check("V1 the on_fail sentence lists no value outside I2", onfail and "人の承認" not in onfail[0])


# ---- V1: the templates (each M1 field's first line, or the comment lines right after it, names the item)
def field_comment(rel, key):
    tl = read(rel).splitlines()
    # `result` is the decision record's (test_evidence_refs), not the validation block's that comes first
    start = next((i for i, l in enumerate(tl) if l.strip().startswith("test_evidence_refs:")), 0) if key == "result" else 0
    for i, line in enumerate(tl):
        if i < start:
            continue
        if re.match(rf"^\s*(- )?{re.escape(key)}:", line) and not line.lstrip().startswith("#"):
            block = [line]
            for nxt in tl[i + 1:]:
                if nxt.lstrip().startswith("#"):
                    block.append(nxt)
                else:
                    break
            return any(NAME in b for b in block)
    return None


CP, AB, WO = "method/templates/33-control-plan.yaml", "method/templates/50-as-built.yaml", "method/templates/40-work-order.md"
for rel, keys in [(CP, ["check_mapping", "when", "on_fail", "status", "approver"]),
                  (AB, ["work_ref", "frozen_commit", "work_order_ref", "mbom_ref", "control_plan_ref", "delivered", "routes_done",
                        "row_changes", "source", "format", "evidence_sha256", "result", "advance_decision", "sequence"])]:
    for k in keys:
        got = field_comment(rel, k)
        check(f"V1 {Path(rel).name} {k} carries a comment naming the item", got, "field absent" if got is None else "no comment")
wo = read(WO).splitlines()
fl = [i for i, l in enumerate(wo) if l.startswith("- 対象 BOM tag/commit:")]
check("V1 40-work-order.md frozen-revision line has its comment on the next line",
      len(fl) == 1 and fl[0] + 1 < len(wo) and "<!--" in wo[fl[0] + 1] and NAME in wo[fl[0] + 1])
check("V1 40-work-order.md frozen-revision line holds no inline comment", len(fl) == 1 and "<!--" not in wo[fl[0]])
check("V1 40-work-order.md has the bounds line", any(l.startswith(f"- {NAME}の上限: holds ") and ", decisions " in l for l in wo))
cp_text, ab_text = read(CP), read(AB)
for v in ["automated | human:<role> | automated+human:<role>", "product-fix", "instrument-recovery", "control-plan-fix", "retired",
          "passed", "failed", "skipped", "not-run"]:
    check(f"V1 33-control-plan.yaml comment states {v}", any(v in l.split("#", 1)[1] for l in cp_text.splitlines() if "#" in l))
check("V1 33 drops human-approval as an on_fail value", "human-approval" not in cp_text)
for v in ["<path>@<40-hex commit>", "{commit, tree}"]:
    check(f"V1 50-as-built.yaml comment states {v}", any(v in l.split("#", 1)[1] for l in ab_text.splitlines() if "#" in l))


# ---- V2 (a): the fields the rehearsals read, by key path in the parsed templates
def has(doc, path):
    cur = doc
    for part in path.split("."):
        if isinstance(cur, list):
            cur = next((x for x in cur if isinstance(x, dict) and part in x), None)
            if cur is None:
                return False
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return True


try:
    cp_doc, ab_doc = yaml.safe_load(cp_text) or {}, yaml.safe_load(ab_text) or {}
    mb_doc = yaml.safe_load(read("method/templates/32-mbom.yaml")) or {}
    parsed = True
except yaml.YAMLError as e:
    cp_doc = ab_doc = mb_doc = {}
    parsed = False
    print(f"  (a template does not parse: {e})")
check("V2 the templates parse", parsed)
fmt = next(iter((cp_doc.get("control_plan") or {}).get("check_mapping") or {"-": None}))
for doc, name, paths in [
        (cp_doc, "33", ["control_plan.check_mapping", f"control_plan.check_mapping.{fmt}.row_key", f"control_plan.check_mapping.{fmt}.outcomes",
                        f"control_plan.check_mapping.{fmt}.identity", "control_plan.characteristics.id",
                        "control_plan.characteristics.approver", "control_plan.characteristics.on_fail.red",
                        "control_plan.characteristics.on_fail.unmeasurable", "control_plan.characteristics.status"]),
        (mb_doc, "32", ["mbom.manufacturing_units.acceptance_refs", "mbom.assembly.acceptance_refs", "mbom.assembly.assembly_reason"]),
        (ab_doc, "50", ["as_built.work_ref", "as_built.frozen_commit", "as_built.work_order_ref", "as_built.mbom_ref", "as_built.control_plan_ref",
                        "as_built.delivered.commit", "as_built.delivered.tree", "as_built.routes_done", "as_built.row_changes",
                        "as_built.test_evidence_refs.source", "as_built.test_evidence_refs.cp_ref", "as_built.test_evidence_refs.evidence_path",
                        "as_built.test_evidence_refs.evidence_sha256", "as_built.test_evidence_refs.format",
                        "as_built.test_evidence_refs.observed_at", "as_built.test_evidence_refs.result",
                        "as_built.advance_decision.result", "as_built.advance_decision.rows", "as_built.advance_decision.not_decided",
                        "as_built.advance_decision.sequence.convergence", "as_built.advance_decision.sequence.control"])]:
    for p in paths:
        check(f"V2 {name} has {p}", has(doc, p))

# ---- V2 (b): the rehearsals re-run, byte for byte
scratch.mkdir(parents=True, exist_ok=True)
for script, args, stored in [("run_rehearsal_v2.py", [str(vp2)], "rehearsal-v2.txt"),
                             ("run_moviepad.py", [str(mpr)], "rehearsal-moviepad.txt"),
                             ("run_moviepad_d2.py", [str(mpr)], "rehearsal-moviepad-d2.txt"),
                             ("rehearse_sequence.py", [], "rehearsal-sequence.txt")]:
    out = scratch / f"rerun-{stored}"
    done = subprocess.run([sys.executable, "-B", script, *args, str(out)], cwd=HERE, capture_output=True,
                          env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    same = done.returncode == 0 and out.is_file() and out.read_bytes() == (HERE / stored).read_bytes()
    check(f"V2 {script} re-run equals {stored}", same, f"exit {done.returncode}")
    # inspection r1 IA-07: a stored output that itself records a missed case is not a pass, whatever the byte equality says
    marks = re.findall(r"\bMISSED\b|: False\b", out.read_text(encoding="utf-8")) if out.is_file() else ["no output"]
    check(f"V2 {stored} records no missed case", not marks, f"{len(marks)} marks")

print(f"V1/V2: {'PASS' if all(results) else 'FAIL'} ({sum(results)}/{len(results)})")
sys.exit(0 if all(results) else 1)
