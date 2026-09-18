"""EXP-20260918-01 の集計 — results.jsonl から腕別の指標と検体別表(markdown)を出す。判定閾値 0.5・拮抗帯 0.4〜0.6(事前宣言)。"""
import json, sys
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1 else "bomdd/reports/jev-qualification-01/results.jsonl")
rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
errs = [r for r in rows if "error" in r]
ok = [r for r in rows if "p" in r]
print(f"records={len(rows)} answered={len(ok)} errors={len(errs)} models={sorted({r['model'] for r in ok})}")
tok_in = sum((r.get("usage") or {}).get("input_tokens") or 0 for r in ok)
tok_out = sum((r.get("usage") or {}).get("output_tokens") or 0 for r in ok)
print(f"tokens in={tok_in} out={tok_out}")

print("\n## 腕別指標\n")
print("| 腕 | N | negative 正答(感度: known-bad を弾く) | positive 正答(特異度: 実在を通す) | 拮抗帯 0.4〜0.6 | 誤り検体 |")
print("|---|---|---|---|---|---|")
for arm in ("ja", "en", "real"):
    rs = [r for r in ok if r["arm"] == arm]
    if not rs:
        continue
    neg = [r for r in rs if not r["label"]]
    pos = [r for r in rs if r["label"]]
    neg_ok = sum(1 for r in neg if not r["pred"])
    pos_ok = sum(1 for r in pos if r["pred"])
    amb = sum(1 for r in rs if r["band"] == "ambiguous")
    miss = ", ".join(f"{r['id']}({'P' if r['label'] else 'n'} {r['p']:.2f})" for r in rs if not r["correct"])
    print(f"| {arm} | {len(rs)} | {neg_ok}/{len(neg)} | {pos_ok}/{len(pos)} | {amb} | {miss or 'なし'} |")

print("\n## ja と en の差(同一 fixture)\n")
ja = {r["id"]: r for r in ok if r["arm"] == "ja"}
en = {r["id"]: r for r in ok if r["arm"] == "en"}
diffs = []
for k in ja:
    if k in en:
        diffs.append((k, ja[k]["p"], en[k]["p"], ja[k]["label"]))
big = [d for d in diffs if abs(d[1] - d[2]) >= 0.3]
flip = [d for d in diffs if (d[1] >= 0.5) != (d[2] >= 0.5)]
print(f"対応 {len(diffs)} 本・|Δp|≥0.3= {len(big)}・判定反転= {len(flip)}")
for k, a, b, lab in sorted(flip):
    print(f"  反転 {k} ({'P' if lab else 'n'}): ja={a:.2f} en={b:.2f}")

print("\n## 検体別(ja/en/real)\n")
print("| id | 腕 | ラベル | P | 判定 | 帯 | 説明 |")
print("|---|---|---|---|---|---|---|")
for r in ok:
    print(f"| {r['id']} | {r['arm']} | {'POS' if r['label'] else 'neg'} | {r['p']:.3f} | {'ok' if r['correct'] else '**MISS**'} | {r['band']} | {r['desc'][:60]} |")
for r in errs:
    print(f"| {r['id']} | {r['arm']} | {'POS' if r['label'] else 'neg'} | — | UNMEASURABLE | {r.get('error_class')} | {r['desc'][:60]} |")
