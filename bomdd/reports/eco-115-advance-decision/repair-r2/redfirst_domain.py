"""Red-first for inspection r2 IA-10: the repaired rehearse_sequence.py with r1's open domain put back (any decimal integer of 1 or more) in a
scratch copy must fail to evaluate Z3 (a 5,000-digit first line), as the inspector's probe did; the repaired domain (1 to 999) reads it.

  python -B repair-r2/redfirst_domain.py <repaired rehearse_sequence.py> <scratch copy path>
"""
import subprocess
import sys

src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
closed = 'holds ([1-9][0-9]{0,2}), decisions ([1-9][0-9]{0,2})'
opened = 'holds ([1-9][0-9]*), decisions ([1-9][0-9]*)'
assert s.count(closed) == 1
open(out, "w", encoding="utf-8", newline="\n").write(s.replace(closed, opened))
done = subprocess.run([sys.executable, "-B", out], capture_output=True, text=True, encoding="utf-8")
err = [line for line in done.stderr.splitlines() if line.strip()]
print("exit", done.returncode)
print("last stderr line:", err[-1][:160] if err else "(none)")
