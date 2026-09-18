r"""EXP-20260918-01 第 2 回 — Jev 設備認定(計画 / 実施 / 様式 / 省略 の弁別・Choice 4 択・実 order の節を機械抽出)。

設計(結果受領前に固定):
- 検体= bomdd/60-change-order-eco-062..079 の節(## / ### 見出し単位)を見出し規則でラベル付け(Jev から独立・当方の判定を挟まない):
    performed = 「製造と受入の実測」「受入の実測」「Phase 4 実測」「クローズ(…verified…)」「### 較正 receipt」「### r\d / N.n r\d(独立検査 round)」「0. 実測(起票根拠)」
    planned   = 「受入」「受入(…候補…)」「影響なし予測」「製造裁定の候補」
    template  = method/templates/60-change-order.md・61〜64 ワークシートの節
    omitted   = 「クローズ(受入 commit で記録)」(cea4b41 の placeholder)・ECO-034 の免除宣言節・第 1 回 fixture の省略/免除 4 本(C17 F4/F6/F8/F12)
  それ以外の見出し(担当設備・変更要求・製造裁定と製造・製造物・preflight/converge receipt・記録・計画・Phase 5 run 等)は対象外。
- 前処理= code がフェンス(```/~~~)を剥がす(self-conformance _strip_fences と同じ分業)・本文は 6000 字で打ち切り(宣言)。
- state= {section}(台帳 status は渡さない— 第 1 回と異なり本文だけで判定させる)。質問= Choice 4 択(下記 CRITERIA)。
- 判定= choice(最大確率)。confidence < 0.5 は「拮抗」として件数を別掲。
- 認定条件(事前宣言)= ①planned → performed の誤分類 ≤ 10% ②performed の再現率 ≥ 85% ③planned+performed の正答率 ≥ 85%。template / omitted は N が小さいので別掲(条件外)。
- 出力= bomdd/reports/jev-qualification-01/results-02.jsonl(生の answer・state sha256・model・usage)。鍵は表示しない。
"""
import argparse, hashlib, importlib.util, json, re, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve()
for p in ROOT.parents:
    if (p / "bomdd" / "60-change-register.yaml").is_file():
        ROOT = p
        break
else:
    ROOT = Path.cwd()
OUT = ROOT / "bomdd" / "reports" / "jev-qualification-01" / "results-02.jsonl"
KEY_FILE = Path("C:/Users/akira/.typesafe/api_key")
MODEL = "jev-latest"
MAX_CHARS = 6000
ECO_RANGE = range(62, 80)

INSTRUCTIONS = (
    "The `section` field is one section of a change-order document from a software methodology repository "
    "(Japanese, some English terms). Classify what kind of content the section is, judging only by what the text "
    "itself states — not by the heading number and not by whether it looks well written."
)
CRITERIA = {
    "performed": "Reports results of work or assessment that has already been carried out: measurements taken, checks run, "
                 "verdicts given, findings listed, receipts of an assessment recorded (things stated as done, with results).",
    "planned": "Describes what will be checked, verified, predicted, or decided later: acceptance criteria to be tested, "
               "predictions frozen before manufacturing, candidate decisions not yet executed (things stated as intended or expected).",
    "template": "A blank form or format example: generic instructions, angle-bracket placeholders, or field names to be "
                "filled in, not about one specific change.",
    "omitted": "States that the item was omitted, exempted, or is not yet written: an exemption declaration, a note that "
               "the receipt was skipped, or a placeholder saying it will be filled in later.",
}

PERFORMED_RE = re.compile(r"^(?:##\s+\d+\.\s+(?:製造と受入の実測|受入の実測|Phase 4 実測|クローズ\(.*verified)|###\s+較正 receipt|###\s+(?:\d+\.\d+\s+)?r\d|##\s+0\.\s+実測\(起票根拠)")
PLANNED_RE = re.compile(r"^##\s+\d+\.\s+(?:受入(?:\(|$|\s)|影響なし予測|製造裁定の候補)")
FENCE_RE = re.compile(r"^(```|~~~)[^\n]*\n.*?(?:^\1[ \t]*$|\Z)", re.S | re.M)


def strip_fences(t: str) -> str:
    return FENCE_RE.sub("", t)


def sections(text: str):
    """(heading_line, body) を ## / ### 単位で返す。## の本文は次の ## か ### まで(サブ節は別検体)。"""
    lines = text.splitlines()
    idx = [i for i, l in enumerate(lines) if re.match(r"^#{2,3}\s", l)]
    for n, i in enumerate(idx):
        j = idx[n + 1] if n + 1 < len(idx) else len(lines)
        yield lines[i], "\n".join(lines[i:j]) + "\n"


def build():
    specs = []
    for n in ECO_RANGE:
        f = ROOT / f"bomdd/60-change-order-eco-{n:03d}.md"
        if not f.is_file():
            continue
        for head, body in sections(f.read_text(encoding="utf-8")):
            if PERFORMED_RE.search(head):
                lab, sub = "performed", ("s0" if head.startswith("## 0.") else "receipt" if "較正 receipt" in head else "round" if re.search(r"###\s+(?:\d+\.\d+\s+)?r\d", head) else "close/measure")
            elif PLANNED_RE.search(head):
                lab, sub = "planned", "acceptance" if "受入" in head else "prediction" if "影響なし" in head else "candidates"
            else:
                continue
            body_s = strip_fences(body)
            if len(body_s.strip().splitlines()) < 2:
                continue   # 見出しだけの節は除外(判定材料なし)
            specs.append(dict(id=f"ECO-{n:03d}:{head[:40]}", label=lab, sub=sub, text=body_s[:MAX_CHARS]))
    # template
    for tf in ["60-change-order.md", "61-impact-analysis.md", "62-migration-oracle.md", "63-diff-audit.md", "64-part-lineage-reattribution.md"]:
        f = ROOT / "method/templates" / tf
        if not f.is_file():
            continue
        for head, body in sections(f.read_text(encoding="utf-8")):
            body_s = strip_fences(body)
            if len(body_s.strip().splitlines()) < 2:
                continue
            specs.append(dict(id=f"TPL:{tf}:{head[:30]}", label="template", sub="template", text=body_s[:MAX_CHARS]))
    # omitted
    pre = subprocess.run(["git", "show", "cea4b41:bomdd/60-change-order-eco-076.md"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    for head, body in sections(pre):
        if head.startswith("## 5. クローズ(受入 commit で記録)"):
            specs.append(dict(id="OM:eco-076@cea4b41:§5", label="omitted", sub="placeholder", text=strip_fences(body)))
    o34 = (ROOT / "bomdd/60-change-order-eco-034.md").read_text(encoding="utf-8")
    m = re.search(r"^<!-- converge: not-required.*?-->", o34, re.M)
    if m:
        specs.append(dict(id="OM:eco-034:exemption", label="omitted", sub="exemption", text=o34[m.start():m.start() + 600]))
    spec = importlib.util.spec_from_file_location("sc", str(ROOT / "method/tools/self-conformance.py"))
    sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
    for name, want_ok, desc, st, txt, eco in sc._C17_FIXTURES:
        if name in {"F4", "F6", "F8", "F12"}:
            specs.append(dict(id=f"OM:C17-{name}", label="omitted", sub="fixture", text=txt))
    return specs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    specs = build()
    if a.list:
        from collections import Counter
        c = Counter((s["label"], s["sub"]) for s in specs)
        for k, v in sorted(c.items()):
            print(k, v)
        print("total", len(specs), "chars", sum(len(s["text"]) for s in specs))
        return 0
    if a.dry:
        specs = specs[:1]
    from typesafe_sdk import Choice, TypeSafeClient, TypeSafeAuthenticationError, TypeSafeError
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        print("UNMEASURABLE: key file empty"); return 2
    OUT.parent.mkdir(parents=True, exist_ok=True)
    q = {"kind": Choice(instructions=INSTRUCTIONS, criteria=CRITERIA)}
    n_ok = n_err = 0
    with TypeSafeClient(api_key=key, model=MODEL) as client, OUT.open("a", encoding="utf-8") as fh:
        for s in specs:
            state = {"section": s["text"]}
            sha = hashlib.sha256(json.dumps(state, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
            rec = dict(ts=datetime.now(timezone.utc).isoformat(timespec="seconds"), id=s["id"], label=s["label"], sub=s["sub"], state_sha256=sha, chars=len(s["text"]))
            try:
                r = client.system_one(state=state, questions=q)
                ans = r.answers["kind"]
                rec.update(model=r.model, choice=ans.choice, confidence=ans.confidence, probabilities=ans.probabilities,
                           usage=dict(input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens),
                           correct=ans.choice == s["label"], ambiguous=ans.confidence < 0.5)
                n_ok += 1
                print(f"{s['id'][:44]:44} {s['label']:9} -> {ans.choice:9} conf={ans.confidence:.2f} {'ok' if rec['correct'] else 'MISS'}")
            except TypeSafeAuthenticationError as e:
                rec.update(error="AUTH", error_class=type(e).__name__); n_err += 1
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); print("UNMEASURABLE AUTH"); break
            except TypeSafeError as e:
                rec.update(error="API", error_class=type(e).__name__, error_msg=str(e)[:200]); n_err += 1
                print(f"{s['id'][:44]:44} UNMEASURABLE {type(e).__name__}: {str(e)[:100]}")
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            time.sleep(0.2)
    print(f"done: ok={n_ok} err={n_err} -> {OUT}")
    return 0 if n_err == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
