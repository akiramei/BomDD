"""ECO-121 V3: the product ECO's table of waiting_on values equals what BomDD's dwell view reads from the committed register.

Usage:
  python -X utf8 compare_table.py [--table N] <order.md> <dwell.json>      exit 0 = equal, 1 = differs, 2 = input error
  python -X utf8 compare_table.py --selftest [--table N] <order.md> <dwell.json>

The table is the N-th (default 1st) Markdown table in the order whose header row starts with "| Entry | waiting_on |". Each row:
"| <ECO id> | <value> | ...". The dwell JSON is `bomdd-job.py --dwell --json --register <register>`.
The view lists open entries only, so a value left on a terminal entry shows as a warning there, not in `open`; the comparison
also fails on any waiting_on/paused warning.
"""
import json
import re
import sys

HEAD_RE = re.compile(r"^\|\s*Entry\s*\|\s*waiting_on\s*\|", re.I)


def read_table(text, nth=1):
    rows, inside, seen = {}, False, 0
    for line in text.splitlines():
        if not inside:
            if HEAD_RE.match(line):
                seen += 1
                inside = seen == nth
            continue
        if not line.startswith("|"):
            break
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if set(cells[0]) <= set("-: "):
            continue
        if cells[0] in rows:
            raise ValueError(f"row repeated: {cells[0]}")
        rows[cells[0]] = cells[1]
    if not inside:
        raise ValueError(f"no table number {nth} whose header starts with '| Entry | waiting_on |'")
    return rows


def read_view(data):
    have = {e["id"]: e["waiting_on"] for e in data.get("open", []) if e.get("waiting_on")}
    warns = [w for w in data.get("warnings", []) if "waiting_on" in w or "paused" in w]
    return have, warns


def compare(table, view, warns):
    out = []
    for eid in sorted(set(table) | set(view)):
        if table.get(eid) != view.get(eid):
            out.append(f"{eid}: table {table.get(eid)!r} / view {view.get(eid)!r}")
    out += [f"warning: {w}" for w in warns]
    return out


def main(argv):
    selftest = argv[:1] == ["--selftest"]
    args = argv[1:] if selftest else list(argv)
    nth = 1
    if args[:1] == ["--table"] and len(args) > 1:
        nth = int(args[1])
        args = args[2:]
    if len(args) != 2:
        print(__doc__)
        return 2
    try:
        table = read_table(open(args[0], encoding="utf-8").read(), nth)
        data = json.load(open(args[1], encoding="utf-8"))
        if "error" in data:
            raise ValueError(f"dwell error: {data['error']}")
        view, warns = read_view(data)
    except (OSError, ValueError, KeyError) as e:
        print(f"INPUT_ERROR {e}")
        return 2
    diffs = compare(table, view, warns)
    if not selftest:
        print(f"table {len(table)} rows / view {len(view)} entries with waiting_on / warnings {len(warns)}")
        for d in diffs:
            print("DIFF", d)
        print("EQUAL" if not diffs else "DIFFERS")
        return 0 if not diffs else 1
    # selftest: the real pair must be equal; a table with one row removed and one value changed must differ on both.
    if diffs or not table:
        print(f"SELFTEST FAIL: the real pair is not equal or the table is empty ({diffs})")
        return 1
    ids = sorted(table)
    broken = dict(table)
    removed = ids[0]
    del broken[removed]
    changed = ids[-1] if len(ids) > 1 else None
    if changed:
        broken[changed] = "external" if broken[changed] != "external" else "human-ruling"
    got = compare(broken, view, warns)
    caught_removed = any(d.startswith(removed + ":") for d in got)
    caught_changed = changed is None or any(d.startswith(changed + ":") for d in got)
    print(f"real pair EQUAL ({len(table)} rows); broken table: removed {removed} -> {'caught' if caught_removed else 'MISSED'}"
          + (f", changed {changed} -> {'caught' if caught_changed else 'MISSED'}" if changed else ""))
    return 0 if caught_removed and caught_changed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
