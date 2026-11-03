"""ECO-121 survey: what each product's register already says about why an open ECO waits.

Read-only. Each register is read with `git show <head>:<path>` at the head given below, so the counts are pinned.
Usage: python -X utf8 survey.py <repos-root>   (prints survey.txt's content)
"""
import collections
import subprocess
import sys

import yaml

OPEN = ("staged", "implemented")
HEADS = {
    "ViewPrism2": ("82c362edafcfbb09591da7bb937beffeb01a2fcd", "bomdd/60-change-register.yaml"),
    "ViewTube": ("62d2b3e432de4cbc8263cbc5a77804f057a114ed", "bomdd/process/change-register.yaml"),
}


def load(root, repo):
    head, path = HEADS[repo]
    text = subprocess.run(["git", "-C", f"{root}/{repo}", "show", f"{head}:{path}"],
                          capture_output=True, check=True).stdout.decode("utf-8")
    return yaml.safe_load(text)


def as_ids(value):
    if value is None or value is False or value is True:
        return []
    if isinstance(value, (str, int)):
        value = [value]
    out = []
    for v in value:
        v = str(v)
        out.append(f"ECO-VT-{int(v):03d}" if v.isdigit() else v)
    return out


def viewprism2(root):
    d = load(root, "ViewPrism2")
    cs = d["changes"]
    applies_from = int(str(d["lifecycle_evidence"]["applies_from"]).split("-")[1])
    op = [c for c in cs if c.get("status") in OPEN]
    print(f"== ViewPrism2 @ {HEADS['ViewPrism2'][0][:8]}: entries {len(cs)}, open {len(op)}")
    print(f"   top-level keys: {list(d)}; lifecycle_evidence.applies_from = ECO-{applies_from:03d}; "
          f"active_scope.open_eco = {d['active_scope'].get('open_eco')}")
    classes = collections.defaultdict(list)
    for c in op:
        n = int(c["id"].split("-")[1])
        g = str(c.get("golden"))
        if g.startswith("pending"):
            classes["golden pending -> human-acceptance"].append(c["id"])
        elif n < applies_from and c["status"] == "implemented" and (g.startswith("approved") or g.startswith("n/a")):
            classes["legacy (before applies_from), implemented, golden approved or n/a: closed under the legacy convention"].append(c["id"])
        else:
            classes[f"no rule (status {c['status']}, golden {g[:20]!r})"].append(c["id"])
    for k, ids in classes.items():
        print(f"   {len(ids):3d}  {k}: {', '.join(ids)}")


def viewtube(root):
    d = load(root, "ViewTube")
    cs = d["changes"]
    status = {c["id"]: c.get("status") for c in cs}
    op = [c for c in cs if c.get("status") in OPEN]
    print(f"== ViewTube @ {HEADS['ViewTube'][0][:8]}: entries {len(cs)}, open {len(op)} "
          f"({collections.Counter(c['status'] for c in op)})")
    print(f"   top-level keys: {list(d)}")
    for key in ("blocks_application_golden", "blocks", "blocks_release", "next_gate", "work_authorized"):
        have = [c for c in op if key in c]
        vals = collections.Counter("[]" if c[key] == [] else type(c[key]).__name__ if not isinstance(c[key], bool) else str(c[key]) for c in have)
        print(f"   open entries with {key}: {len(have)}  values: {dict(vals)}")
    dated = [c["id"] for c in op if any(k.startswith("blocks_application_golden_added_") for k in c)]
    print(f"   open entries with a dated blocks_application_golden_added_* key: {len(dated)}")
    # blocks_application_golden / blocks on X list the ECOs whose golden (or work) X blocks: Y waits on X.
    waits = collections.defaultdict(set)
    for x in cs:
        for key in ("blocks_application_golden", "blocks"):
            for y in as_ids(x.get(key)):
                waits[y].add(x["id"])
    derived = {c["id"]: sorted(b for b in waits.get(c["id"], ()) if status.get(b) in OPEN) for c in op}
    derived = {k: v for k, v in derived.items() if v}
    print(f"   open entries named in an OPEN entry's blocks_application_golden/blocks -> eco:<blocker>: {len(derived)}")
    for k, v in derived.items():
        print(f"      {k} <- {', '.join(v)}")
    print(f"   open entries without such a rule: {len(op) - len(derived)}")


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/akira/source/repos"
    viewprism2(root)
    viewtube(root)
