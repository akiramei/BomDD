"""ECO-119 round 5 - known-bad of the arms by mutants: this tree's qualification against this tree's validator with one mechanism
broken.

Old validators cannot parse an entry {path, since} (exit 2), so the known-bad against earlier commits (verify119_r3kb.py) no longer
tells the arms apart. Each mutant here changes one mechanism of round 5's E13 (R8-4-06). A product is scaffolded by bomdd-init.py
from this working tree, its installed process-validator.py is replaced with the mutant, and the qualification's OQ runs once.
Expected: exactly the named arms FAIL and every other N23 arm PASSes. The product is removed afterwards. Writes out/r5kb-<name>.txt.

usage: python verify119_r5kb.py <mutant name> | --list
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
BOMDD = HERE.parents[2]
OUT = HERE / "out"
VALIDATOR = BOMDD / "method/templates/process-core/tools/process-validator.py"
N23_COUNT = 44
ENV = dict(os.environ, GIT_AUTHOR_NAME="eco119-r5kb", GIT_AUTHOR_EMAIL="r5kb@bomdd.invalid",
           GIT_COMMITTER_NAME="eco119-r5kb", GIT_COMMITTER_EMAIL="r5kb@bomdd.invalid")

REPLAY_DIE = ('                if base is None:\n'
              '                    die(f"{sha[:9]} に since の後の親が無い(裁定層の履歴検査が測定不能)")\n')
REPLAY_SKIP = '                if base is None:\n                    continue\n'
AFTER = "            after = {s} | {r[0] for r in rows}\n"

# name: (what it breaks, [(old, new)], the arms expected to FAIL)
MUTANTS = {
    # the "since off the line" refusal keeps its own test (since is not B or an ancestor of any parent): a since equal to the
    # base parent is "not yet in force" under this mutant, not unmeasurable (the first run conflated the two - order 4I)
    "strict": ("an entry is in force only strictly after its since (not at it), in both layers",
               [("base = next((p for p in parents if si.in_force(sha, p)), None) if sha else None",
                 "base = next((p for p in parents if si.in_force(sha, p) and sha != p), None) if sha else None"),
                ("            t = covered(staged_head, [path])\n            if t:\n",
                 "            t = covered(staged_head, [path])\n"
                 "            if t and not (sha and any(si.in_force(sha, p) for p in parents)):\n"),
                (AFTER, "            after = {r[0] for r in rows}\n"), (REPLAY_DIE, REPLAY_SKIP)],
               {"N23z2", "N23z2r"}),
    "no-entry-since": ("every entry takes the field's since (an entry's own since is ignored)",
                       [('else (x["path"], x["since"]) for x in rl["paths"]]', 'else (x["path"], rl["since"]) for x in rl["paths"]]')],
                       {"N23z5", "N23z5b", "N23z7", "N23n2"}),
    "no-index": ("the first layer judges with HEAD's field only (the index's field not used)",
                 [("ents = list(dict.fromkeys(ruled_entries(head_rl) + ruled_entries(idx_rl)))",
                   "ents = list(dict.fromkeys(ruled_entries(head_rl)))")],
                 # N23n2 added after the first full run: its entry exists only in the index (order 4I)
                 {"N23s", "N23z2", "N23z9", "N23n2"}),
    "no-index-check": ("the index's field is not validated",
                       [('        if errs:\n            die("index の profile の ruled_layer が不正(裁定層の判定が測定不能): "'
                         ' + "・".join(errs))\n', "")],
                       {"N23z3", "N23z3b"}),
    "fieldless-parents": ("the merge field check counts parents without the field (as None)",
                          [("held = [r for r in (ruled_layer_of(root, p) for p in parents) if r is not None]",
                            "held = [ruled_layer_of(root, p) for p in parents]")],
                          {"N23x", "N23x5"}),
    "pathspec": ("the replay's candidates filtered by a literal git pathspec of the entries (as round 4)",
                 [(AFTER, AFTER + '            keep = set(run_git(root, "--literal-pathspecs", "rev-list", "--full-history", '
                                  '"--no-merges", "--ancestry-path", f"{s}..HEAD", "--", *paths).stdout.split())\n'
                                  '            rows = [r for r in rows if r[0] in keep or len(r) > 2]\n')],
                 {"N23z8"}),
    "first-parent": ("a merge is judged only against its first parent, in both layers",
                     [("base = next((p for p in parents if si.in_force(sha, p)), None) if sha else None",
                       "base = next((p for p in parents[:1] if si.in_force(sha, p)), None) if sha else None"),
                      ("            t = covered(staged_head, [path])\n            if t:\n",
                       "            t = covered(staged_head, [path])\n            if t and not others:\n"),
                      ("base = next((p for p in parents if p in after), None)",
                       "base = next((p for p in parents[:1] if p in after), None)"),
                      (REPLAY_DIE, REPLAY_SKIP)],
                     {"N23s", "N23m"}),
}


def _rm_readonly(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def mutant(name: str) -> str:
    src = VALIDATOR.read_text(encoding="utf-8")
    for old, new in MUTANTS[name][1]:
        assert src.count(old) == 1, f"{name}: anchor found {src.count(old)} times: {old[:60]!r}"
        src = src.replace(old, new)
    compile(src, f"mutant-{name}", "exec")
    return src


def main():
    if sys.argv[1] == "--list":
        for k, (what, _, exp) in MUTANTS.items():
            mutant(k)
            print(f"{k}: {what}; expected FAIL {sorted(exp)}")
        return
    name = sys.argv[1]
    what, _, expect = MUTANTS[name]
    src = mutant(name)
    OUT.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f"eco119-r5kb-{name}-"))
    lines = [f"# known-bad (round 5): this tree's qualification against the mutant '{name}' - {what}"]
    try:
        p = subprocess.run([sys.executable, str(BOMDD / "method/tools/bomdd-init.py"), "R5KB", "--dir", str(tmp), "--no-gui",
                            "--no-qualify"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
        assert p.returncode == 0, p.stderr
        prod = tmp / "R5KB"
        (prod / "bomdd/tools/process-validator.py").write_text(src, encoding="utf-8", newline="\n")
        j = tmp / "r5kb.json"
        subprocess.run([sys.executable, str(prod / "bomdd/tools/process-qualification.py"), "--root", str(prod), "--mode", "oq",
                        "--runs", "1", "--json", str(j)], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=ENV, timeout=1800)
        cs = [c for c in json.loads(j.read_text(encoding="utf-8"))["oq"] if c["control"].startswith("N23")]
        failed = {c["control"] for c in cs if not c["pass"]}
        for c in cs:
            lines.append(f"[{c['control']}] {'PASS' if c['pass'] else 'FAIL'} - {c['detail'][:160]}")
        ok = failed == expect and len(cs) == N23_COUNT
        lines.append(f"N23 controls {len(cs)}; FAIL {sorted(failed)}; expected FAIL {sorted(expect)}")
        lines.append(f"known-bad: {'as expected' if ok else 'NOT as expected'}")
    finally:
        shutil.rmtree(tmp, onerror=_rm_readonly)
        lines.append(f"throwaway product removed: {not tmp.exists()}")
    (OUT / f"r5kb-{name}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines[-3:]))


if __name__ == "__main__":
    main()
