"""ECO-126 V1 — GU7 on real ledgers (read-only on the product repositories; everything is written under a scratch folder).

usage: v1_gu7.py <BomDD root> <filing commit> <MoviePad repo> <ViewTube repo> <scratch dir>
Prints one line per check and exits 1 if any expectation fails.
"""
import subprocess
import sys
from pathlib import Path

root, filing, mp, vt, scratch = (Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
NAMES = ["ui-ir.raw.json", "ui-ir.json", "ui-bom.json", "ui-trace-map.json", "37-ui-rulings.yaml", "36-ui-dictionary.yaml"]
bad = []


def git(repo, *a, text=True):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=text, encoding="utf-8" if text else None)


def export(repo, rev, dest):
    dest.mkdir(parents=True, exist_ok=True)
    got = []
    for n in NAMES:
        p = git(repo, "show", f"{rev}:bomdd/ui/{n}", text=False)
        if p.returncode == 0:
            (dest / n).write_bytes(p.stdout)
            got.append(n)
    return got


def gate(tool, ui):
    # GU6 (id drift against the mock) is outside this check; declared so that an untouched ledger can reach exit 0
    p = subprocess.run([sys.executable, str(tool), "--ui-dir", str(ui), "--na", "GU6: V1 reads the ledger checks only"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = p.stdout.replace(str(ui), "<ui>")
    return p.returncode, out


def expect(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + (" — " + detail if detail else ""))
    if not ok:
        bad.append(label)


new = root / "method" / "tools" / "ui-cad-gate.py"
old = scratch / "gate-at-filing.py"
scratch.mkdir(parents=True, exist_ok=True)
old.write_bytes(git(root, "show", f"{filing}:method/tools/ui-cad-gate.py", text=False).stdout)

# 1. ledgers with no bundle: the output of the filing tree's gate and of the changed gate are the same
vt_head = git(vt, "rev-parse", "HEAD").stdout.strip()
# MoviePad's local main is behind the merged work; 9d46268 is the head of the merged ECO-006 branch (the order's "MoviePad HEAD")
for label, repo, rev in (("MoviePad d5dab41 (before ECO-006's manufacture)", mp, "d5dab41"),
                         ("MoviePad 9d46268 (ECO-006 closed; the head of the merged branch)", mp, "9d46268"),
                         (f"ViewTube HEAD ({vt_head[:12]})", vt, vt_head)):
    d = scratch / label.split(" (")[0].replace(" ", "-")
    got = export(repo, rev, d)
    a, b = gate(old, d), gate(new, d)
    expect(f"same output, no bundle: {label}", a == b, f"files {len(got)}/6, exit {a[0]} and {b[0]}, lines {len(a[1].splitlines())}")

# 2. MoviePad at d5dab41 with UQ-0030 retyped as a bundle
base = scratch / "MoviePad-d5dab41"
src = (base / "37-ui-rulings.yaml").read_text(encoding="utf-8").splitlines(keepends=True)


def variant(name, extra_in_bundle="", tail=""):
    d = scratch / name
    d.mkdir(parents=True, exist_ok=True)
    for n in NAMES:
        if (base / n).exists() and n != "37-ui-rulings.yaml":
            (d / n).write_bytes((base / n).read_bytes())
    out, inside, done = [], False, 0
    for line in src:
        if line.startswith("  - id: "):
            inside = line.strip() == "- id: UQ-0030"
        if inside and line.lstrip().startswith("type:"):
            line = "    type: provisional-bundle\n" + extra_in_bundle
            done += 1
        out.append(line)
    assert done == 1, done
    (d / "37-ui-rulings.yaml").write_text("".join(out) + tail, encoding="utf-8", newline="\n")
    return d


OVER = ["UQ-0001", "UQ-0016", "UQ-0020", "UQ-0021", "UQ-0022", "UQ-0023", "UQ-0025", "UQ-0027", "UQ-0028", "UQ-0029"]
rc, out = gate(new, variant("retyped"))
g7 = [l for l in out.splitlines() if l.strip().startswith("- UQ-0030") and "confirmed_checked に無い" in l]
other = [l for l in out.splitlines() if "] FAIL " in l and not l.startswith("[GU7]")]
named = [u for u in OVER if any(f"人が決めた裁定 {u} " in l for l in g7)]
expect("retyped bundle, no list: red, GU7 only, the 10 overlapping rulings named",
       rc == 1 and "[GU7] FAIL" in out and not other and named == OVER and len(g7) == 10,
       f"exit {rc}, named {len(named)}/10, GU7 lines {len(g7)}, other FAIL {len(other)}")

rows = "    confirmed_checked:\n" + "".join(
    f"      - {{id: {u}, touches: {'yes' if u == 'UQ-0027' else 'no'}, why: \"V1 fixture\"}}\n" for u in OVER)
rc, out = gate(new, variant("listed-no-single", rows))
expect("list filled, UQ-0027 touched, no entry of its own: red for that reason",
       rc == 1 and "UQ-0027 に触れると書いたが" in out and out.count("    - ") == 1, f"exit {rc}")

single = ("  - id: UQ-9{n}\n    status: {st}\n    type: other\n    blocking: {bl}\n    touches_confirmed: UQ-0027\n"
          "    target:\n      ui_ids: [\"screen.main\"]\n    question: V1 fixture {n}\n{rest}")
open_tail = "".join(single.format(n=n, st="open", bl="true", rest="") for n in (31, 32))
rc, out = gate(new, variant("listed-single-open", rows, open_tail))
expect("two single entries open and blocking: GU7 passes, GU3 holds manufacture",
       rc == 1 and "[GU7] PASS" in out and "[GU3] FAIL" in out and out.count("] FAIL ") == 1, f"exit {rc}")

soft_tail = "".join(single.format(n=n, st="open", bl="false", rest="") for n in (31, 32))
rc, out = gate(new, variant("listed-single-open-not-blocking", rows, soft_tail))
expect("two single entries open and not blocking: GU7 red for that reason",
       rc == 1 and "[GU7] FAIL" in out and out.count("blocking でない") == 2 and out.count("] FAIL ") == 1, f"exit {rc}")

ruled_tail = "".join(single.format(n=n, st="ruled", bl="true", rest="    ruling: keep\n    decided_by: user\n") for n in (31, 32))
# once ruled by the user, the two single entries are themselves human-decided rulings that overlap the bundle: they are listed too
rows_ruled = rows + "".join(f'      - {{id: UQ-9{n}, touches: no, why: "V1 fixture: the single entry itself"}}\n' for n in (31, 32))
rc0, out0 = gate(new, variant("listed-single-ruled-not-listed", rows, ruled_tail))
expect("two single entries ruled but not listed in the bundle: red, both named",
       rc0 == 1 and out0.count("confirmed_checked に無い") == 2 and "UQ-931" in out0 and "UQ-932" in out0 and out0.count("] FAIL ") == 1,
       f"exit {rc0}")
rc, out = gate(new, variant("listed-single-ruled", rows_ruled, ruled_tail))
base_rc, _ = gate(new, base)
expect("two single entries ruled by the user: green as the untouched ledger", rc == 0 and base_rc == 0 and "[GU7] PASS" in out,
       f"exit {rc}, untouched {base_rc}")

print("V1 real ledgers:", "FAILED " + str(bad) if bad else "all as expected")
sys.exit(1 if bad else 0)
