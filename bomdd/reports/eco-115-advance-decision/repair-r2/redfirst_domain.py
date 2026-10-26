"""Red-first for inspection r2 IA-10: the current rehearsals with the shared bounds parser's domain opened to any decimal integer of 1 or more must
stop the D5 rehearsal on Z3 (a 5,000-digit first line) with ValueError, as the inspector's probe did.

  python -B repair-r2/redfirst_domain.py <scratch directory>     (from bomdd/reports/eco-115-advance-decision/)

Since inspection r4 (IA-13) this runs the control of repair-r4/redfirst_all.py: r3 moved the pattern into rehearse_decision_v2.parse_bounds, so
the control patches that file in a scratch copy holding both rehearsals, and passes only on the expected signature. Exit 0 only when it shows.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "repair-r4"))
import redfirst_all  # noqa: E402

ok, detail = redfirst_all.domain_control(tempfile.mkdtemp(prefix="rf-domain-", dir=os.path.abspath(sys.argv[1])))
print(f"{'SIGNATURE' if ok else 'OTHER    '} domain: {detail}")
sys.exit(0 if ok else 1)
