"""Write the git versions of the two design documents as anchors for measure_origin.py.

Usage: python -B make_anchors.py <repo> <out dir>   (writes <out dir>/index.json and one file per commit and document)
Every commit that changed bomdd/60-change-order-eco-112.md or -113.md; its committer time (UTC) is the anchor's time.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO, OUT = sys.argv[1], Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
index = []
for key, path in (("112", "bomdd/60-change-order-eco-112.md"), ("113", "bomdd/60-change-order-eco-113.md")):
    log = subprocess.run(["git", "-C", REPO, "log", "--format=%H %ct", "--", path], capture_output=True, text=True, check=True).stdout.split("\n")
    for ln in filter(None, log):
        sha, ct = ln.split()
        data = subprocess.run(["git", "-C", REPO, "show", f"{sha}:{path}"], capture_output=True, check=True).stdout
        fn = f"{key}-{sha[:7]}.md"
        (OUT / fn).write_bytes(data)
        ts = datetime.fromtimestamp(int(ct), timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        index.append({"key": key, "commit": sha, "ts": ts, "file": fn})
index.sort(key=lambda a: a["ts"])
(OUT / "index.json").write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8", newline="\n")
print(len(index), "anchors")
