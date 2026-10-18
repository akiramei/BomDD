"""OBS-20261019-01 feasibility experiment (temporary; not a permanent mechanism). A Claude Code hook that snapshots review targets.

Invoked by .claude/settings.local.json (temporary) with the event name as argv[1]; reads the hook input JSON on stdin.
  PreToolUse  Agent / SendMessage   the request's "REVIEW-TARGET: <path>" lines -> each file stored with bomdd-run's store_brief (ECO-112 B2,
                                     unchanged; store bucket EXP-20261019-01); a failure blocks the call (exit 2, reason on stderr)
  PreToolUse  Read (inside a subagent only)   the file about to be read -> stored the same way (content at read time; never blocks)
  PreToolUse  Bash (inside a subagent only)   the command is logged (files it reads are not identified)
  PreToolUse  SubagentHandback (inside a subagent)   the report text's sha256 is logged with the agent id
  PostToolUse Agent      the launch's tool_use_id and the agent id from tool_response are logged (the link from request to agent)
  SubagentStop           agent id, transcript path, sha256 of last_assistant_message are logged
Every invocation appends one JSON line to the experiment ledger.
"""
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "ledger.jsonl"
REPO = Path("C:/Users/akira/source/repos/BomDD")
BUCKET = "EXP-20261019-01"


def log(rec):
    rec["logged_at"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    with LEDGER.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def store(path):
    spec = importlib.util.spec_from_file_location("bomdd_run", REPO / "method" / "tools" / "bomdd-run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    common = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    common = Path(common) if Path(common).is_absolute() else (REPO / common).resolve()
    info, code, msg, created = mod.store_brief(REPO, common, BUCKET, path)
    return {"path": path, "record": info, "code": code, "message": msg, "created": created}


CUR = {"tool": None}


def main():
    event = sys.argv[1]
    data = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    tool, ti = data.get("tool_name"), data.get("tool_input") or {}
    CUR["tool"] = tool
    base = {"event": event, "tool_name": tool, "tool_use_id": data.get("tool_use_id"), "agent_id": data.get("agent_id"),
            "agent_type": data.get("agent_type"), "session_id": data.get("session_id")}
    if event == "PreToolUse" and tool in ("Agent", "SendMessage"):
        text = ti.get("prompt") if tool == "Agent" else ti.get("message")
        targets = re.findall(r"^REVIEW-TARGET:\s*(.+?)\s*$", text or "", re.M)
        snaps = [store(t) for t in targets]
        bad = [s for s in snaps if s["code"]]
        log(dict(base, to=ti.get("to"), targets=targets, snapshots=snaps, request_sha256=hashlib.sha256((text or "").encode("utf-8")).hexdigest(),
                 blocked=bool(bad)))
        if bad:
            sys.stderr.write("review snapshot failed: " + "; ".join(f"{s['code']} {s['path']}" for s in bad) + "\n")
            sys.exit(2)
        return
    if event == "PreToolUse" and data.get("agent_id"):
        if tool == "Read" and ti.get("file_path"):
            log(dict(base, read=store(ti["file_path"])))
        elif tool == "Bash":
            log(dict(base, command=ti.get("command")))
        elif tool == "SubagentHandback":
            msg = ti.get("message") or ""
            log(dict(base, report_sha256=hashlib.sha256(msg.encode("utf-8")).hexdigest(), report_head=msg[:120]))
        return
    if event == "PostToolUse" and tool == "Agent":
        resp = data.get("tool_response")
        rid = resp.get("agentId") if isinstance(resp, dict) else None
        log(dict(base, launched_agent_id=rid, response_keys=sorted(resp) if isinstance(resp, dict) else str(type(resp))))
        return
    if event == "SubagentStop":
        last = data.get("last_assistant_message") or ""
        log(dict(base, agent_transcript_path=data.get("agent_transcript_path"),
                 last_message_sha256=hashlib.sha256(last.encode("utf-8")).hexdigest(), last_message_head=last[:120]))
        return


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:   # an unexpected failure is logged; it blocks only a review launch or follow-up (fail closed there, never elsewhere)
        try:
            log({"event": sys.argv[1] if len(sys.argv) > 1 else "?", "tool_name": CUR["tool"], "error": repr(e)})
        except Exception:
            pass
        if len(sys.argv) > 1 and sys.argv[1] == "PreToolUse" and CUR["tool"] in ("Agent", "SendMessage"):
            sys.stderr.write(f"review snapshot hook error: {e!r}\n")
            sys.exit(2)
        sys.exit(0)
