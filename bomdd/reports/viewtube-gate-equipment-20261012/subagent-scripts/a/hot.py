import io, re, subprocess, sys, time
import yaml
root = r"C:\Users\akira\source\repos\ViewTube"
sys.path.insert(0, root + r"\bomdd\tools")
import validate_record_language as rl
import validate_process as vp

text = io.open(root + r"\bomdd\process\change-register.yaml", encoding="utf-8", newline="").read()
doc = yaml.load(text, Loader=yaml.CSafeLoader)
ids = [e["id"] for e in doc["changes"]]

t0 = time.perf_counter()
old = {eco: rl.entry_text(text, eco) for eco in ids}
t1 = time.perf_counter()
marks = [(m.start(), m.group(1)) for m in re.finditer(r"^[ \t]*- id: (ECO-VT-\d+)", text, re.M)]
new = {}
for i, (pos, name) in enumerate(marks):
    if name not in new:
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        new[name] = text[pos:end]
newd = {eco: new.get(eco, "") for eco in ids}
t2 = time.perf_counter()
print("entry_text x%d: %.2fs ; single pass: %.3fs ; identical=%s" % (len(ids), t1 - t0, t2 - t1, old == newd))

out = subprocess.run(["git", "log", "--format=%x00%B%x00", "--fixed-strings", "--grep=BomDD-ECO-"],
                     cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
messages = out.split("\0")[1::2]
keys = ["BomDD-ECO-Fix", "BomDD-ECO-Accept"]
t0 = time.perf_counter()
res_old = {(k, e): any(e in vp._trailer_values(m, k) for m in messages) for k in keys for e in ids[:104]}
t1 = time.perf_counter()
cache = {k: set(v for m in messages for v in vp._trailer_values(m, k)) for k in keys}
res_new = {(k, e): e in cache[k] for k in keys for e in ids[:104]}
t2 = time.perf_counter()
print("messages", len(messages), "history_has 208 lookups: %.2fs ; precomputed: %.3fs ; identical=%s" % (t1 - t0, t2 - t1, res_old == res_new))

b = subprocess.run(["git", "show", "6c39638:bomdd/process/change-register.yaml"], cwd=root, capture_output=True).stdout
b2 = subprocess.run(["git", "show", "6c39638~1:bomdd/process/change-register.yaml"], cwd=root, capture_output=True).stdout
t0 = time.perf_counter(); yaml.safe_load(b.decode()); yaml.safe_load(b2.decode()); t1 = time.perf_counter()
print("historic register blobs bytes", len(b), len(b2), "pure parse both %.2fs" % (t1 - t0))
