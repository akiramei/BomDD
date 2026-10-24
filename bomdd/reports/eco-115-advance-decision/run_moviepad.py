"""ECO-115 redesign evidence: the advance decision (rehearse_decision_v2) on MoviePad-Remake's real per-delivery records from
EXP-20261024-01 delivery 1 — the first records with an issued work order, a frozen revision and an As-Built entry.

  python -B run_moviepad.py <MoviePad-Remake checkout> <output file>

Inputs, all read from git in that checkout (nothing is edited there):
  the work order as issued      bomdd/40-work-order.md at 7824ba9 (its line names the tag bom-v4)
  the frozen BOM and CP         bomdd/32-mbom.yaml, bomdd/33-control-plan.yaml at bom-v4
  the delivery's copies         the same paths at the delivered commit f30d771
  the As-Built entry            bomdd/50-as-built.yaml at e1d71b3 (AB-FORWARD-01-factory-01)
  the evidence                  bomdd/reports/exp-20261024-01/delivery-1/compare.txt at e1d71b3
Runs: M0 the records as the current templates left them; M1 a migrated copy (each edit listed); M2 known-bad freezes.
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

WO_COMMIT, DELIVERED_COMMIT, RECORDS_COMMIT, TAG = "7824ba9", "f30d771", "e1d71b3", "bom-v4"
EVIDENCE = "bomdd/reports/exp-20261024-01/delivery-1/compare.txt"


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
             "is_ancestor": lambda a, b: git(repo, "merge-base", "--is-ancestor", a, b)[0] == 0}
    wo_full, delivered, frozen = full(repo, WO_COMMIT), full(repo, DELIVERED_COMMIT), full(repo, TAG)
    tree = git(repo, "rev-parse", f"{DELIVERED_COMMIT}^{{tree}}")[1].decode().strip()
    wo_text = show(repo, wo_full, "bomdd/40-work-order.md")
    mbom, cp = show(repo, frozen, "bomdd/32-mbom.yaml"), show(repo, frozen, "bomdd/33-control-plan.yaml")
    d_mbom, d_cp = show(repo, delivered, "bomdd/32-mbom.yaml"), show(repo, delivered, "bomdd/33-control-plan.yaml")
    asbuilt = yaml.safe_load(show(repo, RECORDS_COMMIT, "bomdd/50-as-built.yaml"))
    entry0 = asbuilt["as_built"][0]
    evidence = show(repo, RECORDS_COMMIT, EVIDENCE).encode("utf-8")
    say(f"work order as issued {wo_full[:8]} (line names {rd.frozen_revision(wo_text)!r}); frozen {TAG} = {frozen[:8]}; delivered {delivered[:8]} tree {tree[:8]}")
    say(f"delivered copies equal the frozen revision: M-BOM {d_mbom == mbom}, Control Plan {d_cp == cp}")

    with tempfile.TemporaryDirectory() as td:
        ev = Path(td) / EVIDENCE
        ev.parent.mkdir(parents=True)
        ev.write_bytes(evidence)
        ev_sha = hashlib.sha256(evidence).hexdigest()

        # M0: the records as they are
        r0 = rd.decide(wo_text, mbom, cp, entry0, td, (d_mbom, d_cp), gitcb)
        say(f"== M0 the records as the current templates left them: {r0['result']} ({r0.get('stage')})")
        for route, text in r0.get("defects", []):
            say(f"   - [{route}] {text}")

        # M1: a migrated copy
        say("== M1 migration (each edit is a decision a distribution ECO would make, listed):")
        cp_doc = yaml.safe_load(cp)
        cp_doc["control_plan"]["check_mapping"] = {"line": {"row_key": "token2", "outcomes": {"PASS": "passed", "FAIL": "failed"},
                                                             "identity": r"(?m)^MEASURED_ON (?P<commit>[0-9a-f]{40}) (?P<tree>[0-9a-f]{40})$"}}
        say("   - Control Plan: check_mapping {line: row_key token2, PASS->passed, FAIL->failed, identity: a line 'MEASURED_ON <commit> <tree>'}"
            " (compare.py's output format; compare.py writes no such line today)")
        cp_m = yaml.safe_dump(cp_doc, allow_unicode=True, sort_keys=False)
        entry = {k: v for k, v in entry0.items() if k not in ("test_evidence_refs",)}
        entry.update({"frozen_commit": frozen, "work_order_ref": f"bomdd/40-work-order.md@{wo_full}",
                      "mbom_ref": f"bomdd/32-mbom.yaml@{frozen}", "control_plan_ref": f"bomdd/33-control-plan.yaml@{frozen}",
                      "delivered": {"commit": delivered, "tree": tree}})
        say("   - As-Built: frozen_commit (bom-v4 resolved at receipt), refs as <path>@<40-hex>, delivered {commit, tree}")
        _, units, assembly, by_id, _ = rd.i3a(mbom, cp_m)
        named = sorted({r for u in units for r in u["acceptance_refs"]} | set(assembly["acceptance_refs"]))
        counted = [r for r in named if rd.approver_parts(by_id[r]["approver"])[0]]
        entry["test_evidence_refs"] = [{"source": "decision", "cp_ref": r, "evidence_path": EVIDENCE, "evidence_sha256": ev_sha,
                                        "format": "line", "observed_at": "2026-10-24", "result": None} for r in counted]
        say(f"   - As-Built: one decision record per counted row ({len(counted)}), all naming compare.txt")
        r1a = rd.decide(wo_text, mbom, cp_m, entry, td, (d_mbom, cp_m), gitcb)
        say(f"== M1a the migrated copy, compare.txt as it is: {r1a['result']}")
        cats = {}
        for row, v in sorted((r1a.get("rows") or {}).items()):
            cats.setdefault(f"{v['category']} (test {v['test']})", []).append(row)
        for k, v in sorted(cats.items()):
            say(f"   {k}: {len(v)}")
        # the stamp compare.py would write if the identity rule were adopted; ASSUMED — the inspection ran on the f30d771 tree
        # (inspect.sh, git diff clean), but nothing in compare.txt says so (M1 L4)
        evidence = evidence + f"MEASURED_ON {delivered} {tree}\n".encode()
        ev.write_bytes(evidence)
        ev_sha = hashlib.sha256(evidence).hexdigest()
        for rec in entry["test_evidence_refs"]:
            rec["evidence_sha256"] = ev_sha
        say("   - M1b: compare.txt with a line 'MEASURED_ON <f30d771> <tree>' appended — ASSUMED, as compare.py would stamp its run")
        r1 = rd.decide(wo_text, mbom, cp_m, entry, td, (d_mbom, cp_m), gitcb)
        say(f"== M1b the migrated copy, stamped (ASSUMED): {r1['result']}")
        for row, v in sorted((r1.get("rows") or {}).items()):
            say(f"   {row}: {v['category']} (test {v['test']}){' -> ' + v['route'] if v['route'] else ''}")
        say(f"   not decided: {json.dumps(r1.get('not_decided'))}")
        for route, text in r1.get("defects", []):
            say(f"   - [{route}] {text}")

        # M2: known-bad freezes on the migrated copy
        say("== M2 known-bad freezes (each must be input-defect for its stated reason):")
        cases = [
            ("frozen_commit is the delivered commit", {"frozen_commit": delivered, "mbom_ref": f"bomdd/32-mbom.yaml@{delivered}",
                                                       "control_plan_ref": f"bomdd/33-control-plan.yaml@{delivered}"}, None, "frozen_commit is the delivered commit"),
            ("the work order named at a commit after the delivery", {"work_order_ref": f"bomdd/40-work-order.md@{full(repo, RECORDS_COMMIT)}"}, None,
             "the work order's commit is not an ancestor"),
            ("frozen_commit recorded as bom-v3 while the line names bom-v4", {"frozen_commit": full(repo, "bom-v3"),
                                                                             "mbom_ref": f"bomdd/32-mbom.yaml@{full(repo, 'bom-v3')}",
                                                                             "control_plan_ref": f"bomdd/33-control-plan.yaml@{full(repo, 'bom-v3')}"}, None,
             "not the recorded frozen_commit"),
            ("a FAIL line for one row in the evidence", {}, b"FAIL CP-EDIT-001 injected\n", "violation"),
        ]
        for name, edit, extra, expect in cases:
            e = copy.deepcopy(entry)
            e.update(edit)
            if extra:
                bad = evidence + extra
                ev.write_bytes(bad)
                for rec in e["test_evidence_refs"]:
                    rec["evidence_sha256"] = hashlib.sha256(bad).hexdigest()
            r = rd.decide(wo_text, mbom, cp_m, e, td, (d_mbom, cp_m), gitcb)
            ev.write_bytes(evidence)
            text = json.dumps(r)
            ok = expect in text and (r["result"] == "input-defect" or expect == "violation")
            say(f"   {'OK' if ok else 'MISSED'} {name}: {r['result']} {json.dumps(r.get('defects') or {k: v for k, v in (r.get('rows') or {}).items() if v['category'] != 'pass'})[:220]}")
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
