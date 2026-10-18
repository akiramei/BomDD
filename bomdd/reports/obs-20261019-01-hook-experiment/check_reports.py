"""Check the hook's report sha256 against the reports in the subagents' own transcripts, and the stored snapshots against their names."""
import hashlib
import json
import sys
from pathlib import Path

ledger, subdir, store = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
logged = [(r["agent_id"], r["report_sha256"]) for r in map(json.loads, ledger.open(encoding="utf-8")) if r.get("report_sha256")]
actual = []
for agent in sorted({a for a, _ in logged}):
    f = subdir / f"agent-{agent}.jsonl"
    for ln in f.open(encoding="utf-8"):
        r = json.loads(ln)
        if r.get("type") == "assistant":
            for c in r["message"].get("content") or []:
                if c.get("type") == "tool_use" and c.get("name") == "SubagentHandback":
                    actual.append((agent, hashlib.sha256((c["input"].get("message") or "").encode("utf-8")).hexdigest()))
per = lambda pairs: {a: [s for b, s in pairs if b == a] for a in {x for x, _ in pairs}}
print("reports logged by the hook:", len(logged), "| in the transcripts:", len(actual), "| equal per agent, in order:", per(logged) == per(actual))
for p in sorted(store.iterdir()):
    print("stored", p.name[:12], "re-hash equals name:", hashlib.sha256(p.read_bytes()).hexdigest() == p.name, p.stat().st_size, "bytes")
