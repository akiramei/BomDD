# stage0-survey — 宣言なしリポの変更トポロジー健診(stage-0・リポ非依存版)
#
# ECO 台帳・影響宣言を持たないリポに対し、git 履歴だけから
# 「BomDD 導入判断の材料」(跨ぎ率・ハブ集中・fix 潜伏・三冠・revert 連鎖)を測定する。
# 初出: ViewGrid stage-0(2026-07-07・scratch 治具)。本ツールはその一般化
# (定義の凍結原型= ViewGrid bomdd/52-metrics.yaml stage0_topology_health_check)。
# 事前登録プロトコル: BomDD loops/stage0-oss-01/protocol.md §2(測定定義)。
#
# 使い方:
#   python stage0-survey.py --repo <path> [--unit-depth 2] [--strip-prefixes src]
#     [--bulk-threshold 50] [--top 10] [--json out.json] [--max-commits 0]
#
# 測定規約(protocol §2 で凍結。変更する場合は fork して宣言):
#  1. マージコミットは除外(--no-merges)。bulk コミット(touched > threshold)は
#     機械的掃引として分離集計し、跨ぎ率は bulk 除外/込みの両建てで報告する。
#  2. 仮 unit = 除外・prefix 剥がし後のパス先頭 depth 階層(ルート直下ファイルは "<root>")。
#     仮 unit は M-BOM 裁定を経た境界ではない(健診の初期値)。
#  3. 分類は件名の凍結正規表現(revert > fix > feat > other の優先順)。
#  4. fix 潜伏 = (fix,file) 対ごとの「同一ファイルへの直近 feat からのコミット距離」
#     (時間でなく解析対象コミット列上の距離。feat 前歴のない対は集計外)。
#  5. churn はタッチ回数(行 churn は blob:none クローンで取得不能のため定義から除外)。
#  6. サイズは HEAD 実体の行数(バイナリはスキップ)。
#
# 血統: impact-retrospective.py(宣言 vs 実 diff の遡及採点)の下位形 —
#       影響宣言が存在しないリポで、宣言回収の見込みとハブ台帳初期値を出す。

import argparse, json, math, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

RE_REVERT = re.compile(r'(?i)\brevert|差し戻')
RE_FIX    = re.compile(r'(?i)\b(fix|fixes|fixed|bugfix|hotfix)\b|^bug\b|修正|不具合|バグ', re.I)
RE_FEAT   = re.compile(r'(?i)^(feat|feature|add|added|implement|introduce|new|create)\b|^feat[(!:]|追加|実装|新規')
RE_EXCLUDE = re.compile(
    r'(?i)(^|/)(vendor|vendors|node_modules|third[_-]?party|external|generated|dist|build)/'
    r'|(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|go\.sum|Cargo\.lock|poetry\.lock|uv\.lock|composer\.lock)$'
    r'|\.(min\.js|min\.css|svg|png|jpg|jpeg|gif|ico|webp|woff2?|ttf|eot|pdf|zip|gz|bin|dll|exe|snap)$'
    r'|(^|/)__snapshots__/')


def classify(subject):
    if RE_REVERT.search(subject):
        return "revert"
    if RE_FIX.search(subject):
        return "fix"
    if RE_FEAT.search(subject):
        return "feat"
    return "other"


def unit_of(path, depth, strips):
    parts = path.split("/")
    while len(parts) > 1 and parts[0] in strips:
        parts = parts[1:]
    if len(parts) <= 1:
        return "<root>"
    return "/".join(parts[:depth])


def iter_commits(repo, max_commits):
    args = ["git", "-C", repo, "log", "--no-merges", "--reverse",
            "--pretty=format:\x01%H\x02%s", "--name-only"]
    if max_commits:
        args.insert(4, f"-{max_commits}")
    out = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                         errors="replace").stdout
    for block in out.split("\x01"):
        if not block.strip():
            continue
        head, _, rest = block.partition("\x02")
        subject, _, files_blob = rest.partition("\n")
        files = [f.strip() for f in files_blob.strip().splitlines() if f.strip()]
        yield head.strip(), subject.strip(), files


def head_sizes(repo, paths):
    sizes = {}
    for p in paths:
        f = Path(repo) / p
        try:
            data = f.read_bytes()
            if b"\0" in data[:8192]:
                continue
            sizes[p] = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
        except OSError:
            continue
    return sizes


def tracked_files(repo):
    # ls-files でなく ls-tree(HEAD)を使う — partial clone 等で index が空でも
    # 追跡集合を正しく返す(index 健全時は同一結果。stage0-oss-01 較正で実測)
    out = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "HEAD", "--name-only"],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace").stdout
    return [p for p in out.splitlines() if p and not RE_EXCLUDE.search(p)]


def total_loc(repo, files):
    loc = 0
    counted = 0
    for p in files:
        f = Path(repo) / p
        try:
            data = f.read_bytes()
        except OSError:
            continue
        if b"\0" in data[:8192]:
            continue
        loc += data.count(b"\n")
        counted += 1
    return loc, counted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--unit-depth", type=int, default=2)
    ap.add_argument("--strip-prefixes", default="src")
    ap.add_argument("--bulk-threshold", type=int, default=50)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--max-commits", type=int, default=0, help="0=全履歴")
    ap.add_argument("--unit-scope", default=None,
                    help="unit 集計をこのプレフィックス配下のファイルに限定(カンマ区切り。較正=原型治具の src 限定を再現する用)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--skip-loc", action="store_true")
    a = ap.parse_args()
    strips = set(a.strip_prefixes.split(","))

    head_sha = subprocess.run(["git", "-C", a.repo, "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()

    n = {"total": 0, "bulk": 0}
    kinds = Counter()
    touch = Counter()           # file -> touches(bulk除外)
    fix_touch = Counter()       # file -> fix touches
    unit_touch = Counter()
    multi = {"all": 0, "eligible": 0, "all_incl_bulk": 0, "eligible_incl_bulk": 0,
             "fix_multi": 0, "fix_eligible": 0}
    unit_in_multi = Counter()
    pair_count = Counter()
    last_feat_idx = {}          # file -> 直近 feat の通し番号
    latencies = []
    revert_subjects = []
    idx = 0

    scope = a.unit_scope.split(",") if a.unit_scope else None
    for _sha, subject, files in iter_commits(a.repo, a.max_commits):
        files = [f for f in files if not RE_EXCLUDE.search(f)]
        if not files:
            continue
        idx += 1
        n["total"] += 1
        kind = classify(subject)
        kinds[kind] += 1
        if kind == "revert":
            revert_subjects.append(subject)
        unit_files = files if scope is None else [
            f for f in files if any(f.startswith(s + "/") or f.startswith(s) for s in scope)]
        units = sorted({unit_of(f, a.unit_depth, strips) for f in unit_files})
        is_bulk = len(files) > a.bulk_threshold
        # 跨ぎ率(bulk 込み)
        multi["eligible_incl_bulk"] += 1
        if len(units) >= 2:
            multi["all_incl_bulk"] += 1
        if is_bulk:
            n["bulk"] += 1
            continue  # 以降の主集計から bulk を除外
        multi["eligible"] += 1
        if len(units) >= 2:
            multi["all"] += 1
            for u in units:
                unit_in_multi[u] += 1
            for i in range(len(units)):
                for j in range(i + 1, len(units)):
                    pair_count[(units[i], units[j])] += 1
        if kind == "fix":
            multi["fix_eligible"] += 1
            if len(units) >= 2:
                multi["fix_multi"] += 1
        for f in files:
            touch[f] += 1
            unit_touch[unit_of(f, a.unit_depth, strips)] += 1
            if kind == "fix":
                fix_touch[f] += 1
                if f in last_feat_idx:
                    latencies.append(idx - last_feat_idx[f])
            if kind == "feat":
                last_feat_idx[f] = idx

    files_at_head = tracked_files(a.repo)
    if a.skip_loc:
        loc, counted = None, len(files_at_head)
    else:
        loc, counted = total_loc(a.repo, files_at_head)

    # H1: top-1% share(fix-touch)
    k = max(1, math.ceil(0.01 * len(files_at_head)))
    fix_sorted = fix_touch.most_common()
    total_fix_touches = sum(fix_touch.values())
    top1p_share = (sum(c for _, c in fix_sorted[:k]) / total_fix_touches
                   if total_fix_touches else None)

    # H2: 三冠(churn top / fix top / size top の重なり)
    top_churn = [f for f, _ in touch.most_common(a.top)]
    top_fix = [f for f, _ in fix_sorted[:a.top]]
    sizes = head_sizes(a.repo, set(top_churn) | set(top_fix) | set(
        f for f, _ in touch.most_common(200)))
    top_size = [f for f, _ in sorted(sizes.items(), key=lambda x: -x[1])[:a.top]]
    triple = sorted(set(top_churn) & set(top_fix) & set(top_size))
    churn_fix_overlap = sorted(set(top_churn) & set(top_fix))

    lat_sorted = sorted(latencies)
    def pctl(p):
        return lat_sorted[min(len(lat_sorted) - 1, int(p * len(lat_sorted)))] if lat_sorted else None

    result = {
        "repo": a.repo, "head": head_sha,
        "params": {"unit_depth": a.unit_depth, "strip": sorted(strips),
                   "bulk_threshold": a.bulk_threshold},
        "population": {"commits_analyzed": n["total"], "bulk_commits": n["bulk"],
                       "kinds": dict(kinds),
                       "fix_rate": round(kinds["fix"] / n["total"], 3) if n["total"] else None},
        "size": {"tracked_files": len(files_at_head), "text_files": counted, "loc": loc},
        "multi_unit": {
            "rate_excl_bulk": round(multi["all"] / multi["eligible"], 3) if multi["eligible"] else None,
            "rate_incl_bulk": round(multi["all_incl_bulk"] / multi["eligible_incl_bulk"], 3) if multi["eligible_incl_bulk"] else None,
            "fix_rate": round(multi["fix_multi"] / multi["fix_eligible"], 3) if multi["fix_eligible"] else None,
            "top_units_in_multi": unit_in_multi.most_common(a.top),
            "top_pairs": [["%s <-> %s" % p, c] for p, c in pair_count.most_common(a.top)],
        },
        "hubs": {
            "top_churn_files": touch.most_common(a.top),
            "top_fix_files": fix_sorted[:a.top],
            "fix_top1pct": {"k_files": k, "share": round(top1p_share, 3) if top1p_share is not None else None,
                            "total_fix_touches": total_fix_touches},
            "top_size_files": [[f, sizes[f]] for f in top_size],
            "triple_crown": triple,
            "churn_fix_overlap_top": churn_fix_overlap,
        },
        "fix_latency": {
            "pairs": len(latencies), "p50": pctl(0.50), "p90": pctl(0.90),
            "immediate_le3": sum(1 for x in latencies if x <= 3),
            "late_gt20": sum(1 for x in latencies if x > 20),
            "late_ratio": round(sum(1 for x in latencies if x > 20) / len(latencies), 3) if latencies else None,
        },
        "reverts": {"count": kinds["revert"],
                    "revert_of_revert": sum(1 for s in revert_subjects if re.search(r'(?i)revert.*revert', s))},
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if a.json:
        Path(a.json).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
