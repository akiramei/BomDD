"""Copy this session's transcript lines inside [since, until) into a temp tree that keeps measure.py's main/sub split.
Usage: python window_copy.py SESSION_JSONL SUBAGENT_DIR OUT_DIR SINCE UNTIL"""
import json
import os
import sys

main, subdir, out, since, until = sys.argv[1:6]
os.makedirs(os.path.join(out, "subagents"), exist_ok=True)


def copy(src, dst):
    kept = 0
    with open(src, encoding="utf-8") as f, open(dst, "w", encoding="utf-8") as g:
        for line in f:
            try:
                t = json.loads(line).get("timestamp")
            except Exception:
                continue
            if t and since <= t < until:
                g.write(line)
                kept += 1
    return kept


print("main", copy(main, os.path.join(out, "main.jsonl")))
n = 0
for name in os.listdir(subdir):
    if name.endswith(".jsonl"):
        k = copy(os.path.join(subdir, name), os.path.join(out, "subagents", name))
        n += k > 0
print("subagent files with lines in window", n)
