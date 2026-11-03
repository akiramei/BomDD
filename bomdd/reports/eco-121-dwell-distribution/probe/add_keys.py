"""Add a waiting_on line to one open entry and a top-level paused block to a register copy (text edit, keeps the rest byte-identical)."""
import re
import sys

path, entry_id, value = sys.argv[1], sys.argv[2], sys.argv[3]
data = open(path, "rb").read()
text = data.decode("utf-8")
nl = "\r\n" if "\r\n" in text else "\n"
m = re.search(r"^(\s*)- id: ['\"]?" + re.escape(entry_id) + r"['\"]?\s*$", text, re.M)
if not m:
    sys.exit(f"entry {entry_id} not found")
indent = m.group(1) + "  "
line_end = text.index(nl, m.end() - 1) if not text[m.end() - 1:m.end()] == "\n" else m.end() - 1
insert_at = m.end() + (len(nl) if text[m.end():m.end() + len(nl)] == nl else 0)
text = text[:insert_at] + f"{indent}waiting_on: {value}{nl}" + text[insert_at:]
top = re.search(r"^changes:", text, re.M)
text = text[:top.start()] + f"paused:{nl}  reason: probe for ECO-121 survey{nl}  resume_when: never (scratch copy){nl}" + text[top.start():]
open(path, "wb").write(text.encode("utf-8"))
print("ok", path, entry_id, value)
