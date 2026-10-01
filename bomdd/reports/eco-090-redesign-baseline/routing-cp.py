"""事後の追加計数(事前登録外): 工程表(34-routing)から参照される CP 行の割合。
参照= 34-routing.yaml の全文に CP 行の ID が字面で現れる(どのキーかは問わない)。"""
import sys, re, os, yaml
sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\akira\source\repos"
CP_ID = re.compile(r"\bCP-[A-Z0-9][A-Z0-9-]*\d\b")
KEYS = re.compile(r"^\s*-?\s*([A-Za-z_]+):.*\bCP-", re.M)
print("| リポ | 33 の CP 行 | 工程表から参照される CP 行 | 参照しているキー |")
print("|---|---|---|---|")
for repo in ["ViewPrism2", "ViewTube", "BomDD-Plm", "TimetableAdv", "BomDD-LibraryLending-Sample",
             "BomDD-Transfer03", "BomDD-UnitConv-Sample"]:
    b = os.path.join(R, repo, "bomdd")
    rt = open(os.path.join(b, "34-routing.yaml"), encoding="utf-8").read()
    try:
        c = yaml.safe_load(open(os.path.join(b, "33-control-plan.yaml"), encoding="utf-8"))
        ids = {x["id"] for x in c["control_plan"]["characteristics"] if isinstance(x, dict)}
    except Exception as e:
        print(f"| {repo} | 測定不能(33 読めない) | - | {sorted(set(KEYS.findall(rt)))} |")
        continue
    hit = ids & set(CP_ID.findall(rt))
    keys = sorted(set(KEYS.findall(rt)))
    print(f"| {repo} | {len(ids)} | {len(hit)}/{len(ids)} | {', '.join(keys) or '-'} |")
