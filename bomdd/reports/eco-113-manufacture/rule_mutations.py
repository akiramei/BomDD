"""ECO-113 manufacture: break each new rule in a copy of method/tools and check that the bomdd-run selftest goes red and names the rule's own arm.

usage: python -B rule_mutations.py <method/tools> <work dir>   (Windows; the copies run one after another — the selftest counts shared temp dirs, ECO-112 OBS-20261018-03)
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

repo_tools = Path(sys.argv[1])
work = Path(sys.argv[2])
cases = {
    # X — exclusion
    "X2-no-lock": ("            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)\n", "            pass\n", "v1a-entry-alive"),
    "X2-open-error-is-alive": ('        return None, "LOCK_UNAVAILABLE", _oserr(e)\n    try:', '        return None, "ENTRY_ALIVE", _oserr(e)\n    try:',
                               "v1f-readonly-lock"),
    # W — ownership
    "W1-no-kill-on-close": ("    ext.Basic.LimitFlags = 0x00002000\n", "    ext.Basic.LimitFlags = 0\n", "v2a-entry-killed"),
    "W3-handle-not-closed": ("    if h is not None:\n        _job_close(h)\n", "    if h is not None:\n        pass\n", "v2g-"),
    "W4-code": ('entry_code="JOB_UNAVAILABLE", entry_detail=_oserr(e))', 'entry_code="JOURNAL_WRITE_FAILED", entry_detail=_oserr(e))', "v2c-"),
    # J — judgement
    "J2-not-found-is-alive": ('        return ("gone", None) if code == 2 else ("error", code)', '        return ("active", 1) if code == 2 else ("error", code)',
                              "v2a-abnormal-end"),
    "J2-no-namespace-key": ('    for k in ("host", "session", "appcontainer"):\n', '    for k in ():\n', "v2d-other-"),
    "J2-precedence-reversed": ('CLASS_ORDER = ("ABNORMAL_END", "UNKNOWN", "CELL_ALIVE", "JOURNAL_CORRUPT")',
                               'CLASS_ORDER = ("JOURNAL_CORRUPT", "CELL_ALIVE", "UNKNOWN", "ABNORMAL_END")', "v4q-precedence"),
    # R — recovery
    "R2-release-cell-alive": ('    if run_["class"] == "CELL_ALIVE":   # R2: 拒否', '    if False:   # R2: 拒否', "v3b-release-cell-alive"),
    "R2-no-unverified": ('        rel["cell"] = "unverified"', '        pass', "v3a-release-unknown"),
    "R3-quarantine-cell-alive": ('        alive = next((r for r in runs if r["class"] == "CELL_ALIVE"), None)', '        alive = None',
                                 "v3e-quarantine-cell-alive"),
    # A — records
    "A1-short-write-accepted": ("    if n != len(line):   # A1", "    if False:   # A1", "v4e-short-write"),
    "A2-torn-not-repaired": ("            if torn:\n", "            if False:\n", "v4c-torn-repaired"),
    "A5-ledger-unlocked": ("            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)\n", "            pass\n", "v4j-ledger-concurrent"),
    # S — sequence
    "S1-report-recheck-off": ("    if report is not None and (root / report).exists():   # S1: R10 の再検査", "    if False:   # S1: R10 の再検査",
                              "v4i-report-exists-under-lock"),
    "S1.6-no-retry": ("END_RETRIES = 3 ", "END_RETRIES = 0 ", "v4d-end-failed"),
    "S3-interrupt-closes": ('journal_commit(jpath, {"event": "interrupted", "eco": eco', 'journal_commit(jpath, {"event": "end", "eco": eco', "v4h-"),
    "S4-entry-alive-fields": ('{} if cause == "ENTRY_ALIVE" else {"lock_error": lerr}', '{"lock_error": lerr}', "v1a-entry-alive"),
    # O — output
    "O3-exit-1": ('        emit(_fit(f"UNMEASURABLE {eco} INTERNAL_ERROR({e.__class__.__name__}) → operator"))\n        return 2',
                  '        emit(_fit(f"UNMEASURABLE {eco} INTERNAL_ERROR({e.__class__.__name__}) → operator"))\n        return 1', "v4m-"),
    # A4 (amendment 1:A, V4(f)): one mutation per clause — each check removed must be caught on that clause's own arm
    "A4i-not-object": ("        if not isinstance(r, dict):   # A4 (i)\n            bad.append((off, line))\n            continue\n", "", "v4f-not-object"),
    "A4ii-run-id": ("            if not isinstance(rid, str) or not rid:   # A4 (ii)", "            if False:   # A4 (ii)", "v4f-run-id"),
    "A4iii-order": ('            if (ev == "start" and rid in opened) or (ev != "start" and rid not in started):   # A4 (iii)',
                    "            if False:   # A4 (iii)", "v4f-close-before-start"),
    "A4iv-integer": ("    if not isinstance(q, int) or isinstance(q, bool):   # A4 (iv)", "    if False:   # A4 (iv)", "v4f-q-integer"),
    "A4iv-position": ("    if q < 0 or q > off:   # A4 (iv)", "    if False:   # A4 (iv)", "v4f-q-position"),
    "A4iv-boundary": ('    if q > 0 and data[q - 1:q] != b"\\n":   # A4 (iv)', "    if False:   # A4 (iv)", "v4f-q-boundary"),
    "A4iv-digest": ('    if r.get("excluded_sha256") != _sha(b"".join(b for o, b in bad if o < q)):   # A4 (iv)', "    if False:   # A4 (iv)", "v4f-q-digest"),
    # the word removed from bomdd-job's vocabulary (removing it from bomdd-run's DELIVERY breaks the line builder itself — a crash, not a reason)
    "O2-vocabulary": ('    "RUN_IN_FLIGHT",         # ⑨', '    # ⑨', "DELIVERY と job の停止語彙が一致しない", "bomdd-job.py"),
}
only = set(sys.argv[3:])
bad = 0
for name, (old, new, expect, *target) in cases.items():
    if only and name not in only:
        continue
    d = work / name
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(repo_tools, d, ignore=shutil.ignore_patterns("__pycache__"))
    p = d / "bomdd-run.py"
    t = d / (target[0] if target else "bomdd-run.py")
    s = t.read_text(encoding="utf-8")
    assert s.count(old) == 1, (name, s.count(old), old[:60])
    t.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
    # output to a file, not a pipe: a mutation that breaks the job (W1, W3) leaves cells that inherit and hold a pipe open
    out_p = d / "selftest.out"
    with open(out_p, "wb") as f, open(d / "selftest.err", "wb") as fe:   # stderr apart: O3 prints tracebacks there by design
        pr = subprocess.Popen([sys.executable, "-B", str(p), "--selftest"], stdout=f, stderr=fe,
                              env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        try:
            rc = pr.wait(1200)
        except subprocess.TimeoutExpired:
            pr.kill()
            rc = "timeout"
    out = out_p.read_bytes().decode("utf-8", errors="replace")
    red = rc not in (0, "timeout") and out.startswith("STOP SELFTEST_FAIL")
    named = expect in out
    bad += not (red and named)
    print(f"{name}: exit {rc}, red {red}, names {expect!r} {named} :: {out.splitlines()[0][:70] if out else ''}", flush=True)
print("rule mutations", "PASS" if not bad else f"FAIL ({bad})")
sys.exit(1 if bad else 0)
