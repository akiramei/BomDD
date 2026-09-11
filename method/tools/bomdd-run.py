# bomdd-run — 狭い自動起動の単一入口(ECO-067・Phase 6 第 1 弾)
#
# 目的: 運転員が手で回していた「job ビュー → receipt 再検証 → 台帳 → 次工程」を 1 入口にし、
# receipt の再検証が ADVANCE のときだけ製造セルを起動する。慎重さでなく機構(ECO-062 §1-3)。
# 由来: Phase 5 run-01/02(ECO-062 §10・§10.6)— 判断依存の STOP は ECO-066 で 0 になったが、台帳は人間の
# 手書きで規格が守られず(P5-09/10)、40 桁 ×2 の 1 行目は端末で折り返した(P5-08)。
#
# 仕様(v0 で凍結・ECO-067 §1・r1 IA-01〜04 で R2/R4/R7/R8 を強化):
#  R1 job ビューは bomdd-job.py を in-process で呼んで得る(転写しない)。job.stop_type != NONE なら起動しない。
#  R2 receipt のパスは ECO から機械導出(bomdd-witness の既定パス .git/bomdd-witness/<ECO>.json)。任意パス不可
#     — 運転員が job と receipt を手で束ねる穴(run-01 R3)を入口が持たない。ECO は ID 構文(ECO-NNN / CAPA-NNN・
#     英数とハイフンのみ)で検証し、導出したパスが所定ディレクトリの外へ出ないことも確認する(r1 IA-01)。
#  R3 検証は bomdd-witness.verify(root, path, eco) を in-process で呼ぶ(個体照合つき)。起動条件は
#     verifier_exit == 0 AND 1 行目が "ADVANCE OK:" で始まる AND job.stop_type == NONE の 3 条件 AND。
#  R4 run 台帳は運転員所有・非正本・追記のみ・作業木外(.git/bomdd-run/<ECO>.jsonl)。人間の手書き欄なし。
#     作業木内の台帳は自己参照(W5 と同型)なので exit 2 で拒否する。**判定レコードは起動の前に書く** — 台帳へ
#     書けないなら起動しない(r1 IA-02)。起動後は cell の終了を 2 行目のレコードとして追記する(event= cell)。
#  R5 --cell CMD は 3 条件が成立したときだけ、そのまま(引数を加工せず)プラットフォームのシェルで起動する。
#     承認は起動先のハーネスに委ねる(本ツールは迂回フラグを持たない)。--cell なしは dry(検証+台帳のみ)。
#     起動先には環境変数 BOMDD_JOB(ECO)・BOMDD_JOB_JSON(job ビューの一時ファイル)・BOMDD_WITNESS(receipt パス)を渡す。
#  R6 停止種別 → 配送先の固定表(DELIVERY・機械定義の初版)。witness 側の CODE も配送先を持つ(下記)。
#  R7 本ツール**自身が出す**行は全行 80 桁以内。**判定行は起動の前に出す**(1 行目= decision・r1 IA-03)。cell の出力は
#     その後に続き(起動先の出力であり本ツールは加工しない— R5「そのまま」と承認プロンプトの通過のため・r2 IA-04)、
#     cell 終了後に `cell exit N` の 1 行を出す。40 桁 ×2 は台帳の verifier_line にだけ残す。長いパスは中央省略(…)する。
#  R8 終了コード: 0= 起動した(dry なら ADVANCE)/ 1= STOP(起動せず)/ 2= 測定不能(起動せず)。未知オプションは
#     ARG_ERROR(exit 2・無視しない)。
#
# 使い方:
#   python bomdd-run.py ECO-067                      # dry: 検証+台帳
#   python bomdd-run.py ECO-067 --cell "codex exec ..."   # ADVANCE のときだけ起動
#   python bomdd-run.py ECO-067 --ledger PATH         # 台帳の場所(作業木外のみ)
#   python bomdd-run.py --selftest                    # known-good 1 腕は起動し known-bad 腕は起動しない(痕跡で判定)
#
# 検出力の限界(宣言):
#   (1) 起動先が何をするかは責務外(製造セルの契約)。台帳に残すのは起動した事実と終了コードのみ。
#   (2) receipt の申告値(gates.exit)は再実測しない(bomdd-witness W2 と同じ)。
#   (3) 承認の有無は起動先ハーネスの設定に依存する — 本ツールは承認を作らない・迂回もしない。

import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
ECO_RE = re.compile(r"^(ECO|CAPA)-[A-Za-z0-9]+(-[A-Za-z0-9]+)*$")   # r1 IA-01: 区切り文字・親参照を含まない
WIDTH = 80
KNOWN_OPTS = ("--cell", "--ledger")

# R6: 停止種別 → 配送先(ECO-062 §0.5 の 6 種+F0+MISSING_INPUT)。job の停止語彙(bomdd-job.py F5)と 1 対 1。
DELIVERY = {
    "NONE": "next",
    "NORMATIVE_RULING": "human",
    "CONVERGENCE_LIMIT": "human",
    "VERIFICATION_FAIL": "factory",
    "BOM_CONTRADICTION": "designer",
    "PREFLIGHT_HOLD": "process",
    "LEDGER_INCONSISTENT": "ledger-owner",
    "MISSING_INPUT": "operator",
}
# witness 側の CODE(bomdd-witness W6)→ 配送先。receipt 自体の欠陥は運転員へ・検査赤は工場へ・stop_type は表へ。
WITNESS_DELIVERY = {
    "OK": "next",
    "GATE_FAIL": "factory",
    "STOP_TYPE": "human",   # 既定。実際は receipt の stop_type を DELIVERY で引く(decide 参照)
    "IDENTITY_MISMATCH": "operator", "IDENTITY_UNCHECKED": "operator", "TREE_MISMATCH": "operator",
    "GATES_MISSING": "operator", "GATE_INCOMPLETE": "operator",
    "WITNESS_UNREADABLE": "operator", "WITNESS_MALFORMED": "operator", "TREE_UNAVAILABLE": "operator",
    "ARG_ERROR": "operator", "PRODUCED": "operator", "WITNESS_UNWRITABLE": "operator", "SELFTEST_FAIL": "operator",
}


def _load(name: str):
    """同ディレクトリの bomdd-job.py / bomdd-witness.py を in-process で import する(ハイフン名のため spec 経由)。"""
    path = TOOLS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _code_of(line: str) -> tuple[str, str | None]:
    head = line.split(":", 1)[0].split()
    if len(head) != 2:
        return "?", None
    code, _, rest = head[1].partition("(")
    return code, (rest.rstrip(")") or None)


def _job_value(job: dict, key: str):
    f = job.get(key)
    return f.get("value") if isinstance(f, dict) else None


def _fit(s: str, width: int = WIDTH) -> str:
    """R7: 80 桁に収める(中央省略)。"""
    if len(s) <= width:
        return s
    keep = width - 1
    return s[: keep // 2] + "…" + s[-(keep - keep // 2):]


def _short_path(p, keep: int = 28) -> str:
    s = str(p)
    return s if len(s) <= keep else "…" + s[-(keep - 1):]


def _under(path: Path, parent: Path) -> bool:
    """path が parent 配下(解決後)か。解決不能は False(安全側)。"""
    try:
        return os.path.commonpath([path.resolve(), parent.resolve()]) == str(parent.resolve())
    except (OSError, ValueError):
        return False


def decide(root: Path, eco: str, jobmod, witmod) -> tuple[dict, dict | None]:
    """R1〜R3・R6: 判定レコード(台帳 1 行目の元)。起動はしない。"""
    rec = {"event": "decision", "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"), "eco": eco,
           "receipt": None, "job_state": None, "job_stop_type": None, "verifier_line": None, "verifier_exit": None,
           "code": None, "decision": None, "stop_type": None, "delivery": None, "cell": None, "tree": None}
    jobs, _ = jobmod.select([eco], root)
    job = next((j for j in jobs if _job_value(j, "eco") == eco), None) or (jobs[0] if jobs else None)
    if job is None:
        rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery=DELIVERY["MISSING_INPUT"])
        return rec, job
    rec["job_state"] = _job_value(job, "state")
    jstop = _job_value(job, "stop_type") or "MISSING_INPUT"
    rec["job_stop_type"] = jstop
    if rec["job_state"] is None:  # register に無い / 読めない → 測定不能
        rec.update(decision="UNMEASURABLE", stop_type=jstop, delivery=DELIVERY.get(jstop, "operator"))
        return rec, job
    # R2: receipt パスは ECO から機械導出し、所定ディレクトリ配下であることを確認(r1 IA-01)
    tree, git_dir, err = witmod.worktree_tree(root)
    if git_dir is None:
        cause, detail = err
        rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery="operator",
                   verifier_line=witmod.report_line(2, "TREE_UNAVAILABLE", detail or "詳細なし", cause), verifier_exit=2, code="TREE_UNAVAILABLE")
        return rec, job
    rec["tree"] = tree
    path = witmod.default_path(git_dir, eco)
    if not _under(path, git_dir / "bomdd-witness"):
        rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery="operator", code="ARG_ERROR",
                   verifier_line=witmod.report_line(2, "ARG_ERROR", "receipt パスが所定ディレクトリの外へ出る"), verifier_exit=2)
        return rec, job
    rec["receipt"] = str(path)
    rc, line = witmod.verify(root, path, eco)   # R3: 個体照合つき
    rec["verifier_line"], rec["verifier_exit"] = line, rc
    code, _cause = _code_of(line)
    rec["code"] = code   # receipt 側の理由(witness CODE)。stop_type は job 語彙(F5)で、receipt 欠陥は VERIFICATION_FAIL に写す
    if jstop != "NONE":  # R1: job の停止が先(receipt が有効でも起動しない)
        rec.update(decision="STOP", stop_type=jstop, delivery=DELIVERY.get(jstop, "operator"))
        return rec, job
    if rc == 2:
        rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery=WITNESS_DELIVERY.get(code, "operator"))
        return rec, job
    if rc == 1 or not line.startswith("ADVANCE OK:"):
        wstop = None
        if code == "STOP_TYPE":
            try:
                wstop = json.loads(path.read_text(encoding="utf-8")).get("stop_type")
            except (OSError, ValueError):
                wstop = None
        if isinstance(wstop, str) and wstop in DELIVERY:
            rec.update(decision="STOP", stop_type=wstop, delivery=DELIVERY[wstop])
        else:
            rec.update(decision="STOP", stop_type="VERIFICATION_FAIL", delivery=WITNESS_DELIVERY.get(code, "operator"))
        return rec, job
    rec.update(decision="ADVANCE", stop_type="NONE", delivery="next")
    return rec, job


def launch(rec: dict, job: dict, cell: str, root: Path) -> dict:
    """R5: 3 条件成立時のみ呼ばれる。コマンドはそのまま・環境で job/witness を渡す・承認は起動先。台帳 2 行目のレコードを返す。"""
    with tempfile.NamedTemporaryFile("w", suffix=".json", prefix="bomdd-job-", delete=False, encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
        job_json = f.name
    env = dict(os.environ, BOMDD_JOB=rec["eco"], BOMDD_JOB_JSON=job_json, BOMDD_WITNESS=rec["receipt"])
    ev = {"event": "cell", "run_id": rec["run_id"], "eco": rec["eco"], "cell": cell,
          "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "cell_exit": None}
    try:
        sys.stdout.flush()
        r = subprocess.run(cell, shell=True, cwd=str(root), env=env)
        ev["cell_exit"] = r.returncode
    except OSError as e:
        ev["cell_exit"] = f"OSError: {e.__class__.__name__}"
    finally:
        try:
            os.unlink(job_json)
        except OSError:
            pass
    return ev


def write_ledger(path: Path, rec: dict) -> str | None:
    """R4: 追記のみ。失敗は理由文字列(exit 2 側)。"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return None
    except OSError as e:
        return f"台帳を書けない({e.__class__.__name__}): {_short_path(path)}"


def summary_line(rec: dict, launching: bool) -> str:
    """R7: 判定行(80 桁以内)。起動する場合は「launching」— cell の終了は後続行。"""
    code, cause = _code_of(rec["verifier_line"] or "")
    tag = code if code != "?" else "-"
    if code == "STOP_TYPE" and rec["stop_type"]:
        tag = f"STOP_TYPE({rec['stop_type']})"
    elif cause:
        tag = f"{code}({cause})"
    if rec["job_stop_type"] and rec["job_stop_type"] != "NONE" and rec["decision"] != "ADVANCE":
        tag = f"job:{rec['job_stop_type']}"
    tree = (rec["tree"] or "")[:12] or "-"
    if rec["decision"] != "ADVANCE":   # 起動できるのは ADVANCE だけなので「未起動」は書かない
        return _fit(f"{rec['decision']} {rec['eco']} {tag} → {rec['delivery']} @{tree}")
    return _fit(f"{rec['decision']} {rec['eco']} {tag} → {rec['delivery']} · {'launching' if launching else 'dry'} @{tree}")


def _opt(argv: list, flag: str):
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
        return ""
    return argv[i + 1]


def run(argv: list, root: Path, emit=None) -> int:
    """入口本体。emit(line) で標準出力の各行を出す(1 行目= 判定行・R7)。返り値= 終了コード(R8)。"""
    emit = emit or (lambda s: None)
    if not argv or argv[0].startswith("--"):
        emit("UNMEASURABLE ARG_ERROR: usage: ECO-NNN [--cell CMD] [--ledger PATH] | --selftest")
        return 2
    eco = argv[0]
    if not ECO_RE.match(eco):   # r1 IA-01
        emit(_fit(f"UNMEASURABLE ARG_ERROR: ECO の構文不正(ECO-NNN / CAPA-NNN): {eco!r}"))
        return 2
    # r2 IA-01: 位置で逐次パースする(値集合で「消費済み」と見なすと、オプション値と同じ文字列の余分引数が素通りする)
    opts, unknown, stray, i = {}, [], [], 1
    while i < len(argv):
        a = argv[i]
        if a in KNOWN_OPTS:
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                emit(f"UNMEASURABLE ARG_ERROR: {a} に値がない")
                return 2
            if a in opts:
                emit(f"UNMEASURABLE ARG_ERROR: {a} が重複")
                return 2
            opts[a] = argv[i + 1]
            i += 2
            continue
        (unknown if a.startswith("--") else stray).append(a)
        i += 1
    if unknown or stray:   # r1 IA-01 補足: 未知オプション・余分な引数を無視しない
        emit(_fit(f"UNMEASURABLE ARG_ERROR: 未知の引数: {' '.join(unknown + stray)}"))
        return 2
    cell = opts.get("--cell")
    ledger_s = opts.get("--ledger")
    jobmod, witmod = _load("bomdd-job"), _load("bomdd-witness")
    rec, job = decide(root, eco, jobmod, witmod)
    _, git_dir, _ = witmod.worktree_tree(root)
    if ledger_s:
        ledger = Path(ledger_s)
    elif git_dir is not None:
        ledger = git_dir / "bomdd-run" / f"{eco}.jsonl"
        if not _under(ledger, git_dir / "bomdd-run"):
            emit("UNMEASURABLE ARG_ERROR: 台帳パスが所定ディレクトリの外へ出る")
            return 2
    else:
        emit("UNMEASURABLE TREE_UNAVAILABLE: 台帳の既定パスを導出できない(git 不能)")
        return 2
    if witmod._inside_worktree(ledger, root, git_dir):  # R4: 自己参照の拒否
        emit(_fit(f"UNMEASURABLE ARG_ERROR: 台帳を作業木内に置けない(自己参照): {_short_path(ledger)}"))
        return 2
    launching = rec["decision"] == "ADVANCE" and bool(cell)
    if launching:
        rec["cell"] = cell
    err = write_ledger(ledger, rec)   # R4/r1 IA-02: 判定レコードを起動の前に書く。書けなければ起動しない
    if err:
        emit(_fit("UNMEASURABLE ARG_ERROR: " + err))
        return 2
    emit(summary_line(rec, launching))   # R7/r1 IA-03: 判定行を起動の前に出す
    if launching:
        ev = launch(rec, job, cell, root)   # R5
        err2 = write_ledger(ledger, ev)
        emit(_fit(f"cell exit {ev['cell_exit']}" + (f" · 台帳追記失敗: {err2}" if err2 else "")))
        return 0
    return {"ADVANCE": 0, "STOP": 1, "UNMEASURABLE": 2}[rec["decision"]]


# --- selftest: 一時 git リポ(実リポ非接触)で known-good は起動し known-bad は起動しない ---------------------
def selftest() -> int:
    fails = []
    witmod = _load("bomdd-witness")
    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as wd:
        root, wout = Path(td), Path(wd)
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@x", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
        for cmd in (["init", "-q"], ["config", "core.autocrlf", "false"]):
            if witmod._git(root, *cmd, env=env).returncode != 0:
                return _report(["fixture: git init 不能"])
        (root / "bomdd").mkdir()
        (root / "bomdd" / "open.md").write_text("# Change Order — ECO-900\n\n## 3. 受入\n- 検討中\n", encoding="utf-8")
        (root / "bomdd" / "closed.md").write_text("# Change Order — ECO-902\n\n## 6. クローズ(2026-09-03・verified)\n- PASS\n", encoding="utf-8")
        reg = root / "bomdd" / "60-change-register.yaml"
        reg.write_text("changes:\n"
                       "  - {id: ECO-900, title: t, status: decided, order_ref: bomdd/open.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
                       "  - {id: ECO-902, title: t2, status: in-progress, order_ref: bomdd/closed.md}\n"
                       "  - {id: 'ECO-/../../../x', title: t3, status: decided, order_ref: bomdd/open.md}\n", encoding="utf-8")
        witmod._git(root, "add", "-A", env=env)
        if witmod._git(root, "commit", "-q", "-m", "init", env=env).returncode != 0:
            return _report(["fixture: commit 不能"])
        git_dir = root / ".git"
        wpath = witmod.default_path(git_dir, "ECO-900")
        rc, msg, _ = witmod.produce(root, "ECO-900", [{"name": "g", "exit": 0, "source": "x"}], "NONE", wpath, "selftest")
        if rc != 0:
            return _report([f"fixture produce: {msg}"])
        good = json.loads(wpath.read_text(encoding="utf-8"))
        marker = wout / "launched.txt"
        cell = f'"{sys.executable}" -c "import pathlib,os; pathlib.Path(r\'{marker}\').write_text(os.environ.get(\'BOMDD_JOB\',\'\')+\'|\'+os.environ.get(\'BOMDD_WITNESS\',\'\'))"'
        ledger = wout / "ledger.jsonl"

        def call(argv):
            out = []
            rc = run(argv, root, out.append)
            for ln in out:
                if len(ln) > WIDTH:
                    fails.append(f"{argv[:1]}: 行が {WIDTH} 桁超({len(ln)}): {ln}")
            return rc, out

        def last_rec():
            return json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1]) if ledger.exists() else {}

        def arm(name, w, want_rc, want_dec, want_delivery, launched, eco="ECO-900", use_cell=True):
            if marker.exists():
                marker.unlink()
            if w is None:
                if wpath.exists():
                    wpath.unlink()
            else:
                wpath.write_text(json.dumps(w), encoding="utf-8")
            rc, out = call([eco, "--ledger", str(ledger)] + (["--cell", cell] if use_cell else []))
            recs = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines()] if ledger.exists() else []
            dec = next((r for r in reversed(recs) if r.get("event") == "decision"), {})
            if rc != want_rc or dec.get("decision") != want_dec:
                fails.append(f"{name}: exit {rc} / decision {dec.get('decision')}(期待 {want_rc}/{want_dec}) :: {out[:1]}")
            if dec.get("delivery") != want_delivery:
                fails.append(f"{name}: delivery {dec.get('delivery')} != {want_delivery}")
            if marker.exists() != launched:
                fails.append(f"{name}: 起動痕跡 {marker.exists()}(期待 {launched})— fail-open の入口版" if marker.exists() else f"{name}: 起動されなかった(期待 起動)")
            if not out or not out[0].startswith(want_dec + " "):
                fails.append(f"{name}: 1 行目が decision で始まらない: {out[:1]}")
            return dec, out

        dec_good, out_good = arm("known-good", good, 0, "ADVANCE", "next", True)
        if marker.exists() and marker.read_text(encoding="utf-8") != f"ECO-900|{wpath}":
            fails.append(f"known-good: 起動先が受け取った環境が不正: {marker.read_text(encoding='utf-8')}")
        ev = last_rec()
        if ev.get("event") != "cell" or ev.get("cell_exit") != 0 or dec_good.get("cell") != cell or "launching" not in out_good[0]:
            fails.append(f"known-good: 台帳 2 行目 {ev.get('event')}/{ev.get('cell_exit')} / 判定行 {out_good[:1]}")
        if len(out_good) != 2 or not out_good[1].startswith("cell exit 0"):
            fails.append(f"known-good: 出力が 判定行+cell exit 行 でない: {out_good}")
        arm("dry", good, 0, "ADVANCE", "next", False, use_cell=False)
        arm("kb-tree", dict(good, tree=good["tree"][:-4] + ("0000" if good["tree"][-4:] != "0000" else "1111")), 1, "STOP", "operator", False)
        arm("kb-other-job", dict(good, eco="ECO-901"), 1, "STOP", "operator", False)
        arm("kb-fail", dict(good, gates=[{"name": "g", "exit": 1, "source": "x"}]), 1, "STOP", "factory", False)
        arm("kb-missing", dict(good, gates=[]), 1, "STOP", "operator", False)
        arm("kb-stop", dict(good, stop_type="NORMATIVE_RULING"), 1, "STOP", "human", False)
        w902 = dict(good, witness="WIT-ECO-902", eco="ECO-902")
        witmod.default_path(git_dir, "ECO-902").write_text(json.dumps(w902), encoding="utf-8")
        if marker.exists():
            marker.unlink()
        rc902, out902 = call(["ECO-902", "--ledger", str(ledger), "--cell", cell])
        dec902 = last_rec()
        if rc902 != 1 or dec902.get("decision") != "STOP" or dec902.get("delivery") != "ledger-owner" or marker.exists():
            fails.append(f"kb-job-stop: exit {rc902} / {dec902.get('decision')} / {dec902.get('delivery')} / 起動 {marker.exists()} :: {out902[:1]}")
        arm("kb-absent", None, 2, "UNMEASURABLE", "operator", False)
        arm("kb-no-eco", good, 2, "UNMEASURABLE", "operator", False, eco="ECO-999")
        # r1 IA-01: ECO の構文(区切り・親参照)は ARG_ERROR・起動しない・台帳も書かない
        wpath.write_text(json.dumps(good), encoding="utf-8")
        if marker.exists():
            marker.unlink()
        n_before = len(ledger.read_text(encoding="utf-8").splitlines())
        for bad_eco in ("ECO-/../../../x", "ECO-900/../x", "..", "ECO-900 x", "ECO_900"):
            rc_t, out_t = call([bad_eco, "--ledger", str(ledger), "--cell", cell])
            if rc_t != 2 or not out_t or not out_t[0].startswith("UNMEASURABLE ARG_ERROR") or marker.exists():
                fails.append(f"kb-eco-syntax {bad_eco!r}: exit {rc_t} / 起動 {marker.exists()} :: {out_t[:1]}")
        if len(ledger.read_text(encoding="utf-8").splitlines()) != n_before:
            fails.append("kb-eco-syntax: 不正 ECO で台帳に書いた")
        # r1 IA-02: 台帳に書けない(ディレクトリ)→ 起動しない・exit 2
        bad_ledger = wout / "ledger-as-dir"
        bad_ledger.mkdir()
        if marker.exists():
            marker.unlink()
        rc_bl, out_bl = call(["ECO-900", "--ledger", str(bad_ledger), "--cell", cell])
        if rc_bl != 2 or marker.exists() or not out_bl[0].startswith("UNMEASURABLE"):
            fails.append(f"kb-ledger-unwritable: exit {rc_bl} / 起動 {marker.exists()} :: {out_bl[:1]}(起動してはならない)")
        # 台帳を作業木内に置く → 拒否(自己参照)・起動しない
        if marker.exists():
            marker.unlink()
        rc_in, out_in = call(["ECO-900", "--ledger", str(root / "ledger.jsonl"), "--cell", cell])
        if rc_in != 2 or (root / "ledger.jsonl").exists() or marker.exists():
            fails.append(f"kb-ledger-inside: exit {rc_in} / 存在 {(root / 'ledger.jsonl').exists()} / 起動 {marker.exists()} :: {out_in[:1]}")
        # 引数不正・未知オプション(r1 IA-01 補足)— 全て ARG_ERROR・起動しない
        # r2 IA-01: オプション値と同じ文字列の余分な位置引数・オプションの重複も ARG_ERROR
        for bad in ([], ["--cell", "x"], ["ECO-900", "--cell"], ["ECO-900", "--ledger"], ["ECO-900", "--receipt", "x"], ["ECO-900", "extra"],
                    ["ECO-900", "--ledger", str(ledger), "--bogus"], ["ECO-900", "--ledger", str(ledger), "--cell", cell, cell],
                    ["ECO-900", "--ledger", str(ledger), str(ledger)], ["ECO-900", "--ledger", str(ledger), "--ledger", str(ledger)]):
            if marker.exists():
                marker.unlink()
            rc_b, out_b = call(bad)
            if rc_b != 2 or not out_b or not out_b[0].startswith("UNMEASURABLE ARG_ERROR") or marker.exists():
                fails.append(f"arg {bad}: exit {rc_b} :: {out_b[:1]}")
        # 台帳の形(全レコードに event・decision 行に verifier_line と decision)
        recs = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines()]
        decs = [r for r in recs if r.get("event") == "decision"]
        if len(decs) < 10 or any("verifier_line" not in r or "decision" not in r for r in decs) or any("event" not in r for r in recs):
            fails.append(f"ledger: decision 行 {len(decs)} / 形不正")
        # 配送先表の自己整合(job 語彙と 1 対 1)
        jobmod = _load("bomdd-job")
        vocab = set(getattr(jobmod, "STOP_VOCABULARY", ()) or ())
        if vocab and set(DELIVERY) != vocab:
            fails.append(f"DELIVERY と job の停止語彙が一致しない: {sorted(set(DELIVERY) ^ vocab)}")
        if set(WITNESS_DELIVERY) != set(witmod.CODES):
            fails.append(f"WITNESS_DELIVERY と witness の CODES が一致しない: {sorted(set(WITNESS_DELIVERY) ^ set(witmod.CODES))}")
        # r1 IA-04: selftest 自身の報告行も 80 桁以内
        for txt in (_report_text([]), _report_text(["x"])):
            if len(txt.splitlines()[0]) > WIDTH:
                fails.append(f"selftest 報告行が {WIDTH} 桁超: {txt.splitlines()[0]}")
    return _report(fails)


def _report_text(fails) -> str:
    if fails:
        return f"STOP SELFTEST_FAIL: {len(fails)} 件\n  " + "\n  ".join(fails)
    return "ADVANCE OK: selftest PASS(起動1/dry/kb5/job停止/測定不能2/構文5/台帳3/引数10/80桁/表)"


def _report(fails) -> int:
    print(_report_text(fails))
    return 1 if fails else 0


def main(argv) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", newline="\n", line_buffering=True)
    if "--selftest" in argv:
        return selftest()
    return run(argv, Path.cwd(), print)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
