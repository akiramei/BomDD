import subprocess, collections
VT = r"C:\Users\akira\source\repos\ViewTube"
ls = subprocess.run(["git", "-C", VT, "ls-files", "-s", "-z"], capture_output=True).stdout.split(b"\0")
entries = []
for e in ls:
    if not e:
        continue
    meta, path = e.split(b"\t", 1)
    entries.append((meta.split()[1].decode(), path.decode("utf-8", "replace")))
inp = "".join(f"{sha}\n" for sha, _ in entries)
out = subprocess.run(["git", "-C", VT, "cat-file", "--batch-check=%(objectsize)"], input=inp.encode(), capture_output=True).stdout.decode().split()
n = collections.Counter(); s = collections.Counter()
for (sha, path), size in zip(entries, out):
    parts = path.split("/")
    key = "/".join(parts[:2]) if parts[0] in ("bomdd", "tools", "src") and len(parts) > 2 else parts[0]
    n[key] += 1; s[key] += int(size)
print("total files", sum(n.values()), "bytes", sum(s.values()))
for k, v in s.most_common(15):
    print(f"{v/1e6:9.1f} MB {n[k]:6d} files  {k}")
