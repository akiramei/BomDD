"""EXP-20261025-02: cross-unit dependencies in C# source against the part standards' declarations (preregistration.md).

scan(mbom, files) -> report mapping. mbom: the parsed M-BOM; files: {repo-relative path: source text} for every delivered .cs file.
Library only; calibrate.py and run_delivery.py feed it. Reads nothing itself, writes nothing.
"""
import re

TYPE_DECL = re.compile(r"\b(?:class|record|struct|interface|enum)\s+(?:struct\s+|class\s+)?([A-Z]\w*)"
                       r"|\bdelegate\s+[\w<>\[\],.?\s]+?\s+([A-Z]\w*)\s*[<(]")
IDENT = re.compile(r"[A-Za-z_]\w*")


def blank(src):
    """Comments and string literals replaced by spaces (newlines kept), so their words are not counted."""
    out, i, n = [], 0, len(src)
    while i < n:
        c, two = src[i], src[i:i + 2]
        if two == "//":
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif two == "/*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", src[i:j]))
            i = j
        elif c == '"' or two in ('@"', '$"') or src[i:i + 3] in ('$@"', '@$"'):
            prefix = src[i:i + 3].split('"')[0]
            verbatim, interpolated = "@" in prefix, "$" in prefix
            out.append(" " * (len(prefix) + 1))
            i += len(prefix) + 1
            while i < n:
                if verbatim and src[i:i + 2] == '""':
                    out.append("  ")
                    i += 2
                elif not verbatim and src[i] == "\\":
                    out.append("  ")
                    i += 2
                elif interpolated and src[i:i + 2] in ("{{", "}}"):
                    out.append("  ")
                    i += 2
                elif interpolated and src[i] == "{":
                    # an interpolation hole is code: kept as written (preregistration 2 blanks the text parts only)
                    depth, j = 1, i + 1
                    while j < n and depth:
                        depth += {"{": 1, "}": -1}.get(src[j], 0)
                        j += 1
                    out.append(" " + blank(src[i + 1:j - 1]) + " ")
                    i = j
                elif src[i] == '"':
                    out.append(" ")
                    i += 1
                    break
                else:
                    out.append("\n" if src[i] == "\n" else " ")
                    i += 1
        elif c == "'" and i + 2 < n:
            j = i + 1
            while j < n and src[j] != "'":
                j += 2 if src[j] == "\\" else 1
            out.append(" " * (j + 1 - i))
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def owners(mbom):
    """{unit id: [owned path or folder prefix]} from planned_output_artifact_ref (preregistration 1)."""
    result = {}
    for u in mbom["mbom"]["manufacturing_units"]:
        entries = [e.strip() for e in str(u.get("planned_output_artifact_ref") or "").split(",") if e.strip()]
        if not entries:
            continue
        folder = entries[0].rsplit("/", 1)[0] if "/" in entries[0] else ""
        result[u["id"]] = [e if "/" in e else f"{folder}/{e}" for e in entries]
    return result


def unit_of(path, own):
    hits = [uid for uid, es in own.items() if any(path == e or path.startswith(e.rstrip("/") + "/") for e in es)]
    return hits


def declared(mbom):
    """{unit: set of units it declares} via requires -> provides ids, and {unit: depends_on}."""
    provider = {}
    for u in mbom["mbom"]["manufacturing_units"]:
        for p in ((u.get("part_standard") or {}).get("provides") or []):
            provider[p["id"]] = u["id"]
    decl, dep = {}, {}
    for u in mbom["mbom"]["manufacturing_units"]:
        reqs = ((u.get("part_standard") or {}).get("requires") or [])
        decl[u["id"]] = {provider[r["target"]] for r in reqs if r.get("target") in provider}
        dep[u["id"]] = set(u.get("depends_on") or [])
    return decl, dep


def scan(mbom, files):
    own = owners(mbom)
    unit_files, unowned, ambiguous_files = {}, [], []
    for path in sorted(files):
        hits = unit_of(path, own)
        if not hits:
            unowned.append(path)
        elif len(hits) > 1:
            ambiguous_files.append((path, sorted(hits)))
        else:
            unit_files.setdefault(hits[0], []).append(path)
    blanked = {p: blank(t) for p, t in files.items()}
    type_units = {}
    for uid, paths in unit_files.items():
        for p in paths:
            for m in TYPE_DECL.finditer(blanked[p]):
                type_units.setdefault(m.group(1) or m.group(2), set()).add(uid)
    ambiguous_types = sorted(n for n, us in type_units.items() if len(us) > 1)
    refs = {}
    for uid, paths in unit_files.items():
        for p in paths:
            for tok in set(IDENT.findall(blanked[p])):
                us = type_units.get(tok)
                if us and len(us) == 1 and uid not in us:
                    target = next(iter(us))
                    refs.setdefault((uid, target), set()).add(f"{p}:{tok}")
    decl, dep = declared(mbom)
    pairs = {}
    for (a, b), where in refs.items():
        pairs[(a, b)] = ("declared-used" if b in decl.get(a, set()) else "undeclared", sorted(where))
    for a, bs in decl.items():
        for b in bs:
            if (a, b) not in pairs:
                pairs[(a, b)] = ("declared-unused", [])
    return {"units": {u: sorted(ps) for u, ps in sorted(unit_files.items())}, "unowned": unowned, "ambiguous_files": ambiguous_files,
            "ambiguous_types": ambiguous_types, "pairs": {f"{a} -> {b}": v for (a, b), v in sorted(pairs.items())},
            "depends_on_differs": sorted(u for u in decl if decl[u] != dep.get(u, set()))}
