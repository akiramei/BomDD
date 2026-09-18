"""EXP-20260918-01 — Jev 設備認定 第 1 回(receipt の実在: 意味判定の感度試験)。

検体= self-conformance の C17 fixture 18 本・C16 fixture 17 本(ラベル= fixture の want_ok から導出した
「receipt が実質として存在するか」・Jev から独立)+病的 receipt 1 本+実検体(order の節)7 本。
腕= ja(原文)/ en(当方訳・fixture のみ)/ real(実検体・ja のみ)。
質問= Noul 1 問(固定)。閾値 0.5(事前宣言)・拮抗帯 0.4〜0.6。
出力= bomdd/reports/jev-qualification-01/results.jsonl(追記・生の answer・state の sha256・model・usage)。
鍵= C:/Users/akira/.typesafe/api_key(表示しない)。
"""
import argparse, hashlib, importlib.util, json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve()
for p in ROOT.parents:
    if (p / "bomdd" / "60-change-register.yaml").is_file():
        ROOT = p
        break
else:
    ROOT = Path.cwd()
OUT_DIR = ROOT / "bomdd" / "reports" / "jev-qualification-01"
KEY_FILE = Path("C:/Users/akira/.typesafe/api_key")
MODEL = "jev-latest"
THRESHOLD = 0.5

QUESTION_INSTRUCTIONS = (
    "The `section` field contains one section of a change-order document (Japanese or English). "
    "Does this section report the results of an assessment (a calibration receipt or convergence receipt) "
    "that was actually carried out? Answer no if the section is only a format example or template, a note "
    "that the receipt was omitted or exempted, a statement that the receipt will be written later, a plan of "
    "what will be checked, or an unrelated section."
)
QUESTION_CRITERIA = {
    "true": "The section presents findings of an assessment that has been performed (judgments, detected defects, "
            "limits, or round-by-round results stated as done).",
    "false": "No performed assessment is reported: the text is a template or example, a mention of omission or "
             "exemption, a future plan, a placeholder, or unrelated content.",
}

# ---- fixture の英訳(当方訳・意味を保つ最小の訳。原文の構造〔fence・見出し・HTML コメント〕は保持) ----
EN_C17 = {
    "F1": "## Addendum: post-hoc calibration receipt\n- Claims assessed and verdicts…\n",
    "F2": "## Acceptance\n- V1 PASS\n",
    "F3": "## Acceptance\n- under consideration\n",
    "F4": "<!-- calibrate: not-required reason: administrative close only decided-by: maintainer -->\n",
    "F5": "```\n<!-- calibrate: not-required reason: x decided-by: y -->\n```\n",
    "F6": "<!-- calibrate: not-required reason:  decided-by: maintainer -->\n",
    "F7": "```\n### calibration receipt (format example)\n- Claims assessed and verdicts…\n```\n",
    "F8": "## Acceptance\n- V1 PASS\n\nThe calibration receipt was omitted this time.\n",
    "F9": "### calibration receipt (trigger 1)\n- Claims assessed and verdicts…\n",
    "F10": "~~~\n### calibration receipt\n- Claims assessed and verdicts / instrument defects / limits of detection / asked\n~~~\n",
    "F11": "    <!-- calibrate: not-required reason: example decided-by: nobody -->\n",
    "F12": "## The calibration receipt was omitted\n",
    "F13": "##calibration receipt\n- Claims assessed and verdicts / instrument defects / limits of detection / asked\n",
    "F14": "####### calibrate receipt\n- Claims assessed and verdicts / instrument defects / limits of detection / asked\n",
    "F15": "## calibrate receiptless notes\n- Claims assessed and verdicts / instrument defects / limits of detection / asked\n",
    "F16": "### calibration receipt\n\n## Next section\n",
    "F17": "### calibration receipt (trigger 1)\n- Claims assessed and verdicts: …\n- Instrument defects detected: none\n"
           "- Limits of detection: …\n| Q1 | asked | … |\n",
    "F18": "## Acceptance\n",
}
EN_C16 = {
    "F1": "## Remaining gate\nThe human designates candidate A-1 or candidate A-2.\n",
    "F2": "## Remaining gate\nChoose from candidate A-1 / candidate A-2.\n"
          "## /converge receipt\n- rounds: round 1 = 2 findings / round 2 = 0 findings\n- unresolved items: none\n",
    "F3": "## Record\nTransitioned the ledger status from filed to applied. The diff is one line.\n",
    "F4": "## Checking sources\nRead the sources of the 3 examples and cross-checked their content.\n"
          "## Verdict\nPlease decide among option A (recommended) / option B / option C.\n",
    "F5": "<!-- converge: not-required -->\n## Remaining gate\nCandidate B-1 (recommended) / candidate B-2.\n",
    "F6": "<!-- converge: not-required reason: bookkeeping only -->\n## Remaining gate\nCandidate B-1 (recommended).\n",
    "F7": "<!-- converge: not-required reason: bookkeeping only, no decision candidates decided-by: maintainer -->\n"
          "## Remaining gate\nCandidate B-1 (recommended) / candidate B-2.\n",
    "F8": "<!-- converge: not-required reason:  decided-by: maintainer -->\n## Remaining gate\nCandidate B-1 (recommended).\n",
    "F9": "The declaration format is as follows.\n\n```\n"
          "<!-- converge: not-required reason: <why out of scope> decided-by: <who declared> -->\n```\n\n"
          "## Remaining gate\nCandidate B-1 (recommended).\n",
    "F10": "## Remaining gate\nCandidate A-1 (recommended).\n```\n## /converge receipt\n- round 1\n- unresolved items: none\n```\n",
    "F11": "## Remaining gate\nCandidate A-1 (recommended).\n```\n## /converge receipt\n- round 1\n- unresolved items: none\n",
    "F12": "## Remaining gate\nCandidate A-1 (recommended).\n~~~\n## convergence receipt\n- verdict: converged / trigger path: self-initiated / round 1 / unresolved items: none / DoD ✔\n~~~\n",
    "F13": "## Remaining gate\nCandidate A-1 (recommended).\nThe convergence receipt was omitted this time. Round 1 was not performed; still unconverged.\n",
    "F14": "## Remaining gate\nCandidate A-1 (recommended).\n## /converge receipt\n- round 1 = 2 findings\n- unresolved items: none\n",
    "F15": "    <!-- converge: not-required reason: example decided-by: nobody -->\n## Remaining gate\nCandidate B-1 (recommended).\n",
    "F16": "## Remaining gate\nCandidate A-1 (recommended).\n## /converge receipt\n- verdict: converged (round trajectory: 2→0→0)\n- unresolved items: none\n",
    "F17": "## Remaining gate\nCandidate A-1 (recommended).\n## /converge receipt\n- verdict: converged (round trajectory: 2→0→0)\n"
           "- trigger path: self-initiated\n- unresolved items: none\n- DoD: anchor ✔ / implementation target ✔\n",
}
# ラベル(receipt が実質として存在する= true)。fixture の want_ok は「gate が通るか」なので、
# 「status が対象外」「根拠つき免除」で通る fixture は receipt 不在(false)に写像する。
C17_POSITIVE = {"F1", "F9", "F17"}
C16_POSITIVE = {"F2", "F14", "F16", "F17"}   # F14: 見出し+round 行はあるが判定/DoD 欠落 — 実施済みの round 報告ではある(様式違反≠不在)
C16_POSITIVE_NOTE = "F14 は C16 では様式違反で FAIL だが、意味上は『round 1 = 2 件』という実施報告なので positive に置く(事前宣言)"

PATHOLOGICAL = ("P1", False, "見出し内の否定+本体ラベル完備(C17 限界 (5)・機械は通す)",
                "## 較正 receipt は省略した\n- 査定した主張と判定: (今回は査定していない)\n- 検出した計器欠陥: —\n- 検出力の限界: —\n| Q1 | asked | — |\n")


def load_selfconf():
    spec = importlib.util.spec_from_file_location("sc", str(ROOT / "method" / "tools" / "self-conformance.py"))
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
    return sc


def slice_lines(text: str, start_pat: str, end_pat: str | None) -> str:
    lines = text.splitlines()
    s = next(i for i, l in enumerate(lines) if l.startswith(start_pat))
    if end_pat is None:
        return "\n".join(lines[s:]) + "\n"
    e = next(i for i in range(s + 1, len(lines)) if lines[i].startswith(end_pat))
    return "\n".join(lines[s:e]) + "\n"


def real_specimens():
    o71 = (ROOT / "bomdd/60-change-order-eco-071.md").read_text(encoding="utf-8")
    o75 = (ROOT / "bomdd/60-change-order-eco-075.md").read_text(encoding="utf-8")
    o76 = (ROOT / "bomdd/60-change-order-eco-076.md").read_text(encoding="utf-8")
    o76_pre = subprocess.run(["git", "show", "cea4b41:bomdd/60-change-order-eco-076.md"], cwd=ROOT,
                             capture_output=True, text=True, encoding="utf-8").stdout
    return [
        ("R1", True, "ECO-071 較正 receipt(実施済み)", "verified", slice_lines(o71, "### 較正 receipt", None)),
        ("R2", True, "ECO-075 較正 receipt(実施済み)", "verified", slice_lines(o75, "### 較正 receipt", None)),
        ("R3", True, "ECO-076 較正 receipt(実施済み)", "verified", slice_lines(o76, "### 較正 receipt", None)),
        ("R4", True, "ECO-076 §4 製造と受入の実測(実測結果・receipt 様式ではない)", "verified", slice_lines(o76, "## 4. 製造と受入の実測", "## 5.")),
        ("R5", False, "ECO-076 §3 受入(計画)", "filed", slice_lines(o76, "## 3. 受入", "## /preflight")),
        ("R6", False, "ECO-075 §3 受入(候補・計画)", "filed", slice_lines(o75, "## 3. 受入(候補)", "## 3b.")),
        ("R7", False, "ECO-076 §5 製造 commit 時点(未記入の placeholder)", "implemented", slice_lines(o76_pre, "## 5. クローズ", None)),
    ]


def build(arms):
    sc = load_selfconf()
    specs = []
    if "ja" in arms or "en" in arms:
        for name, want_ok, desc, st, txt, eco in sc._C17_FIXTURES:
            lab = name in C17_POSITIVE
            if "ja" in arms:
                specs.append(dict(id=f"C17-{name}", arm="ja", label=lab, desc=desc, status=st, want_ok=want_ok, text=txt))
            if "en" in arms:
                specs.append(dict(id=f"C17-{name}", arm="en", label=lab, desc=desc, status=st, want_ok=want_ok, text=EN_C17[name]))
        for fx in sc._CONVERGE_FIXTURES:
            name, want_ok, desc, txt = fx[:4]
            lab = name in C16_POSITIVE
            if "ja" in arms:
                specs.append(dict(id=f"C16-{name}", arm="ja", label=lab, desc=desc, status="n/a", want_ok=want_ok, text=txt))
            if "en" in arms:
                specs.append(dict(id=f"C16-{name}", arm="en", label=lab, desc=desc, status="n/a", want_ok=want_ok, text=EN_C16[name]))
        if "ja" in arms:
            n, lab, d, t = PATHOLOGICAL
            specs.append(dict(id=n, arm="ja", label=lab, desc=d, status="verified", want_ok=True, text=t))
    if "real" in arms:
        for n, lab, d, st, t in real_specimens():
            specs.append(dict(id=n, arm="real", label=lab, desc=d, status=st, want_ok=None, text=t))
    return specs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="ja,en,real")
    ap.add_argument("--dry", action="store_true", help="最初の 1 検体だけ送る")
    ap.add_argument("--list", action="store_true", help="送らずに検体一覧だけ")
    a = ap.parse_args()
    arms = set(a.arms.split(","))
    specs = build(arms)
    if a.list:
        for s in specs:
            print(s["id"], s["arm"], "POS" if s["label"] else "neg", len(s["text"]), s["desc"][:50])
        print("total", len(specs), "positives", sum(s["label"] for s in specs))
        return 0
    if a.dry:
        specs = specs[:1]

    from typesafe_sdk import Noul, TypeSafeClient, TypeSafeAuthenticationError, TypeSafeError
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        print("UNMEASURABLE: key file empty"); return 2
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / ("results-dry.jsonl" if a.dry else "results.jsonl")
    q = {"receipt_reported": Noul(instructions=QUESTION_INSTRUCTIONS, criteria=QUESTION_CRITERIA)}
    n_ok = n_err = 0
    with TypeSafeClient(api_key=key, model=MODEL) as client, out.open("a", encoding="utf-8") as fh:
        for s in specs:
            state = {"section": s["text"], "context": f"One section of a change-order document. Ledger status of the change: {s['status']}."}
            sha = hashlib.sha256(json.dumps(state, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
            rec = dict(ts=datetime.now(timezone.utc).isoformat(timespec="seconds"), id=s["id"], arm=s["arm"], label=s["label"],
                       desc=s["desc"], status=s["status"], want_ok=s["want_ok"], state_sha256=sha, chars=len(s["text"]))
            try:
                r = client.system_one(state=state, questions=q)
                p = r.answers["receipt_reported"].noul
                rec.update(model=r.model, p=p, usage=dict(input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens),
                           pred=p >= THRESHOLD, correct=(p >= THRESHOLD) == s["label"], band="ambiguous" if 0.4 <= p <= 0.6 else "clear")
                n_ok += 1
                print(f"{s['id']:8} {s['arm']:4} label={'POS' if s['label'] else 'neg'} p={p:.3f} {'ok ' if rec['correct'] else 'MISS'} {rec['band']}")
            except TypeSafeAuthenticationError as e:
                rec.update(error="AUTH", error_class=type(e).__name__); n_err += 1
                print(f"{s['id']:8} UNMEASURABLE AUTH ({type(e).__name__})"); fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); break
            except TypeSafeError as e:
                rec.update(error="API", error_class=type(e).__name__, error_msg=str(e)[:200]); n_err += 1
                print(f"{s['id']:8} UNMEASURABLE API ({type(e).__name__}): {str(e)[:120]}")
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            time.sleep(0.2)
    print(f"done: ok={n_ok} err={n_err} -> {out}")
    return 0 if n_err == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
