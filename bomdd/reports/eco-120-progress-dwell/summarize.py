"""summarize.py — dwell.py の JSON を製品ごとにまとめる。usage: python summarize.py a.json b.json ..."""
import datetime as dt
import json
import statistics
import sys

BUCKETS = [(7, "<=7d"), (30, "8-30d"), (90, "31-90d"), (10**9, ">90d")]


def bucket(d):
    for lim, name in BUCKETS:
        if d <= lim:
            return name


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]


for path in sys.argv[1:]:
    d = json.load(open(path, encoding="utf-8"))
    name = d["repo"].rstrip("/").split("/")[-1]
    ecos = d["ecos"]
    print(f"\n== {name}  (register commits {d['commits']}, first {d['first_commit'][:10]}, parse failures {len(d['failed'])})")
    open_ = {k: v for k, v in ecos.items() if not v["terminal"]}
    print(f"  ECO {len(ecos)} / open {len(open_)}")
    table = {}
    for v in open_.values():
        table.setdefault(v["current"], {}).setdefault(bucket(v["days_in_current"]), 0)
        table[v["current"]][bucket(v["days_in_current"])] += 1
    for st, b in sorted(table.items()):
        cens = sum(1 for v in open_.values() if v["current"] == st and v["censored"])
        print(f"  {st:12s} " + "  ".join(f"{n}:{b.get(n, 0)}" for _, n in BUCKETS) + (f"  (censored {cens})" if cens else ""))
    # 状態ごとの過去の滞留(次の状態へ移るまで)— 閉じた区間だけ
    spans = {}
    for v in ecos.values():
        h = v["history"]
        for (a_iso, a_st, _), (b_iso, _, _) in zip(h, h[1:]):
            days = (dt.datetime.fromisoformat(b_iso) - dt.datetime.fromisoformat(a_iso)).total_seconds() / 86400
            spans.setdefault(a_st, []).append(days)
    for st, xs in sorted(spans.items()):
        print(f"  past dwell in {st:12s} n={len(xs):3d} median={statistics.median(xs):6.1f}d p90={pct(xs, .9):6.1f}d max={max(xs):6.1f}d")
    oldest = sorted(open_.items(), key=lambda kv: -kv[1]["days_in_current"])[:8]
    for k, v in oldest:
        print(f"    {k:14s} {v['current']:12s} {v['days_in_current']:6.1f}d since {v['history'][-1][0][:10]}{' (censored)' if v['censored'] else ''}")
