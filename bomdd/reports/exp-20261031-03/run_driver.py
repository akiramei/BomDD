"""EXP-20261031-03 step 1 (definitions sections 6 and 8): archive the authority, build the driver next to it, run it.

    python run_driver.py <staging>      # e.g. <scratchpad>/exp08; never a folder inside a repository
Writes expected.json and driver-run.json into this folder. MoviePad's settings.json mtime is recorded before and after.
"""
import hashlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
MOVIEPAD = HERE.parents[3] / "MoviePad"
COMMIT = "126eae9"
SETTINGS = pathlib.Path(os.environ["LOCALAPPDATA"]) / "MoviePad" / "settings.json"


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def mtime():
    return SETTINGS.stat().st_mtime_ns if SETTINGS.exists() else None


def main():
    staging = pathlib.Path(sys.argv[1]).resolve()
    staging.mkdir(parents=True, exist_ok=False)
    authority = staging / "authority"
    tar = subprocess.run(["git", "-C", str(MOVIEPAD), "archive", "--format=tar", COMMIT], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(authority, filter="data")
    dest = staging / "driver"
    dest.mkdir()
    for f in ("Driver.csproj", "Program.cs"):
        shutil.copyfile(HERE / "driver" / f, dest / f)
    b = subprocess.run(["dotnet", "build", str(dest / "Driver.csproj"), "-nologo", "-v", "q", f"-p:AuthorityDir={authority}"],
                       capture_output=True, text=True, timeout=900, encoding="utf-8", errors="replace")
    print(b.stdout[-2000:], b.stderr[-2000:])
    if b.returncode:
        sys.exit(f"build failed ({b.returncode}) - stop (section 10)")
    dll = sorted(dest.glob("bin/**/Driver.dll"))[-1]
    out = staging / "expected.json"
    before = mtime()
    r = subprocess.run(["dotnet", str(dll), str(out)], capture_output=True, text=True, timeout=300, encoding="utf-8",
                       errors="replace")
    after = mtime()
    print(r.stdout, r.stderr[-3000:])
    run = {"authority_commit": COMMIT, "archive_tar_sha256": hashlib.sha256(tar).hexdigest(),
           "driver_dll_sha256": sha(dll), "exit": r.returncode, "stdout": r.stdout.strip(),
           "settings_json": str(SETTINGS), "settings_mtime_ns_before": before, "settings_mtime_ns_after": after,
           "settings_unchanged": before == after}
    if r.returncode == 0:
        shutil.copyfile(out, HERE / "expected.json")
        run["expected_json_sha256"] = sha(HERE / "expected.json")
    (HERE / "driver-run.json").write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(run, indent=1))
    if r.returncode or before != after:
        sys.exit("driver failed or settings.json changed - stop (section 10)")


if __name__ == "__main__":
    main()
