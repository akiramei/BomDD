"""ECO-122 V3 known-bad of the instrument: broken copies of the changed tool, each must turn its arm of v23.py red.

  python -X utf8 mutants.py <tool .py> <work dir>

  M1  the version key without the parse functions' source          -> expected red: V3b
  M2  a cached parse failure read back as an empty snapshot (hit)  -> expected red: V3d
  M3  every blob ever seen kept in the cache file                  -> expected red: V2 amend
  M4  a failure to write the cache raised                          -> expected red: V3c
Each substitution must apply exactly once (else the mutant is reported as not built). PASS when every mutant turns its expected arm red.
"""
import subprocess
import sys
from pathlib import Path

MUTANTS = [
    ("M1", "V3b",
     '        src = inspect.getsource(_dwell_snapshot) + "\\0" + inspect.getsource(_dwell_items)\n',
     '        src = ""\n'),
    ("M2", "V3d",
     '        out[b] = (snap, v[1], v[2])\n',
     '        out[b] = (snap if snap is not None else {}, v[1], v[2] if snap is not None else None)\n'),
    ("M3", "V2 amend",
     '        stats["write"] = _dwell_cache_save(path, key, rel, used) or "ok"\n',
     '        stats["write"] = _dwell_cache_save(path, key, rel, {**cached, **used}) or "ok"\n'),
    ("M4", "V3c",
     '    except OSError as e:\n        return f"{type(e).__name__}: {str(e)[:120]}"\n',
     '    except OSError as e:\n        raise\n'),
]


def main():
    tool, work = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    work.mkdir(parents=True, exist_ok=True)
    src = tool.read_text(encoding="utf-8")
    here = Path(__file__).resolve().parent
    ok_all = True
    for name, arm, a, b in MUTANTS:
        if src.count(a) != 1:
            print(f"{name}: NOT BUILT (substitution found {src.count(a)} times)")
            ok_all = False
            continue
        m = work / f"{name}.py"
        m.write_text(src.replace(a, b), encoding="utf-8", newline="\n")
        p = subprocess.run([sys.executable, "-X", "utf8", str(here / "v23.py"), str(m), str(work / f"{name}-run")],
                           capture_output=True, text=True, encoding="utf-8")
        lines = p.stdout.splitlines()
        red = [l.split(":")[0] for l in lines if ": FAIL" in l]
        hit = any(l.startswith(arm) and ": FAIL" in l for l in lines)
        ok_all &= hit
        print(f"{name} (expected red {arm}): {'RED as expected' if hit else 'NOT RED'}; red arms: {red}")
    print(f"known-bad {'PASS' if ok_all else 'FAIL'}: {'every mutant turned its arm red' if ok_all else 'a mutant was not caught'}")


if __name__ == "__main__":
    main()
