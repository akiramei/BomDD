"""Cost of `git add -A` with default loose compression vs core.looseCompression=0, same files."""
import os, subprocess, sys, time, shutil

N = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
SIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "addwork")
shutil.rmtree(base, ignore_errors=True)
src = os.path.join(base, "src")
for i in range(N):
    d = os.path.join(src, f"d{i % 50}")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"f{i}.txt"), "wb") as h:
        h.write(os.urandom(SIZE // 2).hex().encode())

for name, cfg in (("default", []), ("loose0", [("core.looseCompression", "0")]), ("default2", [])):
    root = os.path.join(base, name)
    shutil.copytree(src, root)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    for k, v in cfg + [("gc.auto", "0")]:
        subprocess.run(["git", "config", k, v], cwd=root, check=True)
    t = time.time(); subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    print(f"{name:9} add={time.time() - t:6.2f}s")
shutil.rmtree(base, ignore_errors=True)
