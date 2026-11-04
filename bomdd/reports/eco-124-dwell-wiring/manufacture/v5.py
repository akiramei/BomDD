"""ECO-124 V5: a new Claude Code session, started for the purpose in BomDD and in ViewTube, quotes the brief it received at start.

  python -X utf8 v5.py <repos root>

For each repository: the brief by hand (bomdd-job --dwell --brief, run just before), then a new headless session
(`claude -p`, cwd = the repository, no tools allowed) asked to quote verbatim every line starting with "dwell:", "DECIDE:" or
"backlog:" that it received as context at session start, or NONE. PASS when the session's quoted "dwell:" line equals the hand-run
line 1. The session is a real Claude Code start (SessionStart source "startup"); its reply is recorded as is.
"""
import subprocess
import sys
from pathlib import Path

PROMPT = ("Do not use any tools. Quote verbatim, one per line, every line that starts with 'dwell:', 'DECIDE:' or 'backlog:' "
          "that you received as context at the start of this session (for example from a SessionStart hook). "
          "If you received none, reply with the single word NONE.")
REGS = [("BomDD", "bomdd/60-change-register.yaml"), ("ViewTube", "bomdd/process/change-register.yaml")]


def main():
    root = Path(sys.argv[1]).resolve()
    tool = root / "BomDD/method/tools/bomdd-job.py"
    fails = 0
    for repo, rel in REGS:
        top = root / repo
        hand = subprocess.run([sys.executable, "-X", "utf8", str(tool), "--dwell", "--brief", "--register", rel], cwd=top,
                              capture_output=True).stdout.decode("utf-8").splitlines()
        r = subprocess.run(["claude", "-p", PROMPT, "--allowedTools", ""], cwd=top, capture_output=True, timeout=300)
        reply = r.stdout.decode("utf-8", "replace").strip().splitlines()
        quoted = next((l.strip().strip("`") for l in reply if l.strip().strip("`").startswith("dwell:")), None)
        ok = r.returncode == 0 and quoted == hand[0]
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {repo}: session exit {r.returncode}")
        print(f"  hand line 1   | {hand[0] if hand else '(none)'}")
        print(f"  session quote | {quoted}")
        for l in reply:
            print(f"    reply | {l}")
    print(f"V5 {'PASS' if not fails else 'FAIL'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
