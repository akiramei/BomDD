# bomdd-run — 狭い自動起動の単一入口(ECO-067・Phase 6 第 1 弾)
#
# 目的: 運転員が手で回していた「job ビュー → receipt 再検証 → 台帳 → 次工程」を 1 入口にし、
# receipt の再検証が ADVANCE のときだけ製造セルを起動する。慎重さでなく機構(ECO-062 §1-3)。
# 由来: Phase 5 run-01/02(ECO-062 §10・§10.6)— 判断依存の STOP は ECO-066 で 0 になったが、台帳は人間の
# 手書きで規格が守られず(P5-09/10)、40 桁 ×2 の 1 行目は端末で折り返した(P5-08)。
#
# 仕様(v0 で凍結・ECO-067 §1):
#  R1 job ビューは bomdd-job.py を in-process で呼んで得る(転写しない)。job.stop_type != NONE なら起動しない。
#  R2 receipt のパスは ECO から機械導出(bomdd-witness の既定パス .git/bomdd-witness/<ECO>.json)。任意パス不可
#     — 運転員が job と receipt を手で束ねる穴(run-01 R3)を入口が持たない。
#  R3 検証は bomdd-witness.verify(root, path, eco) を in-process で呼ぶ(個体照合つき)。起動条件は
#     verifier_exit == 0 AND 1 行目が "ADVANCE OK:" で始まる AND job.stop_type == NONE の 3 条件 AND。
#  R4 run 台帳は運転員所有・非正本・追記のみ・作業木外(.git/bomdd-run/<ECO>.jsonl)。人間の手書き欄なし。
#     作業木内の台帳は自己参照(W5 と同型)なので exit 2 で拒否する。
#  R5 --cell CMD は 3 条件が成立したときだけ、そのまま(引数を加工せず)プラットフォームのシェルで起動する。
#     承認は起動先のハーネスに委ねる(本ツールは迂回フラグを持たない)。--cell なしは dry(検証+台帳のみ)。
#     起動先には環境変数 BOMDD_JOB(ECO)・BOMDD_JOB_JSON(job ビューの一時ファイル)・BOMDD_WITNESS(receipt パス)を渡す。
#  R6 停止種別 → 配送先の固定表(DELIVERY・機械定義の初版)。witness 側の CODE も配送先を持つ(下記)。
#  R7 標準出力は短い 1 行(80 桁以内を目標・tree は 12 桁)。40 桁 ×2 は台帳の verifier_line にだけ残す。
#  R8 終了コード: 0= 起動した(dry なら ADVANCE)/ 1= STOP(起動せず)/ 2= 測定不能(起動せず)。
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
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent

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


def decide(root: Path, eco: str, jobmod, witmod) -> dict:
    """R1〜R3・R6: 判定レコード(台帳 1 行の元)。起動はしない。"""
    rec = {"run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"), "eco": eco, "receipt": None,
           "job_state": None, "job_stop_type": None, "verifier_line": None, "verifier_exit": None, "code": None,
           "decision": None, "stop_type": None, "delivery": None, "cell": None, "cell_exit": None,
           "started_at": None, "tree": None}
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
    # R2: receipt パスは ECO から機械導出
    tree, git_dir, err = witmod.worktree_tree(root)
    if git_dir is None:
        cause, detail = err
        rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery="operator",
                   verifier_line=witmod.report_line(2, "TREE_UNAVAILABLE", detail or "詳細なし", cause), verifier_exit=2)
        return rec, job
    rec["tree"] = tree
    path = witmod.default_path(git_dir, eco)
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
        # STOP_TYPE(receipt が停止種別を運ぶ)は表で配送・それ以外の CODE は witness 側の表
        wstop = None
        if code == "STOP_TYPE":
            try:
                wstop = json.loads(path.read_text(encoding="utf-8")).get("stop_type")
            except (OSError, ValueError):
                wstop = None
        stop = wstop if isinstance(wstop, str) and wstop in DELIVERY else "VERIFICATION_FAIL"
        rec.update(decision="STOP", stop_type=stop, delivery=DELIVERY[stop] if wstop else WITNESS_DELIVERY.get(code, "operator"))
        return rec, job
    rec.update(decision="ADVANCE", stop_type="NONE", delivery="next")
    return rec, job


def launch(rec: dict, job: dict, cell: str, root: Path) -> None:
    """R5: 3 条件成立時のみ呼ばれる。コマンドはそのまま・環境で job/witness を渡す・承認は起動先。"""
    with tempfile.NamedTemporaryFile("w", suffix=".json", prefix="bomdd-job-", delete=False, encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
        job_json = f.name
    env = dict(os.environ, BOMDD_JOB=rec["eco"], BOMDD_JOB_JSON=job_json, BOMDD_WITNESS=rec["receipt"])
    rec["cell"] = cell
    rec["started_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        r = subprocess.run(cell, shell=True, cwd=str(root), env=env)
        rec["cell_exit"] = r.returncode
    except OSError as e:
        rec["cell_exit"] = f"OSError: {e.__class__.__name__}"
    finally:
        try:
            os.unlink(job_json)
        except OSError:
            pass


def write_ledger(path: Path, rec: dict) -> str | None:
    """R4: 追記のみ。失敗は理由文字列(exit 2 側)。"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return None
    except OSError as e:
        return f"台帳を書けない: {path}({e.__class__.__name__})"


def summary_line(rec: dict) -> str:
    """R7: 短い 1 行(80 桁目標)。"""
    code, cause = _code_of(rec["verifier_line"] or "")
    tag = code if code != "?" else "-"
    if code == "STOP_TYPE" and rec["stop_type"]:
        tag = f"STOP_TYPE({rec['stop_type']})"
    elif cause:
        tag = f"{code}({cause})"
    if rec["job_stop_type"] and rec["job_stop_type"] != "NONE" and rec["decision"] != "ADVANCE":
        tag = f"job:{rec['job_stop_type']}"
    tree = (rec["tree"] or "")[:12] or "-"
    if rec["decision"] != "ADVANCE":   # 起動できるのは ADVANCE だけなので「未起動」は書かない(80 桁以内・R7)
        return f"{rec['decision']} {rec['eco']} {tag} → {rec['delivery']} @{tree}"
    cell = "dry" if rec["cell"] is None else f"launched(exit {rec['cell_exit']})"
    return f"{rec['decision']} {rec['eco']} {tag} → {rec['delivery']} · {cell} @{tree}"


def run(argv: list, root: Path) -> tuple[int, str]:
    if not argv or argv[0].startswith("--"):
        return 2, "UNMEASURABLE ARG_ERROR: usage: bomdd-run.py ECO-NNN [--cell CMD] [--ledger PATH] | --selftest"
    eco = argv[0]
    cell = _opt(argv, "--cell")
    ledger_s = _opt(argv, "--ledger")
    if cell == "" or ledger_s == "":
        return 2, "UNMEASURABLE ARG_ERROR: --cell / --ledger に値がない"
    jobmod, witmod = _load("bomdd-job"), _load("bomdd-witness")
    rec, job = decide(root, eco, jobmod, witmod)
    _, git_dir, _ = witmod.worktree_tree(root)
    ledger = Path(ledger_s) if ledger_s else (git_dir / "bomdd-run" / f"{eco}.jsonl" if git_dir else None)
    if ledger is None:
        return 2, "UNMEASURABLE TREE_UNAVAILABLE: 台帳の既定パスを導出できない(git 不能)"
    if witmod._inside_worktree(ledger, root, git_dir):  # R4: 自己参照の拒否
        return 2, f"UNMEASURABLE ARG_ERROR: 台帳を作業木内に置けない(自己参照): {ledger}"
    if rec["decision"] == "ADVANCE" and cell:
        launch(rec, job, cell, root)   # R5
    err = write_ledger(ledger, rec)
    if err:
        return 2, "UNMEASURABLE ARG_ERROR: " + err
    rc = {"ADVANCE": 0, "STOP": 1, "UNMEASURABLE": 2}[rec["decision"]]
    return rc, summary_line(rec)


def _opt(argv: list, flag: str):
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
        return ""
    return argv[i + 1]


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
                       "  - {id: ECO-902, title: t2, status: in-progress, order_ref: bomdd/closed.md}\n", encoding="utf-8")
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

        def arm(name: str, w: dict | None, want_rc: int, want_dec: str, want_delivery: str, launched: bool, eco: str = "ECO-900", use_cell: bool = True):
            if marker.exists():
                marker.unlink()
            if w is None:
                if wpath.exists():
                    wpath.unlink()
            else:
                wpath.write_text(json.dumps(w), encoding="utf-8")
            argv = [eco, "--ledger", str(ledger)] + (["--cell", cell] if use_cell else [])
            rc, line = run(argv, root)
            rec = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1]) if ledger.exists() else {}
            if rc != want_rc or rec.get("decision") != want_dec:
                fails.append(f"{name}: exit {rc} / decision {rec.get('decision')}(期待 {want_rc}/{want_dec}) :: {line}")
            if rec.get("delivery") != want_delivery:
                fails.append(f"{name}: delivery {rec.get('delivery')} != {want_delivery}")
            if marker.exists() != launched:
                fails.append(f"{name}: 起動痕跡 {marker.exists()}(期待 {launched})— fail-open の入口版" if marker.exists() else f"{name}: 起動されなかった(期待 起動)")
            if len(line) > 80:
                fails.append(f"{name}: 1 行が 80 桁超({len(line)}): {line}")
            if not line.startswith(want_dec + " "):
                fails.append(f"{name}: 1 行目が decision で始まらない: {line}")
            return rec, line

        rec_good, _ = arm("known-good", good, 0, "ADVANCE", "next", True)
        if marker.exists() and marker.read_text(encoding="utf-8") != f"ECO-900|{wpath}":
            fails.append(f"known-good: 起動先が受け取った環境が不正: {marker.read_text(encoding='utf-8')}")
        if rec_good.get("cell_exit") != 0 or rec_good.get("verifier_line", "").startswith("ADVANCE OK:") is False:
            fails.append(f"known-good: 台帳 cell_exit {rec_good.get('cell_exit')} / verifier_line {rec_good.get('verifier_line')}")
        arm("dry", good, 0, "ADVANCE", "next", False, use_cell=False)
        # known-bad 5 腕(receipt)— 起動しない
        arm("kb-tree", dict(good, tree=good["tree"][:-4] + ("0000" if good["tree"][-4:] != "0000" else "1111")), 1, "STOP", "operator", False)
        arm("kb-other-job", dict(good, eco="ECO-901"), 1, "STOP", "operator", False)
        arm("kb-fail", dict(good, gates=[{"name": "g", "exit": 1, "source": "x"}]), 1, "STOP", "factory", False)
        arm("kb-missing", dict(good, gates=[]), 1, "STOP", "operator", False)
        arm("kb-stop", dict(good, stop_type="NORMATIVE_RULING"), 1, "STOP", "human", False)
        # job の停止(台帳不整合)— receipt が有効でも起動しない
        w902 = dict(good, witness="WIT-ECO-902", eco="ECO-902")
        witmod.default_path(git_dir, "ECO-902").write_text(json.dumps(w902), encoding="utf-8")
        if marker.exists():
            marker.unlink()
        rc902, line902 = run(["ECO-902", "--ledger", str(ledger), "--cell", cell], root)
        rec902 = json.loads(ledger.read_text(encoding="utf-8").splitlines()[-1])
        if rc902 != 1 or rec902.get("decision") != "STOP" or rec902.get("delivery") != "ledger-owner" or marker.exists():
            fails.append(f"kb-job-stop: exit {rc902} / {rec902.get('decision')} / {rec902.get('delivery')} / 起動 {marker.exists()} :: {line902}")
        # 測定不能(witness 不在・register に無い ECO)— 起動しない
        arm("kb-absent", None, 2, "UNMEASURABLE", "operator", False)
        arm("kb-no-eco", good, 2, "UNMEASURABLE", "operator", False, eco="ECO-999")
        # 台帳を作業木内に置く → 拒否(自己参照)
        rc_in, line_in = run(["ECO-900", "--ledger", str(root / "ledger.jsonl")], root)
        if rc_in != 2 or (root / "ledger.jsonl").exists():
            fails.append(f"kb-ledger-inside: exit {rc_in} / 存在 {(root / 'ledger.jsonl').exists()} :: {line_in}")
        # 引数不正
        for bad in ([], ["--cell", "x"], ["ECO-900", "--cell"], ["ECO-900", "--ledger"]):
            rc_b, line_b = run(bad, root)
            if rc_b != 2 or not line_b.startswith("UNMEASURABLE ARG_ERROR"):
                fails.append(f"arg {bad}: exit {rc_b} :: {line_b}")
        # 台帳の形(追記・全レコードに verifier_line と decision)
        lines = ledger.read_text(encoding="utf-8").splitlines()
        if len(lines) < 10 or any("decision" not in json.loads(ln) for ln in lines):
            fails.append(f"ledger: 行数 {len(lines)} / 形不正")
        # 配送先表の自己整合(job 語彙と 1 対 1)
        jobmod = _load("bomdd-job")
        vocab = set(getattr(jobmod, "STOP_VOCABULARY", ()) or ())
        if vocab and set(DELIVERY) != vocab:
            fails.append(f"DELIVERY と job の停止語彙が一致しない: {sorted(set(DELIVERY) ^ vocab)}")
        if set(WITNESS_DELIVERY) != set(witmod.CODES):
            fails.append(f"WITNESS_DELIVERY と witness の CODES が一致しない: {sorted(set(WITNESS_DELIVERY) ^ set(witmod.CODES))}")
    return _report(fails)


def _report(fails) -> int:
    if fails:
        print("STOP SELFTEST_FAIL: " + f"{len(fails)} 件\n  " + "\n  ".join(fails))
        return 1
    print("ADVANCE OK: selftest PASS(known-good 起動 1 / dry 0 / known-bad 受理せず 5〔tree・別 job・FAIL・欠測・stop〕+ job 停止 1 + 測定不能 2 / "
          "台帳 作業木内拒否 / 引数不正 4 / 1 行 80 桁以内 / 配送先表と語彙の 1 対 1)")
    return 0


def main(argv) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", newline="\n")
    if "--selftest" in argv:
        return selftest()
    rc, line = run(argv, Path.cwd())
    print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
