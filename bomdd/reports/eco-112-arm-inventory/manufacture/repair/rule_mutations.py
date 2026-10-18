"""ECO-112 manufacture: break each new rule in a copy of bomdd-run.py and check that the selftest goes red (and names the rule's arm)."""
import shutil
import subprocess
import sys
from pathlib import Path

repo_tools = Path(sys.argv[1])
work = Path(sys.argv[2])
cases = {
    "G3-off": ('    if rec["job_state"] == "verified":   # ECO-112 G3', '    if False:   # ECO-112 G3', "g3-"),
    "B4-off": ('        res, bcode, bmsg = committed_copies(root, common, eco, rec["tree"])',
               '        res, bcode, bmsg = {"copies": [], "ignored": []}, None, ""', "b-promotion"),
    "LF-off": ('    if b"\\r" in data:', '    if False:', "BRIEF_NOT_LF"),
    "B1-first": ('    executor = opts.get("--executor")\n',
                 '    executor = opts.get("--executor")\n'
                 '    if cell and opts.get("--brief") is None:\n        emit("UNMEASURABLE ARG_ERROR: --cell には --brief PATH|none が必須")\n        return 2\n',
                 "--report はリポ相対パ"),
    # repair manufacture (r1 IA-01, IA-02): the rollback and the execution copy
    "rollback-not-own": ('    if not (info and created):\n        return None', '    if not info:\n        return None', "b-rollback-existing"),
    "rollback-off": ('        _unlink_stored(info["store_ref"])', '        pass', "b-rollback-ledger"),
    "left-line-off": ('        if left:\n            emit(_fit(f"brief left in store: {info[\'sha256\'][:12]} ({left})"))\n        return 2',
                      '        return 2', "b-rollback-fails"),
    "exec-is-store": ('BOMDD_BRIEF=exec_brief or "")',
                      'BOMDD_BRIEF=rec["brief"]["store_ref"] if isinstance(rec.get("brief"), dict) else "")', "b-exec-copy"),
    "exec-not-removed": ('    if d:\n        shutil.rmtree(d, ignore_errors=True)', '    if False:\n        pass', "b-exec-copy-removed"),
}
bad = 0
for name, (old, new, expect) in cases.items():
    d = work / name
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(repo_tools, d, ignore=shutil.ignore_patterns("__pycache__"))
    p = d / "bomdd-run.py"
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (name, old[:60])
    p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
    r = subprocess.run([sys.executable, "-B", str(p), "--selftest"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    red = r.returncode != 0 and r.stdout.startswith("STOP SELFTEST_FAIL")
    named = expect in r.stdout
    bad += not (red and named)
    print(f"{name}: exit {r.returncode}, red {red}, names {expect!r} {named} :: {r.stdout.splitlines()[0][:70] if r.stdout else ''}")
print("rule mutations", "PASS" if not bad else f"FAIL ({bad})")
sys.exit(1 if bad else 0)
