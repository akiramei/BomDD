"""Write a manifest of every file in ROOT's working tree (excluding .git): relpath, size, sha256. usage: wtfp.py ROOT OUT"""
import hashlib
import os
import sys
import time

root, out = sys.argv[1], sys.argv[2]
t = time.perf_counter()
rows = []
total = 0
for d, dirs, files in os.walk(root):
    if ".git" in dirs:
        dirs.remove(".git")
    for f in files:
        p = os.path.join(d, f)
        data = open(p, "rb").read()
        total += len(data)
        rows.append(f"{os.path.relpath(p, root).replace(os.sep, '/')}\t{len(data)}\t{hashlib.sha256(data).hexdigest()}")
rows.sort()
open(out, "w", encoding="utf-8").write("\n".join(rows) + "\n")
print(f"{len(rows)} files, {total/1e6:.0f} MB, {time.perf_counter()-t:.1f}s -> {out}")
