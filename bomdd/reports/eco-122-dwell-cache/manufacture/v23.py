"""ECO-122 V2 and V3 — growth, rewriting and a faulty cache, on a throwaway repository.

  python -X utf8 v23.py <tool .py> <work dir>

The tool is copied into <work dir> as an importable module, so the same script runs on the changed tool and on each broken copy
(mutants.py). Each arm prints PASS or FAIL; an exception inside an arm is a FAIL. `now` is fixed; results are compared as
json.dumps(result, sort_keys=True) against the same tool with no cache.

  V2 grow    after a warm run one new commit: parsed 1, hits = the other commits, result = no cache
  V2 amend   the last commit amended (other content): afterwards the cache file holds no blob outside the history; result = no cache
  V3a        the cache file cut in half, and replaced by text that is not JSON: a miss, every blob parsed, result = no cache, file rewritten
  V3b        a copy of the tool with one line of _dwell_snapshot's source changed, run on the first tool's cache: a miss (version key)
  V3c        the cache directory not writable (its path is a file): result = no cache, the write failure reported; and by the command
             line: exit 0, standard error says "write failed", standard output not an error
  V3d        a commit whose register does not parse: the same warning on the cold and on the warm run
  V3e        the declared limit, shown: a well-formed entry with a changed status is believed (result differs from no cache), and
             no cache gives the history's answer
"""
import datetime as dt
import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

NOW = dt.datetime(2026, 11, 4, 12, 0, tzinfo=dt.timezone.utc)
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x",
           GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)


def git(root, *a, days_ago=None):
    e = dict(ENV)
    if days_ago is not None:
        e["GIT_AUTHOR_DATE"] = e["GIT_COMMITTER_DATE"] = (NOW - dt.timedelta(days=days_ago)).isoformat()
    return subprocess.run(["git", "-C", str(root), *a], capture_output=True, env=e, check=True).stdout.decode().strip()


def blk(entries):
    return "changes:\n" + "".join(f"  - id: {i}\n    title: t\n    status: {s}\n" for i, s in entries)


def main():
    tool, work = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    def _rw(f, path, _):   # git objects are read-only on Windows
        os.chmod(path, 0o700)
        f(path)
    if work.exists():
        shutil.rmtree(work, onexc=_rw)
    work.mkdir(parents=True)
    mods = work / "mods"
    mods.mkdir()
    shutil.copyfile(tool, mods / "bj_t.py")
    src = (mods / "bj_t.py").read_text(encoding="utf-8")
    marker = '    data = yaml.load(blob, Loader=_dwell_loader())\n'
    assert src.count(marker) == 1, "the line to change in _dwell_snapshot is not found once"
    (mods / "bj_t2.py").write_text(src.replace(marker, marker.rstrip("\n") + "   # one changed line (V3b)\n"), encoding="utf-8")
    sys.path.insert(0, str(mods))
    bj = importlib.import_module("bj_t")
    bj2 = importlib.import_module("bj_t2")

    root = work / "repo"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "core.autocrlf", "false")
    (root / "bomdd").mkdir()
    reg = root / "bomdd" / "60-change-register.yaml"
    rel = "bomdd/60-change-register.yaml"

    def commit(text, days_ago, amend=False):
        reg.write_text(text, encoding="utf-8", newline="\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", *(["--amend"] if amend else []), "-m", f"d-{days_ago}", days_ago=days_ago)

    commit(blk([("ECO-001", "filed"), ("ECO-002", "filed")]), 40)
    commit(blk([("ECO-001", "implemented"), ("ECO-002", "filed")]), 30)
    commit("changes: [ {id: ECO-001, status: filed\n", 20)          # does not parse (V3d)
    commit(blk([("ECO-001", "filed"), ("ECO-002", "filed")]), 10)    # the same content as the first commit
    commit(blk([("ECO-001", "filed"), ("ECO-002", "implemented")]), 5)

    cdir = work / "cache"
    results = []

    def run(m=bj, cache_dir=None):
        st = {}
        return json.dumps(m.dwell(reg, 14, NOW, cache_dir=cache_dir, stats=st), ensure_ascii=False, sort_keys=True), st

    def arm(name, fn):
        try:
            ok, note = fn()
        except Exception as e:  # noqa: BLE001
            ok, note = False, f"{type(e).__name__}: {str(e)[:160]}"
        results.append((name, ok))
        print(f"{name}: {'PASS' if ok else 'FAIL'} — {note}")

    def history_blobs():
        return {git(root, "rev-parse", f"{s}:{rel}") for s in git(root, "log", "--format=%H", "--", rel).split()}

    def cache_file():
        return bj._dwell_cache_path(cdir, root, rel)

    def cached_blobs():
        return set(json.loads(cache_file().read_text(encoding="utf-8"))["blobs"])

    def v3d():
        base, _ = run()
        shutil.rmtree(cdir, ignore_errors=True)
        cold, s1 = run(cache_dir=cdir)
        warm, s2 = run(cache_dir=cdir)
        w = lambda r: [x for x in json.loads(r)["warnings"] if "読めないコミット" in x]
        return (w(cold) == w(warm) == w(base) and len(w(base)) == 1 and s2["parsed"] == 0,
                f"warning cold {w(cold)}, warm {w(warm)}; warm parsed {s2['parsed']}")
    arm("V3d parse failure warned cold and warm", v3d)

    def v2grow():
        commit(blk([("ECO-001", "filed"), ("ECO-002", "implemented"), ("ECO-003", "filed")]), 2)
        base, _ = run()
        got, st = run(cache_dir=cdir)
        n = int(json.loads(base)["commits_read"])
        return (got == base and st["parsed"] == 1 and st["hits"] == n - 1, f"parsed {st['parsed']}, hits {st['hits']} of {n} commits")
    arm("V2 grow: one new commit parses 1", v2grow)

    def v2amend():
        before = cached_blobs()
        commit(blk([("ECO-001", "filed"), ("ECO-002", "implemented"), ("ECO-004", "filed")]), 1, amend=True)
        base, _ = run()
        got, st = run(cache_dir=cdir)
        after, hist = cached_blobs(), history_blobs()
        return (got == base and after <= hist and not before <= hist,
                f"cache blobs {len(before)} -> {len(after)}, outside history after: {len(after - hist)}; parsed {st['parsed']}")
    arm("V2 amend: no blob outside the history kept", v2amend)

    def v3a():
        base, _ = run()
        notes, ok = [], True
        for label, mangle in (("cut in half", lambda t: t[: len(t) // 2]), ("not JSON", lambda t: "this is not a cache\n")):
            p = cache_file()
            p.write_text(mangle(p.read_text(encoding="utf-8")), encoding="utf-8")
            got, st = run(cache_dir=cdir)
            reloaded, why = bj._dwell_cache_load(p, bj._dwell_cache_key())
            good = got == base and st["hits"] == 0 and st["parsed"] == len(history_blobs()) and st["read_miss"] and why is None
            ok &= good
            notes.append(f"{label}: miss {st['read_miss']!r}, parsed {st['parsed']}, rewritten loadable {why is None}")
        return ok, "; ".join(notes)
    arm("V3a corrupt cache is a miss", v3a)

    def v3b():
        run(cache_dir=cdir)
        k1, k2 = bj._dwell_cache_key(), bj2._dwell_cache_key()
        base, _ = run(bj2)
        got, st = run(bj2, cache_dir=cdir)
        return (got == base and st["read_miss"] == "version key differs" and st["hits"] == 0 and k1 != k2,
                f"keys differ {k1 != k2}; copy's run: miss {st['read_miss']!r}, hits {st['hits']}, parsed {st['parsed']}")
    arm("V3b another version key is a miss", v3b)

    def v3c():
        blocked = work / "not-a-dir"
        blocked.write_text("x", encoding="utf-8")
        base, _ = run()
        got, st = run(cache_dir=blocked)
        e = dict(os.environ, BOMDD_DWELL_CACHE_DIR=str(blocked))
        p = subprocess.run([sys.executable, "-X", "utf8", str(mods / "bj_t.py"), "--dwell", "--json"], cwd=root, env=e, capture_output=True)
        out, err = p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
        cli_ok = p.returncode == 0 and "dwell cache: write failed" in err and '"error"' not in out and '"open"' in out
        return (got == base and str(st.get("write", "ok")) != "ok" and cli_ok,
                f"in-process write={st.get('write')!r}; command line exit {p.returncode}, stderr {err.strip().splitlines()[:2]}")
    arm("V3c unwritable cache directory", v3c)

    def v3e():
        run(cache_dir=cdir)
        p = cache_file()
        data = json.loads(p.read_text(encoding="utf-8"))
        head_blob = git(root, "rev-parse", f"HEAD:{rel}")
        data["blobs"][head_blob][0]["ECO-001"][0] = "applied"     # well-formed, wrong
        p.write_text(json.dumps(data), encoding="utf-8")
        base, _ = run()
        got, st = run(cache_dir=cdir)
        believed = got != base and "ECO-001" not in [o["id"] for o in json.loads(got)["open"]]
        right = "ECO-001" in [o["id"] for o in json.loads(base)["open"]]
        return (believed and right and st["hits"] > 0,
                f"with the cache ECO-001 open: {not believed}; with no cache ECO-001 open: {right} (the limit shown, not caught)")
    arm("V3e well-formed wrong entry believed (declared limit)", v3e)

    print(f"arms {len(results)}, PASS {sum(ok for _, ok in results)}, FAIL {sum(not ok for _, ok in results)}")
    print("FAILED: " + ", ".join(n for n, ok in results if not ok) if any(not ok for _, ok in results) else "ALL PASS")


if __name__ == "__main__":
    main()
