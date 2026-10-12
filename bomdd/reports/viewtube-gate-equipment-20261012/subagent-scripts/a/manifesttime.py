import time, glob, os
import yaml
root = r"C:\Users\akira\source\repos\ViewTube"
reg = yaml.load(open(os.path.join(root, r"bomdd\process\change-register.yaml"), encoding="utf-8").read(), Loader=yaml.CSafeLoader)
active = [e for e in reg["changes"] if isinstance(e, dict)]
from collections import Counter
print("status counts", Counter(e.get("status") for e in active))
files = sorted(glob.glob(os.path.join(root, r"bomdd\process\change-impact\*.yaml")))
texts = [open(f, encoding="utf-8").read() for f in files]
print("manifests", len(files), "bytes", sum(len(t) for t in texts))
t0 = time.perf_counter()
a = [yaml.safe_load(t) for t in texts]
t1 = time.perf_counter()
b = [yaml.load(t, Loader=yaml.CSafeLoader) for t in texts]
t2 = time.perf_counter()
print("pure", round(t1 - t0, 2), "C", round(t2 - t1, 2), "equal", a == b)
