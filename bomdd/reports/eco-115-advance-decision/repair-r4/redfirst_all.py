#!/usr/bin/env python3
"""Every red-first control of ECO-115's repairs, staged and checked against its own expected failure (inspection r4 IA-13).

  python -B redfirst_all.py <ViewPrism2> <scratch directory>     (from bomdd/reports/eco-115-advance-decision/)

Each control runs the current driver or rehearsal against the code its repair replaced, in a new scratch folder that holds every file the run
imports, and passes only when the run fails *for the finding's own reason* — the expected signature below — so a failure for another reason
(a missing file, an import error, an assertion of the helper) is reported as such and fails the control. Exit 0 only when every control shows its
signature. Read only on the repository; ViewPrism2 is read with git show.

  r1-decision   rehearse_decision_v2.py and rehearse_sequence.py at 35961c3 (the manufacture): exactly the arms of R1, R2 (both IA-09 arms) and R3
                MISSED, and D4 not written
  r2-decision   the same at 2aa2d7d (r1's repairs): exactly the arms of R2 and R3 MISSED
  r3-decision   the same at 7eddaba (r2's repairs): exactly the arms of R3 MISSED, and I3a and D5 disagree
Every control also checks that the staged files are the named revision's blobs (git's object ids) and that a run that should fail cleanly
writes nothing to stderr (inspection r5 IA-14).
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


def staged_identity(folder, rev):
    """Inspection r5 IA-14: each staged rehearsal is the blob of the revision the control names (git's own object id of the staged bytes against
    rev:path), and the driver and gzip are the current tree's; returns the files that are not."""
    wrong = []
    for name in ("rehearse_decision_v2.py", "rehearse_sequence.py", "run_rehearsal_v2.py", "vp2-cp-results.xml.gz"):
        want_rev = rev if rev and name.startswith("rehearse_") else "HEAD"
        staged = subprocess.run(["git", "hash-object", os.path.join(folder, name)], capture_output=True, text=True).stdout.strip()
        if want_rev == "HEAD":
            want = subprocess.run(["git", "hash-object", os.path.join(HERE, name)], capture_output=True, text=True).stdout.strip()
        else:
            want = subprocess.run(["git", "-C", HERE, "rev-parse", f"{want_rev}:{REL}/{name}"], capture_output=True, text=True).stdout.strip()
        if not staged or staged != want:
            wrong.append(name)
    return wrong


def decision_control(base, vp2, rev, exact_missed, must_lines):
    """Passes only when the staged files are rev's, the run exits 1 with no stderr, the arms it misses are exactly exact_missed (none more, none
    fewer — inspection r5 IA-14: a wrong revision misses a different set), and must_lines are printed."""
    folder = tempfile.mkdtemp(prefix=f"rf-{rev}-", dir=base)
    stage(folder, rev)
    wrong = staged_identity(folder, rev)
    out = os.path.join(folder, "out.txt")
    done = run(folder, ["run_rehearsal_v2.py", vp2, out])
    if not os.path.exists(out):
        return False, f"no output (exit {done.returncode}): {done.stderr.strip().splitlines()[-1:]}"
    text = open(out, encoding="utf-8").read()
    # a MISSED line is "   MISSED <arm name>: <result> ..."; the name is read up to its first ": " (one arm's name holds ": both listed", so its
    # frozen form below stops there too)
    missed = [line.strip()[len("MISSED"):].strip().split(": ", 1)[0] for line in text.splitlines() if line.strip().startswith("MISSED")]
    extra, lacking = sorted(set(missed) - set(exact_missed)), sorted(set(exact_missed) - set(missed))
    absent = [s for s in must_lines if s not in text]
    stderr = done.stderr.strip()
    ok = not wrong and done.returncode == 1 and not stderr and not extra and not lacking and len(missed) == len(exact_missed) and not absent
    return ok, (f"staged files not {rev}'s: {wrong or 'none'}; exit {done.returncode}; stderr {'present' if stderr else 'none'}; "
                f"{len(missed)} MISSED (expected {len(exact_missed)}); unexpected {extra or 'none'}; missing {lacking or 'none'}; "
                f"expected lines absent {absent or 'none'}")


def c5_control(base, drop=None):
    folder = tempfile.mkdtemp(prefix="rf-c5-", dir=base)
    stage(folder, None)
    if drop:   # the negative check below: a set-up missing a file the rehearsal imports
        os.remove(os.path.join(folder, drop))
    wrong = staged_identity(folder, None)
    p = os.path.join(folder, "rehearse_sequence.py")
    s = open(p, encoding="utf-8").read()
    new = '''            if last in ("violation", "unmeasurable") and via != f"{row}:{last}":'''
    old = '''            if last in ("violation", "unmeasurable") and f"{row}:{last}" not in on_row[row]:'''
    if s.count(new) != 1:
        return False, "the current C5 clause was not found once (the control's set-up no longer fits the code)"
    open(p, "w", encoding="utf-8", newline="\n").write(s.replace(new, old))
    done = run(folder, ["rehearse_sequence.py"])
    bad = [line.split(":", 1)[0] for line in done.stdout.splitlines() if line.startswith("BAD")]
    ok = not wrong and done.returncode == 1 and not done.stderr.strip() and len(bad) == 1 and bad[0].startswith("BAD Y6 ")
    return ok, (f"staged files not the current tree's: {wrong or 'none'}; exit {done.returncode}; BAD arms {bad or 'none'}; "
                f"stderr {done.stderr.strip().splitlines()[-1:] or 'none'}")


def domain_control(base):
    folder = tempfile.mkdtemp(prefix="rf-domain-", dir=base)
    stage(folder, None)
    wrong = staged_identity(folder, None)
    p = os.path.join(folder, "rehearse_decision_v2.py")
    s = open(p, encoding="utf-8").read()
    closed, opened = "holds ([1-9][0-9]{0,2}), decisions ([1-9][0-9]{0,2})", "holds ([1-9][0-9]*), decisions ([1-9][0-9]*)"
    if s.count(closed) != 1:
        return False, "the shared parser's pattern was not found once (the control's set-up no longer fits the code)"
    open(p, "w", encoding="utf-8", newline="\n").write(s.replace(closed, opened))
    done = run(folder, ["rehearse_sequence.py"])
    last = (done.stderr.strip().splitlines() or [""])[-1]
    ok = not wrong and done.returncode != 0 and last.startswith("ValueError: Exceeds the limit")
    return ok, f"staged files not the current tree's: {wrong or 'none'}; exit {done.returncode}; last stderr line {last[:90]!r}"


# The exact arms each revision's code misses (inspection r5 IA-14): a revision misses its own finding's arms and the arms added for every later
# finding, so a wrong revision staged for a control misses a different set and fails it.
R1 = ["I3a (r1 IA-04) mbom_ref names a path that is not at frozen_commit", "I3a (r1 IA-04) mbom_ref and control_plan_ref swapped",
      "I3a (r1 IA-04) the delivered commit holds another Control Plan than the copy compared", "I3a (r1 IA-02) a bounds line with holds 0",
      "I3a (r1 IA-02) a bounds line missing its decisions", "I3a (r1 IA-02) a bounds line with a non-numeric value",
      "I3a (r1 IA-02) a bounds line with a negative value", "I3a (r1 IA-02) two bounds lines"]
R2 = ["I3a (r2 IA-09) a malformed bounds line and swapped refs", "I3a (r2 IA-10) a bounds line just past it (1000)",
      "I3a (r2 IA-10) a bounds line of 5,000 digits"]
R2_BOUNDS_REASON = "I3a (r2 IA-09) the same, the bounds reason also listed"   # missed only before r1's repair, which added the bounds check
R3 = ["I3a (r3 IA-11) a bounds line ending in a no-break space", "I3a (r3 IA-11) a bounds line ending in an ideographic space"]


def main():
    vp2, scratch = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(scratch, exist_ok=True)
    base = tempfile.mkdtemp(prefix="eco115-redfirst-", dir=scratch)
    controls = [
        ("r1-decision", decision_control(base, vp2, "35961c3", R1 + R2 + [R2_BOUNDS_REASON] + R3,
                                         ["== D4 written into the decision records on every case that decided rows: False"])),
        ("r2-decision", decision_control(base, vp2, "2aa2d7d", R2 + R3, [])),
        ("r3-decision", decision_control(base, vp2, "7eddaba", R3,
                                         ["== I3a and D5 read the bounds line alike on 84 lines (values x line ends): False"])),
        ("c5", c5_control(base)),
        ("domain", domain_control(base)),
    ]
    for name, (ok, detail) in controls:
        print(f"{'SIGNATURE' if ok else 'OTHER    '} {name}: {detail}")
    good = sum(ok for _, (ok, _) in controls)
    print(f"red-first controls showing their own failure: {good} of {len(controls)}")
    # inspection r5 IA-14's probe, kept: a wrong set-up must fail its control, not pass it
    global git_show
    real = git_show
    git_show = lambda rev, name: real("35961c3", name)   # noqa: E731  — stage the manufacture tree whatever revision is asked
    try:
        wrong_rev = decision_control(base, vp2, "2aa2d7d", R2 + R3, [])
    finally:
        git_show = real
    negatives = [("r2 control with 35961c3 staged", wrong_rev), ("c5 control without the shared parser", c5_control(base, "rehearse_decision_v2.py"))]
    for name, (ok, detail) in negatives:
        print(f"{'REFUSED  ' if not ok else 'ACCEPTED '} negative, {name}: {detail}")
    refused = sum(not ok for _, (ok, _) in negatives)
    print(f"wrong set-ups refused: {refused} of {len(negatives)}")
    return 0 if good == len(controls) and refused == len(negatives) else 1


if __name__ == "__main__":
    sys.exit(main())
