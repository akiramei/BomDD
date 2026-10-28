"""ECO-117 V1/V2 re-read with every check id: verify117.py's line filter `^\\[C\\d+b?\\] ` dropped ids with
other suffix letters ([C5a], [C6a], ...). This re-reads the saved outputs with `^\\[C\\d+[a-z]?\\] `.

Usage: python recheck117.py <report-dir> <filing-run-output> <manufacture-run-output>
"""
import re
import sys
from pathlib import Path

REP, FILING, MFG = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
V = REP / "v1v2"
CHECK = re.compile(r"^\[(C\d+[a-z]?)\] (PASS|FAIL)")


def root_of(text):
    m = re.search(r"^self-conformance: (.+)$", text, re.M)
    return m.group(1).strip() if m else None


def lines(path):
    text = path.read_text(encoding="utf-8")
    root = root_of(text)
    out = []
    for l in text.splitlines():
        if CHECK.match(l):
            if root:
                l = l.replace(root, "<ROOT>")
            l = re.sub(r"[A-Za-z]:\\[^\s]*?\\Temp\\[^\s;,)\]]*", "<TMP>", l)
            l = re.sub(r"(bomdd-selfconf-[a-z0-9]+-|tmp)[a-z0-9_]{6,}", r"\1*", l)
            out.append(l.rstrip())
    return out


def ids(ls):
    return [CHECK.match(l).group(1) for l in ls]


def show(name, value):
    print(f"{name}: {value}")


a, b = lines(V / "A-dotnet.txt"), lines(V / "B-dotnet.txt")
show("V1 A/B --dotnet: line counts", (len(a), len(b)))
show("V1 A/B --dotnet: identical", a == b)
show("V1 A/B --dotnet: differing pairs", [(x, y) for x, y in zip(a, b) if x != y][:5])
show("V1 ids", sorted(set(ids(a)), key=lambda s: (int(re.sub(r"\D", "", s)), s)))
f, m = lines(FILING), lines(MFG)
show("V1 this repository, default mode: original at the filing tree / changed at the manufacture tree, line counts", (len(f), len(m)))
show("V1 this repository: identical", f == m)
show("V1 this repository: same ids and verdicts", [CHECK.match(x).groups() for x in f] == [CHECK.match(x).groups() for x in m])
show("V1 this repository: differing pairs", [(x, y) for x, y in zip(f, m) if x != y][:5])
c9b = [l for l in b if l.startswith("[C9]")]
for t in ("B-c9only-witness-present", "B-c9only-witness-absent"):
    ls = lines(V / f"{t}.txt")
    show(f"V2(a) {t}: ids", sorted(set(ids(ls))))
    show(f"V2(a) {t}: == B --dotnet [C9]", ls == c9b)
c = lines(V / "C-dotnet.txt")
show("V2(c) C --dotnet: FAIL lines", [x[:70] for x in c if " FAIL " in x])
for t in ("C-c9only-witness-absent", "C-c9only-witness-present"):
    ls = lines(V / f"{t}.txt")
    show(f"V2(c) {t}: == C --dotnet [C9]", ls == [x for x in c if x.startswith("[C9]")])
m2 = lines(V / "M2-c9only.txt")
show("known-bad M2: non-C9 lines", len([x for x in m2 if not x.startswith("[C9]")]))
