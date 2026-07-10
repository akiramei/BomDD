# impact-retrospective — 影響分析の遡及採点(標準健診・リポ非依存版)
#
# ECO 台帳を持つリポで「宣言影響集合 vs 実 diff」を全 ECO 一括採点し、
# under/over-inclusion とハブ unit(under 実績の集中先)を機械的に発見する。
# 初出: scale-01(ViewPrism2 遡及測定・2026-07-04 — 61 §1.4 ハブ台帳の根拠測定)。
# 原型: ViewPrism2/bomdd/studies/scale01-jig.py(リポ固定版)。
#
# 使い方:
#   python impact-retrospective.py --repo <path> [--impact-field impacted_bom|affected_refs]
#     [--register bomdd/60-change-register.yaml] [--mbom bomdd/32-mbom.yaml] [--test-unit <unit-id>]
#
# 採点規約 v1(scale-01 で凍結):
#  1. 対象 = 影響宣言フィールドを持ち status∈{implemented,applied,verified} かつ件名対応コミット≥1 の ECO。
#     件名(%s)に ECO id を含むコミットのみ対応付け(本文言及は履歴註の誤帰属リスクがあるため不使用)。
#  2. 予測 unit: 宣言要素から E-/M- ID を抽出し、M- は直接・E- は M-BOM ebom_refs 逆引きで unit へ。
#     CP-/K-/spec/散文はファイル写像外(nonfile としてカウントのみ)。
#  3. 実 diff: 対応コミットの union。bomdd/**・*.md 除外(台帳改訂は常時許容= R-052 規約の遡及適用)。
#  4. unit 帰属 = artifact.path の最長前方一致。--test-unit 指定 unit への under は
#     test-only(63 分類の「記録のみ」)として分離集計(違反でない)。
#  5. 出力: ECO 別 under/over+ハブ集中度(under 実績 unit の出現 ECO 数)。
#
# 採点規約 v2(harness ECO-003・2026-07-10 外部レビュー所見3 — 集計の fail-closed 化。
# v1 の測定定義 1〜4 は不変・変えたのは見出し集計と欠測の扱いのみ。v1 数値は summary.decomposition で再現可能):
#  6. unit へ写像できない実変更ファイル(unmapped)は fail-closed の under として
#     見出し(ecos_with_real_under / real_under_files)に含める。v1 では独立カウンタで
#     「未知の変更先があるのに under 0」の見出しが成立し得た(BomDD-Plm ECO-003 で実在を確認)。
#     hub_concentration は unit 帰属が定義できる mapped under のみ(unmapped に unit はない)。
#  7. 影響宣言フィールドは register 一括でなく ECO ごとに判定(impacted_bom → affected_refs の順。
#     --impact-field 指定時はそのフィールドのみ)。混在 register で片方が黙って欠測になる穴を閉じる。
#  8. git 失敗・register/M-BOM の読取り失敗は exit 2「測定不能」で停止(ECO-002 と同族の fail-open 是正)。
#
# 【語彙分岐の候補記録(形式化しない — rule of three 待ち)】
#   影響宣言フィールドは実リポで分岐している: ViewPrism2 = impacted_bom(散文混じりリスト)/
#   BomDD-Plm = affected_refs(ID リスト・R-051 検査対象)。第3の register が現れた時点で
#   ref-v0.9 候補(register 影響宣言の標準形)として裁定する。それまで本ツールは両対応。

import argparse, json, re, subprocess, sys
from collections import Counter, defaultdict

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    sys.exit("PyYAML が必要です: pip install pyyaml")


def die(msg):
    print(f"[impact-retrospective] 測定不能: {msg}", file=sys.stderr)
    sys.exit(2)


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo] + list(args),
                       capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        err = (p.stderr or "").strip().splitlines()
        die(f"git {args[0]} が失敗 (exit {p.returncode}): {err[0] if err else '(stderr なし)'}")
    return p.stdout


def find_units(node):
    """32-mbom 内の manufacturing_units をキー名で再帰探索(リポ間のネスト差を吸収)"""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "manufacturing_units" and isinstance(v, list):
                return v
            r = find_units(v)
            if r is not None:
                return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--register", default="bomdd/60-change-register.yaml")
    ap.add_argument("--mbom", default="bomdd/32-mbom.yaml")
    ap.add_argument("--impact-field", default=None,
                    help="未指定なら impacted_bom → affected_refs の順に自動検出")
    ap.add_argument("--test-unit", action="append", default=[],
                    help="test-only(記録のみ)として分離する unit id(複数可)")
    ap.add_argument("--changes-key", default=None, help="register 内の ECO リストキー(既定: changes)")
    a = ap.parse_args()

    try:
        mbom = yaml.safe_load(open(f"{a.repo}/{a.mbom}", encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        die(f"M-BOM の読取りに失敗: {e}")
    units = find_units(mbom) or []
    if not units:
        die(f"manufacturing_units が {a.mbom} に見つからない")
    unit_path, e2units = {}, defaultdict(set)
    for u in units:
        art = u.get("artifact")
        p = (art.get("path") if isinstance(art, dict) else art) or ""
        unit_path[u["id"]] = p.replace("\\", "/")
        for e in u.get("ebom_refs", []):
            e2units[e].add(u["id"])

    def attribute(f):
        best, blen = None, -1
        for uid, p in unit_path.items():
            if p and (f == p or f.startswith(p.rstrip("/") + "/")) and len(p) > blen:
                best, blen = uid, len(p)
        return best

    try:
        reg = yaml.safe_load(open(f"{a.repo}/{a.register}", encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        die(f"register の読取りに失敗: {e}")
    changes = reg.get(a.changes_key) if a.changes_key else (reg.get("changes") or reg.get("change_orders"))
    if changes is None:
        die("register の ECO リストキーが見つからない(--changes-key で指定)")

    def impact_decl(c):
        """影響宣言を ECO ごとに判定(規約 v2 #7 — register 一括判定は混在時に片方が黙って欠測)"""
        if a.impact_field:
            return c.get(a.impact_field), a.impact_field
        for f in ("impacted_bom", "affected_refs"):
            if c.get(f):
                return c[f], f
        return None, None

    log = git(a.repo, "log", "--format=%H\t%s")
    eco_commits = defaultdict(list)
    for line in log.strip().split("\n"):
        h, s = line.split("\t", 1)
        for m in set(re.findall(r"ECO-\d{3}", s)):
            eco_commits[m].append(h)

    rows, skipped = [], Counter()
    hub = Counter()
    fields_used = Counter()
    for c in changes:
        eid = c["id"]
        ib, field = impact_decl(c)
        status = (str(c.get("status") or "")).split()[0]
        if not ib:
            skipped["no_impact_decl"] += 1; continue
        if status not in ("implemented", "applied", "verified"):
            skipped["not_applied"] += 1; continue
        commits = eco_commits.get(eid, [])
        if not commits:
            skipped["no_commits"] += 1; continue

        pred = set()
        nonfile = 0
        for x in ib:
            ids = re.findall(r"\b([EM]-[A-Z0-9-]+)\b", str(x))
            mapped = False
            for i in ids:
                if i in unit_path: pred.add(i); mapped = True
                elif i in e2units: pred.update(e2units[i]); mapped = True
            if not mapped: nonfile += 1

        actual = set()
        for h in commits:
            for f in git(a.repo, "show", "--name-only", "--format=", h).strip().split("\n"):
                f = f.strip()
                if not f or f.startswith("bomdd/") or f.endswith(".md"): continue
                if "/obj/" in f or "/bin/" in f: continue
                actual.add(f)
        if not actual:
            skipped["doc_only"] += 1; continue

        actual_units = Counter()
        under, test_only, unmapped_files = [], 0, []
        for f in sorted(actual):
            uid = attribute(f)
            if uid: actual_units[uid] += 1
            if uid in pred: continue
            if uid in a.test_unit: test_only += 1
            elif uid is None: unmapped_files.append(f)
            else: under.append((f, uid)); hub[uid] += 1
        over = sorted(u for u in pred if u not in actual_units)
        fields_used[field] += 1
        rows.append({"eco": eid, "field": field, "commits": len(commits), "files": len(actual),
                     "pred_units": sorted(pred), "actual_units": sorted(actual_units),
                     "under": under, "test_only": test_only,
                     "unmapped": len(unmapped_files), "unmapped_files": unmapped_files,
                     "over": over})

    # 規約 v2 #6: 見出しは fail-closed(mapped under + unmapped)。v1 数値は decomposition で再現。
    mapped_under_ecos = [r["eco"] for r in rows if r["under"]]
    unmapped_ecos = [r["eco"] for r in rows if r["unmapped"]]
    fail_closed_ecos = [r["eco"] for r in rows if r["under"] or r["unmapped"]]
    print(json.dumps({
        "fields_used": dict(fields_used), "scored": rows, "skipped": dict(skipped),
        "summary": {
            "code_ecos": len(rows),
            "ecos_with_real_under": len(fail_closed_ecos),
            "real_under_files": sum(len(r["under"]) + r["unmapped"] for r in rows),
            "decomposition": {
                "ecos_with_mapped_under": len(mapped_under_ecos),
                "mapped_under_files": sum(len(r["under"]) for r in rows),
                "ecos_with_unmapped": len(unmapped_ecos),
                "unmapped_files": sum(r["unmapped"] for r in rows),
            },
            "hub_concentration": dict(hub.most_common()),
            "multi_unit_ecos": sum(1 for r in rows if len(r["actual_units"]) >= 2),
        }}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
