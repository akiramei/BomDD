r"""EXP-20260919-01 第 4 回 — AI 文の認知負荷を Jev で「修正方向つき」に読めるか(設備認定)。

設計(結果受領前に固定・README §1 と同一):
- 検体= specimens/*.md(mkspec.py が記録から文字列一致で抽出・manifest.json の sha256 で照合)。
- 質問= Score 7 軸(順序 rubric 4 段・具体的状況)+ Choice primary_issue(8 択)。総合スコアは作らない。
- 反復= 各検体 3 回(再現性)。合計 24 リクエスト。
- 認定条件= ①方向 9 セル ≥ 8 / ②主因 ≥ 2/3 / ③good 偽陽性 21/21 / ④再現性 ≥ 50/56(README §1)。
- 出力= results-01.jsonl(追記)・要約は stdout(README §2 へ転記せず、集計はスクリプトが出す)。
"""
import hashlib, json, sys, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE / "specimens"
OUT = HERE / "results-01.jsonl"
KEY_FILE = Path("C:/Users/akira/.typesafe/api_key")
MODEL = "jev-latest"
REPEATS = 3
IDS = ["A_bad", "A_good", "B_bad", "B_good", "C_bad", "C_good", "obs_fix_msg", "obs_handoff_example"]

INSTRUCTIONS = (
    "The `text` field is a message written by an AI assistant to a human collaborator in a software methodology "
    "project (Japanese, with English technical terms and Markdown). Judge ONLY the writing: how hard it is for a "
    "competent software engineer who is NOT a member of this project to read and follow it. Do not judge whether "
    "the claims are correct, and do not reward or penalise length as such."
)

AXES = {
    "referent": ("How ambiguous are the demonstratives and implied subjects (\"this\", \"that way\", \"the former\", omitted subjects)?", [
        "Every demonstrative or omitted subject has an obvious antecedent in the same or the previous sentence.",
        "One demonstrative requires re-reading an earlier sentence to resolve, but only one reading fits.",
        "A demonstrative or omitted subject can plausibly refer to two different things in the context.",
        "Several references cannot be resolved without knowledge that is outside the text.",
    ]),
    "jargon": ("How much unexplained project-internal vocabulary or prerequisite knowledge does the text demand?", [
        "Specialist terms are either common in software engineering or explained at first use.",
        "One or two project-internal names appear without explanation, but the sentences still make sense without them.",
        "Several internal names, codes or nicknames are used as if already known; an outside reader loses part of the meaning.",
        "The text cannot be understood without the project's internal vocabulary, or a newly coined term is used without definition.",
    ]),
    "density": ("How many logical steps are packed into single sentences or a single paragraph?", [
        "Each sentence makes one point and each paragraph develops one idea in order.",
        "One sentence carries two points joined by a connective, but the order is still linear.",
        "A paragraph advances a rule, its consequence, a historical fact and an evaluation in one breath; the reader must hold several steps at once.",
        "Multiple logical steps are nested inside single sentences (dashes, embedded clauses), so the reader must reconstruct the order of the argument.",
    ]),
    "fact_eval": ("How clearly are observed facts separated from the author's evaluations?", [
        "Statements of what is the case and the author's judgments are in separate sentences and the judgments are marked as such.",
        "A judgment follows a fact in the same sentence but is clearly signalled (\"this means\", \"I think\").",
        "Facts and evaluations alternate inside a sentence, so it is unclear which parts were observed and which are asserted.",
        "Evaluations are written in the grammar of facts throughout; the reader cannot tell observation from opinion.",
    ]),
    "metaphor": ("How much does understanding depend on metaphor or vivid imagery?", [
        "No figurative language, or a figure that only illustrates a meaning already stated literally.",
        "One figure of speech that a reader can safely skip without losing content.",
        "A metaphor carries a meaning that is not stated literally anywhere, so the reader must interpret it.",
        "Key claims are made only through metaphor or imagery; the literal content is missing.",
    ]),
    "buried_conclusion": ("Is the conclusion stated first and concretely, or deferred behind abstract words or background?", [
        "The first sentence states the conclusion concretely (what, how many, which).",
        "The conclusion comes first but uses an abstract placeholder (\"partly\", \"half\", \"some of them\") that only later sentences resolve.",
        "The conclusion is present but appears only after background, history or evidence.",
        "No single sentence states the conclusion; the reader must assemble it from the parts.",
    ]),
    "evidence_overload": ("How much evidence that is not needed for the decision is mixed into the body?", [
        "The body contains only the facts needed for the decision; details are absent or in an appendix.",
        "A few extra numbers or examples that do not change the conclusion.",
        "Tables, lists of identifiers or per-case details occupy a large part of the body and hide the point.",
        "The text is mostly an enumeration of evidence; the argument itself is a small fraction.",
    ]),
}

PRIMARY = {
    "TOO_DENSE": "The dominant obstacle is that too many logical steps are packed into single sentences or one paragraph.",
    "AMBIGUOUS_REFERENCE": "The dominant obstacle is that demonstratives or omitted subjects cannot be resolved with confidence.",
    "JARGON": "The dominant obstacle is unexplained project-internal vocabulary, codes, nicknames or coined terms.",
    "FACT_EVAL_MIXED": "The dominant obstacle is that observed facts and the author's evaluations are interleaved without marking.",
    "METAPHOR": "The dominant obstacle is that essential meaning is carried by metaphor or imagery instead of literal statement.",
    "BURIED_CONCLUSION": "The dominant obstacle is that the conclusion is deferred behind abstract words, background or evidence.",
    "EVIDENCE_OVERLOAD": "The dominant obstacle is that evidence not needed for the decision crowds out the argument.",
    "NONE": "The text is readable as it is; no single dominant obstacle stands out.",
}

# 修正方向は主因からコードで写像(Jev には問わない)
FIX = {
    "TOO_DENSE": "SPLIT_LOGICAL_STEPS", "AMBIGUOUS_REFERENCE": "REPLACE_PRONOUN_WITH_EXPLICIT_REFERENT",
    "JARGON": "DEFINE_OR_REPLACE_TERM", "FACT_EVAL_MIXED": "STATE_FACT_BEFORE_JUDGMENT", "METAPHOR": "REMOVE_OR_DELAY_METAPHOR",
    "BURIED_CONCLUSION": "STATE_CONCLUSION_FIRST_CONCRETELY", "EVIDENCE_OVERLOAD": "MOVE_EVIDENCE_TO_APPENDIX", "NONE": "NO_CHANGE",
}

# 認定条件の定数(README §1 と同一)
NAMED = {"A": ["jargon", "referent", "fact_eval", "metaphor", "density"], "B": ["jargon", "buried_conclusion", "evidence_overload"], "C": ["buried_conclusion"]}
EXPECT_PRIMARY = {"A": {"TOO_DENSE"}, "B": {"JARGON"}, "C": {"BURIED_CONCLUSION", "AMBIGUOUS_REFERENCE"}}
DIR_MARGIN, DIR_MIN = 0.5, 8      # ①
PRIM_MIN = 2                      # ②
GOOD_MAX = 2.0                    # ③(< 2.0 が 21/21)
REP_RANGE, REP_MIN = 0.5, 50      # ④


def load_specs():
    manifest = {m["id"]: m for m in json.loads((SPEC / "manifest.json").read_text(encoding="utf-8"))}
    specs = []
    for i in IDS:
        text = (SPEC / f"{i}.md").read_text(encoding="utf-8")
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if sha != manifest[i]["sha256"]:
            raise SystemExit(f"UNMEASURABLE: specimen {i} sha256 mismatch with manifest")
        specs.append(dict(id=i, pair=manifest[i]["pair"], label=manifest[i]["label"], text=text, sha=sha))
    return specs


def run(specs):
    from typesafe_sdk import Choice, Score, TypeSafeClient, TypeSafeAuthenticationError, TypeSafeError
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        print("UNMEASURABLE: key file empty"); return 2
    questions = {ax: Score(instructions=INSTRUCTIONS + " " + q, criteria=levels) for ax, (q, levels) in AXES.items()}
    questions["primary_issue"] = Choice(instructions=INSTRUCTIONS + " Which single obstacle most impedes reading?", criteria=PRIMARY)
    n_ok = n_err = 0
    with TypeSafeClient(api_key=key, model=MODEL) as client, OUT.open("a", encoding="utf-8") as fh:
        for s in specs:
            for rep in range(1, REPEATS + 1):
                state = {"text": s["text"]}
                sha = hashlib.sha256(json.dumps(state, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
                rec = dict(ts=datetime.now(timezone.utc).isoformat(timespec="seconds"), id=s["id"], pair=s["pair"], label=s["label"],
                           rep=rep, state_sha256=sha, chars=len(s["text"]))
                try:
                    r = client.system_one(state=state, questions=questions)
                    rec["model"] = r.model
                    rec["scores"] = {ax: dict(score=r.answers[ax].score, probabilities=r.answers[ax].probabilities) for ax in AXES}
                    a = r.answers["primary_issue"]
                    rec["primary_issue"] = dict(choice=a.choice, confidence=a.confidence, probabilities=a.probabilities)
                    rec["usage"] = dict(input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens)
                    n_ok += 1
                    print(f"{s['id']:20} rep{rep} " + " ".join(f"{ax[:4]}={r.answers[ax].score:.2f}" for ax in AXES) + f" primary={a.choice}({a.confidence:.2f})")
                except TypeSafeAuthenticationError as e:
                    rec.update(error="AUTH", error_class=type(e).__name__); n_err += 1
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); print("UNMEASURABLE AUTH"); return 2
                except TypeSafeError as e:
                    rec.update(error="API", error_class=type(e).__name__, error_msg=str(e)[:200]); n_err += 1
                    print(f"{s['id']} rep{rep} UNMEASURABLE {type(e).__name__}")
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                time.sleep(0.2)
    print(f"\nrequests ok={n_ok} err={n_err}")
    return 0 if n_err == 0 else 2


def summarize():
    rows = [json.loads(l) for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [r for r in rows if "scores" in r]
    by = {}
    for r in rows:
        by.setdefault(r["id"], []).append(r)
    mean = lambda i, ax: sum(r["scores"][ax]["score"] for r in by[i]) / len(by[i])
    rng = lambda i, ax: max(r["scores"][ax]["score"] for r in by[i]) - min(r["scores"][ax]["score"] for r in by[i])

    def mode(i):
        c = Counter(r["primary_issue"]["choice"] for r in by[i]).most_common()
        return c[0][0] if len(c) == 1 or c[0][1] > c[1][1] else f"拮抗({'/'.join(k for k, _ in c)})"

    axes = list(AXES)
    print("\n## 軸スコア(3 回平均・0〜3)と主因(3 回の最頻値)\n")
    print("| 検体 | " + " | ".join(axes) + " | primary(最頻値) | 修正方向 |")
    print("|---|" + "---|" * (len(axes) + 2))
    for i in IDS:
        if i not in by:
            continue
        m = mode(i)
        print(f"| {i} | " + " | ".join(f"{mean(i, ax):.2f}" for ax in axes) + f" | {m} | {FIX.get(m, '—')} |")

    print("\n## 認定条件\n")
    # ①方向
    cells, ok1 = [], 0
    for pair, named in NAMED.items():
        b, g = f"{pair}_bad", f"{pair}_good"
        for ax in named:
            d = mean(b, ax) - mean(g, ax)
            hit = d >= DIR_MARGIN
            ok1 += hit
            cells.append(f"{pair}:{ax} bad {mean(b, ax):.2f} − good {mean(g, ax):.2f} = {d:+.2f} {'OK' if hit else 'MISS'}")
    print(f"① 方向(名指し軸 9 セルで bad−good ≥ {DIR_MARGIN}): **{ok1}/9**(条件 ≥ {DIR_MIN}) → {'PASS' if ok1 >= DIR_MIN else 'FAIL'}")
    for c in cells:
        print(f"   - {c}")
    # ②主因
    ok2 = 0
    for pair, exp in EXPECT_PRIMARY.items():
        m = mode(f"{pair}_bad")
        hit = m in exp
        ok2 += hit
        print(f"   - {pair}_bad primary= {m}(期待 {'/'.join(sorted(exp))}) {'OK' if hit else 'MISS'}")
    print(f"② 主因(bad 側の最頻値が第三者の主因と一致): **{ok2}/3**(条件 ≥ {PRIM_MIN}) → {'PASS' if ok2 >= PRIM_MIN else 'FAIL'}")
    # ③good 偽陽性
    bad_cells = [(i, ax, mean(i, ax)) for i in ("A_good", "B_good", "C_good") for ax in axes if not mean(i, ax) < GOOD_MAX]
    print(f"③ good 側の偽陽性(good 3 本 × 7 軸で平均 < {GOOD_MAX}): **{21 - len(bad_cells)}/21**(条件 21/21) → {'PASS' if not bad_cells else 'FAIL'}"
          + ("" if not bad_cells else " — 違反: " + ", ".join(f"{i}:{ax}={v:.2f}" for i, ax, v in bad_cells)))
    # ④再現性
    cells4 = [(i, ax, rng(i, ax)) for i in IDS if i in by for ax in axes]
    ok4 = sum(1 for _, _, v in cells4 if v <= REP_RANGE)
    worst = sorted(cells4, key=lambda x: -x[2])[:5]
    print(f"④ 再現性(56 セルで 3 回の範囲 ≤ {REP_RANGE}): **{ok4}/{len(cells4)}**(条件 ≥ {REP_MIN}) → {'PASS' if ok4 >= REP_MIN else 'FAIL'}"
          f" — 最大範囲: " + ", ".join(f"{i}:{ax}={v:.2f}" for i, ax, v in worst))
    verdict = ok1 >= DIR_MIN and ok2 >= PRIM_MIN and not bad_cells and ok4 >= REP_MIN
    print(f"\n**判定: {'認定(4/4 達成)' if verdict else '未達 → この質問設計では採らない'}**")
    print(f"\nrequests={len(rows)} tokens in={sum(r['usage']['input_tokens'] for r in rows)} out={sum(r['usage']['output_tokens'] for r in rows)} model={sorted({r['model'] for r in rows})}")


def main():
    specs = load_specs()
    if "--list" in sys.argv:
        for s in specs:
            print(s["id"], s["label"], len(s["text"]), s["sha"][:16])
        return 0
    if "--summary" not in sys.argv:
        rc = run(specs)
        if rc:
            return rc
    summarize()
    return 0


if __name__ == "__main__":
    sys.exit(main())
