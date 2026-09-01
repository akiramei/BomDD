#!/usr/bin/env python3
"""process-qualification — process-core の設置・稼働適格性確認(harness ECO-015・ECO-017)

IQ(Installation Qualification)— 対象リポの実測:
  IQ-01 profile が厳格パースし必須キーを持つ
  IQ-02 hooks(pre-commit/commit-msg)が設置され、非コメント行で validator を該当モードつきで
        起動する(substring 一致でなく構造検査 — REV-05。実行の担保は OQ の実 commit 経路)
  IQ-03 core.hooksPath が対象リポ直下の bomdd/hooks へ**正準解決**される(endswith 廃止 —
        外部の …/bomdd/hooks を拒否。REV-05)
  IQ-04 hooks が実行可能(POSIX のみ — Windows は git が sh 経由で実行・残余リスクは OQ が担保)
  IQ-05 validator selftest が合格する
  IQ-06 台帳が厳格パースする
  IQ-07 HEAD が実在する(REV-06。worktree の clean は観測記録のみ — 設置直後の適格性確認は
        未コミットで走る正当経路がある: gate ① 裁定 1)
  IQ-08 入口(AGENTS.md)の相対 markdown リンク全数が実在する(ECO-023 — 空ポインタ入口は
        line ready でない。AGENTS.md 不在も FAIL)

OQ(Operational Qualification)— 使い捨て sandbox リポで実 commit 経路を実測:
  OQ-00    対照仕様(保護パスプローブ・台帳パス・状態名・trailer 名)を installed profile から
           導出(ECO-021 → ECO-024 で全面適用 — 既定値のハードコード禁止。導出不能なら明示
           FAIL し以降の OQ を実行しない)
  N19      台帳の不正化→復旧による ID 削除の洗浄を測定不能(exit 2)で止める(ECO-024 IA-01)
  N20/N20b 未コミット/index の書き戻しで HEAD の証拠欠落(E06)を隠せない(ECO-024 IA-02)
  N21      履歴走査の git 失敗を無言省略でなく測定不能(exit 2)にする(ECO-024 IA-03)

  **版の対**: OQ は sandbox へ**対象リポの installed assets** を複写して実測する。したがって
  新しい runner を古い設置 validator へ当てると新規負例が FAIL する(欠陥ではなく**版ずれ**)。
  設備更新の手順は設置物の update_note を参照(kit 再配布は既存を保持する — ECO-021)。
  POS      正常系: 起票→保護パス変更→accept trailer 付きクローズ→validate が全通過
  N1(E01)  ECO なし保護パス変更が遮断される
  N2(E02)  新規エントリの非 initial 登録が遮断される
  N3(E03)  状態の後退が遮断される
  N4(E05)  accept trailer なしの applied 遷移が遮断される
  N5(E06)  hook バイパス(--no-verify)で applied 化しても validate が検出する
  N6(IQ-03) hooksPath 無効化が IQ 検査で検出される(hook 無効の負例)
  N7(E04)  3 状態 profile で fix trailer なしの implemented 遷移が遮断される(実 Git 経路 — REV-11)
  N8(E07)  台帳に実在しない ECO への trailer を validate が検出する(実 Git 経路 — REV-11)

隔離(REV-12): sandbox の git 環境から GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE/GIT_OBJECT_*/
GIT_CONFIG_* 等を除去し、各 sandbox で実 toplevel/git-dir が sandbox 配下であることを実測する
(hook 文脈= GIT_DIR 設定下から起動されても sandbox 外へ書かない)。

決定性: full はスイート全体を --runs 回(既定 2・**2 未満は拒否**)実行し判定・理由集合の一致を
要求する。--runs 1 は iq/oq 単独のみ可で、その場合 DET は SKIP と表示する(PASS 偽装をしない —
REV-11)。想定外の通過(負例が止まらない)は 1 件で FAIL。

exit: 0=適格 / 1=不適格 / 2=測定不能(git 不在・隔離破れ等)
"""

# 検出力の限界(宣言 — ECO-044: 一次記録からの集約参照):
#   (1) IQ-04(hooks 実行可能)は POSIX のみ判定 — Windows は git が sh 経由で実行するため
#       判定対象外とし、残余リスクは OQ が担保(BomDD ECO-017 order・報告へ明示)。
#   (2) sandbox 隔離の環境変数統制は既知集合に対する allowlist/除去 — 据え置き所見
#       (GIT_TRACE 系 side channel 等)は BomDD ECO-016/017 再独立検査 NEW-05・
#       register ECO-017 追記「medium 4 件は据え置き」を参照。
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

try:
    import yaml
except ImportError:
    print("process-qualification: 測定不能 — PyYAML が必要です(pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ASSETS = ["bomdd/process-profile.yaml", "bomdd/hooks/pre-commit", "bomdd/hooks/commit-msg",
          "bomdd/tools/process-validator.py", "bomdd/tools/process-qualification.py"]
REGISTER_FALLBACK = "bomdd/60-change-register.yaml"  # profile 導出不能時の表示用のみ(検査には使わない)

# REV-12: sandbox git から除去する環境変数(前方一致 — repo/index/object/config リダイレクト系)
GIT_ENV_STRIP = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                 "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE",
                 "GIT_CONFIG")


def die(msg: str) -> "NoReturn":
    print(f"process-qualification: 測定不能 — {msg}", file=sys.stderr)
    sys.exit(2)


def _env(isolated_global: Path | None) -> dict:
    env = {k: v for k, v in os.environ.items()
           if not any(k.startswith(p) for p in GIT_ENV_STRIP)}
    if isolated_global is not None:
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

    prof_ok, prof_msg, mod = False, "", None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("pv_iq", vpath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        data = mod.strict_load((root / "bomdd" / "process-profile.yaml").read_text(encoding="utf-8"))
        errs = mod.validate_profile(data)
        prof_ok, prof_msg = not errs, "・".join(errs) or "厳格パース+スキーマ妥当"
    except Exception as e:  # noqa: BLE001 — IQ は全障害を FAIL として列挙する
        prof_msg = f"{type(e).__name__}: {e}"
    res.append(result("IQ-01", "profile 妥当", prof_ok, prof_msg))

    # ECO-019 設計確定 3: hook 起動の判定は validator 側の**単一実装**を共有する
    # (契約の判定基準を 2 箇所に置かない= silence §16(e) の自己適用)
    hooks_ok, hooks_msg = True, []
    if mod is None:
        hooks_ok = False
        hooks_msg.append("validator をロードできず hook 判定が実行不能(欠測は FAIL)")
    else:
        for h, mode in [("pre-commit", "pre-commit"), ("commit-msg", "commit-msg")]:
            p = root / "bomdd" / "hooks" / h
            if not p.is_file():
                hooks_ok = False
                hooks_msg.append(f"{h} がない")
            elif not mod.hook_invokes_validator(p, mode):
                hooks_ok = False
                hooks_msg.append(f"{h} が validator を非コメント行で起動しない(--mode {mode})")
    res.append(result("IQ-02", "hooks 設置+validator 起動(validator と共有の単一実装)", hooks_ok,
                      "・".join(hooks_msg) or "pre-commit/commit-msg とも起動行あり"))

    p = git(root, "config", "core.hooksPath")
    raw = p.stdout.strip()
    hp_ok, resolved = False, "(未設定)"
    if p.returncode == 0 and raw:
        hp = Path(raw)
        if not hp.is_absolute():
            top = git(root, "rev-parse", "--show-toplevel")
            hp = (Path(top.stdout.strip()) if top.returncode == 0 else root) / raw
        try:
            hp_ok = hp.resolve() == (root / "bomdd" / "hooks").resolve()
            resolved = hp.resolve().as_posix()
        except OSError:
            resolved = f"{raw}(解決不能)"
    res.append(result("IQ-03", "core.hooksPath が対象リポ直下 bomdd/hooks へ正準解決", hp_ok,
                      f"設定 '{raw or '(未設定)'}' — 正準比較(外部パス・endswith 一致は拒否)"))

    if os.name == "posix":
        bad = [h for h in ["pre-commit", "commit-msg"]
               if (root / "bomdd" / "hooks" / h).is_file()
               and not os.access(root / "bomdd" / "hooks" / h, os.X_OK)]
        res.append(result("IQ-04", "hooks 実行可能", not bad, f"実行不可: {bad}" if bad else "x bit あり"))
    else:
        res.append(result("IQ-04", "hooks 実行可能", True,
                          "Windows — git が sh 経由で実行(判定対象外。実行の担保は OQ の実 commit 経路)"))

    p = subprocess.run([sys.executable, str(vpath), "--mode", "selftest"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    res.append(result("IQ-05", "validator selftest 合格", p.returncode == 0,
                      (p.stdout.strip().splitlines() or ["(出力なし)"])[-1]))

    # ECO-024 IA-04: 検査対象の台帳パスも installed profile から導出する(既定のハードコードは
    # adapt 済み設備を「台帳がない」と誤 FAIL させていた)
    _spec = installed_spec(root)
    reg_rel = _spec["register"] if _spec else REGISTER_FALLBACK
    reg = root / reg_rel
    reg_ok, reg_msg = False, f"{reg_rel} がない"
    if reg.is_file():
        p = subprocess.run([sys.executable, str(vpath), "--mode", "validate", "--root", str(root)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        reg_ok = p.returncode in (0, 1)  # IQ-06 は「読める」まで(違反の有無は運用の問題)
        reg_msg = "厳格パース可" if reg_ok else f"パース不能/構造不正(exit {p.returncode})"
    res.append(result("IQ-06", "台帳が厳格パース", reg_ok, reg_msg))

    head_ok = git(root, "rev-parse", "--verify", "-q", "HEAD").returncode == 0
    dirty = bool(git(root, "status", "--porcelain").stdout.strip())
    res.append(result("IQ-07", "HEAD 実在(worktree clean は観測のみ)", head_ok,
                      f"HEAD={'あり' if head_ok else 'なし'}・worktree="
                      + ("dirty(観測記録 — 設置直後の適格性確認は正当経路のため FAIL にしない)"
                         if dirty else "clean")))

    # IQ-08(ECO-023): 入口(AGENTS.md)の相対参照 全数の実在 — 「入口から到達可能」は
    # 参照実在を含む(空ポインタ入口は line ready でない)。markdown リンクのみを対象にする
    # (機械判定可能な形の参照だけを契約とする — 散文中のパス文字列は対象外)。
    agents = root / "AGENTS.md"
    if not agents.is_file():
        res.append(result("IQ-08", "入口参照の実在(AGENTS.md)", False,
                          "AGENTS.md がない(入口不在 — 設置検査の対象)"))
    else:
        import re as _re
        links = _re.findall(r"\]\(([^)]+)\)", agents.read_text(encoding="utf-8"))
        rels = [l.split("#")[0] for l in links
                if not l.startswith(("http://", "https://", "#")) and l.split("#")[0]]
        missing = sorted({l for l in rels if not (root / l).exists()})
        res.append(result("IQ-08", "入口参照の実在(AGENTS.md)", not missing,
                          f"相対リンク {len(rels)} 件すべて実在" if not missing
                          else f"参照不在 {len(missing)} 件: {missing[:5]}"))
    return res


# --- OQ sandbox ----------------------------------------------------------------------
# ECO-024 IA-04: OQ 対照が触れる台帳パス・状態名・trailer 名の**単一入力**。run_oq 入口で
# installed profile から一度だけ導出する(対照ごとに既定値を書かない — 導出化の全面適用)。
SPEC: dict = {}


def _reg_text(status: str) -> str:
    return ("changes:\n"
            "  - id: ECO-900\n"
            "    title: OQ synthetic control\n"
            f"    status: {status}\n")


class Sandbox:
    def __init__(self, source_root: Path, base: Path, name: str,
                 profile_override: dict | None = None, defer_equipment: bool = False):
        """defer_equipment(ECO-018): 設備を後から設置する — process-core を後から導入した
        リポ(導入前に台帳履歴がある)を再現し、履歴再演が導入前を違法にしないことを測る"""
        self.root = base / name
        self.source_root = source_root
        self.profile_override = profile_override
        if not defer_equipment:
            self._copy_assets()
        (self.root / SPEC["register"]).parent.mkdir(parents=True, exist_ok=True)
        (self.root / SPEC["register"]).write_text("changes: []\n", encoding="utf-8", newline="\n")
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
        # REV-12: 隔離の実測 — 実 toplevel/git-dir が sandbox 配下であること(環境継承の穴を遮断)
        top = git(self.root, "rev-parse", "--show-toplevel", env=self.env)
        gdir = git(self.root, "rev-parse", "--absolute-git-dir", env=self.env)
        try:
            top_ok = Path(top.stdout.strip()).resolve() == self.root.resolve()
            gd = Path(gdir.stdout.strip()).resolve()
            gd_ok = str(gd).startswith(str(self.root.resolve()))
        except OSError:
            top_ok = gd_ok = False
        if not (top.returncode == 0 and gdir.returncode == 0 and top_ok and gd_ok):
            die(f"sandbox 隔離の破れ — toplevel/git-dir が sandbox 外を指す"
                f"(GIT_DIR 等の環境継承を確認): top={top.stdout.strip()!r} gitdir={gdir.stdout.strip()!r}")
        self._chmod_hooks()
        p = self.commit("oq: init")
        if p.returncode != 0:
            die(f"sandbox 初期 commit 失敗(hook 環境を確認): {p.stderr.strip()}{p.stdout.strip()}")

    def _copy_assets(self) -> None:
        for rel in ASSETS:
            src = self.source_root / rel
            if not src.is_file():
                die(f"設置済み資産がない: {src}(qualification は installed assets を対象とする)")
            dst = self.root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
        if self.profile_override:
            prof_path = self.root / "bomdd" / "process-profile.yaml"
            prof = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
            prof.update(self.profile_override)
            prof_path.write_text(yaml.safe_dump(prof, allow_unicode=True, sort_keys=False),
                                 encoding="utf-8", newline="\n")

    def _chmod_hooks(self) -> None:
        if os.name == "posix":
            for h in ["pre-commit", "commit-msg"]:
                p = self.root / "bomdd" / "hooks" / h
                if p.is_file():
                    os.chmod(p, 0o755)

    def install_equipment(self, msg: str = "chore: install process-core") -> subprocess.CompletedProcess:
        """設備を後から設置する(defer_equipment の相方 — 導入点をこの commit にする)"""
        self._copy_assets()
        self._chmod_hooks()
        return self.commit(msg)

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


def installed_spec(root: Path) -> dict | None:
    """**installed profile の単一入力**(ECO-024 IA-04 裁定 4)— OQ 対照が操作する台帳パス・
    状態名・trailer 名をすべてここから導出する。ECO-021 は同じ規律を保護パスプローブにだけ
    適用したため、register / initial / trailers が既定のまま残り、正当に adapt した設備を
    qualification が全面誤 FAIL していた(導出化の**部分適用**)。
    返す dict: register / states / initial / final / mid / trailers / probe。
    導出不能(profile 不読・必須キー欠落・protected_paths 空)は None — 呼び出し側が明示 FAIL。"""
    try:
        prof = yaml.safe_load((root / "bomdd" / "process-profile.yaml").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — profile 不読は IQ-01 が FAIL 済み。ここは導出不能として扱う
        return None
    if not isinstance(prof, dict):
        return None
    reg = prof.get("register")
    states = [s for s in prof.get("states") or [] if isinstance(s, str)]
    initial = prof.get("initial")
    trailers = prof.get("trailers") or {}
    probe = _probe_rel(root)
    if not (isinstance(reg, str) and reg.strip() and states and initial in states
            and isinstance(trailers, dict) and trailers.get("fix") and trailers.get("accept")
            and probe):
        return None
    return {"register": reg, "states": states, "initial": initial, "final": states[-1],
            # 3 状態対照用の中間状態: validator の STATE_TRAILER は状態名 'implemented'/'applied'
            # に fix/accept 意味論を固定している(profile の差分注入点ではない — 実装不変条件)
            "mid": "implemented", "trailers": dict(trailers), "probe": probe}


def _probe_rel(root: Path) -> str | None:
    """保護パスプローブの導出(ECO-021 裁定 1)— installed profile から導出する単一関数。
    OQ の保護パス対照(POS/N1/N6/N11/N18)はすべてこの結果を共有する(silence §16(e) —
    「保護パスとは何か」の解釈を 2 箇所に置かない)。既定 profile の値をハードコードすると
    adapt(差分注入)されたリポで対照が既定前提のまま空振りする(ECO-021 の欠陥)。
    規則: 先頭のディレクトリ型エントリ(末尾 /)配下にプローブファイルを合成。ディレクトリ型が
    無ければ先頭エントリ(ファイル型)をそのまま使用。**並び順が導出結果を決める(仕様)**。
    空/不在なら None(呼び出し側が明示 FAIL にする — 保護対象ゼロの line を ready と言わない)。"""
    try:
        prof = yaml.safe_load((root / "bomdd" / "process-profile.yaml").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — profile 不読は IQ-01 が FAIL 済み。ここは導出不能として扱う
        return None
    paths = [p for p in (prof or {}).get("protected_paths") or []
             if isinstance(p, str) and p.strip()]
    dirs = [p for p in paths if p.endswith("/")]
    if dirs:
        return dirs[0] + "oq-probe.txt"
    return paths[0] if paths else None


def _blocked_with(p: subprocess.CompletedProcess, code: str) -> tuple[bool, str]:
    out = (p.stderr or "") + (p.stdout or "")
    if p.returncode == 0:
        return False, "想定外の通過(exit 0)— 負例が止まらない"
    ok = f"[{code}]" in out
    return ok, (f"{code} で遮断" if ok else f"遮断されたが理由不一致(exit {p.returncode}): {out.strip()[:120]}")


def run_oq(root: Path, base: Path) -> list[dict]:
    res: list[dict] = []

    # ECO-021 → ECO-024 IA-04: 対照が触れる**全項目**(保護パスプローブ・台帳パス・状態名・
    # trailer 名)を installed profile から導出する。導出不能(protected_paths 空/不在・
    # 必須キー欠落)は明示 FAIL — 保護対象ゼロ/解釈不能な line を ready と判定しない。
    global SPEC
    spec = installed_spec(root)
    if spec is None:
        res.append(result("OQ-00", "対照仕様の導出(installed profile)", False,
                          "protected_paths 空/不在・または register/states/initial/trailers が"
                          "導出不能 — 解釈できない line を ready と判定しない(ECO-021/ECO-024)"))
        return res
    SPEC = spec
    probe = SPEC["probe"]
    res.append(result("OQ-00", "対照仕様の導出(installed profile)", True,
                      f"probe={probe}・register={SPEC['register']}・"
                      f"states={SPEC['initial']}→{SPEC['final']}・"
                      f"accept={SPEC['trailers']['accept']}"))

    s = Sandbox(root, base, "pos")
    ok_steps, detail = True, []

    def step(p: subprocess.CompletedProcess, label: str) -> None:
        nonlocal ok_steps
        if p.returncode != 0:
            ok_steps = False
            detail.append(f"{label} 失敗: {((p.stderr or '') + (p.stdout or '')).strip()[:100]}")

    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    step(s.commit("eco: file ECO-900"), "起票 commit")
    s.write(probe, "hello\n")
    step(s.commit("feat: protected change under ECO-900"), "保護パス commit")
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    step(s.commit("eco: accept ECO-900", f"{SPEC['trailers']['accept']}: ECO-900"), "accept commit")
    step(s.validate(), "validate")
    res.append(result("POS", "正常 ECO が全経路を通過", ok_steps, "・".join(detail) or "起票→保護変更→accept→validate"))

    s = Sandbox(root, base, "n1")
    s.write(probe, "x\n")
    ok, d = _blocked_with(s.commit("feat: no eco"), "E01")
    res.append(result("N1", "E01", ok, d))

    s = Sandbox(root, base, "n2")
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    ok, d = _blocked_with(s.commit("eco: born applied"), "E02")
    res.append(result("N2", "E02", ok, d))

    s = Sandbox(root, base, "n3")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    s.commit("eco: accept ECO-900", f"{SPEC['trailers']['accept']}: ECO-900")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    ok, d = _blocked_with(s.commit("eco: regress"), "E03")
    res.append(result("N3", "E03", ok, d))

    s = Sandbox(root, base, "n4")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    ok, d = _blocked_with(s.commit("eco: accept without trailer"), "E05")
    res.append(result("N4", "E05", ok, d))

    s = Sandbox(root, base, "n5")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
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
    s.write(probe, "x\n")
    slipped = s.commit("feat: no eco, hooks inactive").returncode == 0
    res.append(result("N6", "IQ-03(hook 無効の検出)", detected and slipped,
                      f"IQ-03 検出={detected}・無効時に違反 commit が素通り={slipped}(実測)"))

    # N7(E04): 3 状態 profile の実 Git 経路 — fix trailer なしの implemented 遷移(REV-11)
    s = Sandbox(root, base, "n7", profile_override={
        "states": [SPEC["initial"], SPEC["mid"], SPEC["final"]],
        "open_states": [SPEC["initial"], SPEC["mid"]]})
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    s.write(SPEC["register"], _reg_text(SPEC["mid"]))
    ok, d = _blocked_with(s.commit("eco: fix without trailer"), "E04")
    res.append(result("N7", "E04(3 状態・実 Git 経路)", ok, d))

    # N8(E07): 台帳に実在しない ECO への trailer(REV-11)
    s = Sandbox(root, base, "n8")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    p = git(s.root, "commit", "-q", "--allow-empty",
            "-m", "chore: note", "-m", f"{SPEC['trailers']['accept']}: ECO-999", env=s.env)
    if p.returncode != 0:
        res.append(result("N8", "E07", False, f"trailer commit 自体が失敗: {p.stderr.strip()[:80]}"))
    else:
        ok, d = _blocked_with(s.validate(), "E07")
        res.append(result("N8", "E07(未知 ECO への trailer)", ok, d))

    # --- ECO-018: 第 2 層(履歴合法性・設備完全性)と自己保護の負例 ---
    # N9/N14: --no-verify で born-applied+同 commit trailer → 履歴再演が E02・証拠は不採用で E06
    s = Sandbox(root, base, "n9")
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    p = s.commit("illegal: born applied", f"{SPEC['trailers']['accept']}: ECO-900", no_verify=True)
    if p.returncode != 0:
        res.append(result("N9", "E02(履歴再演)", False, f"バイパス commit 自体が失敗: {p.stderr.strip()[:80]}"))
        res.append(result("N14", "E06(違法遷移の trailer は証拠でない)", False, "N9 が実行できず未測定"))
    else:
        v = s.validate()
        ok9, d9 = _blocked_with(v, "E02")
        ok14, d14 = _blocked_with(v, "E06")
        res.append(result("N9", "E02(履歴再演 — hook 回避を第 2 層が検出)", ok9, d9))
        res.append(result("N14", "E06(違法遷移で植えた trailer は証拠に採用しない)", ok14, d14))

    # N10: --no-verify の遷移飛び越し(3 状態 staged→applied)→ 履歴再演が E03
    s = Sandbox(root, base, "n10", profile_override={
        "states": [SPEC["initial"], SPEC["mid"], SPEC["final"]],
        "open_states": [SPEC["initial"], SPEC["mid"]]})
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    p = s.commit("illegal: jump", f"{SPEC['trailers']['accept']}: ECO-900", no_verify=True)
    if p.returncode != 0:
        res.append(result("N10", "E03(履歴再演)", False, f"バイパス commit 自体が失敗: {p.stderr.strip()[:80]}"))
    else:
        ok, d = _blocked_with(s.validate(), "E03")
        res.append(result("N10", "E03(履歴再演 — 飛び越し)", ok, d))

    # N11: 同一 commit で open_states を書換え+保護パス変更 → HEAD profile 優先で E01
    s = Sandbox(root, base, "n11")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    s.commit("eco: accept ECO-900", f"{SPEC['trailers']['accept']}: ECO-900")
    prof_path = s.root / "bomdd" / "process-profile.yaml"
    prof_path.write_text(prof_path.read_text(encoding="utf-8")
                         .replace("open_states: [staged]", "open_states: [applied]"),
                         encoding="utf-8", newline="\n")
    s.write(probe, "x\n")
    ok, d = _blocked_with(s.commit("attack: self-redefine open_states"), "E01")
    res.append(result("N11", "E01(profile 自己再定義の遮断)", ok, d))

    # N12: pre-commit だけ削除 → 生き残った commit-msg が E08 を発動(冗長性)
    s = Sandbox(root, base, "n12")
    os.remove(s.root / "bomdd" / "hooks" / "pre-commit")
    ok, d = _blocked_with(s.commit("attack: remove enforcer hook"), "E08")
    res.append(result("N12", "E08(単一 hook 削除を他方が遮断)", ok, d))

    # N13: 両 hook を削除 → 第 1 層は無効・第 2 層(validate)が E10 で検出
    s = Sandbox(root, base, "n13")
    for h in ["pre-commit", "commit-msg"]:
        os.remove(s.root / "bomdd" / "hooks" / h)
    p = s.commit("attack: remove both hooks", no_verify=True)
    if p.returncode != 0:
        res.append(result("N13", "E10", False, f"削除 commit 自体が失敗: {p.stderr.strip()[:80]}"))
    else:
        ok, d = _blocked_with(s.validate(), "E10")
        res.append(result("N13", "E10(両 hook 削除を第 2 層が検出)", ok, d))

    # POS2(誤 FAIL 方向の陽性対照): 導入前の履歴を持つリポで再演・証拠要求が発火しない
    s = Sandbox(root, base, "pos2", defer_equipment=True)
    s.write(SPEC["register"], _reg_text(SPEC["final"]))  # 導入前 = trailer 規約が存在しなかった時期の記録
    p1 = s.commit("legacy: register state before adoption")
    p2 = s.install_equipment()
    v = s.validate()
    ok = p1.returncode == 0 and p2.returncode == 0 and v.returncode == 0
    res.append(result("POS2", "導入前履歴を違法にしない(誤 FAIL 方向)", ok,
                      "導入点以降のみ再演・証拠要求も導入点で区切り"
                      if ok else f"想定外の FAIL: {((v.stderr or '') + (v.stdout or '')).strip()[:140]}"))

    # --- ECO-019: 基準統一・証拠要求単位・設備無力化・保護パス履歴 ---
    # N15(IA-04): 導入前から staged の legacy ECO を導入後に applied(trailer なし)→ E06
    s = Sandbox(root, base, "n15", defer_equipment=True)
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("legacy: staged before adoption")
    s.install_equipment()
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    p = s.commit("sneak: legacy applied without trailer", no_verify=True)
    if p.returncode != 0:
        res.append(result("N15", "E06(legacy の導入後遷移)", False, f"バイパス commit 失敗: {p.stderr.strip()[:80]}"))
    else:
        ok, d = _blocked_with(s.validate(), "E06")
        res.append(result("N15", "E06(導入後の遷移は legacy ECO でも証拠要求)", ok, d))

    # N16(IA-05): 第 1 親 staged・第 2 親 applied(trailer なし)・merge に accept trailer → E06
    s = Sandbox(root, base, "n16")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    git(s.root, "checkout", "-q", "-b", "feature", env=s.env)
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    s.commit("sneak: applied without trailer", no_verify=True)
    main = "main"
    for cand in ("main", "master"):
        if git(s.root, "rev-parse", "--verify", "-q", cand, env=s.env).returncode == 0:
            main = cand
            break
    git(s.root, "checkout", "-q", main, env=s.env)
    m = git(s.root, "merge", "--no-ff", "-q", "feature", "-m", "merge feature",
            "-m", f"{SPEC['trailers']['accept']}: ECO-900", env=s.env)
    if m.returncode != 0:
        res.append(result("N16", "E06(merge の偽証拠)", False, f"merge 失敗: {m.stderr.strip()[:80]}"))
    else:
        ok, d = _blocked_with(s.validate(), "E06")
        res.append(result("N16", "E06(遷移していない merge を証拠に採用しない)", ok, d))

    # N17(IA-01): 両 hook を pass-through stub へ置換 → validate が E11
    s = Sandbox(root, base, "n17")
    for h in ["pre-commit", "commit-msg"]:
        (s.root / "bomdd" / "hooks" / h).write_text("#!/bin/sh\nexit 0\n",
                                                    encoding="utf-8", newline="\n")
    p = s.commit("attack: neuter hooks (replace, not delete)")
    if p.returncode != 0:
        res.append(result("N17", "E11(設備の無力化)", False, f"置換 commit 失敗: {p.stderr.strip()[:80]}"))
        res.append(result("N18", "E01(保護パス履歴)", False, "N17 が実行できず未測定"))
    else:
        ok, d = _blocked_with(s.validate(), "E11")
        res.append(result("N17", "E11(存在するが validator を起動しない)", ok, d))
        # N18: 無力化後の ECO なし保護パス変更 → 第 2 層(保護パス履歴検査)が E01
        s.write(probe, "x\n")
        p2 = s.commit("feat: no eco, hooks neutered")
        if p2.returncode != 0:
            res.append(result("N18", "E01(保護パス履歴)", False, f"バイパス commit 失敗: {p2.stderr.strip()[:80]}"))
        else:
            ok2, d2 = _blocked_with(s.validate(), "E01")
            res.append(result("N18", "E01(第 1 層回避後の保護パス変更を第 2 層が検出)", ok2, d2))

    # POS3(誤 FAIL 方向): 導入前に到達済みの状態は証拠を要求されない(IA-04 が免除を消しすぎない)
    s = Sandbox(root, base, "pos3", defer_equipment=True)
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    s.commit("legacy: already applied before adoption")
    s.install_equipment()
    v = s.validate()
    res.append(result("POS3", "導入点で到達済みの状態は証拠不要(誤 FAIL 方向)", v.returncode == 0,
                      "免除の単位は遷移 — 到達済み状態は対象外" if v.returncode == 0
                      else f"想定外の FAIL: {((v.stderr or '') + (v.stdout or '')).strip()[:140]}"))

    # POS4(誤 FAIL 方向): 正規 merge(両親とも合法・accept trailer つき)が通る
    s = Sandbox(root, base, "pos4")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    git(s.root, "checkout", "-q", "-b", "feature", env=s.env)
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    s.commit("eco: accept ECO-900", f"{SPEC['trailers']['accept']}: ECO-900")
    main = "main"
    for cand in ("main", "master"):
        if git(s.root, "rev-parse", "--verify", "-q", cand, env=s.env).returncode == 0:
            main = cand
            break
    git(s.root, "checkout", "-q", main, env=s.env)
    m = git(s.root, "merge", "--no-ff", "-q", "feature", "-m", "merge feature", env=s.env)
    v = s.validate()
    ok = m.returncode == 0 and v.returncode == 0
    res.append(result("POS4", "正規 merge が誤 FAIL しない(誤 FAIL 方向)", ok,
                      "合法遷移+accept 証拠が merge 後も保持される" if ok
                      else f"想定外: merge={m.returncode} validate={((v.stderr or '') + (v.stdout or '')).strip()[:120]}"))

    # --- ECO-024: 第 4R 独立検査の在庫可能分 ---
    # N19(IA-01): 台帳の不正化 → 復旧で ID 削除を洗浄できない(解析不能は測定不能 exit 2)
    s = Sandbox(root, base, "n19")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    s.write(SPEC["register"], "changes: [\n")            # 不正 YAML
    s.commit("corrupt: unparseable register", no_verify=True)
    s.write(SPEC["register"], "changes: []\n")           # 復旧(ECO-900 は消えている)
    p = s.commit("restore: empty register", no_verify=True)
    if p.returncode != 0:
        res.append(result("N19", "exit 2(台帳洗浄)", False, f"バイパス commit 失敗: {p.stderr.strip()[:80]}"))
    else:
        v = s.validate()
        out = ((v.stderr or "") + (v.stdout or "")).strip()
        marked = "解析不能" in out
        ok = v.returncode == 2 and marked
        # detail に sha を入れない(DET は判定・理由集合の一致を見る — 実行ごとに変わる値を
        # 混ぜると失敗時に決定性判定まで巻き添えで崩れる)
        res.append(result("N19", "exit 2(不正化→復旧による ID 削除の洗浄を測定不能で止める)", ok,
                          "解析不能な履歴台帳を測定不能として遮断" if ok
                          else f"想定外(exit {v.returncode}・解析不能マーカー={marked})"))

    # N20(IA-02): HEAD に trailer なし applied・worktree を initial へ書き戻し → E06 を維持
    s = Sandbox(root, base, "n20")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    s.write(SPEC["register"], _reg_text(SPEC["final"]))
    p = s.commit("sneak: applied without trailer", no_verify=True)
    if p.returncode != 0:
        res.append(result("N20", "E06(dirty worktree 隠蔽)", False, f"バイパス commit 失敗: {p.stderr.strip()[:80]}"))
    else:
        s.write(SPEC["register"], _reg_text(SPEC["initial"]))  # commit せず書き戻す(隠蔽の試み)
        ok, d = _blocked_with(s.validate(), "E06")
        res.append(result("N20", "E06(未コミットの書き戻しで HEAD の証拠欠落を隠せない)", ok, d))
        git(s.root, "add", "-A", env=s.env)                    # index へ stage しても同じ
        ok2, d2 = _blocked_with(s.validate(), "E06")
        res.append(result("N20b", "E06(index へ stage しても隠蔽できない)", ok2, d2))

    # N21(IA-03): 履歴走査の git 失敗を注入 → 無言省略でなく測定不能(exit 2)
    s = Sandbox(root, base, "n21")
    s.write(SPEC["register"], _reg_text(SPEC["initial"]))
    s.commit("eco: file ECO-900")
    shutil.rmtree(s.root / ".git" / "refs", ignore_errors=True)   # 履歴走査を失敗させる
    (s.root / ".git" / "HEAD").write_text("ref: refs/heads/broken\n", encoding="utf-8", newline="\n")
    v = s.validate()
    res.append(result("N21", "exit 2(履歴走査の git 失敗を fail-open にしない)", v.returncode == 2,
                      "測定不能として停止" if v.returncode == 2
                      else f"想定外(exit {v.returncode}): {((v.stderr or '') + (v.stdout or '')).strip()[:140]}"))
    return res


def canonical(iq: list[dict], oq: list[dict]) -> str:
    return json.dumps({"iq": iq, "oq": oq}, ensure_ascii=False, sort_keys=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="BomDD process-core qualification (IQ/OQ)")
    ap.add_argument("--root", default=".", help="対象リポ(既定: カレント)")
    ap.add_argument("--mode", default="full", choices=["full", "iq", "oq"])
    ap.add_argument("--runs", type=int, default=2,
                    help="決定性検査の実行回数(既定 2。full は 2 以上を強制 — REV-11)")
    ap.add_argument("--json", help="結果 JSON の出力先")
    a = ap.parse_args()
    if a.runs < 1:
        ap.error("--runs は 1 以上")
    if a.mode == "full" and a.runs < 2:
        ap.error("full は --runs 2 以上(決定性検査 — 1 回丸めの DET PASS 偽装をしない。REV-11)")
    # REV-12(第二面): runner 自身の子プロセス(validator selftest/validate 含む)にも
    # GIT_DIR 等を継承させない — 検査対象は --root が決める(呼出し環境のリダイレクトに従わない)。
    # hook 文脈の validator は git が正しい GIT_DIR を設定するため、ここ(runner)でのみ除去する。
    for k in list(os.environ):
        if any(k.startswith(p) for p in GIT_ENV_STRIP):
            del os.environ[k]
    root = Path(a.root).resolve()
    if not (root / "bomdd" / "process-profile.yaml").is_file():
        die(f"{root} に bomdd/process-profile.yaml がない(process-core 未設置)")

    runs: list[str] = []
    last: dict = {}
    for _ in range(a.runs):
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

    det_measured = len(runs) >= 2
    identical = len(set(runs)) == 1 if det_measured else None
    all_pass = all(r["pass"] for r in last["iq"] + last["oq"])

    print(f"process-qualification: {root}")
    for r in last["iq"] + last["oq"]:
        print(f"  [{r['control']}] {'PASS' if r['pass'] else 'FAIL'} 期待={r['expected']} — {r['detail']}")
    if det_measured:
        print(f"  [DET] {'PASS' if identical else 'FAIL'} 決定性: {len(runs)} 回実行の判定・理由集合が"
              f"{'一致' if identical else '不一致'}")
    else:
        print("  [DET] SKIP 決定性未検証(--runs 1 — PASS とは表示しない)")
    disposition = all_pass and (identical is not False)
    if a.json:
        Path(a.json).write_text(json.dumps({**last, "runs": len(runs), "runs_identical": identical,
                                            "disposition": "PASS" if disposition else "FAIL"},
                                           ensure_ascii=False, indent=1, sort_keys=True),
                                encoding="utf-8", newline="\n")
    print(f"process-qualification: {'PASS — line ready' if disposition else 'FAIL — 製造を開始しない'}")
    return 0 if disposition else 1


if __name__ == "__main__":
    sys.exit(main())
