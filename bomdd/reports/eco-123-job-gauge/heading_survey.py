"""ECO-123 filing basis: what the job view's closure-heading rule decides for every ECO in the register, now and with an English form.

  python -X utf8 heading_survey.py <BomDD repo>

Read-only. For each register entry with an order: the status, whether the order (fences removed, as bomdd-job does) matches the current
CLOSE_HEAD_RE, whether it matches the proposed rule (`クローズ` or `Closure` after the section number, then `verified` on the line), and the
stop the closure rule alone gives under each. Prints the entries whose stop differs, the counts, and every heading the proposed rule
matches that the current rule does not.
"""
import importlib.util
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("bj", root / "method/tools/bomdd-job.py")
bj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bj)
NEW = re.compile(r"^[ \t]{0,3}#{2,6}[ \t]+\d+\.[ \t]*(?:クローズ|Closure)[^\n]*verified", re.M)

entries, err = bj.load_register(root / "bomdd/60-change-register.yaml")
assert not err, err


def stop(status, closed):
    if closed and status != "verified":
        return "LEDGER_INCONSISTENT(closed order, status " + status + ")"
    if status == "verified" and not closed:
        return "LEDGER_INCONSISTENT(verified, no closure)"
    return "NONE"


n, cur_bad, new_bad, changed, added = 0, [], [], [], []
for e in entries:
    if not isinstance(e, dict) or not e.get("order_ref"):
        continue
    p = root / e["order_ref"]
    if not p.exists():
        continue
    n += 1
    text = bj.FENCE_RE.sub("", p.read_text(encoding="utf-8", errors="replace"))
    st = str(e.get("status"))
    c, w = bool(bj.CLOSE_HEAD_RE.search(text)), bool(NEW.search(text))
    s0, s1 = stop(st, c), stop(st, w)
    if s0 != "NONE":
        cur_bad.append(e["id"])
    if s1 != "NONE":
        new_bad.append(e["id"])
    if s0 != s1:
        changed.append(f"{e['id']} ({st}): {s0} -> {s1}")
    for m in NEW.finditer(text):
        if not bj.CLOSE_HEAD_RE.match(m.group(0)):
            added.append(f"{e['id']}: {m.group(0).strip()[:110]}")

print(f"entries with an order: {n}")
print(f"closure rule alone, current rule: {len(cur_bad)} not NONE: {', '.join(cur_bad)}")
print(f"closure rule alone, proposed rule: {len(new_bad)} not NONE: {', '.join(new_bad) or '-'}")
print(f"changed ({len(changed)}):")
print("\n".join("  " + c for c in changed))
print(f"headings matched only by the proposed rule ({len(added)}):")
print("\n".join("  " + a for a in added))
# the entries still not NONE under the proposed rule: what their orders hold
ANY = re.compile(r"^[ \t]{0,3}#{2,6}[^\n]*(?:クローズ|Closure)[^\n]*$", re.M)
kinds = {}
for e in entries:
    if not isinstance(e, dict) or e.get("id") not in new_bad:
        continue
    text = bj.FENCE_RE.sub("", (root / e["order_ref"]).read_text(encoding="utf-8", errors="replace"))
    heads = [m.group(0).strip() for m in ANY.finditer(text)]
    k = ("no closure heading" if not heads else
         "closure heading without 'verified'" if not any("verified" in h for h in heads) else "closure heading in another form")
    kinds.setdefault(k, []).append(e["id"] + (f" [{heads[-1][:60]}]" if k == "closure heading in another form" else ""))
for k, v in kinds.items():
    print(f"still not NONE, {k} ({len(v)}): {', '.join(v)}")
