# dwell-session-hook — Claude Code の SessionStart hook: BomDD リポでセッションを始めたら滞留の短い形を文脈に出す(ECO-124 P2)
#
# 目的: 進捗の表示(bomdd-job --dwell)を、誰かが思い出して走らせることに頼らない。hook の標準出力は Claude Code が
# セッションの文脈に加える。判断の規則は playbook §8(この道具は表示だけ — 止めない・判定しない)。
#
# 動き:
#   - 入力(標準入力の JSON)の cwd、無ければプロセスの cwd から git の top を求め、register を
#     bomdd/60-change-register.yaml → bomdd/process/change-register.yaml の順に探す。無ければ何も出さず exit 0(他のリポに触れない)。
#   - 有れば同じフォルダの bomdd-job.py を --dwell --brief で走らせ、時間の上限(既定 75 秒)の中で出力をそのまま出す。
#   - 失敗・上限到達・想定外の出力は「dwell: not measured — 理由」の 1 行(黙らない・セッションを止めない)。hook としては常に exit 0。
#
# 使い方:
#   python dwell-session-hook.py                 # hook として(標準入力に Claude Code の JSON)
#   python dwell-session-hook.py --check [--settings PATH]   # ~/.claude/settings.json に入っているか(exit 0 入っている / 1 ない / 2 読めない)
#   python dwell-session-hook.py --selftest
#
# 入れ方(1 台に 1 回・ユーザー設定): ~/.claude/settings.json の hooks に
#   "SessionStart": [{"matcher": "startup|resume|clear|compact",
#                     "hooks": [{"type": "command", "command": "python -X utf8 \"<BomDD>/method/tools/dwell-session-hook.py\"", "timeout": 90}]}]
#
# 限界(宣言): Claude Code のセッションで hook を入れた機械だけに出る(他のハーネスは AGENTS.md の手動コマンド)。
#   最初の 1 回は解析キャッシュが空で遅い(ViewTube 約 40 秒)— 上限を超えると「not measured」で、キャッシュは書かれないまま。
#   出力は最後の SessionStart の時点のもの。register の内容が正しいかは読まない(ECO-120 の限界のまま)。

import io
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
JOB_TOOL = TOOLS_DIR / "bomdd-job.py"
REGISTER_CANDIDATES = ("bomdd/60-change-register.yaml", "bomdd/process/change-register.yaml")
BOUND_SECONDS = 75
HOOK_NAME = "dwell-session-hook.py"


def not_measured(reason: str) -> str:
    return f"dwell: not measured — {reason}\n"


def resolve_cwd(stdin_text: str) -> str:
    """入力の cwd(文字列で実在するフォルダ)を使い、それ以外はプロセスの cwd。"""
    try:
        data = json.loads(stdin_text) if stdin_text.strip() else {}
    except ValueError:
        data = {}
    cwd = data.get("cwd") if isinstance(data, dict) else None
    return cwd if isinstance(cwd, str) and cwd and os.path.isdir(cwd) else os.getcwd()


def find_register(cwd: str):
    """(top, rel) か None。git でないフォルダ・register のないリポは None(何も出さない)。"""
    try:
        r = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    top = Path(r.stdout.decode("utf-8", "replace").strip())
    for rel in REGISTER_CANDIDATES:
        if (top / rel).is_file():
            return top, rel
    return None


def _kill_tree(p):
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
    else:
        import signal
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            p.kill()


def run_brief(top: Path, rel: str, tool: Path = JOB_TOOL, bound: float = BOUND_SECONDS, env=None) -> str:
    """bomdd-job --dwell --brief を上限つきで走らせ、出す文字列を返す(失敗は 1 行)。"""
    cmd = [sys.executable, "-X", "utf8", str(tool), "--dwell", "--brief", "--register", rel]
    kw = {"start_new_session": True} if os.name != "nt" else {}
    try:
        p = subprocess.Popen(cmd, cwd=str(top), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, **kw)
    except OSError as e:
        return not_measured(f"could not start the tool: {type(e).__name__}: {str(e)[:120]}")
    try:
        out, err = p.communicate(timeout=bound)
    except subprocess.TimeoutExpired:
        _kill_tree(p)
        try:
            p.communicate(timeout=10)
        except subprocess.SubprocessError:
            pass
        return not_measured(f"time bound {bound:g} s reached (run bomdd-job --dwell --brief by hand)")
    text = out.decode("utf-8", "replace")
    if p.returncode != 0:
        tail = err.decode("utf-8", "replace").strip().splitlines()[-1:] or ["(no message)"]
        return not_measured(f"tool exit {p.returncode}: {tail[0][:160]}")
    if not text.startswith("dwell: "):
        return not_measured(f"unexpected tool output: {text[:80]!r}")
    return text


def hook_main(stdin_text: str, tool: Path = JOB_TOOL, bound: float = BOUND_SECONDS, env=None) -> str:
    try:
        found = find_register(resolve_cwd(stdin_text))
        if found is None:
            return ""
        return run_brief(found[0], found[1], tool, bound, env)
    except Exception as e:  # noqa: BLE001 — どの失敗も黙らない(「止まったものはない」と見分けがつかなくなる)
        return not_measured(f"{type(e).__name__}: {str(e)[:160]}")


def check_install(settings: Path) -> tuple:
    """(exit, 1 行)。0= 入っている・1= ない・2= 読めない。"""
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return 1, f"not installed: {settings} does not exist"
    except (OSError, ValueError) as e:
        return 2, f"settings unreadable: {settings}: {type(e).__name__}: {str(e)[:120]}"
    groups = ((data.get("hooks") or {}).get("SessionStart") or []) if isinstance(data, dict) else []
    for g in groups if isinstance(groups, list) else []:
        for h in (g.get("hooks") or []) if isinstance(g, dict) else []:
            cmd = h.get("command", "") if isinstance(h, dict) else ""
            if isinstance(cmd, str) and HOOK_NAME in cmd:
                return 0, f"installed: matcher {g.get('matcher', '(all)')!r}, timeout {h.get('timeout', '(default)')}, command {cmd}"
    return 1, f"not installed: no SessionStart entry runs {HOOK_NAME} in {settings}"


def selftest() -> int:
    """ECO-124 V3 の腕。git を使う(fixture のリポは一時フォルダ)。"""
    fails = []
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)

    def git(root, *a):
        r = subprocess.run(["git", "-C", str(root), *a], capture_output=True, env=env)
        if r.returncode != 0:
            raise RuntimeError(f"fixture git {a[:2]}: {r.stderr.decode(errors='replace')[:120]}")

    def repo(root, rel=None, commit=True):
        root.mkdir()
        git(root, "init", "-q")
        git(root, "config", "core.autocrlf", "false")
        if rel:
            p = root / rel
            p.parent.mkdir(parents=True)
            p.write_text("changes:\n  - id: ECO-001\n    title: t\n    status: filed\n", encoding="utf-8", newline="\n")
            if commit:
                git(root, "add", "-A")
                git(root, "commit", "-q", "-m", "c")
        return root

    def run(stdin_text, **kw):
        return hook_main(stdin_text, env=cenv, **kw)

    try:
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            cenv = dict(env, BOMDD_DWELL_CACHE_DIR=str(t / "cache"))
            # (a) register のないリポ・git でないフォルダ → 何も出さない
            none_repo = repo(t / "none")
            plain = t / "plain"
            plain.mkdir()
            for d in (none_repo, plain):
                if run(json.dumps({"cwd": str(d)})) != "":
                    fails.append(f"(a) register のない場所で出力した: {d.name}")
            # (b) register のあるリポ(両方の置き場所)→ 短い形
            for name, rel in (("p1", REGISTER_CANDIDATES[0]), ("p2", REGISTER_CANDIDATES[1])):
                r = repo(t / name, rel)
                out = run(json.dumps({"cwd": str(r / "bomdd")}))   # サブフォルダからでも top を見つける
                if not out.startswith(f"dwell: {name} {rel} — open 1, over 14 d 0"):
                    fails.append(f"(b) {rel}: 短い形が出ない: {out[:120]!r}")
            # (c) 道具が測れない(未コミットの register)→ 道具自身の 1 行 / 道具が落ちる → hook の 1 行
            unc = repo(t / "unc", REGISTER_CANDIDATES[0], commit=False)
            out = run(json.dumps({"cwd": str(unc)}))
            if not (out.startswith("dwell: not measured — ") and out.count("\n") == 1):
                fails.append(f"(c) 未コミットの register で 1 行にならない: {out[:120]!r}")
            crash = t / "crash.py"
            crash.write_text("import sys\nsys.stderr.write('boom\\n')\nsys.exit(3)\n", encoding="utf-8")
            out = run(json.dumps({"cwd": str(t / "p1")}), tool=crash)
            if out != not_measured("tool exit 3: boom"):
                fails.append(f"(c) 落ちた道具が 1 行にならない: {out[:120]!r}")
            odd = t / "odd.py"
            odd.write_text("print('hello')\n", encoding="utf-8")
            if not run(json.dumps({"cwd": str(t / "p1")}), tool=odd).startswith("dwell: not measured — unexpected tool output"):
                fails.append("(c) 想定外の出力が 1 行にならない")
            # (d) 上限 → 1 行・上限のあたりで戻る(子の子も止める)
            slow = t / "slow.py"
            slow.write_text("import subprocess, sys, time\nsubprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n"
                            "time.sleep(30)\n", encoding="utf-8")
            t0 = time.perf_counter()
            out = run(json.dumps({"cwd": str(t / "p1")}), tool=slow, bound=1.5)
            el = time.perf_counter() - t0
            if not out.startswith("dwell: not measured — time bound 1.5 s reached") or el > 12:
                fails.append(f"(d) 上限: {el:.1f} 秒・{out[:100]!r}")
            # (e) cwd のない入力・空・JSON でない・実在しない cwd → プロセスの cwd
            here = os.getcwd()
            os.chdir(t / "p1")
            try:
                for s in ("{}", "", "not json", json.dumps({"cwd": str(t / "missing")}), json.dumps({"cwd": 5})):
                    if not run(s).startswith("dwell: p1 "):
                        fails.append(f"(e) 入力 {s[:30]!r} でプロセスの cwd を使わない")
            finally:
                os.chdir(here)
            # (f) --check: 入っている / ない / ファイルなし / 読めない
            s_in = t / "in.json"
            s_in.write_text(json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "x"}]}],
                                                  "SessionStart": [{"matcher": "startup", "hooks": [
                                                      {"type": "command", "command": f"python {HOOK_NAME}", "timeout": 90}]}]}}),
                            encoding="utf-8")
            s_out = t / "out.json"
            s_out.write_text(json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "x"}]}]}}), encoding="utf-8")
            s_bad = t / "bad.json"
            s_bad.write_text("{not json", encoding="utf-8")
            got = [check_install(p)[0] for p in (s_in, s_out, t / "absent.json", s_bad)]
            if got != [0, 1, 1, 2]:
                fails.append(f"(f) --check の結果 {got} != [0, 1, 1, 2]")
    except Exception as e:  # noqa: BLE001 — fixture の構築失敗は測定不能
        print(f"dwell-session-hook selftest UNMEASURABLE: {type(e).__name__}: {str(e)[:160]}")
        return 2
    if fails:
        print("dwell-session-hook selftest FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("dwell-session-hook selftest PASS(ECO-124 V3: register なし/git でない= 無言・register 2 か所×サブフォルダ= 短い形・"
          "道具の測れない 1 行・落ちた道具/想定外の出力= hook の 1 行・上限 1.5 秒で子の子ごと止めて 1 行・cwd なし/空/JSON でない/"
          "実在しない/型違い= プロセスの cwd・--check 4 種)")
    return 0


def main(argv) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", newline="\n")
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        settings = Path.home() / ".claude" / "settings.json"
        if "--settings" in argv:
            i = argv.index("--settings")
            if i + 1 >= len(argv):
                print("settings unreadable: --settings に値がない")
                return 2
            settings = Path(argv[i + 1])
        rc, line = check_install(settings)
        print(line)
        return rc
    try:
        stdin_text = sys.stdin.buffer.read().decode("utf-8", "replace") if sys.stdin and not sys.stdin.isatty() else ""
    except (OSError, ValueError, AttributeError):
        stdin_text = ""
    print(hook_main(stdin_text), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
