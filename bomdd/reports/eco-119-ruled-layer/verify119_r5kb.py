"""ECO-119 rounds 5 and 6 - known-bad of the arms by mutants: this tree's qualification against this tree's validator with one
mechanism broken.

Old validators cannot parse an entry {path, since} (exit 2), so the known-bad against earlier commits (verify119_r3kb.py) no longer
tells the arms apart. Each mutant here changes one mechanism of E13: the first seven are round 5's (R8-4-06), the last six round
6's (R8-5-07: each puts back one way round 5 read an input). A product is scaffolded by bomdd-init.py from this working tree, its
installed process-validator.py is replaced with the mutant, and the qualification's OQ runs once. Expected: exactly the named arms
FAIL and every other N23 arm PASSes. The product and the qualification's sandboxes (bomdd-oq-* made during the run) are removed
afterwards. Writes out/r5kb-<name>.txt.

Not armed (declared, order 4K): the want/duplicate guard of the raw framing and the replay's guard "since の後の親が無い" - no input
reaches either.

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
N23_COUNT = 50
ENV = dict(os.environ, GIT_AUTHOR_NAME="eco119-r5kb", GIT_AUTHOR_EMAIL="r5kb@bomdd.invalid",
           GIT_COMMITTER_NAME="eco119-r5kb", GIT_COMMITTER_EMAIL="r5kb@bomdd.invalid")

REPLAY_DIE = ('                if base is None:  # 防御(R8-5-07): --ancestry-path の行の親は s か s の子孫なので、入力ではここに来ない\n'
              '                    die(f"{sha[:9]} に since の後の親が無い(裁定層の履歴検査が測定不能)")\n')
REPLAY_SKIP = '                if base is None:\n                    continue\n'
OLD_FRAMING = ('    out = {}\n'
               '    for chunk in p.stdout.split("\\x01")[1:]:\n'
               '        sha, sep, rest = chunk.partition("\\0")\n'
               '        if not sep or sha not in want or sha in out:\n'
               '            out = None\n'
               '            break\n'
               '        out[sha] = [x for x in (rest[1:] if rest.startswith("\\n") else rest).split("\\0") if x]\n')
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
                       # round 6: N23v2 too (its entry's own since is the branch's HEAD; the field's since is on main's line)
                       {"N23z5", "N23z5b", "N23z7", "N23n2", "N23v2"}),
    "no-index": ("the first layer judges with HEAD's field only (the index's field not used)",
                 [("ents = list(dict.fromkeys(ruled_entries(head_rl) + ruled_entries(idx_rl)))",
                   "ents = list(dict.fromkeys(ruled_entries(head_rl)))")],
                 # round 5: N23n2 added after the first full run (order 4I). Round 6: N23n2 is now also refused by the index
                 # entry's since check, which this mutant keeps, so it leaves; N23z9b (the index's profile only) joins
                 {"N23s", "N23z2", "N23z9", "N23z9b"}),
    "no-index-check": ("the index's profile is not validated (strict parse kept)",
                       [('d = profile_at(root, ":", "index ", validate=True)',
                         'd = profile_at(root, ":", "index ", validate=False)')],
                       {"N23z3", "N23z3b"}),
    "fieldless-parents": ("the merge field check counts parents without the field (as None)",
                          [("held = [r for r in (ruled_layer_of(root, p) for p in parents) if r is not None]",
                            "held = [ruled_layer_of(root, p) for p in parents]")],
                          {"N23x", "N23x5", "N23x6"}),
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
    # --- round 6 (R8-5-07): each puts back one way round 5 read an E13 input ---
    "order-fallback": ("the first layer reads the order from the index, then falls back to HEAD (round 5)",
                       [('        p = run_git(root, "show", f":{ref}")\n        return p.stdout if p.returncode == 0 else None\n',
                         '        for spec in (f":{ref}", f"HEAD:{ref}"):\n            p = run_git(root, "show", spec)\n'
                         '            if p.returncode == 0:\n                return p.stdout\n        return None\n')],
                       {"N23e2"}),
    "safe-load": ("profiles are parsed with yaml.safe_load (round 5) - duplicate keys pass",
                  [("        d = strict_load(p.stdout)\n    except yaml.YAMLError as e:\n",
                    "        d = yaml.safe_load(p.stdout)\n    except yaml.YAMLError as e:\n")],
                  {"N23z3c"}),
    "name-only": ("the replay's paths read from --name-only -z split on \\x01 (round 5)",
                  [('["git", "-C", str(root), "diff-tree", "--stdin", "-r", "--raw", "-z", "--no-renames"]',
                    '["git", "-C", str(root), "diff-tree", "--stdin", "-r", "--no-renames", "--name-only", "-z", '
                    '"--format=%x01%H"]'),
                   ("    out = parse_raw_z(p.stdout, want)\n", OLD_FRAMING)],
                  {"N23fr"}),
    "wt-profile": ("with no profile at HEAD, the hook modes read the working tree's profile, not the index's (round 5)",
                   [("prof = load_profile(root, head_preferred=True, index_fallback=hook)",
                     "prof = load_profile(root, head_preferred=True, index_fallback=False)")],
                   {"N23z9b"}),
    "exit-first": ("the no-profile exit comes before the merge field check (round 5)",
                   [('        if a.mode == "commit-msg" and head_exists(root):\n', '        if False:\n')],
                   {"N23x6"}),
    "since-touched-only": ("an index entry's since is checked only when its paths are touched (round 5)",
                           [("        if sha is None or not any(si.in_force(sha, p) for p in parents):\n",
                             "        if False:\n")],
                           {"N23v2", "N23n", "N23v"}),
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
        # the qualification's sandboxes (tempfile, prefix bomdd-oq-) go under tmp, so they are removed with it (2:a, order 4J)
        qenv = dict(ENV, TMP=str(tmp), TEMP=str(tmp), TMPDIR=str(tmp))
        subprocess.run([sys.executable, str(prod / "bomdd/tools/process-qualification.py"), "--root", str(prod), "--mode", "oq",
                        "--runs", "1", "--json", str(j)], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=qenv, timeout=1800)
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
