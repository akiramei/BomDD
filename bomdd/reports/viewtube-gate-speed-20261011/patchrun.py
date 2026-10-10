"""Run a ViewTube validator with in-memory source patches, without writing to ViewTube.

usage: python patchrun.py <validator.py> <patches.py> <name> -- <validator args...>
The validator source is read, each (old, new) pair of PATCHES[name] is applied (old must occur
exactly once), and the result is executed as __main__ with __file__ set to the original path, so
path resolution (REPO_ROOT = parents[2]) is unchanged.
"""
import runpy
import sys
from pathlib import Path

target = Path(sys.argv[1]).resolve()
patches = runpy.run_path(sys.argv[2])["PATCHES"][sys.argv[3]]
rest = sys.argv[sys.argv.index("--") + 1:]
source = target.read_text(encoding="utf-8")
for old, new in patches:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"patch anchor occurs {count} times: {old[:80]!r}")
    source = source.replace(old, new)
sys.argv = [str(target), *rest]
sys.path.insert(0, str(target.parent))
code = compile(source, str(target), "exec")
glb = {"__name__": "__main__", "__file__": str(target)}
exec(code, glb)
