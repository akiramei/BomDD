"""Extract the primary records for the review-origin measurement from a Claude Code session transcript and its subagent transcripts.

Usage: python -B extract_primary.py <session.jsonl> <subagents dir> <out dir> <file-history dir of the session>
  (file-history dir: ~/.claude/file-history/<session id>/ — Claude Code's checkpoint copies)

Writes (JSON Lines, one record per line, UTF-8, LF):
  reviews.jsonl  every review request sent to a reviewer subagent and every report it handed back, in time order
                 {agent, seq, kind: request|report, ts, source: {file, line}, text}
  edits.jsonl    every file-writing tool call of the main session (Write content, Edit old/new strings, Bash and PowerShell commands), with
                 its tool result's error flag {seq, ts, tool, file_path, source: {file, line}, payload, old_string, replace_all, result}
  file-history.json, file-history/   the checkpoint copies of the two design documents (full content at a snapshot), with their times
  sources.json   the sha256 and size of each transcript file read
The measurement (`measure_origin.py`) reads only these files, so a third party can re-measure without the transcripts.
"""
import hashlib
import json
import sys
from pathlib import Path

SRC, SUBDIR, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
sources = {}


def read(path):
    data = path.read_bytes()
    sources[path.name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    return [(i, json.loads(ln)) for i, ln in enumerate(data.decode("utf-8").splitlines(), 1) if ln.strip()]


reviews = []
for f in sorted(SUBDIR.glob("agent-*.jsonl")):
    agent = f.stem.replace("agent-", "")
    for ln, r in read(f):
        if r.get("type") == "user" and isinstance(r["message"].get("content"), str):
            reviews.append({"agent": agent, "kind": "request", "ts": r["timestamp"], "source": {"file": f.name, "line": ln},
                            "text": r["message"]["content"]})
        elif r.get("type") == "assistant":
            for c in r["message"].get("content") or []:
                if c.get("type") == "tool_use" and c.get("name") == "SubagentHandback":
                    reviews.append({"agent": agent, "kind": "report", "ts": r["timestamp"], "source": {"file": f.name, "line": ln},
                                    "text": (c.get("input") or {}).get("message", "")})
reviews.sort(key=lambda x: (x["agent"], x["ts"]))
seq = {}
for x in reviews:
    seq[(x["agent"], x["kind"])] = seq.get((x["agent"], x["kind"]), 0) + 1
    x["seq"] = seq[(x["agent"], x["kind"])]

main = read(SRC)
results = {}
for ln, r in main:
    if r.get("type") == "user" and isinstance(r["message"].get("content"), list):
        for c in r["message"]["content"]:
            if c.get("type") == "tool_result":
                body = c.get("content")
                body = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
                results[c.get("tool_use_id")] = {"is_error": bool(c.get("is_error")) or body.lstrip().startswith("<tool_use_error>"),
                                                 "head": body[:300]}
edits = []
for ln, r in main:
    if r.get("type") != "assistant":
        continue
    for c in r["message"].get("content") or []:
        if c.get("type") != "tool_use":
            continue
        i, name = c.get("input") or {}, c.get("name")
        payload = {"Write": i.get("content"), "Edit": i.get("new_string"), "Bash": i.get("command"), "PowerShell": i.get("command")}.get(name)
        if payload:
            edits.append({"ts": r["timestamp"], "tool": name, "file_path": i.get("file_path"), "source": {"file": SRC.name, "line": ln},
                          "payload": payload, "old_string": i.get("old_string") if name == "Edit" else None,
                          "replace_all": bool(i.get("replace_all")) if name == "Edit" else None,
                          "result": results.get(c.get("id"))})
edits.sort(key=lambda x: x["ts"])
for n, e in enumerate(edits, 1):
    e["seq"] = n

# file-history backups (Claude Code's checkpoints: the full content of a tracked file at a snapshot) for the design documents
FH = Path(sys.argv[4]) if len(sys.argv) > 4 else None
DESIGN = ("60-change-order-eco-112.md", "60-change-order-eco-113.md")
backups = {}
for ln, r in main:
    entries = []
    if r.get("type") == "file-history-snapshot":
        entries = list(((r.get("snapshot") or {}).get("trackedFileBackups") or {}).items())
    elif r.get("type") == "file-history-delta":
        entries = [(r.get("trackingPath"), r.get("backup") or {})]
    for path, b in entries:
        if path and path.replace("\\", "/").endswith(DESIGN) and b.get("backupFileName"):
            backups[b["backupFileName"]] = {"tracking_path": path, "version": b.get("version"), "backup_time": b.get("backupTime"),
                                            "backup_file": b["backupFileName"], "source": {"file": SRC.name, "line": ln}}
fh_out = OUT / "file-history"
fh_out.mkdir(exist_ok=True)
index = []
for name, b in sorted(backups.items(), key=lambda kv: kv[1]["backup_time"]):
    src = FH / name if FH else None
    if src is not None and src.exists():
        data = src.read_bytes()
        (fh_out / name.replace("@", "_at_")).write_bytes(data)
        b.update(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), copied_as=f"file-history/{name.replace('@', '_at_')}")
    else:
        b.update(missing=True)
    index.append(b)
(OUT / "file-history.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def dump(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


dump("reviews.jsonl", reviews)
dump("edits.jsonl", edits)
(OUT / "sources.json").write_text(json.dumps(sources, indent=1) + "\n", encoding="utf-8", newline="\n")
print(f"reviews {len(reviews)} (requests {sum(x['kind'] == 'request' for x in reviews)}, reports {sum(x['kind'] == 'report' for x in reviews)}); edits {len(edits)}")
