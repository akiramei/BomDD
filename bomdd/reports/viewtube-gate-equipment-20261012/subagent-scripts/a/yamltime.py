import time, sys
import yaml
p = r"C:\Users\akira\source\repos\ViewTube\bomdd\process\change-register.yaml"
t0 = time.perf_counter()
text = open(p, encoding="utf-8").read()
t1 = time.perf_counter()
print("read", round(t1 - t0, 3), "chars", len(text), "lines", text.count("\n"))
print("yaml", yaml.__version__, "has CSafeLoader", hasattr(yaml, "CSafeLoader"))
t0 = time.perf_counter()
a = yaml.safe_load(text)
t1 = time.perf_counter()
print("safe_load (pure)", round(t1 - t0, 2))
if hasattr(yaml, "CSafeLoader"):
    t0 = time.perf_counter()
    b = yaml.load(text, Loader=yaml.CSafeLoader)
    t1 = time.perf_counter()
    print("CSafeLoader", round(t1 - t0, 2), "equal", a == b)
print("entries", len(a.get("changes", [])))
