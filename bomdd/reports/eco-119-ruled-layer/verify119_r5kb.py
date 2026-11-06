"""ECO-119 rounds 5 to 7 - known-bad of the arms by mutants: this tree's qualification against this tree's validator and hooks
with one mechanism broken.

Old validators cannot parse an entry {path, since} (exit 2), so the known-bad against earlier commits (verify119_r3kb.py) no longer
tells the arms apart. Each mutant here changes one mechanism of E13: seven are round 5's (R8-4-06), six round 6's (R8-5-07: each
puts back one way round 5 read an input), six round 7's (R8-6-05: three of them break the commit-msg hook, the first mutants of a
hook), and two round 8's (R8-7-03: the inspector's i1 and i2). A product is scaffolded by bomdd-init.py from this working tree, its installed process-validator.py (or commit-msg
hook) is replaced with the mutant, and the qualification's OQ runs once. Expected: exactly the named arms FAIL and every other N23
arm PASSes. The product and the qualification's sandboxes (bomdd-oq-* made during the run) are removed afterwards. Writes
out/r5kb-<name>.txt.

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
HOOKS = BOMDD / "method/templates/process-core/hooks"
# a replacement is (old, new) on the validator, or (product path, old, new) on another installed file (a hook)
TARGETS = {"bomdd/tools/process-validator.py": VALIDATOR, "bomdd/hooks/commit-msg": HOOKS / "commit-msg"}
N23_COUNT = 58
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
                       # round 6: N23v2 too (its entry's own since is the branch's HEAD; the field's since is on main's line).
                       # Round 7: N23rb too (the rebased entry's own since is what goes off the line)
                       # Round 8: N23mi too (the merged entry then takes the field's since, which is on the line)
                       {"N23z5", "N23z5b", "N23z7", "N23n2", "N23v2", "N23rb", "N23mi"}),
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
                          # round 8: N23oc too (the profile-less first MERGE_HEAD line counts as a parent with no field)
                          {"N23x", "N23x5", "N23x6", "N23oc"}),
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
                  # round 7: N23pu too (the parent's duplicate key then parses, to the same field as main's)
                  {"N23z3c", "N23pu"}),
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
                   {"N23x6", "N23oc"}),
    "since-touched-only": ("an index entry's since is checked only when its paths are touched (round 5)",
                           [("        if sha is None or not any(si.in_force(sha, p) for p in parents):\n",
                             "        if False:\n")],
                           # round 8: N23mi too (a merge's entry is then never checked)
                           {"N23v2", "N23n", "N23v", "N23mi"}),
    # --- round 7 (R8-6-05): round 6's mechanisms with no arm or mutant, and round 7's changes ---
    "since-all": ("every index entry's since is checked, including those carried over from HEAD (round 6)",
                  [("        if (path, since) in head_entries:\n            continue\n", "")],
                  {"N23rb"}),
    "wt-replay": ("validate's replay takes the field from the profile it loaded, the working tree's when HEAD has none (round 6)",
                  [('    rl = prof.get("ruled_layer") if head_has_profile(root) else None\n',
                    '    rl = prof.get("ruled_layer")\n')],
                  {"N23wt"}),
    "parent-lenient": ("a merge parent's profile that does not parse is taken as no field",
                       [('    d = profile_at(root, f"{rev}:", f"親 {rev[:9]} ", validate=False)\n',
                         '    try:\n        d = profile_at(root, f"{rev}:", f"親 {rev[:9]} ", validate=False)\n'
                         '    except SystemExit:\n        d = None\n')],
                       {"N23pu"}),
    "hook-no-index": ("the commit-msg hook exits before the validator when only the index has the profile (round 5's hook)",
                      [("bomdd/hooks/commit-msg", "    || git cat-file -e :bomdd/process-profile.yaml 2>/dev/null \\\n", "")],
                      {"N23z9b"}),
    "hook-no-merge": ("the commit-msg hook exits before the validator on a merge into a HEAD with no profile (round 5's hook)",
                      [("bomdd/hooks/commit-msg", "    || merge_parent_has_profile \\\n", "")],
                      # round 8: N23x8 too (after the profile's removal the merged index has none, so only the
                      # MERGE_HEAD clause starts the missing validator)
                      {"N23x6", "N23oc", "N23x8"}),
    "hook-merge-any": ("the commit-msg hook starts the validator on every merge (round 6's hook)",
                       [("bomdd/hooks/commit-msg", "    || merge_parent_has_profile \\\n",
                         "    || git rev-parse -q --verify MERGE_HEAD >/dev/null 2>&1 \\\n")],
                       # round 8: N23x8 too (its merge after the branch removed the profile then starts the missing validator)
                       {"N23x7", "N23x8"}),
    # --- round 8 (R8-7-03): the inspector's i1 and i2 ---
    "hook-first-line": ("the commit-msg hook reads only the first line of MERGE_HEAD (octopus parents 2 and later ignored)",
                        [("bomdd/hooks/commit-msg",
                          '  while read -r c; do\n    [ -n "$c" ] && git cat-file -e "$c:bomdd/process-profile.yaml" '
                          '2>/dev/null && return 0\n  done < "$mh"\n',
                          '  read -r c < "$mh"\n  [ -n "$c" ] && git cat-file -e "$c:bomdd/process-profile.yaml" '
                          '2>/dev/null && return 0\n')],
                        {"N23oc"}),
    "merge-skip-since": ("at a merge, the since check of the index entries is skipped",
                         [("    for path, since in ruled_entries(idx_rl):\n        if (path, since) in head_entries:\n",
                           "    for path, since in ([] if others else ruled_entries(idx_rl)):\n"
                           "        if (path, since) in head_entries:\n")],
                         {"N23mi"}),
}


def _rm_readonly(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def mutant(name: str) -> dict[str, str]:
    """{product path: mutated text} - only the files the mutant changes."""
    texts: dict[str, str] = {}
    for rep in MUTANTS[name][1]:
        rel, old, new = rep if len(rep) == 3 else ("bomdd/tools/process-validator.py", *rep)
        src = texts.get(rel) or TARGETS[rel].read_text(encoding="utf-8")
        assert src.count(old) == 1, f"{name}: anchor found {src.count(old)} times in {rel}: {old[:60]!r}"
        texts[rel] = src.replace(old, new)
    for rel, src in texts.items():
        if rel.endswith(".py"):
            compile(src, f"mutant-{name}", "exec")
        else:  # a hook: sh -n parses it without running it
            p = subprocess.run(["sh", "-n"], input=src, capture_output=True, text=True, encoding="utf-8", errors="replace")
            assert p.returncode == 0, f"{name}: {rel} does not parse: {p.stderr.strip()}"
    return texts


def main():
    if sys.argv[1] == "--list":
        for k, (what, _, exp) in MUTANTS.items():
            print(f"{k} ({', '.join(sorted(mutant(k)))}): {what}; expected FAIL {sorted(exp)}")
        return
    name = sys.argv[1]
    what, _, expect = MUTANTS[name]
    texts = mutant(name)
    OUT.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f"eco119-r5kb-{name}-"))
    lines = [f"# known-bad (round 5): this tree's qualification against the mutant '{name}' - {what}"]
    try:
        p = subprocess.run([sys.executable, str(BOMDD / "method/tools/bomdd-init.py"), "R5KB", "--dir", str(tmp), "--no-gui",
                            "--no-qualify"], capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
        assert p.returncode == 0, p.stderr
        prod = tmp / "R5KB"
        for rel, src in texts.items():
            (prod / rel).write_text(src, encoding="utf-8", newline="\n")
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
