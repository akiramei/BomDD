"""EXP-20261030-03 - take each deriver's table from its stored transcript (definitions.md section 5.1). Nothing is retyped.

Usage: python extract_tables.py <staging-dir> <agents.json> <subagents-dir>
agents.json = {"T01": "<agent id>", ...}; the transcript is <subagents-dir>/agent-<id>.jsonl.
Source, in order: the content of the deriver's last Write to <Tnn>/table.json (refused by the harness, so never written), else the
last ```json block of its SubagentHandback message. Writes <staging>/<Tnn>/table.json byte-for-byte as authored and prints the
source, the derivation time (first to last transcript timestamp) and every path touched outside the package.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BLOCK = re.compile(r"```\s*json[ \t]*\r?\n(.*?)\r?\n```", re.S | re.I)


def norm(p):
    return str(p).replace("\\", "/").lower()


def scan(path, pkg):
    write, handback, touched, stamps, seen = None, None, [], [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(o, dict):
            continue
        if o.get("timestamp"):
            stamps.append(datetime.fromisoformat(o["timestamp"].replace("Z", "+00:00")))
        if o.get("type") != "assistant":
            continue
        content = (o.get("message") or {}).get("content")
        for c in content if isinstance(content, list) else []:
            if not isinstance(c, dict) or c.get("type") != "tool_use" or c.get("id") in seen:
                continue
            seen.add(c.get("id"))
            inp = c.get("input") or {}
            name = c.get("name")
            if name == "Write" and norm(inp.get("file_path", "")).endswith(f"/{pkg.lower()}/table.json"):
                write = inp.get("content")
            elif name == "SubagentHandback":
                handback = inp.get("message")
            else:
                for k in ("file_path", "path", "command", "pattern"):
                    if k in inp:
                        touched.append((name, k, str(inp[k])))
    return write, handback, touched, stamps


def main():
    stage, agents, sub = Path(sys.argv[1]).resolve(), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")), Path(sys.argv[3])
    for pkg, aid in sorted(agents.items()):
        write, handback, touched, stamps = scan(sub / f"agent-{aid}.jsonl", pkg)
        if write:
            text, source = write, "write-content"
        else:
            blocks = BLOCK.findall(handback or "")
            text, source = (blocks[-1], "handback-block") if blocks else (None, "none")
        if text is not None:
            (stage / pkg / "table.json").write_bytes(text.encode("utf-8"))
        root = f"{norm(stage)}/{pkg.lower()}"
        outside = [t for t in touched if t[0] == "Bash" or (t[1] in ("file_path", "path") and not norm(t[2]).startswith(root))]
        minutes = round((max(stamps) - min(stamps)).total_seconds() / 60, 1) if stamps else None
        sys.stdout.write(f"{pkg} source={source} chars={len(text or '')} minutes={minutes} tool_calls={len(touched)} "
                         f"outside={outside}\n")


if __name__ == "__main__":
    main()
