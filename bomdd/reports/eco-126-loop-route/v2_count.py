"""ECO-126 V2 — the count. Transcribes the 2026-11-17 table of MoviePad ECO-006 into the loop record form, runs loop-count
on it, and compares its numbers with a tally taken straight from the table.

usage: v2_count.py                 (from anywhere: the table and the output folder are beside this script)
       v2_count.py <BomDD root> <findings.tsv> <out dir>      (the older form; the table must still have TABLE_SHA256)
Writes <out dir>/eco-006.loop.yaml. Exits 1 if any expectation fails.

The table (`v2/findings.tsv`, 65 rows) is the fixed input: a byte copy of the count of 2026-11-17
(`bomdd/reports/count-survey-20261110/loop-trial/eco-006/stage-count/findings.tsv`, a folder that is not committed).
The script refuses any other bytes.
"""
import csv
import hashlib
import importlib.util
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TABLE_SHA256 = "67861a0945b7fa2afe5bbdcad9a3e22b1aac6914a38583faccb82a92a4dc8315"
if len(sys.argv) == 4:
    root, tsv, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
elif len(sys.argv) == 1:
    root, tsv, out = HERE.parents[2], HERE / "v2" / "findings.tsv", HERE / "v2"
else:
    sys.exit("usage: v2_count.py   |   v2_count.py <BomDD root> <findings.tsv> <out dir>")
tool = root / "method" / "tools" / "loop-count.py"
spec = importlib.util.spec_from_file_location("loop_count", tool)
lc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lc)
bad = []


def expect(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + (" — " + detail if detail else ""))
    if not ok:
        bad.append(label)


raw = tsv.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
expect("the table is the fixed input (sha256)", sha == TABLE_SHA256, f"{tsv.name}: {sha[:8]}…{sha[-8:]}, {len(raw)} bytes")
if sha != TABLE_SHA256:
    print("V2: the table is not the fixed input — nothing else was run")
    sys.exit(1)
rows = list(csv.DictReader(raw.decode("utf-8").splitlines(), delimiter="\t"))
SRC = {"orchestrator": "producer", "reader": "reader", "maker": "maker"}

# --- the record (rounds, reactions and reports are from MoviePad's order of ECO-006; the items are the table's rows) ---
L = [f"schema: {lc.SCHEMA}", "eco: ECO-006", "product: MoviePad", f"source_table_sha256: {sha}", 'limits: {rounds: 5, budget: "1.5M tokens for other sessions"}', "rounds:",
     "  - n: 1",
     "    set: {commit: b84cedd, jig: ce3520a98558e382, files: {MoviePad.dll: 5ae0b02f8f20b0c1}}",
     '    handed_at: "2026-11-13T21:19:50Z"',
     "    launches: unknown",
     "    reply: {words: 使いやすくなりました。}",
     "    repairs: {fixed_after_reproduction: 0, patched_without_reproduction: 0}",
     "    checks_replaced: 0",
     "    reasks: 0",
     "  - n: 2",
     "    set: {commit: 5ab2031, jig: none, files: {MoviePad.dll: 61eac4f1c8c7f446}}",
     '    handed_at: "2026-11-14T06:47:51Z"',
     "    launches: unknown",
     "    reply: {words: 全部合格}",
     "    repairs: {fixed_after_reproduction: 0, patched_without_reproduction: 0}",
     "    checks_replaced: 1",
     "    reasks: 1",
     "items:"]
for r in rows:
    f = [f"id: {r['id']}", f"round: {r['turn']}", f"source: {SRC[r['source']]}", f"kind: {r['kind']}", f"subject: {r['subject']}",
         f"disposition: {r['disp']}", f"outcome: {r['outcome']}"]
    if r["parent"]:
        f.append(f"about: {r['parent']}")
    if r["channel"]:
        f.append(f'channel: "{r["channel"]}"')
    L.append("  - {" + ", ".join(f) + "}")
L += ["reactions:",
      "  - {id: X1, round: 1, words: 使いやすくなりました。, kind: pass, kind_by: reading, class: none}",
      "  - {id: X2, round: 1, words: \"H3. ほとんどの時間、ゆっくりが表示される。ゆっくり判定が厳しい可能性\", kind: pass_but, kind_by: user, "
      "class: decision_change, lands_on: [P-R20], listed_before_use: yes}",
      "  - {id: X3, round: 2, words: 全部合格, kind: pass, kind_by: user, class: none}",
      "reports:",
      '  - {id: U-1, accepted: yes, named_in: "A: 受け入れる"}',
      '  - {id: U-2, accepted: yes, named_in: "A: 受け入れる"}',
      '  - {id: U-3, accepted: yes, named_in: "A: 受け入れる"}',
      "  - {id: U-4, accepted: dropped}"]
out.mkdir(parents=True, exist_ok=True)
rec = out / "eco-006.loop.yaml"
rec.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")

# --- 1. the complete record passes --check ---
p = subprocess.run([sys.executable, str(tool), "--check", str(rec)], capture_output=True, text=True, encoding="utf-8", errors="replace")
(out / "v2-loop-count-eco-006.txt").write_text(p.stdout, encoding="utf-8", newline="\n")
expect("the transcribed record passes --check", p.returncode == 0 and "gaps: 0" in p.stdout, f"exit {p.returncode}")

# --- 2. the tool's numbers equal a tally taken straight from the table ---
t = lc.tally(lc.load(str(rec)))
direct = {s: Counter(r["disp"] for r in rows if SRC[r["source"]] == s) for s in lc.SOURCES}
expect("rows and subjects", (t["rows"], t["subjects"]) == (65, 51) == (len(rows), len({r["subject"] for r in rows})),
       f"{t['rows']} rows, {t['subjects']} subjects")
expect("disposition by source equals the table", all(dict(t["by_src"][s]) == dict(direct[s]) for s in lc.SOURCES),
       " / ".join(f"{s} {dict(sorted(direct[s].items()))}" for s in lc.SOURCES))
direct_out = {s: Counter((r["disp"], r["outcome"]) for r in rows if SRC[r["source"]] == s) for s in lc.SOURCES}
expect("outcome by disposition equals the table", all(dict(t["outcome"][s]) == dict(direct_out[s]) for s in lc.SOURCES))
expect("asked of the user: producer 8/10, reader 15/33, maker 5/22",
       [(t["asked"][s], sum(t["by_src"][s].values())) for s in lc.SOURCES] == [(8, 10), (15, 33), (5, 22)],
       str([(t["asked"][s], sum(t["by_src"][s].values())) for s in lc.SOURCES]))
expect("the one difference lands on a producer's decision that was listed before use",
       t["causes"] == [("X2", "P-R20", "producer", "yes")], str(t["causes"]))
expect("kinds: one assigned by the producer's reading, two by the user",
       dict(t["reaction_kinds"]) == {("pass", "reading"): 1, ("pass_but", "user"): 1, ("pass", "user"): 1})

# --- 3. known-bad on the real record: each mutation makes --check exit 1 for its own reason ---
text = rec.read_text(encoding="utf-8")
MUT = [("a reaction with no kind", "kind: pass_but, ", "", "種類(kind)"),
       # (the jig field is kept: since the repair a round with no `set` at all has two gaps — the set and the jig field)
       ("a round with no commit and no files", "    set: {commit: 5ab2031, jig: none, files: {MoviePad.dll: 61eac4f1c8c7f446}}\n",
        "    set: {jig: none}\n", "版の組"),
       ("an accepted report with no naming reply", '  - {id: U-2, accepted: yes, named_in: "A: 受け入れる"}', "  - {id: U-2, accepted: yes}",
        "named_in"),
       ("an item with no disposition", "disposition: to_user_report, outcome: diff", "outcome: diff", "行き先"),
       # the rules --check reads since the repair of 2026-11-17 (they were declared as not checked before)
       ("a reply with no reaction row", "  - {id: X3, round: 2, words: 全部合格, kind: pass, kind_by: user, class: none}\n", "",
        "反応の行が 1 つも無い"),
       ("no budget", ', budget: "1.5M tokens for other sessions"', "", "費用の枠"),
       ("a round with no jig field", "jig: none, ", "", "治具の欄"),
       ("a reply with no launches field", "    launches: unknown\n    reply: {words: 全部合格}", "    reply: {words: 全部合格}", "launches が無い"),
       ("an item whose round is not a round", "{id: P-R20, round: 1,", "{id: P-R20, round: 9,", "round が rounds に無い")]
for label, old, new, must in MUT:
    assert text.count(old) == 1, label
    m = out / "mutant.yaml"
    m.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
    q = subprocess.run([sys.executable, str(tool), "--check", str(m)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    expect(f"known-bad: {label}", q.returncode == 1 and must in q.stdout and q.stdout.count("[gap]") == 1,
           f"exit {q.returncode}, gaps {q.stdout.count('[gap]')}")
    m.unlink()

print("note: the 65 item rows come from the table. The rounds, the three reactions and the four reports are entered by hand in this")
print("      script from MoviePad's order; the lines about them show that the tool reports what was entered, not that the entry is right.")
print(f"V2 (table sha256 {sha[:8]}…{sha[-8:]}):", "FAILED " + str(bad) if bad else "all as expected")
sys.exit(1 if bad else 0)
