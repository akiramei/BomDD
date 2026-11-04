"""Repeat V5's headless session N times in one repository; per run: hook output delivered (stream event) and the reply."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v5
top, n = sys.argv[1], int(sys.argv[2])
model = ["--model", sys.argv[3]] if len(sys.argv) > 3 else []   # optional; without it the CLI's default model
for i in range(n):
    r = subprocess.run(["claude", "-p", v5.PROMPT, "--allowedTools", "", "--output-format", "stream-json", "--verbose",
                        "--include-hook-events"] + model, cwd=top, capture_output=True, timeout=300, env=v5.clean_env())
    hook, result, sid, used = None, None, None, None
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        try:
            d = json.loads(line)
        except Exception:
            continue
        sid = d.get("session_id", sid)
        if d.get("type") == "system" and d.get("subtype") == "init":
            used = d.get("model")
        if d.get("subtype") == "hook_response" and "dwell:" in (d.get("stdout") or ""):
            hook = d["stdout"].splitlines()[0]
        if d.get("type") == "result":
            result = d.get("result")
    print(f"run {i + 1} exit {r.returncode} session {sid} model {used}")
    print(f"  hook line 1 | {hook}")
    for l in (result or "(no result)").splitlines():
        print(f"  reply       | {l}")
