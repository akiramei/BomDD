# loop-count — 周で回す変更の記録を、段ごとに数える(candidate・BomDD ECO-126)
#
# 製品の変更管理手順 §3.5(周で回す変更)の記録 `bomdd/loops/eco-NNN.yaml` を読み、
#   - 決めたこと・見つけたことを、出どころ(producer / maker / reader)と行き先で数える(製造側自身の決定も行に入る)
#   - 人の反応を、種類と「誰がその種類を付けたか」で数える
#   - 原因が結ばれた反応が、何に行き着いたか・それは使う前に載っていたかを出す
#   - 直しの回数(再現してから直した / 再現せずに手当てした)を出す
#
# 使い方:
#   python loop-count.py <bomdd/loops/eco-NNN.yaml>          集計を出す(exit 0。記録の欠けは [gap] の行で知らせる)
#   python loop-count.py --check <...yaml>                    記録の欠けがあれば exit 1(受入の前に走らせる)
#   python loop-count.py --selftest                           既知の良品と既知の不良の腕で、判定を実測
#
# 終了コード: 0 = 集計した(--check では欠けなし)/ 1 = --check で欠けあり・selftest 不成立 / 2 = 入力エラー(読めない・形が違う)
#
# 記録の書式(schema: loop-record/0.1-candidate)— この節が書式の正本(/eco-turn が指す):
#   schema: loop-record/0.1-candidate
#   eco: ECO-NNN
#   limits: {rounds: <周の上限・1 以上の整数>, budget: "<費用の枠・自由記述>"}   # 2 つとも必須
#   rounds:                                    # 1 つ以上
#     - n: 1                                   # 周の番号(整数・重複なし)
#       set: {commit: <sha>, jig: <治具の sha256 か none>, files: {<主なファイル>: <sha256>, ...}}   # jig は必須(治具なしは none)・files は 1 つ以上・値は空でない
#       handed_at: "<渡した時刻>"
#       launches: unknown | {count: <n>, matching: <m>}     # handover-stamp.py check の「record line」をそのまま写す(起動 0 回なら {count: 0, matching: 0})。
#                                                           # 起動口を使わなかった・check が入力エラー(exit 2)なら unknown。返事のある周には必須
#       reply: {words: "<返事の原文>"}                       # 返事が来るまでは省く。その周に反応の行があれば必須。返事のある周には反応の行が 1 つ以上
#       repairs: {fixed_after_reproduction: <n>, patched_without_reproduction: <n>}
#       checks_replaced: <n>                   # 人の反応で置き換えた検査の数(§3.5 の条件)
#       reasks: <n>                            # 返事を聞き直した回数
#   items:                                     # 決めたこと・見つけたこと。1 行 1 件
#     - id: <一意>
#       round: <n>                             # rounds にある番号(必須)
#       source: producer | maker | reader      # 周を回す側 / 製造の担当 / 別の文脈の読み手
#       kind: provisional | ratification | decision | notice | finding | preread
#       subject: <同じ中身の行をまとめる名前(省けば id)>
#       about: <どの決定についての行か(任意)>
#       disposition: to_user_check | to_user_report | asked | no_action | not_asked | fixed | record_fixed | known_only | measured_closed
#       channel: "<確認項目・裁定・図面の行の番号>"   # asked と fixed には必須
#       why: "<理由>"                           # not_asked には必須
#       outcome: passed | accepted | diff | tied_to_diff | open | measured | none   # 後で分かったこと(任意)
#   reactions:                                 # 返事 1 つにつき 1 行以上。違いが無い返事も 1 行(class: none)
#     - id: <一意>
#       round: <n>                             # rounds にある番号
#       words: "<原文>"
#       kind: pass | pass_but | fail           # 合格 / 合格だが直したい / 不合格(目的に届いていない)
#       kind_by: user | reading                # 種類を付けたのは人か、製造側の読みか
#       class: decision_change | new_want | repair | unresolved | outside | left_as_is | none
#       lands_on: [<items の id>, ...]         # 原因が結ばれたとき(list)
#       listed_before_use: yes | no | unknown  # lands_on があれば必須: 行き着いた先は、使う前の引き渡しに載っていたか
#   reports:                                   # 未解決の報告
#     - id: <一意>
#       accepted: yes | no | dropped           # 受け入れた / 受け入れない(直す周へ)/ この変更の主張から外した
#       named_in: "<受け入れを名指しした返事の原文>"   # accepted: yes には必須
#
# 語の意味(items)— disposition は「製造側が、その行をどこへ回したか」、outcome は「後で記録に現れた出来事」:
#   kind         provisional   製造側が仮に決めたこと(図面に [仮] と書いた決定)
#                ratification  作り手や読み手の項目を「そのまま」と追認した決定
#                decision      作り手が、製造の中で決めたこと
#                notice        作り手が気づいて、直さなかったこと
#                finding       別の文脈の読みの指摘
#                preread       作る前の読みが返した行
#   disposition  to_user_check   確認項目か、単独の裁定に入れた(人に「見てください」と渡した)
#                to_user_report  未解決の報告に入れた(人に「受け入れるかを名指してください」と渡した。reports にも 1 行)
#                asked           作る前に、人に伺った(channel = 伺った裁定の番号)
#                not_asked       作る前の読みの行を、伺わないと決めた(why = 理由)
#                fixed           作る前に、その行のとおりに図面を直した(channel = 直した図面の行の番号)。人には渡していない
#                record_fixed    作った後に、図面か台帳の文を実物に合わせて直した(動きは変えていない)。人には渡していない
#                no_action       「未確認の細部」の一覧に入れた(人がすることは無い)
#                known_only      既に書いてある限界・改訂として残した。人には渡していない
#                measured_closed 製造側が測って閉じた
#   outcome      passed        合格の返事が覆う確認項目に入っていた
#                accepted      受け入れの返事で名指しされた
#                diff          人の違いの指摘が、この行を指した
#                tied_to_diff  人に渡さなかったが、後で、違いの指摘と結び付いた
#                open          任意の項目で、試した記録が無い
#                measured      後で測った数字がある
#                none          記録に、その後の出来事が無い(問題が無かった、という意味ではない)
#   /eco-turn の一覧との対応: 確認項目・単独の裁定 = to_user_check / 「未解決の報告」= to_user_report /
#   「未確認の細部」= no_action。
#
# 書き方の注意: 時刻や yes / no のように YAML が別の型に読む値は、引用符で囲む(囲まないと、原文や時刻が「無い」と報告される)。
#
# --check が**見ない**もの(宣言 — 見ないことは許可ではない):
#   - outcome の語彙(任意の欄。語彙の外の語は、段 3 の表に別の行として出る)/ subject・about の中身
#   - reply の無い周に launches が無いこと(返事が来るまでは省いてよい)
# 既知の欠陥: UTF-8 でない記録は、[input](exit 2)ではなく例外で落ちる(exit 1)。
# selftest の腕が覆う範囲(BomDD ECO-126 の証拠 mutants_tools.py・2026-11-17 に実測): 検査を 1 つずつ外した写しのうち、
#   別の文脈の読みが作った 47 と、後から足した検査の 10 のすべてで、selftest が赤になった。覆っていないと分かっているもの:
#   上の「見ないもの」と、UTF-8 でない記録。写しの一覧に無い検査については、何も言えない。
#
# これは**測る**道具で、止めない。記録が無くても、製品の検査器は変更を止めない(BomDD ECO-126 の宣言)。
# 行き先や種類を書くのは製造側である — この道具は、書かれたものを数え、欠けを見せるだけで、正しさは測らない
# (named_in が本当にその返事の原文か、kind_by: user が本当に人の付けた種類か、は確かめない)。
# kind_by: reading(製造側の読みで付けた種類)は、user が付けたものと分けて数える。

import argparse
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML が必要です: pip install pyyaml")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCHEMA = "loop-record/0.1-candidate"
SOURCES = ["producer", "reader", "maker"]
ITEM_KINDS = {"provisional", "ratification", "decision", "notice", "finding", "preread"}
DISPOSITIONS = ["to_user_check", "to_user_report", "asked", "no_action", "not_asked", "fixed", "record_fixed",
                "known_only", "measured_closed"]
ASKED = {"to_user_check", "to_user_report", "asked"}          # 人に「見て・名指して・選んで」と頼んだ
PREREAD_DISPOSITIONS = {"asked", "fixed", "not_asked"}        # 作る前の読みの行は、この 3 つのどれか
REACTION_KINDS = ["pass", "pass_but", "fail"]                 # 合格 / 合格だが直したい / 不合格(目的に届いていない)
KIND_BY = ["user", "reading"]
REACTION_CLASSES = ["decision_change", "new_want", "repair", "unresolved", "outside", "left_as_is", "none"]
LISTED = {"yes", "no", "unknown"}
ACCEPTED = {"yes", "no", "dropped"}
SCALAR = (str, int, float)


class InputError(Exception):
    pass


def _yn(v):
    """YAML は yes / no を真偽値に読む。どちらの書き方も受ける。"""
    if v is True:
        return "yes"
    if v is False:
        return "no"
    return str(v).strip().lower() if isinstance(v, SCALAR) else ""


def _text(v):
    return str(v).strip() if isinstance(v, SCALAR) and not isinstance(v, bool) else ""


def _count(v, where):
    if v is None:
        return 0
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise InputError(f"{where} は 0 以上の整数({v!r})")
    return v


def load(path):
    """読んで、形を確かめる。形が違えば InputError(exit 2)— 欠け(exit 1)と混ぜない。"""
    try:
        with open(path, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        raise InputError(f"読めない: {path} — {e}")
    if not isinstance(doc, dict):
        raise InputError("top-level が mapping でない")
    if doc.get("schema") != SCHEMA:
        raise InputError(f"schema が {SCHEMA} でない({doc.get('schema')!r})")
    for key in ("rounds", "items", "reactions", "reports"):
        v = doc.get(key)
        if v is None:
            v = []
        if not isinstance(v, list):
            raise InputError(f"{key} が list でない")
        for x in v:
            if not isinstance(x, dict):
                raise InputError(f"{key} に mapping でない要素がある")
        doc[key] = v
    lim = doc.get("limits")
    if lim is not None and not isinstance(lim, dict):
        raise InputError("limits が mapping でない")
    lr = (lim or {}).get("rounds")
    if lr is not None and (isinstance(lr, bool) or not isinstance(lr, int) or lr < 1):
        raise InputError(f"limits.rounds は 1 以上の整数({lr!r})")
    for r in doc["rounds"]:
        w = f"rounds {r.get('n')!r}"
        for k in ("set", "reply", "repairs"):
            if r.get(k) is not None and not isinstance(r[k], dict):
                raise InputError(f"{w}: {k} が mapping でない")
        files = (r.get("set") or {}).get("files")
        if files is not None and not isinstance(files, dict):
            raise InputError(f"{w}: set.files が mapping でない(<ファイル>: <sha256>)")
        if not (r.get("launches") is None or r.get("launches") == "unknown" or isinstance(r.get("launches"), dict)):
            raise InputError(f"{w}: launches は unknown か {{count, matching}}")
        if isinstance(r.get("launches"), dict):   # handover-stamp check の record line: 2 つとも 0 以上の整数
            for k in ("count", "matching"):
                v = r["launches"].get(k)
                if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                    raise InputError(f"{w}: launches.{k} は 0 以上の整数({v!r})")
        k = r.get("repairs") or {}
        _count(k.get("fixed_after_reproduction"), f"{w}: repairs.fixed_after_reproduction")
        _count(k.get("patched_without_reproduction"), f"{w}: repairs.patched_without_reproduction")
        _count(r.get("checks_replaced"), f"{w}: checks_replaced")
        _count(r.get("reasks"), f"{w}: reasks")
    for key in ("items", "reactions", "reports"):
        for x in doc[key]:
            for k in ("id", "round", "subject", "about", "source", "kind", "disposition", "outcome", "kind_by", "class",
                      "channel", "why", "words", "named_in", "accepted", "listed_before_use"):
                if x.get(k) is not None and not isinstance(x[k], (str, int, float, bool)):
                    raise InputError(f"{key} {x.get('id')!r}: {k} が 1 つの値でない({type(x[k]).__name__})")
            if key == "reactions" and x.get("lands_on") is not None:
                lo = x["lands_on"]
                if not isinstance(lo, list) or not all(isinstance(t, SCALAR) for t in lo):
                    raise InputError(f"reactions {x.get('id')!r}: lands_on は items の id の list")
    return doc


def gaps(doc):
    """記録の欠け(--check が exit 1 にするもの)。"""
    out = []
    if not doc["rounds"]:
        out.append("rounds: 周が 1 つも無い(渡した版の記録が無い)")
    lim = doc.get("limits") or {}
    if lim.get("rounds") is None:
        out.append("limits: 周の上限(limits.rounds)が無い")
    if not _text(lim.get("budget")):
        out.append("limits: 費用の枠(limits.budget)が無い")
    round_numbers = [r.get("n") for r in doc["rounds"]]
    seen = set()
    for it in doc["items"]:
        iid = _text(it.get("id"))
        if not iid:
            out.append("items: id のない行がある")
            continue
        if iid in seen:
            out.append(f"items {iid}: id が重複している")
        seen.add(iid)
        if it.get("round") is None or it.get("round") not in round_numbers:
            out.append(f"items {iid}: round が rounds に無い({it.get('round')!r})")
        if it.get("source") not in SOURCES:
            out.append(f"items {iid}: source が {SOURCES} のどれでもない")
        if it.get("kind") not in ITEM_KINDS:
            out.append(f"items {iid}: kind が不正({it.get('kind')})")
        d = it.get("disposition")
        if d not in DISPOSITIONS:
            out.append(f"items {iid}: 行き先(disposition)が無いか不正({d})")
        elif it.get("kind") == "preread" and d not in PREREAD_DISPOSITIONS:
            out.append(f"items {iid}: 作る前の読みの行は asked / fixed / not_asked のどれかに振り分ける")
        if d in ("asked", "fixed") and not _text(it.get("channel")):
            out.append(f"items {iid}: {d} なのに、伺った裁定・直した図面の行の番号(channel)が無い")
        if d == "not_asked" and not _text(it.get("why")):
            out.append(f"items {iid}: not_asked なのに理由(why)が無い")
    rounds_n = []
    for r in doc["rounds"]:
        n = r.get("n")
        if isinstance(n, bool) or not isinstance(n, int):
            out.append(f"rounds: 番号(n)が整数でない周がある({n!r})")
        elif n in rounds_n:
            out.append(f"rounds {n}: 番号が重複している")
        rounds_n.append(n)
        s = r.get("set") or {}
        files = s.get("files") or {}
        if not _text(s.get("commit")) or not files or not all(_text(v) for v in files.values()):
            out.append(f"rounds {n}: 版の組(set.commit と、files の空でない sha256 が 1 つ以上)が無い")
        if not _text(s.get("jig")):
            out.append(f"rounds {n}: 治具の欄(set.jig — 治具の sha256 か none)が無い")
        if not _text(r.get("handed_at")):
            out.append(f"rounds {n}: 渡した時刻(handed_at)が無い")
        la = r.get("launches")
        if isinstance(la, dict) and la["matching"] > la["count"]:
            out.append(f"rounds {n}: launches の matching が count より大きい({la['matching']} > {la['count']})")
        if _text((r.get("reply") or {}).get("words")):   # 返事のある周
            if la is None:
                out.append(f"rounds {n}: 返事があるのに launches が無い(handover-stamp check の record line か unknown)")
            if not any(x.get("round") == n for x in doc["reactions"]):
                out.append(f"rounds {n}: 返事があるのに、反応の行が 1 つも無い(違いの無い返事も 1 行 — class: none)")
    rx_ids = set()
    for x in doc["reactions"]:
        xid = _text(x.get("id"))
        if not xid:
            out.append("reactions: id のない行がある")
            continue
        if xid in rx_ids:
            out.append(f"reactions {xid}: id が重複している")
        rx_ids.add(xid)
        if x.get("round") not in rounds_n:
            out.append(f"reactions {xid}: round が rounds に無い({x.get('round')!r})")
        else:
            rd = next(r for r in doc["rounds"] if r.get("n") == x.get("round"))
            if not _text((rd.get("reply") or {}).get("words")):
                out.append(f"reactions {xid}: 周 {x.get('round')} に返事の原文(reply.words)が無い")
        if not _text(x.get("words")):
            out.append(f"reactions {xid}: 原文(words)が無い")
        if x.get("kind") not in REACTION_KINDS:
            out.append(f"reactions {xid}: 種類(kind)が無いか不正({x.get('kind')})")
        if x.get("kind_by") not in KIND_BY:
            out.append(f"reactions {xid}: 種類を誰が付けたか(kind_by: user | reading)が無い")
        if x.get("class") not in REACTION_CLASSES:
            out.append(f"reactions {xid}: 区分(class)が無いか不正({x.get('class')})")
        for t in x.get("lands_on") or []:
            if str(t) not in seen:
                out.append(f"reactions {xid}: lands_on の {t} が items に無い")
        if (x.get("lands_on") or []) and _yn(x.get("listed_before_use")) not in LISTED:
            out.append(f"reactions {xid}: 行き着いた先が、使う前に載っていたか(listed_before_use)が無い")
    report_ids = set()
    for p in doc["reports"]:
        pid = _text(p.get("id"))
        if not pid:
            out.append("reports: id のない行がある")
        elif pid in report_ids:
            out.append(f"reports {pid}: id が重複している")
        report_ids.add(pid)
        acc = _yn(p.get("accepted"))
        if acc not in ACCEPTED:
            out.append(f"reports {pid}: accepted が yes / no / dropped のどれでもない({p.get('accepted')!r})")
        elif acc == "yes" and not _text(p.get("named_in")):
            out.append(f"reports {pid}: 受け入れたのに、名指しした返事(named_in)が無い")
    return out


def tally(doc):
    """集計(数だけ。表示と照合が共有する)。"""
    items = doc["items"]
    by_src = {s: Counter(i.get("disposition") for i in items if i.get("source") == s) for s in SOURCES}
    subjects = defaultdict(list)
    for i in items:
        subjects[_text(i.get("subject")) or _text(i.get("id"))].append(i)
    rx = doc["reactions"]
    causes = []
    ids = {_text(i.get("id")): i for i in items}
    for x in rx:
        for t in x.get("lands_on") or []:
            causes.append((x.get("id"), str(t), (ids.get(str(t)) or {}).get("source"), _yn(x.get("listed_before_use"))))
    rep = Counter()
    for r in doc["rounds"]:
        k = r.get("repairs") or {}
        rep["fixed_after_reproduction"] += k.get("fixed_after_reproduction") or 0
        rep["patched_without_reproduction"] += k.get("patched_without_reproduction") or 0
        rep["checks_replaced"] += r.get("checks_replaced") or 0
        rep["reasks"] += r.get("reasks") or 0
    return {
        "rows": len(items), "subjects": len(subjects), "by_src": by_src,
        "asked": {s: sum(v for d, v in by_src[s].items() if d in ASKED) for s in SOURCES},
        "outcome": {s: Counter((i.get("disposition"), i.get("outcome")) for i in items if i.get("source") == s) for s in SOURCES},
        "reaction_kinds": Counter((x.get("kind"), x.get("kind_by")) for x in rx),
        "reaction_classes": Counter(x.get("class") for x in rx),
        "causes": causes, "repairs": rep,
        "reports": Counter(_yn(p.get("accepted")) for p in doc["reports"]),
        "preread": Counter(i.get("disposition") for i in items if i.get("kind") == "preread"),
    }


def show(doc, t, g):
    rounds = doc["rounds"]
    lim = doc.get("limits") or {}
    limit = lim.get("rounds")
    print(f"loop-count: {doc.get('eco')} — rounds {len(rounds)}" + (f" / limit {limit}" if limit is not None else "")
          + (f" / budget {lim.get('budget')}" if lim.get("budget") is not None else ""))
    if isinstance(limit, int) and not isinstance(limit, bool) and len(rounds) > limit:
        print(f"  [over] 周の上限 {limit} を超えている({len(rounds)})— 延ばしたのが誰の言葉かは、変更の文書を見る")
    for r in rounds:
        s = r.get("set") or {}
        reply = _text((r.get("reply") or {}).get("words"))
        print(f"  round {r.get('n')}: commit {s.get('commit')} files {len(s.get('files') or {})} "
              f"launches {r.get('launches', 'unknown')} reply {'yes' if reply else 'none yet'}")
    print(f"\nstage 1 — decided or found: rows {t['rows']} / subjects {t['subjects']}")
    print("\nstage 2 — disposition (rows)")
    print("  %-16s %9s %7s %6s %5s" % ("", *SOURCES, "all"))
    for d in DISPOSITIONS:
        n = [t["by_src"][s][d] for s in SOURCES]
        if sum(n):
            print("  %-16s %9d %7d %6d %5d" % (d, *n, sum(n)))
    for s in SOURCES:
        print(f"  asked of the user, {s}: {t['asked'][s]} / {sum(t['by_src'][s].values())}")
    print("\nstage 3 — outcome by disposition (rows)")
    for s in SOURCES:
        for (d, o), n in sorted(t["outcome"][s].items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
            print(f"  {s:9s} {str(d):16s} {str(o):14s} {n}")
    print("\nreactions — kind (who assigned it)")
    for (k, by), n in sorted(t["reaction_kinds"].items(), key=str):
        print(f"  {str(k):9s} by {str(by):8s} {n}")
    print("  class:", dict(sorted(t["reaction_classes"].items(), key=str)))
    print("\nwhere tied causes land")
    if not t["causes"]:
        print("  (none tied)")
    for xid, tid, src, listed in t["causes"]:
        print(f"  {xid} -> {tid} (source {src}; listed before use: {listed})")
    if t["preread"]:
        print("\nread before manufacture — rows by disposition:", dict(sorted(t["preread"].items(), key=str)))
    r = t["repairs"]
    print(f"\ninner loop — fixed after reproduction {r['fixed_after_reproduction']}, patched without reproduction "
          f"{r['patched_without_reproduction']}, checks replaced {r['checks_replaced']}, re-asks {r['reasks']}")
    print("reports:", dict(sorted(t["reports"].items(), key=str)))
    for m in g:
        print(f"[gap] {m}")
    print(f"gaps: {len(g)}")


_GOOD = f"""schema: {SCHEMA}
eco: ECO-ST
limits: {{rounds: 3, budget: "1.5M tokens"}}
rounds:
  - n: 1
    set: {{commit: abc1234, jig: none, files: {{app.dll: 00ff}}}}
    handed_at: "2026-01-01T00:00:00Z"
    launches: {{count: 1, matching: 1}}
    reply: {{words: ok}}
    repairs: {{fixed_after_reproduction: 1, patched_without_reproduction: 2}}
    checks_replaced: 3
    reasks: 4
items:
  - {{id: P-1, round: 1, source: producer, kind: provisional, disposition: to_user_check, channel: H1, outcome: diff}}
  - {{id: F-1, round: 1, source: reader, kind: finding, disposition: no_action, outcome: none}}
  - {{id: F-2, round: 1, source: maker, kind: notice, disposition: fixed, channel: D-12}}
  - {{id: M-1, round: 1, source: maker, kind: decision, disposition: to_user_report, outcome: accepted}}
  - {{id: Q-1, round: 1, source: reader, kind: preread, disposition: asked, channel: UQ-1, outcome: passed}}
  - {{id: Q-2, round: 1, source: reader, kind: preread, disposition: not_asked, why: already ruled}}
reactions:
  - {{id: X1, round: 1, words: w, kind: pass_but, kind_by: user, class: decision_change, lands_on: [P-1], listed_before_use: yes}}
  - {{id: X2, round: 1, words: w2, kind: pass, kind_by: reading, class: none}}
reports:
  - {{id: U-1, accepted: yes, named_in: "U-1 を受け入れる"}}
"""
_REACTION = "{id: X1, round: 1, words: w, kind: pass_but, kind_by: user, class: decision_change, lands_on: [P-1], listed_before_use: yes}"
_REACTION2 = "  - {id: X2, round: 1, words: w2, kind: pass, kind_by: reading, class: none}\n"
_ROUND_SET = "set: {commit: abc1234, jig: none, files: {app.dll: 00ff}}"
_LAUNCHES = "    launches: {count: 1, matching: 1}\n"
_LIMITS = 'limits: {rounds: 3, budget: "1.5M tokens"}\n'
_REPORT = '  - {id: U-1, accepted: yes, named_in: "U-1 を受け入れる"}\n'
_ROUND2 = ("  - n: 2\n    set: {commit: def5678, jig: none, files: {app.dll: 11aa}}\n"
           '    handed_at: "2026-01-02T00:00:00Z"\n')
_EMPTY = object()   # 腕の印: schema・eco・limits だけの記録(周も行も無い)
# (label, 置き換え前, 置き換え後, 期待 exit, 出力に含まれるべき語[, 欠けの数])。
# exit 1 の腕は、欠けがちょうど 1 件であることも見る(欠けの数を None にした腕だけ、数を見ない)
_ARMS = (
    ("known-good", None, None, 0, "gaps: 0"),
    ("known-bad: 種類の無い反応", "kind: pass_but, ", "", 1, "種類(kind)"),
    ("known-bad: 種類を誰が付けたかが無い", "kind_by: user, ", "", 1, "kind_by"),
    ("known-bad: 区分の無い反応", "class: decision_change, ", "", 1, "区分(class)"),
    ("known-bad: 原文の無い反応", "words: w, ", "", 1, "原文(words)"),
    ("known-bad: 周に無い番号の反応", _REACTION2, _REACTION2.replace("round: 1", "round: 9"), 1, "round が rounds に無い"),
    ("known-bad: items に無い行き先", "lands_on: [P-1]", "lands_on: [P-9]", 1, "items に無い"),
    ("known-bad: 使う前に載っていたかが無い", ", listed_before_use: yes", "", 1, "listed_before_use"),
    ("known-bad: 版の組の無い周(files なし)", _ROUND_SET, "set: {commit: abc1234, jig: none}", 1, "版の組"),
    ("known-bad: 版の組の無い周(commit なし)", _ROUND_SET, "set: {jig: none, files: {app.dll: 00ff}}", 1, "版の組"),
    ("known-bad: 版の組の無い周(sha256 が空)", _ROUND_SET, "set: {commit: abc1234, jig: none, files: {app.dll: ''}}", 1, "版の組"),
    ("known-bad: 渡した時刻の無い周", '    handed_at: "2026-01-01T00:00:00Z"\n', "", 1, "handed_at"),
    ("known-bad: 返事の原文の無い周に反応がある", "    reply: {words: ok}\n", "", 1, "reply.words", 2),
    ("known-bad: 行き先の無い行", "kind: finding, disposition: no_action, ", "kind: finding, ", 1, "行き先(disposition)"),
    ("known-bad: 振り分けていない作る前の読み", "kind: preread, disposition: asked, channel: UQ-1",
     "kind: preread, disposition: no_action", 1, "作る前の読み"),
    ("known-bad: asked なのに裁定の番号が無い", "disposition: asked, channel: UQ-1, ", "disposition: asked, ", 1, "channel"),
    ("known-bad: fixed なのに直した行の番号が無い", "disposition: fixed, channel: D-12", "disposition: fixed", 1, "channel"),
    ("known-bad: not_asked なのに理由が無い", "disposition: not_asked, why: already ruled", "disposition: not_asked", 1, "why"),
    ("known-bad: 名指しの無い受け入れ", ', named_in: "U-1 を受け入れる"', "", 1, "named_in"),
    ("known-bad: accepted の語彙の外", "accepted: yes, ", "accepted: accepted, ", 1, "yes / no / dropped"),
    ("known-bad: 周が 1 つも無い(空の記録)", _EMPTY, "", 1, "周が 1 つも無い"),
    ("known-bad(形): lands_on が list でない", "lands_on: [P-1]", "lands_on: P-1", 2, "[input]"),
    ("known-bad(形): set が mapping でない", _ROUND_SET, "set: abc", 2, "[input]"),
    ("known-bad(形): repairs の数が数でない", "fixed_after_reproduction: 1", "fixed_after_reproduction: many", 2, "[input]"),
    # --- ECO-126 の直し(2026-11-17・別の文脈の読みの 2 回目が「見ない」と実測した 6 つ)---
    ("known-bad: 返事があるのに反応の行が無い", "  - " + _REACTION + "\n" + _REACTION2, "", 1, "反応の行が 1 つも無い"),
    ("known-bad: reports の id が重複", _REPORT, _REPORT + "  - {id: U-1, accepted: dropped}\n", 1, "reports U-1: id が重複"),
    ("known-bad: items の round が rounds に無い", "id: F-1, round: 1, ", "id: F-1, round: 7, ", 1, "items F-1: round が rounds に無い"),
    ("known-bad: items に round が無い", "id: F-1, round: 1, ", "id: F-1, ", 1, "items F-1: round が rounds に無い"),
    ("known-bad: limits が無い", _LIMITS, "", 1, "limits", 2),
    ("known-bad: 周の上限が無い", _LIMITS, 'limits: {budget: "1.5M tokens"}\n', 1, "周の上限(limits.rounds)"),
    ("known-bad: 費用の枠が無い", _LIMITS, "limits: {rounds: 3}\n", 1, "費用の枠(limits.budget)"),
    ("known-bad: 治具の欄が無い", _ROUND_SET, "set: {commit: abc1234, files: {app.dll: 00ff}}", 1, "治具の欄(set.jig"),
    ("known-bad: 返事があるのに launches が無い", _LAUNCHES, "", 1, "launches が無い"),
    ("known-bad: launches の matching が count より大きい", _LAUNCHES, "    launches: {count: 1, matching: 2}\n", 1, "matching が count より大きい"),
    ("known-bad(形): launches の count が数でない", _LAUNCHES, "    launches: {count: many, matching: 0}\n", 2, "[input]"),
    ("known-bad(形): launches に matching が無い", _LAUNCHES, "    launches: {count: 1}\n", 2, "[input]"),
    ("known-bad(形): 周の上限が数でない", _LIMITS, 'limits: {rounds: three, budget: "1.5M tokens"}\n', 2, "[input]"),
    # handover-stamp check の record line を、そのまま写した記録(exit 3 の行・exit 1 の行・使わなかったとき)は欠けではない
    ("known-good: launches が起動 0 回の record line", _LAUNCHES, "    launches: {count: 0, matching: 0}\n", 0, "launches {'count': 0, 'matching': 0}"),
    ("known-good: launches が一致しない起動を含む record line", _LAUNCHES, "    launches: {count: 2, matching: 1}\n", 0,
     "launches {'count': 2, 'matching': 1}"),
    ("known-good: launches: unknown", _LAUNCHES, "    launches: unknown\n", 0, "launches unknown"),
    # --- selftest が覆っていなかった検査(同じ読みが「外しても緑のまま」と実測したもの)---
    ("known-bad: id の無い反応", "  - {id: X2, round: 1, words: w2", "  - {round: 1, words: w2", 1, "reactions: id のない行"),
    ("known-bad: 反応の id が重複", "  - {id: X2, round: 1, words: w2", "  - {id: X1, round: 1, words: w2", 1, "reactions X1: id が重複"),
    ("known-bad: 周の番号が重複", "items:\n", _ROUND2.replace("n: 2", "n: 1") + "items:\n", 1, "番号が重複"),
    ("known-bad: 周の番号が整数でない", "  - n: 1\n", "  - n: one\n", 1, "番号(n)が整数でない", None),
    ("known-bad: 出どころが語彙の外", "source: reader, kind: finding", "source: nobody, kind: finding", 1, "items F-1: source"),
    ("known-bad: 行の種類が語彙の外", "kind: finding, disposition: no_action", "kind: thing, disposition: no_action", 1, "items F-1: kind"),
    ("known-bad: 行の id が重複", "id: F-1, round: 1, ", "id: P-1, round: 1, ", 1, "items P-1: id が重複"),
    ("known-bad: id の無い行", "id: F-1, round: 1, ", "round: 1, ", 1, "items: id のない行"),
    ("known-bad: id の無い報告", "  - {id: U-1, accepted: yes", "  - {accepted: yes", 1, "reports: id のない行"),
    ("known-bad(形): 1 つの値でない欄", "words: w, ", "words: [w], ", 2, "[input]"),
    ("known-bad(形): launches が数", _LAUNCHES, "    launches: 3\n", 2, "[input]"),
    ("known-bad(形): files が mapping でない", "files: {app.dll: 00ff}", "files: [app.dll]", 2, "[input]"),
    ("known-bad(形): 行が mapping でない", _REPORT, _REPORT + "  - just a string\n", 2, "[input]"),
    ("known-good: 周の上限を超えると [over] が出る", "items:\n", _ROUND2 + _ROUND2.replace("n: 2", "n: 3").replace("def5678", "0a1b2c3")
     + _ROUND2.replace("n: 2", "n: 4").replace("def5678", "4d5e6f7") + "items:\n", 0, "[over] 周の上限 3 を超えている(4)"),
)
# 数え方の腕: 良品の集計に、この行が出ていること(行き先・種類・合計の取り違えを見つける)
_TALLY_LINES = ("loop-count: ECO-ST — rounds 1 / limit 3 / budget 1.5M tokens",
                "rows 6 / subjects 6", "asked of the user, producer: 1 / 1", "asked of the user, reader: 1 / 3",
                "asked of the user, maker: 1 / 2",
                "  producer  to_user_check    diff           1", "  maker     to_user_report   accepted       1",
                "X1 -> P-1 (source producer; listed before use: yes)", "pass_but  by user     1", "pass      by reading  1",
                "  class: {'decision_change': 1, 'none': 1}",
                "read before manufacture — rows by disposition: {'asked': 1, 'not_asked': 1}",
                "fixed after reproduction 1, patched without reproduction 2, checks replaced 3, re-asks 4",
                "reports: {'yes': 1}")
_TALLY_ONLY_GOOD = "known-good"   # 集計の行を照合するのは、この腕だけ(ほかの known-good は、名指した語だけを見る)


def _selftest():
    import subprocess
    bad = []
    for arm in _ARMS:
        label, old, new, want, must = arm[:5]
        n_gaps = arm[5] if len(arm) > 5 else 1
        body = _GOOD
        if old is not None:
            if old is _EMPTY:
                body = f"schema: {SCHEMA}\neco: ECO-ST\n{_LIMITS}"
            elif body.count(old) != 1:
                bad.append(f"{label}: 腕の置き換え元が 1 か所でない({body.count(old)})")
                continue
            else:
                body = body.replace(old, new)
        with tempfile.TemporaryDirectory(prefix="loop-count-st-") as d:
            p = Path(d) / "eco-st.yaml"
            p.write_text(body, encoding="utf-8")
            r = subprocess.run([sys.executable, __file__, "--check", str(p)], capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            out = (r.stdout or "") + (r.stderr or "")
            if r.returncode != want:
                bad.append(f"{label}: 期待 exit {want}・実測 {r.returncode}")
            elif must not in out:
                bad.append(f"{label}: その理由で落ちていない(語 {must!r})")
            elif want == 1 and n_gaps is not None and out.count("[gap]") != n_gaps:
                bad.append(f"{label}: 欠けが {n_gaps} 件でない({out.count('[gap]')})")
            elif "Traceback" in out:
                bad.append(f"{label}: 例外で落ちている")
            elif label == _TALLY_ONLY_GOOD:
                miss = [l for l in _TALLY_LINES if l not in out]
                if miss:
                    bad.append(f"{label}: 集計の行が出ていない {miss}")
    if bad:
        print("selftest FAIL(計器を先に疑う): " + " / ".join(bad))
        return 1
    n_bad = sum(1 for a in _ARMS if a[3] != 0)
    print(f"selftest PASS({len(_ARMS)} 腕: known-bad {n_bad}・known-good {len(_ARMS) - n_bad})")
    return 0


def main():
    ap = argparse.ArgumentParser(description="周で回す変更の記録を段ごとに数える(BomDD ECO-126)")
    ap.add_argument("record", nargs="?", help="bomdd/loops/eco-NNN.yaml")
    ap.add_argument("--check", action="store_true", help="記録の欠けがあれば exit 1")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(_selftest())
    try:
        if not args.record:
            raise InputError("記録のパスが要る")
        doc = load(args.record)
    except InputError as e:
        print(f"[input] {e}")
        sys.exit(2)
    g = gaps(doc)
    show(doc, tally(doc), g)
    sys.exit(1 if (args.check and g) else 0)


if __name__ == "__main__":
    main()
