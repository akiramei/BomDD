"""Known-bad (red-side) differential: original vs patched, same inputs, compare findings.

Nothing is written to ViewTube. Modules are loaded from source in memory; the patched copy gets
the PATCHES of patches.py. Each case prints the findings of both and SAME/DIFFERENT.
"""
import copy
import importlib.util
import runpy
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
VT = Path(r"C:\Users\akira\source\repos\ViewTube")
TOOLS = VT / "bomdd" / "tools"
S = Path(__file__).resolve().parent
PATCHES = runpy.run_path(str(S / "patches.py"))["PATCHES"]
sys.path.insert(0, str(TOOLS))


def load(module_name, file_name, patch_key=None, register_as=None):
    path = TOOLS / file_name
    source = path.read_text(encoding="utf-8")
    for old, new in (PATCHES[patch_key] if patch_key else []):
        assert source.count(old) == 1, old[:60]
        source = source.replace(old, new)
    spec = importlib.util.spec_from_loader(register_as or module_name, loader=None, origin=str(path))
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(path)
    if register_as:
        sys.modules[register_as] = module
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


results = []


def report(case, a, b):
    same = a == b
    results.append(same)
    print(f"[{'SAME' if same else 'DIFFERENT'}] {case}")
    print(f"    original: {a}")
    if not same:
        print(f"    patched : {b}")


# ---- A. record consistency: release-policy assertions, true and flipped ----------------------
import os
os.chdir(VT)
rc_o = load("rc_o", "validate_record_consistency.py")
rc_p = load("rc_p", "validate_record_consistency.py", "record_consistency")
policy = rc_o.load(rc_o.RELEASE_POLICY)


def codes(findings):
    return [(f.code, getattr(f, "statement", None) or getattr(f, "claim", None)) for f in findings]


def summary(findings):
    return sorted((f.code, str(f.__dict__.get("evidence", f.__dict__.get("measured")))) for f in findings)


variants = {"as committed": policy}
corr = policy.get("record_integrity_correction") or {}
for key in ("lifecycle_transition_performed", "validator_rule_changed"):
    if isinstance(corr.get(key), bool):
        flipped = copy.deepcopy(policy)
        flipped["record_integrity_correction"][key] = not corr[key]
        variants[f"{key} flipped (known-bad)"] = flipped
# A baseline where nothing moved (both blobs equal): the root commit's child is unlikely to stage
# the register, so pick the first commit that holds the register and its parent lacks a move.
for name, pol in variants.items():
    t0 = time.perf_counter(); fo = rc_o.check_release_policy_assertions(pol); t1 = time.perf_counter()
    fp = rc_p.check_release_policy_assertions(pol); t2 = time.perf_counter()
    report(f"A record_consistency / {name}  ({t1 - t0:.1f}s vs {t2 - t1:.1f}s)",
           [f.payload for f in fo], [f.payload for f in fp])
# Empty before-register: the original never parses the after-blob; nor must the patch.
for name, before, after in [("empty before, unparsable after", b"", b"changes: [\n"),
                            ("entries before, unparsable after", b"changes:\n- id: X\n  status: a\n", b"changes: [\n")]:
    outs = []
    for mod in (rc_o, rc_p):
        saved = mod.blob
        mod.blob = lambda rev, path, _b=before, _a=after: (_b if rev.endswith("~1") else _a) \
            if path.endswith("change-register.yaml") else saved(rev, path)
        try:
            outs.append([f.payload for f in mod.check_release_policy_assertions(policy)])
        except Exception as error:  # the exception type is part of the behaviour
            outs.append(f"raised {type(error).__name__}")
        finally:
            mod.blob = saved
    report(f"A record_consistency / {name}", outs[0], outs[1])

# ---- B. machinery claims: the qualification suite against each module ------------------------
for label, key in (("original", None), ("patched", "machinery_claims")):
    load("validate_machinery_claims", "validate_machinery_claims.py", key,
         register_as="validate_machinery_claims")
    st = load("selftest_machinery_claims", "selftest_machinery_claims.py")
    sys.argv = ["selftest_machinery_claims.py"]
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            code = st.run()
        except SystemExit as exit_:
            code = exit_.code
    lines = buf.getvalue().strip().splitlines()
    print(f"    B selftest_machinery_claims with {label} module: exit={code} | {lines[-1] if lines else ''}")
    globals()[f"b_{label}"] = (code, buf.getvalue())
report("B machinery_claims / qualification suite output", b_original, b_patched)

# ---- D. process history check: real register + known-bad synthetic entries -------------------
vp_o = load("vp_o", "validate_process.py", register_as="vp_o")
vp_p = load("vp_p", "validate_process.py", "process", register_as="vp_p")
pol = vp_o._load_yaml(VT / vp_o.POLICY_PATH)
register = vp_o._load_yaml(VT / vp_o.REGISTER_PATH)
head_register = vp_o._git_head_register(VT)
template = next(e for e in register["changes"] if e.get("status") == "applied")
bad = copy.deepcopy(register)
for fake in ("ECO-VT-999", "eco-vt-100"):          # absent id; case-variant of a present id
    entry = copy.deepcopy(template); entry["id"] = fake; bad["changes"].append(entry)
for name, reg in (("real register", register), ("register + 2 known-bad ids", bad)):
    outs = []
    for mod in (vp_o, vp_p):
        t0 = time.perf_counter()
        findings = mod.validate_register_document(
            VT, pol, reg, staged_files=[], head_register=head_register, commit_message=None,
            check_files=True, check_history=True, prospective_documents={})
        outs.append(([(f.code, f.message) for f in findings], time.perf_counter() - t0))
    report(f"D process history / {name}  ({outs[0][1]:.1f}s vs {outs[1][1]:.1f}s)",
           [x for x in outs[0][0] if 'HISTORY' in x[0]] + [len(outs[0][0])],
           [x for x in outs[1][0] if 'HISTORY' in x[0]] + [len(outs[1][0])])
    if outs[0][0] != outs[1][0]:
        print("    full finding lists differ")
        results.append(False)

print(f"\nTOTAL: {sum(results)}/{len(results)} SAME")
