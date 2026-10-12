import glob, os, time
import yaml
root = r"C:\Users\akira\source\repos\ViewTube\bomdd"
files = glob.glob(os.path.join(root, "**", "*.yaml"), recursive=True) + glob.glob(os.path.join(root, "**", "*.yml"), recursive=True)
same = diff = both_err = one_err = 0
tp = tc = 0.0
bad = []
for f in files:
    try:
        text = open(f, encoding="utf-8").read()
    except Exception:
        continue
    ra = rb = ea = eb = None
    t0 = time.perf_counter()
    try:
        ra = yaml.safe_load(text)
    except Exception as e:
        ea = type(e).__name__
    t1 = time.perf_counter()
    try:
        rb = yaml.load(text, Loader=yaml.CSafeLoader)
    except Exception as e:
        eb = type(e).__name__
    t2 = time.perf_counter()
    tp += t1 - t0; tc += t2 - t1
    if ea or eb:
        if ea and eb:
            both_err += 1
        else:
            one_err += 1; bad.append((f, ea, eb))
    elif ra == rb:
        same += 1
    else:
        diff += 1; bad.append((f, "differs", ""))
print("files", len(files), "same", same, "differ", diff, "both_err", both_err, "one_err", one_err)
print("pure %.1fs C %.1fs" % (tp, tc))
for b in bad[:10]:
    print(b)
