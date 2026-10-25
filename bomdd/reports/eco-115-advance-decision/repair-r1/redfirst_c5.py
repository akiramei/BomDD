"""Red-first for inspection r1 IA-05: the repaired rehearse_sequence.py with C5's manufacture-tree clause put back (the row's own cause
among the routing causes on the row, instead of the recorded cause) must give Y6 BAD and Y7 OK."""
import subprocess
import sys

src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
new = '''            if last in ("violation", "unmeasurable") and via != f"{row}:{last}":'''
old = '''            if last in ("violation", "unmeasurable") and f"{row}:{last}" not in on_row[row]:'''
assert s.count(new) == 1
open(out, "w", encoding="utf-8", newline="\n").write(s.replace(new, old))
done = subprocess.run([sys.executable, "-B", out], capture_output=True, text=True, encoding="utf-8")
for line in done.stdout.splitlines():
    if line.startswith(("BAD", "arms:")) or " Y6 " in line or " Y7 " in line:
        print(line[:160])
print("exit", done.returncode)
