"""Copy harness/ into the staging folder next to the authority archive and build it there (never inside a repository).

    python build_harness.py <staging>      # expects <staging>/authority = git archive of MoviePad 126eae9
Prints the path of the built harness.dll.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent


def main():
    staging = pathlib.Path(sys.argv[1]).resolve()
    authority = staging / "authority"
    if not (authority / "MoviePad.csproj").is_file():
        sys.exit(f"no authority archive at {authority}")
    dest = staging / "harness"
    dest.mkdir(exist_ok=True)
    for f in ("Harness.csproj", "Program.cs", "SelfTest.cs"):
        shutil.copyfile(HERE / "harness" / f, dest / f)
    p = subprocess.run(["dotnet", "build", str(dest / "Harness.csproj"), "-nologo", "-v", "q",
                        f"-p:AuthorityDir={authority}"], capture_output=True, text=True, timeout=900,
                       encoding="utf-8", errors="replace")
    sys.stdout.write(p.stdout[-3000:])
    sys.stderr.write(p.stderr[-3000:])
    if p.returncode:
        sys.exit(p.returncode)
    dlls = sorted(dest.glob("bin/**/Harness.dll"))
    print(dlls[-1] if dlls else "no Harness.dll")


if __name__ == "__main__":
    main()
