"""ECO-118 V8 - the stop E12 refuses and allows as stated, in a throwaway product made by bomdd-init.py.

The product gets process-core with the profile field structure_check (written by the scaffold) and the kit's tool. The
three BOM files are copied from MoviePad-Remake's history with git (read only). Every commit goes through the product's
hooks (pre-commit, commit-msg). Writes <this folder>/out/v8.txt; the product is removed at the end.

usage: python verify118_v8.py <path to MoviePad-Remake>
"""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _rm_readonly(func, path, _exc):
    # git writes its objects read-only; on Windows rmtree cannot remove them without this
    os.chmod(path, stat.S_IWRITE)
    func(path)

HERE = Path(__file__).resolve().parent
BOMDD = HERE.parents[2]
OUT = HERE / "out"
FILES = ["bomdd/30-ebom.yaml", "bomdd/32-mbom.yaml", "bomdd/33-control-plan.yaml"]
REG = "bomdd/60-change-register.yaml"
ENV = dict(os.environ, GIT_AUTHOR_NAME="eco118-v8", GIT_AUTHOR_EMAIL="v8@bomdd.invalid",
           GIT_COMMITTER_NAME="eco118-v8", GIT_COMMITTER_EMAIL="v8@bomdd.invalid")


def sh(*args, cwd=None):
    return subprocess.run(list(args), capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd, env=ENV)


def main():
    mp = Path(sys.argv[1])
    OUT.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="eco118-v8-"))
    lines = ["# V8 - E12 in a bomdd-init product (MoviePad-Remake's BOM files)"]
    ok_all = True
    try:
        p = sh(sys.executable, str(BOMDD / "method" / "tools" / "bomdd-init.py"), "V8Prod", "--dir", str(tmp),
               "--no-gui", "--no-qualify")
        prod = tmp / "V8Prod"
        assert p.returncode == 0, p.stderr
        field = [l for l in (prod / "bomdd" / "process-profile.yaml").read_text(encoding="utf-8").splitlines()
                 if l.startswith("structure_check:")]
        lines.append(f"scaffold: profile {field}, tool in kit {(prod / 'bomdd-kit/method/tools/bom-structure-check.py').is_file()}, "
                     f"hooksPath {sh('git', '-C', str(prod), 'config', 'core.hooksPath').stdout.strip()}")
        template = {f: (prod / f).read_bytes() for f in FILES}
        ids = [f"ECO-80{i}" for i in range(1, 7)]
        st = {c: "staged" for c in ids}

        def reg_text():
            return "changes:\n" + "".join(f"  - id: {c}\n    title: V8 arm\n    status: {s}\n" for c, s in st.items())

        def put(src):
            for f in FILES:
                if src == "template":
                    b = template[f]
                else:
                    rev, fix = (src, False) if not src.endswith("+p1fix") else (src[:-6], True)
                    b = subprocess.run(["git", "-C", str(mp), "cat-file", "blob", f"{rev}:{f}"], capture_output=True, check=True).stdout
                    if fix:
                        b = b.replace(b"PS-M-EXPORT-CLOCK-001-P01", b"PS-M-EXPORT-001-P03").replace(b"PS-M-EXPORT-COPY-001-P01", b"PS-M-EXPORT-001-P04")
                (prod / f).write_bytes(b)

        def commit(msg, *more, paths=None):
            sh("git", "-C", str(prod), "add", *(paths or FILES + [REG]))
            args = ["git", "-C", str(prod), "commit", "-q", "-m", msg]
            for m in more:
                args += ["-m", m]
            return sh(*args)

        def accept(cid, src, label):
            put(src)
            st[cid] = "applied"
            (prod / REG).write_text(reg_text(), encoding="utf-8", newline="\n")
            r = commit(f"eco: accept {cid} ({label})", f"BomDD-ECO-Accept: {cid}")
            out = r.stdout + r.stderr
            if r.returncode != 0:
                st[cid] = "staged"
                sh("git", "-C", str(prod), "reset", "-q", "HEAD", "--", *FILES, REG)
                sh("git", "-C", str(prod), "checkout", "-q", "--", *FILES, REG)
            return r.returncode, out

        def arm(name, got_ok, detail):
            nonlocal ok_all
            ok_all &= got_ok
            lines.append(f"{name}: {'as expected' if got_ok else 'NOT as expected'} - {detail}")

        def show(out):
            keep = [l.strip() for l in out.splitlines() if "[E12]" in l or l.strip().startswith(("[A1-", "[P1-", "[C1-", "verdict:", "population:"))]
            return " | ".join(keep[:6])

        (prod / REG).write_text(reg_text(), encoding="utf-8", newline="\n")
        r = commit("eco: file ECO-801..806", paths=[REG])
        lines.append(f"filing commit exit {r.returncode}")

        rc, out = accept("ECO-801", "d3683d6", "d3683d6's BOM")
        arm("1 d3683d6 at an applied transition -> refused, E12, findings printed",
            rc != 0 and "[E12]" in out and "[A1-4]" in out, f"exit {rc}: {show(out)}")

        rc, out = accept("ECO-801", "3ba3d00", "3ba3d00's BOM as committed")
        lines.append(f"2 3ba3d00 as committed (the frozen condition: allowed): exit {rc} - {show(out)}")
        lit_allowed = rc == 0
        rc, out = accept("ECO-801" if not lit_allowed else "ECO-802", "3ba3d00+p1fix", "3ba3d00 with the two P1 ids renamed")
        arm("2' 3ba3d00 with the two P1 ids renamed (derived copy) -> allowed, PASS named",
            rc == 0 and "PASS" in out, f"exit {rc}: {show(out)}")

        # R8-1-01: the acceptance commit just made, amended with d3683d6's BOM (HEAD already applied, so no transition)
        put("d3683d6")
        sh("git", "-C", str(prod), "add", *FILES)
        r = sh("git", "-C", str(prod), "commit", "-q", "--amend", "--no-edit")
        out = r.stdout + r.stderr
        arm("2'' the acceptance commit amended with d3683d6's BOM -> refused, E12 (R8-1-01)",
            r.returncode != 0 and "[E12]" in out, f"exit {r.returncode}: {show(out)}")
        sh("git", "-C", str(prod), "reset", "-q", "HEAD", "--", *FILES)
        sh("git", "-C", str(prod), "checkout", "-q", "--", *FILES)

        # R8-2-01: the same with an editor (GIT_EDITOR=true leaves the message as git wrote it, comment block included);
        # then its known-bad: strip_commit_comments made the identity in the working-tree validator lets it through
        def editor_amend():
            put("d3683d6")
            sh("git", "-C", str(prod), "add", *FILES)
            r = subprocess.run(["git", "-C", str(prod), "commit", "-q", "--amend"], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", env=dict(ENV, GIT_EDITOR="true"))
            out = r.stdout + r.stderr
            if r.returncode != 0:
                sh("git", "-C", str(prod), "reset", "-q", "HEAD", "--", *FILES)
                sh("git", "-C", str(prod), "checkout", "-q", "--", *FILES)
            return r.returncode, out
        rc, out = editor_amend()
        arm("2''' the acceptance commit amended in an editor with d3683d6's BOM -> refused, E12 (R8-2-01)",
            rc != 0 and "[E12]" in out, f"exit {rc}: {show(out)}")
        vpath0 = prod / "bomdd" / "tools" / "process-validator.py"
        vsrc0 = vpath0.read_text(encoding="utf-8")
        a0 = "    out = []\n    for line in msg.splitlines():\n"
        assert vsrc0.count(a0) == 1
        vpath0.write_text(vsrc0.replace(a0, "    return msg  # ECO-118 V8 known-bad (R8-2-01)\n" + a0), encoding="utf-8", newline="\n")
        rc, out = editor_amend()
        arm("KB2 comment stripping disabled -> the editor amend gets through (shown), then undone", rc == 0, f"exit {rc}")
        vpath0.write_text(vsrc0, encoding="utf-8", newline="\n")
        if rc == 0:  # undo the amended commit: back to the acceptance commit it replaced
            sh("git", "-C", str(prod), "reset", "-q", "--hard", "HEAD@{1}")
        restored0 = sh("git", "-C", str(prod), "status", "--porcelain", "--", "bomdd/tools/process-validator.py").stdout.strip() == ""
        head_ok = sh(sys.executable, str(prod / "bomdd-kit/method/tools/bom-structure-check.py"), "--root", str(prod), "--rev", "HEAD").returncode == 0
        lines.append(f"   validator restored: {restored0}; HEAD's BOM passes again (the derived copy): {head_ok}")
        ok_all &= restored0 and head_ok

        # R8-3-01: git comments with another character - core.commentChar=auto with a '#' body line, core.commentString.
        # The acceptance commit's message is first redone with a '#42' line (the BOM unchanged, still passing).
        r0 = sh("git", "-C", str(prod), "commit", "-q", "--amend", "-m", "eco: accept ECO-801 (the derived copy)",
                "-m", "#42 is the issue this closes", "-m", "BomDD-ECO-Accept: ECO-801")
        lines.append(f"   the acceptance message redone with a '#42' line: exit {r0.returncode}")

        def config_amend(key, val):
            sh("git", "-C", str(prod), "config", key, val)
            rc_, out_ = editor_amend()
            sh("git", "-C", str(prod), "config", "--unset", key)
            return rc_, out_
        for label, key, val in (("2-auto", "core.commentChar", "auto"), ("2-string", "core.commentString", ";")):
            rc, out = config_amend(key, val)
            arm(f"{label} {key}={val}, an editor amend with d3683d6's BOM -> refused, E12 (R8-3-01)",
                rc != 0 and "[E12]" in out, f"exit {rc}: {show(out)}")
        vsrc1 = vpath0.read_text(encoding="utf-8")
        a1 = "def commit_comment_prefixes(root: Path) -> tuple[str, ...]:\n"
        assert vsrc1.count(a1) == 1
        vpath0.write_text(vsrc1.replace(a1, a1 + '    return ("#",)  # ECO-118 V8 known-bad (R8-3-01)\n'), encoding="utf-8", newline="\n")
        rc, out = config_amend("core.commentChar", "auto")
        arm("KB3 the prefixes back to '#' only -> the auto editor amend gets through (shown), then undone", rc == 0, f"exit {rc}")
        vpath0.write_text(vsrc1, encoding="utf-8", newline="\n")
        if rc == 0:
            sh("git", "-C", str(prod), "reset", "-q", "--hard", "HEAD@{1}")
        restored1 = sh("git", "-C", str(prod), "status", "--porcelain", "--", "bomdd/tools/process-validator.py").stdout.strip() == ""
        head_ok1 = sh(sys.executable, str(prod / "bomdd-kit/method/tools/bom-structure-check.py"), "--root", str(prod), "--rev", "HEAD").returncode == 0
        lines.append(f"   validator restored: {restored1}; HEAD's BOM passes again: {head_ok1}")
        ok_all &= restored1 and head_ok1 and r0.returncode == 0

        rc, out = accept("ECO-803", "template", "the scaffold's template BOM")
        arm("3 the template BOM (no part standard) -> allowed, NOT-APPLICABLE named",
            rc == 0 and "NOT-APPLICABLE" in out, f"exit {rc}: {show(out)}")

        put("41a5b18")
        r = commit("bom: an intermediate commit with 41a5b18's BOM (no transition)", paths=FILES)
        arm("4 41a5b18 on a non-applied commit -> allowed (the stop is not per commit)",
            r.returncode == 0 and "[E12]" not in r.stdout + r.stderr, f"exit {r.returncode}")
        put("template")
        commit("bom: back to the template (no transition)", paths=FILES)

        tool = prod / "bomdd-kit" / "method" / "tools" / "bom-structure-check.py"
        saved = tool.read_bytes()
        tool.unlink()
        rc, out = accept("ECO-804", "template", "the tool removed")
        arm("5a the tool removed -> refused", rc != 0 and "[E12]" in out, f"exit {rc}: {show(out)}")
        tool.write_bytes(saved)

        put("template")
        (prod / FILES[1]).write_text("mbom: [\n", encoding="utf-8")
        st["ECO-804"] = "applied"
        (prod / REG).write_text(reg_text(), encoding="utf-8", newline="\n")
        r = commit("eco: accept ECO-804 (an M-BOM that does not parse)", "BomDD-ECO-Accept: ECO-804")
        out = r.stdout + r.stderr
        arm("5b a staged 32-mbom.yaml that does not parse -> refused", r.returncode != 0 and "[E12]" in out,
            f"exit {r.returncode}: {show(out)}")
        if r.returncode != 0:
            st["ECO-804"] = "staged"
            sh("git", "-C", str(prod), "reset", "-q", "HEAD", "--", *FILES, REG)
            sh("git", "-C", str(prod), "checkout", "-q", "--", *FILES, REG)

        # known-bad of the gate: the validator's E12 check (check_structure) disabled in the working tree (not staged, so E08 is not
        # involved; the hook runs the working-tree validator) lets arm 1 through; then restored
        vpath = prod / "bomdd" / "tools" / "process-validator.py"
        vsrc = vpath.read_text(encoding="utf-8")
        anchor = '    """E12(ECO-118)— profile に structure_check があり、受入遷移を含む commit のときだけ再計算する。"""\n'
        assert vsrc.count(anchor) == 1
        vpath.write_text(vsrc.replace(anchor, anchor + "    return []  # ECO-118 V8 known-bad\n"), encoding="utf-8", newline="\n")
        rc, out = accept("ECO-805", "d3683d6", "d3683d6 with E12's refusal disabled")
        arm("KB E12's refusal disabled -> arm 1 gets through (shown), then restored", rc == 0, f"exit {rc}: {show(out) or out.strip()[-300:]}")
        vpath.write_text(vsrc, encoding="utf-8", newline="\n")
        restored = sh("git", "-C", str(prod), "status", "--porcelain", "--", "bomdd/tools/process-validator.py").stdout.strip() == ""
        lines.append(f"   validator restored (no diff against HEAD): {restored}")
        ok_all &= restored
        put("template")
        commit("bom: back to the template after the known-bad (no transition)", paths=FILES)

        prof_path = prod / "bomdd" / "process-profile.yaml"
        prof_path.write_text("".join(l for l in prof_path.read_text(encoding="utf-8").splitlines(keepends=True)
                                     if not l.startswith("structure_check:")), encoding="utf-8", newline="\n")
        r0 = commit("equipment: drop structure_check under ECO-806 (E08 needs an open ECO)", paths=["bomdd/process-profile.yaml"])
        rc, out = accept("ECO-806", "d3683d6", "d3683d6 with the field removed")
        arm("6 the profile without the field -> no E12 on the d3683d6 commit",
            r0.returncode == 0 and rc == 0 and "[E12]" not in out, f"profile commit exit {r0.returncode}, accept exit {rc}")
    finally:
        shutil.rmtree(tmp, onerror=_rm_readonly)
        lines.append(f"throwaway product removed: {not tmp.exists()}")
    lines.append(f"V8: every arm but 2 {'as expected' if ok_all else 'NOT as expected'}; arm 2 (3ba3d00 as committed) is judged in the order's section 4")
    (OUT / "v8.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
