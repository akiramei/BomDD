"""dwell.py — register の git 履歴から ECO の状態遷移と滞留日数を導出する(読み取りのみ)。

usage: python dwell.py <repo> <register-relpath> [--json OUT]
各コミットの register を読み、ECO ごとに (日時, status) の変化点を記録する。
読めなかったコミットは黙って捨てず件数と SHA を出す。
"""
import datetime as dt
import json
import subprocess
import sys

import yaml

try:
    Loader = yaml.CSafeLoader
except AttributeError:
    Loader = yaml.SafeLoader

TERMINAL = {"verified", "applied", "superseded", "rejected", "withdrawn", "cancelled", "closed"}


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout


def items_of(doc):
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict):
        for v in doc.values():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0]:
                return v
    return None


def main():
    repo, rel = sys.argv[1], sys.argv[2]
    out = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    # --status-commits: status の行を足した・消したコミットだけを読む(状態の変化はそこでしか起きない — 上位集合)
    pick = ["-G", r"^\s*status:"] if "--status-commits" in sys.argv else []
    log = git(repo, "log", "--reverse", *pick, "--format=%H %cI", "--", rel).decode().split("\n")
    commits = [l.split(" ", 1) for l in log if l.strip()]
    hist = {}      # id -> [(iso, status, sha)]
    failed = []
    for sha, iso in commits:
        try:
            doc = yaml.load(git(repo, "show", f"{sha}:{rel}"), Loader=Loader)
            its = items_of(doc)
            if its is None:
                raise ValueError("no item list")
        except Exception as e:  # noqa: BLE001
            failed.append((sha[:10], iso[:10], type(e).__name__))
            continue
        for it in its:
            if not isinstance(it, dict) or "id" not in it:
                continue
            st = str(it.get("status"))
            h = hist.setdefault(str(it["id"]), [])
            if not h or h[-1][1] != st:
                h.append((iso, st, sha[:10]))
    now = dt.datetime.now(dt.timezone.utc)
    first_iso = commits[0][1] if commits else None
    res = {"repo": repo, "register": rel, "commits": len(commits), "first_commit": first_iso,
           "failed": failed, "ecos": {}}
    for eid, h in hist.items():
        cur_iso, cur, _ = h[-1]
        since = dt.datetime.fromisoformat(cur_iso)
        res["ecos"][eid] = {
            "history": h,
            "current": cur,
            "terminal": cur in TERMINAL,
            "days_in_current": round((now - since).total_seconds() / 86400, 1),
            "censored": cur_iso == first_iso,  # 最初の観測時点から同じ状態= それより前は不明
        }
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"{repo}: commits={len(commits)} failed={len(failed)} ecos={len(hist)}")
    for f_ in failed[:10]:
        print("  failed:", *f_)


if __name__ == "__main__":
    main()
