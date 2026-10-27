#!/usr/bin/env python3
"""EXP-20261027-03, side measurement 2: the cost of porting ViewPrism2's receiving instrument to ViewTube.

Reads blobs with `git show <commit>:<path>` (read-only in both product repositories) and compares them line by line.

  python bomdd/reports/exp-20261027-03/instrument_diff.py <ViewPrism2 repo> <ViewTube repo>

Method (stated in the output as well):
- Each file is read as a git blob (bytes). Line endings are counted in bytes (CRLF, lone CR) before any normalisation.
- View A, "raw lines": decoded as UTF-8, split on LF, trailing CR and trailing whitespace removed.
- View B, "code lines": comments removed with `tokenize`, docstrings (a string expression that is the first statement of
  the module, a class or a function) removed with `ast`, blank lines dropped, runs of whitespace collapsed to one space,
  leading whitespace kept as an indentation depth only. ViewPrism2's comments and docstrings are Japanese and ViewTube's
  English (ViewTube records in English by the user's ruling), so view A counts translated comments as changed lines;
  view B measures the code.
- difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes(): `equal` lines are shared; `replace` blocks are
  changed (both sides' line counts reported); `delete` lines exist only in the first file; `insert` lines only in the
  second. Inside each `replace` block a second-file line is "edited" when some first-file line of the same block has
  SequenceMatcher ratio >= 0.6 with it, otherwise "rewritten" (threshold chosen before the run, not tuned).
- Function level (view B per definition): every top-level `def`/`class` is matched by name; a matched pair is
  "identical" when its view-B lines are equal, otherwise "changed" with the ratio of its view-B lines; unmatched names
  are first-only or second-only. Selftest helpers (the `selftest` function and the `_`-prefixed fixtures after it) are
  reported apart from the instrument proper.
"""
import ast
import difflib
import hashlib
import io
import re
import subprocess
import sys
import tokenize

EDIT_RATIO = 0.6


def blob(repo, commit, path):
    return subprocess.run(["git", "-C", repo, "show", f"{commit}:{path}"], capture_output=True, check=True).stdout


def full(repo, commit):
    return subprocess.run(["git", "-C", repo, "rev-parse", commit], capture_output=True, check=True,
                          text=True).stdout.strip()


def endings(data):
    crlf = data.count(b"\r\n")
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "lf_lines": data.count(b"\n"),
            "crlf": crlf, "lone_cr": data.count(b"\r") - crlf}


def raw_lines(text):
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()   # the element after the final LF is not a line
    return [ln.rstrip("\r").rstrip() for ln in lines]


# review and design-loop finding ids as the two products' comments cite them: ViewTube's converge loops (L<loop>R<round>-NN),
# its R8 rounds (R270-<round>-NN, R269-...), ViewPrism2's R8 (R8-<round>-NN) and converge (L1R<round>-NN)
TAG = re.compile(r"\b(R27[01]-[12]-\d\d|R269-\d-\d+|R8-\d-\d\d|L\dR\d-\d\d)\b")


def tags(text):
    """Top-level def/class name -> the finding ids cited in its raw source span."""
    tree = ast.parse(text)
    lines = text.split("\n")
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            out[node.name] = sorted(set(TAG.findall("\n".join(lines[start - 1:node.end_lineno]))))
    return out


def strip_comments_docstrings(text):
    """Source with comments blanked and docstrings removed, line numbers kept (removed lines become empty)."""
    lines = text.split("\n")
    tree = ast.parse(text)
    drop = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                drop.update(range(first.lineno, first.end_lineno + 1))
    out = list(lines)
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.COMMENT:
            r, c = tok.start
            out[r - 1] = out[r - 1][:c]
    for n in drop:
        out[n - 1] = ""
    return out


def norm(line):
    s = line.rstrip("\r").rstrip()
    if not s.strip():
        return None
    depth = len(s) - len(s.lstrip())
    return f"{depth:02d}|" + re.sub(r"\s+", " ", s.strip())


def code_lines(text):
    return [x for x in (norm(ln) for ln in strip_comments_docstrings(text)) if x is not None]


def compare(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    c = {"equal": 0, "replace_a": 0, "replace_b": 0, "delete": 0, "insert": 0, "edited_b": 0, "rewritten_b": 0}
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            c["equal"] += i2 - i1
        elif op == "delete":
            c["delete"] += i2 - i1
        elif op == "insert":
            c["insert"] += j2 - j1
        else:
            c["replace_a"] += i2 - i1
            c["replace_b"] += j2 - j1
            block = a[i1:i2]
            for ln in b[j1:j2]:
                best = max(difflib.SequenceMatcher(None, x, ln, autojunk=False).ratio() for x in block)
                c["edited_b" if best >= EDIT_RATIO else "rewritten_b"] += 1
    c["len_a"], c["len_b"] = len(a), len(b)
    return c


def definitions(text):
    """Top-level def/class name -> view-B lines of its source span (decorators included)."""
    tree = ast.parse(text)
    stripped = strip_comments_docstrings(text)
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            span = stripped[start - 1:node.end_lineno]
            out[node.name] = [x for x in (norm(ln) for ln in span) if x is not None]
    return out


def module_level(text):
    """View-B lines outside every top-level def/class (constants, imports, the __main__ guard)."""
    tree = ast.parse(text)
    stripped = strip_comments_docstrings(text)
    inside = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            inside.update(range(start, node.end_lineno + 1))
    return [x for n, ln in enumerate(stripped, 1) if n not in inside for x in [norm(ln)] if x is not None]


def fmt_compare(c, a_name, b_name):
    shared_b = c["equal"] / c["len_b"] if c["len_b"] else 0
    return [f"  lines: {a_name} {c['len_a']}, {b_name} {c['len_b']}",
            f"  shared (equal): {c['equal']}  = {shared_b:.1%} of {b_name}, {c['equal'] / c['len_a'] if c['len_a'] else 0:.1%} of {a_name}",
            f"  changed (replace): {a_name} side {c['replace_a']}, {b_name} side {c['replace_b']} "
            f"(edited {c['edited_b']}, rewritten {c['rewritten_b']}; ratio >= {EDIT_RATIO})",
            f"  {a_name} only (delete): {c['delete']}",
            f"  {b_name} only (insert): {c['insert']}",
            f"  {b_name}'s lines not shared: {c['len_b'] - c['equal']} = {1 - shared_b:.1%}"]


def pair(label, a_name, a_text, a_meta, b_name, b_text, b_meta):
    out = [f"## {label}", "", f"- {a_name}: {a_meta['where']} (blob sha256 {a_meta['sha256']}, {a_meta['bytes']} bytes, "
           f"{a_meta['lf_lines']} LF, {a_meta['crlf']} CRLF, {a_meta['lone_cr']} lone CR)",
           f"- {b_name}: {b_meta['where']} (blob sha256 {b_meta['sha256']}, {b_meta['bytes']} bytes, "
           f"{b_meta['lf_lines']} LF, {b_meta['crlf']} CRLF, {b_meta['lone_cr']} lone CR)", ""]
    ra, rb = raw_lines(a_text), raw_lines(b_text)
    out += ["View A (raw lines, trailing whitespace removed):"] + fmt_compare(compare(ra, rb), a_name, b_name)
    ra_nb, rb_nb = [x for x in ra if x.strip()], [x for x in rb if x.strip()]
    out += ["View A' (raw lines, blank lines dropped):"] + fmt_compare(compare(ra_nb, rb_nb), a_name, b_name)
    ca, cb = code_lines(a_text), code_lines(b_text)
    out += ["View B (code lines: comments, docstrings and blank lines removed, whitespace normalised):"] + \
        fmt_compare(compare(ca, cb), a_name, b_name)
    out.append("")

    da, db = definitions(a_text), definitions(b_text)
    order_a = {n: i for i, n in enumerate(da)}
    order_b = {n: i for i, n in enumerate(db)}

    def selftest_span(order):
        # the fixtures: the first `_`-prefixed definition after `audit`, through `selftest`
        after = [i for n, i in order.items() if n.startswith("_") and i > order["audit"]]
        return min(after), order["selftest"]

    span_a, span_b = selftest_span(order_a), selftest_span(order_b)

    def part(order, span, name):
        return "selftest" if span[0] <= order[name] <= span[1] else "instrument"

    rows = []
    for name in sorted(set(da) | set(db), key=lambda n: (order_b.get(n, 10_000), order_a.get(n, 10_000))):
        pa = part(order_a, span_a, name) if name in da else None
        pb = part(order_b, span_b, name) if name in db else None
        where = pb or pa
        if name in da and name in db:
            if da[name] == db[name]:
                rows.append((where, name, "identical", len(da[name]), len(db[name]), 1.0))
            else:
                r = difflib.SequenceMatcher(None, da[name], db[name], autojunk=False).ratio()
                rows.append((where, name, "changed", len(da[name]), len(db[name]), r))
        elif name in da:
            rows.append((where, name, f"{a_name} only", len(da[name]), 0, 0.0))
        else:
            rows.append((where, name, f"{b_name} only", 0, len(db[name]), 0.0))
    for where in ("instrument", "selftest"):
        sel = [r for r in rows if r[0] == where]
        tally = {}
        for r in sel:
            k = r[2]
            t = tally.setdefault(k, [0, 0, 0])
            t[0] += 1
            t[1] += r[3]
            t[2] += r[4]
        out.append(f"Definitions, {where} (view B lines; matched by top-level name):")
        for k in ("identical", "changed", f"{a_name} only", f"{b_name} only"):
            if k in tally:
                n, la, lb = tally[k]
                out.append(f"  {k}: {n} definitions, {a_name} {la} lines, {b_name} {lb} lines")
        out.append("")
    ma, mb = module_level(a_text), module_level(b_text)
    out += ["Module level outside definitions (constants, imports, guard), view B:"] + fmt_compare(compare(ma, mb), a_name, b_name)
    ta, tb = tags(a_text), tags(b_text)
    out += ["", "Per definition (part, name, status, lines first, lines second, ratio; the second file's finding ids that the",
            "first file's same definition does not cite):"]
    for r in rows:
        new_tags = [t for t in tb.get(r[1], []) if t not in ta.get(r[1], [])]
        out.append(f"  {r[0]:10s} {r[1]:28s} {r[2]:14s} {r[3]:5d} {r[4]:5d} {r[5]:.2f}  {' '.join(new_tags)}")
    # the second file's not-identical instrument definitions, split by whether their source cites a finding id the first's does not
    cited = uncited = 0
    n_cited = n_uncited = 0
    for r in rows:
        if r[0] != "instrument" or r[2] == "identical" or r[4] == 0:
            continue
        new_tags = [t for t in tb.get(r[1], []) if t not in ta.get(r[1], [])]
        if new_tags:
            cited += r[4]
            n_cited += 1
        else:
            uncited += r[4]
            n_uncited += 1
    out += ["", f"Instrument definitions of the second file that are changed or new: {n_cited + n_uncited} "
            f"({cited + uncited} view-B lines);",
            f"  citing a finding id the first file's same definition does not: {n_cited} definitions, {cited} lines;",
            f"  citing none: {n_uncited} definitions, {uncited} lines.",
            "  (A citation shows that a review or design-loop finding touched the definition, not that every line in it",
            "  came from that finding; an uncited definition can still be a repair.)", ""]
    return out


def main(argv):
    vp2, vt = argv[1], argv[2]
    specs = {
        "VP2@82c362e": (vp2, "82c362e", "bomdd/receive_delivery.py"),
        "VT@33a2581e": (vt, "33a2581e", "bomdd/tools/receive_delivery.py"),
        "VT@44bd91d0": (vt, "44bd91d0", "bomdd/tools/receive_delivery.py"),
        "VT-probes@33a2581e": (vt, "33a2581e", "bomdd/tools/selftest_receive_delivery_probes.py"),
        "VP2-r8probe@82c362e": (vp2, "82c362e", "bomdd/reports/receiving/eco-148-r8/r8_probe.py"),
    }
    texts, metas = {}, {}
    for k, (repo, c, p) in specs.items():
        data = blob(repo, c, p)
        m = endings(data)
        m["where"] = f"{full(repo, c)}:{p}"
        texts[k], metas[k] = data.decode("utf-8"), m
    out = ["# EXP-20261027-03 - porting cost of the receiving instrument (ViewPrism2 -> ViewTube)", "",
           "Generated by `bomdd/reports/exp-20261027-03/instrument_diff.py`; method in its docstring.", ""]
    out += pair("1. The port: ViewPrism2 ECO-148's instrument against ViewTube ECO-VT-270's (as applied)",
                "VP2", texts["VP2@82c362e"], metas["VP2@82c362e"], "VT", texts["VT@33a2581e"], metas["VT@33a2581e"])
    out += pair("2. After the port: ViewTube ECO-VT-270 against ECO-VT-271 (applied 44bd91d0)",
                "VT270", texts["VT@33a2581e"], metas["VT@33a2581e"], "VT271", texts["VT@44bd91d0"], metas["VT@44bd91d0"])
    out += ["## 3. The R8 probe files (each product's own; reported, not part of the port's count)", ""]
    for k in ("VP2-r8probe@82c362e", "VT-probes@33a2581e"):
        m = metas[k]
        out.append(f"- {k}: {m['where']}: {m['lf_lines']} LF lines, {len(code_lines(texts[k]))} code lines (view B), "
                   f"{m['crlf']} CRLF")
    c = compare(code_lines(texts["VP2-r8probe@82c362e"]), code_lines(texts["VT-probes@33a2581e"]))
    out += ["View B, VP2's r8_probe.py against VT's selftest_receive_delivery_probes.py:"] + fmt_compare(c, "VP2", "VT")
    out.append("")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
