#!/usr/bin/env python3
"""process-qualification — process-core の設置・稼働適格性確認(harness ECO-015)

IQ(Installation Qualification)— 対象リポの実測:
  IQ-01 profile が厳格パースし必須キーを持つ
  IQ-02 hooks(pre-commit/commit-msg)が設置され validator を参照する
  IQ-03 core.hooksPath が hooks ディレクトリへ解決される(ファイル存在≠有効化)
  IQ-04 hooks が実行可能(POSIX のみ — Windows は git が sh 経由で実行)
  IQ-05 validator selftest が合格する
  IQ-06 台帳が厳格パースする

OQ(Operational Qualification)— 使い捨て sandbox リポで実 commit 経路を実測:
  POS      正常系: 起票→保護パス変更→accept trailer 付きクローズ→validate が全通過
  N1(E01)  ECO なし保護パス変更が遮断される
  N2(E02)  新規エントリの非 initial 登録が遮断される
  N3(E03)  状態の後退が遮断される
  N4(E05)  accept trailer なしの applied 遷移が遮断される
  N5(E06)  hook バイパス(--no-verify)で applied 化しても validate が検出する
  N6(IQ-03) hooksPath 無効化が IQ 検査で検出される(hook 無効の負例)

決定性: スイート全体を --runs 回(既定 2)実行し、判定・理由集合の一致を要求する。
想定外の通過(負例が止まらない)は 1 件で FAIL(ViewTube CAPA-VT-002 AC-PORT-011 の一般形)。

exit: 0=適格 / 1=不適格 / 2=測定不能(git 不在等)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ASSETS = ["bomdd/process-profile.yaml", "bomdd/hooks/pre-commit", "bomdd/hooks/commit-msg",
          "bomdd/tools/process-validator.py"]
REGISTER = "bomdd/60-change-register.yaml"  # sandbox 用(対象リポの profile とは独立の既定)


def die(msg: str) -> "NoReturn":
    print(f"process-qualification: 測定不能 — {msg}", file=sys.stderr)
    sys.exit(2)


def _env(isolated_global: Path | None) -> dict:
    env = dict(os.environ)
    if isolated_global is not None:
        # sandbox はユーザー/システム git 設定から隔離(gpgsign・hooks templatedir 等の交絡排除)
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        env["GIT_CONFIG_GLOBAL"] = str(isolated_global)
    return env


def git(cwd: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True,
                              text=True, encoding="utf-8", errors="replace", env=env)
    except OSError as e:
        die(f"git を実行できない: {e}")


def result(name: str, expected: str, ok: bool, detail: str) -> dict:
    return {"control": name, "expected": expected, "pass": bool(ok), "detail": detail}


# --- IQ ------------------------------------------------------------------------------
def run_iq(root: Path) -> list[dict]:
    res: list[dict] = []
    vpath = root / "bomdd" / "tools" / "process-validator.py"

    prof_ok, prof_msg = False, ""
    try:
        prof = (root / "bomdd" / "process-profile.yaml")
        import importlib.util
        spec = importlib.util.spec_from_file_location("pv_iq", vpath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        data = mod.strict_load(prof.read_text(encoding="utf-8"))
        missing = [k for k in mod.REQUIRED_KEYS if k not in data]
        prof_ok, prof_msg = not missing, f"必須キー欠落: {missing}" if missing else "厳格パース+必須キー"
    except Exception as e:  # noqa: BLE001 — IQ は全障害を FAIL として列挙する
        prof_msg = f"{type(e).__name__}: {e}"
    res.append(result("IQ-01", "profile 妥当", prof_ok, prof_msg))

    hooks_ok, hooks_msg = True, []
    for h in ["pre-commit", "commit-msg"]:
        p = root / "bomdd" / "hooks" / h
        if not p.is_file():
            hooks_ok, _ = False, hooks_msg.append(f"{h} がない")
        elif "process-validator.py" not in p.read_text(encoding="utf-8", errors="replace"):
            hooks_ok, _ = False, hooks_msg.append(f"{h} が validator を参照しない")
    res.append(result("IQ-02", "hooks 設置+validator 参照", hooks_ok,
                      "・".join(hooks_msg) or "pre-commit/commit-msg"))

    p = git(root, "config", "core.hooksPath")
    hp = p.stdout.strip().replace("\\", "/")
    hp_ok = p.returncode == 0 and (hp == "bomdd/hooks" or hp.endswith("/bomdd/hooks"))
    res.append(result("IQ-03", "core.hooksPath=bomdd/hooks", hp_ok,
                      f"実測 '{hp or '(未設定)'}'(ファイル存在は有効化の証拠にならない)"))

    if os.name == "posix":
        bad = [h for h in ["pre-commit", "commit-msg"]
               if (root / "bomdd" / "hooks" / h).is_file()
               and not os.access(root / "bomdd" / "hooks" / h, os.X_OK)]
        res.append(result("IQ-04", "hooks 実行可能", not bad, f"実行不可: {bad}" if bad else "x bit あり"))
    else:
        res.append(result("IQ-04", "hooks 実行可能", True, "Windows — git が sh 経由で実行(判定対象外)"))

    p = subprocess.run([sys.executable, str(vpath), "--mode", "selftest"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    res.append(result("IQ-05", "validator selftest 合格", p.returncode == 0,
                      (p.stdout.strip().splitlines() or ["(出力なし)"])[-1]))

    reg = root / REGISTER
    reg_ok, reg_msg = False, f"{REGISTER} がない"
    if reg.is_file():
        p = subprocess.run([sys.executable, str(vpath), "--mode", "validate", "--root", str(root)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        reg_ok = p.returncode in (0, 1)  # IQ-06 は「読める」まで(違反の有無は運用の問題)
        reg_msg = "厳格パース可" if reg_ok else f"パース不能(exit {p.returncode})"
    res.append(result("IQ-06", "台帳が厳格パース", reg_ok, reg_msg))
    return res


# --- OQ sandbox ----------------------------------------------------------------------
def _reg_text(status: str) -> str:
    return ("changes:\n"
            "  - id: ECO-900\n"
            "    title: OQ synthetic control\n"
            f"    status: {status}\n")


class Sandbox:
    def __init__(self, source_root: Path, base: Path, name: str):
        self.root = base / name
        for rel in ASSETS:
            src = source_root / rel
            if not src.is_file():
                die(f"設置済み資産がない: {src}(qualification は installed assets を対象とする)")
            dst = self.root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
        (self.root / REGISTER).write_text("changes: []\n", encoding="utf-8", newline="\n")
        self.gcfg = base / f"{name}.gitconfig"
        self.gcfg.write_text("", encoding="utf-8")
        self.env = _env(self.gcfg)
        for args in [("init", "-q"), ("config", "user.name", "bomdd-oq"),
                     ("config", "user.email", "oq@bomdd.invalid"),
                     ("config", "commit.gpgsign", "false"),
                     ("config", "core.hooksPath", "bomdd/hooks")]:
            p = git(self.root, *args, env=self.env)
            if p.returncode != 0:
                die(f"sandbox git {args} 失敗: {p.stderr.strip()}")
        if os.name == "posix":
            for h in ["pre-commit", "commit-msg"]:
                os.chmod(self.root / "bomdd" / "hooks" / h, 0o755)
        p = self.commit("oq: init")
        if p.returncode != 0:
            die(f"sandbox 初期 commit 失敗(hook 環境を確認): {p.stderr.strip()}{p.stdout.strip()}")

    def write(self, rel: str, text: str) -> None:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")

    def commit(self, *msgs: str, no_verify: bool = False) -> subprocess.CompletedProcess:
        git(self.root, "add", "-A", env=self.env)
        args = ["commit", "-q"] + (["--no-verify"] if no_verify else [])
        for m in msgs:
            args += ["-m", m]
        return git(self.root, *args, env=self.env)

    def validate(self) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(self.root / "bomdd" / "tools" / "process-validator.py"),
                               "--mode", "validate", "--root", str(self.root)],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")


def _blocked_with(p: subprocess.CompletedProcess, code: str) -> tuple[bool, str]:
    out = (p.stderr or "") + (p.stdout or "")
    if p.returncode == 0:
        return False, f"想定外の通過(exit 0)— 負例が止まらない"
    ok = f"[{code}]" in out
    return ok, (f"{code} で遮断" if ok else f"遮断されたが理由不一致(exit {p.returncode}): {out.strip()[:120]}")


def run_oq(root: Path, base: Path) -> list[dict]:
    res: list[dict] = []

    s = Sandbox(root, base, "pos")
    ok_steps, detail = True, []

    def step(p: subprocess.CompletedProcess, label: str) -> None:
        nonlocal ok_steps
        if p.returncode != 0:
            ok_steps = False
            detail.append(f"{label} 失敗: {((p.stderr or '') + (p.stdout or '')).strip()[:100]}")

    s.write(REGISTER, _reg_text("staged"))
    step(s.commit("eco: file ECO-900"), "起票 commit")
    s.write("src/a.txt", "hello\n")
    step(s.commit("feat: protected change under ECO-900"), "保護パス commit")
    s.write(REGISTER, _reg_text("applied"))
    step(s.commit("eco: accept ECO-900", "BomDD-ECO-Accept: ECO-900"), "accept commit")
    step(s.validate(), "validate")
    res.append(result("POS", "正常 ECO が全経路を通過", ok_steps, "・".join(detail) or "起票→保護変更→accept→validate"))

    s = Sandbox(root, base, "n1")
    s.write("src/a.txt", "x\n")
    ok, d = _blocked_with(s.commit("feat: no eco"), "E01")
    res.append(result("N1", "E01", ok, d))

    s = Sandbox(root, base, "n2")
    s.write(REGISTER, _reg_text("applied"))
    ok, d = _blocked_with(s.commit("eco: born applied"), "E02")
    res.append(result("N2", "E02", ok, d))

    s = Sandbox(root, base, "n3")
    s.write(REGISTER, _reg_text("staged"))
    s.commit("eco: file ECO-900")
    s.write(REGISTER, _reg_text("applied"))
    s.commit("eco: accept ECO-900", "BomDD-ECO-Accept: ECO-900")
    s.write(REGISTER, _reg_text("staged"))
    ok, d = _blocked_with(s.commit("eco: regress"), "E03")
    res.append(result("N3", "E03", ok, d))

    s = Sandbox(root, base, "n4")
    s.write(REGISTER, _reg_text("staged"))
    s.commit("eco: file ECO-900")
    s.write(REGISTER, _reg_text("applied"))
    ok, d = _blocked_with(s.commit("eco: accept without trailer"), "E05")
    res.append(result("N4", "E05", ok, d))

    s = Sandbox(root, base, "n5")
    s.write(REGISTER, _reg_text("staged"))
    s.commit("eco: file ECO-900")
    s.write(REGISTER, _reg_text("applied"))
    p = s.commit("eco: bypass applied(conversational OK)", no_verify=True)
    if p.returncode != 0:
        res.append(result("N5", "E06", False, f"バイパス commit 自体が失敗: {p.stderr.strip()[:80]}"))
    else:
        ok, d = _blocked_with(s.validate(), "E06")
        res.append(result("N5", "E06", ok, d))

    s = Sandbox(root, base, "n6")
    git(s.root, "config", "--unset", "core.hooksPath", env=s.env)
    iq3 = [r for r in run_iq(s.root) if r["control"] == "IQ-03"][0]
    detected = not iq3["pass"]
    # バイパスの実在も観測(hook 無効なら E01 相当が素通りする — IQ-03 が必要な理由)
    s.write("src/a.txt", "x\n")
    slipped = s.commit("feat: no eco, hooks inactive").returncode == 0
    res.append(result("N6", "IQ-03(hook 無効の検出)", detected and slipped,
                      f"IQ-03 検出={detected}・無効時に違反 commit が素通り={slipped}(実測)"))
    return res


def canonical(iq: list[dict], oq: list[dict]) -> str:
    return json.dumps({"iq": iq, "oq": oq}, ensure_ascii=False, sort_keys=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="BomDD process-core qualification (IQ/OQ)")
    ap.add_argument("--root", default=".", help="対象リポ(既定: カレント)")
    ap.add_argument("--mode", default="full", choices=["full", "iq", "oq"])
    ap.add_argument("--runs", type=int, default=2, help="決定性検査の実行回数(既定 2)")
    ap.add_argument("--json", help="結果 JSON の出力先")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    if not (root / "bomdd" / "process-profile.yaml").is_file():
        die(f"{root} に bomdd/process-profile.yaml がない(process-core 未設置)")

    runs: list[str] = []
    last: dict = {}
    for i in range(max(1, a.runs)):
        iq = run_iq(root) if a.mode in ("full", "iq") else []
        oq = []
        if a.mode in ("full", "oq"):
            base = Path(tempfile.mkdtemp(prefix="bomdd-oq-"))
            try:
                oq = run_oq(root, base)
            finally:
                shutil.rmtree(base, ignore_errors=True)
        runs.append(canonical(iq, oq))
        last = {"iq": iq, "oq": oq}

    identical = len(set(runs)) == 1
    all_pass = all(r["pass"] for r in last["iq"] + last["oq"])

    print(f"process-qualification: {root}")
    for r in last["iq"] + last["oq"]:
        print(f"  [{r['control']}] {'PASS' if r['pass'] else 'FAIL'} 期待={r['expected']} — {r['detail']}")
    print(f"  [DET] {'PASS' if identical else 'FAIL'} 決定性: {len(runs)} 回実行の判定・理由集合が"
          f"{'一致' if identical else '不一致'}")
    disposition = all_pass and identical
    if a.json:
        Path(a.json).write_text(json.dumps({**last, "runs": len(runs), "runs_identical": identical,
                                            "disposition": "PASS" if disposition else "FAIL"},
                                           ensure_ascii=False, indent=1, sort_keys=True),
                                encoding="utf-8", newline="\n")
    print(f"process-qualification: {'PASS — line ready' if disposition else 'FAIL — 製造を開始しない'}")
    return 0 if disposition else 1


if __name__ == "__main__":
    sys.exit(main())
