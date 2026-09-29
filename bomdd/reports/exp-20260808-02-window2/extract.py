import re, glob, os, sys
ROOT = r"C:\Users\akira\source\repos\ViewTube"
rows = []  # (eco, id, severity, source)

def norm_sev(s):
    s = s.lower()
    if "blocking_if_ruled" in s:
        return "blocking_if_ruled"
    if "blocking" in s:
        return "blocking"
    if "material" in s:
        return "material"
    if "minor" in s:
        return "minor"
    return "?"

# --- markdown reviews 187..211
for n in range(178, 212):
    p = os.path.join(ROOT, "bomdd", "eco", f"ECO-VT-{n}-independent-review.md")
    if not os.path.exists(p):
        continue
    text = open(p, encoding="utf-8").read()
    if n in (187, 191, 192):
        # YAML-in-markdown: "- id: X" followed by "severity: Y"
        for m in re.finditer(r"^\s*- id: ([^\n]+)\n\s*severity: ([^\n]+)", text, re.M):
            rows.append((n, m.group(1).strip(), norm_sev(m.group(2)), os.path.basename(p)))
        continue
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        m = re.match(r"^#{3,4} ([RI]\d{3}[abc]-F\d+)(.*)$", ln)
        if not m:
            continue
        fid, rest = m.group(1), m.group(2)
        sev = norm_sev(rest.split(" - ", 2)[1] if " - " in rest else rest)
        if n == 194:
            # severity is on a following "- Severity:" bullet
            for ln2 in lines[i+1:i+4]:
                mm = re.match(r"^- Severity: (.*)$", ln2)
                if mm:
                    sev = norm_sev(mm.group(1)); break
        else:
            # take the first severity word in the heading remainder
            sev = norm_sev(rest[:60])
        rows.append((n, fid, sev, os.path.basename(p)))

# --- YAML reviews 186, 189
for n in (186, 189):
    for p in sorted(glob.glob(os.path.join(ROOT, "test-results", f"eco-vt-{n}-*", "r8-round-*.yaml"))):
        text = open(p, encoding="utf-8").read()
        for m in re.finditer(r"^\s*- id: ([^\n]+)\n\s*severity: ([^\n]+)", text, re.M):
            rows.append((n, m.group(1).strip(), norm_sev(m.group(2)), os.path.relpath(p, ROOT)))

rows.sort(key=lambda r: (r[0], r[1]))
for r in rows:
    print(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}")
print("TOTAL", len(rows), file=sys.stderr)
from collections import Counter
print(Counter(r[0] for r in rows), file=sys.stderr)
print(Counter(r[2] for r in rows), file=sys.stderr)
