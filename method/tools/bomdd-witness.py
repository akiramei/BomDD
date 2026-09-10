# bomdd-witness — 検査結果を tree に束縛する witness の生成と検証(ECO-062 第 1 弾)
#
# 目的: 運転員が「終わったという主張」でなく「このツリー状態に対してこの検査結果が出た」という
# 証拠片を再検証してから進めるための機構。慎重さでなく機構(§13 第 1 層⑤)。
# 由来: ECO-062 §1-2(witness 形式)・§1-3(遷移条件= hash 一致+機械検証)・§5 Phase 2
# (W1〜W4・known-bad 予行で HEAD^{tree} 比較の fail-open を実測)。
#
# 仕様(v0 で凍結):
#  W1 tree の定義は self-conformance C18 と同一 — 追跡対象+追加可能ファイルの worktree 内容
#     (一時 index に add -A → write-tree)。HEAD^{tree} は未コミット変更を覆えないので使わない。
#  W2 gates[].source は座標(ログのパス・task id)のみ — 値の転写を持たない。
#  W3 stop_type の語彙は bomdd-job.py と共通(固定値)。
#  W4 pre-push の 2 行 witness(.git/bomdd-selfconf-witness)とは別ファイル — 既定は
#     .git/bomdd-witness/<ECO>.json(witness は自分が束縛する tree に含められないため .git 配下)。
#  W5 produce は作業木内(.git 配下を除く)への出力を exit 2 で拒否する — 作業木内の witness は
#     次の write-tree に自分が入って tree を変え、known-good が必ず STOP する(初回 selftest が捕捉)。
#
# 検証の判定: ①witness.tree == 現 worktree tree ②gates 非空かつ全 exit 0 ③stop_type NONE
#   → exit 0(ADVANCE)。①〜③のいずれか不成立 → exit 1(STOP+理由)。witness 不在・読取不能・
#   git 不能 → exit 2(測定不能は合格ではない)。
#
# 使い方:
#   python bomdd-witness.py produce --eco ECO-062 --gate self-conformance=0:scratch/selfconf.log [--stop NONE] [--out PATH]
#   python bomdd-witness.py verify [PATH | --eco ECO-062]
#   python bomdd-witness.py --selftest        # 一時 git リポで陽性対照(good / hash / fail / missing / stop / dirty / 不在 / 作業木内出力)
#
# 検出力の限界(宣言):
#   (1) witness の改竄・削除は信頼境界外(pre-push witness と同じ整理・ECO-046)。
#   (2) gates の exit は produce 時の申告値 — 本ツールは検査を再実行しない(再実測は受入側の責務)。
#   (3) 追跡外かつ .gitignore 対象の変更は tree に入らない(C18 と同じ被覆)。

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

STOP_VOCABULARY = ("NONE", "NORMATIVE_RULING", "VERIFICATION_FAIL", "BOM_CONTRADICTION",
                   "CONVERGENCE_LIMIT", "PREFLIGHT_HOLD", "LEDGER_INCONSISTENT", "MISSING_INPUT")
TREE_DEFINITION = "worktree write-tree (add -A on temp index) — self-conformance C18 と同一"


class _GitUnavailable:
    """git 実行不能(IA-03: FileNotFoundError 等)を returncode 127 の結果として返す — 測定不能は exit 2 へ分類する。"""
    returncode = 127
    stdout = ""
    stderr = "git unavailable"


def _git(root: Path, *args, env=None):
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env)
    except OSError:
        return _GitUnavailable()


def gate_problem(g) -> str | None:
    """IA-01: gate の完全性 — name 非空 str・exit は bool でない int・source 非空 str。問題なしなら None。"""
    if not isinstance(g, dict):
        return "gate が object でない"
    name = g.get("name")
    if not isinstance(name, str) or not name.strip():
        return "gate.name が空"
    ex = g.get("exit")
    if isinstance(ex, bool) or not isinstance(ex, int):
        return f"gate.exit が整数でない({name})"
    src = g.get("source")
    if not isinstance(src, str) or not src.strip():
        return f"gate.source が空({name})— 証拠座標が要る(W2)"
    return None


def worktree_tree(root: Path):
    """W1: 追跡対象+追加可能ファイルの worktree 内容の tree。失敗は None(測定不能)。"""
    gd = _git(root, "rev-parse", "--git-dir")
    if gd.returncode != 0:
        return None, None
    git_dir = Path(gd.stdout.strip())
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    with tempfile.TemporaryDirectory() as td:
        tmp_index = Path(td) / "index"
        src = git_dir / "index"
        if src.exists():
            shutil.copy2(src, tmp_index)
        env = dict(os.environ, GIT_INDEX_FILE=str(tmp_index))
        if _git(root, "add", "-A", env=env).returncode != 0:
            return None, git_dir
        wt = _git(root, "write-tree", env=env)
        if wt.returncode != 0:
            return None, git_dir
        return wt.stdout.strip(), git_dir


def default_path(git_dir: Path, eco: str) -> Path:
    return git_dir / "bomdd-witness" / f"{eco}.json"


def _inside_worktree(path: Path, root: Path, git_dir: Path | None) -> bool:
    """作業木内(かつ .git 配下でない)なら True。解決不能は安全側(True)。"""
    try:
        p = path.resolve()
        r = root.resolve()
    except OSError:
        return True
    if git_dir is not None:
        try:
            p.relative_to(git_dir.resolve())
            return False
        except ValueError:
            pass
    try:
        p.relative_to(r)
        return True
    except ValueError:
        return False


def produce(root: Path, eco: str, gates: list, stop: str, out: Path | None, producer: str) -> tuple[int, str, Path | None]:
    if stop not in STOP_VOCABULARY:
        return 2, f"stop_type 不正: {stop}(語彙= {', '.join(STOP_VOCABULARY)})", None
    for g in gates:  # IA-01: 不完全な gate を書かない(生成側でも拒否)
        prob = gate_problem(g)
        if prob:
            return 2, f"gate 不完全: {prob}", None
    tree, git_dir = worktree_tree(root)
    if tree is None:
        return 2, "tree を取得できない(git 不能 — 測定不能は合格ではない)", None
    if out is not None and _inside_worktree(out, root, git_dir):
        # W5(selftest が自分で捕捉した欠陥): 作業木内に置いた witness は次の write-tree に自分が
        # 含まれて tree を変え、known-good が必ず STOP する(自己参照)。.git 配下か作業木外のみ許す。
        return 2, f"witness を束縛対象の作業木内に置けない(自己参照): {out} — .git 配下か作業木外を指定", None
    head = _git(root, "rev-parse", "HEAD").stdout.strip() or None
    w = {"witness": f"WIT-{eco}", "eco": eco, "tree": tree, "tree_definition": TREE_DEFINITION,
         "head": head, "gates": gates, "stop_type": stop, "producer": producer,
         "produced_at": date.today().isoformat()}
    path = out or default_path(git_dir, eco)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(w, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0, f"witness 生成: {path}(tree {tree[:12]}・gates {len(gates)}・stop {stop})", path


def verify(root: Path, path: Path, eco: str | None = None) -> tuple[int, str]:
    """0= ADVANCE / 1= STOP(理由)/ 2= 測定不能。eco を渡すと個体(witness.eco)を照合する(IA-02)。"""
    try:
        w = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return 2, f"witness 読取不能: {path}({e})— 測定不能は合格ではない"
    if not isinstance(w, dict):
        return 2, "witness 形状不正(object でない)— 測定不能は合格ではない"
    tree, _ = worktree_tree(root)
    if tree is None:
        return 2, "現 tree を取得できない(git 不能)— 測定不能は合格ではない"
    if eco is not None and w.get("eco") != eco:
        return 1, f"STOP: 個体不一致(witness.eco={w.get('eco')} / 要求 {eco})— 別 job の receipt"
    if w.get("tree") != tree:
        return 1, f"STOP: tree 不一致(witness {str(w.get('tree'))[:12]} / 現 {tree[:12]})— 検査後の変更か未検査"
    gates = w.get("gates")
    if not isinstance(gates, list) or not gates:
        return 1, "STOP: gates 欠測(測定不能は合格ではない)"
    for g in gates:  # IA-01: 完全性(name・exit の型・source)を先に見る — 存在だけでは進めない
        prob = gate_problem(g)
        if prob:
            return 1, f"STOP: gate 不完全({prob})"
    bad = [g for g in gates if g["exit"] != 0]
    if bad:
        return 1, f"STOP: gate FAIL 混入({', '.join(g['name'] for g in bad)})"
    if w.get("stop_type") != "NONE":
        return 1, f"STOP: stop_type={w.get('stop_type')}"
    return 0, f"ADVANCE: tree 一致({tree[:12]})・gates {len(gates)} 件 exit 0・stop NONE" + (f"・個体 {eco} 一致" if eco else "")


class ArgError(ValueError):
    """CLI 引数の不正(IA-05)— main で exit 2 に分類する。"""


def parse_gates(argv: list) -> list:
    """--gate name=exit:source(3 要素とも必須)。不正は ArgError。"""
    gates = []
    for i, a in enumerate(argv):
        if a == "--gate":
            if i + 1 >= len(argv):
                raise ArgError("--gate に値がない")
            spec = argv[i + 1]  # name=exit:source
            name, eq, rest = spec.partition("=")
            ex, colon, src = rest.partition(":")
            if not eq or not colon or not name.strip() or not src.strip():
                raise ArgError(f"--gate の形式不正: {spec!r}(name=exit:source・3 要素とも必須)")
            try:
                exit_code = int(ex)
            except ValueError:
                raise ArgError(f"--gate の exit が整数でない: {spec!r}") from None
            gates.append({"name": name, "exit": exit_code, "source": src})
    return gates


def _opt(argv: list, flag: str) -> str | None:
    """flag の値を返す。flag があるのに値がなければ ArgError。flag がなければ None。"""
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
        raise ArgError(f"{flag} に値がない")
    return argv[i + 1]


# --- selftest: 一時 git リポで陽性対照(実リポの作業木に触れない) ---------------------------
def selftest() -> int:
    fails = []
    # witness の出力先は作業木の**外**(wd)— 作業木内に置くと自分が tree に入る(W5・初回 selftest が捕捉)
    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as wd:
        root = Path(td)
        wout = Path(wd)
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@x", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
        for cmd in (["init", "-q"], ["config", "core.autocrlf", "false"]):
            if _git(root, *cmd, env=env).returncode != 0:
                return _report(["fixture: git init 不能"])
        (root / "a.txt").write_text("a\n", encoding="utf-8", newline="\n")
        _git(root, "add", "-A", env=env)
        if _git(root, "commit", "-q", "-m", "init", env=env).returncode != 0:
            return _report(["fixture: commit 不能"])
        out = wout / "w.json"
        rc, msg, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE", out, "selftest")
        if rc != 0:
            return _report([f"produce: {msg}"])
        good = json.loads(out.read_text(encoding="utf-8"))
        rc_in, msg_in, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE",
                                   root / "inside.json", "selftest")
        if rc_in != 2 or (root / "inside.json").exists():
            fails.append(f"kb-inside: 作業木内への出力が exit {rc_in}(2 で拒否すべき)")
        rc_git, _, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE",
                               root / ".git" / "bomdd-witness" / "ECO-900.json", "selftest")
        if rc_git != 0:
            fails.append(f"default(.git 配下)への出力が exit {rc_git}")

        def arm(name: str, w: dict | None, want: int):
            p = wout / f"{name}.json"
            if w is not None:
                p.write_text(json.dumps(w), encoding="utf-8")
            rc, msg = verify(root, p)
            if rc != want:
                fails.append(f"{name}: exit {rc} != {want}({msg})")

        arm("known-good", good, 0)
        arm("kb-hash", dict(good, tree=good["tree"][:-4] + ("0000" if good["tree"][-4:] != "0000" else "1111")), 1)
        arm("kb-fail", dict(good, gates=[{"name": "g", "exit": 1, "source": "x"}]), 1)
        arm("kb-missing", dict(good, gates=[]), 1)
        arm("kb-stop", dict(good, stop_type="NORMATIVE_RULING"), 1)
        arm("kb-absent", None, 2)
        # dirty 腕: 未追跡ファイルを置くと known-good でも STOP(HEAD^{tree} 比較なら素通りする腕)
        (root / "dirty.tmp").write_text("d\n", encoding="utf-8")
        head_tree = _git(root, "rev-parse", "HEAD^{tree}", env=env).stdout.strip()
        if head_tree != good["tree"]:
            fails.append("dirty 前提: clean 時は HEAD^{tree} == worktree tree のはず")
        arm("kb-dirty", good, 1)
        (root / "dirty.tmp").unlink()
        rc_bad_stop, msg_bad_stop, _ = produce(root, "ECO-900", [], "BOGUS", wout / "x.json", "selftest")
        if rc_bad_stop != 2:
            fails.append(f"produce: 不正 stop_type が exit {rc_bad_stop}")
        # --- r2 追加腕(独立検査 IA-01〜03・05 の陽性対照)---
        # IA-01: 構造不完全な gate(空名・bool exit・source なし)は存在しても ADVANCE しない
        arm("kb-structural", dict(good, gates=[{"name": "", "exit": False, "source": None}]), 1)
        arm("kb-bool-exit", dict(good, gates=[{"name": "g", "exit": False, "source": "x"}]), 1)
        arm("kb-no-source", dict(good, gates=[{"name": "g", "exit": 0}]), 1)
        rc_inc, _, _ = produce(root, "ECO-900", [{"name": "", "exit": 0, "source": "x"}], "NONE", wout / "inc.json", "selftest")
        if rc_inc != 2:
            fails.append(f"produce: 不完全 gate が exit {rc_inc}(2 で拒否すべき)")
        # IA-02: 個体照合 — 別 ECO の witness を --eco で受理しない / 一致なら 0
        p = wout / "eco.json"
        p.write_text(json.dumps(good), encoding="utf-8")
        rc_mis, _ = verify(root, p, eco="ECO-901")
        rc_hit, _ = verify(root, p, eco="ECO-900")
        if rc_mis != 1 or rc_hit != 0:
            fails.append(f"kb-eco-mismatch: 不一致 exit {rc_mis}(1)/ 一致 exit {rc_hit}(0)")
        # IA-03: git 実行不能は exit 2(traceback でない)
        saved = os.environ.get("PATH")
        try:
            os.environ["PATH"] = ""
            rc_nogit, _ = verify(root, out)
            rc_nogit_p, _, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE", wout / "ng.json", "selftest")
        finally:
            if saved is None:
                del os.environ["PATH"]
            else:
                os.environ["PATH"] = saved
        if rc_nogit != 2 or rc_nogit_p != 2:
            fails.append(f"kb-nogit: verify exit {rc_nogit} / produce exit {rc_nogit_p}(2 であるべき)")
        # IA-05: 引数不正は ArgError(main で exit 2)
        for bad_argv in (["--gate", "malformed"], ["--gate", "g=x:src"], ["--gate", "g=0"], ["--gate"]):
            try:
                parse_gates(bad_argv)
                fails.append(f"parse_gates が {bad_argv} を受理")
            except ArgError:
                pass
        for bad_argv, flag in ((["verify", "--eco"], "--eco"), (["produce", "--eco", "--out", "x"], "--eco")):
            try:
                _opt(bad_argv, flag)
                fails.append(f"_opt が {bad_argv} を受理")
            except ArgError:
                pass
    return _report(fails)


def _report(fails) -> int:
    if fails:
        print("bomdd-witness selftest FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("bomdd-witness selftest PASS(known-good 0 / hash・fail・missing・stop・dirty 1 / 不在 2 / 不正 stop 2 / 作業木内出力 2 / "
          "r2: 構造不完全 gate 1・不完全 gate 生成拒否 2・個体不一致 1・git 不能 2・引数不正 ArgError)")
    return 0


def main(argv) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", newline="\n")
    if "--selftest" in argv:
        return selftest()
    if not argv:
        print(__doc__ or "usage: produce | verify | --selftest")
        return 2
    root = Path.cwd()
    cmd = argv[0]
    try:
        eco = _opt(argv, "--eco")
        out_s = _opt(argv, "--out")
        out = Path(out_s) if out_s else None
        if cmd == "produce":
            if not eco:
                raise ArgError("--eco が必要")
            stop = _opt(argv, "--stop") or "NONE"
            producer = _opt(argv, "--producer") or "unknown(self-reported)"
            rc, msg, _ = produce(root, eco, parse_gates(argv), stop, out, producer)
            print(msg)
            return rc
        if cmd == "verify":
            path = out
            if path is None:
                consumed = {v for f in ("--eco", "--out", "--stop", "--producer", "--gate")
                            for v in ([_opt(argv, f)] if f != "--gate" else [])} - {None}
                pos = [a for a in argv[1:] if not a.startswith("--") and a not in consumed]
                if pos:
                    path = Path(pos[0])
                elif eco:
                    _, git_dir = worktree_tree(root)
                    if git_dir is None:
                        print("git 不能 — 測定不能は合格ではない")
                        return 2
                    path = default_path(git_dir, eco)
            if path is None:
                raise ArgError("verify: PATH か --eco が必要")
            rc, msg = verify(root, path, eco)
            print(msg)
            return rc
        raise ArgError(f"不明なコマンド: {cmd}")
    except ArgError as e:  # IA-05: 引数不正は traceback でなく exit 2(測定不能側)
        print(f"引数不正: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
