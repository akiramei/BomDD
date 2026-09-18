r"""EXP-20260919-01 — 検体の機械抽出(転記なし)。

第三者が「分かりにくい」と評した AI 文(bad)と、その第三者の書き換え(good)を、
セッション記録(Claude Code transcript jsonl・リポ外)と handoff 正本から**文字列一致で切り出す**。
当方が本文を打ち直さないため、ラベル付けと本文の双方に当方の手が入らない。
出力= specimens/<id>.md と specimens/manifest.json(sha256 完全 64 桁・出典座標・文字数)。
"""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SPEC = HERE / "specimens"
TR = Path("C:/Users/akira/.claude/projects")
T_VT = TR / "C--Users-akira-source-repos-ViewTube" / "a4eadffc-ac51-403d-9193-118238f5f36b.jsonl"
T_B14 = TR / "C--Users-akira-source-repos-BomDD" / "1a2e8a9e-14ec-410d-9c0b-81f8ff7d35d5.jsonl"
T_B18 = TR / "C--Users-akira-source-repos-BomDD" / "f3ee84a6-42ba-4f43-ac3c-c091d4b024ac.jsonl"
T_NOW = TR / "C--Users-akira-source-repos-BomDD" / "ec1b0c29-8a29-4f31-b746-7438e1f3b24e.jsonl"
HANDOFF = ROOT / "method" / "templates" / "product-profile" / "skills" / "handoff.md"


def texts(path, role):
    """transcript の text ブロックを (timestamp, text) で列挙。"""
    out = []
    for line in path.open(encoding="utf-8"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") != role:
            continue
        c = (d.get("message") or {}).get("content")
        if isinstance(c, str):
            out.append((d.get("timestamp", ""), c))
        elif isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "text":
                    out.append((d.get("timestamp", ""), b.get("text", "")))
    return out


def find(path, role, needle):
    hits = [(ts, t) for ts, t in texts(path, role) if needle in t]
    if len(hits) != 1:
        raise SystemExit(f"UNMEASURABLE: {path.name} role={role} needle={needle!r} hits={len(hits)} (expected 1)")
    return hits[0]


def slice_(text, start, end, inclusive=True):
    i = text.index(start)
    j = text.index(end, i) + (len(end) if inclusive else 0)
    return text[i:j]


def main():
    specs = []
    # --- 対 A: ECO-VT-165 probe 報告の 1 段落(2026-09-18)/ 第三者の書き換え(user 転送・2026-09-19)
    ts, t = find(T_VT, "assistant", "本のアーム")
    a_bad = slice_(t, "§10 は「現行の全 step 形", "かぶっているだけです。**")
    specs.append(dict(id="A_bad", pair="A", label="bad", source=f"{T_VT.name} assistant {ts}", text=a_bad))
    ts, t = find(T_NOW, "user", "分かりやすくした書き換え")
    a_good = slice_(t, "§10 では、次の2つを", "表現しているだけです。")
    specs.append(dict(id="A_good", pair="A", label="good", source=f"{T_NOW.name} user {ts}(第三者の書き換え・user 転送)", text=a_good))
    # --- 対 B: 2026-09-14 の DISCUSS(ECO-076 の起票根拠)/ 第三者の圧縮版(user 転送)
    ts, t = find(T_B14, "assistant", "探索収率")
    b_bad = t[t.index("[DISCUSS / COMPLETE]"):].strip()
    specs.append(dict(id="B_bad", pair="B", label="bad", source=f"{T_B14.name} assistant {ts}(commit b2b4540 の元メッセージ)", text=b_bad))
    ts, t = find(T_B18, "user", "私なら全体をこの程度まで圧縮")
    b_good = slice_(t, "[DISCUSS / COMPLETE]", "ファイル変更・起票は行っていません。")
    specs.append(dict(id="B_good", pair="B", label="good", source=f"{T_B18.name} user {ts}(第三者コメント・user 転送)", text=b_good))
    # --- 対 C: B の冒頭 1 文(第三者が名指し)/ 第三者の言い換え
    c_bad = slice_(b_bad, "ただしレビューが「今後見るべき」とした点は", "残り半分が未測定です。")
    specs.append(dict(id="C_bad", pair="C", label="bad", source="B_bad の部分文字列(第三者が名指しした 1 文)", text=c_bad))
    c_good = slice_(t, "「レビューの懸念は2つあります。", "仕組みはありません。」")[1:-1]
    specs.append(dict(id="C_good", pair="C", label="good", source=f"{T_B18.name} user {ts}(第三者の言い換え)", text=c_good))
    # --- 観測腕(ラベルなし・認定条件外)
    ts, t = find(T_VT, "assistant", "`ce55fcb` として着地しました")
    specs.append(dict(id="obs_fix_msg", pair="-", label="unlabeled", source=f"{T_VT.name} assistant {ts}(A_bad と同じ書き手・同日の次メッセージ全文)", text=t.strip()))
    h = HANDOFF.read_text(encoding="utf-8")
    ex = slice_(h, "[DISCUSS / PAUSED]", "付録(根拠・返答不要): 件ごとの所見数と反映先= <system of record のパス>")
    ex = ex.replace("[DISCUSS / PAUSED]                    ← 読み手規則の適用例: 結論先行・内部語なし・証拠は付録・問いは 1 点", "[DISCUSS / PAUSED]")
    specs.append(dict(id="obs_handoff_example", pair="-", label="derived_good", source="method/templates/product-profile/skills/handoff.md §3 DISCUSS 例(B_good から派生・独立でない)", text=ex))

    SPEC.mkdir(exist_ok=True)
    manifest = []
    for s in specs:
        (SPEC / f"{s['id']}.md").write_text(s["text"], encoding="utf-8", newline="\n")
        manifest.append(dict(id=s["id"], pair=s["pair"], label=s["label"], source=s["source"], chars=len(s["text"]),
                             sha256=hashlib.sha256(s["text"].encode("utf-8")).hexdigest()))
        print(f"{s['id']:20} {s['label']:13} chars={len(s['text']):5} {s['source']}")
    (SPEC / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
