#!/usr/bin/env python3
"""Every red-first control of ECO-115's repairs, staged and checked against its own expected failure (inspection r4 IA-13).

  python -B redfirst_all.py <ViewPrism2> <scratch directory>     (from bomdd/reports/eco-115-advance-decision/)

Each control runs the current driver or rehearsal against the code its repair replaced, in a new scratch folder that holds every file the run
imports, and passes only when the run fails *for the finding's own reason* — the expected signature below — so a failure for another reason
(a missing file, an import error, an assertion of the helper) is reported as such and fails the control. Exit 0 only when every control shows its
signature. Read only on the repository; ViewPrism2 is read with git show.

  r1-decision   rehearse_decision_v2.py and rehearse_sequence.py at 35961c3 (the manufacture): the IA-04 arms and the IA-02 arms MISSED, and
                D4 not written
  r2-decision   the same at 2aa2d7d (r1's repairs): the IA-09 arm that expects the ref defect beside the bounds one, 1000 and 5,000 digits MISSED
  r3-decision   the same at 7eddaba (r2's repairs): the no-break-space and ideographic-space arms MISSED, and I3a and D5 disagree
  c5            the current files with C5's manufacture-tree clause put back: exactly Y6 BAD
  domain        the current files with the shared parser's domain opened to any decimal integer: the D5 rehearsal stops on Z3 with ValueError
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = "bomdd/reports/eco-115-advance-decision"
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")


def git_show(rev, name):
    return subprocess.run(["git", "-C", HERE, "show", f"{rev}:{REL}/{name}"], capture_output=True, check=True).stdout


def stage(folder, rev):
    """The driver and the gzip from the current tree; the decision and sequence rehearsals from rev (None = current)."""
    for name in ("run_rehearsal_v2.py", "vp2-cp-results.xml.gz"):
        shutil.copy(os.path.join(HERE, name), folder)
    for name in ("rehearse_decision_v2.py", "rehearse_sequence.py"):
        data = git_show(rev, name) if rev else open(os.path.join(HERE, name), "rb").read()
        open(os.path.join(folder, name), "wb").write(data)


def run(folder, args):
    return subprocess.run([sys.executable, "-B", *args], cwd=folder, capture_output=True, text=True, encoding="utf-8", env=ENV)


def decision_control(base, vp2, rev, must_miss, must_lines):
    folder = tempfile.mkdtemp(prefix=f"rf-{rev}-", dir=base)
    stage(folder, rev)
    out = os.path.join(folder, "out.txt")
    done = run(folder, ["run_rehearsal_v2.py", vp2, out])
    if not os.path.exists(out):
        return False, f"no output (exit {done.returncode}): {done.stderr.strip().splitlines()[-1:]}"
    text = open(out, encoding="utf-8").read()
    # a MISSED line is "   MISSED <arm name>: <result> ..."; arm names may hold a colon, so an expected name is matched as a prefix of the rest
    missed = [line.strip()[len("MISSED"):].strip() for line in text.splitlines() if line.strip().startswith("MISSED")]
    lacking = [m for m in must_miss if not any(x.startswith(m) for x in missed)]
    absent = [s for s in must_lines if s not in text]
    ok = done.returncode == 1 and not lacking and not absent
    return ok, f"exit {done.returncode}; {len(missed)} MISSED; expected missing {lacking or 'none'}; expected lines absent {absent or 'none'}"


def c5_control(base):
    folder = tempfile.mkdtemp(prefix="rf-c5-", dir=base)
    stage(folder, None)
    p = os.path.join(folder, "rehearse_sequence.py")
    s = open(p, encoding="utf-8").read()
    new = '''            if last in ("violation", "unmeasurable") and via != f"{row}:{last}":'''
    old = '''            if last in ("violation", "unmeasurable") and f"{row}:{last}" not in on_row[row]:'''
    if s.count(new) != 1:
        return False, "the current C5 clause was not found once (the control's set-up no longer fits the code)"
    open(p, "w", encoding="utf-8", newline="\n").write(s.replace(new, old))
    done = run(folder, ["rehearse_sequence.py"])
    bad = [line.split(":", 1)[0] for line in done.stdout.splitlines() if line.startswith("BAD")]
    ok = done.returncode == 1 and len(bad) == 1 and bad[0].startswith("BAD Y6 ")
    return ok, f"exit {done.returncode}; BAD arms {bad or 'none'}; stderr {done.stderr.strip().splitlines()[-1:] or 'none'}"


def domain_control(base):
    folder = tempfile.mkdtemp(prefix="rf-domain-", dir=base)
    stage(folder, None)
    p = os.path.join(folder, "rehearse_decision_v2.py")
    s = open(p, encoding="utf-8").read()
    closed, opened = "holds ([1-9][0-9]{0,2}), decisions ([1-9][0-9]{0,2})", "holds ([1-9][0-9]*), decisions ([1-9][0-9]*)"
    if s.count(closed) != 1:
        return False, "the shared parser's pattern was not found once (the control's set-up no longer fits the code)"
    open(p, "w", encoding="utf-8", newline="\n").write(s.replace(closed, opened))
    done = run(folder, ["rehearse_sequence.py"])
    last = (done.stderr.strip().splitlines() or [""])[-1]
    ok = done.returncode != 0 and last.startswith("ValueError: Exceeds the limit")
    return ok, f"exit {done.returncode}; last stderr line {last[:90]!r}"


def main():
    vp2, scratch = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(scratch, exist_ok=True)
    base = tempfile.mkdtemp(prefix="eco115-redfirst-", dir=scratch)
    controls = [
        ("r1-decision", decision_control(base, vp2, "35961c3",
                                         ["I3a (r1 IA-04) mbom_ref names", "I3a (r1 IA-04) mbom_ref and control_plan_ref swapped",
                                          "I3a (r1 IA-04) the delivered commit", "I3a (r1 IA-02) a bounds line with holds 0",
                                          "I3a (r1 IA-02) a bounds line missing", "I3a (r1 IA-02) a bounds line with a non-numeric",
                                          "I3a (r1 IA-02) a bounds line with a negative", "I3a (r1 IA-02) two bounds lines"],
                                         ["== D4 written into the decision records on every case that decided rows: False"])),
        ("r2-decision", decision_control(base, vp2, "2aa2d7d",
                                         ["I3a (r2 IA-09) a malformed bounds line and swapped refs: both listed",
                                          "I3a (r2 IA-10) a bounds line just past it", "I3a (r2 IA-10) a bounds line of 5,000 digits"], [])),
        ("r3-decision", decision_control(base, vp2, "7eddaba",
                                         ["I3a (r3 IA-11) a bounds line ending in a no-break space",
                                          "I3a (r3 IA-11) a bounds line ending in an ideographic space"],
                                         ["== I3a and D5 read the bounds line alike on 84 lines (values x line ends): False"])),
        ("c5", c5_control(base)),
        ("domain", domain_control(base)),
    ]
    for name, (ok, detail) in controls:
        print(f"{'SIGNATURE' if ok else 'OTHER    '} {name}: {detail}")
    good = sum(ok for _, (ok, _) in controls)
    print(f"red-first controls showing their own failure: {good} of {len(controls)}")
    return 0 if good == len(controls) else 1


if __name__ == "__main__":
    sys.exit(main())
