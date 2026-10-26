"""Red-first for inspection r1 IA-05: the current rehearse_sequence.py with C5's manufacture-tree clause put back (the row's own cause among the
routing causes on the row, instead of the recorded cause) must give exactly Y6 BAD.

  python -B repair-r1/redfirst_c5.py <scratch directory>     (from bomdd/reports/eco-115-advance-decision/)

Since inspection r4 (IA-13) this runs the control of repair-r4/redfirst_all.py, which stages every file the rehearsal imports (the shared
bounds parser in rehearse_decision_v2.py, since r3) and passes only on the expected signature; before, this helper copied one file and accepted
any child failure. Exit 0 only when the signature shows.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "repair-r4"))
import redfirst_all  # noqa: E402

ok, detail = redfirst_all.c5_control(tempfile.mkdtemp(prefix="rf-c5-", dir=os.path.abspath(sys.argv[1])))
print(f"{'SIGNATURE' if ok else 'OTHER    '} c5: {detail}")
sys.exit(0 if ok else 1)
