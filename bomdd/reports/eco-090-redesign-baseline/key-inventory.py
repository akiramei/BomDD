"""7 リポの 30/32/33/34 の構造棚卸し(読み取りのみ)。
各ファイル: 解析可否・トップレベルキー・リスト要素(単位/特性)の候補と、その要素キーの出現数。
"""
import sys, glob, os, collections
import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\akira\source\repos"
REPOS = ["ViewPrism2", "ViewTube", "BomDD-Plm", "TimetableAdv",
         "BomDD-LibraryLending-Sample", "BomDD-Transfer03", "BomDD-UnitConv-Sample"]
LAYERS = ["30-ebom", "32-mbom", "33-control-plan", "34-routing"]


def find_lists(node, path="", out=None):
    """id を持つ dict のリストを全て探す(パス → 要素数)。"""
    if out is None:
        out = {}
    if isinstance(node, dict):
        for k, v in node.items():
            find_lists(v, f"{path}.{k}" if path else str(k), out)
    elif isinstance(node, list):
        ids = [x for x in node if isinstance(x, dict) and ("id" in x or "fmea_id" in x)]
        if ids:
            out[path] = ids
        for i, x in enumerate(node):
            if isinstance(x, (dict, list)):
                find_lists(x, path + "[]", out)
    return out


for repo in REPOS:
    print(f"\n######## {repo}")
    for layer in LAYERS:
        files = sorted(glob.glob(os.path.join(ROOT, repo, "bomdd", layer + "*.yaml")))
        if not files:
            print(f"  {layer}: なし")
            continue
        for f in files:
            rel = os.path.relpath(f, os.path.join(ROOT, repo))
            try:
                with open(f, encoding="utf-8") as fh:
                    docs = list(yaml.safe_load_all(fh))
            except Exception as e:
                print(f"  {rel}: 解析不可 ({type(e).__name__}: {str(e).splitlines()[0][:120]})")
                continue
            docs = [d for d in docs if d is not None]
            print(f"  {rel}: 文書 {len(docs)}")
            for di, d in enumerate(docs):
                if isinstance(d, dict):
                    print(f"    doc{di} top: {list(d.keys())[:15]}")
                lists = find_lists(d)
                for p, items in lists.items():
                    if p.count("[]") > 1:
                        continue
                    kc = collections.Counter(k for it in items for k in it.keys())
                    top = ", ".join(f"{k}:{c}" for k, c in kc.most_common(40))
                    print(f"    list {p} n={len(items)}\n      keys {top}")
