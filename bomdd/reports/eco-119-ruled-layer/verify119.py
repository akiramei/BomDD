"""ECO-119 V1 - MoviePad-Remake's ruled-layer history replayed through E13 in a throwaway product made by bomdd-init.py.

The product gets the profile field ruled_layer {since: bom-v4, paths: the four ruled files and bomdd/reports/adr/}. E12 is
switched off in the same profile commit (structure_check removed) so that only E13 is measured: the copied E-BOM sits beside the
template M-BOM and Control Plan, which E12 would read. The six commits of the order's section 0 are replayed in their real order,
each with its ruled files copied from MoviePad-Remake (git, read only) and the register state of its parent recreated with the
same ECO ids. Every commit goes through the product's hooks. Writes <this folder>/out/v1.txt; the product is removed at the end.

usage: python verify119.py <path to MoviePad-Remake>
"""
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
OUT = HERE / "out"
RULED = ["bomdd/10-requirements.yaml", "bomdd/20-spec.md", "bomdd/30-ebom.yaml", "bomdd/31-kbom.yaml", "bomdd/reports/adr/"]
REG = "bomdd/60-change-register.yaml"
ENV = dict(os.environ, GIT_AUTHOR_NAME="eco119-v1", GIT_AUTHOR_EMAIL="v1@bomdd.invalid",
           GIT_COMMITTER_NAME="eco119-v1", GIT_COMMITTER_EMAIL="v1@bomdd.invalid")


def _rm_readonly(func, path, _exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def sh(*args, env=None):
    return subprocess.run(list(args), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env or ENV)


def main():
    mp = Path(sys.argv[1])
    OUT.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="eco119-v1-"))
    lines = ["# V1 - MoviePad-Remake's ruled-layer history through E13 (a bomdd-init product)"]
    ok_all = True
    try:
        p = sh(sys.executable, str(BOMDD / "method/tools/bomdd-init.py"), "V1Prod", "--dir", str(tmp), "--no-gui", "--no-qualify")
        prod = tmp / "V1Prod"
        assert p.returncode == 0, p.stderr
        g = lambda *a, env=None: sh("git", "-C", str(prod), *a, env=env)
        mpg = lambda *a: subprocess.run(["git", "-C", str(mp), *a], capture_output=True, check=True).stdout
        main_branch = "main" if g("rev-parse", "--verify", "-q", "main").returncode == 0 else "master"
        reg: dict[str, str] = {}

        def write_reg():
            (prod / REG).write_text("changes:\n" + "".join(f"  - id: {c}\n    title: V1 replay\n    status: {s}\n"
                                                           for c, s in reg.items()), encoding="utf-8", newline="\n")

        def order(cid, cites):
            body = f"# {cid}\n\n## Sources read\n" + "".join(f"- {c}\n" for c in cites)
            (prod / f"bomdd/60-change-order-{cid.lower()}.md").write_text(body, encoding="utf-8", newline="\n")

        def commit(msg, *more, paths=None):
            g("add", "-A", "--", *(paths or ["."]))
            args = ["commit", "-q", "-m", msg]
            for m_ in more:
                args += ["-m", m_]
            r = g(*args)
            return r.returncode, r.stdout + r.stderr

        def undo():
            g("reset", "-q", "--hard")
            g("clean", "-q", "-fd")

        def copy_change(c):
            """the ruled files commit c touched, as they stand at c (deleted ones removed)"""
            touched = []
            for line in mpg("diff-tree", "--no-commit-id", "--name-status", "-r", "--no-renames", c).decode().splitlines():
                st, path = line.split("\t", 1)
                if not any(path == r or (r.endswith("/") and path.startswith(r)) for r in RULED):
                    continue
                touched.append(path)
                dst = prod / path
                if st == "D":
                    dst.unlink(missing_ok=True)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(mpg("cat-file", "blob", f"{c}:{path}"))
            return touched

        def copy_state(c):
            """every ruled file as it stands at c"""
            for r in RULED:
                names = mpg("ls-tree", "-r", "--name-only", c, "--", r).decode().split()
                for path in names:
                    (prod / path).parent.mkdir(parents=True, exist_ok=True)
                    (prod / path).write_bytes(mpg("cat-file", "blob", f"{c}:{path}"))

        def cite(c, path):
            """a real line of the change: the new side's first changed line (1 for an added file)"""
            d = mpg("diff", "-U0", f"{c}^", c, "--", path).decode()
            m = re.search(r"^@@ -\S+ \+(\d+)", d, re.M)
            return f"{path}:{m.group(1) if m else 1}"

        def arm(name, cond, detail):
            nonlocal ok_all
            ok_all &= cond
            lines.append(f"{name}: {'as expected' if cond else 'NOT as expected'} - {detail}")

        def show(out):
            return " | ".join(l.strip()[:230] for l in out.splitlines() if "[E13]" in l)[:600]

        def accept(cid):
            reg[cid] = "applied"
            write_reg()
            return commit(f"eco: accept {cid}", f"BomDD-ECO-Accept: {cid}", paths=[REG])

        # set-up: an equipment ECO (E08), the field, the release tag on a side branch
        reg["ECO-900"] = "staged"
        write_reg()
        rc, out = commit("eco: file ECO-900 (equipment: the ruled-layer field)", paths=[REG])
        prof_p = prod / "bomdd/process-profile.yaml"
        text = prof_p.read_text(encoding="utf-8")
        text = "".join(l for l in text.splitlines(keepends=True) if not l.startswith("structure_check:"))
        text += ("\nruled_layer:\n  since: bom-v4\n  paths: [" + ", ".join(RULED) + "]\n")
        prof_p.write_text(text, encoding="utf-8", newline="\n")
        rc2, out2 = commit("equipment: ruled_layer set, structure_check off (V1 measures E13 only)", paths=["bomdd/process-profile.yaml"])
        g("checkout", "-q", "-b", "rel")
        g("commit", "-q", "--allow-empty", "-m", "release")
        g("tag", "bom-v4")
        g("checkout", "-q", main_branch)
        lines.append(f"set-up: filing exit {rc}, profile exit {rc2}, tag bom-v4 on a side branch")
        ok_all &= rc == 0 and rc2 == 0

        # bbce170 (G3 round 1's spec change) before the release, then the ruled files as at bom-v4
        copy_state("bbce170^")
        commit("phase 3: the ruled files before G3 round 1")
        copy_change("bbce170")
        rc, out = commit("phase 3: bbce170's spec change (before the release)")
        arm("bbce170 before since -> allowed", rc == 0 and "[E13]" not in out, f"exit {rc}")
        copy_state("bom-v4")
        rc0, _ = commit("phase 3: the ruled files at bom-v4")
        rcm = g("merge", "-q", "--no-ff", "rel", "-m", "release: bom-v4").returncode
        lines.append(f"   the ruled files at bom-v4 committed (exit {rc0}); the release merged (exit {rcm}) - since is now an ancestor")
        ok_all &= rc0 == 0 and rcm == 0

        reg.update({"ECO-001": "staged", "ECO-002": "staged"})
        write_reg()
        commit("eco: file ECO-001, ECO-002", paths=[REG])
        accept("ECO-001")
        accept("ECO-002")

        # b06a5bf: ECO-003 filed in the same commit as the spec change -> refused; then file first, change next -> allowed
        t = copy_change("b06a5bf")
        reg["ECO-003"] = "staged"
        write_reg()
        order("ECO-003", [cite("b06a5bf", p_) for p_ in t])
        rc, out = commit("b06a5bf: file ECO-003 and change the spec in one commit", "BomDD-ECO-Ruling: ECO-003")
        arm("b06a5bf in ECO-003's filing commit -> refused (not open at HEAD)", rc != 0 and "[E13]" in out and "ECO-003" in out, f"exit {rc}: {show(out)}")
        undo()
        reg["ECO-003"] = "staged"
        write_reg()
        order("ECO-003", [cite("b06a5bf", "bomdd/20-spec.md"), cite("ec6e549", "bomdd/31-kbom.yaml")])
        commit("eco: file ECO-003 (filing only)", paths=[REG, "bomdd/60-change-order-eco-003.md"])
        copy_change("b06a5bf")
        rc, out = commit("b06a5bf: the spec correction under ECO-003", "BomDD-ECO-Ruling: ECO-003")
        arm("b06a5bf in the next commit, ECO-003 open, its order citing the spec -> allowed", rc == 0, f"exit {rc}: {show(out)}")
        copy_change("ec6e549")
        rc, out = commit("ec6e549: the K-BOM line under ECO-003", "BomDD-ECO-Ruling: ECO-003")
        arm("ec6e549 (extra) ECO-003 open, 31-kbom cited -> allowed", rc == 0, f"exit {rc}: {show(out)}")
        accept("ECO-003")

        # 0b50020: no open ECO, no trailer -> refused, naming 20-spec.md and 30-ebom.yaml
        copy_change("0b50020")
        rc, out = commit("0b50020: a Control Plan row split carried into the ruled files")
        arm("0b50020 with no open ECO and no trailer -> refused, names 20-spec.md and 30-ebom.yaml",
            rc != 0 and "bomdd/20-spec.md" in out and "bomdd/30-ebom.yaml" in out, f"exit {rc}: {show(out)}")
        undo()

        # known-bad of the gate: check_ruled_layer disabled in the working-tree validator lets the 0b50020 arm through
        vp = prod / "bomdd/tools/process-validator.py"
        vsrc = vp.read_text(encoding="utf-8")
        anchor = "def check_ruled_layer(root: Path, old: dict[str, dict], prof: dict, msg: str) -> list[str]:\n"
        assert vsrc.count(anchor) == 1
        vp.write_text(vsrc.replace(anchor, anchor + "    return []  # ECO-119 V1 known-bad\n"), encoding="utf-8", newline="\n")
        copy_change("0b50020")
        g("add", "-A", "--", "bomdd/20-spec.md", "bomdd/30-ebom.yaml")
        r = g("commit", "-q", "-m", "0b50020 with E13 disabled")
        arm("KB check_ruled_layer disabled -> the 0b50020 arm gets through (shown), then undone", r.returncode == 0, f"exit {r.returncode}")
        vp.write_text(vsrc, encoding="utf-8", newline="\n")
        if r.returncode == 0:
            g("reset", "-q", "--hard", "HEAD~1")
        restored = g("status", "--porcelain").stdout.strip() == ""
        lines.append(f"   validator restored and the commit undone (clean tree): {restored}")
        ok_all &= restored

        # f4861e8: the ADR change in ECO-005's filing commit -> refused; filed first, then the change with both ADRs cited -> allowed
        reg["ECO-004"] = "staged"
        write_reg()
        commit("eco: file ECO-004", paths=[REG])
        accept("ECO-004")
        t = copy_change("f4861e8")
        reg["ECO-005"] = "staged"
        write_reg()
        cites = [cite("f4861e8", p_) for p_ in t]
        order("ECO-005", cites)
        rc, out = commit("f4861e8: file ECO-005 with the ruling's ADRs in one commit", "BomDD-ECO-Ruling: ECO-005")
        arm("f4861e8 in ECO-005's filing commit -> refused", rc != 0 and "[E13]" in out, f"exit {rc}: {show(out)}")
        undo()
        reg["ECO-005"] = "staged"
        write_reg()
        order("ECO-005", cites)
        commit("eco: file ECO-005 (filing only)", paths=[REG, "bomdd/60-change-order-eco-005.md"])
        copy_change("f4861e8")
        rc, out = commit("f4861e8: ADR-002 and ADR-006 under ECO-005", "BomDD-ECO-Ruling: ECO-005")
        arm(f"f4861e8 in the next commit, both ADRs cited ({', '.join(cites)}) -> allowed", rc == 0, f"exit {rc}: {show(out)}")

        # 31273e7: the order cites 20-spec and 30-ebom but not 31-kbom -> refused naming 31-kbom; all three cited -> allowed
        order("ECO-005", cites + [cite("31273e7", "bomdd/20-spec.md"), cite("31273e7", "bomdd/30-ebom.yaml")])
        commit("eco-005: Sources read cites the spec and the E-BOM", paths=["bomdd/60-change-order-eco-005.md"])
        copy_change("31273e7")
        rc, out = commit("31273e7: the BOM line (the K-BOM uncited)", "BomDD-ECO-Ruling: ECO-005")
        arm("31273e7 with 31-kbom.yaml uncited -> refused, names 31-kbom.yaml with count 0",
            rc != 0 and "31-kbom.yaml" in out and "引用数 0" in out, f"exit {rc}: {show(out)}")
        undo()
        order("ECO-005", cites + [cite("31273e7", p_) for p_ in ("bomdd/20-spec.md", "bomdd/30-ebom.yaml", "bomdd/31-kbom.yaml")])
        commit("eco-005: Sources read cites all three", paths=["bomdd/60-change-order-eco-005.md"])
        copy_change("31273e7")
        rc, out = commit("31273e7: the BOM line, all three cited", "BomDD-ECO-Ruling: ECO-005")
        arm("31273e7 with all three cited -> allowed", rc == 0, f"exit {rc}: {show(out)}")

        # the history version: 79f1791's ADR note committed with --no-verify and no trailer -> validate reports E13 history
        copy_change("79f1791")
        g("add", "-A")
        r = g("commit", "-q", "--no-verify", "-m", "79f1791: ADR-003 note, hooks skipped")
        v = sh(sys.executable, str(prod / "bomdd/tools/process-validator.py"), "--mode", "validate", "--root", str(prod))
        vout = v.stdout + v.stderr
        e13 = [l.strip() for l in vout.splitlines() if "[E13]" in l]
        arm("79f1791 with --no-verify -> the full mode reports it (history E13, the only E13)",
            r.returncode == 0 and len(e13) == 1 and "history:" in e13[0] and "ADR-003" in e13[0], f"validate exit {v.returncode}: {e13}")
        other = [l.strip() for l in vout.splitlines() if re.match(r"\s*\[E\d\d\]", l) and "[E13]" not in l]
        lines.append(f"   other violations in the full mode: {other or 'none'}")
        ok_all &= not other
        # known-bad of the replay's boundary: without --ancestry-path the pre-release commits merged in from main are reported
        vsrc2 = vp.read_text(encoding="utf-8")
        assert vsrc2.count('"--ancestry-path", ') == 1
        vp.write_text(vsrc2.replace('"--ancestry-path", ', ""), encoding="utf-8", newline="\n")
        v2 = sh(sys.executable, str(vp), "--mode", "validate", "--root", str(prod))
        n2 = sum(1 for l in (v2.stdout + v2.stderr).splitlines() if "[E13]" in l)
        vp.write_text(vsrc2, encoding="utf-8", newline="\n")
        arm("KB2 the replay without --ancestry-path -> the pre-release commits are reported too (more than one E13)", n2 > 1, f"E13 lines {n2}")
    finally:
        shutil.rmtree(tmp, onerror=_rm_readonly)
        lines.append(f"throwaway product removed: {not tmp.exists()}")
    lines.append(f"V1: {'PASS' if ok_all else 'FAIL'}")
    (OUT / "v1.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
