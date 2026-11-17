#!/usr/bin/env python3
"""v4_route.py — BomDD ECO-126 V4: does a product scaffolded by bomdd-init accept the commit sequence of
"a change turned in rounds" (change-management §3.5) through its installed hooks and lifecycle validator?

What it does (nothing in the BomDD repo is changed except the output file next to this script):
  1. scaffolds temporary GUI products with method/tools/bomdd-init.py (the working tree's kit) into a temp dir
  2. checks the installed kit (eco-turn skill, §3.5, provisional-bundle, loop-count, handover-stamp, GU7)
  3. drives the route's commits with real `git commit` (the installed pre-commit / commit-msg hooks run):
     filing -> drawing addendum + rulings ledger (ui-cad-gate) -> candidate round 1 -> loop record ->
     candidate round 2 -> loop record -> acceptance -> loop-count --check
     `process-validator.py --mode validate` is run after every commit that passed
  4. negative control: a protected-path commit with no open ECO must be refused by E01 (before filing and after
     acceptance); control for the commit-msg hook: an acceptance without the accept trailer must be refused by E05
  5. variant B: repeats the route on a second scaffold with `ruled_layer` enabled in bomdd/process-profile.yaml, and
     adds one commit that changes a ruled-layer file the way a round's addendum would. The route as now worded
     (§3.5 "新しい望み" / eco-turn §3, repaired after the first run of this check) gives that commit the trailer
     `BomDD-ECO-Ruling: <this ECO>` and a path:line citation in the order's Sources read section — that commit is
     `B.r` and is expected to pass. The commit without the trailer, with the trailer only, and with a citation of
     another file only are expected-refusal controls (E13).
  6. variant C: a third scaffold whose profile is changed to three states (staged -> implemented -> applied, the
     qualification runner's own three-state profile) under the open ECO. The route as now worded (§4 / eco-turn §4)
     puts one `implemented` transition commit with the fix trailer between the last candidate and the acceptance.
     Controls: staged -> applied directly is refused (E03); the `implemented` transition without the fix trailer
     is refused (E04).

Line format: `PASS <id> ...` / `FAIL <id> ... — <the validator's own message>` / `NOTE ...` (observation, not a check).
A line whose description starts with "control" is an expected refusal; every other commit line is a step of the route
as worded in the installed kit, and its refusal is a FAIL.
Exit: 0 = every expectation held / 1 = at least one FAIL / 2 = the script itself could not run.

Run:  PYTHONIOENCODING=utf-8 python bomdd/reports/eco-126-loop-route/v4_route.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                       # <BomDD repo root>
OUT = HERE / "v4-output.txt"
INIT = ROOT / "method" / "tools" / "bomdd-init.py"

LINES: list[str] = []
FAILS: list[str] = []
N_CHECKS = 0
MANIFESTS: dict[str, str] = {}

ECO = "ECO-001"
ORDER = "bomdd/60-change-order-eco-001.md"
PROFILE = "bomdd/process-profile.yaml"
RECORD = "bomdd/loops/eco-001.yaml"
LEDGER = "bomdd/ui/37-ui-rulings.yaml"
ADDENDUM = "bomdd/ui/addendum-eco-001.md"
REQ = "bomdd/10-requirements.yaml"
SPEC = "bomdd/20-spec.md"
APP = "src/app.txt"
KIT_TOOLS = "bomdd-kit/method/tools"


def emit(line: str) -> None:
    LINES.append(line)
    print(line, flush=True)


def check(cid: str, ok: bool, desc: str, detail: str = "") -> bool:
    global N_CHECKS
    N_CHECKS += 1
    emit(f"{'PASS' if ok else 'FAIL'} {cid} {desc}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILS.append(cid)
    return ok


def note(text: str) -> None:
    emit(f"NOTE {text}")


def _env() -> dict:
    """Identity for the temp repos is supplied by the check itself (self-conformance `_c11_env`, ECO-020)."""
    strip = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR", "GIT_PREFIX")
    env = {k: v for k, v in os.environ.items() if k not in strip}
    env.setdefault("GIT_AUTHOR_NAME", "bomdd-v4")
    env.setdefault("GIT_AUTHOR_EMAIL", "v4@bomdd.invalid")
    env.setdefault("GIT_COMMITTER_NAME", "bomdd-v4")
    env.setdefault("GIT_COMMITTER_EMAIL", "v4@bomdd.invalid")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


ENV = _env()


def run(cmd, cwd=None, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], cwd=str(cwd) if cwd else None, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=ENV, timeout=timeout)


def out(p: subprocess.CompletedProcess) -> str:
    return (p.stdout or "") + (p.stderr or "")


def one_line(text: str, limit: int = 900) -> str:
    s = " | ".join(l.strip() for l in text.splitlines() if l.strip())
    return s if len(s) <= limit else s[:limit] + " …(cut)"


def rule_msg(p: subprocess.CompletedProcess) -> str:
    """The validator's own violation lines ([Exx] …, with their indented continuation lines). Falls back to all output."""
    keep, on = [], False
    for l in out(p).splitlines():
        if re.match(r"^\[E\d\d\]", l):
            on = True
            keep.append(l)
        elif on and l.startswith("    "):
            keep.append(l)
        else:
            on = False
    return one_line("\n".join(keep) if keep else out(p)) + f" (exit {p.returncode})"


def cleanup_tmp(tmp: Path) -> list[str]:
    """Same handling as self-conformance `_cleanup_tmp` (ECO-065): git writes read-only loose objects on Windows."""
    leftovers: list[str] = []

    def _retry(func, path, exc):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except OSError:
            if str(path) not in leftovers:
                leftovers.append(str(path))

    try:
        if sys.version_info >= (3, 12):
            shutil.rmtree(tmp, onexc=_retry)
        else:
            shutil.rmtree(tmp, onerror=lambda f, p, ei: _retry(f, p, ei[1]))
    except OSError as e:
        leftovers.append(f"{tmp}({e.__class__.__name__})")
    if tmp.exists() and str(tmp) not in leftovers:
        leftovers.append(str(tmp))
    return leftovers


class StepError(RuntimeError):
    pass


class Product:
    def __init__(self, tmp: Path, name: str):
        self.tmp, self.name, self.root = tmp, name, tmp / name
        self.msgdir = tmp / f"{name}-msgs"
        self.n_msg = 0
        self.prof: dict = {}

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return run(["git", "-C", self.root, *args])

    def head(self) -> str:
        p = self.git("rev-parse", "HEAD")
        if p.returncode != 0:
            raise StepError(f"git rev-parse HEAD failed: {one_line(out(p))}")
        return p.stdout.strip()

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def write(self, rel: str, text: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    def commit(self, paths, subject: str, *paragraphs: str) -> subprocess.CompletedProcess:
        """A real `git commit` (hooks run). Only the named paths are staged; the message goes in with -F (UTF-8)."""
        for rel in paths:
            a = self.git("add", "--", rel)
            if a.returncode != 0:
                raise StepError(f"git add {rel} failed: {one_line(out(a))}")
        self.msgdir.mkdir(parents=True, exist_ok=True)
        self.n_msg += 1
        f = self.msgdir / f"msg-{self.n_msg:02d}.txt"
        f.write_text("\n\n".join([subject, *paragraphs]) + "\n", encoding="utf-8", newline="\n")
        return self.git("commit", "-q", "-F", str(f))

    def validate(self) -> subprocess.CompletedProcess:
        return run([sys.executable, self.root / "bomdd" / "tools" / "process-validator.py",
                    "--mode", "validate", "--root", self.root])

    def tool(self, name: str, *args: str) -> subprocess.CompletedProcess:
        """A tool of the installed kit, run with the product as cwd."""
        return run([sys.executable, f"{KIT_TOOLS}/{name}", *args], cwd=self.root)

    def reset(self) -> None:
        self.git("reset", "-q", "--hard")
        self.git("clean", "-q", "-fd", "--", "src", "bomdd")

    def status_of(self, rev: str = "HEAD") -> str | None:
        p = self.git("show", f"{rev}:{self.prof['register']}")
        if p.returncode != 0:
            return None
        for e in (yaml.safe_load(p.stdout) or {}).get("changes") or []:
            if isinstance(e, dict) and e.get("id") == ECO:
                return e.get("status")
        return None


# ------------------------------------------------------------------------------------------------------------------
def scaffold(tmp: Path, name: str, cid: str) -> Product | None:
    p = run([sys.executable, INIT, name, "--dir", tmp, "--gui", "--no-qualify"])
    P = Product(tmp, name)
    if p.returncode != 0:
        check(cid, False, f"scaffold {name} with bomdd-init --gui --no-qualify", one_line(out(p)))
        return None
    hooks = P.git("config", "--get", "core.hooksPath").stdout.strip()
    head = P.git("rev-parse", "--verify", "-q", "HEAD")
    P.prof = yaml.safe_load(P.read(PROFILE))
    v = P.validate()
    lock = yaml.safe_load(P.read("bomdd.lock"))["bomdd_lock"]
    ok = head.returncode == 0 and hooks == "bomdd/hooks" and v.returncode == 0 and (tmp / f"{name}UI").is_dir()
    check(cid, ok, f"scaffold {name} with bomdd-init --gui --no-qualify",
          f"first commit {head.stdout.strip()[:9]} made with hooks on; core.hooksPath={hooks}; CAD repo created; "
          f"validate exit {v.returncode}; kit {lock['kit']['files']} files from method commit "
          f"{str(lock['method']['commit'])[:9]} dirty={lock['method']['dirty']}; states={P.prof['states']} "
          f"open_states={P.prof['open_states']} protected_paths={P.prof['protected_paths']} "
          f"structure_check={'yes' if P.prof.get('structure_check') else 'no'} "
          f"ruled_layer={'yes' if P.prof.get('ruled_layer') else 'no (commented out in the template)'}")
    # Which kit was measured: the method working tree can change between runs (and between the two scaffolds of one run),
    # so the result is tied to the sha256 the scaffold recorded for the files this check exercises.
    try:
        files = json.loads(P.read(lock["kit"]["manifest"]))["files"]
        keys = ["method/tools/ui-cad-gate.py", "method/tools/loop-count.py", "method/tools/handover-stamp.py",
                "method/tools/bomdd-init.py", "method/tools/bom-structure-check.py", "method/templates/37-ui-rulings.yaml",
                "method/templates/product-profile/change-management.md", "method/templates/product-profile/skills/eco-turn.md",
                "method/templates/process-core/tools/process-validator.py", "method/templates/process-core/process-profile.yaml",
                "method/templates/process-core/hooks/pre-commit", "method/templates/process-core/hooks/commit-msg"]
        MANIFESTS[name] = str(lock["kit"]["manifest_sha256"])[:12]
        note(f"{name} kit snapshot (sha256, first 12; manifest_sha256 {str(lock['kit']['manifest_sha256'])[:12]}): "
             + " ".join(f"{k.rsplit('/', 1)[-1]}={str(files.get(k, 'MISSING'))[:12]}" for k in keys))
    except (OSError, KeyError, ValueError) as e:
        note(f"{name} kit snapshot could not be read: {type(e).__name__}: {e}")
    return P if ok else None


def kit_checks(P: Product) -> None:
    skill = P.root / ".claude" / "skills" / "eco-turn" / "SKILL.md"
    check("K1", skill.is_file(), ".claude/skills/eco-turn/SKILL.md exists")
    cm = P.read("bomdd/change-management.md")
    check("K2", "3.5 周で回す変更" in cm, "bomdd/change-management.md contains `3.5 周で回す変更`")
    kit_led = P.read("bomdd-kit/method/templates/37-ui-rulings.yaml")
    check("K3", "provisional-bundle" in kit_led, "kit copy of 37-ui-rulings.yaml contains `provisional-bundle`",
          f"bomdd-kit/method/templates/37-ui-rulings.yaml: {kit_led.count('provisional-bundle')} occurrences; the product's own "
          f"bomdd/37-ui-rulings.yaml: {P.read('bomdd/37-ui-rulings.yaml').count('provisional-bundle')}")
    check("K4", (P.root / KIT_TOOLS / "loop-count.py").is_file(), f"kit contains {KIT_TOOLS}/loop-count.py")
    check("K5", (P.root / KIT_TOOLS / "handover-stamp.py").is_file(), f"kit contains {KIT_TOOLS}/handover-stamp.py")
    gate = P.root / KIT_TOOLS / "ui-cad-gate.py"
    check("K6", gate.is_file() and "GU7" in gate.read_text(encoding="utf-8"), f"kit contains {KIT_TOOLS}/ui-cad-gate.py with GU7")
    s1 = P.tool("loop-count.py", "--selftest")
    check("K7", s1.returncode == 0, "installed loop-count.py --selftest", one_line(out(s1)) + f" (exit {s1.returncode})")
    s2 = P.tool("ui-cad-gate.py", "--selftest")
    check("K8", s2.returncode == 0, "installed ui-cad-gate.py --selftest", one_line(out(s2)) + f" (exit {s2.returncode})")
    # The wording the route's steps below follow (the premise for calling a step "the route as worded").
    sk = skill.read_text(encoding="utf-8") if skill.is_file() else ""
    cmt = "status は変えない(遷移の trailer は付けない)"
    check("K9", cmt in cm, f"installed change-management §4 states the candidate rule ('{cmt}')")
    for cid, label, text in (("K10", "bomdd/change-management.md", cm), (
            "K11", ".claude/skills/eco-turn/SKILL.md", sk)):
        ok = "BomDD-ECO-Ruling" in text and "Sources read" in text and "ruled_layer" in text
        check(cid, ok, f"installed {label} names the ruling trailer (BomDD-ECO-Ruling) and the Sources read citation for a "
                       f"ruled-layer change in a product with ruled_layer")
    for cid, label, text in (("K12", "bomdd/change-management.md", cm), (
            "K13", ".claude/skills/eco-turn/SKILL.md", sk)):
        ok = "staged → implemented → applied" in text and "`implemented` への遷移" in text
        check(cid, ok, f"installed {label} names the `implemented` transition commit (fix trailer) for a three-state product")


def passed_commit(P: Product, cid: str, desc: str, p: subprocess.CompletedProcess, extra: str = "") -> bool:
    """A commit the route expects to pass: exit 0, then validate (second layer) exit 0 on the new HEAD."""
    if p.returncode != 0:
        return check(cid, False, desc, "REFUSED: " + rule_msg(p))
    v = P.validate()
    ok = v.returncode == 0
    subj = P.git("log", "-1", "--format=%h %s").stdout.strip()
    return check(cid, ok, desc, f"commit {subj}; validate exit {v.returncode}"
                 + ("" if ok else " " + rule_msg(v)) + (f"; {extra}" if extra else ""))


def refused_commit(P: Product, cid: str, desc: str, p: subprocess.CompletedProcess, code: str, needle: str = "") -> bool:
    """A control / probe that must be refused by a named rule (the rule id must be in the output — a hook that
    cannot find python also exits non-zero)."""
    o = out(p)
    ok = p.returncode != 0 and f"[{code}]" in o and (needle in o)
    if p.returncode == 0:
        detail = "NOT refused (exit 0) — the commit went through"
        P.git("reset", "-q", "--soft", "HEAD~1")   # keep the route's premise: the commit must not exist
    else:
        detail = "refused: " + rule_msg(p)
    return check(cid, ok, desc, detail)


def neg_e01(P: Product, cid: str, when: str) -> None:
    P.write("src/v4-no-eco.txt", f"a protected change with no open ECO ({when})\n")
    p = P.commit(["src/v4-no-eco.txt"], "feat: protected change with no open ECO")
    refused_commit(P, cid, f"negative control ({when}): a commit under {P.prof['protected_paths'][0]} with no open ECO "
                           f"is refused by E01", p, "E01")
    P.reset()


def sha256(P: Product, rel: str) -> str:
    return hashlib.sha256((P.root / rel).read_bytes()).hexdigest()


def register_text(P: Product, status: str, approved: bool) -> str:
    head, sep, _ = P.read(P.prof["register"]).partition("\nchanges:\n")
    if not sep:
        raise StepError("the register template has no `changes:` line")
    entry = (f"  - id: {ECO}\n"
             f"    title: \"V4 probe — a change turned in rounds (周で回す変更)\"\n"
             f"    date: \"{date.today().isoformat()}\"\n"
             f"    origin: requirement\n"
             f"    status: {status}\n"
             f"    order_ref: {ORDER}\n"
             f"    summary: \"ECO-126 V4 の合成の変更。周で回す(上限 3 周)と起票時に名指した。\"\n")
    if approved:
        entry += (f"    golden: \"approved({date.today().isoformat()} v4-probe 実機: 確認項目 H1 合格・"
                  f"未解決の報告 U-1 を名指しで受け入れ)\"\n")
    return head + "\nchanges:\n" + entry


def order_text(state: str) -> str:
    return (f"# {ECO} — V4 probe: a change turned in rounds ({state})\n\n"
            "> 経路: change-management §3.5(周で回す変更)。gate① で「周で回す」と名指し(合成の記録)。\n\n"
            "## 1. 変更要求(原文)\n- 「一覧を使いやすくしたい」(方向・数行)\n\n"
            "## 2. 起きてはならないことの一覧\n- 利用者のデータを書き換えない\n\n"
            "## 3. 受入基準\n- 確認項目 H1 が合格\n\n"
            "## 4. 周の上限と費用の枠\n- 周の上限: 3\n- 別セッションの費用の枠: 0(合成)\n")


UI_FILES = {
    "bomdd/ui/ui-ir.json": '{"actions": [{"uiId": "action.v4.one"}], "inputs": []}\n',
    "bomdd/ui/ui-bom.json": '{"items": []}\n',
    "bomdd/ui/ui-trace-map.json": '{"mappings": []}\n',
    "bomdd/ui/36-ui-dictionary.yaml": "actions: {}\n",
}
_CONFIRMED = ("rulings:\n"
              "  - id: UQ-V4-1\n    status: ruled\n    target: {ui_ids: [\"action.v4.one\"]}\n"
              "    question: 人が決めた裁定\n    ruling: keep\n    decided_by: user\n")
LEDGER_OPEN = (_CONFIRMED +
               "  - id: UQ-V4-2\n    status: open\n    type: provisional-bundle\n    blocking: false\n"
               "    target: {ui_ids: [\"action.v4.one\"]}\n    question: 図面の追補で [仮] の印が付いた決定を、そのままでよいか\n"
               "    confirmed_checked: [{id: UQ-V4-1, touches: no, why: \"並び順だけを決めた — UQ-V4-1 の意味は変えない\"}]\n")
LEDGER_CLOSED = (_CONFIRMED +
                 "  - id: UQ-V4-2\n    status: ruled\n    type: provisional-bundle\n    blocking: false\n"
                 "    target: {ui_ids: [\"action.v4.one\"]}\n    question: 図面の追補で [仮] の印が付いた決定を、そのままでよいか\n"
                 "    ruling: accept-as-built\n    decided_by: producer\n"
                 "    confirmed_checked: [{id: UQ-V4-1, touches: no, why: \"並び順だけを決めた — UQ-V4-1 の意味は変えない\"}]\n"
                 "    evidence:\n      - \"確認項目が覆った決定: 並び順(H1)\"\n      - \"作ったままの決定: 既定値\"\n")
ADDENDUM_TEXT = ("# 図面の追補 — ECO-001 周 1\n\n"
                 "- [裁定] 一覧の操作 action.v4.one は残す(UQ-V4-1)\n"
                 "- [仮] 並び順は新しい順\n- [仮] 既定値は 10 件\n")


def gate(P: Product) -> subprocess.CompletedProcess:
    return P.tool("ui-cad-gate.py", "--ui-dir", "bomdd/ui")


def record_text(P: Product, rounds: list[dict], final: bool) -> str:
    doc = {
        "schema": "loop-record/0.1-candidate", "eco": ECO, "limits": {"rounds": 3},
        "rounds": rounds,
        "items": [
            {"id": "P-1", "round": 1, "source": "producer", "kind": "provisional", "disposition": "to_user_check",
             "channel": "H1", "outcome": "diff" if final else "pending"},
            {"id": "Q-1", "round": 1, "source": "reader", "kind": "preread", "disposition": "not_asked",
             "why": "役割が 1 通りにしか読めない足し物だった"},
        ],
        "reactions": ([{"id": "X1", "round": 1, "words": "新しい順より、名前の順がよい", "kind": "pass_but", "kind_by": "user",
                        "class": "decision_change", "lands_on": ["P-1"], "listed_before_use": "yes"}] if final else []),
        "reports": ([{"id": "U-1", "accepted": "yes", "named_in": "U-1 を受け入れる"}] if final else []),
    }
    return yaml.safe_dump(doc, allow_unicode=True, sort_keys=False)


def round_row(P: Product, n: int, commit: str, reply: str | None) -> dict:
    row = {"n": n, "set": {"commit": commit, "files": {APP: sha256(P, APP)}},
           "handed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "repairs": {"fixed_after_reproduction": 0, "patched_without_reproduction": 0}}
    if reply:
        row["reply"] = {"words": reply}
    return row


def enable_ruled_layer(P: Product, cid: str) -> bool:
    since = P.head()
    text = P.read(PROFILE)
    pat = re.compile(r"^# ruled_layer:\n#   since:[^\n]*\n#   paths:[^\n]*\n", re.M)
    if len(pat.findall(text)) != 1:
        raise StepError("the commented ruled_layer example was not found exactly once in the installed profile")
    block = (f"ruled_layer:\n  since: \"{since}\"   # 欄を足すときの HEAD(V4 probe — 設計リリースの tag は無い)\n"
             f"  paths: [{REQ}, {SPEC}]\n")
    P.write(PROFILE, pat.sub(lambda _m: block, text, count=1))
    p = P.commit([PROFILE], "equipment(eco-001): ruled_layer を有効にする(since = 欄を足すときの HEAD)")
    ok = passed_commit(P, cid, f"enable ruled_layer in {PROFILE} under the open {ECO} (E08 asks for an open ECO; since = the "
                               f"full SHA of the HEAD it is added on; paths = [{REQ}, {SPEC}])", p,
                       f"since {since[:9]}")
    if ok:
        P.prof = yaml.safe_load(P.read(PROFILE))
    return ok


def ruled_change(P: Product, L: str) -> None:
    """One commit that changes a ruled-layer file the way a round's addendum would (a new want added to the requirements)."""
    ruling = P.prof["trailers"].get("ruling", "BomDD-ECO-Ruling")
    text = P.read(REQ) + "# ECO-001 周 2 の新しい望み(発話つき): 「新しい順より、名前の順がよい」 — V4 probe\n"
    line_no = len(text.splitlines())
    P.write(REQ, text)
    subject = "fix(eco-001): 周 2 追補 — 新しい望みを要求の表に足す"
    # --- controls first (expected refusals): each leaves the change staged, so the route's own commit below is the
    # same change with what the installed wording asks for ---
    p = P.commit([REQ], subject)
    refused_commit(P, f"{L}.r.ctl", f"control (E13 is armed): the ruled-layer change ({REQ}) with no ruling trailer and no "
                                    f"Sources read section is refused by E13", p, "E13", "ruling trailer が無い")
    p = P.commit([], subject, f"{ruling}: {ECO}")
    refused_commit(P, f"{L}.r.ctl2", f"control: the same change + trailer `{ruling}: {ECO}` only (the order still has no "
                                     f"Sources read section) is refused by E13", p, "E13", "Sources read 節が無い")
    order = P.read(ORDER)
    P.write(ORDER, order + f"\n## Sources read\n- `{SPEC}:1` — 仕様の見出し(この周では変えない)\n")
    p = P.commit([ORDER], subject, f"{ruling}: {ECO}")
    refused_commit(P, f"{L}.r.ctl3", f"control: + a `## Sources read` section in {ORDER} that cites another file only "
                                     f"(`{SPEC}:1`) is refused by E13", p, "E13", "引用数 0")
    # --- the route as now worded (§3.5 新しい望み / eco-turn §3): trailer + path:line citation, on the round's commit ---
    P.write(ORDER, P.read(ORDER) + f"- `{REQ}:{line_no}` — 周 1 の返事で出た新しい望みを足す行\n")
    p = P.commit([ORDER], subject, f"{ruling}: {ECO}")
    ok = passed_commit(P, f"{L}.r", f"ruled-layer change ({REQ}) as the route now words it: trailer `{ruling}: {ECO}` ({ECO} "
                                    f"open in the parent's register) + the order's `Sources read` cites `{REQ}:{line_no}`, the "
                                    f"order staged in the same commit", p)
    if not ok:
        P.reset()


def enable_three_states(P: Product, cid: str) -> bool:
    """states [staged, implemented, applied] / open_states [staged, implemented] — the three-state profile the
    qualification runner itself uses (its N7 / N10 controls). The profile is equipment: the change goes through E08."""
    text = P.read(PROFILE)
    pats = [(r"^states: \[staged, applied\]$", "states: [staged, implemented, applied]"),
            (r"^open_states: \[staged\](?=\s)", "open_states: [staged, implemented]")]
    for pat, rep in pats:
        if len(re.findall(pat, text, re.M)) != 1:
            raise StepError(f"the installed profile does not have exactly one line matching {pat!r}")
        text = re.sub(pat, rep, text, count=1, flags=re.M)
    P.write(PROFILE, text)
    p = P.commit([PROFILE], "equipment(eco-001): 状態を 3 つにする(staged → implemented → applied)")
    ok = passed_commit(P, cid, f"change {PROFILE} to three states under the open {ECO} (E08 asks for an open ECO; the new "
                               f"rules apply from the next commit — the HEAD profile is the rule)", p)
    if ok:
        P.prof = yaml.safe_load(P.read(PROFILE))
        ok = check(cid + ".read", P.prof["states"] == ["staged", "implemented", "applied"]
                   and P.prof["open_states"] == ["staged", "implemented"],
                   "the committed profile reads back as three states",
                   f"states={P.prof['states']} open_states={P.prof['open_states']} trailers.fix={P.prof['trailers']['fix']}")
    return ok


def route(P: Product, L: str, ruled: bool = False, three: bool = False) -> None:
    initial, final_state = P.prof["initial"], P.prof["states"][-1]
    accept_tr, fix_tr = P.prof["trailers"]["accept"], P.prof["trailers"]["fix"]
    reg = P.prof["register"]

    neg_e01(P, f"{L}.neg1", "before filing")

    # a. filing — register entry in the initial status + the order, committed alone
    P.write(reg, register_text(P, initial, approved=False))
    P.write(ORDER, order_text(initial))
    p = P.commit([reg, ORDER], "起票(eco-001): V4 probe — 周で回す変更を起票(上限 3 周)")
    if not passed_commit(P, f"{L}.a", f"filing: {ECO} in status '{initial}' + {ORDER}, committed alone", p):
        raise StepError("filing was refused — the rest of the route cannot be driven")

    if ruled and not enable_ruled_layer(P, f"{L}.rl"):
        raise StepError("ruled_layer could not be enabled — the variant cannot be driven")
    if three and not enable_three_states(P, f"{L}.p3"):
        raise StepError("the three-state profile could not be set up — the variant cannot be driven")

    # b. drawing addendum + rulings ledger with an open provisional-bundle; the gate; the commit
    for rel, body in UI_FILES.items():
        P.write(rel, body)
    P.write(LEDGER, LEDGER_OPEN)
    P.write(ADDENDUM, ADDENDUM_TEXT)
    g = gate(P)
    other = [l for l in g.stdout.splitlines() if "] FAIL " in l]
    last = (g.stdout.strip().splitlines() or [""])[-1]
    check(f"{L}.b.gate", g.returncode == 0 and "[GU7] PASS" in g.stdout and not other,
          "ui-cad-gate.py --ui-dir bomdd/ui with an open provisional-bundle: exit 0 and [GU7] PASS",
          f"exit {g.returncode}; [GU7] PASS present={'[GU7] PASS' in g.stdout}; FAIL lines={len(other)}; last line: {last}")
    p = P.commit([*UI_FILES, LEDGER, ADDENDUM], "decide(eco-001): 周 1 — 図面の追補と裁定台帳(仮の決定の束)")
    passed_commit(P, f"{L}.b", "drawing addendum + rulings ledger under bomdd/ui/ (no trailer)"
                  + (f" — with ruled_layer on, this shows bomdd/ui/ is not a ruled-layer path in paths=[{REQ}, {SPEC}]"
                     if ruled else ""), p)

    # c. candidate, round 1 — protected path, status unchanged, no trailer
    P.write(APP, "round 1\n")
    p = P.commit([APP], "fix(eco-001): 周 1 候補 — 仮の決定で作った最初の版")
    passed_commit(P, f"{L}.c", f"candidate commit, round 1: {APP} (protected), no trailer", p,
                  f"{ECO} status in HEAD = '{P.status_of()}' (unchanged)")
    c1 = P.head()

    # d. loop record (round 1) -> candidate round 2 -> loop record (round 2)
    P.write(RECORD, record_text(P, [round_row(P, 1, c1, None)], final=False))
    p = P.commit([RECORD], "record(eco-001): 周 1 の記録(版の組・渡した時刻)")
    lc = P.tool("loop-count.py", "--check", RECORD)
    passed_commit(P, f"{L}.d.rec1", f"loop record {RECORD} (round 1) committed", p,
                  f"loop-count --check exit {lc.returncode}")

    if ruled:
        ruled_change(P, L)

    P.write(APP, "round 2\n")
    p = P.commit([APP], "fix(eco-001): 周 2 候補 — 反応 X1(並び順)を受けた直し")
    passed_commit(P, f"{L}.d.cand2", f"candidate commit, round 2: {APP} (protected), no trailer", p,
                  f"{ECO} status in HEAD = '{P.status_of()}' (unchanged)")
    c2 = P.head()
    rows = [round_row(P, 1, c1, "新しい順より、名前の順がよい"), round_row(P, 2, c2, "合格")]
    rows[0]["set"]["files"][APP] = hashlib.sha256(P.git("show", f"{c1}:{APP}").stdout.encode("utf-8")).hexdigest()
    P.write(RECORD, record_text(P, rows, final=True))
    p = P.commit([RECORD], "record(eco-001): 周 2 の記録(返事・反応の種類・未解決の報告の名指し)")
    passed_commit(P, f"{L}.d.rec2", f"loop record {RECORD} (round 2) committed", p)

    if three:
        # control: the two-state shape of the acceptance (staged -> applied in one step) is a skipped stage here
        P.write(reg, register_text(P, final_state, approved=True))
        p = P.commit([reg], "accept(eco-001): golden 合格 — V4 probe(implemented を置かずに applied へ)", f"{accept_tr}: {ECO}")
        refused_commit(P, f"{L}.e03.ctl", f"control: '{initial}' -> '{final_state}' directly (accept trailer present, no "
                                          f"`implemented` commit) is refused by E03", p, "E03", "飛び越し")
        P.reset()
        # the route as now worded (§4 / eco-turn §4): one `implemented` transition commit with the fix trailer, after the
        # user's "合格" on a candidate and before the confirmation items are handed over
        P.write(reg, register_text(P, "implemented", approved=False))
        subject = "fix(eco-001): 周 2 の候補を implemented にする(人の「合格」の後・確認項目を渡す前)"
        p = P.commit([reg], subject)
        refused_commit(P, f"{L}.e04.ctl", f"control: the `implemented` transition without `{fix_tr}: {ECO}` is refused by E04",
                       p, "E04")
        p = P.commit([], subject, f"{fix_tr}: {ECO}")
        passed_commit(P, f"{L}.impl", f"the `implemented` transition commit: {ECO} '{initial}' -> 'implemented' with the trailer "
                                      f"`{fix_tr}: {ECO}` (register only, no product code)", p,
                      f"{ECO} status in HEAD = '{P.status_of()}'")
    before = P.status_of()

    # e. acceptance — the bundle is closed, the gate is run again, the status moves with the accept trailer
    P.write(LEDGER, LEDGER_CLOSED)
    g = gate(P)
    last = (g.stdout.strip().splitlines() or [""])[-1]
    check(f"{L}.e.gate", g.returncode == 0, "ui-cad-gate.py after the bundle is closed (eco-turn R3 / R4): exit 0",
          f"exit {g.returncode}; GU7 listed={'[GU7]' in g.stdout} (no open bundle -> GU7 does not run); last line: {last}")
    P.write(reg, register_text(P, final_state, approved=True))
    P.write(ORDER, P.read(ORDER).replace(f"({initial})", f"({final_state})", 1)
            + "\n## クローズ\n- 実機確認: 確認項目 H1 合格・未解決の報告 U-1 を名指しで受け入れ(合成)\n- 教訓: なし(V4 probe)\n")
    paths = [reg, ORDER, LEDGER]
    subject = "accept(eco-001): golden 合格 — V4 probe(周 2 で「合格」・確認項目 H1 合格)"
    p = P.commit(paths, subject)
    refused_commit(P, f"{L}.e.ctl", f"control (commit-msg hook is active): the acceptance commit without `{accept_tr}: {ECO}` "
                                    f"is refused by E05", p, "E05")
    if P.prof.get("structure_check"):
        s = run([sys.executable, P.root / P.prof["structure_check"], "--root", P.root, "--index"])
        verdict = next((l for l in s.stdout.splitlines() if l.startswith("verdict:")), "")
        note(f"{L}: bom-structure-check.py --root . --index on the staged acceptance: exit {s.returncode} — {verdict[:140]}")
    p = P.commit([], subject, f"{accept_tr}: {ECO}")
    e12 = one_line("\n".join(l for l in out(p).splitlines() if "[E12]" in l or l.startswith("    ")), 300)
    passed_commit(P, f"{L}.e", f"acceptance: {ECO} '{before}' -> '{final_state}' with the trailer `{accept_tr}: {ECO}` in the "
                               f"final trailer block", p,
                  f"{ECO} status in HEAD = '{P.status_of()}'; hook output: {e12 or '(no [E12] line)'}")
    v = P.validate()
    okline = next((l for l in v.stdout.splitlines() if "validate OK" in l), "")
    scope = next((l for l in v.stdout.splitlines() if "[scope]" in l), "")
    check(f"{L}.e.validate", v.returncode == 0 and bool(okline),
          "process-validator.py --mode validate on the finished history (replay of every transition, protected-path "
          "change" + (" and ruled-layer change" if ruled else "") + ")",
          one_line(scope + "\n" + okline) if v.returncode == 0 else rule_msg(v))

    # f. loop-count --check on the final record
    lc = P.tool("loop-count.py", "--check", RECORD)
    gaps = next((l for l in lc.stdout.splitlines() if l.startswith("gaps:")), "")
    check(f"{L}.f", lc.returncode == 0, f"{KIT_TOOLS}/loop-count.py --check {RECORD} on the final record: exit 0",
          f"exit {lc.returncode}; {(lc.stdout.splitlines() or [''])[0]}; {gaps}")

    neg_e01(P, f"{L}.neg2", f"after acceptance — {ECO} is '{final_state}', nothing is open")

    if ruled:
        # control: `validate exit 0` above says something about E13 only if the replay reports a ruled-layer change that
        # skipped the hooks. Made last, so it changes nothing the route's lines measured.
        P.write(REQ, P.read(REQ) + "# a ruled-layer change made with the hooks skipped — V4 control\n")
        P.git("add", "--", REQ)
        p = P.git("commit", "-q", "--no-verify", "-m", "control: ruled-layer change with the hooks skipped")
        v = P.validate()
        sha = P.head()[:9]
        ok = p.returncode == 0 and v.returncode == 1 and "[E13]" in out(v) and f"history:{sha}" in out(v)
        check(f"{L}.replay.ctl", ok, "control (the second layer is armed for E13): a ruled-layer change committed with "
                                     "--no-verify and no trailer is reported by validate", "reported: " + rule_msg(v))

    dirty = P.git("status", "--porcelain").stdout.strip()
    log = P.git("log", "--reverse", "--format=%h %s").stdout.strip().splitlines()
    note(f"{L}: history ({len(log)} commits, working tree {'clean' if not dirty else 'NOT clean: ' + one_line(dirty, 200)}): "
         + " / ".join(log))


def main() -> int:
    emit(f"v4_route: ECO-126 V4 — the route's commit sequence through the installed hooks and lifecycle validator "
         f"({date.today().isoformat()})")
    gv = run(["git", "--version"])
    if gv.returncode != 0:
        emit("FAIL env git cannot be run — the hooks cannot be driven")
        return 2
    mc = run(["git", "-C", ROOT, "rev-parse", "HEAD"]).stdout.strip()
    note(f"environment: {gv.stdout.strip()}; python {sys.version.split()[0]}; {sys.platform}; method repo HEAD {mc[:9]} "
         f"(the kit is copied from the working tree, uncommitted changes included)")
    note("history of this check: the first result (2026-11-17, kit manifest 93faf84a9895, before the route text was repaired) "
         "had B.r REFUSED by E13 — the ruled-layer change as the route was then worded (§3.5 / §4: no ruling trailer, no Sources "
         "read) met `[E13] ruled-layer-change-without-ruling: … ruling trailer が無い`; every other route commit passed. "
         "§3.5 / eco-turn §3 now name the trailer and the citation, so B.r below is the commit with both, and the no-trailer "
         "commit is kept as the control B.r.ctl. Variant C (three states) was added in the same revision of this script.")
    tmp = Path(tempfile.mkdtemp(prefix="bomdd-v4-"))
    try:
        emit("== Variant A: the scaffolded profile as installed (2 states, ruled_layer not enabled) ==")
        A = scaffold(tmp, "V4RouteA", "A.scaffold")
        if A is not None:
            kit_checks(A)
            try:
                route(A, "A", ruled=False)
            except StepError as e:
                check("A.abort", False, "variant A stopped", str(e))
        emit("== Variant B: the same route with ruled_layer enabled (E13) ==")
        B = scaffold(tmp, "V4RouteB", "B.scaffold")
        if B is not None:
            try:
                route(B, "B", ruled=True)
            except StepError as e:
                check("B.abort", False, "variant B stopped", str(e))
        emit("== Variant C: the same route on a three-state profile (staged -> implemented -> applied; E03 / E04) ==")
        C = scaffold(tmp, "V4RouteC", "C.scaffold")
        if C is not None:
            try:
                route(C, "C", three=True)
            except StepError as e:
                check("C.abort", False, "variant C stopped", str(e))
        ids = {p.name: m for p, m in ((x, MANIFESTS.get(x.name)) for x in (A, B, C) if x is not None)}
        same = len(set(ids.values())) == 1 and len(ids) == 3
        note(f"kit manifest the run is bound to: {ids} — {'one kit for all three scaffolds' if same else 'NOT one kit: the method working tree changed during the run (or a scaffold failed)'}")
    finally:
        left = cleanup_tmp(tmp)
        note("cleanup: temp directory removed" if not left else f"cleanup: {len(left)} path(s) could not be removed: {left[:3]}")
    emit(f"SUMMARY V4: {N_CHECKS} checks — PASS {N_CHECKS - len(FAILS)} / FAIL {len(FAILS)}"
         + (f" {FAILS}" if FAILS else "")
         + f" — exit {1 if FAILS else 0}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    rc = 2
    try:
        rc = main()
    except Exception as e:  # noqa: BLE001 — a crash is reported in the output file, not hidden
        emit(f"FAIL script crashed: {type(e).__name__}: {e}")
        rc = 2
        raise
    finally:
        OUT.write_bytes(("\n".join(LINES) + "\n").encode("utf-8"))
    sys.exit(rc)
