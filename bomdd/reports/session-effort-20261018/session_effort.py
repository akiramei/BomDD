"""Effort measurement of one Claude Code session transcript (observed values only).

Usage: python -B session_effort.py <session.jsonl> <subagents dir> > out.md

Partition of the session's wall clock into three states, by what ends each idle gap:
  AI_ACTIVE   from a turn's start (a human message, a task notification or a peer report) to the last assistant/tool record of that turn
  BG_WAIT     idle gap ended by a task notification or a peer (subagent) report: the AI had ended its turn to wait for background work
  HUMAN_WAIT  idle gap ended by a human message
Inside AI_ACTIVE: tool execution (tool_use -> its tool_result) by tool and by Bash description class; the rest is model time
(generation, thinking, harness overhead). Background Bash tasks: start (the tool_use with run_in_background) -> its notification.
Tokens: assistant records deduplicated by requestId (one API call is split into several records).
"""
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

JST = timedelta(hours=9)
SRC, SUBDIR = Path(sys.argv[1]), Path(sys.argv[2])


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def fmt(td):
    s = int(td.total_seconds()) if isinstance(td, timedelta) else int(td)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


recs = [json.loads(ln) for ln in SRC.open(encoding="utf-8")]
ev = [r for r in recs if r.get("timestamp") and r.get("type") in ("user", "assistant", "system", "attachment")]
ev.sort(key=lambda r: r["timestamp"])


def kind(r):
    if r["type"] == "user":
        m = r["message"].get("content")
        if isinstance(m, list) and any(x.get("type") == "tool_result" for x in m):
            return "tool_result"
        return (r.get("origin") or {}).get("kind") or "user-other"
    return r["type"]


STARTERS = {"human", "task-notification", "peer"}
t0, t1 = ts(ev[0]["timestamp"]), ts(ev[-1]["timestamp"])
state = Counter()
gaps = []           # (start, end, ender)
turns = []          # (start, end, starter, text)
last_active = ts(ev[0]["timestamp"])
cur = None
for r in ev:
    k, t = kind(r), ts(r["timestamp"])
    if k in STARTERS:
        if cur:
            turns.append(cur)
        gap = t - last_active
        state["HUMAN_WAIT" if k == "human" else "BG_WAIT"] += gap.total_seconds()
        if k != "human":
            state[f"BG_WAIT ended by {k}"] += gap.total_seconds()
        gaps.append((last_active, t, k))
        m = r["message"].get("content")
        cur = [t, t, k, (m if isinstance(m, str) else "")[:70].replace("\n", " ")]
        last_active = t
    else:
        if cur is None:
            cur = [t, t, "start", ""]
        if r["type"] in ("assistant", "user", "system"):
            state["AI_ACTIVE"] += (t - last_active).total_seconds()
            last_active = t
            cur[1] = t
if cur:
    turns.append(cur)

# tool execution inside turns
uses = {}
tool_time = defaultdict(float)
tool_n = Counter()
bash_class_time = defaultdict(float)
bash_class_n = Counter()
bg_start = {}
bg_tasks = []
CLASSES = [
    ("self-conformance", re.compile(r"self-conformance", re.I)),
    ("CI wait", re.compile(r"gh run list|Wait for CI", re.I)),
    ("V3 instrument", re.compile(r"arm_inventory|V3 instrument|pinned V3", re.I)),
    ("inspection cell (codex)", re.compile(r"codex exec|independent inspection", re.I)),
    ("rule mutations", re.compile(r"rule.?mutation|Break each new rule", re.I)),
    ("selftests", re.compile(r"--selftest|selftests?", re.I)),
    ("git commit/push", re.compile(r"git (commit|push)|Commit and push", re.I)),
    ("witness/decision", re.compile(r"bomdd-witness|bomdd-run.py ECO-1", re.I)),
    ("read/search", re.compile(r"\b(sed -n|grep|cat|head|tail|ls|wc|awk)\b")),
]


def klass(desc, cmd):
    for name, rx in CLASSES:
        if rx.search(desc or "") or rx.search(cmd or ""):
            return name
    return "other"


for r in ev:
    if r["type"] == "assistant":
        for c in r["message"].get("content") or []:
            if c.get("type") == "tool_use":
                uses[c["id"]] = (ts(r["timestamp"]), c["name"], c.get("input") or {})
    elif kind(r) == "tool_result":
        for c in r["message"]["content"]:
            if c.get("type") == "tool_result" and c.get("tool_use_id") in uses:
                st, name, inp = uses[c["tool_use_id"]]
                dt = (ts(r["timestamp"]) - st).total_seconds()
                tool_time[name] += dt
                tool_n[name] += 1
                if name in ("Bash", "PowerShell"):
                    k2 = klass(inp.get("description"), inp.get("command"))
                    if inp.get("run_in_background"):
                        txt = c.get("content")
                        txt = txt if isinstance(txt, str) else json.dumps(txt)
                        m = re.search(r"ID: (\w+)", txt)
                        if m:
                            bg_start[m.group(1)] = (st, k2, inp.get("description"))
                    else:
                        bash_class_time[k2] += dt
                        bash_class_n[k2] += 1

for r in ev:
    if kind(r) == "task-notification":
        m = re.search(r"<task-id>(\w+)</task-id>", r["message"]["content"])
        if m and m.group(1) in bg_start:
            st, k2, desc = bg_start.pop(m.group(1))
            bg_tasks.append((st, ts(r["timestamp"]), k2, desc))

# tokens (dedupe by requestId)


def tokens(records):
    """One API call is split into several records; each field is taken as its maximum over the call's records (output grows per block)."""
    per = defaultdict(Counter)
    for r in records:
        if r.get("type") != "assistant":
            continue
        rid = r.get("requestId") or r.get("uuid")
        u = r["message"].get("usage") or {}
        for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
            per[rid][k] = max(per[rid][k], u.get(k) or 0)
    tot = Counter()
    for c in per.values():
        tot.update(c)
    tot["calls"] = len(per)
    return tot


main_tok = tokens(recs)
sub_rows = []
sub_tok = Counter()
for f in sorted(SUBDIR.glob("*.jsonl")):
    rs = [json.loads(ln) for ln in f.open(encoding="utf-8")]
    tt = [ts(r["timestamp"]) for r in rs if r.get("timestamp")]
    tk = tokens(rs)
    sub_tok.update(tk)
    sub_rows.append((f.stem, min(tt) + JST if tt else None, (max(tt) - min(tt)) if tt else timedelta(0), tk))

compact = [ts(r["timestamp"]) + JST for r in recs if r.get("type") == "system" and r.get("subtype") == "compact_boundary"]

out = []
P = out.append
P(f"# Session effort — `{SRC.name}`\n")
P(f"- span: {(t0 + JST):%Y-%m-%d %H:%M} → {(t1 + JST):%H:%M} JST = **{fmt(t1 - t0)}**; compactions: {len(compact)} ({', '.join(f'{c:%H:%M}' for c in compact)})")
tot = sum(state[k] for k in ("AI_ACTIVE", "BG_WAIT", "HUMAN_WAIT"))
P("\n## Wall clock by state\n\n| state | time | share |\n|---|---|---|")
for k in ("AI_ACTIVE", "BG_WAIT", "BG_WAIT ended by task-notification", "BG_WAIT ended by peer", "HUMAN_WAIT"):
    P(f"| {k} | {fmt(state[k])} | {state[k] / tot:.0%} |")
fg = sum(tool_time.values()) if "tool_time" in globals() else 0
P("\n## Turns started by a human message (each a ruling or request)\n\n| # | JST | wait before (human) | text (first 70 chars) |\n|---|---|---|---|")
hum = [g for g in gaps if g[2] == "human"]
hi = 0
for s, e, k, txt in turns:
    if k == "human":
        hi += 1
        g = next((g for g in hum if g[1] == s), None)
        P(f"| {hi} | {(s + JST):%H:%M} | {fmt(g[1] - g[0]) if g else '-'} | {txt.strip()[:70]} |")
P("\n## Segments between human messages (AI active / background wait inside each)\n\n| from human # | start JST | length | AI active | BG wait | turns | tool calls |\n|---|---|---|---|---|---|---|")
hstarts = [s for s, e, k, _ in turns if k == "human"] + [t1 + timedelta(seconds=1)]
for i in range(len(hstarts) - 1):
    a, b = hstarts[i], hstarts[i + 1]
    act = sum((min(e, b) - max(s, a)).total_seconds() for s, e, k, _ in turns if s >= a and s < b)
    bgw = sum((e - s).total_seconds() for s, e, k in gaps if k != "human" and s >= a and e < b)
    nt = sum(1 for s, e, k, _ in turns if a <= s < b)
    nc = sum(1 for u in uses.values() if a <= u[0] < b)
    end = max((e for s, e, k, _ in turns if a <= s < b), default=a)
    P(f"| {i + 1} | {(a + JST):%H:%M} | {fmt(end - a)} | {fmt(act)} | {fmt(bgw)} | {nt} | {nc} |")
P("\n## Tool execution inside AI-active time (foreground)\n\n| tool | calls | time |\n|---|---|---|")
for k, v in sorted(tool_time.items(), key=lambda x: -x[1]):
    P(f"| {k} | {tool_n[k]} | {fmt(v)} |")
P("\n### Foreground Bash/PowerShell by class\n\n| class | calls | time |\n|---|---|---|")
for k, v in sorted(bash_class_time.items(), key=lambda x: -x[1]):
    P(f"| {k} | {bash_class_n[k]} | {fmt(v)} |")
P("\n## Background tasks (start → completion notification)\n\n| class | n | total | max |\n|---|---|---|---|")
bgc = defaultdict(list)
for s, e, k2, d in bg_tasks:
    bgc[k2].append((e - s).total_seconds())
for k, v in sorted(bgc.items(), key=lambda x: -sum(x[1])):
    P(f"| {k} | {len(v)} | {fmt(sum(v))} | {fmt(max(v))} |")
P(f"\nunmatched background starts (no notification seen): {len(bg_start)}")
P("\n### Each background task\n\n| start JST | duration | class | description |\n|---|---|---|---|")
for s, e, k2, d in sorted(bg_tasks):
    P(f"| {(s + JST):%H:%M} | {fmt(e - s)} | {k2} | {(d or '')[:60]} |")
P("\n## Subagents\n\n| agent | start JST | span | API calls | output tokens | cache-read tokens |\n|---|---|---|---|---|---|")
for n, st, sp, tk in sub_rows:
    P(f"| {n} | {st:%H:%M} | {fmt(sp)} | {tk['calls']} | {tk['output_tokens']:,} | {tk['cache_read_input_tokens']:,} |")
P("\n## Tokens (assistant API calls, deduplicated by requestId)\n\n| scope | API calls | input | cache write | cache read | output |\n|---|---|---|---|---|---|")
for name, tk in (("main session", main_tok), ("subagents", sub_tok)):
    P(f"| {name} | {tk['calls']:,} | {tk['input_tokens']:,} | {tk['cache_creation_input_tokens']:,} | {tk['cache_read_input_tokens']:,} | {tk['output_tokens']:,} |")
P("\n## Limits\n\n- Times are transcript timestamps; a tool_use's time includes the harness's permission check and the result's write.")
P("- BG_WAIT and HUMAN_WAIT are told apart by what ended the gap; a human reply that arrives while background work also runs is HUMAN_WAIT.")
P("- Model time = AI_ACTIVE minus foreground tool time; it holds generation, thinking and harness overhead together.")
P("- Work outside this transcript (Codex inspection cells, CI) appears only as background-task durations; its own tokens are not counted.")
sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
