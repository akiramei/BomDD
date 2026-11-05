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
  IQ-09 (profile に structure_check がある場合のみ — ECO-118)構造検査の道具が実在し selftest が通る

OQ(Operational Qualification)— 使い捨て sandbox リポで実 commit 経路を実測:
  OQ-00    対照仕様(保護パスプローブ・台帳パス・状態名・trailer 名)を installed profile から
           導出(ECO-021 → ECO-024 で全面適用 — 既定値のハードコード禁止。導出不能なら明示
           FAIL し以降の OQ を実行しない)
  N19      台帳の不正化→復旧による ID 削除の洗浄を測定不能(exit 2)で止める(ECO-024 IA-01)
  N20/N20b 未コミット/index の書き戻しで HEAD の証拠欠落(E06)を隠せない(ECO-024 IA-02)
  N21      履歴走査の git 失敗を無言省略でなく測定不能(exit 2)にする(ECO-024 IA-03)
  N23a〜z2 (ECO-119)E13: 設計リリースを main に置き、後の profile commit で ruled_layer を SHA で足して実測 —
           リリース前・欄を足す前は検査しない・trailer なし / 台帳に無い ID を含む・閉じた・指示書なし・Sources read
           なし・引用 0・削除・rename out・エディタのコメント塊・-m の `#` 段落は遮断・open+引用は通過・裁定層に
           触れない commit は対象外・merge(リリース前の枝・欄の無い枝へ main・リリース後の枝は trailer で通過)・
           --no-verify / 日本語のパス / merge / fast-forward を履歴の再演がちょうどその commit で検出・since の不解決と
           系列外は遮断・tag 名の since は profile 不正・欄なしは E13 なし。round 3: merge で欄を落とす・octopus の
           台帳は遮断・欄を消して戻した間と読めない profile の直後は再演が検出・paths を広げた commit は報告しない
           (N23x・u・y・z・z2)・裁定 B: 単独の commit で変えた欄を取り込む merge は両方向とも通し、どの親にも無い
           欄を merge で作ると遮断(N23x2・x3・x4)。round 4: 狭めて戻した間は再演が検出(N23z4)。round 5(裁定 B —
           項目ごとの since・HEAD の欄だけで判定・profile の履歴は読まない): since は欄を足すときの HEAD で、戻すと前の
           commit も判定(N23p・p2)・項目を足す commit がその下を作ると index の欄で遮断/--no-verify なら再演が報告
           (N23z2・z2r)・形の正しくない項目を足す commit は測定不能で止める(N23z3・z3b)・綴りを変えて戻した間・末尾の
           / つきのファイルの項目を再演が検出(N23z6・z8)・profile を戻す commit の変更を遮断(N23z9)・since で分かれた
           枝からの -s ours を遮断(N23x5)・{path, since} で足した項目は前を判定しない/パスだけに書き換えると判定する
           (N23z5・z5b・z7)・項目の since の不解決を遮断(N23n2)
  N22a〜k  (profile に structure_check がある場合のみ — ECO-118)E12: FAIL の BOM の受入は遮断・
           NOT-APPLICABLE は通して名前を出す・遷移のない途中の commit は止めない・PASS は通す・
           道具の不在と解析できない M-BOM は遮断・欄を外せば E12 は無い・受入 commit の --amend も
           遮断(エディタを開く amend も — N22i・コメント文字の設定 auto / commentString でも — N22j/k)(sandbox 1 本)。
           sandbox には道具と、道具の fixture で PASS する BOM を置く(既存の受入対照のため)

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
import re
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
FIXTURE_MBOM = "bomdd/32-mbom.yaml"  # N22f が壊す M-BOM(構造検査の道具が読む 3 ファイルの 1 つ・ECO-118)

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

    # IQ-09(ECO-118): profile に structure_check があるときだけ — 道具が実在し、自己検査が通る
    # (欄があって道具が無い設備は、E12 が受入遷移をすべて遮断する= fail-closed の設定ずれ)
    rel = _structure_rel(root)
    if rel:
        tool = root / rel
        if not tool.is_file():
            res.append(result("IQ-09", "構造検査の道具の実在+selftest", False, f"{rel} がない"))
        else:
            p = subprocess.run([sys.executable, str(tool), "--selftest"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            res.append(result("IQ-09", "構造検査の道具の実在+selftest", p.returncode == 0,
                              (p.stdout.strip().splitlines() or ["(出力なし)"])[-1]))
    return res


def _structure_rel(root: Path) -> str | None:
    """profile の structure_check(ECO-118)。無ければ None — E12 の対照は、その設備が無い line に作らない。"""
    try:
        prof = yaml.safe_load((root / "bomdd" / "process-profile.yaml").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — profile 不読は IQ-01 が FAIL 済み
        return None
    sc = prof.get("structure_check") if isinstance(prof, dict) else None
    return sc if isinstance(sc, str) and sc else None


_FIXTURES: dict = {}


def structure_fixture(tool: Path, name: str) -> dict | None:
    """道具自身の selftest fixture(--write-fixture)を {相対パス: bytes} で返す — BOM の写しを
    qualification に二重に持たない。書けなければ None。"""
    key = (str(tool), name)
    if key not in _FIXTURES:
        d = Path(tempfile.mkdtemp(prefix="bomdd-oq-fx-"))
        try:
            p = subprocess.run([sys.executable, str(tool), "--write-fixture", name, str(d)],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            _FIXTURES[key] = ({f.relative_to(d).as_posix(): f.read_bytes() for f in d.rglob("*") if f.is_file()}
                              if p.returncode == 0 else None)
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return _FIXTURES[key]


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
        # ECO-118: profile に structure_check があれば、道具と、それが PASS する BOM(道具の fixture)を
        # 置く — 置かなければ E12 が受入遷移のある対照(POS 等)を「道具が無い」で遮断する
        rel = _structure_rel(self.root)
        if rel and (self.source_root / rel).is_file():
            dst = self.root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes((self.source_root / rel).read_bytes())
            for r, b in (structure_fixture(self.source_root / rel, "good") or {}).items():
                (self.root / r).parent.mkdir(parents=True, exist_ok=True)
                (self.root / r).write_bytes(b)

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

    # --- ECO-118: E12(受入遷移での BOM 構造検査の再計算)— profile に structure_check がある設備だけ ---
    rel = _structure_rel(root)
    if rel:
        res += _oq_structure(root, base, rel)
    # --- ECO-119: E13(裁定層の保護)— 欄は製品が設計リリースで書くので、sandbox の profile に足して実測する ---
    res += _oq_ruled_layer(root, base)
    return res


def _oq_ruled_layer(root: Path, base: Path) -> list[dict]:
    """N23a〜z9(ECO-119 V2 の腕を qualification に入れ子で — a〜w と c2・n2・p2・x・x2〜x5・y・z・z2・z2r・z3・z3b・z4〜z9・
    z5b・u の 44 本に、round 6 の e2・fr・v2・x6・z3c・z9b を足した 50 本)。sandbox 1 本で順に。
    欄なしの対照は別 sandbox。
    設計リリースは main の上(実製品 MoviePad-Remake と同じ形 — R8-1-01)・欄は後の profile commit で SHA として足す
    (裁定 2:A)・trailer 名は installed profile から(ECO-024 — R8-1-07)。"""
    res: list[dict] = []
    spec_p, adr1, adr2 = "bomdd/20-spec.md", "bomdd/adr/ADR-1.md", "bomdd/adr/ADR-2.md"
    adr3, adr4, adr_jp = "bomdd/adr/ADR-3.md", "bomdd/adr/ADR-4.md", "bomdd/adr/ADR-日本.md"
    s = Sandbox(root, base, "n23")
    acc = SPEC["trailers"]["accept"]
    ruling = SPEC["trailers"].get("ruling") or "BomDD-ECO-Ruling"
    prof_rel = "bomdd/process-profile.yaml"
    prof_path = s.root / prof_rel
    main = git(s.root, "rev-parse", "--abbrev-ref", "HEAD", env=s.env).stdout.strip() or "main"

    def out(p: subprocess.CompletedProcess) -> str:
        return (p.stdout or "") + (p.stderr or "")

    def head() -> str:
        return git(s.root, "rev-parse", "HEAD", env=s.env).stdout.strip()

    def commit_paths(*msgs: str, add=(), rm=(), env=None, extra=()) -> subprocess.CompletedProcess:
        for a in add:
            git(s.root, "add", "--", a, env=s.env)
        for r in rm:
            git(s.root, "rm", "-q", "--cached", "--", r, env=s.env)
        args = ["commit", "-q", *extra]
        for m in msgs:
            args += ["-m", m]
        return git(s.root, *args, env=env or s.env)

    def undo() -> None:
        git(s.root, "reset", "-q", "--hard", env=s.env)   # merge の途中(MERGE_HEAD)も消える
        git(s.root, "clean", "-q", "-fd", "--", "bomdd/", env=s.env)

    def passed(name: str, expected: str, p: subprocess.CompletedProcess) -> None:
        ok = p.returncode == 0 and "[E13]" not in out(p)
        res.append(result(name, expected, ok, "通過" if ok else f"想定外(exit {p.returncode}): {out(p).strip()[:140]}"))

    def refused(name: str, expected: str, p: subprocess.CompletedProcess, needle: str = "") -> None:
        ok, d = _blocked_with(p, "E13")
        ok = ok and (needle in out(p))
        res.append(result(name, expected, ok, d + (f"・{needle} を表示" if needle and ok else "")))
        if p.returncode == 0:   # 遮断されるはずの commit / merge が通った(検証器の欠陥)— 後の腕の前提を変えないよう取り消す
            git(s.root, "reset", "-q", "--hard", "HEAD~1", env=s.env)
        undo()

    def set_ruled_layer(since: str, msg: str) -> subprocess.CompletedProcess:
        prof = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
        prof["ruled_layer"] = {"since": since, "paths": [spec_p, "bomdd/adr"]}   # 'bomdd/adr' は / なしでも下に当たる
        prof_path.write_text(yaml.safe_dump(prof, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
        return commit_paths(msg, add=(prof_rel,))

    # --- 準備: 設計リリースより前(欄なし)— Phase 3 の変更と、リリースより前に分かれる枝 2 本 ---
    file40 = "bomdd/40-file.md"   # round 5 の N23z8(ファイルの項目を末尾の / つきで書く)用 — リリースより前からある
    s.write(spec_p, "# spec\nline 2\n")
    s.write(adr1, "# ADR-1\n")
    s.write(adr2, "# ADR-2\n")
    s.write(file40, "# 40\n")
    p = commit_paths("phase 3: spec and ADRs", add=(spec_p, adr1, adr2, file40))
    # N23a: 設計リリースより前(欄が無い)は検査しない
    res.append(result("N23a", "E13 なし(設計リリースより前・欄を足す前は検査しない)", p.returncode == 0,
                      "通過" if p.returncode == 0 else f"想定外(exit {p.returncode}): {out(p).strip()[:140]}"))
    steps = []
    for br, path in (("early", adr3), ("early2", adr4)):
        steps.append(git(s.root, "checkout", "-q", "-b", br, env=s.env))
        s.write(path, f"# {path}\n")
        steps.append(commit_paths(f"{br}: ruled change on a branch forked before the release", add=(path,)))
        steps.append(git(s.root, "checkout", "-q", main, env=s.env))
    steps.append(git(s.root, "commit", "-q", "--allow-empty", "-m", "release (G3 passed)", env=s.env))
    release = head()
    steps.append(git(s.root, "tag", "oq-release", env=s.env))
    # 起票: ECO-950(open・引用あり)/ ECO-951(後で applied)/ ECO-952(Sources read なし)/ ECO-953(指示書なし)
    reg = {c: SPEC["initial"] for c in ("ECO-950", "ECO-951", "ECO-952", "ECO-953")}  # 状態名は installed profile から(ECO-024)
    s.write(SPEC["register"], _reg_many(reg))
    s.write("bomdd/60-change-order-eco-950.md", f"# ECO-950\n## Sources read\n- {spec_p}:1-2\n- {adr1}:1\n")
    s.write("bomdd/60-change-order-eco-951.md", f"# ECO-951\n## Sources read\n- {spec_p}:1\n")
    s.write("bomdd/60-change-order-eco-952.md", f"# ECO-952\n## 1. change\n- {spec_p}:1\n")
    steps.append(s.commit("eco: file ECO-950..953"))
    reg["ECO-951"] = SPEC["final"]
    s.write(SPEC["register"], _reg_many(reg))
    steps.append(s.commit("eco: accept ECO-951", f"{acc}: ECO-951"))
    # N23p(round 5・裁定 B): since は欄を足すときの HEAD — それより前の裁定層の変更は、どちらの層も判定しない
    # (リリースの後でも。since を後ろの release へ戻すと判定される — N23p2)
    s.write(spec_p, "# spec\nline 2 before the field\n")
    p_pre = commit_paths("spec: after the release, before the field", add=(spec_p,))
    pre_field = head()
    res.append(result("N23p", "E13 なし(since〔欄を足すときの HEAD〕より前の commit は判定しない)", p_pre.returncode == 0,
                      "通過" if p_pre.returncode == 0 else f"想定外(exit {p_pre.returncode}): {out(p_pre).strip()[:140]}"))
    steps.append(set_ruled_layer(pre_field, "equipment: ruled_layer since the HEAD it is added on (the release is tagged "
                                            "oq-release) under ECO-950"))
    bad = [x for x in steps if x.returncode != 0]
    if bad:
        res.append(result("N23", "E13(準備)", False, f"準備の git 操作が失敗: {out(bad[0]).strip()[:160]}"))
        return res

    # --- 第 1 層の遮断 ---
    s.write(spec_p, "# spec\nline 2 changed\n")
    refused("N23b", "E13(trailer なしの裁定層の変更→遮断)", commit_paths("spec: no trailer", add=(spec_p,)), "trailer が無い")
    s.write(spec_p, "# spec\nline 2 changed\n")
    refused("N23c", "E13(台帳に無い ECO を名指す→遮断)", commit_paths("spec", f"{ruling}: ECO-999", add=(spec_p,)), "ECO-999")
    s.write(spec_p, "# spec\nline 2 changed\n")
    refused("N23c2", "E13(名指す ID の 1 つが台帳に無い→他が満たしても遮断)",
            commit_paths("spec", f"{ruling}: ECO-999\n{ruling}: ECO-950", add=(spec_p,)), "ECO-999")
    s.write(spec_p, "# spec\nline 2 changed\n")
    refused("N23d", "E13(閉じた ECO を名指す→遮断)", commit_paths("spec", f"{ruling}: ECO-951", add=(spec_p,)), "open でない")
    s.write(spec_p, "# spec\nline 2 changed\n")
    refused("N23e", "E13(指示書の無い ECO→遮断)", commit_paths("spec", f"{ruling}: ECO-953", add=(spec_p,)), "指示書")
    s.write(spec_p, "# spec\nline 2 changed\n")
    refused("N23f", "E13(Sources read 節の無い指示書→遮断)", commit_paths("spec", f"{ruling}: ECO-952", add=(spec_p,)), "Sources read 節が無い")
    # N23e2(round 6・R8-5-02): 名指す ECO の指示書を同じ commit で消す → 遮断(作られる commit の指示書だけを読む — 再演と同じ)
    s.write(spec_p, "# spec\nline 2 changed\n")
    git(s.root, "rm", "-q", "--", "bomdd/60-change-order-eco-950.md", env=s.env)
    refused("N23e2", "E13(名指す ECO の指示書を同じ commit で消す→遮断 — `HEAD:` の指示書へ縮退しない)",
            commit_paths("spec with the order removed", f"{ruling}: ECO-950", add=(spec_p,)), "指示書")
    s.write(adr2, "# ADR-2 changed\n")
    refused("N23g", "E13(引用していない裁定層ファイル〔引用数 0〕→遮断)", commit_paths("adr", f"{ruling}: ECO-950", add=(adr2,)), "引用数 0")
    git(s.root, "rm", "-q", "--", adr1, env=s.env)
    refused("N23h", "E13(裁定層ファイルの削除・trailer なし→遮断)", commit_paths("adr: delete"), adr1)
    git(s.root, "mv", spec_p, "bomdd/moved-spec.md", env=s.env)
    refused("N23i", "E13(裁定層の外への rename・trailer なし→遮断)", commit_paths("spec: rename out"), spec_p)
    # 裁定 4:A: trailer の読みがコメント行の扱いで変わる commit は止める(エディタのコメント塊・-m の `#` 段落)
    s.write(adr1, "# ADR-1 changed\n")
    refused("N23k", "E13(エディタのコメント塊つき→遮断・-m / -F へ案内)",
            commit_paths("adr: ruled change", f"{ruling}: ECO-950", add=(adr1,), extra=("-e",),
                         env=dict(s.env, GIT_EDITOR="true")), "-m")
    s.write(adr1, "# ADR-1 changed\n")
    refused("N23q", "E13(-m の trailer の後ろに `# 注記` の段落→遮断・git はその段落を保存する)",
            commit_paths("adr: ruled change", f"{ruling}: ECO-950", "# note", add=(adr1,)), "コメント行")
    # 陽性: 名指す ECO が open・指示書の Sources read が触れたファイルを引く
    s.write(spec_p, "# spec\nline 2 changed\n")
    passed("N23j", "E13 なし(open な ECO+Sources read の引用→通過)",
           commit_paths("spec: ruled change", f"{ruling}: ECO-950", add=(spec_p,)))
    s.write("bomdd/notes.md", "x\n")
    passed("N23l", "E13 なし(裁定層に触れない commit)", commit_paths("notes: no ruled path", add=("bomdd/notes.md",)))

    # --- merge(裁定 1:A)---
    # N23r: リリースより前に分かれた枝の merge(第 1 親= main との差分が ADR-3 を持ち込む)は trailer が要る
    refused("N23r", "E13(リリースより前に分かれた枝の merge・trailer なし→遮断)",
            git(s.root, "merge", "-q", "--no-ff", "early", "-m", "merge early", env=s.env), adr3)
    # N23s: 欄を足す前に分かれた枝へ main を merge(HEAD の profile に欄が無い)→ 他の親の欄で判定して遮断
    git(s.root, "checkout", "-q", "early2", env=s.env)
    p = git(s.root, "merge", "-q", "--no-ff", main, "-m", "merge main into early2", env=s.env)
    refused("N23s", "E13(欄の無い枝へ main を merge・枝の変更を境界の後の親との差分で判定→遮断)", p, adr4)
    git(s.root, "checkout", "-q", main, env=s.env)
    # N23t: リリースの後に分かれた枝 — 枝の commit は自分で判定され、merge にも open な ECO の trailer が要る(ECO は merge の後に applied)
    steps = [git(s.root, "checkout", "-q", "-b", "feat", env=s.env)]
    s.write(adr1, "# ADR-1 on feat\n")
    pf = commit_paths("adr: on feat", f"{ruling}: ECO-950", add=(adr1,))
    steps.append(git(s.root, "checkout", "-q", main, env=s.env))
    p_no = git(s.root, "merge", "-q", "--no-ff", "feat", "-m", "merge feat", env=s.env)
    ok_no, d_no = _blocked_with(p_no, "E13")
    undo()
    p_yes = git(s.root, "merge", "-q", "--no-ff", "feat", "-m", "merge feat", "-m", f"{ruling}: ECO-950", env=s.env)
    ok = (all(x.returncode == 0 for x in steps) and pf.returncode == 0 and ok_no
          and p_yes.returncode == 0 and "[E13]" not in out(p_yes))
    res.append(result("N23t", "E13(リリース後の枝の merge は trailer なしで遮断・open な ECO の trailer で通過)", ok,
                      "遮断→通過" if ok else f"想定外(枝 {pf.returncode}・trailer なし {d_no}・あり {p_yes.returncode}): "
                                              f"{out(p_yes).strip()[:120]}"))
    if not ok:
        undo()

    # --- 第 2 層(T4): 第 1 層を回避した変更を履歴の再演が見つける。報告される commit の集合を正確に照合する ---
    expect: dict[str, str] = {}
    s.write(spec_p, "# spec\nsneaked\n")
    p1 = commit_paths("spec: sneaked", add=(spec_p,), extra=("--no-verify",))
    expect[head()] = "--no-verify の直接の変更"
    s.write(adr_jp, "# 日本\n")
    p2 = commit_paths("adr: non-ASCII path", add=(adr_jp,), extra=("--no-verify",))
    expect[head()] = "日本語のパス(-z で読む — R8-1-02)"
    p3 = git(s.root, "merge", "-q", "--no-ff", "--no-verify", "early", "-m", "merge early", env=s.env)
    expect[head()] = "リリースより前の枝の merge"
    git(s.root, "checkout", "-q", "early2", env=s.env)
    p4 = git(s.root, "merge", "-q", "--no-ff", "--no-verify", main, "-m", "merge main into early2", env=s.env)
    rev = head()
    git(s.root, "checkout", "-q", main, env=s.env)
    p5 = git(s.root, "merge", "-q", "--ff-only", "early2", env=s.env)
    expect[rev] = "欄の無い枝へ main を merge して fast-forward"
    v = s.validate()
    e13 = [l for l in out(v).splitlines() if "[E13]" in l]
    got = {m.group(1) for m in (re.search(r"history:([0-9a-f]{9})", l) for l in e13) if m}
    want = {sha[:9] for sha in expect}
    made = all(x.returncode == 0 for x in (p1, p2, p3, p4, p5))
    ok = made and len(e13) == len(want) and got == want and pre_field[:9] not in got
    res.append(result("N23m", "E13(--no-verify・日本語のパス・リリース前の枝の merge・欄の無い枝からの fast-forward を"
                              "履歴の再演がちょうどその commit で検出・欄を足す前と正しく通った commit は報告しない)", ok,
                      f"history の E13 {len(e13)} 件= 期待の {len(want)} commit と一致" if ok
                      else f"想定外(作成 {made}・E13 {len(e13)} 件・余分 {sorted(got - want)}・不足 "
                           f"{sorted(want - got)}): {out(v).strip()[:160]}"))

    # --- round 3(R8 round 2 の所見と、その裁定)---
    # N23x(round 3 の 1:A → 裁定 B・R8-2-01): 欄を足す前に分かれた枝へ main を -s ours で merge(結果は枝の欄なし profile)→ 遮断
    git(s.root, "checkout", "-q", "-b", "old3", pre_field, env=s.env)
    p = git(s.root, "merge", "-q", "--no-ff", "-s", "ours", main, "-m", "sync main into old3 (ours)", env=s.env)
    refused("N23x", "E13(merge の結果が境界の後の親の欄を落とす→遮断・fast-forward の後に両層が止まるのを防ぐ)", p, "ruled_layer を落とす")
    git(s.root, "checkout", "-q", main, env=s.env)
    # N23u(R8-2-04): octopus merge — E13 は全部の親の台帳を合算する(3 番目の親で applied の ECO を名指す merge は遮断)
    adr5 = "bomdd/adr/ADR-5.md"
    reg["ECO-954"] = SPEC["initial"]
    s.write(SPEC["register"], _reg_many(reg))
    s.write("bomdd/60-change-order-eco-954.md", f"# ECO-954\n## Sources read\n- {adr5}:1\n")
    st = [s.commit("eco: file ECO-954")]
    st.append(git(s.root, "checkout", "-q", "-b", "b1", env=s.env))
    s.write(adr5, "# ADR-5\n")
    st.append(commit_paths("adr5 on b1", f"{ruling}: ECO-954", add=(adr5,)))
    st.append(git(s.root, "checkout", "-q", "-b", "b3", main, env=s.env))
    s.write("bomdd/notes3.md", "x\n")
    st.append(commit_paths("notes on b3", add=("bomdd/notes3.md",)))
    st.append(git(s.root, "checkout", "-q", "-b", "b2", main, env=s.env))
    s.write(SPEC["register"], _reg_many(dict(reg, **{"ECO-954": SPEC["final"]})))
    st.append(s.commit("eco: accept ECO-954 on b2", f"{acc}: ECO-954"))
    st.append(git(s.root, "checkout", "-q", main, env=s.env))
    if all(x.returncode == 0 for x in st):
        # accept trailer も付ける(R8-3-08: 無いと E05 でも止まり、E13 の比較元の違いを試せない)
        p = git(s.root, "merge", "-q", "--no-ff", "b1", "b3", "b2", "-m", "octopus", "-m",
                f"{ruling}: ECO-954\n{acc}: ECO-954", env=s.env)
        refused("N23u", "E13(octopus merge — 3 番目の親で applied の ECO は open でない→遮断・再演と同じ比較元)", p, "open でない")
    else:
        res.append(result("N23u", "E13(octopus)", False, f"準備の git 操作が失敗: {out(next(x for x in st if x.returncode)).strip()[:140]}"))
    # N23y(round 3 の 2:A・R8-2-02): 欄を消して(E08)、その間に裁定層を変え、欄を戻す → 再演がその commit を報告
    good_profile = prof_path.read_text(encoding="utf-8")
    pr = yaml.safe_load(good_profile)
    pr.pop("ruled_layer", None)
    prof_path.write_text(yaml.safe_dump(pr, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    st = [commit_paths("equipment: the field removed under ECO-950", add=(prof_rel,))]
    s.write(spec_p, "# spec\nin a removal window\n")
    st.append(commit_paths("spec: while the field is removed", add=(spec_p,)))
    window = head()
    prof_path.write_text(good_profile, encoding="utf-8", newline="\n")
    st.append(commit_paths("equipment: the field re-added under ECO-950", add=(prof_rel,)))
    # N23z(R8-2-03): 読めない profile の直後の --no-verify の裁定層の変更 → 再演が報告(欄はそれより前にあった)
    prof_path.write_text("ruled_layer: [\n", encoding="utf-8", newline="\n")
    st.append(commit_paths("equipment: a broken profile", add=(prof_rel,), extra=("--no-verify",)))
    s.write(spec_p, "# spec\nafter a broken profile\n")
    st.append(commit_paths("spec: after a broken profile", add=(spec_p,), extra=("--no-verify",)))
    broken_next = head()
    prof_path.write_text(good_profile, encoding="utf-8", newline="\n")
    st.append(commit_paths("equipment: the profile restored", add=(prof_rel,), extra=("--no-verify",)))
    made = all(x.returncode == 0 for x in st)
    v = s.validate()
    e13b = [l for l in out(v).splitlines() if "[E13]" in l]
    got2 = {m.group(1) for m in (re.search(r"history:([0-9a-f]{9})", l) for l in e13b) if m}
    new = got2 - got
    res.append(result("N23y", "E13(欄を消して戻した間の裁定層の変更を履歴の再演が検出)", made and window[:9] in new,
                      "history の E13 で検出" if made and window[:9] in new
                      else f"想定外(作成 {made}・新しい報告 {sorted(new)}): {out(v).strip()[:140]}"))
    ok = made and new == {window[:9], broken_next[:9]}
    res.append(result("N23z", "E13(読めない profile の直後の --no-verify の変更を履歴の再演が検出 — 新しい報告は N23y と"
                              "この 2 件だけ)", ok,
                      "history の E13 で検出" if ok else f"想定外(作成 {made}・新しい報告 {sorted(new)}): {out(v).strip()[:140]}"))
    # N23z2(round 5・裁定 B): 項目を {path, since: HEAD} で足す commit が、その下のファイルを同じ commit で作る → 第 1 層が
    # index の欄で判定して遮断(再演はこの commit を、since の直後の commit として判定する — N23z2r)
    pr = yaml.safe_load(good_profile)
    pr["ruled_layer"]["paths"] = list(pr["ruled_layer"]["paths"]) + [{"path": "bomdd/extra", "since": head()}]
    prof_path.write_text(yaml.safe_dump(pr, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    s.write("bomdd/extra/x.md", "x\n")
    refused("N23z2", "E13(項目を足す commit が、その下のファイルを同じ commit で作る→ index の欄で遮断 — 再演と同じ判定)",
            commit_paths("equipment: an entry added, with a file under it", add=(prof_rel, "bomdd/extra/x.md")), "bomdd/extra/x.md")

    # --- 裁定 B(round 3): merge の結果の欄が境界の後のどれかの親の欄と同じなら通す・どれとも違えば遮断 ---
    # main の系列を汚さないよう、main から分けた trunk の上で(以降の対照は main に戻って続ける)
    def with_paths(extra: str) -> None:
        q = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
        q["ruled_layer"]["paths"] = list(q["ruled_layer"]["paths"]) + [extra]
        prof_path.write_text(yaml.safe_dump(q, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")

    st = [git(s.root, "checkout", "-q", "-b", "trunk", main, env=s.env),
          git(s.root, "checkout", "-q", "-b", "featA", env=s.env),
          git(s.root, "commit", "-q", "--allow-empty", "-m", "featA work", env=s.env),
          git(s.root, "checkout", "-q", "trunk", env=s.env)]
    with_paths("bomdd/extra2")
    st.append(commit_paths("equipment: paths extended on trunk under ECO-950", add=(prof_rel,)))
    st.append(git(s.root, "checkout", "-q", "featA", env=s.env))
    # N23x2: trunk が単独の commit で欄を変えた後、作業中の枝へ trunk を取り込む(同期の merge)→ 通す
    if all(x.returncode == 0 for x in st):
        passed("N23x2", "E13 なし(単独の commit で変えた欄を、作業中の枝へ同期の merge で取り込む — 裁定 B)",
               git(s.root, "merge", "-q", "--no-ff", "trunk", "-m", "sync trunk into featA", env=s.env))
    else:
        res.append(result("N23x2", "E13 なし(同期の merge)", False,
                          f"準備の git 操作が失敗: {out(next(x for x in st if x.returncode)).strip()[:140]}"))
    # N23x3: 枝が単独の commit で欄を変え、trunk へ merge → 通す
    st = [git(s.root, "checkout", "-q", "-b", "featB", "trunk", env=s.env)]
    with_paths("bomdd/extra3")
    st.append(commit_paths("equipment: paths extended on featB under ECO-950", add=(prof_rel,)))
    st.append(git(s.root, "checkout", "-q", "trunk", env=s.env))
    if all(x.returncode == 0 for x in st):
        passed("N23x3", "E13 なし(枝の単独の commit で変えた欄を、merge で trunk へ取り込む — 裁定 B)",
               git(s.root, "merge", "-q", "--no-ff", "featB", "-m", "merge featB", env=s.env))
    else:
        res.append(result("N23x3", "E13 なし(枝の欄の変更の merge)", False,
                          f"準備の git 操作が失敗: {out(next(x for x in st if x.returncode)).strip()[:140]}"))
    # N23x4: merge の解決で、どの親にも無い欄を作る → 遮断(「変える」)
    st = [git(s.root, "checkout", "-q", "-b", "featC", "trunk", env=s.env)]
    with_paths("bomdd/extra4")
    st.append(commit_paths("equipment: paths extended on featC under ECO-950", add=(prof_rel,)))
    st.append(git(s.root, "checkout", "-q", "trunk", env=s.env))
    st.append(git(s.root, "merge", "-q", "--no-ff", "--no-commit", "featC", env=s.env))
    if all(x.returncode == 0 for x in st):
        with_paths("bomdd/extra5")
        refused("N23x4", "E13(merge の解決で、境界の後のどの親の欄とも違う欄を作る→遮断 — 裁定 B)",
                commit_paths("merge featC with an invented field", add=(prof_rel,)), "ruled_layer を変える")
    else:
        res.append(result("N23x4", "E13(merge で欄を作る)", False,
                          f"準備の git 操作が失敗: {out(next(x for x in st if x.returncode)).strip()[:140]}"))
        undo()
    git(s.root, "checkout", "-q", main, env=s.env)

    # --- round 4(R8 round 3 の所見): 判定に使う欄の決め方を 1 か所に(values_for)---
    # 腕ごとに別の validate で判定する(1 本の腕の失敗— たとえば測定不能— が他の腕の判定を隠さないように)
    def e13_set(v: subprocess.CompletedProcess) -> set[str]:
        return {m.group(1) for m in (re.search(r"history:([0-9a-f]{9})", l) for l in out(v).splitlines() if "[E13]" in l)
                if m}

    def report(made_: bool, v: subprocess.CompletedProcess, new_: set[str], gone: set[str]) -> str:
        return (f"準備 {made_}・validate exit {v.returncode}・新しい報告 {sorted(new_)}・消えた報告 {sorted(gone)}: "
                f"{out(v).strip()[:120]}")

    got_b = e13_set(s.validate())
    good_now = prof_path.read_text(encoding="utf-8")

    def write_prof(mut) -> None:
        q = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
        mut(q["ruled_layer"])
        prof_path.write_text(yaml.safe_dump(q, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")

    def arm_new(name: str, expected: str, st_: list, v_: subprocess.CompletedProcess, base_: set[str], want: set[str]) -> set[str]:
        """新しい報告がちょうど want で、前からの報告が消えないこと(腕ごとに別の validate)。新しい基準線を返す。"""
        made_ = all(x.returncode == 0 for x in st_)
        got_ = e13_set(v_)
        new_ = got_ - base_
        ok_ = made_ and v_.returncode != 2 and new_ == {w[:9] for w in want} and base_ <= got_
        res.append(result(name, expected, ok_, ("history の E13 でちょうど期待の commit を検出" if want else "新しい報告 0")
                          if ok_ else report(made_, v_, new_, base_ - got_)))
        return got_
    # N23z4(R8-3-02): paths を狭め(E08)、外した項目のファイルを trailer なしで変え、paths を戻す → 再演が報告
    pr = yaml.safe_load(good_now)
    pr["ruled_layer"]["paths"] = ["bomdd/adr"]
    prof_path.write_text(yaml.safe_dump(pr, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    st = [commit_paths("equipment: paths narrowed under ECO-950", add=(prof_rel,))]
    s.write(spec_p, "# spec\nin a narrowing window\n")
    st.append(commit_paths("spec: while paths is narrowed", add=(spec_p,)))
    narrow_c = head()
    prof_path.write_text(good_now, encoding="utf-8", newline="\n")
    st.append(commit_paths("equipment: paths restored under ECO-950", add=(prof_rel,)))
    made = all(x.returncode == 0 for x in st)
    v = s.validate()
    got1 = e13_set(v)
    new1 = got1 - got_b
    ok = made and v.returncode != 2 and new1 == {narrow_c[:9]} and got_b <= got1
    res.append(result("N23z4", "E13(paths を狭めて戻した間の、外した項目のファイルの変更を履歴の再演が検出)", ok,
                      "history の E13 でその commit だけを検出" if ok else report(made, v, new1, got_b - got1)))
    got2 = got1

    # N23z3 / z3b(R8-3-01 → round 5): 枝で paths に形の正しくない項目を足す commit は、第 1 層が index の欄を検査して止める
    # (exit 2)。--no-verify で作って main へ -s ours で merge しても、再演は HEAD の欄だけを使うので前後の --no-verify の
    # 変更をどちらも報告し、前からの報告も消えない
    def odd_entry_arm(name: str, entry: str, expected: str, extra_ok) -> None:
        nonlocal got2
        s.write(spec_p, f"# spec\nno-verify before {entry}\n")
        st_ = [commit_paths(f"spec: no-verify before {entry}", add=(spec_p,), extra=("--no-verify",))]
        nv1 = head()
        br = f"odd-{name}"
        st_.append(git(s.root, "checkout", "-q", "-b", br, env=s.env))
        write_prof(lambda r: r["paths"].append(entry))
        hooked = commit_paths(f"equipment: the entry {entry} on a side branch under ECO-950", add=(prof_rel,))
        st_.append(commit_paths(f"equipment: the entry {entry} on a side branch under ECO-950 (hooks skipped)",
                                add=(prof_rel,), extra=("--no-verify",)))
        st_.append(git(s.root, "checkout", "-q", main, env=s.env))
        st_.append(git(s.root, "merge", "-q", "--no-ff", "-s", "ours", br, "-m", f"merge {br} (ours)", env=s.env))
        s.write(adr2, f"# ADR-2\nno-verify after {entry}\n")
        st_.append(commit_paths(f"adr: no-verify after {entry}", add=(adr2,), extra=("--no-verify",)))
        nv2 = head()
        made_ = all(x.returncode == 0 for x in st_)
        v_ = s.validate()
        got_ = e13_set(v_)
        new_ = got_ - got2
        ok_ = (made_ and hooked.returncode != 0 and "index の profile が不正" in out(hooked) and v_.returncode != 2
               and new_ == {nv1[:9], nv2[:9]} and got2 <= got_ and extra_ok(v_))
        res.append(result(name, expected, ok_, "第 1 層が測定不能で止め・history の E13 で前後の 2 件を検出" if ok_
                          else f"hook の commit exit {hooked.returncode}・" + report(made_, v_, new_, got2 - got_)))
        got2 = got_

    odd_entry_arm("N23z3", ":(exclude)bomdd", "E13(paths に `:(exclude)` の項目を足す commit は第 1 層が止める〔exit 2〕・"
                  "枝から -s ours で merge しても再演は前後の --no-verify の変更を両方報告)", lambda _v: True)
    odd_entry_arm("N23z3b", "../outside", "E13(paths に `..` の項目を足す commit は第 1 層が止める〔exit 2〕・再演は測定不能に"
                  "ならず前後の変更を両方報告)", lambda _v: "outside" not in out(_v))

    # --- round 5(R8 round 4 の所見と裁定 B): 判定は HEAD の欄の項目ごとの since だけで決まる ---
    # N23z6(R8-4-01): 項目を外し(E08)、その下を変え、綴りを変えて戻す(`bomdd/adr` → `bomdd/adr/`・since は欄の since)
    # → 再演が報告(綴りは判定に関係しない)
    write_prof(lambda r: r.__setitem__("paths", [x for x in r["paths"] if x != "bomdd/adr"]))
    st = [commit_paths("equipment: bomdd/adr taken out of paths under ECO-950", add=(prof_rel,))]
    s.write(adr2, "# ADR-2\nwhile bomdd/adr is out\n")
    st.append(commit_paths("adr: while bomdd/adr is out of paths", add=(adr2,)))
    win6 = head()
    write_prof(lambda r: r["paths"].append("bomdd/adr/"))
    st.append(commit_paths("equipment: restored as bomdd/adr/ under ECO-950", add=(prof_rel,)))
    got2 = arm_new("N23z6", "E13(項目を外して綴りを変えて戻した間の変更を履歴の再演が検出 — 照合は綴りでなく覆うパス)",
                   st, s.validate(), got2, {win6})
    # N23z8(R8-4-04): ファイルの項目を末尾の / つきで書き(`bomdd/40-file.md/`)、--no-verify で変える → 再演が報告
    write_prof(lambda r: r["paths"].append(file40 + "/"))
    st = [commit_paths("equipment: a file entry written with a trailing slash under ECO-950", add=(prof_rel,))]
    s.write(file40, "# 40\nchanged with hooks skipped\n")
    st.append(commit_paths("file40: changed with hooks skipped", add=(file40,), extra=("--no-verify",)))
    nv8 = head()
    got2 = arm_new("N23z8", "E13(ファイルの項目を末尾の / つきで書いても --no-verify の変更を履歴の再演が検出 — git の pathspec "
                            "を使わない)", st, s.validate(), got2, {nv8})
    # N23fr(round 6・R8-5-01): 名前に \x01<SHA> を持つファイル(plumbing で作る — Windows の index には入らない)を足し、裁定層を
    # trailer なしで変える commit を、ruling つきの空の commit の上に作る → 再演がその commit を報告(パスで見出しを偽れない)。
    # 作業ツリーと index には触れない(HEAD を枝へ付け替えて validate し、main へ戻す)
    def git_in(text: str, *args: str, env=None) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(s.root), *args], input=text, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=env or s.env)

    st = [git(s.root, "branch", "crafted", env=s.env)]
    st.append(git(s.root, "symbolic-ref", "HEAD", "refs/heads/crafted", env=s.env))
    st.append(git(s.root, "commit", "-q", "--allow-empty", "-m", "empty, with a ruling", "-m", f"{ruling}: ECO-950", env=s.env))
    c2 = head()
    gp = git(s.root, "rev-parse", "--git-path", "oq-crafted-index", env=s.env).stdout.strip()
    idx = Path(gp) if Path(gp).is_absolute() else s.root / gp
    envi = dict(s.env, GIT_INDEX_FILE=str(idx))
    blob_spec = git_in("# spec\ncrafted\n", "hash-object", "-w", "--stdin")
    blob_x = git_in("x\n", "hash-object", "-w", "--stdin")
    st += [blob_spec, blob_x, git(s.root, "read-tree", "HEAD", env=envi),
           git(s.root, "update-index", "--cacheinfo", f"100644,{blob_spec.stdout.strip()},{spec_p}", env=envi)]
    wt = git(s.root, "write-tree", env=envi)
    st.append(wt)
    lst = git(s.root, "ls-tree", "-z", wt.stdout.strip(), env=s.env)
    st.append(lst)
    mk = git_in(lst.stdout + f"100644 blob {blob_x.stdout.strip()}\ta\x01{c2}\0", "mktree", "-z")
    st.append(mk)
    ct = git(s.root, "commit-tree", mk.stdout.strip(), "-p", c2, "-m", "spec: a crafted path, no trailer", env=s.env)
    st.append(ct)
    crafted = ct.stdout.strip()
    st.append(git(s.root, "update-ref", "refs/heads/crafted", crafted, env=s.env))
    v = s.validate()
    st.append(git(s.root, "symbolic-ref", "HEAD", f"refs/heads/{main}", env=s.env))
    if idx.exists():
        idx.unlink()
    undo()
    arm_new("N23fr", "E13(名前に \\x01<SHA> を持つパスで差分の見出しを偽る commit を、履歴の再演が報告 — raw を位置で読む)",
            st, v, got2, {crafted})
    # N23z3c(round 6・R8-5-04): index の欄に since の重複キー → それを作る commit を止める(exit 2)— 通すと次の commit から
    # すべて止まり、--no-verify でしか戻せない
    txt = prof_path.read_text(encoding="utf-8")
    prof_path.write_text(txt.replace("ruled_layer:\n", f"ruled_layer:\n  since: {head()}\n", 1), encoding="utf-8", newline="\n")
    p = commit_paths("equipment: a duplicate since key under ECO-950", add=(prof_rel,))
    ok = p.returncode != 0 and "index の profile がパース不能" in out(p)
    res.append(result("N23z3c", "exit 2(index の profile に重複キー〔ruled_layer.since〕→ それを作る commit を止める)", ok,
                      "測定不能で停止" if ok else f"想定外(exit {p.returncode}): {out(p).strip()[:140]}"))
    if p.returncode == 0:
        git(s.root, "reset", "-q", "--hard", "HEAD~1", env=s.env)
    undo()
    # N23z9(R8-4-03): profile を消し(E08)、profile を戻す commit で裁定層も変える(trailer なし)→ 第 1 層が index の欄で遮断
    st = [git(s.root, "rm", "-q", "--", prof_rel, env=s.env)]
    st.append(commit_paths("equipment: the profile removed under ECO-950"))
    prof_path.parent.mkdir(parents=True, exist_ok=True)
    good_z9 = git(s.root, "show", f"HEAD~1:{prof_rel}", env=s.env).stdout
    prof_path.write_text(good_z9, encoding="utf-8", newline="\n")
    s.write(spec_p, "# spec\nwith the profile restored\n")
    if all(x.returncode == 0 for x in st):
        refused("N23z9", "E13(HEAD に profile が無いとき、profile を戻す commit の裁定層の変更を index の欄で遮断 — 速い道も同じ)",
                commit_paths("equipment+spec: the profile restored with a ruled change", add=(prof_rel, spec_p)), spec_p)
    else:
        res.append(result("N23z9", "E13(profile を戻す commit)", False,
                          f"準備の git 操作が失敗: {out(next(x for x in st if x.returncode)).strip()[:140]}"))
        undo()
    # N23z9b(round 6・R8-5-05): profile を index にだけ戻し(作業ツリーには無い)、裁定層を trailer なしで変える → 遮断
    # (HEAD に profile が無ければ hook は index 版の profile を読む — 作業ツリー版へ縮退しない)
    if prof_path.exists():
        prof_path.unlink()
    rz = git(s.root, "restore", "--staged", "--source=HEAD~1", "--", prof_rel, env=s.env)
    s.write(spec_p, "# spec\nwith the profile restored in the index only\n")
    if rz.returncode == 0 and not prof_path.exists():
        refused("N23z9b", "E13(profile を index にだけ戻す commit の裁定層の変更を、index 版の profile の欄で遮断)",
                commit_paths("spec: the profile restored in the index only", add=(spec_p,)), spec_p)
    else:
        res.append(result("N23z9b", "E13(profile を index にだけ戻す)", False, f"準備の git 操作が失敗: {out(rz).strip()[:140]}"))
        undo()
    # N23x6(round 6・R8-5-03): profile を消した枝へ main を -s ours で merge(結果に profile が無い)→ 遮断
    # (profile の無い HEAD でも、merge の欄の照合は素通しの前に git だけで行う)
    st = [git(s.root, "checkout", "-q", "-b", "noprof", env=s.env),
          git(s.root, "checkout", "-q", main, env=s.env)]
    prof_path.parent.mkdir(parents=True, exist_ok=True)
    prof_path.write_text(good_z9, encoding="utf-8", newline="\n")
    st.append(commit_paths("equipment: the profile restored on main under ECO-950", add=(prof_rel,)))
    st.append(git(s.root, "checkout", "-q", "noprof", env=s.env))
    if all(x.returncode == 0 for x in st):
        refused("N23x6", "E13(profile の無い枝へ main を -s ours で merge し欄を落とす→遮断 — profile の無い HEAD でも照合)",
                git(s.root, "merge", "-q", "--no-ff", "-s", "ours", main, "-m", "sync main into noprof (ours)", env=s.env),
                "ruled_layer を落とす")
    else:
        res.append(result("N23x6", "E13(profile の無い枝の merge)", False,
                          f"準備の git 操作が失敗: {out(next(x for x in st if x.returncode)).strip()[:140]}"))
        undo()
    git(s.root, "checkout", "-q", main, env=s.env)
    pz = git(s.root, "cat-file", "-e", f"HEAD:{prof_rel}", env=s.env)   # main の profile は N23x6 の準備で戻した
    if pz.returncode != 0:
        res.append(result("N23z9", "E13(profile を戻す)", False, f"profile を戻せない: {out(st[2]).strip()[:140]}"))
        return res
    # N23x5(R8-2-01 を事実だけで): since で分かれ commit を持つ枝(欄なし)へ main を -s ours で merge → 遮断(欄の無い親は数えない)
    st = [git(s.root, "checkout", "-q", "-b", "old5", pre_field, env=s.env),
          git(s.root, "commit", "-q", "--allow-empty", "-m", "old5 work", env=s.env)]
    if all(x.returncode == 0 for x in st):
        refused("N23x5", "E13(since で分かれ commit を持つ枝へ main を -s ours で merge し欄を落とす→遮断 — 欄の無い親は数えない)",
                git(s.root, "merge", "-q", "--no-ff", "-s", "ours", main, "-m", "sync main into old5 (ours)", env=s.env),
                "ruled_layer を落とす")
    else:
        res.append(result("N23x5", "E13(-s ours で欄を落とす)", False,
                          f"準備の git 操作が失敗: {out(next(x for x in st if x.returncode)).strip()[:140]}"))
    git(s.root, "checkout", "-q", main, env=s.env)
    # N23p2(裁定 B: 事実が決める): since をリリースへ戻す(E08)→ 欄を足す前の commit(N23p)を再演が新たに報告。since を戻して元に
    write_prof(lambda r: r.__setitem__("since", release))
    st = [commit_paths("equipment: since moved back to the release under ECO-950", add=(prof_rel,))]
    v = s.validate()
    arm_new("N23p2", "E13(since をリリースへ戻すと、欄を足す前の commit も再演が判定 — 始点は profile に書いた since)",
            st, v, got2, {pre_field})
    write_prof(lambda r: r.__setitem__("since", pre_field))
    st = [commit_paths("equipment: since set back to the HEAD the field was added on under ECO-950", add=(prof_rel,))]
    got2 = e13_set(s.validate())

    # --- round 5: 項目ごとの since({path, since})---
    # N23z5(R8-3-06 → 裁定 B): 欄を消した間に、後で足す項目の下のファイルを作り、その項目を {path, since: HEAD} で足して欄を
    # 戻す → 再演は報告しない。N23z5b: 同じ項目をパスだけ(欄の since)に書き換える → 再演がその commit を報告
    q = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
    kept = q.pop("ruled_layer")
    prof_path.write_text(yaml.safe_dump(q, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    st = [commit_paths("equipment: the field removed again under ECO-950", add=(prof_rel,))]
    s.write("bomdd/extra9/x.md", "x\n")
    st.append(commit_paths("notes: a file under a later entry, while the field is removed", add=("bomdd/extra9/x.md",)))
    win_c = head()
    q["ruled_layer"] = dict(kept, paths=list(kept["paths"]) + [{"path": "bomdd/extra9", "since": win_c}])
    prof_path.write_text(yaml.safe_dump(q, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    st.append(commit_paths("equipment: the field re-added with bomdd/extra9 since the HEAD under ECO-950", add=(prof_rel,)))
    got2 = arm_new("N23z5", "E13 なし(後で {path, since: HEAD} で足した項目は、その since より前の commit を判定しない)",
                   st, s.validate(), got2, set())
    write_prof(lambda r: r.__setitem__("paths", [x if not isinstance(x, dict) else x["path"] for x in r["paths"]]))
    st = [commit_paths("equipment: bomdd/extra9 rewritten as a plain path under ECO-950", add=(prof_rel,))]
    arm_new("N23z5b", "E13(同じ項目をパスだけ〔欄の since〕に書き換えると、欄を消した間の commit を再演が報告)",
            st, s.validate(), got2, {win_c})
    write_prof(lambda r: r.__setitem__("paths", [x if x != "bomdd/extra9" else {"path": x, "since": win_c}
                                                for x in r["paths"]]))
    commit_paths("equipment: bomdd/extra9 since the HEAD again under ECO-950", add=(prof_rel,))
    got2 = e13_set(s.validate())
    # N23z2r(N23z2 の再演の側): 同じ commit を --no-verify で作る → 再演が報告(since の直後の commit も判定する)
    write_prof(lambda r: r["paths"].append({"path": "bomdd/extra", "since": head()}))
    s.write("bomdd/extra/x.md", "x\n")
    st = [commit_paths("equipment: an entry added, with a file under it (hooks skipped)", add=(prof_rel, "bomdd/extra/x.md"),
                       extra=("--no-verify",))]
    z2r = head()
    got2 = arm_new("N23z2r", "E13(項目を足す commit がその下のファイルを作る — --no-verify でも再演が報告・since の直後の commit "
                             "も判定)", st, s.validate(), got2, {z2r})
    # N23z7(R8-4-02): 項目を持つ枝を main へ -s ours で merge → main でその項目の下を変える(hook を通る)→ main が
    # {path, since: HEAD} で項目を足す → 再演は報告しない(ずっと赤にならない)
    st = [git(s.root, "checkout", "-q", "-b", "side7", env=s.env)]
    write_prof(lambda r: r["paths"].append("bomdd/extra7"))
    st.append(commit_paths("equipment: bomdd/extra7 on a side branch under ECO-950", add=(prof_rel,)))
    st.append(git(s.root, "checkout", "-q", main, env=s.env))
    st.append(git(s.root, "merge", "-q", "--no-ff", "-s", "ours", "side7", "-m", "merge side7 (ours)", env=s.env))
    s.write("bomdd/extra7/x.md", "x\n")
    st.append(commit_paths("notes: bomdd/extra7 on main before main has the entry", add=("bomdd/extra7/x.md",)))
    gap7 = head()
    write_prof(lambda r: r["paths"].append({"path": "bomdd/extra7", "since": gap7}))
    st.append(commit_paths("equipment: bomdd/extra7 since the HEAD on main under ECO-950", add=(prof_rel,)))
    got2 = arm_new("N23z7", "E13 なし(枝だけが持った項目を main が後で {path, since: HEAD} で足しても、その前の hook を通った "
                            "commit は報告しない)", st, s.validate(), got2, set())
    # N23n2: 項目の since が解決できない → その項目の下に触れる commit は遮断(測定不能は合格ではない)
    write_prof(lambda r: r["paths"].append({"path": "bomdd/extra8", "since": "0" * 40}))
    s.write("bomdd/extra8/y.md", "y\n")
    refused("N23n2", "E13(項目の since が解決できない→その項目の下に触れる commit を遮断)",
            commit_paths("extra8: under an entry whose since does not resolve", f"{ruling}: ECO-950",
                         add=(prof_rel, "bomdd/extra8/y.md")), "解決できない")

    # N23v2(round 6・R8-5-06): 枝の HEAD を since にした項目を、main へ squash で取り込む → squash の commit を遮断
    # (since が main の系列に無い — 通すと main の validate が測定不能になり、全部の検査が止まる)
    st = [git(s.root, "checkout", "-q", "-b", "sq", env=s.env),
          git(s.root, "commit", "-q", "--allow-empty", "-m", "sq work", env=s.env)]
    write_prof(lambda r: r["paths"].append({"path": "bomdd/extra10", "since": head()}))
    st.append(commit_paths("equipment: bomdd/extra10 since the branch's HEAD under ECO-950", add=(prof_rel,)))
    st.append(git(s.root, "checkout", "-q", main, env=s.env))
    st.append(git(s.root, "merge", "-q", "--squash", "sq", env=s.env))
    if all(x.returncode == 0 for x in st):
        refused("N23v2", "E13(枝の HEAD を since にした項目の squash の commit→遮断 — since が main の系列に無い)",
                commit_paths("squash sq into main"), "系列に無い")
    else:
        res.append(result("N23v2", "E13(squash)", False,
                          f"準備の git 操作が失敗: {out(next(x for x in st if x.returncode)).strip()[:140]}"))
        undo()
    git(s.root, "checkout", "-q", main, env=s.env)

    # N23n: since が解決できない → その since を書く commit を遮断(round 6・R8-5-06)。--no-verify で作った後の裁定層の変更も遮断
    p_h = set_ruled_layer("0" * 40, "equipment: since set to a commit that does not exist under ECO-950")
    ok_h = p_h.returncode != 0 and "[E13]" in out(p_h) and "解決できない" in out(p_h)
    # 止まった profile の変更(作業ツリーと index に残る)を --no-verify で作る(通ってしまったならそれを使う)
    p0 = p_h if p_h.returncode == 0 else commit_paths("equipment: since set to a commit that does not exist (hooks skipped)",
                                                      add=(prof_rel,), extra=("--no-verify",))
    s.write(spec_p, "# spec\nafter a broken since\n")
    p = commit_paths("spec", f"{ruling}: ECO-950", add=(spec_p,))
    ok, d = _blocked_with(p, "E13")
    res.append(result("N23n", "E13(since が解決できない→それを書く commit を遮断・--no-verify の後の裁定層の変更も遮断)",
                      ok and ok_h and p0.returncode == 0,
                      f"書く commit {'遮断' if ok_h else '通過/理由不一致: ' + out(p_h).strip()[:80]}・{d}"
                      if p0.returncode == 0 else f"profile の commit が失敗: {out(p0).strip()[:120]}"))
    undo()
    # N23v: since が HEAD の系列に無い(main から分かれた枝だけにある commit)→ それを書く commit を遮断(round 6)・
    # --no-verify の後の裁定層の変更も遮断(R8-1-03 の「系列から外れる」側)(early は N23m で merge 済み= main の祖先なので使わない)
    git(s.root, "checkout", "-q", "-b", "offline", env=s.env)
    # --no-verify: HEAD の since は N23n で解決できない値のまま — その欄を残す commit は、どれも第 1 層が止める(round 6)
    git(s.root, "commit", "-q", "--allow-empty", "--no-verify", "-m", "a commit only on a side branch", env=s.env)
    off = head()
    git(s.root, "checkout", "-q", main, env=s.env)
    p_h = set_ruled_layer(off, "equipment: since set off the main line under ECO-950")
    ok_h = p_h.returncode != 0 and "[E13]" in out(p_h) and "系列に無い" in out(p_h)
    p0 = p_h if p_h.returncode == 0 else commit_paths("equipment: since set off the main line (hooks skipped)",
                                                      add=(prof_rel,), extra=("--no-verify",))
    s.write(spec_p, "# spec\nafter since moved off the line\n")
    p = commit_paths("spec", f"{ruling}: ECO-950", add=(spec_p,))
    ok, d = _blocked_with(p, "E13")
    ok = ok and "系列に無い" in out(p)
    res.append(result("N23v", "E13(since が HEAD の系列に無い→それを書く commit を遮断・--no-verify の後の裁定層の変更も遮断)",
                      ok and ok_h and p0.returncode == 0,
                      f"書く commit {'遮断' if ok_h else '通過/理由不一致: ' + out(p_h).strip()[:80]}・{d}"
                      if p0.returncode == 0 else f"profile の commit が失敗: {out(p0).strip()[:120]}"))
    undo()
    # N23w(裁定 2:A): since に tag 名を書いた profile は不正(validator が profile を読めずに止まる)
    pr = yaml.safe_load(prof_path.read_text(encoding="utf-8"))
    pr["ruled_layer"]["since"] = "oq-release"
    prof_path.write_text(yaml.safe_dump(pr, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    p0 = commit_paths("equipment: since as a tag under ECO-950", add=(prof_rel,), extra=("--no-verify",))
    v = s.validate()
    ok = p0.returncode == 0 and v.returncode == 2 and "since" in out(v)
    res.append(result("N23w", "exit 2(since が tag 名の profile は不正 — tag は差分なしに動かせる)", ok,
                      "profile 不正で停止" if ok else f"想定外(commit {p0.returncode}・validate {v.returncode}): {out(v).strip()[:140]}"))

    # N23o: 欄の無い profile → E13 は無い(既設の製品は不変)
    s2 = Sandbox(root, base, "n23o")
    s2.write(spec_p, "# spec\n")
    s2.commit("spec")
    s2.write(spec_p, "# spec changed\n")
    passed("N23o", "E13 なし(profile に ruled_layer が無ければ E13 は無い)", s2.commit("spec: no trailer, no field"))
    return res


def _reg_many(statuses: dict) -> str:
    return "changes:\n" + "".join(f"  - id: {cid}\n    title: OQ synthetic control\n    status: {st}\n"
                                  for cid, st in statuses.items())


def _oq_structure(root: Path, base: Path, rel: str) -> list[dict]:
    """N22a〜k(ECO-118 V8 の腕を qualification に入れ子で)。sandbox 1 本で、腕ごとに別の ECO を遷移させる。"""
    tool = root / rel
    fx = {n: structure_fixture(tool, n) for n in ("good", "fail", "not-applicable")} if tool.is_file() else {}
    if not tool.is_file() or not all(fx.values()):
        return [result("N22", "E12(構造検査)", False,
                       f"道具 {rel} が無いか fixture を書けない — E12 の対照を実測できない(欠測は FAIL)")]
    res: list[dict] = []
    s = Sandbox(root, base, "n22")
    acc = SPEC["trailers"]["accept"]
    st = {c: SPEC["initial"] for c in ("ECO-901", "ECO-902", "ECO-903", "ECO-904")}
    s.write(SPEC["register"], _reg_many(st))
    s.commit("eco: file ECO-901..904")

    def put(name: str) -> None:
        for r, b in fx[name].items():
            (s.root / r).write_bytes(b)

    def accept(cid: str, msg: str) -> subprocess.CompletedProcess:
        st[cid] = SPEC["final"]
        s.write(SPEC["register"], _reg_many(st))
        return s.commit(msg, f"{acc}: {cid}")

    def undo(cid: str) -> None:
        st[cid] = SPEC["initial"]
        git(s.root, "reset", "-q", "--hard", env=s.env)

    def out(p: subprocess.CompletedProcess) -> str:
        return (p.stdout or "") + (p.stderr or "")

    put("fail")
    p = accept("ECO-901", "eco: accept ECO-901 with a BOM that fails A1-4")
    ok, d = _blocked_with(p, "E12")
    ok = ok and "[A1-4]" in out(p)
    res.append(result("N22a", "E12(FAIL の BOM で受入→遮断・所見を表示)", ok, d + ("・所見 [A1-4] を表示" if ok else "")))
    undo("ECO-901")

    put("not-applicable")
    p = accept("ECO-901", "eco: accept ECO-901 with no part standard")
    ok = p.returncode == 0 and "NOT-APPLICABLE" in out(p)
    res.append(result("N22b", "E12 なし(部品規格の無い BOM は NOT-APPLICABLE として通し、出力に名前を出す)", ok,
                      "通過・NOT-APPLICABLE を表示" if ok else f"想定外(exit {p.returncode}): {out(p).strip()[:140]}"))

    put("fail")
    p = s.commit("bom: an intermediate commit with a failing BOM (no transition)")
    put("good")
    p2 = s.commit("bom: back to a passing BOM (no transition)")
    ok = p.returncode == 0 and p2.returncode == 0
    res.append(result("N22c", "E12 なし(遷移のない途中の commit は止めない)", ok,
                      "途中の commit は通過" if ok else f"想定外(exit {p.returncode}/{p2.returncode}): {out(p).strip()[:140]}"))

    p = accept("ECO-902", "eco: accept ECO-902 with a passing BOM")
    ok = p.returncode == 0 and "PASS" in out(p)
    res.append(result("N22d", "E12 なし(PASS の BOM で受入→通過・PASS を表示)", ok,
                      "通過・PASS を表示" if ok else f"想定外(exit {p.returncode}): {out(p).strip()[:140]}"))

    # N22h(R8-1-01): 受入 commit を --amend で作り直して FAIL の BOM を入れる — HEAD は既に applied なので遷移は
    # 見えないが、accept trailer で受入 commit と分かり E12 が走る
    put("fail")
    git(s.root, "add", "-A", env=s.env)
    ok, d = _blocked_with(git(s.root, "commit", "-q", "--amend", "--no-edit", env=s.env), "E12")
    res.append(result("N22h", "E12(受入 commit の --amend で FAIL の BOM を入れる→遮断)", ok, d))
    git(s.root, "reset", "-q", "--hard", env=s.env)

    # N22i(R8-2-01): エディタを開く --amend — hook が受け取るメッセージには git のコメント塊が付く。エディタは
    # 「git が書いたまま閉じる」もの(true)で代用する
    put("fail")
    git(s.root, "add", "-A", env=s.env)
    ok, d = _blocked_with(git(s.root, "commit", "-q", "--amend", env=dict(s.env, GIT_EDITOR="true")), "E12")
    res.append(result("N22i", "E12(エディタを開く --amend で FAIL の BOM を入れる→遮断)", ok, d))
    git(s.root, "reset", "-q", "--hard", env=s.env)

    # N22j / N22k(R8-3-01): git が '#' 以外でコメントを書く設定 — core.commentChar=auto で本文に '#' 行がある場合
    # (git は ';' などを選ぶ)と core.commentString。受入 commit の本文に '#' 行を入れ直してから(PASS の BOM のまま)、
    # 設定ごとにエディタの --amend で FAIL の BOM を入れる
    p0 = git(s.root, "commit", "-q", "--amend", "-m", "eco: accept ECO-902 with a passing BOM",
             "-m", "#42 is the issue this closes", "-m", f"{acc}: ECO-902", env=s.env)
    for name, key, val in (("N22j", "core.commentChar", "auto"), ("N22k", "core.commentString", ";")):
        git(s.root, "config", key, val, env=s.env)
        put("fail")
        git(s.root, "add", "-A", env=s.env)
        ok, d = _blocked_with(git(s.root, "commit", "-q", "--amend", env=dict(s.env, GIT_EDITOR="true")), "E12")
        res.append(result(name, f"E12({key}={val} のエディタ --amend で FAIL の BOM を入れる→遮断)", ok and p0.returncode == 0,
                          d if p0.returncode == 0 else f"準備の amend が失敗: {(p0.stderr or '').strip()[:80]}"))
        git(s.root, "reset", "-q", "--hard", env=s.env)
        git(s.root, "config", "--unset", key, env=s.env)

    (s.root / rel).unlink()
    ok, d = _blocked_with(accept("ECO-903", "eco: accept ECO-903 with the tool removed"), "E12")
    res.append(result("N22e", "E12(道具の不在で受入→遮断)", ok, d))
    undo("ECO-903")

    s.write(FIXTURE_MBOM, "mbom: [\n")
    ok, d = _blocked_with(accept("ECO-903", "eco: accept ECO-903 with an M-BOM that does not parse"), "E12")
    res.append(result("N22f", "E12(解析できない M-BOM で受入→遮断 — 測れないは合格ではない)", ok, d))
    undo("ECO-903")

    prof_path = s.root / "bomdd" / "process-profile.yaml"
    prof_path.write_text("".join(l for l in prof_path.read_text(encoding="utf-8").splitlines(keepends=True)
                                 if not l.startswith("structure_check:")), encoding="utf-8", newline="\n")
    p0 = s.commit("equipment: drop structure_check under ECO-904")
    put("fail")
    p = accept("ECO-904", "eco: accept ECO-904 with a failing BOM, the field removed")
    ok = p0.returncode == 0 and p.returncode == 0 and "[E12]" not in out(p)
    res.append(result("N22g", "E12 なし(profile に欄が無ければ E12 は無い — 既設の製品は不変)", ok,
                      "欄なしでは FAIL の BOM でも通過" if ok
                      else f"想定外(exit {p0.returncode}/{p.returncode}): {(out(p0) + out(p)).strip()[:140]}"))
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
