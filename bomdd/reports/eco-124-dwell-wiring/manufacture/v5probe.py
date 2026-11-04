"""Probe prompts in BomDD: does the session see the hook text at all? One run per prompt, reply recorded as is."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v5
top = sys.argv[1]
PROMPTS = [
    "Do not use any tools. Is there any SessionStart hook output in your context? If yes, copy it exactly; if no, say NO.",
    "Do not use any tools. In your context, find the text 'open 3, over 14 d'. Copy the whole line that contains it, or say NOT FOUND.",
]
for p in PROMPTS:
    r = subprocess.run(["claude", "-p", p, "--allowedTools", ""], cwd=top, capture_output=True, timeout=300, env=v5.clean_env())
    print("PROMPT |", p)
    print("exit", r.returncode)
    for l in r.stdout.decode("utf-8", "replace").strip().splitlines():
        print("  reply |", l)
