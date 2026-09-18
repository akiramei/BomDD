"""第 2 回の集計 — results-02.jsonl から混同行列・sub 別内訳・認定条件 ①②③ の判定(事前宣言値)を markdown で出す。"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1 else "bomdd/reports/jev-qualification-01/results-02.jsonl")
rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
ok = [r for r in rows if "choice" in r]
errs = [r for r in rows if "error" in r]
labels = ["performed", "planned", "template", "omitted"]
print(f"records={len(rows)} answered={len(ok)} errors={len(errs)} models={sorted({r['model'] for r in ok})}")
print(f"tokens in={sum((r.get('usage') or {}).get('input_tokens') or 0 for r in ok)} out={sum((r.get('usage') or {}).get('output_tokens') or 0 for r in ok)}")

cm = Counter((r["label"], r["choice"]) for r in ok)
print("\n## 混同行列(行= ラベル・列= Jev の choice)\n")
print("| ラベル \\ choice | " + " | ".join(labels) + " | N | 正答率 |")
print("|---|" + "---|" * (len(labels) + 2))
for lab in labels:
    n = sum(cm[(lab, c)] for c in labels)
    if n == 0:
        continue
    acc = cm[(lab, lab)] / n
    print(f"| {lab} | " + " | ".join(str(cm[(lab, c)]) for c in labels) + f" | {n} | {acc:.2f} |")

print("\n## sub 別(ラベル内の内訳)\n")
print("| ラベル/sub | N | 正答 | 誤分類先 | 拮抗(conf<0.5) |")
print("|---|---|---|---|---|")
groups = defaultdict(list)
for r in ok:
    groups[(r["label"], r["sub"])].append(r)
for (lab, sub), rs in sorted(groups.items()):
    wrong = Counter(r["choice"] for r in rs if not r["correct"])
    amb = sum(1 for r in rs if r["ambiguous"])
    print(f"| {lab}/{sub} | {len(rs)} | {sum(r['correct'] for r in rs)} | {dict(wrong) or '—'} | {amb} |")

planned = [r for r in ok if r["label"] == "planned"]
performed = [r for r in ok if r["label"] == "performed"]
c1 = sum(1 for r in planned if r["choice"] == "performed")
c2 = sum(1 for r in performed if r["choice"] == "performed")
both = planned + performed
c3 = sum(1 for r in both if r["correct"])
print("\n## 認定条件(事前宣言)\n")
print(f"- ① planned → performed の誤分類: {c1}/{len(planned)} = {c1/len(planned):.2%}(条件 ≤ 10%)→ {'達成' if c1/len(planned) <= 0.10 else '未達'}")
print(f"- ② performed の再現率: {c2}/{len(performed)} = {c2/len(performed):.2%}(条件 ≥ 85%)→ {'達成' if c2/len(performed) >= 0.85 else '未達'}")
print(f"- ③ planned+performed の正答率: {c3}/{len(both)} = {c3/len(both):.2%}(条件 ≥ 85%)→ {'達成' if c3/len(both) >= 0.85 else '未達'}")
print(f"- 拮抗(confidence < 0.5): {sum(1 for r in ok if r['ambiguous'])}/{len(ok)}")

print("\n## 誤分類の検体(全件)\n")
print("| id | ラベル/sub | choice | conf | p(performed) | p(planned) |")
print("|---|---|---|---|---|---|")
for r in ok:
    if not r["correct"]:
        pr = r["probabilities"]
        print(f"| {r['id'][:60]} | {r['label']}/{r['sub']} | {r['choice']} | {r['confidence']:.2f} | {pr.get('performed',0):.2f} | {pr.get('planned',0):.2f} |")
for r in errs:
    print(f"| {r['id'][:60]} | {r['label']}/{r['sub']} | UNMEASURABLE | {r.get('error_class')} | | |")
