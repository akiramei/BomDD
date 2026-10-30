"""Store the mutants as line edits against the clean mock, and rebuild them byte for byte (the 31 copies are 3.6 MB).

    python record_mutants.py pack   <mock.html> <mutants-dir> <mutants.json> <mutant-edits.json>
    python record_mutants.py verify <mock.html> <mutant-edits.json> [<mutants-dir>]   # rebuild; compare to the files if given
"""
import difflib
import hashlib
import json
import pathlib
import sys


def lines(p):
    return pathlib.Path(p).read_bytes().decode("utf-8").splitlines(keepends=True)


def pack(mock, mdir, mjson, out):
    base = lines(mock)
    rows = []
    for m in json.load(open(mjson, encoding="utf-8")):
        path = pathlib.Path(mdir) / m["file"]
        new = lines(path)
        ops = [[tag, i1, i2, new[j1:j2]] for tag, i1, i2, j1, j2 in
               difflib.SequenceMatcher(a=base, b=new, autojunk=False).get_opcodes() if tag != "equal"]
        rows.append(dict(m, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), edits=ops))
    pathlib.Path(out).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"packed {len(rows)}")


def rebuild(base, ops):
    out, pos = [], 0
    for tag, i1, i2, new in ops:
        out += base[pos:i1]
        out += new
        pos = i2
    out += base[pos:]
    return "".join(out).encode("utf-8")


def verify(mock, edits, mdir=None):
    base = lines(mock)
    bad = 0
    for r in json.load(open(edits, encoding="utf-8")):
        data = rebuild(base, r["edits"])
        ok = hashlib.sha256(data).hexdigest() == r["sha256"]
        if mdir is not None:
            ok = ok and data == (pathlib.Path(mdir) / r["file"]).read_bytes()
        bad += 0 if ok else 1
    print(f"verified {'all' if not bad else 'NOT all'}: {bad} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1] == "pack":
        pack(*sys.argv[2:6])
    else:
        sys.exit(verify(*sys.argv[2:5]))
