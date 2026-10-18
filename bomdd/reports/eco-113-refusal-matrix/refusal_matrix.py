r"""ECO-113 loop 5: mechanical check of S4 (refusals before decide()) against the rest of the order.

Usage: python -B refusal_matrix.py <order.md> <out.md>
The verdict is the report's first line (`# S4 refusal matrix — PASS|FAIL|UNMEASURABLE`); the exit code mirrors it (0/1/2).

What it checks (and what it does not):
 C1 the reasons the order DEFINES == the rows of S4's table. "Defined" follows S4's own convention: every phrase  cause `X`  anywhere in §1,
    plus every class bullet of J2. It does NOT prove that no other refusal exists in the code; it proves the order's text and its table agree.
 C2 every row has all five columns non-empty.
 C3 every row's "arises in" names a rule whose text contains the reason.
 C4 every rule or limit cited in a row's "way out" exists as a heading; and if the way out cites R2, R2 does not refuse that reason.
 C5 O1 gives each reason exactly one verdict group (`A`, `B`: `VERDICT`, ... exit N), with STOP → exit 1 and UNMEASURABLE → exit 2.
 C6 every reason is named in at least one acceptance item (§3) besides the coverage line.
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

src = Path(sys.argv[1]).read_text(encoding="utf-8")
out_path = Path(sys.argv[2])


def bullet(rule_id):
    m = re.search(r"^- \*\*" + re.escape(rule_id) + r" —.*?(?=^- \*\*|^### |^## )", src, re.S | re.M)
    return m.group(0) if m else None


def finish(verdict, body):
    text = "\n".join([f"# S4 refusal matrix — {verdict}", ""] + body) + "\n"
    out_path.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    sys.exit({"PASS": 0, "FAIL": 1}.get(verdict, 2))


sec1 = re.search(r"^## 1\. .*?(?=^## 2\.)", src, re.S | re.M)
j2, o1, r2 = bullet("J2"), bullet("O1"), bullet("R2")
s4 = re.search(r"^- \*\*S4 —.*?(?=^### )", src, re.S | re.M)
acc = re.search(r"^## 3\. Acceptance.*?(?=^## )", src, re.S | re.M)
missing = [n for n, v in (("§1", sec1), ("J2", j2), ("O1", o1), ("R2", r2), ("S4", s4), ("§3", acc)) if not v]
if missing:
    finish("UNMEASURABLE", [f"a required section was not found: {missing}"])
sec1, s4, acc = sec1.group(0), s4.group(0), acc.group(0)

defined = {}
for m in re.finditer(r"cause `([A-Z_]+)`", sec1):
    rule = None
    for rm in re.finditer(r"^- \*\*([A-Z]\d+) —", sec1[: m.start()], re.M):
        rule = rm.group(1)
    defined.setdefault(m.group(1), rule or "?")
for r in re.findall(r"^\s+- `([A-Z_]+)` —", j2, re.M):
    defined.setdefault(r, "J2")

rows = {}
for line in s4.splitlines():
    if line.strip().startswith("| `"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = re.match(r"`([A-Z_]+)`", cells[0])
        if m and len(cells) == 5:
            rows[m.group(1)] = cells

# O1 verdict groups: "`A`, `B`: `VERDICT`, ... exit N"
groups = []
for m in re.finditer(r"((?:`[A-Z_]+`(?:, )?)+): `(STOP|UNMEASURABLE)[^`]*`[^.]*?exit (\d)", o1):
    groups.append((re.findall(r"`([A-Z_]+)`", m.group(1)), m.group(2), m.group(3)))
r2_refused = set(re.findall(r"`([A-Z_]+)` refused", r2))
headings = set(re.findall(r"^- \*\*([A-Z][A-Z0-9]*\d+)[ (—]", src, re.M))
cov = re.search(r"\*\*Coverage \(T1\).*?(?=\n\n)", acc, re.S)
acc_items = acc.replace(cov.group(0), "") if cov else acc

fails, matrix = [], []
c1 = set(defined) == set(rows)
if not c1:
    fails.append(f"C1 defined - table: {sorted(set(defined) - set(rows))}; table - defined: {sorted(set(rows) - set(defined))}")
for reason in sorted(set(defined) | set(rows)):
    cells = rows.get(reason)
    r = {"reason": reason, "defined_in": defined.get(reason, "-"), "row": bool(cells)}
    if cells:
        r["c2"] = all(cells)
        rule = re.match(r"([A-Z]\d)", cells[1])
        body = bullet(rule.group(1)) if rule else None
        r["c3"] = bool(body) and reason in body
        cited = set(re.findall(r"\(([A-Z]\d+)\)", cells[4]))
        bad_cite = sorted(c for c in cited if c not in headings)
        refused = "R2" in cited and reason in r2_refused
        r["c4"] = not bad_cite and not refused
        r["cites"] = sorted(cited)
        if not r["c2"]:
            fails.append(f"C2 {reason}: an empty column")
        if not r["c3"]:
            fails.append(f"C3 {reason}: 'arises in' {cells[1]!r} does not name a rule that contains it")
        if bad_cite:
            fails.append(f"C4 {reason}: way out cites {bad_cite}, not a heading")
        if refused:
            fails.append(f"C4 {reason}: way out cites R2, which refuses {reason}")
    hits = [(v, e) for names, v, e in groups if reason in names]
    r["c5"] = len(hits) == 1 and ((hits[0][0] == "STOP") == (hits[0][1] == "1"))
    r["o1"] = hits
    if not r["c5"]:
        fails.append(f"C5 {reason}: O1 verdict groups {hits} (need exactly one; STOP→1, UNMEASURABLE→2)")
    r["c6"] = reason in acc_items
    if not r["c6"]:
        fails.append(f"C6 {reason}: no acceptance item names it")
    matrix.append(r)

lines = [f"C1 (defined == table): {c1}", "",
         "| reason | defined in | S4 row | C2 | C3 | C4 (cites) | C5 (O1) | C6 |", "|---|---|---|---|---|---|---|---|"]
for r in matrix:
    lines.append(f"| `{r['reason']}` | {r['defined_in']} | {r['row']} | {r.get('c2')} | {r.get('c3')} | {r.get('c4')} {r.get('cites', '')} "
                 f"| {r['c5']} {r['o1']} | {r['c6']} |")
lines += ["", "Failures:"] + ([f"- {f}" for f in fails] or ["- none"])
finish("PASS" if not fails else "FAIL", lines)
