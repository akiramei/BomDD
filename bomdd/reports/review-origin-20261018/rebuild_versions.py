"""Rebuild the design documents as each review round saw them (step 1 of the review-origin measurement).

Usage: python -B rebuild_versions.py <dir> [--emulate-shell]
  reads  <dir>/primary/{edits.jsonl, reviews.jsonl, file-history.json, file-history/}, <dir>/anchors/, <dir>/round_map.json
  writes <dir>/versions/<ECO>-<round>.md and <dir>/versions.json; with --emulate-shell also <dir>/primary/shell-replays/ (see below)

Anchors (content certain at a time): a Write that succeeded; a Claude Code checkpoint copy (file-history); a git commit (anchors/).
Between anchors the Edits that succeeded are replayed in time order. A shell command that names the document:
  - read-only (no write pattern)                     -> ignored;
  - a write whose replay result is stored under primary/shell-replays/ -> applied (the stored result);
  - otherwise                                        -> the document is marked unconfirmed from then on.
At the next anchor: the replayed content equals the anchor -> every replayed version since the previous anchor is confirmed;
it differs -> the versions since the first unconfirmed point (or since the previous anchor, if none) are UNKNOWN. An Edit whose old text is
not in the replayed content makes the content UNKNOWN until the next anchor. After the last anchor, versions are confirmed only if no
unconfirmed point follows. The version a round reviewed is the content at its review request.

--emulate-shell (machine-dependent; run once, on the machine that holds the session's scratch files): a write segment of the shell command
(sed -i, a python script or `python -c` given the document, printf/cat redirected into it, cp from another tracked document) is re-run by
bash on a temporary copy, and the resulting content is stored as primary/shell-replays/<seq>-<key>.md with an index entry. Later runs
without the flag use the stored results, so a third party re-measures without the scratch files. A wrong replay cannot pass silently:
it is caught at the next anchor, and the versions in between read UNKNOWN.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

D = Path(sys.argv[1])
EMULATE = "--emulate-shell" in sys.argv
# --drop-edit N: the positive control — leave out edit #N; the anchors must then turn the affected versions UNKNOWN
DROP = int(sys.argv[sys.argv.index("--drop-edit") + 1]) if "--drop-edit" in sys.argv else None
SCRATCH = "C:/Users/akira/AppData/Local/Temp/claude/C--Users-akira-source-repos-BomDD/98c0182d-ade5-422d-ac43-d4b21ef32d72/scratchpad"
REPO = "C:/Users/akira/source/repos/BomDD"
PATHS = {"112": ["bomdd/60-change-order-eco-112.md", f"{REPO}/bomdd/60-change-order-eco-112.md"],
         "113": ["bomdd/60-change-order-eco-113.md", f"{REPO}/bomdd/60-change-order-eco-113.md"],
         "113s": [f"{SCRATCH}/eco113/60-change-order-eco-113.md", f'"$S/eco113/60-change-order-eco-113.md"']}
WRITE_RE = re.compile(r"sed -i|>>|>\s*\"?[^ >]*60-change-order|python[^\n|]*\.py[^\n|]*60-change-order|open\([^)]*['\"]w|write_text|\bcp\b")


def doc_key(path):
    p = (path or "").replace("\\", "/")
    if p.endswith("eco113/60-change-order-eco-113.md") and "scratchpad" in p:
        return "113s"
    if "scratchpad" in p:
        return None
    if p.endswith("60-change-order-eco-112.md"):
        return "112"
    if p.endswith("60-change-order-eco-113.md"):
        return "113"
    return None


def touches(cmd, k):
    c = cmd.replace("\\", "/")
    if k == "113s":
        return "eco113/60-change-order-eco-113.md" in c or ("scratchpad/eco113" in c and "60-change-order-eco-113.md" in c)
    return f"bomdd/60-change-order-eco-{k}.md" in c


edits = [json.loads(ln) for ln in (D / "primary" / "edits.jsonl").open(encoding="utf-8")]
fh = json.loads((D / "primary" / "file-history.json").read_text(encoding="utf-8"))
anchors = json.loads((D / "anchors" / "index.json").read_text(encoding="utf-8"))
SR = D / "primary" / "shell-replays"
sr_index_p = SR / "index.json"
sr_index = json.loads(sr_index_p.read_text(encoding="utf-8")) if sr_index_p.exists() else {}
FAILURES = []   # shell writes that could not be re-run (recorded, not guessed)


def split_segments(cmd):
    """Split a shell command at top-level &&, || and ; and newlines (outside quotes and heredocs)."""
    segs, cur, q, i = [], [], None, 0
    heredoc = None
    lines_mode = False
    while i < len(cmd):
        ch = cmd[i]
        if heredoc:
            cur.append(ch)
            if cmd.startswith("\n" + heredoc, i) and (i + 1 + len(heredoc) == len(cmd) or cmd[i + 1 + len(heredoc)] in "\n "):
                cur.append(cmd[i + 1:i + 1 + len(heredoc)])
                i += 1 + len(heredoc)
                heredoc = None
                continue
            i += 1
            continue
        if q:
            cur.append(ch)
            if ch == q and (q == "'" or cmd[i - 1] != "\\"):
                q = None
        elif ch in "'\"":
            q = ch
            cur.append(ch)
        elif cmd.startswith("<<", i):
            m = re.match(r"<<-?\s*['\"]?(\w+)['\"]?", cmd[i:])
            if m:
                heredoc = m.group(1)
                cur.append(m.group(0))
                i += len(m.group(0))
                continue
            cur.append(ch)
        elif cmd.startswith("&&", i) or cmd.startswith("||", i):
            segs.append("".join(cur))
            cur = []
            i += 2
            continue
        elif ch in ";\n" and not (ch == "\n" and cur and cur[-1] == "\\"):
            segs.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    segs.append("".join(cur))
    return [s.replace("\\\n", " ") for s in segs if s.strip()]


def emulate(e, k, content, state_of):
    """Re-run the write segments of shell command e on a temporary copy of the document; None if not possible."""
    cmd = e["payload"]
    m = re.match(r"\s*(?:S=\"[^\"]*\"\s*(?:&&|;)\s*)?cp\s+(\S+)\s+(\S+)\s*(?:&&|;|$)", cmd)
    tmp = Path(tempfile.mkdtemp(prefix="rebuild-"))
    try:
        doc = tmp / "bomdd" / Path(PATHS[k][0]).name
        doc.parent.mkdir(parents=True)
        doc.write_bytes(content.encode("utf-8"))
        target = str(doc).replace("\\", "/")
        script = cmd.replace("\\", "/") if "\\" in cmd and "C:\\" in cmd else cmd
        for p in sorted(PATHS[k], key=len, reverse=True):   # the absolute forms first: the relative form is inside them
            script = script.replace(p, f'"{target}"' if p.startswith('"') else target)
        if k == "113s":
            script = re.sub(r"(?<![/\w-])60-change-order-eco-113\.md", target, script)
        # keep only the segments that set a variable, change directory, or name the temporary copy; drop the rest (other files, checks)
        keep = []
        segs = [s.strip() for s in split_segments(script)]
        f_is_target = any(re.match(r"^(export\s+)?f=", s) and target in s for s in segs)
        for s in segs:
            if re.match(r"^(export\s+)?[A-Za-z_]\w*=", s) and " " not in s.split("=", 1)[1].strip().strip('"'):
                keep.append(s)
            elif s.startswith("cd ") or target in s or (f_is_target and "$f" in s):
                keep.append(s)
        script = " && ".join(keep)
        # refuse anything that could act outside the temporary copy: git, removal, moves, the repository by absolute path
        if not script or re.search(r"\bgit\b|\brm\b|\bmv\b|/c/Users/akira/source|C:/Users/akira/source|cd \.\.", script):
            return None
        r = subprocess.run(["bash", "-c", script], cwd=str(tmp), capture_output=True, timeout=120,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        out = doc.read_bytes().decode("utf-8")
        if out == content and r.returncode != 0:
            FAILURES.append({"seq": e["seq"], "ts": e["ts"], "key": k, "exit": r.returncode,
                             "stderr": r.stderr.decode("utf-8", errors="replace")[-600:], "script": script[:600]})
            return None
        return out
    except Exception as x:
        FAILURES.append({"seq": e["seq"], "ts": e["ts"], "key": k, "error": repr(x)})
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


events = defaultdict(list)
# A checkpoint copy is taken just before the first Write/Edit of the file after a snapshot, and holds the content before that call; its
# backup time is a moment after that call's own timestamp. So it is placed just before the latest Write/Edit of the same document that
# precedes it by at most 5 seconds (the triggering call), or at its own time when there is none.
doc_calls = defaultdict(list)
for e in edits:
    if e["tool"] in ("Write", "Edit") and doc_key(e.get("file_path")):
        doc_calls[doc_key(e.get("file_path"))].append(e["ts"])
for b in fh:
    k = doc_key(b["tracking_path"])
    if k and not b.get("missing"):
        bt = b["backup_time"]
        trig = [t for t in doc_calls[k] if t <= bt]
        at = bt
        if trig:
            from datetime import datetime
            gap = (datetime.fromisoformat(bt.replace("Z", "+00:00")) - datetime.fromisoformat(trig[-1].replace("Z", "+00:00"))).total_seconds()
            if gap <= 5:
                at = trig[-1]
        events[k].append((at, -1, "anchor", {"content": (D / "primary" / b["copied_as"]).read_bytes().decode("utf-8"),
                                             "src": f"checkpoint {b['backup_file']}"}))
for a in anchors:
    events[a["key"]].append((a["ts"], 0, "anchor", {"content": (D / "anchors" / a["file"]).read_bytes().decode("utf-8"), "src": f"git {a['commit'][:7]}"}))
for e in edits:
    failed = bool((e.get("result") or {}).get("is_error"))
    if e["seq"] == DROP:
        continue
    if e["tool"] in ("Write", "Edit") and not failed:
        k = doc_key(e.get("file_path"))
        if k:
            events[k].append((e["ts"], 1, e["tool"].lower(), e))
    elif e["tool"] in ("Bash", "PowerShell"):
        head = (e.get("result") or {}).get("head", "")
        if "PreToolUse" in head and "hook error" in head:   # blocked by a hook before it ran: it changed nothing
            continue
        for k in PATHS:
            if touches(e["payload"], k):
                events[k].append((e["ts"], 1, "shell", e))

timeline = {}
for k, evs in events.items():
    evs.sort(key=lambda x: (x[0], x[1]))
    states, cur, basis, pending, dirty_at = [], None, None, [], None

    def resolve_mismatch():
        for s in pending:
            if dirty_at is None or s["ts"] >= dirty_at:
                s["status"], s["content"] = "unknown", None
            else:
                s["status"] = "confirmed"

    for ts, _, kind, data in evs:
        if kind == "anchor":
            if pending:
                if cur is not None and cur == data["content"]:
                    for s in pending:
                        s["status"] = "confirmed"
                else:
                    resolve_mismatch()
            cur, basis, pending, dirty_at = data["content"], data["src"], [], None
            states.append({"ts": ts, "content": cur, "status": "anchor", "basis": basis})
        elif kind == "write":
            cur, basis, pending, dirty_at = data["payload"], f"write #{data['seq']}", [], None
            states.append({"ts": ts, "content": cur, "status": "anchor", "basis": basis})
        elif kind == "shell":
            if cur is None or not WRITE_RE.search(data["payload"]):
                continue
            key = f"{data['seq']}-{k}"
            res = None
            if key in sr_index and sr_index[key]["before_sha256"] == hashlib.sha256(cur.encode("utf-8")).hexdigest():
                res = (SR / sr_index[key]["file"]).read_bytes().decode("utf-8")
            elif EMULATE:
                res = emulate(data, k, cur, None)
                if res is not None:
                    SR.mkdir(parents=True, exist_ok=True)
                    (SR / f"{key}.md").write_bytes(res.encode("utf-8"))
                    sr_index[key] = {"file": f"{key}.md", "seq": data["seq"], "ts": ts, "key": k,
                                     "before_sha256": hashlib.sha256(cur.encode("utf-8")).hexdigest(),
                                     "after_sha256": hashlib.sha256(res.encode("utf-8")).hexdigest(), "changed": res != cur}
            if res is None:
                if dirty_at is None:
                    dirty_at = ts
                continue
            if res != cur:
                cur = res
                s = {"ts": ts, "content": cur, "status": "pending", "basis": f"{basis} + replay to #{data['seq']} (shell)"}
                states.append(s)
                pending.append(s)
        else:
            if cur is None:
                continue
            old, new = data.get("old_string") or "", data["payload"]
            if old and old in cur:
                cur = cur.replace(old, new) if data.get("replace_all") else cur.replace(old, new, 1)
                s = {"ts": ts, "content": cur, "status": "pending", "basis": f"{basis} + replay to #{data['seq']}"}
                states.append(s)
                pending.append(s)
            else:
                if dirty_at is None:
                    dirty_at = ts
                resolve_mismatch()
                cur, pending, dirty_at = None, [], None
                states.append({"ts": ts, "content": None, "status": "unknown", "basis": f"edit #{data['seq']}: old text not in the replayed content"})
    for s in pending:
        s["status"] = "confirmed" if dirty_at is None or s["ts"] < dirty_at else "unknown"
        if s["status"] == "unknown":
            s["content"] = None
    timeline[k] = states

if EMULATE:
    SR.mkdir(parents=True, exist_ok=True)
    sr_index_p.write_text(json.dumps(sr_index, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (SR / "failures.json").write_text(json.dumps(FAILURES, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

# the version each round reviewed
rmap = json.loads((D / "round_map.json").read_text(encoding="utf-8"))
reviews = [json.loads(ln) for ln in (D / "primary" / "reviews.jsonl").open(encoding="utf-8")]
reqs = defaultdict(list)
reps = defaultdict(list)
for x in reviews:
    if x["kind"] == "request" and not x["text"].lstrip().startswith("<system-reminder>"):
        reqs[x["agent"]].append(x)
    elif x["kind"] == "report":
        reps[x["agent"]].append(x)
(D / "versions").mkdir(exist_ok=True)
out = []
for agent, cfg in rmap.items():
    if agent.startswith("_") or agent == "receipt_counts":
        continue
    rq = sorted(reqs[agent], key=lambda x: x["ts"])
    for label, rep in zip(cfg["rounds"], sorted(reps[agent], key=lambda x: x["ts"])):
        req = max((q for q in rq if q["ts"] <= rep["ts"]), key=lambda q: q["ts"])
        k = "113s" if (cfg["eco"] == "ECO-113" and label.startswith("L5")) else ("112" if cfg["eco"] == "ECO-112" else "113")
        prev = [s for s in timeline.get(k, []) if s["ts"] <= req["ts"]]
        s = prev[-1] if prev else None
        row = {"eco": cfg["eco"], "round": label, "agent": agent, "request_ts": req["ts"], "request_source": req["source"],
               "report_ts": rep["ts"], "document": k}
        if s and s["content"] is not None and s["status"] in ("anchor", "confirmed"):
            fn = f"{cfg['eco']}-{label}.md"
            (D / "versions" / fn).write_bytes(s["content"].encode("utf-8"))
            row.update(file=f"versions/{fn}", sha256=hashlib.sha256(s["content"].encode("utf-8")).hexdigest(), basis=s["basis"], status=s["status"])
        else:
            row.update(file=None, sha256=None, basis=(s or {}).get("basis", "no state before the request"), status="unknown")
        out.append(row)
out.sort(key=lambda r: r["request_ts"])
(D / "versions.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
known = sum(r["file"] is not None for r in out)
print(f"reviewed versions known: {known} / {len(out)}")
for r in out:
    print(f"  {r['eco']} {r['round']:5} {r['status']:9} {r['basis'][:90]}")
