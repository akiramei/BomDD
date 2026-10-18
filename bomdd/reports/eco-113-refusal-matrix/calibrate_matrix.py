"""Known-bad calibration of refusal_matrix.py: each mutated copy of the order must read FAIL (the report's first line), the original PASS."""
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
order = (here / "60-change-order-eco-113.md").read_text(encoding="utf-8")


def mutate(old, new):
    assert order.count(old) == 1, old[:70]
    return order.replace(old, new)


cases = {
    "K0-original": order,
    "K1-missing-row": "\n".join(l for l in order.splitlines() if not l.startswith("  | `JOURNAL_CORRUPT` | J2 |")) + "\n",
    "K2-bad-cite": mutate("wait for the other entry; retry (L2) |", "wait (L99) |"),
    "M1-o1-names-removed": mutate("`ENTRY_ALIVE`, `ABNORMAL_END`, `CELL_ALIVE`: `STOP`", "`ABNORMAL_END`: `STOP`"),
    "M2-new-reason-no-row": mutate("The ledger (`--ledger`) is not read for this.",
                                   "The ledger (`--ledger`) is not read for this. A journal on a full disk → cause `JOURNAL_FULL`."),
    "M3-way-out-refuses": mutate("wait and retry; if persistent, outside the tool (L3) |", "release (R2) |"),
}
want = {k: ("PASS" if k.startswith("K0") else "FAIL") for k in cases}
bad = 0
for name, text in cases.items():
    p = here / f"cal-{name}.md"
    p.write_text(text, encoding="utf-8", newline="\n")
    r = subprocess.run([sys.executable, "-B", str(here / "refusal_matrix.py"), str(p), str(here / f"cal-{name}.out.md")],
                       capture_output=True, text=True, encoding="utf-8")
    first = (here / f"cal-{name}.out.md").read_text(encoding="utf-8").splitlines()[0]
    got = first.rsplit("— ", 1)[-1]
    ok = got == want[name] and r.returncode == {"PASS": 0, "FAIL": 1}[want[name]]
    bad += not ok
    print(f"{name}: want {want[name]}, first line {got!r}, exit {r.returncode} -> {'OK' if ok else 'WRONG'}")
    p.unlink()
    (here / f"cal-{name}.out.md").unlink()
print("calibration", "PASS" if not bad else f"FAIL ({bad})")
sys.exit(1 if bad else 0)
