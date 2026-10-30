"""Hash the run's inputs before an agent starts, and compare later (definitions.md section 8).

    python seal_inputs.py write <staging> <out.json>
    python seal_inputs.py check <staging> <sealed.json>     # exit 1 on any difference
Covers authority/ (every file), bindings.json, the harness dll and the writer prompt.
"""
import hashlib
import json
import pathlib
import sys


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def collect(staging):
    st = pathlib.Path(staging)
    out = {}
    for p in sorted((st / "authority").rglob("*")):
        if p.is_file() and "bin" not in p.relative_to(st / "authority").parts[:1] and "obj" not in p.relative_to(st / "authority").parts[:1]:
            out[str(p.relative_to(st)).replace("\\", "/")] = digest(p)
    for rel in ("bindings.json", "harness/bin/Debug/net10.0/Harness.dll", "writer/prompt.md"):
        p = st / rel
        out[rel] = digest(p) if p.is_file() else None
    return out


if __name__ == "__main__":
    cmd, staging, path = sys.argv[1:4]
    if cmd == "write":
        h = collect(staging)
        pathlib.Path(path).write_text(json.dumps(h, indent=1), encoding="utf-8")
        print(f"sealed {len(h)} files")
    else:
        old = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        new = collect(staging)
        diff = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        print(f"files {len(new)} differing {len(diff)}")
        for k in diff[:20]:
            print("  ", k)
        sys.exit(1 if diff else 0)
