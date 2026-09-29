import re, collections, os
ROOT = r"C:\Users\akira\source\repos\ViewTube"
def norm(s):
    s = s.lower()
    return ("blocking_if_ruled" if "blocking_if_ruled" in s else "blocking" if "blocking" in s
            else "material" if "material" in s else "minor" if "minor" in s else "?")
for n in (178, 179, 180, 181, 182, 183, 184, 185, 188, 190):
    p = os.path.join(ROOT, "bomdd", "process", "change-impact", f"ECO-VT-{n}.yaml")
    if not os.path.exists(p):
        print(f"{n}: manifest absent"); continue
    t = open(p, encoding="utf-8").read()
    m = re.search(r"^independent_review:\n(.*?)(?=^\S|\Z)", t, re.S | re.M)
    blk = m.group(1) if m else ""
    pairs = re.findall(r"^\s*- id: ([^\n]+)\n\s*severity: ([^\n]+)", blk, re.M)
    c = collections.Counter(norm(s) for _, s in pairs)
    rounds = len(re.findall(r"^\s*- round: ", blk, re.M))
    print(f"{n}: review_block_lines={blk.count(chr(10))} rounds_listed={rounds} findings={len(pairs)} "
          f"blocking={c['blocking']} bir={c['blocking_if_ruled']} material={c['material']} minor={c['minor']} other={c['?']}")
    ids = [i for i, _ in pairs]
    if ids:
        print("   ids:", ids[:3], "...", ids[-2:])
