"""M-BOM / CP 再設計の基準計数(読み取りのみ)。定義は preregistration.md(実行前に固定)。"""
import os, re, sys, statistics, subprocess, collections
import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\akira\source\repos"
REPOS = [("ViewPrism2", "主"), ("ViewTube", "主"), ("BomDD-Plm", "ツール"), ("TimetableAdv", "ゲーム"),
         ("BomDD-LibraryLending-Sample", "サンプル"), ("BomDD-Transfer03", "サンプル"),
         ("BomDD-UnitConv-Sample", "サンプル")]
INV_ANY = re.compile(r"\bINV-\d{3}\b")
INV_DEF = re.compile(r"^\|\s*(INV-\d{3})\s*\|", re.M)
M_ID = re.compile(r"\bM-[A-Z0-9][A-Z0-9-]*\d\b")
CP_ID = re.compile(r"\bCP-[A-Z0-9][A-Z0-9-]*\d\b")
WHEN_KEY = re.compile(r"gate|station|sampling|when|frequency", re.I)
REACT_KEY = re.compile(r"stop_condition|reaction|on_fail|on_red", re.I)
UNREADABLE = "読めない"


def load(repo, name):
    p = os.path.join(ROOT, repo, "bomdd", name)
    if not os.path.isfile(p):
        return None, "なし"
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f), "ok"
    except Exception as e:
        return None, f"{UNREADABLE}({type(e).__name__})"


def dig(d, path):
    for k in path.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def rows_of(v):
    """invariants などを行の文字列リストへ。dict の行は 'id: text' 形に。"""
    out = []
    for x in as_list(v):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            out.append(" ".join(f"{k}: {val}" for k, val in x.items()))
        else:
            out.append(str(x))
    return out


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def head(repo):
    try:
        h = subprocess.run(["git", "-C", os.path.join(ROOT, repo), "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", os.path.join(ROOT, repo), "status", "--porcelain"],
                               capture_output=True, text=True).stdout
        n = len([l for l in dirty.splitlines() if l.strip()])
        return h or "(git なし)", ("clean" if n == 0 else f"dirty({n})") if h else "-"
    except Exception:
        return "(git なし)", "-"


def ref_count(u):
    n = len(as_list(u.get("ebom_refs"))) + len(as_list(u.get("kbom_refs"))) + len(as_list(u.get("depends_on")))
    ic = u.get("interface_contract")
    if isinstance(ic, dict):
        n += len(ic)
    elif isinstance(ic, list):
        n += len(ic)
    elif ic:
        n += 1
    return n


res = {}
for repo, kind in REPOS:
    r = {"kind": kind}
    r["head"], r["tree"] = head(repo)
    e, r["e_state"] = load(repo, "30-ebom.yaml")
    m, r["m_state"] = load(repo, "32-mbom.yaml")
    c, r["c_state"] = load(repo, "33-control-plan.yaml")
    rt, r["rt_state"] = load(repo, "34-routing.yaml")
    units = [u for u in as_list(dig(m, "mbom.manufacturing_units")) if isinstance(u, dict)] if m else []
    eitems = {i.get("id"): i for i in as_list(dig(e, "ebom.items")) if isinstance(i, dict)} if e else {}
    cps = [x for x in as_list(dig(c, "control_plan.characteristics")) if isinstance(x, dict)] if c else []
    r["n_units"], r["n_cp"] = len(units), len(cps)

    # M1
    cls = collections.Counter()
    copies = 0
    units_with_inv = 0
    for u in units:
        rows = rows_of(u.get("invariants"))
        if rows:
            units_with_inv += 1
        e_rows = set()
        for er in as_list(u.get("ebom_refs")):
            if isinstance(er, str) and er in eitems:
                e_rows |= {norm(x) for x in rows_of(eitems[er].get("invariants"))}
        for row in rows:
            s = norm(row)
            if re.fullmatch(r"(id: )?INV-\d{3}[.。]?", s):
                cls["参照のみ"] += 1
                continue  # 本文が無い行は写しの判定対象外(事前登録「本文が完全一致」)
            elif INV_ANY.search(s):
                cls["ID+本文"] += 1
            else:
                cls["本文のみ"] += 1
            if e_rows and s in e_rows:
                copies += 1
    r["m1"] = {"units_with_inv": units_with_inv, "cls": dict(cls), "copies": copies,
               "e_checked": r["e_state"] == "ok",
               "display_contract_units": sum(1 for u in units if u.get("display_contract"))}

    # M2
    f32 = len(as_list(m.get("fmea"))) if isinstance(m, dict) else None
    f33 = len(as_list(dig(c, "control_plan.fmea"))) if isinstance(c, dict) else None
    r["m2"] = (f32, f33)

    # M3
    when_rows = sum(1 for x in cps if any(WHEN_KEY.search(k) for k in x))
    react_rows = sum(1 for x in cps if any(REACT_KEY.search(k) for k in x))
    when_keys = sorted({k for x in cps for k in x if WHEN_KEY.search(k)})
    react_keys = sorted({k for x in cps for k in x if REACT_KEY.search(k)})
    alt = []
    if isinstance(c, dict):
        for k in c.get("control_plan", {}) or {}:
            if WHEN_KEY.search(k):
                alt.append(f"33:{k}({len(as_list(c['control_plan'][k]))})")
    if isinstance(rt, dict):
        def walk(d, p=""):
            if isinstance(d, dict):
                for k, v in d.items():
                    if WHEN_KEY.search(k) or k in ("hold_points",):
                        alt.append(f"34:{p}{k}")
                    walk(v, f"{p}{k}.")
            elif isinstance(d, list):
                for x in d:
                    walk(x, p)
        walk(rt)
    alt = sorted(collections.Counter(alt).items())
    r["m3"] = {"when_rows": when_rows, "react_rows": react_rows, "when_keys": when_keys,
               "react_keys": react_keys, "alt": alt}

    # 結びつき(M4/M6 共通)
    tie = collections.defaultdict(set)  # CP id -> M ids
    cp_ids = [x.get("id") for x in cps]
    for x in cps:
        for v in as_list(x.get("verifies")):
            for mid in M_ID.findall(str(v)):
                tie[x.get("id")].add(mid)
    for u in units:
        for cid in CP_ID.findall(str(u.get("acceptance_refs"))):
            tie[cid].add(u.get("id"))

    def layer(cid):
        n = len(tie.get(cid, ()))
        return "要求直結(0)" if n == 0 else ("単位(1)" if n == 1 else "またぐ(2+)")
    r["cp_layers"] = dict(collections.Counter(layer(i) for i in cp_ids)) if cps else None
    # 事後の感度確認(事前登録外): 治具・オラクル・fixture の unit を除いた「またぐ」
    jig = {u.get("id") for u in units if re.search(r"HARNESS|ORACLE|FIXTURE", str(u.get("id")))}
    r["cross_ex_jig"] = sum(1 for i in cp_ids if len(tie.get(i, set()) - jig) >= 2) if cps else None

    # M4
    spec_p = os.path.join(ROOT, repo, "bomdd", "20-spec.md")
    inv = set()
    if os.path.isfile(spec_p):
        with open(spec_p, encoding="utf-8", errors="replace") as f:
            inv = set(INV_DEF.findall(f.read()))
    if inv and cps:
        reach = collections.Counter()
        for i in sorted(inv):
            layers = {layer(x.get("id")) for x in cps if i in INV_ANY.findall(str(x))}
            if not layers:
                reach["届かない"] += 1
            for L in layers:
                reach[L] += 1
        r["m4"] = (len(inv), dict(reach))
    else:
        r["m4"] = (len(inv), "INV 定義なし" if not inv else f"CP {r['c_state']}")

    # M5
    rc = [(ref_count(u), u.get("id")) for u in units]
    if rc:
        r["m5"] = (statistics.median([x for x, _ in rc]), max(rc))
    else:
        r["m5"] = None

    # M6
    unit_ids = {u.get("id") for u in units}
    edges = set()
    for u in units:
        for d in as_list(u.get("depends_on")):
            for mid in M_ID.findall(str(d)):
                if mid in unit_ids and mid != u.get("id"):
                    edges.add((u.get("id"), mid))
    r["dep_units"] = sum(1 for u in units if u.get("depends_on"))
    if not cps:
        r["m6"] = (len(edges), f"CP {r['c_state']}")
    elif r["dep_units"] == 0:
        r["m6"] = (len(edges), "測定不能(M unit に depends_on の欄が無い)")
    else:
        covered = sum(1 for a, b in edges if any(a in s and b in s for s in tie.values()))
        r["m6"] = (len(edges), covered)
    res[repo] = r

# ---- 出力 ----
P = print
P("# M-BOM / CP 再設計 — 基準計数(2026-10-01)\n")
P("定義と読み方は preregistration.md(実行前に固定)。字面と YAML 構造のみ。届く ≠ 検査されている。\n")
P("| リポ | 区分 | HEAD | 作業木 | 30 | 32 | 33 | 34 | M unit | CP 行 |")
P("|---|---|---|---|---|---|---|---|---|---|")
for repo, r in res.items():
    P(f"| {repo} | {r['kind']} | {r['head']} | {r['tree']} | {r['e_state']} | {r['m_state']} | {r['c_state']} | {r['rt_state']} | {r['n_units']} | {r['n_cp']} |")

P("\n## M1 M-BOM が設計の中身を持つか\n")
P("| リポ | invariants を持つ unit | 参照のみ | ID+本文 | 本文のみ | E 品目と完全一致(写し) | display_contract を持つ unit |")
P("|---|---|---|---|---|---|---|")
for repo, r in res.items():
    x = r["m1"]
    cp = str(x["copies"]) if x["e_checked"] else f"測定不能(30 {r['e_state']})"
    P(f"| {repo} | {x['units_with_inv']}/{r['n_units']} | {x['cls'].get('参照のみ', 0)} | {x['cls'].get('ID+本文', 0)} | {x['cls'].get('本文のみ', 0)} | {cp} | {x['display_contract_units']} |")

P("\n## M2 FMEA の置き場所\n")
P("| リポ | 32 の fmea | 33 の control_plan.fmea |")
P("|---|---|---|")
for repo, r in res.items():
    f32, f33 = r["m2"]
    P(f"| {repo} | {f32 if f32 is not None else r['m_state']} | {f33 if f33 is not None else r['c_state']} |")

P("\n## M3 CP 行の「いつ測るか」「落ちたら何をするか」\n")
P("**計器の点検(実行後)**: キー名の一致で数えたため、意味が違うキーも拾う。ViewTube の `sampling` は「何件測るか」"
  "(例 all fixed cases)で「いつ」ではなく、`stop_condition` は「何を不合格とするか」(例 any mismatch, unobserved required "
  "field/state, or fixture failure)で「落ちたら何をするか」ではない。下表の ViewTube 41/41 はこの読み替えを前提に読む。\n")
P("| リポ | いつ の欄を持つ行 | 処置 の欄を持つ行 | 使われたキー | 別ファイル・別節の代替 |")
P("|---|---|---|---|---|")
for repo, r in res.items():
    x = r["m3"]
    if r["c_state"] != "ok":
        P(f"| {repo} | 測定不能(33 {r['c_state']}) | 測定不能 | - | {', '.join(f'{k}×{n}' for k, n in x['alt']) or '-'} |")
        continue
    keys = ", ".join(x["when_keys"] + x["react_keys"]) or "-"
    P(f"| {repo} | {x['when_rows']}/{r['n_cp']} | {x['react_rows']}/{r['n_cp']} | {keys} | {', '.join(f'{k}×{n}' for k, n in x['alt']) or '-'} |")

P("\n## CP 行の層(結びつく M unit の数)\n")
P("| リポ | 要求直結(0) | 単位(1) | またぐ(2+) | またぐ(治具の unit を除く・事後の感度確認) |")
P("|---|---|---|---|---|")
for repo, r in res.items():
    L = r["cp_layers"]
    if L is None:
        P(f"| {repo} | 測定不能(33 {r['c_state']}) | - | - | - |")
    else:
        P(f"| {repo} | {L.get('要求直結(0)', 0)} | {L.get('単位(1)', 0)} | {L.get('またぐ(2+)', 0)} | {r['cross_ex_jig']} |")

P("\n## M4 不変条件がどの層の検査行へ届くか(INV 単位・1 つの INV が複数層に届けば各層で数える)\n")
P("| リポ | 仕様の INV | 届かない | 要求直結(0) | 単位(1) | またぐ(2+) |")
P("|---|---|---|---|---|---|")
for repo, r in res.items():
    n, x = r["m4"]
    if isinstance(x, str):
        P(f"| {repo} | {n} | {x} | - | - | - |")
    else:
        P(f"| {repo} | {n} | {x.get('届かない', 0)} | {x.get('要求直結(0)', 0)} | {x.get('単位(1)', 0)} | {x.get('またぐ(2+)', 0)} |")

P("\n## M5 単位ごとの参照数(E 参照+K 参照+依存+インターフェース契約の項目数)\n")
P("| リポ | 中央値 | 最大 | 最大の unit |")
P("|---|---|---|---|")
for repo, r in res.items():
    if r["m5"] is None:
        P(f"| {repo} | - | - | - |")
    else:
        med, (mx, mid) = r["m5"]
        P(f"| {repo} | {med} | {mx} | {mid} |")

P("\n## M6 単位間の接続(depends_on)に、両端に結びつく検査行があるか\n")
P("| リポ | depends_on を持つ unit | 接続 | 両端を検査する行がある接続 |")
P("|---|---|---|---|")
for repo, r in res.items():
    n, cov = r["m6"]
    P(f"| {repo} | {r['dep_units']}/{r['n_units']} | {n} | {cov if isinstance(cov, str) else f'{cov}/{n}'} |")
