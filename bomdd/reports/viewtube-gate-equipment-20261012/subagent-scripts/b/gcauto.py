"""Does `git commit` after `git add -A` of >6700 new files trigger auto gc/maintenance, and what does it cost?"""
import os, subprocess, sys, tempfile, time, shutil

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
SIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gcwork")
shutil.rmtree(base, ignore_errors=True)
os.makedirs(base)


def make(name, extra):
    root = os.path.join(base, name)
    os.makedirs(root)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "x"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "x@x.invalid"], cwd=root, check=True)
    for k, v in extra:
        subprocess.run(["git", "config", k, v], cwd=root, check=True)
    for i in range(N):
        d = os.path.join(root, f"d{i % 50}")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"f{i}.txt"), "wb") as h:
            h.write(os.urandom(SIZE // 2).hex().encode())
    t = time.time(); subprocess.run(["git", "add", "-A"], cwd=root, check=True); add = time.time() - t
    t = time.time(); subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "fixture"], cwd=root, check=True); commit = time.time() - t
    packs = len([f for f in os.listdir(os.path.join(root, ".git", "objects", "pack")) if f.endswith(".pack")])
    print(f"{name:12} add={add:6.2f}s commit={commit:6.2f}s packs_after_commit={packs}")


make("default", [])
make("gc_off", [("gc.auto", "0"), ("maintenance.auto", "false")])
shutil.rmtree(base, ignore_errors=True)
