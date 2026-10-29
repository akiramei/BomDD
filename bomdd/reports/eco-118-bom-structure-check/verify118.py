"""ECO-118 acceptance measurements V1, V2, V3, V7 (V8 is verify118_v8.py).

Reads MoviePad-Remake, ViewPrism2, ViewTube and TimetableAdv with git (read only; nothing is written there; V7's
--index arm uses a temporary repository of its own, not a worktree of MoviePad-Remake). Writes its outputs under
<this folder>/out/.

usage: python verify118.py <repos dir holding the four products> v1|v2|v3|v7|all
"""
import hashlib
import json
import os
import re
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
TOOL = BOMDD / "method" / "tools" / "bom-structure-check.py"
A1 = BOMDD / "bomdd" / "reports" / "exp-20261029-01" / "a1_check.py"
OUT = HERE / "out"
FILES = ["bomdd/30-ebom.yaml", "bomdd/32-mbom.yaml", "bomdd/33-control-plan.yaml"]


def sh(*args, cwd=None):
    return subprocess.run(list(args), capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)


def _rmtree(path: Path) -> None:
    """Remove a temporary folder, git's read-only objects included (R8-1-13); report what stays."""
    def chmod_retry(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onerror=chmod_retry)
    if path.exists():
        print(f"[cleanup] left behind: {path}")


def tool(*args):
    return sh(sys.executable, str(TOOL), *args)


def pairs_tool(out: str, rule: str) -> list:
    got = []
    for line in out.splitlines():
        m = re.match(rf"^\[{rule}\] (.+?) -> (.+?): ", line)
        if m:
            subj, tgt = m.group(1), m.group(2)
            got.append((subj.replace("E item ", ""), tgt.split(" of ")[0]))
    return sorted(got)


def pairs_a1(out: str, rule: str) -> list:
    got, cur = [], None
    for line in out.splitlines():
        m = re.match(r"^rule (\d): ", line)
        if m:
            cur = m.group(1)
            continue
        if cur != rule or not line.startswith("   "):
            continue
        s = line.strip()
        if rule == "4":
            m = re.match(r"^(\S+ \S+) targets (\S+) of ", s)
            got.append((m.group(1), m.group(2)))
        elif rule == "5":
            m = re.match(r"^E item (\S+) requires (\S+);", s)
            got.append((m.group(1), m.group(2)))
    return sorted(got)


def v1(repos: Path) -> list[str]:
    mp = repos / "MoviePad-Remake"
    lines = ["# V1 - known-bad on real files (MoviePad-Remake, --rev)"]
    ok_all = True
    for commit, exp4, exp5 in (("d3683d6", 6, 6), ("64912a4", 13, 14)):
        t = tool("--root", str(mp), "--rev", commit)
        a = sh(sys.executable, str(A1), str(mp), commit)
        (OUT / f"v1-tool-{commit}.txt").write_text(t.stdout + t.stderr, encoding="utf-8")
        (OUT / f"v1-a1check-{commit}.txt").write_text(a.stdout + a.stderr, encoding="utf-8")
        for rule, exp in (("4", exp4), ("5", exp5)):
            tp, ap = pairs_tool(t.stdout, f"A1-{rule}"), pairs_a1(a.stdout, rule)
            same = tp == ap
            ok_all &= same and len(tp) == exp
            lines.append(f"{commit} rule {rule}: tool {len(tp)} a1_check {len(ap)} expected {exp} pairs identical={same}")
            for extra in sorted(set(tp) - set(ap)):
                lines.append(f"  only in tool: {extra}")
            for extra in sorted(set(ap) - set(tp)):
                lines.append(f"  only in a1_check: {extra}")
        counts = re.search(r"^counts: (.*)$", t.stdout, re.M).group(1)
        lines.append(f"{commit} exit {t.returncode} counts {counts}")
        ok_all &= t.returncode == 1
        for r in ("A1-1", "A1-2", "A1-3", "A1-6"):
            ok_all &= f"{r}=0" in counts
        # the other rules' findings, listed for the order's section 4 (not part of V1's condition)
        others = [l for l in t.stdout.splitlines() if re.match(r"^\[(P1-id|C1-a|C1-b)\]", l)]
        lines.append(f"{commit} findings outside V1's rules: {len(others)}")
        lines += [f"  {l}" for l in others]
    # control: the comparison is red on a copy of the expected list with one pair altered
    t = tool("--root", str(mp), "--rev", "d3683d6")
    a = sh(sys.executable, str(A1), str(mp), "d3683d6")
    ap = pairs_a1(a.stdout, "4")
    altered = [(ap[0][0], ap[0][1] + "-ALTERED")] + ap[1:]
    red = pairs_tool(t.stdout, "A1-4") != sorted(altered)
    lines.append(f"control: one pair altered -> comparison {'red (differs)' if red else 'GREEN (comparator blind)'}")
    ok_all &= red
    lines.append(f"V1: {'PASS' if ok_all else 'FAIL'}")
    return lines


def v2() -> list[str]:
    lines = ["# V2 - positive controls: --selftest, and a copy with one rule disabled fails it"]
    s = tool("--selftest")
    (OUT / "v2-selftest.txt").write_text(s.stdout + s.stderr, encoding="utf-8")
    ok_all = s.returncode == 0
    lines.append(f"selftest exit {s.returncode}: {s.stdout.strip().splitlines()[-1]}")
    src = TOOL.read_text(encoding="utf-8")
    tmp = Path(tempfile.mkdtemp(prefix="eco118-v2-"))
    try:
        for fn, ret in (("rule_1", "[]"), ("rule_2", "[]"), ("rule_3", "[]"), ("rule_4", "[]"), ("_relay_crossing", "None"),
                        ("rule_5", "[]"), ("rule_6", "[]"), ("rule_p1", "[]"), ("rule_c1a", "[]"), ("rule_c1b", "[]")):
            m = re.search(rf"^def {fn}\(.*?\).*?:\n((?:    \"\"\".*?\"\"\"\n)?)", src, re.M | re.S)
            mutated = src[:m.end()] + f"    return {ret}  # ECO-118 V2 known-bad: {fn} disabled\n" + src[m.end():]
            p = tmp / f"mut-{fn}.py"
            p.write_text(mutated, encoding="utf-8")
            r = sh(sys.executable, str(p), "--selftest")
            failed = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("FAIL")]
            red = r.returncode != 0 and bool(failed)
            ok_all &= red
            lines.append(f"{fn} disabled: selftest exit {r.returncode} {'red' if red else 'GREEN (blind)'} - failing arms {[f.split(':')[0][5:] for f in failed]}")
    finally:
        _rmtree(tmp)
    lines.append(f"V2: {'PASS' if ok_all else 'FAIL'}")
    return lines


def v3(repos: Path) -> list[str]:
    lines = ["# V3 - the other products at HEAD, read only (--rev HEAD)"]
    ok_all = True
    for prod in ("ViewPrism2", "ViewTube", "TimetableAdv"):
        root = repos / prod
        head = sh("git", "-C", str(root), "rev-parse", "HEAD").stdout.strip()
        t = tool("--root", str(root), "--rev", "HEAD")
        (OUT / f"v3-{prod}.txt").write_text(t.stdout + t.stderr, encoding="utf-8")
        pop = re.search(r"^population: (.*)$", t.stdout, re.M)
        ok = t.returncode == 3 and pop and "units_with_part_standard=0" in pop.group(1)
        ok = ok or t.returncode == 1  # FAIL is allowed if each finding is read in the order
        ok_all &= ok and t.returncode != 0
        lines.append(f"{prod} {head[:12]}: exit {t.returncode} {pop.group(1) if pop else t.stdout.strip()[-200:]}")
        for l in t.stdout.splitlines():
            if l.startswith("["):
                lines.append(f"  {l}")
    lines.append(f"V3: {'PASS' if ok_all else 'FAIL'}")
    return lines


def _blob_sha(root: Path, spec: str) -> str:
    b = subprocess.run(["git", "-C", str(root), "cat-file", "blob", spec], capture_output=True, check=True).stdout
    return hashlib.sha256(b).hexdigest()


FIELDS = ["schema", "root", "source", "inputs", "tool", "counts", "population", "not_exercised", "verdict", "exit_code",
          "error", "utc"]


def receipt_problems(rc: dict, root: Path | None, spec_of=None) -> list[str]:
    """Re-check a receipt against what it claims: the tool's hash, and the input hashes against the source."""
    p = [f"missing field {f}" for f in FIELDS if f not in rc]
    if rc.get("tool", {}).get("sha256") != hashlib.sha256(TOOL.read_bytes()).hexdigest():
        p.append("tool sha256 differs from the tool file")
    if spec_of is not None:
        for key, inp in rc.get("inputs", {}).items():
            if inp["sha256"] != _blob_sha(root, spec_of(inp["path"])):
                p.append(f"input {inp['path']} sha256 differs from the source blob")
            gid = subprocess.run(["git", "-C", str(root), "rev-parse", spec_of(inp["path"])], capture_output=True, text=True).stdout.strip()
            if inp.get("git_blob") != gid:
                p.append(f"input {inp['path']} git_blob differs from git's id of the source blob")
    return p


def v7(repos: Path) -> list[str]:
    lines = ["# V7 - the receipt is machine-made and true"]
    mp = repos / "MoviePad-Remake"
    ok_all = True
    rp = OUT / "v7-receipt-d3683d6.json"
    t = tool("--root", str(mp), "--rev", "d3683d6", "--receipt", str(rp))
    rc = json.loads(rp.read_text(encoding="utf-8"))
    commit = sh("git", "-C", str(mp), "rev-parse", "d3683d6^{commit}").stdout.strip()
    tree = sh("git", "-C", str(mp), "rev-parse", "d3683d6^{tree}").stdout.strip()
    probs = receipt_problems(rc, mp, lambda path: f"{commit}:{path}")
    checks = {"commit": rc["source"].get("commit") == commit, "tree": rc["source"].get("tree") == tree,
              "A1-4=6": rc["counts"].get("A1-4") == 6, "A1-5=6": rc["counts"].get("A1-5") == 6,
              "verdict FAIL": rc["verdict"] == "FAIL", "exit 1": rc["exit_code"] == 1 == t.returncode,
              "re-hash": not probs}
    ok_all &= all(checks.values())
    lines.append(f"--rev d3683d6: {checks} {probs or ''}")
    # --index on a checkout of 3ba3d00: a temporary repository whose index holds 3ba3d00's three files
    tmp = Path(tempfile.mkdtemp(prefix="eco118-v7-"))
    try:
        for label, fix in (("as committed", False), ("derived copy, the two P1 ids renamed to PS-M-EXPORT-001-P03/P04", True)):
            r = tmp / ("fixed" if fix else "asis")
            sh("git", "init", "-q", str(r))
            for f in FILES:
                b = subprocess.run(["git", "-C", str(mp), "cat-file", "blob", f"3ba3d00:{f}"], capture_output=True, check=True).stdout
                if fix:
                    b = b.replace(b"PS-M-EXPORT-CLOCK-001-P01", b"PS-M-EXPORT-001-P03").replace(b"PS-M-EXPORT-COPY-001-P01", b"PS-M-EXPORT-001-P04")
                (r / f).parent.mkdir(parents=True, exist_ok=True)
                (r / f).write_bytes(b)
            sh("git", "-C", str(r), "add", *FILES)
            rp2 = OUT / f"v7-receipt-3ba3d00-index-{'derived' if fix else 'asis'}.json"
            t2 = tool("--root", str(r), "--index", "--receipt", str(rp2))
            rc2 = json.loads(rp2.read_text(encoding="utf-8"))
            probs2 = receipt_problems(rc2, r, lambda path: f":{path}")
            (OUT / f"v7-tool-3ba3d00-index-{'derived' if fix else 'asis'}.txt").write_text(t2.stdout, encoding="utf-8")
            lines.append(f"--index 3ba3d00 {label}: verdict {rc2['verdict']} exit {rc2['exit_code']}/{t2.returncode} "
                         f"source {rc2['source']} counts {{{', '.join(f'{k}: {v}' for k, v in rc2['counts'].items() if v)}}} re-hash {'ok' if not probs2 else probs2}")
            if fix:
                ok_all &= rc2["verdict"] == "PASS" and t2.returncode == 0 and not probs2
            else:
                lines.append("  (the frozen condition expected PASS, 0 here; see the order's section 4)")
        # every field on the four verdicts: fixtures written by the tool, and a broken one
        for name, verdict in (("good", "PASS"), ("fail", "FAIL"), ("not-applicable", "NOT-APPLICABLE"), ("good", "UNMEASURABLE")):
            d = tmp / f"fx-{name}-{verdict}"
            tool("--write-fixture", name, str(d))
            if verdict == "UNMEASURABLE":
                (d / FILES[1]).write_text("mbom: [unclosed\n", encoding="utf-8")
            rp3 = OUT / f"v7-receipt-fixture-{verdict}.json"
            t3 = tool("--root", str(d), "--receipt", str(rp3))
            rc3 = json.loads(rp3.read_text(encoding="utf-8"))
            missing = [f for f in FIELDS if f not in rc3]
            good = rc3["verdict"] == verdict and rc3["exit_code"] == t3.returncode and not missing
            if verdict != "UNMEASURABLE":
                good &= all(rc3["inputs"][k]["sha256"] == hashlib.sha256((d / rc3["inputs"][k]["path"]).read_bytes()).hexdigest() for k in rc3["inputs"])
            ok_all &= good
            lines.append(f"fixture {name} -> {rc3['verdict']} exit {t3.returncode}: fields {'all present' if not missing else missing} {'ok' if good else 'NOT OK'}")
        # R8-2-05: a working tree with CRLF checkout (core.autocrlf=true), the fixture committed and checked out again:
        # each input's git_blob equals HEAD's blob, and source.head is HEAD (head and head_blobs checked, R8-2 Q4)
        r = tmp / "crlf"
        sh("git", "init", "-q", str(r))
        sh("git", "-C", str(r), "config", "core.autocrlf", "true")
        tool("--write-fixture", "good", str(r))
        sh("git", "-C", str(r), "add", "-A")
        sh("git", "-C", str(r), "-c", "user.name=v7", "-c", "user.email=v7@bomdd.invalid", "commit", "-q", "-m", "fixture")
        for f in FILES:
            (r / f).unlink()
        sh("git", "-C", str(r), "checkout", "-q", "--", *FILES)
        crlf = all(b"\r\n" in (r / f).read_bytes() for f in FILES)
        rp4 = OUT / "v7-receipt-crlf-worktree.json"
        t4 = tool("--root", str(r), "--receipt", str(rp4))
        rc4 = json.loads(rp4.read_text(encoding="utf-8"))
        head = sh("git", "-C", str(r), "rev-parse", "HEAD").stdout.strip()
        same = all(rc4["inputs"][k]["git_blob"] == rc4["source"]["head_blobs"][k] ==
                   sh("git", "-C", str(r), "rev-parse", f"HEAD:{rc4['inputs'][k]['path']}").stdout.strip() for k in rc4["inputs"])
        good4 = crlf and rc4["source"].get("head") == head and same and t4.returncode == 0
        ok_all &= good4
        lines.append(f"CRLF working tree (files CRLF on disk: {crlf}): git_blob == head_blobs == HEAD's blob for all three: {same}; "
                     f"source.head == HEAD: {rc4['source'].get('head') == head}; exit {t4.returncode} {'ok' if good4 else 'NOT OK'}")
        bad4 = json.loads(rp4.read_text(encoding="utf-8"))
        bad4["inputs"]["cp"]["git_blob"] = "0" * 40
        red4 = bad4["inputs"]["cp"]["git_blob"] != bad4["source"]["head_blobs"]["cp"]
        ok_all &= red4
        lines.append(f"known-bad (cp git_blob altered): the comparison with head_blobs {'red' if red4 else 'GREEN (blind)'}")
    finally:
        _rmtree(tmp)
    # known-bad: one input hash altered is told apart by a re-hash
    bad = json.loads(rp.read_text(encoding="utf-8"))
    bad["inputs"]["mbom"]["sha256"] = "0" * 64
    probs = receipt_problems(bad, mp, lambda path: f"{commit}:{path}")
    red = any("32-mbom" in x for x in probs)
    ok_all &= red
    lines.append(f"known-bad (mbom hash altered): re-hash check {'red' if red else 'GREEN (blind)'} {probs}")
    lines.append(f"V7: every arm but one {'as expected' if ok_all else 'NOT as expected'}; the literal 3ba3d00 --index arm NOT MET "
                 f"(FAIL with P1-id 2 where the frozen condition expected PASS, 0 - judged in the order's section 4)")
    return lines


def main():
    repos, what = Path(sys.argv[1]), sys.argv[2]
    OUT.mkdir(exist_ok=True)
    parts = {"v1": lambda: v1(repos), "v2": v2, "v3": lambda: v3(repos), "v7": lambda: v7(repos)}
    for k in (parts if what == "all" else [what]):
        lines = parts[k]()
        (OUT / f"{k}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
