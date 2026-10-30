"""Isolation of an agent run (definitions.md section 8): every path the agent's tool calls name (Read / Glob / Grep paths,
Bash commands, written content), flagged when it leaves the folders the agent was given.

    python isolation.py <agent-transcript.jsonl> <allowed-prefix> [<allowed-prefix> ...]   # "../x" = a relative allowance
Paths are compared case-insensitively with "/" separators. Prints counts per tool and every flag.
"""
import json
import re
import sys
from pathlib import Path

PATHLIKE = re.compile(r"(?i)(?:[a-z]:[/\\]|/c/|\.\.[/\\])[^\s\"'`|;&<>()]*")
ALWAYS_BAD = re.compile(r"(?i)source[/\\]+repos|\.claude[/\\]+projects|[/\\]memory[/\\]|bomdd[/\\]reports")


def norm(p):
    p = p.replace("\\", "/")
    if p.lower().startswith("/c/"):
        p = "c:/" + p[3:]
    return p.lower().rstrip("/")


def tool_texts(path):
    seen = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(o, dict) or o.get("type") != "assistant":
            continue
        for c in (o.get("message") or {}).get("content") or []:
            if not isinstance(c, dict) or c.get("type") != "tool_use" or c.get("id") in seen:
                continue
            seen.add(c.get("id"))
            inp = c.get("input") or {}
            for k in ("file_path", "path", "pattern", "command", "content"):
                if isinstance(inp.get(k), str):
                    yield c.get("name"), k, inp[k]


def main(transcript, allowed):
    allowed = [norm(a) for a in allowed]
    counts, flags = {}, []
    for name, k, v in tool_texts(transcript):
        counts[name] = counts.get(name, 0) + 1
        for m in ALWAYS_BAD.finditer(v):
            flags.append(f"{name}.{k}: names {m.group(0)!r}: {v[max(0, m.start() - 80):m.end() + 80]!r}")
        if k == "content":
            continue
        for m in PATHLIKE.finditer(v):
            p = norm(m.group(0))
            if p.startswith(".."):
                # relative to the agent's folder: allowed only when given as an allowed "../name" prefix
                if not any(p.startswith(a) for a in allowed if a.startswith("..")):
                    flags.append(f"{name}.{k}: outside (relative): {m.group(0)}")
                continue
            if not any(p.startswith(a) for a in allowed):
                flags.append(f"{name}.{k}: outside: {m.group(0)}")
    print("tool calls", counts, "flags", len(flags))
    for f in flags:
        print("  ", f[:400])
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:]))
