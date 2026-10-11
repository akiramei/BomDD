"""Write the pre-commit hook's synthetic message (bomdd/hooks/pre-commit:96-117) for REPO's staged register to OUT."""
import subprocess
import sys
from pathlib import Path

import yaml

repo, out = sys.argv[1], sys.argv[2]
register = yaml.safe_load(subprocess.check_output(
    ["git", "show", ":bomdd/process/change-register.yaml"], cwd=repo, text=True, encoding="utf-8",
    errors="strict"))
lines = []
for item in register.get("changes", []):
    eco = item.get("id")
    if eco:
        lines.append(f"BomDD-ECO-Fix: {eco}")
        lines.append(f"BomDD-ECO-Accept: {eco}")
Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"{len(lines)} trailer lines")
