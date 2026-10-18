"""When did the text each design-review finding points at first appear? (ECO-112 / ECO-113 design reviews, 2026-10-18)

Usage: python -B measure_origin.py <dir>
  <dir> holds primary/ (from extract_primary.py), round_map.json, baseline/, versions/ and versions.json (from rebuild_versions.py);
  writes findings.jsonl and summary.md there. Deterministic: the same inputs give the same outputs.

Step 1 — the reviewed versions: read from versions.json (rebuild_versions.py; each file's sha256 is checked on reading).
Step 2 — the findings. Each report's findings are the finding IDs it is the first in its ECO to use; their number must equal the receipt's
  round count (round_map.json). A finding's quoted strings ("…" or “…”, split at ellipses, at least MIN characters after normalising whitespace,
  backticks and asterisks) are looked up in the ECO's reviewed versions up to the reporting round.
Step 3 — two axes, kept apart (user ruling 2026-10-18 "A"):
  origin time  INITIAL  every usable quote is in the ECO's first reviewed version, or the finding was reported in the ECO's first round
                        (that round reviewed the first version itself; origin_basis "first reviewed round")
               LATER    every usable quote is absent from the first reviewed version and present in a later one (the round named)
               UNKNOWN  no quote; no quote found in a known reviewed version; the first reviewed version unknown; quotes that disagree
               A quote that also occurs in the repository's baseline text (baseline/) is not used (it may be cited code, not design text).
  cause        copied from the record only — the reviewer's tag in the finding, or the order's "Classes in this loop" line:
               FIX_CHANGE "new defect from the consolidation|amendment" or a note "introduced by … repair"; EXISTING "existing design defect"
               without such a note; otherwise UNKNOWN. "inconsistency from duplicated text" is the type DUPLICATION, its cause UNKNOWN.
Limit: the time measured is the quoted text's, not the defect's; a defect in old text caused by a later change elsewhere reads INITIAL
unless the finding also quotes the new text (the quotes then disagree: UNKNOWN). Nothing is guessed.
"""
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

D = Path(sys.argv[1])
MIN = 15
ID_RE = re.compile(r"^\W{0,4}(F\d+|R\d+-\d+|L\dR\d+-\d+|AR\d+-\d+|A1R\d+-\d+)\b")
QUOTE_RE = re.compile(r"\"([^\"\n]{%d,600})\"|“([^”]{%d,600})”" % (MIN, MIN))
HEAD_RE = re.compile(r"^\s*findings:\s*(\d+)", re.I | re.M)
SEV_RE = re.compile(r"\[(material|minor)\]|—\s*(material|minor)\s*—", re.I)
TAGS = [("new defect from the consolidation", "FIX_CHANGE"), ("new defect from the amendment", "FIX_CHANGE"),
        ("existing design defect", "EXISTING"), ("inconsistency from duplicated text", "DUPLICATION")]


def norm(s):
    s = s.replace("`", "").replace("**", "").replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", s).strip(" .,;:")


def frags(q):
    return [f for f in (norm(p) for p in re.split(r"…|\.\.\.", q)) if len(f) >= MIN]


def doc_key(path):
    p = (path or "").replace("\\", "/")
    if p.endswith("eco113/60-change-order-eco-113.md") and "scratchpad" in p:
        return "113s"
    if "scratchpad" in p:
        return None
    if p.endswith("60-change-order-eco-112.md"):
        return "112"
    if p.endswith("60-change-order-eco-113.md"):
        return "113"
    return None


NAMES = {"112": "60-change-order-eco-112.md", "113": "60-change-order-eco-113.md", "113s": "eco113/60-change-order-eco-113.md"}

# ---------- step 1: the reviewed versions (built by rebuild_versions.py) ----------
VERS = {(v["eco"], v["round"]): v for v in json.loads((D / "versions.json").read_text(encoding="utf-8"))}

# ---------- step 2: rounds and findings ----------
rmap = json.loads((D / "round_map.json").read_text(encoding="utf-8"))
reviews = [json.loads(ln) for ln in (D / "primary" / "reviews.jsonl").open(encoding="utf-8")]
by_agent = defaultdict(lambda: {"request": [], "report": []})
for x in reviews:
    if x["kind"] == "request" and x["text"].lstrip().startswith("<system-reminder>"):
        continue
    by_agent[x["agent"]][x["kind"]].append(x)
rounds = []
for agent, kinds in by_agent.items():
    cfg = rmap[agent]
    reqs = sorted(kinds["request"], key=lambda x: x["ts"])
    reps = sorted(kinds["report"], key=lambda x: x["ts"])
    assert len(reps) == len(cfg["rounds"]), (agent, len(reps), len(cfg["rounds"]))
    key = "112" if cfg["eco"] == "ECO-112" else "113"
    for label, rep in zip(cfg["rounds"], reps):
        req = max((q for q in reqs if q["ts"] <= rep["ts"]), key=lambda q: q["ts"])
        if "scratchpad\\eco113" in req["text"] or "same scratch" in req["text"] or (cfg["eco"] == "ECO-113" and label.startswith("L5")):
            key = "113s"
        rounds.append({"eco": cfg["eco"], "label": label, "req": req, "rep": rep, "agent": agent, "key": key})
rounds.sort(key=lambda r: r["req"]["ts"])
for r in rounds:
    v = VERS[(r["eco"], r["label"])]
    content = (D / v["file"]).read_bytes().decode("utf-8") if v["file"] else None
    if content is not None:
        assert hashlib.sha256(content.encode("utf-8")).hexdigest() == v["sha256"], v["file"]
    r["norm"] = norm(content) if content is not None else None
    r["version"] = {"file": v["file"], "sha256": v["sha256"], "basis": v["basis"], "status": v["status"]}

recorded = {}
for eco, order in (("ECO-112", "order-eco-112.md"), ("ECO-113", "order-eco-113.md")):
    txt = (D / "baseline" / order).read_text(encoding="utf-8")
    for m in re.finditer(r"\*\*Classes in this loop[^:]*:\*\*(.*?)(?=\n- \*\*|\n#|\Z)", txt, re.S):
        body = re.sub(r"\s+", " ", m.group(1))
        for part in re.finditer(r"(new defect from the (?:consolidation|amendment)|existing design defect|inconsistency from duplicated text) \d+ \(([^)]*)\)", body):
            cls, inner = part.group(1), part.group(2)
            for idm in re.finditer(r"(L\dR\d+-\d+|AR\d+-\d+|A1R\d+-\d+)((?:,? [^,;)]*)?)", inner):
                recorded.setdefault((eco, idm.group(1)), []).append((cls, idm.group(2).strip(", ")))
            rng = re.search(r"(A1R\d)-(\d) to A1R\d-(\d)", inner)
            if rng:
                for n in range(int(rng.group(2)), int(rng.group(3)) + 1):
                    recorded.setdefault((eco, f"{rng.group(1)}-{n}"), []).append((cls, ""))
baseline = [norm(p.read_text(encoding="utf-8")) for p in sorted((D / "baseline").glob("3a9de06--*"))]

findings, mismatches = [], []
seen = defaultdict(set)
for idx, r in enumerate(rounds):
    eco = r["eco"]
    eco_rounds = [x for x in rounds if x["eco"] == eco]
    pos = eco_rounds.index(r)
    text = r["rep"]["text"]
    lines = text.split("\n")
    starts = [(i, m.group(1)) for i, l in enumerate(lines) for m in [ID_RE.match(l)] if m]
    new, local = [], set()
    for i, fid in starts:
        if fid not in seen[eco] and fid not in local:
            new.append((i, fid))
        local.add(fid)
    seen[eco] |= local
    head = HEAD_RE.search(text)
    want = rmap["receipt_counts"][eco][pos]
    if len(new) != want or (head and int(head.group(1)) != want):
        mismatches.append(f"{eco} {r['label']}: header {head.group(1) if head else '?'}, new IDs {len(new)}, receipt {want}")
    for i, fid in new:
        nxt = next((j for j, _ in starts if j > i), len(lines))
        body = "\n".join(lines[i:nxt]).strip()
        sev = SEV_RE.search(body)
        quotes = [m.group(1) or m.group(2) for m in QUOTE_RE.finditer(body)]
        qs = []
        for fr in dict.fromkeys(f for q in quotes for f in frags(q)):
            if any(fr in b for b in baseline):
                qs.append({"fragment": fr, "status": "also_in_repository_text"})
                continue
            hits = [k for k, x in enumerate(eco_rounds[:pos + 1]) if x["norm"] is not None and fr in x["norm"]]
            if not hits:
                qs.append({"fragment": fr, "status": "not_in_reviewed_version" if eco_rounds[pos]["norm"] is not None else "reviewed_version_unknown"})
                continue
            k0 = hits[0]
            before = [x for x in eco_rounds[:k0] if x["norm"] is not None]
            gap = [x["label"] for x in eco_rounds[:k0] if x["norm"] is None]
            q = {"fragment": fr, "status": "found", "first_round": eco_rounds[k0]["label"], "first_version": eco_rounds[k0]["version"]["file"],
                 "unknown_versions_before": gap}
            if k0 == 0:
                q["side"] = "INITIAL"
            elif eco_rounds[0]["norm"] is None:
                q["side"] = None
                q["status"] = "first_version_unknown"
            else:
                q["side"] = "LATER"
                q["absent_in"] = before[-1]["label"] if before else None
            qs.append(q)
        sides = {q["side"] for q in qs if q.get("side")}
        if not quotes:
            origin, reason = "UNKNOWN", "no quoted text in the finding"
        elif not sides:
            st = Counter(q["status"] for q in qs) if qs else Counter({"quotes shorter than the minimum": 1})
            origin, reason = "UNKNOWN", "no usable quote (" + ", ".join(f"{a} {b}" for a, b in st.items()) + ")"
        elif len(sides) > 1:
            origin, reason = "UNKNOWN", "quotes disagree (some in the first reviewed version, some not)"
        else:
            origin, reason = sides.pop(), ""
        basis = "quote" if origin != "UNKNOWN" else None
        if origin == "UNKNOWN" and pos == 0:   # the ECO's first round reviewed the first version itself: INITIAL by definition
            origin, basis = "INITIAL", "first reviewed round"
        appeared = None
        if origin == "LATER":
            q0 = min((q for q in qs if q.get("side") == "LATER"), key=lambda q: [x["label"] for x in eco_rounds].index(q["first_round"]))
            appeared = {"first_reviewed_in": q0["first_round"], "last_absent_in": q0.get("absent_in"),
                        "unknown_versions_between": [g for g in q0["unknown_versions_before"]
                                                     if [x["label"] for x in eco_rounds].index(g) > [x["label"] for x in eco_rounds].index(q0["absent_in"])]
                        if q0.get("absent_in") else q0["unknown_versions_before"]}
        tag_hits = [(t, c) for t, c in TAGS if t in body.lower()]
        rec = recorded.get((eco, fid), [])
        notes = " ".join(n for _, n in rec)
        classes = [c for _, c in tag_hits] + [dict(TAGS)[c] for c, _ in rec]
        cause, cause_src = "UNKNOWN", None
        if "introduced by" in notes and "repair" in notes:
            cause, cause_src = "FIX_CHANGE", "receipt note: " + notes
        elif "FIX_CHANGE" in classes and "EXISTING" not in classes:
            cause, cause_src = "FIX_CHANGE", "recorded class"
        elif "EXISTING" in classes and "FIX_CHANGE" not in classes:
            cause, cause_src = "EXISTING", "recorded class"
        findings.append({"eco": eco, "round": r["label"], "id": fid, "severity": (sev.group(1) or sev.group(2)).lower() if sev else None,
                         "review_request": {"ts": r["req"]["ts"], "source": r["req"]["source"]},
                         "report": {"ts": r["rep"]["ts"], "source": r["rep"]["source"]},
                         "reviewed_version": r["version"], "origin": origin, "origin_basis": basis, "origin_reason": reason, "appeared": appeared,
                         "quotes": qs, "cause": cause, "cause_source": cause_src,
                         "type": "DUPLICATION" if "DUPLICATION" in classes else None,
                         "recorded_classes": sorted({c for c, _ in rec} | {t for t, _ in tag_hits}), "text": body})

with (D / "findings.jsonl").open("w", encoding="utf-8", newline="\n") as fh_:
    for f in findings:
        fh_.write(json.dumps(f, ensure_ascii=False) + "\n")

# ---------- summary ----------
out = []
P = out.append
P("# Review-finding origin — ECO-112 / ECO-113 design reviews (measured 2026-10-19)\n")
P(f"Findings: **{len(findings)}** (ECO-112 {sum(f['eco'] == 'ECO-112' for f in findings)}, ECO-113 {sum(f['eco'] == 'ECO-113' for f in findings)}); "
  f"per-round counts against the receipts: {'all equal' if not mismatches else 'MISMATCH — ' + '; '.join(mismatches)}.\n")
P("## Reviewed versions\n\n| ECO | round | review request (UTC) | version | sha256 (12) | basis |\n|---|---|---|---|---|---|")
for r in rounds:
    v = r["version"]
    P(f"| {r['eco']} | {r['label']} | {r['req']['ts'][:19]} | {v['file'] or 'UNKNOWN'} | {(v['sha256'] or '')[:12]} | {v['basis']} |")
P("\n## Origin time\n\nINITIAL is shown by its basis: a quote found in the first reviewed version, or the finding being reported in the ECO's "
  "first round (that round reviewed the first version itself).\n")
P("| ECO | INITIAL (quote) | INITIAL (first round) | LATER | UNKNOWN | total |\n|---|---|---|---|---|---|")
for eco in ("ECO-112", "ECO-113", None):
    fs = [f for f in findings if eco is None or f["eco"] == eco]
    c = Counter(f["origin"] + ("/" + f["origin_basis"] if f["origin"] == "INITIAL" else "") for f in fs)
    P(f"| {eco or 'both'} | {c['INITIAL/quote']} | {c['INITIAL/first reviewed round']} | {c['LATER']} | {c['UNKNOWN']} | {len(fs)} |")
P("\n## By loop\n\n| ECO | loop | rounds | findings | INITIAL | LATER | UNKNOWN |\n|---|---|---|---|---|---|---|")
loops = defaultdict(list)
for f in findings:
    loops[(f["eco"], re.match(r"(L\d|AR|A2)", f["round"]).group(1))].append(f)
for (eco, lp), fs in sorted(loops.items(), key=lambda kv: (kv[0][0], min(f["review_request"]["ts"] for f in kv[1]))):
    c = Counter(f["origin"] for f in fs)
    nr = len({r["label"] for r in rounds if r["eco"] == eco and r["label"].startswith(lp)})
    P(f"| {eco} | {lp} | {nr} | {len(fs)} | {c['INITIAL']} | {c['LATER']} | {c['UNKNOWN']} |")
P("\n## UNKNOWN, by reason\n\n| reason | findings |\n|---|---|")
for k, v in Counter(re.sub(r" \(.*", "", f["origin_reason"]) for f in findings if f["origin"] == "UNKNOWN").most_common():
    P(f"| {k} | {v} |")
P("\n## Cause (recorded only) against origin time\n\n| cause | INITIAL | LATER | UNKNOWN | total |\n|---|---|---|---|---|")
for cz in ("FIX_CHANGE", "EXISTING", "UNKNOWN"):
    fs = [f for f in findings if f["cause"] == cz]
    c = Counter(f["origin"] for f in fs)
    P(f"| {cz} | {c['INITIAL']} | {c['LATER']} | {c['UNKNOWN']} | {len(fs)} |")
P(f"\nType DUPLICATION (recorded): {sum(f['type'] == 'DUPLICATION' for f in findings)}.")
P("\n## LATER: where the quoted text first appeared\n\nA reviewed version is the one produced by the repairs after the round before it, so "
  "\"new in the reporting round's version\" means the text came from the repairs just before that round.\n")
P("| ECO | new in the reporting round's version | in an earlier round's version of the same loop | from an earlier loop |\n|---|---|---|---|")
for eco in ("ECO-112", "ECO-113"):
    c = Counter()
    for f in findings:
        if f["eco"] != eco or f["origin"] != "LATER":
            continue
        fr = f["appeared"]["first_reviewed_in"]
        lp = lambda lab: re.match(r"(L\d|AR|A2)", lab).group(1)
        c["same" if fr == f["round"] else ("loop" if lp(fr) == lp(f["round"]) else "earlier")] += 1
    P(f"| {eco} | {c['same']} | {c['loop']} | {c['earlier']} |")
P("\n## Severity (the reviewer's tag) against origin time\n\n| severity | INITIAL | LATER | UNKNOWN |\n|---|---|---|---|")
for sv in ("material", "minor", None):
    c = Counter(f["origin"] for f in findings if f["severity"] == sv)
    P(f"| {sv or 'not stated'} | {c['INITIAL']} | {c['LATER']} | {c['UNKNOWN']} |")
P("\n## Limits\n")
P("- The time measured is the quoted text's appearance in a reviewed version, not the defect's cause.")
P("- A finding with no quote, or whose quotes are paraphrases or cited code, is UNKNOWN; nothing is filled in by reading.")
P(f"- A quote can match an unrelated occurrence of the same words; the minimum length is {MIN} characters after normalisation.")
P("- ECO-113's first reviewed version was written from ECO-112's pre-split draft; text carried over reads INITIAL for ECO-113.")
P("- Versions are rebuilt from the session's own records; where a shell command may have changed a document between anchors and the next anchor "
  "differs, the versions in between are UNKNOWN.")
(D / "summary.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("\n".join(l for l in out if not l.startswith("| ECO-11") or "UNKNOWN" not in l)[:6000])
