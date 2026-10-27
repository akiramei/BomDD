"""Count xunit v3 <test> result words over every committed test-results.xml at a6314a87 (read from git, no working tree)."""
import collections
import subprocess
import sys
import xml.etree.ElementTree as ET

repo = sys.argv[1]
files = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", "a6314a87", "test-results"], capture_output=True, text=True).stdout.split()
files = [f for f in files if f.endswith("test-results.xml")]
c = collections.Counter()
for f in files:
    data = subprocess.run(["git", "-C", repo, "show", f"a6314a87:{f}"], capture_output=True).stdout
    try:
        for t in ET.fromstring(data).iter("test"):
            c[t.get("result")] += 1
    except ET.ParseError:
        c["<unparsed file>"] += 1
print(len(files), "files", dict(c))
