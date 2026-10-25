"""ECO-115 calibration on real per-delivery records: the advance decision (rehearse_decision_v2) on MoviePad-Remake delivery 2
(EXP-20261024-01 second trial), whose records were written by the procedure revised after delivery 1 — the frozen commit, the
work order at its issue commit, the delivered commit and tree, and a comparator output that names the unit it measured.

  python -B run_moviepad_d2.py <MoviePad-Remake checkout> <output file>

Read-only (git show). Runs: N0 the records as written; N1 with only what the method's templates would add at distribution (the
Control Plan's check_mapping, and the decision records the receiving side writes at decision time) — no field constructed and
no stamp assumed; N2 known-bad inputs on N1, each expected to change the result for its own reason.
"""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import rehearse_decision_v2 as rd  # noqa: E402

RECORDS_COMMIT, ENTRY_ID = "b53f048", "AB-FORWARD-01-factory-02"
MAPPING = {"line": {"row_key": r"(?P<outcome>[A-Z]+) (?P<row>\S+)(?: .*)?", "outcomes": {"PASS": "passed", "FAIL": "failed"},
                    "identity": r"(?m)^MEASURED_ON (?P<commit>[0-9a-f]{40}) (?P<tree>[0-9a-f]{40})$"}}


def git(repo, *args):
    done = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    return done.returncode, done.stdout


def show(repo, rev, path):
    code, out = git(repo, "show", f"{rev}:{path}")
    return out.decode("utf-8") if code == 0 else None


def full(repo, rev):
    code, out = git(repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    return out.decode().strip() if code == 0 else None


def main():
    repo, out_path = sys.argv[1], sys.argv[2]
    lines = []
    say = lines.append
    gitcb = {"resolve": lambda rev: full(repo, rev),
             "is_ancestor": lambda a, b: git(repo, "merge-base", "--is-ancestor", a, b)[0] == 0,
             "tree": lambda c: (lambda r: r[1].decode().strip() if r[0] == 0 else None)(git(repo, "rev-parse", f"{c}^{{tree}}")),
             "show": lambda c, path: show(repo, c, path)}
    entry0 = next(e for e in yaml.safe_load(show(repo, RECORDS_COMMIT, "bomdd/50-as-built.yaml"))["as_built"] if e["id"] == ENTRY_ID)
    frozen, issued = entry0["frozen_commit"], entry0["work_order_ref"].split("@")[1]
    delivered = entry0["delivered"]["commit"]
    wo_text = show(repo, issued, "bomdd/40-work-order.md")
    mbom, cp = show(repo, frozen, "bomdd/32-mbom.yaml"), show(repo, frozen, "bomdd/33-control-plan.yaml")
    d_mbom, d_cp = show(repo, delivered, "bomdd/32-mbom.yaml"), show(repo, delivered, "bomdd/33-control-plan.yaml")
    ev_path = entry0["test_evidence_refs"][0]["evidence_path"]
    evidence = show(repo, RECORDS_COMMIT, ev_path).encode("utf-8")
    say(f"records {RECORDS_COMMIT} entry {ENTRY_ID}: frozen {frozen[:8]}, work order at {issued[:8]} (line {rd.frozen_revision(wo_text)!r}), "
        f"delivered {delivered[:8]} tree {entry0['delivered']['tree'][:8]}; evidence {ev_path} first line {evidence.decode().splitlines()[0][:24]}…")
    say(f"delivered copies equal the frozen revision: M-BOM {d_mbom == mbom}, Control Plan {d_cp == cp}")

    missed = 0
    with tempfile.TemporaryDirectory() as td:
        ev = Path(td) / ev_path
        ev.parent.mkdir(parents=True)
        ev.write_bytes(evidence)
        ev_sha = hashlib.sha256(evidence).hexdigest()

        r0 = rd.decide(wo_text, mbom, cp, entry0, td, (d_mbom, d_cp), gitcb)
        say(f"== N0 the records as written: {r0['result']} ({r0.get('stage')})")
        for route, text in r0.get("defects", []):
            say(f"   - [{route}] {text}")

        say("== N1 with only what distribution would add (nothing constructed, no stamp assumed):")
        cp_doc = yaml.safe_load(cp)
        cp_doc["control_plan"]["check_mapping"] = MAPPING
        cp_m = yaml.safe_dump(cp_doc, allow_unicode=True, sort_keys=False)
        say("   - Control Plan: check_mapping for the comparator's line format (the template field ECO-115 adds)")
        _, units, assembly, by_id, _ = rd.i3a(mbom, cp_m)
        named = sorted({r for u in units for r in u["acceptance_refs"]} | set(assembly["acceptance_refs"]))
        counted = [r for r in named if rd.approver_parts(by_id[r]["approver"])[0]]
        entry = copy.deepcopy(entry0)
        entry["test_evidence_refs"] = [{"source": "decision", "cp_ref": r, "evidence_path": ev_path, "evidence_sha256": ev_sha,
                                        "format": "line", "observed_at": "2026-10-25", "result": None} for r in counted]
        say(f"   - As-Built: one decision record per counted row ({len(counted)}), written by the receiving side at decision time")
        # the frozen revision with check_mapping is also what the delivery would carry once the template has the field
        # inspection r1 IA-04: the decision binds the bytes it reads to the refs' paths, so the Control Plan with the field stands for the
        # frozen revision's file wherever that file stands (the freeze, the issue and the delivery carry it unchanged)
        g1 = dict(gitcb, show=lambda c, path: (lambda got: cp_m if path == "bomdd/33-control-plan.yaml" and got == cp else got)(
            gitcb["show"](c, path)))
        r1 = rd.decide(wo_text, mbom, cp_m, entry, td, (d_mbom, cp_m), g1)
        again = rd.decide(wo_text, mbom, cp_m, entry, td, (d_mbom, cp_m), g1)
        say(f"== N1 result: {r1['result']} (run twice, byte-identical JSON: {json.dumps(r1, sort_keys=True) == json.dumps(again, sort_keys=True)})")
        for row, v in sorted((r1.get("rows") or {}).items()):
            say(f"   {row}: {v['category']} (test {v['test']}){' -> ' + v['route'] if v['route'] else ''}")
        say(f"   not decided: {json.dumps(r1.get('not_decided'))}")

        say("== N2 known-bad inputs on N1 (each must change the result for its own reason):")
        other = full(repo, "f30d771")
        cases = [
            ("a stamped evidence of another unit (stage1-check, names 0066d2b)", show(repo, RECORDS_COMMIT, "bomdd/reports/exp-20261024-01/stage1-check/compare.txt"),
             "the evidence measured another unit"),
            ("delivered.tree altered by one digit", None, "delivered.tree is not the delivered commit's tree"),
            ("frozen_commit recorded as bom-v4", None, "resolves to"),
        ]
        for name, alt_ev, expect in cases:
            e = copy.deepcopy(entry)
            if alt_ev is not None:
                b = alt_ev.encode("utf-8")
                ev.write_bytes(b)
                for rec in e["test_evidence_refs"]:
                    rec["evidence_sha256"] = hashlib.sha256(b).hexdigest()
            elif "tree" in name:
                t = e["delivered"]["tree"]
                e["delivered"]["tree"] = ("0" if t[0] != "0" else "1") + t[1:]
            else:
                v4 = full(repo, "bom-v4")
                e.update({"frozen_commit": v4, "mbom_ref": f"bomdd/32-mbom.yaml@{v4}", "control_plan_ref": f"bomdd/33-control-plan.yaml@{v4}"})
            r = rd.decide(wo_text, mbom, cp_m, e, td, (d_mbom, cp_m), g1)
            ev.write_bytes(evidence)
            text = json.dumps(r)
            missed += expect not in text
            say(f"   {'OK' if expect in text else 'MISSED'} {name}: {r['result']} "
                f"{json.dumps(r.get('defects') or sorted({v['test'] for v in (r.get('rows') or {}).values() if v['category'] != 'pass'}))[:200]}")
        del other
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    # inspection r1 IA-07: a MISSED case fails the caller, not only the text
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main())
