"""Summarise out/ from reproduce.py: seconds per hook block, then what each long Python process spent
its time on (from the timer log written by site/sitecustomize.py)."""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).resolve().parent / "out"
STAMP = re.compile(r"^(\++) (\d+\.\d+) (\d+) (.*)$")

# Line ranges of bomdd/hooks/pre-commit at e912e5d8 (identical at 769bb27a). Each block starts at
# the comment that introduces it.
PRE_COMMIT_BLOCKS = [
    (1, 50, "setup (tools, staged list, interpreter)"),
    (51, 86, "protected-path decision"),
    (87, 135, "validate_process (staged register: synthetic message)"),
    (136, 224, "release-workflow, run-evidence, record-citations, MCP-host validators"),
    (225, 257, "expectation coupling"),
    (258, 311, "capture-plan sweep"),
    (312, 379, "change impact (copy, trusted harness, validator)"),
    (380, 457, "UI-golden equipment qualification"),
    (458, 695, "UI-manufacturing equipment qualification"),
    (696, 704, "validate_process --selftest"),
]
DETAIL_LINES = {
    332: "change impact: checkout-index --all", 334: "change impact: narrowed copy",
    359: "change impact: trusted harness", 369: "change impact: validator", 378: "change impact: rm -rf",
    388: "UI-golden: checkout-index --all", 447: "UI-golden: harness", 456: "UI-golden: rm -rf",
    470: "UI-mfg: checkout-index --all", 490: "UI-mfg: ECO-VT-023 bootstrap check",
    670: "UI-mfg: harness", 694: "UI-mfg: rm -rf",
    124: "validate_process --commit-msg (synthetic)", 300: "capture-plan sweep runner",
    697: "validate_process --selftest",
}


def trace_costs(path):
    stamps = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = STAMP.match(line)
        if match:
            stamps.append((float(match.group(2)), int(match.group(3)), match.group(4)[:100]))
    costs = [(t1 - t0, line, cmd) for (t0, line, cmd), (t1, _, _) in zip(stamps, stamps[1:])]
    return stamps, costs


def block_of(line):
    for low, high, name in PRE_COMMIT_BLOCKS:
        if low <= line <= high:
            return name
    return "?"


def command_name(argv):
    if not argv:
        return "?"
    head = re.split(r"[\\/]", argv[0])[-1].lower().removesuffix(".exe")
    rest = argv[1:]
    if head in ("git",):
        words = []
        skip = False
        for item in rest:
            if skip:
                skip = False
                continue
            if item in ("-C", "-c"):
                skip = True
                continue
            if item.startswith("-"):
                continue
            words.append(item)
            break
        return "git " + (words[0] if words else "?")
    if head.startswith("python") or head == "py":
        scripts = [re.split(r"[\\/]", item)[-1] for item in rest if item.endswith(".py")]
        flags = [item for item in rest if item.startswith("--")][:1]
        if "-c" in rest:
            return "python -c"
        if "-" in rest:
            return "python - (stdin)"
        return "python " + (scripts[0] if scripts else "?") + (" " + flags[0] if flags else "")
    if head == "dotnet":
        verb = rest[0] if rest else "?"
        target = next((re.split(r"[\\/]", item)[-1] for item in rest[1:] if not item.startswith("-")), "")
        return f"dotnet {verb} {target}".strip()
    return head + (" " + re.split(r"[\\/]", rest[0])[-1] if rest else "")


def processes(log_path):
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    procs = []
    open_by_pid = {}
    for record in sorted(records, key=lambda item: item["t"]):
        pid = record["pid"]
        if record["event"] == "start":
            proc = {"pid": pid, "argv": record["argv"], "start": record["t"], "end": None, "runs": []}
            procs.append(proc)
            open_by_pid[pid] = proc
        elif record["event"] == "run" and pid in open_by_pid:
            open_by_pid[pid]["runs"].append(record)
        elif record["event"] == "exit" and pid in open_by_pid:
            open_by_pid.pop(pid)["end"] = record["t"]
    return procs


def main():
    if (OUT / "summary.txt").exists():
        print((OUT / "summary.txt").read_text(encoding="utf-8"))
    for hook in ("pre-commit", "commit-msg"):
        if not (OUT / f"{hook}.trace").exists():
            continue
        stamps, costs = trace_costs(OUT / f"{hook}.trace")
        if not stamps:
            continue
        print(f"== {hook}: traced span {stamps[-1][0] - stamps[0][0]:.1f}s")
        if hook == "pre-commit":
            per_block = defaultdict(float)
            for dt, line, _ in costs:
                per_block[block_of(line)] += dt
            for _, _, name in PRE_COMMIT_BLOCKS:
                print(f"  {per_block.get(name, 0.0):8.1f}s  {name}")
            per_line = defaultdict(float)
            for dt, line, _ in costs:
                per_line[line] += dt
            print("  -- named steps")
            for line, label in sorted(DETAIL_LINES.items()):
                if line in per_line:
                    print(f"  {per_line[line]:8.1f}s  L{line} {label}")
        print("  -- longest traced lines")
        for dt, line, cmd in sorted(costs, reverse=True)[:10]:
            print(f"  {dt:8.1f}s  L{line} {cmd}")

    print("\n== Python processes over 5 s (timer log), with what they waited on")
    for proc in processes(OUT / "timer-log.jsonl"):
        if proc["end"] is None:
            continue
        duration = proc["end"] - proc["start"]
        if duration < 5:
            continue
        grouped = defaultdict(lambda: [0, 0.0, 0.0])
        for run in proc["runs"]:
            entry = grouped[command_name(run["argv"])]
            entry[0] += 1
            entry[1] += run["dt"]
            entry[2] = max(entry[2], run["dt"])
        waited = sum(run["dt"] for run in proc["runs"])
        print(f"\n{duration:8.1f}s  {command_name(['python', *proc['argv']])}  "
              f"(children {waited:.1f}s, own {duration - waited:.1f}s, {len(proc['runs'])} calls)")
        for name, (count, total, longest) in sorted(grouped.items(), key=lambda item: -item[1][1])[:12]:
            print(f"    {total:8.1f}s  x{count:<4} max {longest:6.1f}s  {name}")


main()
