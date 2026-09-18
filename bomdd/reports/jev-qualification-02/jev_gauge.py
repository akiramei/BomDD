r"""EXP-20260919-01 第 5 回 — 運用内 before/after 計測(文章のひずみゲージ)。user DECIDE B(2026-09-19)。

分業(README §3 と同一・結果受領前に固定):
  Jev   = 計測だけ(Score 5 軸・順序 rubric 4 段・0= 問題なし … 3= 重大)。主因の Choice は問わない。
  code  = 改善方向の決定(初稿で最も高い軸 1 つ → 対応表 FIX)と採否(狙った軸が ≥ 0.3 下がり、他の軸が ≥ 0.3 上がらない → ADOPT)。
  LLM   = 実際の書き直し(狙った軸だけ)。
  上限= 書き直し 2 回。2 回目は 1 回目が ADOPT かつ残る軸に ≥ 2.0 があるときだけ。

使い方:
  python jev_gauge.py measure  <msg_id> <draft.md>                      # 初稿を計測 → 狙う軸と修正方向
  python jev_gauge.py compare  <msg_id> <draft.md> <rewrite.md> [--round N]   # 書き直しを計測 → 差分と採否
  python jev_gauge.py summary                                           # 通ごとの表と認定条件の集計
記録= gauge-log.jsonl(追記・sha256 完全 64 桁・確率分布・usage)。鍵は表示・記録しない。到達不能は UNMEASURABLE(PASS に数えない)。
"""
import hashlib, json, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOG = HERE / "gauge-log.jsonl"
KEY_FILE = Path("C:/Users/akira/.typesafe/api_key")
MODEL = "jev-latest"
DROP, RISE, RETRY_FLOOR, MAX_ROUNDS = 0.3, 0.3, 2.0, 2

INSTRUCTIONS = (
    "The `text` field is a message written by an AI assistant to a human collaborator who IS a member of this software "
    "methodology project (Japanese, with English technical terms and Markdown). Project-internal names are known to the "
    "reader; do not penalise their mere presence. Judge ONLY how much effort the reader must spend to follow the writing. "
    "Do not judge whether the claims are correct, and do not reward or penalise length as such."
)

AXES = {
    "referential_ambiguity": ("How ambiguous are the demonstratives and omitted subjects (\"this\", \"that way\", \"the former\", subjects left implicit)?", [
        "Every demonstrative or omitted subject has an obvious antecedent in the same or the previous sentence.",
        "One demonstrative requires re-reading an earlier sentence to resolve, but only one reading fits.",
        "A demonstrative or omitted subject can plausibly refer to two different things in the context.",
        "Several references cannot be resolved without knowledge that is outside the text.",
    ]),
    "semantic_density": ("How many logical steps (rule, consequence, historical fact, evaluation) are advanced inside one sentence or one paragraph?", [
        "Each sentence makes one point and each paragraph develops one idea in order.",
        "One sentence carries two points joined by a connective, but the order is still linear.",
        "A paragraph advances a rule, its consequence, a fact about the past and an evaluation in one breath; the reader holds several steps at once.",
        "Multiple logical steps are nested inside single sentences (dashes, embedded clauses), so the reader must reconstruct the order of the argument.",
    ]),
    "dependency_depth": ("How many relations between named things must the reader hold at once to parse a sentence (A is declared as B, which under rule C is not D)?", [
        "Each sentence introduces at most one new relation between named things, and earlier relations are restated when reused.",
        "One sentence asks the reader to hold two relations at once, but the next sentence restates the result.",
        "A sentence stacks three or more relations among named things without restating any of them.",
        "Relations are stacked across several sentences with no restatement, so the reader must build a graph of the terms to follow the argument.",
    ]),
    "sentence_overload": ("How heavy are individual sentences (length, nested clauses, dashes, inline emphasis interrupting the reading)?", [
        "Sentences are short, single-clause or lightly coordinated, and read in one pass.",
        "Some sentences have one subordinate clause or one dash insertion; still readable in one pass.",
        "Several sentences have nested clauses, dash insertions or bold fragments that force re-reading.",
        "Most sentences must be re-read; the reader loses the main clause inside the insertions.",
    ]),
    "unnecessary_rhetoric": ("How much metaphor, dramatic phrasing or emphasis adds interpretation cost without adding literal content?", [
        "No figurative language or dramatic emphasis; or a figure that only illustrates a meaning already stated literally.",
        "One figure of speech or emphatic phrase that the reader can skip without losing content.",
        "A metaphor or dramatic phrasing carries meaning that is not stated literally anywhere, so the reader must interpret it.",
        "Key claims are made mainly through metaphor, imagery or emphasis; the literal content is missing.",
    ]),
}

FIX = {
    "referential_ambiguity": "EXPLICIT_REFERENTS(指示語・省略主語を固有の名前に置き換える)",
    "semantic_density": "SPLIT_LOGICAL_STEPS(1 文 1 論点・規則→帰結→事実→評価の順に段落を分ける)",
    "dependency_depth": "RESTATE_RELATIONS(関係を 1 つずつ言い直し、前提になる関係を先に置く)",
    "sentence_overload": "SHORTEN_SENTENCES(入れ子・ダッシュ・文中の強調を外して短文にする)",
    "unnecessary_rhetoric": "REMOVE_RHETORIC(比喩・劇的表現・強調を削り、字義どおりに言う)",
}


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def measure_text(client, text):
    from typesafe_sdk import Score
    questions = {ax: Score(instructions=INSTRUCTIONS + " " + q, criteria=levels) for ax, (q, levels) in AXES.items()}
    r = client.system_one(state={"text": text}, questions=questions)
    scores = {ax: dict(score=round(r.answers[ax].score, 3), probabilities=r.answers[ax].probabilities) for ax in AXES}
    return scores, r.model, dict(input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens)


def client_or_exit():
    from typesafe_sdk import TypeSafeClient
    key = KEY_FILE.read_text(encoding="utf-8").strip() if KEY_FILE.is_file() else ""
    if not key:
        print("UNMEASURABLE: key file missing or empty"); sys.exit(2)
    return TypeSafeClient(api_key=key, model=MODEL)


def log(rec):
    rec = dict(ts=datetime.now(timezone.utc).isoformat(timespec="seconds"), **rec)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def rows():
    if not LOG.is_file():
        return []
    return [json.loads(l) for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()]


def fmt(scores):
    return " ".join(f"{ax}={scores[ax]['score']:.2f}" for ax in AXES)


def cmd_measure(msg_id, draft_path):
    text = Path(draft_path).read_text(encoding="utf-8")
    try:
        with client_or_exit() as client:
            scores, model, usage = measure_text(client, text)
    except Exception as e:  # noqa: BLE001 — 到達不能・認証失敗は UNMEASURABLE として記録
        log(dict(kind="measure", msg_id=msg_id, round=0, draft_sha256=sha(text), chars=len(text), error=type(e).__name__, error_msg=str(e)[:200]))
        print(f"UNMEASURABLE {type(e).__name__}: {str(e)[:200]}"); return 2
    target = max(AXES, key=lambda ax: scores[ax]["score"])
    rec = log(dict(kind="measure", msg_id=msg_id, round=0, draft_sha256=sha(text), chars=len(text), model=model, scores=scores, target=target, fix=FIX[target], usage=usage))
    print(f"[{msg_id}] draft  {fmt(scores)}")
    print(f"[{msg_id}] target= {target} ({scores[target]['score']:.2f}) → {FIX[target]}")
    return 0


def cmd_compare(msg_id, draft_path, rewrite_path, rnd):
    draft = Path(draft_path).read_text(encoding="utf-8")
    rewrite = Path(rewrite_path).read_text(encoding="utf-8")
    prev = [r for r in rows() if r.get("msg_id") == msg_id and "scores" in r]
    if not prev:
        print("UNMEASURABLE: no measure record for this msg_id (run measure first)"); return 2
    base = prev[-1]  # round 0 の初稿、または round 1 で ADOPT した書き直しが基準
    if base["kind"] == "compare" and base.get("verdict") != "ADOPT":
        base = next(r for r in reversed(prev) if r["round"] < rnd and (r["kind"] == "measure" or r.get("verdict") == "ADOPT"))
    base_sha = base.get("rewrite_sha256") if base["kind"] == "compare" else base["draft_sha256"]
    if base_sha != sha(draft):
        print(f"UNMEASURABLE: draft file does not match the recorded base text (sha {base_sha[:16]} vs {sha(draft)[:16]})"); return 2
    target = max(AXES, key=lambda ax: base["scores"][ax]["score"])
    try:
        with client_or_exit() as client:
            scores, model, usage = measure_text(client, rewrite)
    except Exception as e:  # noqa: BLE001
        log(dict(kind="compare", msg_id=msg_id, round=rnd, draft_sha256=sha(draft), rewrite_sha256=sha(rewrite), error=type(e).__name__, error_msg=str(e)[:200]))
        print(f"UNMEASURABLE {type(e).__name__}: {str(e)[:200]}"); return 2
    delta = {ax: round(scores[ax]["score"] - base["scores"][ax]["score"], 3) for ax in AXES}
    worst_other = max((delta[ax] for ax in AXES if ax != target), default=0.0)
    adopt = delta[target] <= -DROP and worst_other < RISE
    verdict = "ADOPT" if adopt else "KEEP_ORIGINAL"
    remaining = max(scores[ax]["score"] for ax in AXES) if adopt else max(base["scores"][ax]["score"] for ax in AXES)
    retry = adopt and rnd < MAX_ROUNDS and remaining >= RETRY_FLOOR
    log(dict(kind="compare", msg_id=msg_id, round=rnd, draft_sha256=sha(draft), rewrite_sha256=sha(rewrite), chars_draft=len(draft), chars_rewrite=len(rewrite),
             model=model, target=target, scores=scores, delta=delta, worst_other_rise=round(worst_other, 3), verdict=verdict, retry_allowed=retry, usage=usage))
    print(f"[{msg_id}] round {rnd} target= {target}")
    print(f"[{msg_id}] base    {fmt(base['scores'])}")
    print(f"[{msg_id}] rewrite {fmt(scores)}")
    print(f"[{msg_id}] delta   " + " ".join(f"{ax}={delta[ax]:+.2f}" for ax in AXES))
    print(f"[{msg_id}] verdict= {verdict}(target {delta[target]:+.2f} ≤ −{DROP} / 他軸の最大上昇 {worst_other:+.2f} < {RISE}) retry_allowed= {retry}")
    print(f"gauge: {target} {base['scores'][target]['score']:.2f}→{scores[target]['score']:.2f} {verdict}")
    return 0


def cmd_summary():
    rs = [r for r in rows() if "scores" in r]
    ids = []
    for r in rs:
        if r["msg_id"] not in ids:
            ids.append(r["msg_id"])
    print("| 通 | 初稿 最高軸(値) | r1 差分(狙った軸) | r1 他軸最大上昇 | r1 採否 | r2 採否 | 最終最高値 |\n|---|---|---|---|---|---|---|")
    n_dir = n_side = n_adopt = n_measured = 0
    for i in ids:
        g = [r for r in rs if r["msg_id"] == i]
        m = next((r for r in g if r["kind"] == "measure"), None)
        c1 = next((r for r in g if r["kind"] == "compare" and r["round"] == 1), None)
        c2 = next((r for r in g if r["kind"] == "compare" and r["round"] == 2), None)
        if not m:
            continue
        n_measured += 1
        t = m["target"]
        d1 = c1["delta"][t] if c1 else None
        if c1:
            n_dir += d1 <= -DROP
            n_side += c1["worst_other_rise"] >= RISE
            n_adopt += c1["verdict"] == "ADOPT"
        last = c2 if (c2 and c2["verdict"] == "ADOPT") else (c1 if (c1 and c1["verdict"] == "ADOPT") else m)
        final_max = max(last["scores"][ax]["score"] for ax in AXES)
        print(f"| {i} | {t}({m['scores'][t]['score']:.2f}) | {d1:+.2f} | {c1['worst_other_rise']:+.2f} | {c1['verdict']} | {c2['verdict'] if c2 else '—'} | {final_max:.2f} |"
              if c1 else f"| {i} | {t}({m['scores'][t]['score']:.2f}) | — | — | (未比較) | — | {final_max:.2f} |")
    n = len(ids)
    print(f"\n認定条件(N=10・README §3): ①計測記録あり {n_measured}/{n} / ②狙った軸が ≥ {DROP} 下がった {n_dir}/{n} (条件 ≥ 7/10) / ③他軸が ≥ {RISE} 上がった {n_side}/{n} (条件 ≤ 3/10) / 採用 {n_adopt}/{n}")
    print("④ user の「分かりにくい」指摘は gauge-log 外(improvements.md の受入節に通番で記録)。⑤ 追加時間は各通の ts 差(measure→compare)。")
    print(f"requests={len(rs)} tokens in={sum(r['usage']['input_tokens'] for r in rs)} out={sum(r['usage']['output_tokens'] for r in rs)}")


def main(argv):
    if len(argv) >= 3 and argv[0] == "measure":
        return cmd_measure(argv[1], argv[2])
    if len(argv) >= 4 and argv[0] == "compare":
        rnd = int(argv[argv.index("--round") + 1]) if "--round" in argv else 1
        return cmd_compare(argv[1], argv[2], argv[3], rnd)
    if argv and argv[0] == "summary":
        cmd_summary(); return 0
    print(__doc__); return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
