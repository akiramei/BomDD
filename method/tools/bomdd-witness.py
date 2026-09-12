# bomdd-witness — 検査結果を tree に束縛する witness の生成と検証(ECO-062 第 1 弾・ECO-066 で報告形式を固定)
#
# 目的: 運転員が「終わったという主張」でなく「このツリー状態に対してこの検査結果が出た」という
# 証拠片を再検証してから進めるための機構。慎重さでなく機構(§13 第 1 層⑤)。
# 由来: ECO-062 §1-2(witness 形式)・§1-3(遷移条件= hash 一致+機械検証)・§5 Phase 2
# (W1〜W4・known-bad 予行で HEAD^{tree} 比較の fail-open を実測)・ECO-066(Phase 5 run-01 の所見
# P5-01/02/03/06/07: 運転員が報告を機構で読めるように 1 行目を固定・個体照合を既定化)。
#
# 仕様(v0 で凍結・W6/W7 は ECO-066):
#  W1 tree の定義は self-conformance C18 と同一 — 追跡対象+追加可能ファイルの worktree 内容
#     (一時 index に add -A → write-tree)。HEAD^{tree} は未コミット変更を覆えないので使わない。
#  W2 gates[].source は座標(ログのパス・task id)のみ — 値の転写を持たない。
#  W3 stop_type の語彙は bomdd-job.py と共通(固定値)。
#  W4 pre-push の 2 行 witness(.git/bomdd-selfconf-witness)とは別ファイル — 既定は
#     .git/bomdd-witness/<ECO>.json(witness は自分が束縛する tree に含められないため .git 配下)。
#  W5 produce は作業木内(.git 配下を除く)への出力を exit 2 で拒否する — 作業木内の witness は
#     次の write-tree に自分が入って tree を変え、known-good が必ず STOP する(初回 selftest が捕捉)。
#     判定は Windows 拡張長パス(\\?\C:\...)の接頭辞を剥がし normcase で比較する(IA-08・r3)。
#  W6 CLI の標準出力 1 行目は **全経路**(verify・produce・--selftest・引数不正)で `<VERDICT> <CODE>[(<CAUSE>)]: <message>`
#     に固定する(ECO-066 §1-1・r1 IA-01 で produce/selftest も対象に)。VERDICT= ADVANCE / STOP / UNMEASURABLE は終了コード
#     0 / 1 / 2 と 1 対 1(produce の成功は ADVANCE PRODUCED・selftest の失敗は STOP SELFTEST_FAIL)。CODE は本ツールローカルの語彙
#     (CODES 15・job の停止語彙とは別物・本 ECO で閉じる)。運転員の実行基盤が終了コードを丸めても(pwsh -Command は
#     非 0 を 1 にする・P5-07)1 行目で 3 値と理由を機械的に読める。tree 不一致は両 tree を 40 桁で示し
#     最初に異なる位置を添える(P5-03)。測定不能は原因(TREE_CAUSES 7)を添える(P5-06)。GIT_UNAVAILABLE は「git を起動できない
#     (OSError)」のみ — 起動できた git/ラッパーの非 0 は rc 127 でも GIT_DIR_FAILED 等(r1 IA-03)。index の複製失敗は
#     INDEX_COPY_FAILED(r1 IA-02)。git の stdout/stderr は utf-8・errors=replace で読む(r1 IA-04・非 UTF-8 でも落ちない)。
#  W7 CLI の `verify PATH` は `--eco ECO` が必須 — 無ければ UNMEASURABLE IDENTITY_UNCHECKED(exit 2)。
#     個体未照合の receipt で進むのは「別 job の receipt を流用する」失敗型(Phase 5 R3)。関数 verify(eco=None)
#     は selftest 用に省略可のまま。
#
# 検証の判定: ①witness.eco == 要求 ECO ②witness.tree == 現 worktree tree ③gates 非空かつ全 exit 0
#   ④stop_type NONE → exit 0(ADVANCE OK)。①〜④のいずれか不成立 → exit 1(STOP <CODE>)。witness 不在・
#   読取不能・形状不正・git 不能・一時 index 不能・個体未照合(CLI)→ exit 2(UNMEASURABLE <CODE> — 測定不能は
#   合格ではない)。
#
# 使い方:
#   python bomdd-witness.py produce --eco ECO-062 --gate self-conformance=0:scratch/selfconf.log [--stop NONE] [--out PATH]
#   python bomdd-witness.py verify --eco ECO-062              # 既定パス(.git/bomdd-witness/ECO-062.json)を個体照合つきで検証
#   python bomdd-witness.py verify PATH --eco ECO-062         # 任意パス。--eco は必須(個体照合・W7)
#   python bomdd-witness.py --selftest        # 一時 git リポで陽性対照(CODE ごとの腕・CAUSE ごとの腕・CLI 腕)
#
# 検出力の限界(宣言):
#   (1) witness の改竄・削除は信頼境界外(pre-push witness と同じ整理・ECO-046)。
#   (2) gates の exit は produce 時の申告値 — 本ツールは検査を再実行しない(再実測は受入側の責務)。
#   (3) 追跡外かつ .gitignore 対象の変更は tree に入らない(C18 と同じ被覆)。
#   (4) 1 行目の形式は運転員が読むための契約で、終了コードの丸めそのもの(実行基盤側)は直せない。

import io
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

STOP_VOCABULARY = ("NONE", "NORMATIVE_RULING", "VERIFICATION_FAIL", "BOM_CONTRADICTION",
                   "CONVERGENCE_LIMIT", "PREFLIGHT_HOLD", "LEDGER_INCONSISTENT", "MISSING_INPUT")
TREE_DEFINITION = "worktree write-tree (add -A on temp index) — self-conformance C18 と同一"
# W6: 検証報告の語彙(本ツールローカル・job の停止語彙 W3 とは別物)
VERDICTS = {0: "ADVANCE", 1: "STOP", 2: "UNMEASURABLE"}
CODES = ("OK", "IDENTITY_MISMATCH", "IDENTITY_UNCHECKED", "TREE_MISMATCH", "GATES_MISSING", "GATE_INCOMPLETE",
         "GATE_FAIL", "STOP_TYPE", "WITNESS_UNREADABLE", "WITNESS_MALFORMED", "TREE_UNAVAILABLE", "ARG_ERROR",
         "PRODUCED", "WITNESS_UNWRITABLE", "SELFTEST_FAIL")   # r1 IA-01: produce / selftest の経路も固定形式に
TREE_CAUSES = ("GIT_UNAVAILABLE", "GIT_DIR_FAILED", "TEMP_UNAVAILABLE", "INDEX_COPY_FAILED", "TEMP_IN_WORKTREE", "ADD_FAILED",
               "WRITE_TREE_FAILED")   # r1 IA-02: index 複製の失敗を temp 不能と分ける
# r1 IA-04: git の出力は utf-8・置換で読む — 非 UTF-8 バイトで reader thread が落ちて stderr 末尾を失わない
_RUN_KW = dict(capture_output=True, text=True, encoding="utf-8", errors="replace")


def report_line(rc: int, code: str, msg: str, cause: str | None = None) -> str:
    """W6: 1 行目の固定形式。語彙外の code/cause は selftest で弾く(本番で来たら文字列のまま出す)。"""
    return f"{VERDICTS[rc]} {code}" + (f"({cause})" if cause else "") + f": {msg}"


class _GitUnavailable:
    """git 実行不能(IA-03: FileNotFoundError 等)を returncode 127 の結果として返す — 測定不能は exit 2 へ分類する。"""
    returncode = 127
    stdout = ""
    stderr = "git unavailable"


def _git(root: Path, *args, env=None):
    try:
        return subprocess.run(["git", "-C", str(root), *args], env=env, **_RUN_KW)
    except OSError:
        return _GitUnavailable()


def _tail(text) -> str:
    """git stderr の末尾 1 行(空なら "")。message に添える(P5-06)。"""
    lines = [ln.strip() for ln in str(text or "").splitlines() if ln.strip()]
    return lines[-1][:200] if lines else ""


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
    """W1: 追跡対象+追加可能ファイルの worktree 内容の tree。
    返り値 (tree, git_dir, err) — 失敗は tree=None・err=(CAUSE, detail)(P5-06: 5 経路を区別・原因を捨てない)。"""
    gd = _git(root, "rev-parse", "--git-dir")
    if gd.returncode != 0:
        # r1 IA-03: GIT_UNAVAILABLE は「起動できない」(OSError の番兵)だけ — 起動できた git/ラッパーの rc 127 は GIT_DIR_FAILED
        cause = "GIT_UNAVAILABLE" if isinstance(gd, _GitUnavailable) else "GIT_DIR_FAILED"
        return None, None, (cause, _tail(gd.stderr))
    git_dir = Path(gd.stdout.strip())
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    try:
        # IA-06: 一時 index の置き場を作れない(OS temp 不能)は測定不能 → TEMP_UNAVAILABLE(exit 2)。traceback にしない。
        # 後片付けの失敗(sandbox 所有等)は測定結果に関係しないので無視する(r1b・with ブロック外へ例外を出さない)
        tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    except OSError as e:
        return None, git_dir, ("TEMP_UNAVAILABLE", f"{e.__class__.__name__}: {str(e)[:200]}")
    with tmp as td:
        # IA-06 変種(受理側で実測): tempfile が cwd= 作業木へフォールバックすると一時 dir 自身が
        # add -A で tree に入り「tree 不一致」を偽生成する — 作業木内の temp は測定不能として拒否。
        if _inside_worktree(Path(td), root, git_dir):
            return None, git_dir, ("TEMP_IN_WORKTREE", str(td))
        tmp_index = Path(td) / "index"
        src = git_dir / "index"
        try:
            if src.exists():
                shutil.copy2(src, tmp_index)
        except OSError as e:  # r1 IA-02: 既存 index の読取/複製失敗は temp 不能ではない
            return None, git_dir, ("INDEX_COPY_FAILED", f"{e.__class__.__name__}: {str(e)[:200]}")
        env = dict(os.environ, GIT_INDEX_FILE=str(tmp_index))
        added = _git(root, "add", "-A", env=env)
        if added.returncode != 0:
            cause = "GIT_UNAVAILABLE" if isinstance(added, _GitUnavailable) else "ADD_FAILED"
            return None, git_dir, (cause, _tail(added.stderr))
        wt = _git(root, "write-tree", env=env)
        if wt.returncode != 0:
            cause = "GIT_UNAVAILABLE" if isinstance(wt, _GitUnavailable) else "WRITE_TREE_FAILED"
            return None, git_dir, (cause, _tail(wt.stderr))
        return wt.stdout.strip(), git_dir, None


def default_path(git_dir: Path, eco: str) -> Path:
    return git_dir / "bomdd-witness" / f"{eco}.json"


def _canon(path: Path) -> str:
    """IA-08(r3): Windows 拡張長パス(\\\\?\\C:\\... / \\\\?\\UNC\\...)は resolve() が接頭辞を保持し、
    relative_to が別ルート扱いにする — 接頭辞を剥がし normcase で比較する。"""
    s = str(path)
    if s.startswith("\\\\?\\UNC\\"):
        s = "\\\\" + s[8:]
    elif s.startswith("\\\\?\\"):
        s = s[4:]
    return os.path.normcase(str(Path(s).resolve()))


def _inside_worktree(path: Path, root: Path, git_dir: Path | None) -> bool:
    """作業木内(かつ .git 配下でない)なら True。解決不能は安全側(True)。"""
    try:
        p = _canon(path)
        r = _canon(root)
        g = _canon(git_dir) if git_dir is not None else None
    except OSError:
        return True
    sep = os.sep
    if g is not None and (p == g or p.startswith(g.rstrip(sep) + sep)):
        return False
    return p == r or p.startswith(r.rstrip(sep) + sep)


def produce(root: Path, eco: str, gates: list, stop: str, out: Path | None, producer: str) -> tuple[int, str, Path | None]:
    """(rc, 1 行目, path)— 1 行目は W6 の固定形式(r1 IA-01: produce の経路も対象)。"""
    if stop not in STOP_VOCABULARY:
        return 2, report_line(2, "ARG_ERROR", f"stop_type 不正: {stop}(語彙= {', '.join(STOP_VOCABULARY)})"), None
    for g in gates:  # IA-01: 不完全な gate を書かない(生成側でも拒否)
        prob = gate_problem(g)
        if prob:
            return 2, report_line(2, "GATE_INCOMPLETE", f"gate 不完全: {prob}"), None
    tree, git_dir, err = worktree_tree(root)
    if tree is None:
        cause, detail = err
        return 2, report_line(2, "TREE_UNAVAILABLE", f"tree を取得できない({detail or '詳細なし'})— 測定不能は合格ではない", cause), None
    if out is not None and _inside_worktree(out, root, git_dir):
        # W5(selftest が自分で捕捉した欠陥): 作業木内に置いた witness は次の write-tree に自分が
        # 含まれて tree を変え、known-good が必ず STOP する(自己参照)。.git 配下か作業木外のみ許す。
        return 2, report_line(2, "ARG_ERROR", f"witness を束縛対象の作業木内に置けない(自己参照): {out} — .git 配下か作業木外を指定"), None
    head = _git(root, "rev-parse", "HEAD").stdout.strip() or None
    w = {"witness": f"WIT-{eco}", "eco": eco, "tree": tree, "tree_definition": TREE_DEFINITION,
         "head": head, "gates": gates, "stop_type": stop, "producer": producer,
         "produced_at": date.today().isoformat()}
    path = out or default_path(git_dir, eco)
    try:  # IA-08b(受理側追加): 書込不能・不正パスは traceback でなく測定不能 exit 2
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(w, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    except OSError as e:
        return 2, report_line(2, "WITNESS_UNWRITABLE", f"witness を書けない: {path}({e.__class__.__name__})— 測定不能は合格ではない"), None
    return 0, report_line(0, "PRODUCED", f"witness 生成: {path}(tree {tree[:12]}・gates {len(gates)}・stop {stop})"), path


# --- ECO-074(Phase 7 第 3 弾): inspection gate を run 台帳から導出 -------------------------------------
# 申告(--gate)でなく、入口 bomdd-run が書いた台帳(.git/bomdd-run/<ECO>.jsonl)の最後の report つき cell 行から導出する(W2 と両立)。
# exit の固定写像: ACCEPT かつ range=是正確認+回帰 → 0 / REJECT → 1 / MISSING・UNPARSED・range が境界探索・range なし → 2。
# produce 時に現在の報告ファイルの sha256 が台帳と一致しなければ gate を作らない(ARG_ERROR)。
INSPECTION_ACCEPT_RANGE = "是正確認+回帰"


def _ledger_report_path_error(root: Path, git_dir: Path | None, path: str) -> str | None:
    """r1 IA-03: 台帳の report.path にも入口(bomdd-run --report)と同じ境界を課す — リポ相対・`..`/絶対/空要素/前後空白なし・作業木内・.git 配下不可。"""
    s = path.replace("\\", "/")
    if not s.strip() or s.strip() != s or s.startswith("/") or re.match(r"^[A-Za-z]:", s) or any(seg in ("..", "") for seg in s.split("/")):
        return f"台帳の report.path がリポ相対でない: {path!r}"
    p = root / s
    try:
        if os.path.commonpath([p.resolve(), root.resolve()]) != str(root.resolve()):
            return "台帳の report.path が作業木の外を指す"
        if git_dir is not None and os.path.commonpath([p.resolve(), git_dir.resolve()]) == str(git_dir.resolve()):
            return "台帳の report.path が .git 配下を指す"
    except (OSError, ValueError):
        return "台帳の report.path を解決できない"
    return None


def inspection_gate_from_ledger(root: Path, ledger: Path, eco: str, git_dir: Path | None = None):
    """(gate, None) / (None, 理由)。r1: 壊れた行は台帳不正(IA-01)・行の eco を個体照合(IA-02)・path の境界(IA-03)・sha は MISSING 以外で必須(IA-04)。"""
    try:
        lines = ledger.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return None, f"run 台帳を読めない: {ledger.name}({e.__class__.__name__})"
    row = None
    for i, ln in enumerate(lines, 1):
        if not ln.strip():
            continue
        try:
            r = json.loads(ln)
        except ValueError:
            return None, f"run 台帳に壊れた行がある({i} 行目)— 測定不能は合格ではない"
        if not isinstance(r, dict):
            return None, f"run 台帳の {i} 行目が object でない"
        if r.get("event") == "cell" and isinstance(r.get("report"), dict):
            row = r
    if row is None:
        return None, "run 台帳に report つきの cell 行がない"
    if row.get("eco") != eco:
        return None, f"台帳の cell 行の個体が一致しない: {row.get('eco')!r} != {eco}"
    rp = row["report"]
    path, sha, verdict, rng = rp.get("path"), rp.get("sha256"), rp.get("verdict"), rp.get("range")
    if not isinstance(path, str) or not path:
        return None, "台帳の report.path がない"
    perr = _ledger_report_path_error(root, git_dir, path)
    if perr:
        return None, perr
    if verdict == "ACCEPT" and rng == INSPECTION_ACCEPT_RANGE:
        ex = 0
    elif verdict == "REJECT":
        ex = 1
    else:
        ex = 2   # MISSING / UNPARSED / 境界探索の ACCEPT / range なし = 受入根拠にならない(測定不能側)
    if verdict == "MISSING":   # 報告なしの記録: sha は持たない(exit 2 の gate として残す)
        if sha:
            return None, "台帳の MISSING 行に sha256 がある(形状不正)"
    else:   # r1 IA-04: MISSING 以外は sha 必須・現在の報告と一致
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            return None, "台帳の report.sha256 がない/形状不正(64 桁小文字 hex)"
        try:
            cur = hashlib.sha256((root / path).read_bytes()).hexdigest()
        except OSError:
            return None, f"報告ファイルを読めない: {path}"
        if cur != sha:
            return None, f"報告の sha256 が台帳と一致しない: {path}"
    gate = {"name": "inspection", "exit": ex, "source": path, "verdict": verdict, "sha256": sha, "range": rng,
            "executor": row.get("executor"), "run_id": row.get("run_id")}
    return gate, None


def _first_diff(a: str, b: str) -> str:
    """P5-03: 最初に異なる位置(0 起点)。長さ違いは短い方の長さ。"""
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return str(i)
    return str(n) if len(a) != len(b) else "なし"


def _verify(root: Path, path: Path, eco: str | None = None) -> tuple[int, str, str | None, str]:
    """(rc, code, cause, msg)。0= ADVANCE / 1= STOP / 2= 測定不能。eco を渡すと個体(witness.eco)を照合する(IA-02)。"""
    try:
        w = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return 2, "WITNESS_UNREADABLE", None, f"witness 読取不能: {path}({e})— 測定不能は合格ではない"
    if not isinstance(w, dict):
        return 2, "WITNESS_MALFORMED", None, "witness 形状不正(object でない)— 測定不能は合格ではない"
    tree, _, err = worktree_tree(root)
    if tree is None:
        cause, detail = err
        return 2, "TREE_UNAVAILABLE", cause, f"現 tree を取得できない({detail or '詳細なし'})— 測定不能は合格ではない"
    if eco is not None and w.get("eco") != eco:
        return 1, "IDENTITY_MISMATCH", None, f"個体不一致(witness.eco={w.get('eco')} / 要求 {eco})— 別 job の receipt"
    wt = w.get("tree")
    if wt != tree:
        pos = _first_diff(wt, tree) if isinstance(wt, str) else "n/a(tree が文字列でない)"
        return 1, "TREE_MISMATCH", None, f"tree 不一致(witness {wt} / 現 {tree}・最初の差分位置 {pos})— 検査後の変更か未検査"
    gates = w.get("gates")
    if not isinstance(gates, list) or not gates:
        return 1, "GATES_MISSING", None, "gates 欠測(測定不能は合格ではない)"
    for g in gates:  # IA-01: 完全性(name・exit の型・source)を先に見る — 存在だけでは進めない
        prob = gate_problem(g)
        if prob:
            return 1, "GATE_INCOMPLETE", None, f"gate 不完全({prob})"
    bad = [g for g in gates if g["exit"] != 0]
    if bad:
        return 1, "GATE_FAIL", None, f"gate FAIL 混入({', '.join(g['name'] for g in bad)})"
    if w.get("stop_type") != "NONE":
        return 1, "STOP_TYPE", None, f"stop_type={w.get('stop_type')}"
    return 0, "OK", None, f"tree 一致({tree[:12]})・gates {len(gates)} 件 exit 0・stop NONE" + (f"・個体 {eco} 一致" if eco else "")


def verify(root: Path, path: Path, eco: str | None = None) -> tuple[int, str]:
    """(rc, 1 行目)— 1 行目は W6 の固定形式。"""
    rc, code, cause, msg = _verify(root, path, eco)
    return rc, report_line(rc, code, msg, cause)


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


def run_cli(argv: list, root: Path) -> tuple[int, str]:
    """CLI 本体(印字しない)— (rc, 出力 1 行目)。selftest が CLI 腕をここで回す(W7・ARG_ERROR)。"""
    if not argv:
        return 2, report_line(2, "ARG_ERROR", "usage: produce | verify | --selftest(冒頭コメント参照)")
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
            gates = parse_gates(argv)
            if "--inspection-from-ledger" in argv:   # ECO-074: 台帳から inspection gate を導出(申告でない)
                _, git_dir, err = worktree_tree(root)
                if git_dir is None:
                    cause, detail = err
                    return 2, report_line(2, "TREE_UNAVAILABLE", f"台帳の既定パスを導出できない({detail or '詳細なし'})", cause)
                gate, gerr = inspection_gate_from_ledger(root, git_dir / "bomdd-run" / f"{eco}.jsonl", eco, git_dir)
                if gate is None:
                    raise ArgError(f"--inspection-from-ledger: {gerr}")
                gates.append(gate)
            rc, msg, _ = produce(root, eco, gates, stop, out, producer)
            return rc, msg
        if cmd == "verify":
            path = out
            if path is None:
                consumed = {v for f in ("--eco", "--out", "--stop", "--producer", "--gate")
                            for v in ([_opt(argv, f)] if f != "--gate" else [])} - {None}
                pos = [a for a in argv[1:] if not a.startswith("--") and a not in consumed]
                if pos:
                    path = Path(pos[0])
                elif eco:
                    _, git_dir, err = worktree_tree(root)
                    if git_dir is None:
                        cause, detail = err
                        return 2, report_line(2, "TREE_UNAVAILABLE", f"既定パスを導出できない({detail or '詳細なし'})— 測定不能は合格ではない", cause)
                    path = default_path(git_dir, eco)
            if path is None:
                raise ArgError("verify: PATH か --eco が必要")
            if eco is None:  # W7: 個体未照合は合格ではない(Phase 5 R3 — 別 job の receipt を流用する失敗型)
                return 2, report_line(2, "IDENTITY_UNCHECKED", f"verify {path} には --eco ECO が必要(個体照合なしでは判定しない)")
            return verify(root, path, eco)
        raise ArgError(f"不明なコマンド: {cmd}")
    except ArgError as e:  # IA-05: 引数不正は traceback でなく exit 2(測定不能側)
        return 2, report_line(2, "ARG_ERROR", str(e))


# --- selftest: 一時 git リポで陽性対照(実リポの作業木に触れない) ---------------------------
class _FakeGit:
    """selftest 用: 特定サブコマンドを失敗させる(ADD_FAILED / WRITE_TREE_FAILED / GIT_DIR_FAILED の陽性対照)。"""
    def __init__(self, rc: int, stderr: str):
        self.returncode, self.stdout, self.stderr = rc, "", stderr


def _code_of(line: str) -> tuple[str, str | None]:
    """1 行目から (CODE, CAUSE) を取り出す(運転員が読むのと同じ経路で検査する)。"""
    head = line.split(":", 1)[0].split()
    if len(head) != 2:
        return "?", None
    code, _, rest = head[1].partition("(")
    return code, (rest.rstrip(")") or None)


def selftest() -> int:
    # ECO-068: selftest 自身の前提(OS temp・git)不在は traceback でなく UNMEASURABLE の 1 行・exit 2(selftest 失敗の 1 と区別)
    try:
        td_cm, wd_cm = tempfile.TemporaryDirectory(), tempfile.TemporaryDirectory()
    except OSError as e:
        print(report_line(2, "TREE_UNAVAILABLE", f"selftest の前提不在 — {e.__class__.__name__}: {str(e)[:120]}", "TEMP_UNAVAILABLE"))
        return 2
    return _selftest_body(td_cm, wd_cm)


def _selftest_body(td_cm, wd_cm) -> int:
    fails = []
    # witness の出力先は作業木の**外**(wd)— 作業木内に置くと自分が tree に入る(W5・初回 selftest が捕捉)
    with td_cm as td, wd_cm as wd:
        root = Path(td)
        wout = Path(wd)
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@x", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
        for cmd in (["init", "-q"], ["config", "core.autocrlf", "false"]):
            r0 = _git(root, *cmd, env=env)
            if r0.returncode != 0:
                if isinstance(r0, _GitUnavailable):  # ECO-068: git 不能は測定不能(exit 2)・selftest 失敗(exit 1)ではない
                    print(report_line(2, "TREE_UNAVAILABLE", "selftest の前提不在 — git を起動できない", "GIT_UNAVAILABLE"))
                    return 2
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

        def arm(name: str, w: dict | None, want: int, code: str | None = None, cause: str | None = None, contains: str | None = None):
            """W6: 終了コードだけでなく 1 行目の CODE(と CAUSE・文言)も期待どおりか — 運転員が読む経路を検査する。"""
            p = wout / f"{name}.json"
            if w is not None:
                p.write_text(json.dumps(w), encoding="utf-8")
            rc, line = verify(root, p)
            got_code, got_cause = _code_of(line)
            if rc != want:
                fails.append(f"{name}: exit {rc} != {want}({line})")
            if not line.startswith(VERDICTS[rc] + " "):
                fails.append(f"{name}: 1 行目が VERDICT で始まらない({line})")
            if code is not None and got_code != code:
                fails.append(f"{name}: CODE {got_code} != {code}({line})")
            if cause is not None and got_cause != cause:
                fails.append(f"{name}: CAUSE {got_cause} != {cause}({line})")
            if contains is not None and contains not in line:
                fails.append(f"{name}: 文言に {contains!r} がない({line})")
            if got_code not in CODES:
                fails.append(f"{name}: 語彙外の CODE {got_code}")
            return line

        arm("known-good", good, 0, "OK")
        arm("kb-hash", dict(good, tree=good["tree"][:-4] + ("0000" if good["tree"][-4:] != "0000" else "1111")), 1,
            "TREE_MISMATCH", contains="最初の差分位置 36")   # P5-03: 末尾改変でも位置と 40 桁が出る
        arm("kb-hash-head", dict(good, tree=("0" if good["tree"][0] != "0" else "1") + good["tree"][1:]), 1,
            "TREE_MISMATCH", contains="最初の差分位置 0")
        arm("kb-tree-type", dict(good, tree=None), 1, "TREE_MISMATCH", contains="n/a")
        arm("kb-fail", dict(good, gates=[{"name": "g", "exit": 1, "source": "x"}]), 1, "GATE_FAIL")
        arm("kb-missing", dict(good, gates=[]), 1, "GATES_MISSING")
        arm("kb-stop", dict(good, stop_type="NORMATIVE_RULING"), 1, "STOP_TYPE")
        arm("kb-absent", None, 2, "WITNESS_UNREADABLE")
        (wout / "kb-malformed.json").write_text("[]", encoding="utf-8")
        arm("kb-malformed", None, 2, "WITNESS_MALFORMED")
        # dirty 腕: 未追跡ファイルを置くと known-good でも STOP(HEAD^{tree} 比較なら素通りする腕)
        (root / "dirty.tmp").write_text("d\n", encoding="utf-8")
        head_tree = _git(root, "rev-parse", "HEAD^{tree}", env=env).stdout.strip()
        if head_tree != good["tree"]:
            fails.append("dirty 前提: clean 時は HEAD^{tree} == worktree tree のはず")
        arm("kb-dirty", good, 1, "TREE_MISMATCH")
        (root / "dirty.tmp").unlink()
        rc_bad_stop, msg_bad_stop, _ = produce(root, "ECO-900", [], "BOGUS", wout / "x.json", "selftest")
        if rc_bad_stop != 2:
            fails.append(f"produce: 不正 stop_type が exit {rc_bad_stop}")
        # --- r2 追加腕(独立検査 IA-01〜03・05 の陽性対照)---
        # IA-01: 構造不完全な gate(空名・bool exit・source なし)は存在しても ADVANCE しない
        arm("kb-structural", dict(good, gates=[{"name": "", "exit": False, "source": None}]), 1, "GATE_INCOMPLETE")
        arm("kb-bool-exit", dict(good, gates=[{"name": "g", "exit": False, "source": "x"}]), 1, "GATE_INCOMPLETE")
        arm("kb-no-source", dict(good, gates=[{"name": "g", "exit": 0}]), 1, "GATE_INCOMPLETE")
        rc_inc, _, _ = produce(root, "ECO-900", [{"name": "", "exit": 0, "source": "x"}], "NONE", wout / "inc.json", "selftest")
        if rc_inc != 2:
            fails.append(f"produce: 不完全 gate が exit {rc_inc}(2 で拒否すべき)")
        # IA-02: 個体照合 — 別 ECO の witness を --eco で受理しない / 一致なら 0
        p = wout / "eco.json"
        p.write_text(json.dumps(good), encoding="utf-8")
        rc_mis, line_mis = verify(root, p, eco="ECO-901")
        rc_hit, line_hit = verify(root, p, eco="ECO-900")
        if rc_mis != 1 or rc_hit != 0 or _code_of(line_mis)[0] != "IDENTITY_MISMATCH" or _code_of(line_hit)[0] != "OK":
            fails.append(f"kb-eco-mismatch: 不一致 exit {rc_mis}(1)/ 一致 exit {rc_hit}(0)/ {line_mis} / {line_hit}")
        # --- ECO-066: CLI 腕(W7 個体未照合・ARG_ERROR・既定パス)---
        rc_unc, line_unc = run_cli(["verify", str(p)], root)
        if rc_unc != 2 or _code_of(line_unc)[0] != "IDENTITY_UNCHECKED":
            fails.append(f"cli-unchecked: verify PATH 単独が exit {rc_unc} / {line_unc}(2 IDENTITY_UNCHECKED であるべき)")
        rc_cli_ok, line_cli_ok = run_cli(["verify", str(p), "--eco", "ECO-900"], root)
        if rc_cli_ok != 0 or _code_of(line_cli_ok)[0] != "OK":
            fails.append(f"cli-ok: verify PATH --eco が exit {rc_cli_ok} / {line_cli_ok}")
        rc_cli_def, line_cli_def = run_cli(["verify", "--eco", "ECO-900"], root)
        if rc_cli_def != 0 or _code_of(line_cli_def)[0] != "OK":
            fails.append(f"cli-default: verify --eco(既定パス)が exit {rc_cli_def} / {line_cli_def}")
        rc_cli_out, line_cli_out = run_cli(["verify", "--out", str(p)], root)
        if rc_cli_out != 2 or _code_of(line_cli_out)[0] != "IDENTITY_UNCHECKED":
            fails.append(f"cli-out-unchecked: verify --out PATH(--eco なし)が exit {rc_cli_out} / {line_cli_out}")
        for bad in ([], ["bogus"], ["verify"], ["verify", "--eco"], ["produce"], ["produce", "--eco", "E", "--gate", "x"]):
            rc_arg, line_arg = run_cli(bad, root)
            if rc_arg != 2 or _code_of(line_arg)[0] != "ARG_ERROR":
                fails.append(f"cli-arg {bad}: exit {rc_arg} / {line_arg}(2 ARG_ERROR であるべき)")
        # IA-03: git 実行不能は exit 2(traceback でない)— ECO-066: CAUSE= GIT_UNAVAILABLE
        saved = os.environ.get("PATH")
        try:
            os.environ["PATH"] = ""
            rc_nogit, line_nogit = verify(root, out)
            rc_nogit_p, msg_nogit_p, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE", wout / "ng.json", "selftest")
        finally:
            if saved is None:
                del os.environ["PATH"]
            else:
                os.environ["PATH"] = saved
        if rc_nogit != 2 or rc_nogit_p != 2 or _code_of(line_nogit) != ("TREE_UNAVAILABLE", "GIT_UNAVAILABLE") or _code_of(msg_nogit_p) != ("TREE_UNAVAILABLE", "GIT_UNAVAILABLE"):
            fails.append(f"kb-nogit: verify exit {rc_nogit} {line_nogit} / produce exit {rc_nogit_p} {msg_nogit_p}(2・GIT_UNAVAILABLE であるべき)")
        # IA-06(r2): OS temp 不能は exit 2(traceback でない)/ 変種: temp が作業木内へフォールバックしても 2 — ECO-066: CAUSE を区別
        saved_td = tempfile.tempdir
        try:
            tempfile.tempdir = str(root / "no-such-dir" / "x")
            rc_notmp, line_notmp = verify(root, out)
            rc_notmp_p, _, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE", wout / "nt.json", "selftest")
            tempfile.tempdir = str(root)   # 作業木内へのフォールバック相当
            rc_intmp, line_intmp = verify(root, out)
        finally:
            tempfile.tempdir = saved_td
        if rc_notmp != 2 or rc_notmp_p != 2 or rc_intmp != 2:
            fails.append(f"kb-notmp: verify {rc_notmp} / produce {rc_notmp_p} / 作業木内 temp {rc_intmp}(全て 2 であるべき)")
        if _code_of(line_notmp) != ("TREE_UNAVAILABLE", "TEMP_UNAVAILABLE"):
            fails.append(f"kb-notmp: CAUSE が TEMP_UNAVAILABLE でない({line_notmp})")
        if _code_of(line_intmp) != ("TREE_UNAVAILABLE", "TEMP_IN_WORKTREE"):
            fails.append(f"kb-intmp: CAUSE が TEMP_IN_WORKTREE でない({line_intmp})")
        if any(p.name.startswith("tmp") for p in root.iterdir()):
            fails.append("kb-notmp: 作業木に temp 残置")
        # ECO-066(P5-06): git サブコマンド失敗の CAUSE(ADD_FAILED / WRITE_TREE_FAILED / GIT_DIR_FAILED)— _git を差し替えて再現
        # r1 IA-03: 起動できた git/ラッパーの rc 127 は GIT_UNAVAILABLE ではない(rev-parse を rc 127 で失敗させる腕)
        real_git = globals()["_git"]
        for sub, want_cause, rc_fake in (("add", "ADD_FAILED", 128), ("write-tree", "WRITE_TREE_FAILED", 128),
                                         ("rev-parse", "GIT_DIR_FAILED", 128), ("rev-parse", "GIT_DIR_FAILED", 127)):
            def fake_git(root_, *args, env=None, _sub=sub, _rc=rc_fake):
                if args and args[0] == _sub:
                    return _FakeGit(_rc, f"fatal: simulated {_sub} failure rc={_rc}")
                return real_git(root_, *args, env=env)
            globals()["_git"] = fake_git
            try:
                rc_fk, line_fk = verify(root, out)
            finally:
                globals()["_git"] = real_git
            if rc_fk != 2 or _code_of(line_fk) != ("TREE_UNAVAILABLE", want_cause) or "simulated" not in line_fk:
                fails.append(f"kb-{sub}(rc {rc_fake}): exit {rc_fk} / {line_fk}(2・{want_cause}・stderr 末尾を含むべき)")
        # r1 IA-02: 既存 index の複製失敗(.git/index がディレクトリ)は INDEX_COPY_FAILED — 実 fixture(モックなし)
        with tempfile.TemporaryDirectory() as td2:
            r2 = Path(td2)
            if _git(r2, "init", "-q", env=env).returncode == 0:
                (r2 / ".git" / "index").mkdir()
                rc_ix, line_ix = verify(r2, out)
                if rc_ix != 2 or _code_of(line_ix) != ("TREE_UNAVAILABLE", "INDEX_COPY_FAILED"):
                    fails.append(f"kb-index-copy: exit {rc_ix} / {line_ix}(2・INDEX_COPY_FAILED であるべき)")
            else:
                fails.append("kb-index-copy: fixture の git init 不能")
        # r1 IA-04: 非 UTF-8 の stderr でも subprocess の読取が落ちず、末尾行が(置換つきで)残る — _RUN_KW を同じ経路で検査
        try:
            pr = subprocess.run([sys.executable, "-c", "import sys; sys.stderr.buffer.write(b'x\\n\\x81\\xff tail\\n'); sys.exit(3)"], **_RUN_KW)
            if pr.returncode != 3 or "tail" not in _tail(pr.stderr):
                fails.append(f"kb-stderr-bytes: rc {pr.returncode} / tail {_tail(pr.stderr)!r}(3・tail を含むべき)")
        except Exception as e:  # noqa: BLE001 — 落ちること自体が欠陥
            fails.append(f"kb-stderr-bytes: 例外 {e.__class__.__name__}: {e}")
        # r1 IA-01: produce / selftest の CLI 経路も固定形式(PRODUCED / ARG_ERROR / GATE_INCOMPLETE / WITNESS_UNWRITABLE / SELFTEST_FAIL)
        rc_pl, line_pl = run_cli(["produce", "--eco", "ECO-900", "--gate", "g=0:x", "--out", str(wout / "pl.json")], root)
        if rc_pl != 0 or _code_of(line_pl)[0] != "PRODUCED" or not line_pl.startswith("ADVANCE "):
            fails.append(f"cli-produce: exit {rc_pl} / {line_pl}(0 ADVANCE PRODUCED であるべき)")
        if _code_of(msg_bad_stop)[0] != "ARG_ERROR" or _code_of(msg_in)[0] != "ARG_ERROR":
            fails.append(f"cli-produce-arg: {msg_bad_stop} / {msg_in}(ARG_ERROR であるべき)")
        _, line_inc2, _ = produce(root, "ECO-900", [{"name": "", "exit": 0, "source": "x"}], "NONE", wout / "inc2.json", "selftest")
        _, line_unw2, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE", wout / "w.json" / "y.json", "selftest")
        if _code_of(line_inc2)[0] != "GATE_INCOMPLETE" or _code_of(line_unw2)[0] != "WITNESS_UNWRITABLE":
            fails.append(f"cli-produce-codes: {line_inc2} / {line_unw2}")
        if not _report_text(["x"]).startswith("STOP SELFTEST_FAIL: ") or not _report_text([]).startswith("ADVANCE OK: "):
            fails.append("selftest 自身の 1 行目が固定形式でない")
        for c in CODES:
            if _code_of(report_line(0, c, "m"))[0] != c:
                fails.append(f"report_line/_code_of の往復が {c} で崩れる")
        # IA-08(r3): Windows 拡張長パス(\\?\C:\...)で作業木内を外部と誤判定しない(W5)
        if os.name == "nt":
            ext = Path("\\\\?\\" + str((root / "ext.json").resolve()))
            rc_ext, _, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE", ext, "selftest")
            if rc_ext != 2 or (root / "ext.json").exists():
                fails.append(f"kb-extpath: 拡張長パスの作業木内出力が exit {rc_ext}(2 で拒否すべき)")
            ext_git = Path("\\\\?\\" + str((root / ".git" / "bomdd-witness" / "ext.json").resolve()))
            rc_ext_git, _, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE", ext_git, "selftest")
            if rc_ext_git != 0:
                fails.append(f"kb-extpath: 拡張長パスの .git 配下出力が exit {rc_ext_git}(0 であるべき)")
        # IA-08b(受理側追加): 書込不能パス(ファイルの下)は exit 2・traceback なし
        rc_unw, _, _ = produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE", wout / "w.json" / "x.json", "selftest")
        if rc_unw != 2:
            fails.append(f"kb-unwritable: 書込不能パスが exit {rc_unw}(2 であるべき)")
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
        # W6: 語彙の自己整合(report_line が語彙外を作らない・VERDICT と rc の対応)
        for rc_v, name_v in ((0, "ADVANCE"), (1, "STOP"), (2, "UNMEASURABLE")):
            if not report_line(rc_v, "OK", "m").startswith(name_v + " OK: "):
                fails.append(f"report_line: rc {rc_v} の VERDICT が {name_v} でない")
        if report_line(2, "TREE_UNAVAILABLE", "m", "ADD_FAILED") != "UNMEASURABLE TREE_UNAVAILABLE(ADD_FAILED): m":
            fails.append("report_line: CAUSE の形式が (CAUSE) でない")
        # --- ECO-074: inspection gate を台帳から導出(作業木を変えるので末尾で実施) ---
        ldir = root / ".git" / "bomdd-run"
        ldir.mkdir(parents=True, exist_ok=True)
        ledger = ldir / "ECO-900.jsonl"
        (root / "reports").mkdir(exist_ok=True)
        rep_p = root / "reports" / "r.md"
        rep_p.write_text("[INFORM / COMPLETE]\n\nACCEPT\n", encoding="utf-8")
        sha_ok = hashlib.sha256(rep_p.read_bytes()).hexdigest()

        def ledger_rows(verdict, rng, sha=sha_ok, path="reports/r.md", with_report=True):
            rows = [{"event": "decision", "run_id": "r0", "eco": "ECO-900", "decision": "ADVANCE"}]
            cell = {"event": "cell", "run_id": "r0", "eco": "ECO-900", "executor": "EQ-002", "cell_exit": 0}
            if with_report:
                cell["report"] = {"path": path, "exists": sha is not None, "size": 1, "sha256": sha, "verdict": verdict, "verdict_line": verdict, "range": rng}
            rows.append(cell)
            ledger.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

        def insp(name, want_rc, want_exit=None, contains=None):
            outp = wout / f"insp-{name}.json"
            rc_i, line_i = run_cli(["produce", "--eco", "ECO-900", "--out", str(outp), "--gate", "g=0:x", "--inspection-from-ledger"], root)
            if rc_i != want_rc:
                fails.append(f"insp-{name}: exit {rc_i} != {want_rc}({line_i})")
            if want_exit is not None and rc_i == 0:
                g = [x for x in json.loads(outp.read_text(encoding="utf-8"))["gates"] if x.get("name") == "inspection"]
                if len(g) != 1 or g[0].get("exit") != want_exit or g[0].get("source") != "reports/r.md" or g[0].get("executor") != "EQ-002":
                    fails.append(f"insp-{name}: gate 不正: {g}")
            if contains and contains not in line_i:
                fails.append(f"insp-{name}: 文言に {contains!r} がない({line_i})")

        ledger_rows("ACCEPT", "是正確認+回帰"); insp("accept-corrective", 0, 0)
        ledger_rows("ACCEPT", "境界探索"); insp("accept-boundary", 0, 2)
        ledger_rows("ACCEPT", None); insp("accept-norange", 0, 2)
        ledger_rows("REJECT", "是正確認+回帰"); insp("reject", 0, 1)
        ledger_rows("MISSING", "是正確認+回帰", sha=None); insp("missing", 0, 2)
        # r1 IA-01: 壊れた行は台帳不正 / IA-02: 行の eco 個体照合 / IA-03: path の境界 / IA-04: sha 欠落・形状(MISSING 以外)
        ledger_rows("ACCEPT", "是正確認+回帰")
        ledger.write_text(ledger.read_text(encoding="utf-8") + "{broken\n", encoding="utf-8"); insp("broken-line", 2, contains="壊れた行")
        ledger_rows("ACCEPT", "是正確認+回帰")
        ledger.write_text(ledger.read_text(encoding="utf-8").replace('"eco": "ECO-900"', '"eco": "ECO-999"'), encoding="utf-8"); insp("other-eco", 2, contains="個体が一致しない")
        ext = wout / "ext.md"; ext.write_text("ACCEPT\n", encoding="utf-8")
        ledger_rows("ACCEPT", "是正確認+回帰", sha=hashlib.sha256(ext.read_bytes()).hexdigest(), path=str(ext)); insp("path-absolute", 2, contains="リポ相対でない")
        ledger_rows("ACCEPT", "是正確認+回帰", path="reports/../r.md"); insp("path-dotdot", 2, contains="リポ相対でない")
        ledger_rows("ACCEPT", "是正確認+回帰", path=".git/r.md"); insp("path-gitdir", 2, contains=".git")
        ledger_rows("ACCEPT", "境界探索", sha=None); insp("sha-missing-boundary", 2, contains="sha256 がない")
        ledger_rows("UNPARSED", "是正確認+回帰", sha=None); insp("sha-missing-unparsed", 2, contains="sha256 がない")
        ledger_rows("ACCEPT", "是正確認+回帰", sha=sha_ok.upper()); insp("sha-upper", 2, contains="形状不正")
        ledger_rows("ACCEPT", "是正確認+回帰", sha=sha_ok[:12]); insp("sha-short", 2, contains="形状不正")
        ledger_rows("MISSING", "是正確認+回帰", sha=sha_ok); insp("missing-with-sha", 2, contains="形状不正")
        ledger_rows("UNPARSED", "是正確認+回帰"); insp("unparsed", 0, 2)
        ledger_rows("ACCEPT", "是正確認+回帰", sha="0" * 64); insp("sha-mismatch", 2, contains="一致しない")
        ledger_rows("ACCEPT", "是正確認+回帰", path="reports/none.md"); insp("report-absent", 2, contains="読めない")
        ledger_rows("ACCEPT", "是正確認+回帰", with_report=False); insp("no-cell-report", 2, contains="cell 行がない")
        ledger.unlink(); insp("ledger-absent", 2, contains="読めない")
        # 最後の report つき cell 行が採られる(先の REJECT より後の ACCEPT)
        rows = [json.dumps({"event": "cell", "run_id": "r1", "eco": "ECO-900", "executor": "EQ-002", "cell_exit": 0,
                            "report": {"path": "reports/r.md", "sha256": sha_ok, "verdict": "REJECT", "range": "境界探索"}}, ensure_ascii=False),
                json.dumps({"event": "cell", "run_id": "r2", "eco": "ECO-900", "executor": "EQ-002", "cell_exit": 0,
                            "report": {"path": "reports/r.md", "sha256": sha_ok, "verdict": "ACCEPT", "range": "是正確認+回帰"}}, ensure_ascii=False)]
        ledger.write_text("\n".join(rows) + "\n", encoding="utf-8"); insp("last-row", 0, 0)
    return _report(fails)


def _report_text(fails) -> str:
    """selftest の 1 行目も W6 の固定形式(r1 IA-01)。FAIL は STOP SELFTEST_FAIL(exit 1)。"""
    if fails:
        return report_line(1, "SELFTEST_FAIL", f"{len(fails)} 件\n  " + "\n  ".join(fails))
    return report_line(0, "OK", "selftest PASS(known-good / hash・fail・missing・stop・dirty・不完全 gate・個体不一致 1〔CODE 別〕/ 不在・形状不正・"
                       "git 不能・temp 不能・index 複製失敗・作業木内 temp・add/write-tree/git-dir 失敗〔rc 128・127〕2〔CAUSE 別〕/ CLI: PATH 単独= "
                       "IDENTITY_UNCHECKED 2・--eco 付き 0・既定パス 0・引数不正 ARG_ERROR 2・produce= PRODUCED 0/ARG_ERROR/GATE_INCOMPLETE/WITNESS_UNWRITABLE 2 / "
                       "非 UTF-8 stderr で落ちない / 作業木内出力 2 / 拡張長パス 2/.git 配下 0 / 差分位置 36・0 / inspection-from-ledger〔ECO-074〕: ACCEPT+是正確認→0・境界探索/range なし/MISSING/UNPARSED→2・REJECT→1・sha 不一致/報告不在/cell 行なし/台帳不在= ARG_ERROR・最後の行 / r1: 壊れた行・別 ECO 行・絶対/../.git path・sha 欠落/大文字/短縮・MISSING に sha= ARG_ERROR)")


def _report(fails) -> int:
    print(_report_text(fails))
    return 1 if fails else 0


def main(argv) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", newline="\n")
    if "--selftest" in argv:
        return selftest()
    rc, line = run_cli(argv, Path.cwd())
    print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
