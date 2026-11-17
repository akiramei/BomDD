#!/usr/bin/env python3
"""mutants_tools.py — BomDD ECO-126: which checks of loop-count.py and handover-stamp.py does each tool's own
--selftest notice when the check is removed?

For every entry one check is removed (or one value changed) in a copy of the tool, and the copy's --selftest is run.
"killed" = the self-test went red; "SURVIVED" = it stayed green, so no arm depends on that check.

The lists LC_REVIEW and HS_REVIEW are the reviewer's own (round 2 of the fresh-context review, 2026-11-17: 47 and 25
entries, one of them a skip), kept verbatim except one entry whose source line was rewritten by the repair of KD-02.
LC_NEW and HS_NEW are the checks added by the repair of 2026-11-17 (KD-02, KD-03), written by the producer.
An entry whose source text is not found exactly once is reported as SKIP and counted apart: it is not a kill.

Run:  PYTHONIOENCODING=utf-8 python bomdd/reports/eco-126-loop-route/mutants_tools.py
Exit: 0 = ran (survivors are reported, not failed) / 2 = could not run. Writes mutants-tools-output.txt beside itself.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[2] / "method" / "tools"
ENV = dict(os.environ, HANDOVER_NO_START="1", PYTHONIOENCODING="utf-8")

LC_REVIEW = [
 ("control: accepted vocabulary check removed", "        if acc not in ACCEPTED:", "        if False:"),
 ("control: named_in check removed", '        elif acc == "yes" and not _text(p.get("named_in")):', "        elif False:"),
 ("#28 class check removed", '        if x.get("class") not in REACTION_CLASSES:', "        if False:"),
 ("#28 handed_at check removed", '        if not _text(r.get("handed_at")):', "        if False:"),
 ("#28 set.commit part removed", 'if not _text(s.get("commit")) or not files or', "if not files or"),
 ("#3 empty-hash part removed", ' or not all(_text(v) for v in files.values()):', ":"),
 ("#28 disposition check removed", "        if d not in DISPOSITIONS:", "        if False:"),
 ("#28 lands_on existence check removed", "            if str(t) not in seen:", "            if False:"),
 ("#28 listed_before_use check removed", 'if (x.get("lands_on") or []) and _yn(x.get("listed_before_use")) not in LISTED:', "if False:"),
 ("#28 preread rule removed", '        elif it.get("kind") == "preread" and d not in PREREAD_DISPOSITIONS:', "        elif False:"),
 ("#1 no-round gap removed", '    if not doc["rounds"]:', "    if False:"),
 ("#4 reaction id check removed", "        if not xid:\n            out.append(\"reactions: id のない行がある\")\n            continue", "        if False:\n            continue"),
 ("#4 duplicate reaction id check removed", "        if xid in rx_ids:", "        if False:"),
 ("#4 duplicate round n check removed", "        elif n in rounds_n:", "        elif False:"),
 ("#4 round n integer check removed", "        if isinstance(n, bool) or not isinstance(n, int):\n            out.append(f\"rounds: 番号", "        if False:\n            out.append(f\"rounds: 番号"),
 ("#4 'fixed' dropped from channel rule", 'if d in ("asked", "fixed") and', 'if d in ("asked",) and'),
 ("#4 'asked' dropped from channel rule", 'if d in ("asked", "fixed") and', 'if d in ("fixed",) and'),
 ("#4 reaction words check removed", '        if not _text(x.get("words")):', "        if False:"),
 ("#4 reaction round-in-rounds check removed", '        if x.get("round") not in rounds_n:', "        if False and x.get('round') not in rounds_n:"),
 ("#4 reply.words check removed", '            if not _text((rd.get("reply") or {}).get("words")):', "            if False:"),
 ("items: source check removed", '        if it.get("source") not in SOURCES:', "        if False:"),
 ("items: kind check removed", '        if it.get("kind") not in ITEM_KINDS:', "        if False:"),
 ("items: duplicate id check removed", "        if iid in seen:", "        if False:"),
 ("items: id missing check removed", "        if not iid:\n            out.append(\"items: id のない行がある\")\n            continue", "        if False:\n            continue"),
 ("reports: id check removed", "        if not pid:", "        if False:"),
 ("not_asked why check removed", '        if d == "not_asked" and not _text(it.get("why")):', "        if False:"),
 ("kind check removed", '        if x.get("kind") not in REACTION_KINDS:', "        if False:"),
 ("kind_by check removed", '        if x.get("kind_by") not in KIND_BY:', "        if False:"),
 ("tally: patched_without_reproduction not summed", 'rep["patched_without_reproduction"] += k.get("patched_without_reproduction") or 0', "pass"),
 ("tally: fixed_after_reproduction not summed", 'rep["fixed_after_reproduction"] += k.get("fixed_after_reproduction") or 0', "pass"),
 ("tally: checks_replaced not summed", 'rep["checks_replaced"] += r.get("checks_replaced") or 0', "pass"),
 ("tally: reasks not summed", 'rep["reasks"] += r.get("reasks") or 0', "pass"),
 ("tally: to_user_report dropped from ASKED", 'ASKED = {"to_user_check", "to_user_report", "asked"}', 'ASKED = {"to_user_check", "asked"}'),
 ("tally: to_user_check dropped from ASKED", 'ASKED = {"to_user_check", "to_user_report", "asked"}', 'ASKED = {"to_user_report", "asked"}'),
 ("tally: 'asked' dropped from ASKED", 'ASKED = {"to_user_check", "to_user_report", "asked"}', 'ASKED = {"to_user_check", "to_user_report"}'),
 ("tally: reaction kinds counted by kind only (kind_by fixed to user)", 'Counter((x.get("kind"), x.get("kind_by")) for x in rx)', 'Counter((x.get("kind"), "user") for x in rx)'),
 ("tally: class counter emptied", '"reaction_classes": Counter(x.get("class") for x in rx)', '"reaction_classes": Counter()'),
 ("tally: reports counter emptied", '"reports": Counter(_yn(p.get("accepted")) for p in doc["reports"])', '"reports": Counter()'),
 ("tally: preread counter emptied", '"preread": Counter(i.get("disposition") for i in items if i.get("kind") == "preread")', '"preread": Counter()'),
 ("tally: stage-3 outcome emptied", '"outcome": {s: Counter((i.get("disposition"), i.get("outcome")) for i in items if i.get("source") == s) for s in SOURCES}', '"outcome": {s: Counter() for s in SOURCES}'),
 ("show: [over] line removed", "    if isinstance(limit, int) and not isinstance(limit, bool) and len(rounds) > limit:", "    if False:"),
 ("show: budget not shown", '+ (f" / budget {lim.get(\'budget\')}" if lim.get("budget") is not None else ""))', ')'),
 ("shape: scalar-field type check removed", "                if x.get(k) is not None and not isinstance(x[k], (str, int, float, bool)):", "                if False:"),
 ("shape: launches check removed", '        if not (r.get("launches") is None or r.get("launches") == "unknown" or isinstance(r.get("launches"), dict)):', "        if False:"),
 ("shape: files mapping check removed", "        if files is not None and not isinstance(files, dict):", "        if False:"),
 ("shape: list-element mapping check removed", "            if not isinstance(x, dict):", "            if False:"),
 ("exit: --check never exits 1", "    sys.exit(1 if (args.check and g) else 0)", "    sys.exit(0)"),
]
LC_NEW = [
 ("new: limits.rounds missing check removed", '    if lim.get("rounds") is None:', "    if False:"),
 ("new: budget missing check removed", '    if not _text(lim.get("budget")):', "    if False:"),
 ("new: item round check removed", '        if it.get("round") is None or it.get("round") not in round_numbers:', "        if False:"),
 ("new: jig field check removed", '        if not _text(s.get("jig")):', "        if False:"),
 ("new: matching > count check removed", '        if isinstance(la, dict) and la["matching"] > la["count"]:', "        if False:"),
 ("new: launches missing (with a reply) check removed", "            if la is None:", "            if False:"),
 ("new: reply with no reaction row check removed", '            if not any(x.get("round") == n for x in doc["reactions"]):', "            if False:"),
 ("new: duplicate report id check removed", "        elif pid in report_ids:", "        elif False:"),
 ("new: limits.rounds type check removed", "    if lr is not None and (isinstance(lr, bool) or not isinstance(lr, int) or lr < 1):", "    if False:"),
 ("new: launches count/matching type check removed", "                if isinstance(v, bool) or not isinstance(v, int) or v < 0:", "                if False:"),
]
HS_REVIEW = [
 ("control: exit 3 for zero launches removed", "    if not mine:\n        print(\"unknown", "    if False:\n        print(\"unknown"),
 ("'other' (mismatching launch) dropped from the exit-1 condition", "    if other or now_diff or broken:", "    if now_diff or broken:"),
 ("'now_diff' dropped from the exit-1 condition", "    if other or now_diff or broken:", "    if other or broken:"),
 ("'broken' dropped from the exit-1 condition", "    if other or now_diff or broken:", "    if other or now_diff:"),
 ("#9 program not added to the stamped files", "    names = list(dict.fromkeys([*files, program]))", "    names = list(dict.fromkeys([*files]))"),
 ("#5 stamp id not compared (every well-formed line is 'mine')", '            elif parts[1].strip() == m["stamp_id"]:', "            elif True:"),
 ("#5 'earlier stamps' line removed", "    if earlier:", "    if False:"),
 ("#6/#8 _safe always true", '    return isinstance(name, str) and bool(NAME_RE.match(name)) and ".." not in name.split("/")', "    return True"),
 ("#8 '..' test removed from _safe", ' and ".." not in name.split("/")', ""),
 ("#6 NAME_RE allows & and ^", 'NAME_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]*(/[A-Za-z0-9_][A-Za-z0-9._-]*)*$")', 'NAME_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._&^-]*(/[A-Za-z0-9_][A-Za-z0-9._&^-]*)*$")'),
 ("NAME_RE allows a leading / (absolute)", 'NAME_RE = re.compile(r"^[A-Za-z0-9_]', 'NAME_RE = re.compile(r"^/?[A-Za-z0-9_]'),
 ("NAME_RE allows drive colon and backslash", 'NAME_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]*(/[A-Za-z0-9_][A-Za-z0-9._-]*)*$")', 'NAME_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._:\\\\-]*([/\\\\][A-Za-z0-9_][A-Za-z0-9._-]*)*$")'),
 ("#11 manifest: HEX64/_safe clause removed", '          and all(_safe(n) and isinstance(h, str) and HEX64.match(h) for n, h in m["files"].items())\n', ""),
 ("#11 manifest: stamp_id clause removed", '          and isinstance(m.get("stamp_id"), str) and re.fullmatch(r"[0-9a-f]{12}", m["stamp_id"] or "")\n', ""),
 ("#11 manifest: main/program membership removed", '          and m["main"] in m["files"] and m["program"] in m["files"])', "          )"),
 ("#11 manifest: schema clause removed", 'isinstance(m, dict) and m.get("schema") == SCHEMA and', "isinstance(m, dict) and"),
 ("#7 malformed: stamp-id pattern test removed (4 fields only)", '            if len(parts) != 4 or not re.fullmatch(r"[0-9a-f]{12}", parts[1].strip()):', "            if len(parts) != 4:"),
 ("#7 malformed lines not reported/counted", "                broken.append(raw)", "                pass"),
 ("match ignores the logged hash", '    match = [l for l in mine if l[2] == m["main"] and l[3].lower() == want]', '    match = [l for l in mine if l[2] == m["main"]]'),
 ("match ignores the logged main name", '    match = [l for l in mine if l[2] == m["main"] and l[3].lower() == want]', '    match = [l for l in mine if l[3].lower() == want]'),
 ("now_diff looks at the main file only", '    now_diff = [n for n, h in m["files"].items() if not (d / n).is_file() or sha256(d / n) != h]', '    now_diff = [n for n, h in m["files"].items() if n == m["main"] and (not (d / n).is_file() or sha256(d / n) != h)]'),
 ("now_diff: missing file not counted", 'if not (d / n).is_file() or sha256(d / n) != h]', 'if (d / n).is_file() and sha256(d / n) != h]'),
 ("launcher(cmd): logs a constant hash from the manifest instead of hashing", "%T%\t{stamp}\t{main}\t%H%", "%T%\t{stamp}\t{main}\t0000"),
 ("launcher(cmd): HANDOVER_NO_START ignored is not tested (skip)", None, None),
 ("stamp: file-existence check removed", "        if not (d / name).is_file():\n            raise InputError(f\"ファイルが無い", "        if False:\n            raise InputError(f\"ファイルが無い"),
 ("record line prints matching as count", "print(f\"record line — launches: {{count: {len(mine)}, matching: {len(match)}}}\")", "print(f\"record line — launches: {{count: {len(mine)}, matching: {len(mine)}}}\")"),
]
HS_NEW = [
 ("new: manifest main/program string clause removed", '          and isinstance(m.get("main"), str) and isinstance(m.get("program"), str)\n', ""),
 ("new: unreadable log is re-raised instead of [input]", '            raise InputError(f"{LOG} が読めない: {e}")', "            raise"),
 ("new: the catch-all exits 1 instead of 2", '{type(e).__name__}: {e}")\n        sys.exit(2)', '{type(e).__name__}: {e}")\n        sys.exit(1)'),
]


def run_list(tool, title, entries, tmp, lines):
    src = (TOOLS / tool).read_text(encoding="utf-8")
    n = {"killed": 0, "SURVIVED": 0, "SKIP": 0}
    survivors = []
    for label, a, b in entries:
        if a is None:
            n["SKIP"] += 1
            lines.append(f"SKIP     [{title}] {label} (not a mutant)")
            continue
        if src.count(a) != 1:
            n["SKIP"] += 1
            lines.append(f"SKIP     [{title}] {label} (source text found {src.count(a)} times)")
            continue
        p = Path(tmp) / ("mut_" + tool.replace("-", "_"))
        p.write_text(src.replace(a, b), encoding="utf-8")
        r = subprocess.run([sys.executable, str(p), "--selftest"], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=ENV)
        word = "SURVIVED" if r.returncode == 0 else "killed"
        n[word] += 1
        if word == "SURVIVED":
            survivors.append(label)
        tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
        lines.append(f"{word:8s} [{title}] {label}" + ("" if word == "SURVIVED" else f"   <- {tail[-1][:150] if tail else ''}"))
        print(lines[-1], flush=True)
    lines.append(f"TOTAL    [{title}] {tool}: killed {n['killed']} / survived {n['SURVIVED']} / skipped {n['SKIP']} of {len(entries)}")
    print(lines[-1], flush=True)
    return survivors


def main():
    lines = []
    for tool in ("loop-count.py", "handover-stamp.py"):
        base = subprocess.run([sys.executable, str(TOOLS / tool), "--selftest"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=ENV)
        lines.append(f"BASE     {tool} --selftest: exit {base.returncode} — {(base.stdout or '').strip().splitlines()[-1][:120]}")
        print(lines[-1], flush=True)
        if base.returncode != 0:
            return 2
    with tempfile.TemporaryDirectory(prefix="bomdd-mut-") as tmp:
        run_list("loop-count.py", "reviewer", LC_REVIEW, tmp, lines)
        run_list("loop-count.py", "repair", LC_NEW, tmp, lines)
        run_list("handover-stamp.py", "reviewer", HS_REVIEW, tmp, lines)
        run_list("handover-stamp.py", "repair", HS_NEW, tmp, lines)
    (HERE / "mutants-tools-output.txt").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
