"""EXP-20261025-02 driver: calibrate the scanner (preregistration 6), and only if both arms give exactly their expected output, scan
MoviePad-Remake delivery 1. Read-only on the product (git show / ls-tree at the delivered commit).

  python -B run_exp.py <MoviePad-Remake checkout> <output file>
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import scan_deps as sd  # noqa: E402

DELIVERED = "f30d771"


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout.decode("utf-8")


def delivery(repo):
    mbom = yaml.safe_load(git(repo, "show", f"{DELIVERED}:bomdd/32-mbom.yaml"))
    paths = [p for p in git(repo, "ls-tree", "-r", "--name-only", DELIVERED).splitlines() if p.endswith(".cs")]
    return mbom, {p: git(repo, "show", f"{DELIVERED}:{p}") for p in paths}


def fixture():
    def unit(uid, files, provides, requires):
        return {"id": uid, "planned_output_artifact_ref": files,
                "part_standard": {"provides": [{"id": f"PS-{uid}-P01"}] if provides else [],
                                  "requires": [{"id": f"PS-{uid}-R{i:02}", "target": f"PS-{t}-P01"} for i, t in enumerate(requires, 1)]},
                "depends_on": requires}
    mbom = {"mbom": {"manufacturing_units": [unit("M-A", "src/A/Alpha.cs", True, ["M-B"]), unit("M-B", "src/B/Beta.cs", True, ["M-C"]),
                                             unit("M-C", "src/C", True, [])]}}
    files = {
        "src/A/Alpha.cs": ('namespace X.A;\n// Gamma is mentioned in a comment only\n/* Gamma again */\npublic sealed class Alpha {\n'
                           '    public Beta B = new Beta();\n    public string S = "Gamma in a string";\n    public string V = @"Gamma ""quoted"" verbatim";\n'
                           '    public string I => $"Delta {Gamma.Value} {{Delta}}";\n}\n'),
        "src/B/Beta.cs": "namespace X.B;\npublic sealed record Beta(int N = 0);\n",
        "src/C/Gamma.cs": "namespace X.C;\npublic static class Gamma { public const int Value = 1; }\n",
        "src/D/Delta.cs": "namespace X.D;\npublic sealed class Delta { }\n",
    }
    # Gamma's only code reference is inside an interpolation hole (must count); Delta appears only in the interpolated text (must not)
    mbom["mbom"]["manufacturing_units"].append(unit("M-D", "src/D/Delta.cs", True, []))
    expected = {"M-A -> M-B": "declared-used", "M-A -> M-C": "undeclared", "M-B -> M-C": "declared-unused"}
    return mbom, files, expected


def verdicts(report):
    return {k: v[0] for k, v in report["pairs"].items()}


def main():
    repo, out_path = sys.argv[1], sys.argv[2]
    lines = []
    say = lines.append
    # arm 1: synthetic fixture with known labels
    mbom, files, expected = fixture()
    r = sd.scan(mbom, files)
    got = verdicts(r)
    where = r["pairs"].get("M-A -> M-C", ("", []))[1]
    arm1 = got == expected and where == ["src/A/Alpha.cs:Gamma"] and not r["unowned"] and not r["ambiguous_files"]
    say(f"calibration arm 1 (synthetic fixture): {'OK' if arm1 else 'FAILED'} got {json.dumps(got, sort_keys=True)}; A->C found at {where}")
    # arm 2: the real delivery with one undeclared reference added to History.cs
    mbom, files = delivery(repo)
    base = sd.scan(mbom, files)
    altered = dict(files)
    hist = "src/MoviePad.Core/Editing/History.cs"
    altered[hist] = files[hist] + "\ninternal static class CalibrationProbe { internal const double X = TimeMath.MinLen; }\n"
    r2 = sd.scan(mbom, altered)
    diff = {k: v for k, v in verdicts(r2).items() if verdicts(base).get(k) != v}
    arm2 = diff == {"M-HISTORY-001 -> M-DOCUMENT-001": "undeclared"}
    say(f"calibration arm 2 (delivery + one undeclared reference in History.cs): {'OK' if arm2 else 'FAILED'} difference from the unaltered scan {json.dumps(diff, sort_keys=True)}")
    if not (arm1 and arm2):
        say("calibration failed: the delivery is not read (preregistration 6)")
    else:
        say(f"== delivery {DELIVERED}")
        for uid, ps in base["units"].items():
            say(f"   unit {uid}: {len(ps)} file(s)")
        say(f"   unowned .cs files: {base['unowned']}")
        say(f"   files owned by two units: {base['ambiguous_files']}")
        say(f"   type names declared in two units (not attributed): {base['ambiguous_types']}")
        say(f"   units whose depends_on differs from their resolved requires: {base['depends_on_differs']}")
        for scope, test in (("production units (src/)", lambda k: "M-SELF-ACCEPTANCE-001" not in k.split(" -> ")[0]),
                            ("self-acceptance unit (test/), reported apart", lambda k: k.startswith("M-SELF-ACCEPTANCE-001 "))):
            say(f"== {scope}")
            counts = {}
            for k, (v, where) in base["pairs"].items():
                if not test(k):
                    continue
                counts[v] = counts.get(v, 0) + 1
                shown = ", ".join(where[:6]) + (f", … ({len(where)} in all)" if len(where) > 6 else "")
                say(f"   {v:16} {k}" + (f"   [{shown}]" if where else ""))
            say(f"   counts: {json.dumps(counts, sort_keys=True)}")
        again = sd.scan(mbom, files)
        say(f"== run twice, byte-identical JSON: {json.dumps(again, sort_keys=True) == json.dumps(base, sort_keys=True)}")
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
