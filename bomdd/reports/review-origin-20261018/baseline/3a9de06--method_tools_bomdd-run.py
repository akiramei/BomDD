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
#  R9 独立性判定(ECO-072・Phase 7 第 1 弾): --cell には --executor EQ-NNN が必須(無ければ ARG_ERROR・起動しない)。
#     job.required_capability.producer(order の配員欄・台帳で実在確認済み)と executor を設備台帳 bomdd/70-equipment.yaml で
#     照合し、同一 id(SAME_ID)/ model+harness+account_lineage の 3 軸すべて一致(SAME_LINEAGE)/ いずれかの軸が unknown
#     (AXIS_UNKNOWN:<axis>)/ producer 未宣言(PRODUCER_UNDECLARED)/ executor が台帳にない(EXECUTOR_UNKNOWN)は
#     STOP INDEPENDENCE_FAIL → operator(配員のやり直し)。台帳が読めないときは UNMEASURABLE MISSING_INPUT。判定は
#     宣言属性の照合であり独立性の実効は主張しない(Grok 公式の境界)。起動先には BOMDD_EXECUTOR も渡す。
#  R10 cell の判定の回収(ECO-073・Phase 7 第 2 弾): --report PATH(--cell と組・リポ相対・作業木内・.git 配下不可・`..` 不可)を
#     与えると、cell 終了後に PATH を読み {path, exists, size, sha256, verdict, verdict_line} を台帳の cell 行に束ね、
#     `report <VERDICT> sha256:<12 桁> (<EQ>)` の 1 行を出す。判定語の契約(REPORT_VERDICT): 先頭の handoff ヘッダ行(`[` で始まる)
#     0〜1 行と空行を飛ばし、最初の非空行の先頭が ACCEPT|REJECT|UNMEASURABLE ならその語。報告なし= MISSING・契約外= UNPARSED。
#     散文は解釈しない。入口は判定に基づいて行動しない(入口の exit は R8 のまま= 起動したら 0。cell の終了コードは 2 行目と台帳・
#     register/witness を動かさない= 第 3 弾)。起動先には BOMDD_REPORT(与えたパスそのまま・cwd= root)を渡す。
#     r1 IA-02 / r2 IA-06: 宛先が起動前に既に存在するなら(ファイル・ディレクトリを問わず)起動しない(ARG_ERROR・既存物を今回の報告と
#     取り違えない・書けない宛先へ起動しない)。cell 終了時点で
#     無ければ MISSING(子プロセスの遅延書込みは cell 側の責務)。r1 IA-03: root は cwd(ECO-067 の規約)— 別 cwd では register 不在=
#     MISSING_INPUT で起動しない。r1 IA-05: 判定語は行頭から照合(行頭空白は契約外= UNPARSED)・verdict_line は原文。
#  R11 verified 昇格の要求(ECO-074・Phase 7 第 3 弾): --report には --range 境界探索|是正確認+回帰 が必須(台帳 cell 行の report.range と
#     env BOMDD_RANGE)。job.state が verified かつ job.independent_inspection.required(配員欄に inspector)のとき、witness に name=inspection の
#     gate(bomdd-witness produce --inspection-from-ledger が台帳から導出)が無ければ STOP INSPECTION_MISSING → operator(独立検査の結果回収)。
#     gate の exit≠0 は witness 側の GATE_FAIL(→ factory)。verified 以外・inspector 宣言なしは従来どおり。register は動かさない(入口は止めるだけ)。
#
# 使い方:
#   python bomdd-run.py ECO-067                      # dry: 検証+台帳
#   python bomdd-run.py ECO-067 --cell "codex exec ..." --executor EQ-002   # ADVANCE かつ独立なときだけ起動
#   python bomdd-run.py ECO-067 --cell "codex exec -o bomdd/reports/x.md ..." --executor EQ-002 --report bomdd/reports/x.md
#   python bomdd-run.py ECO-067 --ledger PATH         # 台帳の場所(作業木外のみ)
#   python bomdd-run.py --selftest                    # known-good 1 腕は起動し known-bad 腕は起動しない(痕跡で判定)
#
# 検出力の限界(宣言):
#   (1) 起動先が何をするかは責務外(製造セルの契約)。台帳に残すのは起動した事実と終了コードのみ。
#   (2) receipt の申告値(gates.exit)は再実測しない(bomdd-witness W2 と同じ)。
#   (3) 承認の有無は起動先ハーネスの設定に依存する — 本ツールは承認を作らない・迂回もしない。

import hashlib
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
KNOWN_OPTS = ("--cell", "--ledger", "--executor", "--report", "--range")
RANGES = ("境界探索", "是正確認+回帰")   # R11: round の目的(playbook §3)
VERDICT_RE = re.compile(r"^(ACCEPT|REJECT|UNMEASURABLE)\b")   # R10: 判定語の契約(大小文字を区別・固定語彙)
EQ_ID_RE = re.compile(r"^EQ-\d{3}$")

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
    "INDEPENDENCE_FAIL": "operator",   # R9(ECO-072): 配員のやり直し
    "INSPECTION_MISSING": "operator",  # R11(ECO-074): 独立検査の結果回収
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


def _unknown(v) -> bool:
    return not isinstance(v, str) or not v.strip() or v.strip().lower() == "unknown"


def _norm(v: str) -> str:
    """r1 IA-02: 表記揺れ(大小文字・連続空白)を独立の根拠にしない — casefold+空白正規化で比較する。"""
    return " ".join(v.split()).casefold()


def check_independence(root: Path, job: dict, executor: str, jobmod) -> tuple[str | None, str, dict]:
    """R9: (cause, detail, axes)。cause None= 独立(起動可)。LEDGER_UNREADABLE は測定不能(呼び側で UNMEASURABLE)。"""
    eq, err = jobmod.load_equipment(root)
    if eq is None:
        return "LEDGER_UNREADABLE", err or "設備台帳 読取不能", {}
    cap = _job_value(job, "required_capability")
    producer = cap.get("producer") if isinstance(cap, dict) else None
    if not isinstance(producer, str) or not producer:
        return "PRODUCER_UNDECLARED", "order に配員欄(- producer: EQ-NNN)がない", {}
    if executor not in eq:
        return "EXECUTOR_UNKNOWN", f"executor {executor} が設備台帳にない", {}
    if producer not in eq:
        return "PRODUCER_UNKNOWN", f"producer {producer} が設備台帳にない", {}
    if executor == producer:
        return "SAME_ID", f"producer と executor が同一 {producer}", {}
    axes = {}
    for ax in jobmod.INDEPENDENCE_AXES:
        pv, ev = eq[producer].get(ax), eq[executor].get(ax)
        if _unknown(pv) or _unknown(ev):
            return f"AXIS_UNKNOWN:{ax}", f"軸 {ax} が unknown(照合不能を通過にしない)", axes
        axes[ax] = (_norm(pv) == _norm(ev))
    if all(axes.values()):
        return "SAME_LINEAGE", "model・harness・account_lineage がすべて一致", axes
    return None, "独立(3 軸のいずれかが異なる)", axes


def decide(root: Path, eco: str, jobmod, witmod, executor: str | None = None) -> tuple[dict, dict | None]:
    """R1〜R3・R6・R9: 判定レコード(台帳 1 行目の元)。起動はしない。"""
    rec = {"event": "decision", "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"), "eco": eco,
           "receipt": None, "job_state": None, "job_stop_type": None, "verifier_line": None, "verifier_exit": None,
           "code": None, "decision": None, "stop_type": None, "delivery": None, "cell": None, "tree": None,
           "executor": executor, "producer": None, "independence": None, "report": None, "inspection": None}
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
    insp_req = _job_value(job, "independent_inspection")   # R11(r1 IA-05): gate の有無・値は判定前に記録(失敗時も残す)
    if rec["job_state"] == "verified" and isinstance(insp_req, dict) and insp_req.get("required"):
        try:
            _gates = json.loads(path.read_text(encoding="utf-8")).get("gates") or []
        except (OSError, ValueError):
            _gates = []
        _g = next((x for x in _gates if isinstance(x, dict) and x.get("name") == "inspection"), None)
        rec["inspection"] = {"required": True, "inspector": insp_req.get("inspector"), "gate": _g}
    else:
        rec["inspection"] = {"required": False}
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
    if rec["inspection"].get("required") and rec["inspection"].get("gate") is None:   # R11: verified 昇格には inspection gate が要る(台帳から導出したもの)
        rec.update(decision="STOP", stop_type="INSPECTION_MISSING", delivery=DELIVERY["INSPECTION_MISSING"])
        return rec, job
    if executor is not None:   # R9: job・receipt が ADVANCE のときだけ独立性を照合(先行する停止理由を隠さない)
        cap = _job_value(job, "required_capability")
        rec["producer"] = cap.get("producer") if isinstance(cap, dict) else None
        cause, detail, axes = check_independence(root, job, executor, jobmod)
        rec["independence"] = {"cause": cause, "detail": detail, "axes": axes}
        if cause == "LEDGER_UNREADABLE":
            rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery="operator")
            return rec, job
        if cause is not None:
            rec.update(decision="STOP", stop_type="INDEPENDENCE_FAIL", delivery=DELIVERY["INDEPENDENCE_FAIL"])
            return rec, job
    rec.update(decision="ADVANCE", stop_type="NONE", delivery="next")
    return rec, job


def report_verdict(text: str) -> tuple[str, str | None]:
    """R10: (verdict, verdict_line)。先頭の handoff ヘッダ行(`[` で始まる)を 1 行まで飛ばし、最初の非空行の先頭を固定語彙と照合。契約外= UNPARSED。"""
    lines = [ln.rstrip("\r") for ln in text.split("\n")]
    i, skipped_header = 0, False
    while i < len(lines):
        ln = lines[i]   # r1 IA-05: 行頭を保つ(空白始まりは契約外)・verdict_line は原文
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("[") and not skipped_header:
            skipped_header = True
            i += 1
            continue
        m = VERDICT_RE.match(ln)
        return (m.group(1) if m else "UNPARSED"), ln[:120]
    return "UNPARSED", None


def bind_report(root: Path, report: str, rng: str | None = None) -> dict:
    """R10/R11: 報告ファイルの結線(存在・大きさ・sha256・判定語・range)。読めない/無い= MISSING(推定で埋めない)。"""
    out = {"path": report, "exists": False, "size": None, "sha256": None, "verdict": "MISSING", "verdict_line": None, "range": rng}
    p = root / report
    try:
        data = p.read_bytes()
    except OSError:
        return out
    out.update(exists=True, size=len(data), sha256=hashlib.sha256(data).hexdigest())
    v, line = report_verdict(data.decode("utf-8", errors="replace"))
    out.update(verdict=v, verdict_line=line)
    return out


def _report_path_error(root: Path, git_dir: Path | None, report: str) -> str | None:
    """R10: --report の構文・所在検査。None= 可。リポ相対・`..` なし・`\\` は `/` 扱い・作業木内・.git 配下不可。"""
    s = report.replace("\\", "/")
    if not s.strip() or s.strip() != s or s.startswith("/") or re.match(r"^[A-Za-z]:", s) or any(seg in ("..", "") for seg in s.split("/")):
        return f"--report はリポ相対パス(絶対・`..`・空要素・前後空白不可): {report!r}"
    p = root / s
    if not _under(p, root):
        return "--report が作業木の外へ出る"
    if git_dir is not None and _under(p, git_dir):
        return "--report を .git 配下に置けない(commit できる場所に限る)"
    return None


def launch(rec: dict, job: dict, cell: str, root: Path, report: str | None = None, rng: str | None = None) -> dict:
    """R5/R10: 3 条件成立時のみ呼ばれる。コマンドはそのまま・環境で job/witness/executor/report を渡す・承認は起動先。台帳 2 行目のレコードを返す。"""
    with tempfile.NamedTemporaryFile("w", suffix=".json", prefix="bomdd-job-", delete=False, encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
        job_json = f.name
    env = dict(os.environ, BOMDD_JOB=rec["eco"], BOMDD_JOB_JSON=job_json, BOMDD_WITNESS=rec["receipt"], BOMDD_EXECUTOR=rec.get("executor") or "",
               BOMDD_REPORT=report or "", BOMDD_RANGE=rng or "")
    ev = {"event": "cell", "run_id": rec["run_id"], "eco": rec["eco"], "cell": cell, "executor": rec.get("executor"),
          "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "cell_exit": None, "report": None}
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
    if report:   # R10: cell 終了後に報告を束ねる(cell が書いたものを読むだけ・解釈しない)
        ev["report"] = bind_report(root, report, rng)
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
    if rec["stop_type"] == "INSPECTION_MISSING":   # R11
        tag = "INSPECTION_MISSING"
    ind = rec.get("independence") or {}
    if ind.get("cause") and rec["decision"] != "ADVANCE":   # R9
        tag = f"INDEPENDENCE_FAIL({ind['cause']})" if rec["stop_type"] == "INDEPENDENCE_FAIL" else f"MISSING_INPUT({ind['cause']})"
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
        emit("UNMEASURABLE ARG_ERROR: ECO [--cell --executor --report --range] [--ledger]")
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
    executor = opts.get("--executor")
    if executor is not None and not EQ_ID_RE.match(executor):   # R9
        emit(_fit(f"UNMEASURABLE ARG_ERROR: --executor の構文不正(EQ-NNN): {executor!r}"))
        return 2
    if cell and executor is None:   # R9: 起動には配員の宣言が要る(fail-closed)
        emit("UNMEASURABLE ARG_ERROR: --cell には --executor EQ-NNN が必須(独立性判定)")
        return 2
    report = opts.get("--report")
    if report is not None and not cell:   # R10
        emit("UNMEASURABLE ARG_ERROR: --report は --cell と組で指定する")
        return 2
    rng = opts.get("--range")   # R11
    if rng is not None and report is None:
        emit("UNMEASURABLE ARG_ERROR: --range は --report と組で指定する")
        return 2
    if report is not None and rng is None:
        emit("UNMEASURABLE ARG_ERROR: --report には --range 境界探索|是正確認+回帰 が必須")
        return 2
    if rng is not None and rng not in RANGES:
        emit(_fit(f"UNMEASURABLE ARG_ERROR: --range の語彙外: {rng!r}"))
        return 2
    jobmod, witmod = _load("bomdd-job"), _load("bomdd-witness")
    _, git_dir0, _ = witmod.worktree_tree(root)
    if report is not None:
        perr = _report_path_error(root, git_dir0, report)
        if perr:
            emit(_fit("UNMEASURABLE ARG_ERROR: " + perr))
            return 2
        if (root / report).exists():   # r1 IA-02 / r2 IA-06: 既存物(ファイル・ディレクトリ)を今回の cell の報告と取り違えない(fail-closed)
            emit(_fit(f"UNMEASURABLE ARG_ERROR: --report の宛先が既に存在する: {report}"))
            return 2
    rec, job = decide(root, eco, jobmod, witmod, executor)
    rec["report"] = report
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
        ev = launch(rec, job, cell, root, report, rng)   # R5/R10/R11
        err2 = write_ledger(ledger, ev)
        emit(_fit(f"cell exit {ev['cell_exit']}" + (f" · 台帳追記失敗: {err2}" if err2 else "")))
        if report is not None:   # R10: 判定語の回収を 1 行で(入口の exit は R8 のまま 0・判定で行動しない)
            rp = ev["report"] or {}
            sha = (rp.get("sha256") or "")[:12]
            emit(_fit(f"report {rp.get('verdict')} " + (f"sha256:{sha} " if sha else "(no file) ") + f"({rec.get('executor')})"))
        return 0
    return {"ADVANCE": 0, "STOP": 1, "UNMEASURABLE": 2}[rec["decision"]]


# --- selftest: 一時 git リポ(実リポ非接触)で known-good は起動し known-bad は起動しない ---------------------
def selftest() -> int:
    # ECO-068: selftest 自身の前提(OS temp・git)不在は traceback でなく UNMEASURABLE の 1 行・exit 2
    try:
        td_cm, wd_cm = tempfile.TemporaryDirectory(), tempfile.TemporaryDirectory()
    except OSError as e:
        print(f"UNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE): selftest の前提不在 — {e.__class__.__name__}: {str(e)[:120]}")
        return 2
    return _selftest_body(td_cm, wd_cm)


def _selftest_body(td_cm, wd_cm) -> int:
    fails = []
    witmod = _load("bomdd-witness")
    with td_cm as td, wd_cm as wd:
        root, wout = Path(td), Path(wd)
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@x", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
        for cmd in (["init", "-q"], ["config", "core.autocrlf", "false"]):
            r0 = witmod._git(root, *cmd, env=env)
            if r0.returncode != 0:
                if isinstance(r0, witmod._GitUnavailable):  # ECO-068: git 不能は測定不能(exit 2)
                    print("UNMEASURABLE TREE_UNAVAILABLE(GIT_UNAVAILABLE): selftest の前提不在 — git を起動できない")
                    return 2
                return _report(["fixture: git init 不能"])
        (root / "bomdd").mkdir()
        (root / "bomdd" / "open.md").write_text("# Change Order — ECO-900\n\n## 担当設備\n\n- producer: EQ-001\n- inspector: EQ-002\n\n## 3. 受入\n- 検討中\n", encoding="utf-8")
        (root / "bomdd" / "closed-insp.md").write_text("# Change Order — ECO-904\n\n## 担当設備\n\n- producer: EQ-001\n- inspector: EQ-002\n\n## 6. クローズ(2026-09-12・verified)\n- PASS\n", encoding="utf-8")
        (root / "bomdd" / "nocap.md").write_text("# Change Order — ECO-903\n\n## 3. 受入\n- 検討中\n", encoding="utf-8")
        (root / "bomdd" / "closed.md").write_text("# Change Order — ECO-902\n\n## 6. クローズ(2026-09-03・verified)\n- PASS\n", encoding="utf-8")
        eqp = root / "bomdd" / "70-equipment.yaml"
        EQ_TXT = ("equipment:\n"
                  "  - {id: EQ-001, kind: ai-model, model: m1, harness: h1, account_lineage: a1}\n"
                  "  - {id: EQ-002, kind: ai-model, model: m2, harness: h2, account_lineage: a2}\n"
                  "  - {id: EQ-003, kind: ai-model, model: m1, harness: h1, account_lineage: a1}\n"
                  "  - {id: EQ-004, kind: ai-model, model: unknown, harness: h4, account_lineage: a4}\n"
                  "  - {id: EQ-005, kind: ai-model, model: m1, harness: h1, account_lineage: a5}\n"
                  "  - {id: EQ-006, kind: ai-model, model: M1, harness: '  h1  ', account_lineage: A1}\n")
        eqp.write_text(EQ_TXT, encoding="utf-8")
        reg = root / "bomdd" / "60-change-register.yaml"
        reg.write_text("changes:\n"
                       "  - {id: ECO-900, title: t, status: decided, order_ref: bomdd/open.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
                       "  - {id: ECO-902, title: t2, status: in-progress, order_ref: bomdd/closed.md}\n"
                       "  - {id: ECO-903, title: t3, status: decided, order_ref: bomdd/nocap.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
                       "  - {id: ECO-904, title: t4, status: verified, order_ref: bomdd/closed-insp.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
                       "  - {id: ECO-905, title: t5, status: verified, order_ref: bomdd/closed.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
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
        cell = f'"{sys.executable}" -c "import pathlib,os; pathlib.Path(r\'{marker}\').write_text(os.environ.get(\'BOMDD_JOB\',\'\')+\'|\'+os.environ.get(\'BOMDD_WITNESS\',\'\')+\'|\'+os.environ.get(\'BOMDD_EXECUTOR\',\'\'))"'
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

        def arm(name, w, want_rc, want_dec, want_delivery, launched, eco="ECO-900", use_cell=True, executor="EQ-002"):
            if marker.exists():
                marker.unlink()
            if w is None:
                if wpath.exists():
                    wpath.unlink()
            else:
                wpath.write_text(json.dumps(w), encoding="utf-8")
            rc, out = call([eco, "--ledger", str(ledger)] + (["--cell", cell] if use_cell else []) + (["--executor", executor] if executor else []))
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
        if marker.exists() and marker.read_text(encoding="utf-8") != f"ECO-900|{wpath}|EQ-002":
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
        rc902, out902 = call(["ECO-902", "--ledger", str(ledger), "--cell", cell, "--executor", "EQ-002"])
        dec902 = last_rec()
        if rc902 != 1 or dec902.get("decision") != "STOP" or dec902.get("delivery") != "ledger-owner" or marker.exists():
            fails.append(f"kb-job-stop: exit {rc902} / {dec902.get('decision')} / {dec902.get('delivery')} / 起動 {marker.exists()} :: {out902[:1]}")
        arm("kb-absent", None, 2, "UNMEASURABLE", "operator", False)
        arm("kb-no-eco", good, 2, "UNMEASURABLE", "operator", False, eco="ECO-999")
        # --- R9(ECO-072): 独立性判定 — known-bad は起動しない・独立は起動する ---
        d1, o1 = arm("ind-same-id", good, 1, "STOP", "operator", False, executor="EQ-001")
        if (d1.get("independence") or {}).get("cause") != "SAME_ID" or d1.get("stop_type") != "INDEPENDENCE_FAIL" or "INDEPENDENCE_FAIL(SAME_ID)" not in o1[0]:
            fails.append(f"ind-same-id: {d1.get('independence')} / {d1.get('stop_type')} :: {o1[:1]}")
        d2, _ = arm("ind-same-lineage", good, 1, "STOP", "operator", False, executor="EQ-003")
        if (d2.get("independence") or {}).get("cause") != "SAME_LINEAGE":
            fails.append(f"ind-same-lineage: {d2.get('independence')}")
        d3, _ = arm("ind-axis-unknown", good, 1, "STOP", "operator", False, executor="EQ-004")
        if (d3.get("independence") or {}).get("cause") != "AXIS_UNKNOWN:model":
            fails.append(f"ind-axis-unknown: {d3.get('independence')}")
        d4, _ = arm("ind-executor-unknown", good, 1, "STOP", "operator", False, executor="EQ-999")
        if (d4.get("independence") or {}).get("cause") != "EXECUTOR_UNKNOWN":
            fails.append(f"ind-executor-unknown: {d4.get('independence')}")
        d5, o5 = arm("ind-one-axis-differs", good, 0, "ADVANCE", "next", True, executor="EQ-005")
        if (d5.get("independence") or {}).get("axes") != {"model": True, "harness": True, "account_lineage": False} or d5.get("producer") != "EQ-001":
            fails.append(f"ind-one-axis-differs: {d5.get('independence')} / producer {d5.get('producer')}")
        if marker.exists() and not marker.read_text(encoding="utf-8").endswith("|EQ-005"):
            fails.append(f"ind-one-axis-differs: BOMDD_EXECUTOR が渡っていない: {marker.read_text(encoding='utf-8')}")
        # r1 IA-02: 大小文字・空白だけの差は同系統(SAME_LINEAGE)・起動しない
        d8, _ = arm("ind-case-only", good, 1, "STOP", "operator", False, executor="EQ-006")
        if (d8.get("independence") or {}).get("cause") != "SAME_LINEAGE":
            fails.append(f"ind-case-only: {d8.get('independence')}")
        # producer 未宣言(配員欄なしの order)+ executor → STOP PRODUCER_UNDECLARED(起動しない)
        w903 = dict(good, witness="WIT-ECO-903", eco="ECO-903")
        witmod.default_path(git_dir, "ECO-903").write_text(json.dumps(w903), encoding="utf-8")
        d6, o6 = arm("ind-producer-undeclared", good, 1, "STOP", "operator", False, eco="ECO-903", executor="EQ-002")
        if (d6.get("independence") or {}).get("cause") != "PRODUCER_UNDECLARED":
            fails.append(f"ind-producer-undeclared: {d6.get('independence')} :: {o6[:1]}")
        # dry(--cell なし)は executor なしでも従来どおり ADVANCE / executor つき dry も照合する
        arm("ind-dry-no-executor", good, 0, "ADVANCE", "next", False, use_cell=False, executor=None)
        arm("ind-dry-same-id", good, 1, "STOP", "operator", False, use_cell=False, executor="EQ-001")
        # 台帳不在 → job 側が先に MISSING_INPUT(宣言あり+台帳不能)で止める(STOP job:MISSING_INPUT → operator・起動しない)
        eqp.unlink()
        d7, o7 = arm("ind-ledger-missing", good, 1, "STOP", "operator", False, executor="EQ-002")
        if d7.get("job_stop_type") != "MISSING_INPUT" or "job:MISSING_INPUT" not in o7[0]:
            fails.append(f"ind-ledger-missing: {d7.get('job_stop_type')} :: {o7[:1]}")
        eqp.write_text(EQ_TXT, encoding="utf-8")
        # --- R10(ECO-073): 報告の結線と判定語の契約 ---
        (root / "reports").mkdir(exist_ok=True)
        src = wout / "rep-src.txt"
        cell_rep = f'"{sys.executable}" -c "import os,shutil; shutil.copy(r\'{src}\', os.environ[\'BOMDD_REPORT\'])"'
        cell_norep = f'"{sys.executable}" -c "pass"'
        def rep_arm(name, content, want_verdict, want_line3):
            rp = root / "reports" / "r.md"
            if rp.exists():
                rp.unlink()
            if content is None:
                c = cell_norep
            else:
                src.write_text(content, encoding="utf-8")
                c = cell_rep
            rc_r, out_r = call(["ECO-900", "--ledger", str(ledger), "--cell", c, "--executor", "EQ-002", "--report", "reports/r.md", "--range", "是正確認+回帰"])
            ev_r = last_rec()
            rpt = ev_r.get("report") or {}
            if rc_r != 0 or ev_r.get("event") != "cell" or rpt.get("verdict") != want_verdict or rpt.get("range") != "是正確認+回帰" or len(out_r) != 3 or not out_r[2].startswith(want_line3):
                fails.append(f"{name}: exit {rc_r} / verdict {rpt.get('verdict')} / out {out_r}")
            if content is not None:
                want_sha = hashlib.sha256(rp.read_bytes()).hexdigest() if rp.exists() else None
                if rpt.get("sha256") != want_sha or rpt.get("exists") is not True or rpt.get("size") != (len(rp.read_bytes()) if rp.exists() else None):
                    fails.append(f"{name}: sha256/exists/size が実ファイルと一致しない: {rpt}")
                if want_sha and not out_r[2].startswith(f"report {want_verdict} sha256:{want_sha[:12]} (EQ-002)"):
                    fails.append(f"{name}: report 行の形が不正: {out_r[2]}")
            else:
                if rpt.get("exists") is not False or rpt.get("sha256") is not None:
                    fails.append(f"{name}: MISSING の記録が不正: {rpt}")
            if rp.exists():
                rp.unlink()
        rep_arm("rep-accept-header", "[INFORM / COMPLETE]\n\nACCEPT\n", "ACCEPT", "report ACCEPT sha256:")
        rep_arm("rep-reject-noheader", "REJECT — 理由: IA-01\n", "REJECT", "report REJECT sha256:")
        rep_arm("rep-unmeasurable", "\n\n[INFORM / BLOCKED]\n\n\nUNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE): x\n", "UNMEASURABLE", "report UNMEASURABLE sha256:")
        rep_arm("rep-missing", None, "MISSING", "report MISSING (no file) (EQ-002)")
        rep_arm("rep-unparsed-summary", "要約: 問題なし\nACCEPT\n", "UNPARSED", "report UNPARSED sha256:")
        rep_arm("rep-unparsed-fence", "```\nACCEPT\n```\n", "UNPARSED", "report UNPARSED sha256:")
        rep_arm("rep-unparsed-two-headers", "[INFORM / COMPLETE]\n[DECIDE / BLOCKED]\nACCEPT\n", "UNPARSED", "report UNPARSED sha256:")
        rep_arm("rep-unparsed-lowercase", "accept\n", "UNPARSED", "report UNPARSED sha256:")
        rep_arm("rep-unparsed-prefix", "ACCEPTED by me\n", "UNPARSED", "report UNPARSED sha256:")
        rep_arm("rep-empty", "", "UNPARSED", "report UNPARSED sha256:")
        if report_verdict("[x]\r\n\r\nREJECT: y\r\n") != ("REJECT", "REJECT: y"):
            fails.append("report_verdict: CRLF/コロン付きの REJECT を読めない")
        rep_arm("rep-unparsed-leading-space", "  ACCEPT\n", "UNPARSED", "report UNPARSED sha256:")   # r1 IA-05
        if report_verdict("  ACCEPT\n")[1] != "  ACCEPT":
            fails.append("IA-05: verdict_line が原文でない")
        rep_arm("rep-unparsed-bom", "\ufeffACCEPT\n", "UNPARSED", "report UNPARSED sha256:")
        # r1 IA-02: 宛先が起動前に存在 → ARG_ERROR・起動なし・台帳不変
        (root / "reports" / "stale.md").write_text("ACCEPT\n", encoding="utf-8")
        n_st = len(ledger.read_text(encoding="utf-8").splitlines())
        if marker.exists():
            marker.unlink()
        rc_st, out_st = call(["ECO-900", "--ledger", str(ledger), "--cell", cell, "--executor", "EQ-002", "--report", "reports/stale.md", "--range", "境界探索"])
        if rc_st != 2 or not out_st[0].startswith("UNMEASURABLE ARG_ERROR") or marker.exists() or len(ledger.read_text(encoding="utf-8").splitlines()) != n_st:
            fails.append(f"IA-02 stale: exit {rc_st} / 起動 {marker.exists()} :: {out_st[:1]}")
        (root / "reports" / "stale.md").unlink()
        (root / "reports" / "dirtarget").mkdir()   # r2 IA-06: 同名ディレクトリも起動前拒否
        rc_dt, out_dt = call(["ECO-900", "--ledger", str(ledger), "--cell", cell, "--executor", "EQ-002", "--report", "reports/dirtarget", "--range", "境界探索"])
        if rc_dt != 2 or not out_dt[0].startswith("UNMEASURABLE ARG_ERROR") or marker.exists() or len(ledger.read_text(encoding="utf-8").splitlines()) != n_st:
            fails.append(f"IA-06 dir: exit {rc_dt} / 起動 {marker.exists()} :: {out_dt[:1]}")
        (root / "reports" / "dirtarget").rmdir()
        # r1 IA-01(R8 明確化): cell exit≠0 でも報告は束ねられ、入口 exit は 0(起動した)・3 行の順
        src.write_text("[INFORM / COMPLETE]\n\nREJECT — IA-01\n", encoding="utf-8")
        cell_rep7 = f'"{sys.executable}" -c "import os,shutil,sys; shutil.copy(r\'{src}\', os.environ[\'BOMDD_REPORT\']); sys.exit(7)"'
        rc7, out7 = call(["ECO-900", "--ledger", str(ledger), "--cell", cell_rep7, "--executor", "EQ-002", "--report", "reports/r7.md", "--range", "境界探索"])
        ev7 = last_rec()
        if rc7 != 0 or ev7.get("cell_exit") != 7 or (ev7.get("report") or {}).get("verdict") != "REJECT" or len(out7) != 3 or not out7[1].startswith("cell exit 7") or not out7[2].startswith("report REJECT sha256:"):
            fails.append(f"IA-01: cell exit 7 の扱い: exit {rc7} / {ev7.get('cell_exit')} / {out7}")
        (root / "reports" / "r7.md").unlink()
        # --report の構文・所在: 絶対 / `..` / .git 配下 / 前後空白 / 空 / --cell なし → ARG_ERROR・起動しない・台帳不変
        n_before_r = len(ledger.read_text(encoding="utf-8").splitlines())
        for bad_rep in (["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--report", "reports/x.md"],   # R11: --range なし
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--report", "reports/x.md", "--range", "探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--report", str(wout / "x.md"), "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--report", "reports/../x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--report", ".git/x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--report", " reports/x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--report", "/reports/x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--report", "reports//x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--executor", "EQ-002", "--report", "reports/x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--executor", "EQ-002", "--report"]):
            if marker.exists():
                marker.unlink()
            rc_x, out_x = call(bad_rep)
            if rc_x != 2 or not out_x or not out_x[0].startswith("UNMEASURABLE ARG_ERROR") or marker.exists():
                fails.append(f"rep-arg {bad_rep[-1]!r}: exit {rc_x} :: {out_x[:1]}")
        if len(ledger.read_text(encoding="utf-8").splitlines()) != n_before_r:
            fails.append("rep-arg: 不正 --report で台帳に書いた")
        # --report なしの既存経路は不変(cell 行に report=None・出力 2 行)
        d_nr, o_nr = arm("rep-none-regression", good, 0, "ADVANCE", "next", True)
        if last_rec().get("report") is not None or len(o_nr) != 2:
            fails.append(f"rep-none-regression: {last_rec().get('report')} / {o_nr}")
        # --cell に --executor なし / 構文外 → ARG_ERROR・起動しない
        for bad_ex in (["ECO-900", "--ledger", str(ledger), "--cell", cell], ["ECO-900", "--ledger", str(ledger), "--cell", cell, "--executor", "EQ-1"],
                       ["ECO-900", "--ledger", str(ledger), "--cell", cell, "--executor", "eq-002"]):
            if marker.exists():
                marker.unlink()
            rc_e, out_e = call(bad_ex)
            if rc_e != 2 or not out_e or not out_e[0].startswith("UNMEASURABLE ARG_ERROR") or marker.exists():
                fails.append(f"ind-arg {bad_ex[-2:]}: exit {rc_e} / 起動 {marker.exists()} :: {out_e[:1]}")
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
        # --- R11(ECO-074): verified 昇格には inspection gate が要る ---
        gate_ok = {"name": "inspection", "exit": 0, "source": "reports/r.md", "verdict": "ACCEPT", "range": "是正確認+回帰"}
        def prod(eco_, gates):
            p_ = witmod.default_path(git_dir, eco_)
            rc_p, m_p, _ = witmod.produce(root, eco_, gates, "NONE", p_, "selftest")
            if rc_p != 0:
                fails.append(f"R11 fixture produce {eco_}: {m_p}")
        def r11(name, eco_, gates, want_rc, want_dec, want_delivery, want_stop=None):
            prod(eco_, gates)
            rc_x, out_x = call([eco_, "--ledger", str(ledger)])
            d_x = last_rec()
            if rc_x != want_rc or d_x.get("decision") != want_dec or d_x.get("delivery") != want_delivery or (want_stop and d_x.get("stop_type") != want_stop):
                fails.append(f"{name}: exit {rc_x} / {d_x.get('decision')} / {d_x.get('stop_type')} / {d_x.get('delivery')} :: {out_x[:1]}")
            return d_x, out_x
        d_a, o_a = r11("insp-verified-gate-ok", "ECO-904", [{"name": "g", "exit": 0, "source": "x"}, gate_ok], 0, "ADVANCE", "next")
        if not ((d_a.get("inspection") or {}).get("required") is True and (d_a.get("inspection") or {}).get("gate", {}).get("exit") == 0):
            fails.append(f"insp-verified-gate-ok: 台帳の inspection 記録が不正: {d_a.get('inspection')}")
        d_b, o_b = r11("insp-verified-gate-missing", "ECO-904", [{"name": "g", "exit": 0, "source": "x"}], 1, "STOP", "operator", "INSPECTION_MISSING")
        if not o_b or "INSPECTION_MISSING" not in o_b[0]:
            fails.append(f"insp-verified-gate-missing: 判定行に INSPECTION_MISSING がない: {o_b[:1]}")
        d_c, _ = r11("insp-verified-gate-fail", "ECO-904", [{"name": "g", "exit": 0, "source": "x"}, dict(gate_ok, exit=1, verdict="REJECT")], 1, "STOP", "factory", "VERIFICATION_FAIL")
        if ((d_c.get("inspection") or {}).get("gate") or {}).get("exit") != 1:   # r1 IA-05: 失敗した gate も記録される
            fails.append(f"insp-verified-gate-fail: 失敗時の inspection 記録なし: {d_c.get('inspection')}")
        r11("insp-verified-gate-unmeasurable", "ECO-904", [{"name": "g", "exit": 0, "source": "x"}, dict(gate_ok, exit=2, range="境界探索")], 1, "STOP", "factory", "VERIFICATION_FAIL")
        d_e, _ = r11("insp-verified-no-inspector", "ECO-905", [{"name": "g", "exit": 0, "source": "x"}], 0, "ADVANCE", "next")
        if (d_e.get("inspection") or {}).get("required") is not False:
            fails.append(f"insp-verified-no-inspector: required が False でない: {d_e.get('inspection')}")
        # 非 verified+inspector(ECO-900)は gate 不要(既存の known-good 腕が ADVANCE している= 後方互換)
        wpath.write_text(json.dumps(good), encoding="utf-8")
        d_f, _ = r11("insp-decided-inspector", "ECO-900", good["gates"], 0, "ADVANCE", "next")
        # 台帳の形(全レコードに event・decision 行に verifier_line と decision)
        recs = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines()]
        decs = [r for r in recs if r.get("event") == "decision"]
        if len(decs) < 10 or any("verifier_line" not in r or "decision" not in r or "executor" not in r or "independence" not in r for r in decs) or any("event" not in r for r in recs):
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
    return "ADVANCE OK: selftest PASS(起動4/dry2/kb5/job1/不能3/独立性9/報告27/gate6/構文5/台帳3/引数13/表)"


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
