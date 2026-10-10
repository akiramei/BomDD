"""Read-only timing of the ViewTube commit-gate stages (no staging, no commit)."""
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")


def t(name, cmd):
    s = time.perf_counter()
    p = subprocess.run(cmd, cwd=VT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    e = time.perf_counter() - s
    last = (p.stdout + p.stderr).strip().splitlines()[-1:] or [""]
    print(f"{name:32} rc={p.returncode} {e:7.1f}s | {last[0][:110]}", flush=True)
    return e


py = sys.executable
t("python -c 'import yaml'", [py, "-c", "import yaml"])
t("validate_process --quiet", [py, "bomdd/tools/validate_process.py", "--quiet"])
t("validate_release_workflow", [py, "bomdd/tools/validate_release_workflow.py"])
t("validate_run_evidence", [py, "bomdd/tools/validate_run_evidence.py"])
t("validate_record_citations", [py, "bomdd/tools/validate_record_citations.py"])
t("validate_mcp_host_location", [py, "bomdd/tools/validate_mcp_host_location.py"])
tmp = tempfile.mkdtemp()
t("git checkout-index --all", ["git", "checkout-index", "--all", f"--prefix={tmp}/"])
s = time.perf_counter()
shutil.rmtree(tmp, ignore_errors=True)
print(f"{'rm -rf (checkout copy)':32}      {time.perf_counter() - s:7.1f}s")
