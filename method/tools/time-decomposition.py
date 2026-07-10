#!/usr/bin/env python3
"""time-decomposition.py — セッショントランスクリプトの工数分解(観測値)

Claude Code のセッショントランスクリプト(.jsonl)から、壁時計工数を
  人間応答待ち / ツール実行 / その他の空白 + Bash カテゴリ別実働 + サブエージェント別スパン
に分解する。工数は観測値を正とする規律(transfer-02 還元 2026-07-10: 台帳の自己申告
3m45s vs 観測 1h05m の 17 倍乖離)の機械面。

usage:
  python time-decomposition.py <session.jsonl> [--gap-min 2] [--tz-hours 9]

分類ヒューリスティック(限界は出力にも明記される):
  - 空白(gap-min 分超のイベント間隔)の分類:
      HUMAN  = 直前が AskUserQuestion、または直後が user テキスト/queue-operation
      TOOL   = 直前が tool_use(コマンド実行中)
      OTHER  = それ以外(ターン境界等)
    人間待ちとバックグラウンド作業待ちが重なる区間は HUMAN 側に計上される。
  - Bash カテゴリはコマンド文字列の正規表現(git をコマンド位置で最優先判定 —
    コミットメッセージ中の 'dotnet test' 等の誤分類を避ける)。2 分超の呼び出しは
    個別に列挙されるので、分類は目視で監査すること。
"""
import argparse
import datetime
import io
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CMD_CATEGORIES = [
    ("git", re.compile(r"(?:^|&&|;|\n)\s*(?:cd\s+\"?[^&;\n\"]*\"?\s*&&\s*)?git\s")),
    ("dotnet test", re.compile(r"dotnet\s+test")),
    ("dotnet build", re.compile(r"dotnet\s+(build|restore|publish)")),
    ("dotnet run/ef", re.compile(r"dotnet\s+(run|ef)")),
    ("oracle/probe", re.compile(r"oracle", re.I)),
]


def categorize(cmd):
    for name, pat in CMD_CATEGORIES:
        if pat.search(cmd):
            return name
    return "other"


def load_events(path):
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = o.get("timestamp")
            if not ts:
                continue
            t = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            events.append((t, o))
    events.sort(key=lambda e: e[0])
    return events


def describe(o):
    typ = o.get("type", "?")
    c = (o.get("message") or {}).get("content")
    if isinstance(c, list):
        for x in c:
            if x.get("type") == "tool_use":
                return "tool_use", x.get("name", "?"), x.get("input", {})
            if x.get("type") == "tool_result":
                return "tool_result", None, None
            if x.get("type") == "text":
                return "text", None, None
    elif isinstance(c, str):
        return "text", None, None
    return typ, None, None


def bash_calls(events):
    pending, calls = {}, []
    for t, o in events:
        c = (o.get("message") or {}).get("content")
        if not isinstance(c, list):
            continue
        for x in c:
            if x.get("type") == "tool_use" and x.get("name") == "Bash":
                inp = x.get("input", {})
                pending[x["id"]] = (t, inp.get("command", ""), inp.get("description", ""))
            if x.get("type") == "tool_result" and x.get("tool_use_id") in pending:
                t0, cmd, desc = pending.pop(x["tool_use_id"])
                calls.append((t0, t - t0, cmd, desc))
    return calls


def fmt(td):
    return str(td).split(".")[0]


def analyze_session(path, gap_min, tz):
    events = load_events(path)
    if not events:
        print(f"no timestamped events in {path}")
        return
    span = events[-1][0] - events[0][0]
    print(f"=== {os.path.basename(path)} ===")
    print(f"span: {events[0][0].astimezone(tz)} -> {events[-1][0].astimezone(tz)}  ({fmt(span)})")

    totals = defaultdict(datetime.timedelta)
    print(f"\n--- gaps > {gap_min}min ---")
    for i in range(1, len(events)):
        gap = events[i][0] - events[i - 1][0]
        if gap < datetime.timedelta(minutes=gap_min):
            continue
        pk, pn, _ = describe(events[i - 1][1])
        ck, _, _ = describe(events[i][1])
        curtype = events[i][1].get("type")
        if (pk == "tool_use" and pn == "AskUserQuestion") or (
            curtype in ("user", "queue-operation") and ck in ("text", "queue-operation")
        ):
            cat = "HUMAN"
        elif pk == "tool_use":
            cat = "TOOL"
        else:
            cat = "OTHER"
        totals[cat] += gap
        print(f"{events[i-1][0].astimezone(tz).strftime('%H:%M:%S')} +{fmt(gap)} {cat:5} after {pk}:{pn or ''}")
    print("\ngap totals: " + "  ".join(f"{k}={fmt(v)}" for k, v in sorted(totals.items())))

    calls = bash_calls(events)
    agg = defaultdict(lambda: [0, datetime.timedelta()])
    for t0, dur, cmd, desc in calls:
        k = categorize(cmd)
        agg[k][0] += 1
        agg[k][1] += dur
    print("\n--- bash by category ---")
    for k, (n, tot) in sorted(agg.items(), key=lambda kv: -kv[1][1]):
        print(f"{k:14} n={n:4} total={fmt(tot)}")
    print(f"\n--- bash calls > {gap_min}min (分類の目視監査用) ---")
    for t0, dur, cmd, desc in sorted(calls):
        if dur >= datetime.timedelta(minutes=gap_min):
            print(f"{t0.astimezone(tz).strftime('%H:%M:%S')} {fmt(dur)} [{categorize(cmd)}] {desc or cmd[:80]}")


def analyze_subagents(session_path, gap_min, tz):
    subdir = os.path.join(
        os.path.dirname(session_path),
        os.path.splitext(os.path.basename(session_path))[0],
        "subagents",
    )
    if not os.path.isdir(subdir):
        return
    print(f"\n=== subagents ({subdir}) ===")
    print(f"{'agent':20} {'start':>5} {'span':>9} {'bash':>9} {'dotnet test':>14}")
    grand = defaultdict(lambda: [0, datetime.timedelta()])
    for fn in sorted(os.listdir(subdir)):
        if not fn.endswith(".jsonl"):
            continue
        events = load_events(os.path.join(subdir, fn))
        if not events:
            continue
        span = events[-1][0] - events[0][0]
        calls = bash_calls(events)
        bash_tot = sum((d for _, d, _, _ in calls), datetime.timedelta())
        tn, tt = 0, datetime.timedelta()
        for _, dur, cmd, _ in calls:
            k = categorize(cmd)
            grand[k][0] += 1
            grand[k][1] += dur
            if k == "dotnet test":
                tn += 1
                tt += dur
        name = fn.replace("agent-", "").replace(".jsonl", "")[:18]
        start = events[0][0].astimezone(tz).strftime("%H:%M")
        print(f"{name:20} {start:>5} {fmt(span):>9} {fmt(bash_tot):>9} {tn:4} / {fmt(tt):>8}")
    print("\nsubagent bash grand totals: " + "  ".join(
        f"{k}={fmt(v[1])}(n={v[0]})" for k, v in sorted(grand.items(), key=lambda kv: -kv[1][1])
    ))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session", help="セッショントランスクリプト .jsonl のパス")
    ap.add_argument("--gap-min", type=float, default=2.0, help="空白と数える最小間隔(分)")
    ap.add_argument("--tz-hours", type=float, default=9.0, help="表示タイムゾーン(UTC からの時間)")
    args = ap.parse_args()
    tz = datetime.timezone(datetime.timedelta(hours=args.tz_hours))
    analyze_session(args.session, args.gap_min, tz)
    analyze_subagents(args.session, args.gap_min, tz)
    print("\n注意: HUMAN/TOOL 分類はヒューリスティック(人間待ちと背景作業待ちの重なりは HUMAN 計上)。")
    print("工数を記録へ転記する際は観測値を正とし、自己申告値には来歴(self-reported)を明記すること。")


if __name__ == "__main__":
    main()
