r"""ECO-113: mechanical check that the receipt's evidence records match the evidence files, and that a record fix leaves the design unchanged.

Usage:
  python -B record_check.py design-hash <order.md>            print sha256 of everything before "## 収束 receipt" (the design: header..§3)
  python -B record_check.py evidence <order.md> <dir>         every sha256 prefix the order states for an evidence file must be that file's sha256,
                                                              and every evidence file must be named with its current sha256 at least once
Exit 0 = PASS, 1 = FAIL. The verdict is also the output's first line.
"""
import hashlib
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

mode, order = sys.argv[1], Path(sys.argv[2])
text = order.read_text(encoding="utf-8")
cut = text.find("\n## 収束 receipt")
if cut < 0:
    print("UNMEASURABLE: no receipt heading")
    sys.exit(2)
if mode == "design-hash":
    print(hashlib.sha256(text[:cut].encode("utf-8")).hexdigest())
    sys.exit(0)

evdir = Path(sys.argv[3])
names = ("refusal_matrix.py", "calibrate_matrix.py", "refusal-matrix.md")
actual = {n: hashlib.sha256((evdir / n).read_bytes()).hexdigest() for n in names}
receipt = text[cut:]
fails, lines = [], []
# every "<name>` ... sha256 `<hex>…`" and "<name>` (sha256 `<hex>…`)" mention, and the parenthesised "(`<name>`, sha256 `<hex>…`)" form
for m in re.finditer(r"`(refusal_matrix\.py|calibrate_matrix\.py|refusal-matrix\.md)`[^`\n]{0,40}?sha256 `([0-9a-f]{8,64})…?`", receipt):
    name, pref = m.group(1), m.group(2)
    ok = actual[name].startswith(pref)
    lines.append(f"{name}: stated {pref} actual {actual[name][:16]} -> {'OK' if ok else 'MISMATCH'}")
    if not ok:
        fails.append(f"{name}: stated {pref} != actual {actual[name][:16]}")
# bare prefixes stated next to a name in a "Script sha256 `x`; report `y`" sentence
for m in re.finditer(r"Script sha256 `([0-9a-f]{8,64})…?`; report `([0-9a-f]{8,64})…?`", receipt):
    for name, pref in (("refusal_matrix.py", m.group(1)), ("refusal-matrix.md", m.group(2))):
        ok = actual[name].startswith(pref)
        lines.append(f"{name}: stated {pref} actual {actual[name][:16]} -> {'OK' if ok else 'MISMATCH'}")
        if not ok:
            fails.append(f"{name}: stated {pref} != actual {actual[name][:16]}")
for n in names:
    if not any(n in ln and "OK" in ln for ln in lines):
        fails.append(f"{n}: its current sha256 is not stated in the receipt")
print("PASS" if not fails else "FAIL")
print("\n".join(lines))
for f in fails:
    print("FAIL:", f)
sys.exit(0 if not fails else 1)
