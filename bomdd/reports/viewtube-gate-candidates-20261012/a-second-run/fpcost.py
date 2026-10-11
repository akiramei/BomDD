"""Estimate the cost of fingerprinting the working-tree inputs of validate_process.py --commit-msg.

Read-only on ROOT. usage: python fpcost.py ROOT
W-set = (1) the machinery-claim record surface (same rglob as validate_machinery_claims.record_surface)
      ∪ (2) every path string in the register (any depth) that names an existing file, plus every file
            in the directory of a cited conformance report (validate_ui_golden reads relative to it)
      ∪ (3) fixed files: hooks, .gitattributes, policies, tools code
      ∪ (4) working copies of staged paths (git diff --cached --name-only)
"""
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

import yaml

root = Path(sys.argv[1]).resolve()
t0 = time.perf_counter()
pol = yaml.safe_load((root / "bomdd/process/machinery-claim-policy.yaml").read_text(encoding="utf-8"))
prefixes = pol["record_surface"]["prefixes"]
suffixes = tuple(pol["record_surface"]["suffixes"])
surface = []
for prefix in prefixes:
    base = root / prefix
    if base.is_dir():
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in suffixes:
                surface.append(p)
t_walk = time.perf_counter() - t0

reg = yaml.safe_load((root / "bomdd/process/change-register.yaml").read_text(encoding="utf-8"))
cited = set()
report_dirs = set()


def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)


def add(rel):
    if isinstance(rel, str) and rel.strip() and ":" not in rel:
        p = root / rel.strip().replace("\\", "/")
        if p.is_file():
            cited.add(p)


mpol = pol
bound_prefixes = tuple(mpol["binds"]["impacted_path_prefixes"])
for e in reg.get("changes", []):
    st = e.get("status")
    ev = e.get("evidence") or {}
    add(e.get("body"))                                        # validate_process:496, consistency, language
    if st in ("implemented", "applied"):
        add((ev.get("review") or {}).get("evidence"))         # validate_process:565
        if e.get("ui_change") is True:
            vis = ev.get("visual") or {}
            for k in ("cad_golden", "application_golden"):
                add((vis.get(k) or {}).get("evidence"))
            sg = vis.get("self_golden") or {}
            add(sg.get("evidence"))
            add(sg.get("undrawn_form_record"))
            cr = sg.get("conformance_report")
            if isinstance(cr, str) and (root / cr).is_file():
                report_dirs.add((root / cr).parent)
    if st in ("staged", "implemented"):
        add(f"bomdd/process/change-impact/{e.get('id')}.yaml")  # record_consistency:637
        if any(str(i).startswith(bound_prefixes) for i in e.get("impacted_files") or []):
            for c in ev.get("machinery_claims") or []:
                if isinstance(c, dict):
                    add(c.get("probe"))
                    cs = c.get("carriers")
                    for cc in (cs if isinstance(cs, list) else [cs]):
                        if isinstance(cc, str) and not cc.startswith("commit-message:"):
                            add(cc)
for d in report_dirs:
    for p in d.rglob("*"):
        if p.is_file():
            cited.add(p)

fixed = [root / x for x in (".gitattributes", "bomdd/hooks/pre-commit", "bomdd/hooks/commit-msg")]
fixed += list((root / "bomdd/tools").glob("*.py"))
staged = subprocess.run(["git", "diff", "--cached", "--name-only", "-z"], cwd=root,
                        capture_output=True).stdout.decode("utf-8", "replace").split("\0")
staged_w = [root / s for s in staged if s and (root / s).is_file()]

allset = {p.resolve() for p in surface} | {p.resolve() for p in cited} | \
         {p.resolve() for p in fixed if p.is_file()} | {p.resolve() for p in staged_w}
extra = allset - {p.resolve() for p in surface}

tracked = set(subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True)
              .stdout.decode("utf-8", "replace").split("\0"))
untracked_surface = [p for p in surface if p.relative_to(root).as_posix() not in tracked]


def size(ps):
    return sum(p.stat().st_size for p in ps)


paths = sorted(allset)
t1 = time.perf_counter()
for p in paths:
    st = os.stat(p)
t_stat = time.perf_counter() - t1
t2 = time.perf_counter()
h = hashlib.sha256()
for p in paths:
    h.update(str(p).encode())
    h.update(hashlib.sha256(p.read_bytes()).digest())
t_hash = time.perf_counter() - t2
t3 = time.perf_counter()
for p in paths:
    st = os.stat(p)
t_stat2 = time.perf_counter() - t3
rd_set = {p.resolve() for d in report_dirs for p in d.rglob("*") if p.is_file()}
narrow = [p for p in paths if p not in rd_set]
t5 = time.perf_counter()
for p in narrow:
    hashlib.sha256(p.read_bytes()).digest()
t_hash_narrow = time.perf_counter() - t5
print(f"W-set without conformance-report dirs: {len(narrow)} files, {size(narrow)/1e6:.1f} MB, "
      f"sha256 {t_hash_narrow:.2f} s")
t4 = time.perf_counter()
gs = subprocess.run(["git", "--no-optional-locks", "status", "--porcelain=v1", "-z", "-uall",
                     "--ignored=matching", "--", *prefixes, ".gitattributes"], cwd=root,
                    capture_output=True)
t_gs = time.perf_counter() - t4

print(f"root={root}")
print(f"surface (rglob {prefixes} x {suffixes}): {len(surface)} files, {size(surface)/1e6:.1f} MB; "
      f"walk {t_walk:.2f}s; of which not tracked by git: {len(untracked_surface)} files, "
      f"{size(untracked_surface)/1e6:.1f} MB")
by_prefix = {}
for p in untracked_surface:
    k = "/".join(p.relative_to(root).parts[:2])
    by_prefix[k] = by_prefix.get(k, 0) + 1
print("  untracked surface by top dirs:", sorted(by_prefix.items(), key=lambda kv: -kv[1])[:8])
for p in untracked_surface:
    print("   untracked:", p.relative_to(root).as_posix())
rd_files = [p for d in report_dirs for p in d.rglob("*") if p.is_file()]
print(f"conformance-report dirs (upper bound for validate_ui_golden reads): {len(rd_files)} files, "
      f"{size(rd_files)/1e6:.1f} MB")
print(f"register-cited existing files: {len(cited)}; conformance report dirs: {len(report_dirs)}")
print(f"W-set union: {len(allset)} files, {size(paths)/1e6:.1f} MB; outside the surface: {len(extra)} "
      f"files, {size(extra)/1e6:.1f} MB")
print(f"stat all (first pass, after walk): {t_stat*1000:.0f} ms; second pass: {t_stat2*1000:.0f} ms")
print(f"sha256 all: {t_hash:.2f} s")
print(f"git status --porcelain -uall --ignored over surface prefixes: {t_gs:.2f} s, "
      f"{gs.stdout.count(b'\0')} entries, rc={gs.returncode}")
