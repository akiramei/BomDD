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
#  R12 必須の検査の結果を昇格判定が読む(ECO-112 G1-G4): job.state が verified のとき、witness の ADVANCE と R11 の後に、register の
#     required_gates(order の required_gates: 行と一致することを bomdd-job が保証)の各 ID が witness の gate 名と完全一致すること。欄なし/空=
#     UNMEASURABLE GATES_UNDECLARED、欠け= UNMEASURABLE REQUIRED_GATE_MISSING(ID を名指し)。読むのは申告の exit(G4・W2)— 再実行しない。
#     判定レコードに required_gates と matched_gates。verified 以外では照合しない(製造・検査の cell は gate が揃う前に起動する)。
#  R13 ブリーフ(ECO-112 B1-B5): --brief PATH|none は --cell と組で必須(既存の引数検査のすべての後)・none と --report は組めない。ADVANCE の
#     起動でだけ <git-common-dir>/bomdd-run/briefs/<ECO>/<sha256> に置く(CR を含むものは BRIEF_NOT_LF・既存は再ハッシュ・一時ファイル+os.replace・
#     再読込で照合)。判定レコードに brief {path, sha256, size, store_ref}(store_ref= 保管用の写し)。cell には store_ref を渡さず、一時ディレクトリの
#     実行用コピーを BOMDD_BRIEF に渡す(書いて再ハッシュ・cell の終了後か起動しなかったときに消す・r1 IA-02)。保管の後に実行用コピーか判定レコードが
#     失敗したら、この呼び出しが作った保管用の写しだけを取り除く(取り除けなければ 2 行目に brief left in store・exit 2・r1 IA-01)。ストアの
#     ファイルは「保存された」ブリーフで、起動の有無は台帳(ADVANCE の判定レコードと cell レコード)で読む。昇格判定(R12 の後)はストアの各ブリーフが
#     束縛された tree の bomdd/reports/ に同じ sha256 で在ることを要求(BRIEF_NOT_COMMITTED・BRIEF_STORE_FAILED)し brief_copies を記録する。
#  R14 入口自身の理由(ECO-112 O1): entry_code 欄(code 欄は witness の CODE のまま)と 1 行目のタグ。
#  R15 実行中の起動(ECO-113 X/W/J/R/A/S/O — 規則の正本は order §1。ここは所在の索引):
#     X 排他= <git-common-dir>/bomdd-run/<ECO>.lock の OS ロック(msvcrt.locking LK_NBLCK / flock LOCK_NB)。衝突だけが ENTRY_ALIVE、
#       それ以外の失敗は LOCK_UNAVAILABLE。起動は戻るまで・回復は全体・dry は分類のあいだだけ保持する。
#     W 所有(Windows)= cell を CREATE_SUSPENDED で起動し、名前つきの kill-on-close Job Object へハンドルで入れてから再開する。入口は
#       job の外。入口が唯一のハンドルを持ち、run() のどの出口でも閉じる(閉じれば OS が job の全プロセスを終わらせる)。POSIX は job なし。
#     J 判定= run journal <git-common-dir>/bomdd-run/<ECO>.runs.jsonl の開いた実行(start があり end/abort/release がない)を job の存在で
#       ABNORMAL_END / CELL_ALIVE / UNKNOWN に、壊れた行を JOURNAL_CORRUPT に分類する(最も厳しいものを報告・pid は使わない)。
#     R 回復= --release RUN_ID --by EQ-NNN / --quarantine-journal --by EQ-NNN(人の行為を記録するだけ・何も止めない)。
#     A 記録= journal は 1 レコード 1 行・1 回の os.write・binary・fsync・ロック下。末尾の切れた行は無いものとし次の書き手が切り詰めて
#       repair を記録する。台帳の追記は <台帳>.lock の短い OS ロック(10 秒)の下。
#     S 起動の順= 引数検査(台帳パスを含む)→ ロック → 分類 → --report の再検査 → decide() → job・start・判定レコード・1 行目・再開・待機。
#       decide() の前の拒否は停止種別 RUN_IN_FLIGHT(order S4 の表)。
#     O 終了コード= O1。run() の外へ出た想定外の例外は INTERNAL_ERROR(exit 2・O3)。
#
# 使い方:
#   python bomdd-run.py ECO-067                      # dry: 検証+台帳
#   python bomdd-run.py ECO-067 --cell "codex exec ..." --executor EQ-002   # ADVANCE かつ独立なときだけ起動
#   python bomdd-run.py ECO-067 --cell "codex exec -o bomdd/reports/x.md ..." --executor EQ-002 --report bomdd/reports/x.md
#   python bomdd-run.py ECO-067 --ledger PATH         # 台帳の場所(作業木外のみ)
#   python bomdd-run.py ECO-067 --release RUN_ID --by EQ-003      # 開いた実行を閉じる(人が、その実行のプロセスが無いと表明する)
#   python bomdd-run.py ECO-067 --quarantine-journal --by EQ-003  # journal の壊れた行を以後の読み取りから外す(何も動かさない)
#   python bomdd-run.py --selftest                    # known-good 1 腕は起動し known-bad 腕は起動しない(痕跡で判定)
#
# 検出力の限界(宣言):
#   (1) 起動先が何をするかは責務外(製造セルの契約)。台帳に残すのは起動した事実と終了コードのみ。
#   (2) receipt の申告値(gates.exit)は再実測しない(bomdd-witness W2 と同じ)。
#   (3) 承認の有無は起動先ハーネスの設定に依存する — 本ツールは承認を作らない・迂回もしない。

import errno
import hashlib
import importlib.util
import io
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

IS_WIN = os.name == "nt"
if IS_WIN:
    import ctypes
    import ctypes.wintypes as _wt
    import msvcrt
else:  # pragma: no cover - POSIX branch (ECO-113 L1)
    import fcntl

TOOLS_DIR = Path(__file__).resolve().parent
ECO_RE = re.compile(r"^(ECO|CAPA)-[A-Za-z0-9]+(-[A-Za-z0-9]+)*$")   # r1 IA-01: 区切り文字・親参照を含まない
WIDTH = 80
KNOWN_OPTS = ("--cell", "--ledger", "--executor", "--report", "--range", "--brief")
SHA_NAME_RE = re.compile(r"^[0-9a-f]{64}$")   # ECO-112 B2/B4: ストアのファイル名= 内容の sha256
REPORTS_PREFIX = "bomdd/reports/"              # ECO-112 B4: ブリーフの恒久の置き場(束縛された tree の中)
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
    "RUN_IN_FLIGHT": "operator",       # R15(ECO-113 O2): 実行中の起動・終わりを記録しない実行・journal の欠陥
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


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_common_dir(root: Path, witmod) -> Path | None:
    """ECO-112 B2: `git rev-parse --git-common-dir`(worktree が複数でも 1 つ)。導出不能= None。"""
    r = witmod._git(root, "rev-parse", "--git-common-dir")
    if getattr(r, "returncode", 1) != 0 or not (r.stdout or "").strip():
        return None
    p = Path(r.stdout.strip())
    return (p if p.is_absolute() else (root / p)).resolve()


def brief_store_dir(common: Path, eco: str) -> Path:
    return common / "bomdd-run" / "briefs" / eco


def store_brief(root: Path, common: Path | None, eco: str, brief: str) -> tuple[dict | None, str | None, str, bool]:
    """ECO-112 B2/B3: ブリーフを内容アドレスのストアへ置く。(record, entry_code, message, created)。失敗= (None, code, 理由, created)。
    created= この呼び出しが最終名を作った(見たとき無く、自分の os.replace が置いた)— r1 IA-01 のロールバックが取り除いてよいのはこれだけ。"""
    src = Path(brief)
    src = src if src.is_absolute() else root / src
    try:
        data = src.read_bytes()
    except OSError as e:
        return None, "BRIEF_UNREADABLE", f"ブリーフを読めない({e.__class__.__name__}): {_short_path(src)}", False
    if b"\r" in data:   # 本リポは `* text=auto eol=lf` — CRLF のブリーフは別のバイトで commit される
        return None, "BRIEF_NOT_LF", f"ブリーフに CR がある(LF に限る): {_short_path(src)}", False
    sha = _sha(data)
    if common is None:
        return None, "BRIEF_STORE_FAILED", "git の共通ディレクトリを導出できない", False
    d = brief_store_dir(common, eco)
    final = d / sha
    created = False
    try:
        d.mkdir(parents=True, exist_ok=True)
        if final.exists():
            if _sha(final.read_bytes()) != sha:
                return None, "BRIEF_STORE_FAILED", f"ストアの既存ファイルが名前と一致しない: {sha[:12]}", False
        else:
            tmp = d / f".tmp-{os.urandom(6).hex()}"
            tmp.write_bytes(data)
            try:
                os.replace(tmp, final)
                created = True
            except OSError:
                try:
                    tmp.unlink()
                except OSError:
                    pass
                if not (final.exists() and _sha(final.read_bytes()) == sha):   # 同じバイトを並行に置いた場合だけ受け入れる
                    return None, "BRIEF_STORE_FAILED", f"ストアへ置けない: {sha[:12]}", False
        if _sha(final.read_bytes()) != sha:
            return None, "BRIEF_STORE_FAILED", f"ストアの再読込が一致しない: {sha[:12]}", created
    except OSError as e:
        return None, "BRIEF_STORE_FAILED", f"ストアへ置けない({e.__class__.__name__}): {sha[:12]}", created
    return {"path": str(brief), "sha256": sha, "size": len(data), "store_ref": str(final)}, None, "", created


_exec_write = Path.write_bytes   # ECO-112 V2(g): selftest が実行用コピーの書き込み失敗を差し込む継ぎ目
_unlink_stored = os.unlink       # ECO-112 V2(h): selftest がロールバックの取り除き失敗を差し込む継ぎ目


def exec_copy(info: dict) -> tuple[str | None, str | None, str]:
    """ECO-112 B3(r1 IA-02): cell に渡す実行用コピー — 保管用の写しと同じバイトの別ファイル(新しい一時ディレクトリ・作業木とストアの外)。
    (path, dir, message)。失敗= (None, dir, 理由)— dir が作られていれば呼び出し側が消す。"""
    d = None
    try:
        d = tempfile.mkdtemp(prefix="bomdd-brief-")
        x = Path(d) / (Path(info["path"]).name or "brief")
        _exec_write(x, Path(info["store_ref"]).read_bytes())
        if _sha(x.read_bytes()) != info["sha256"]:
            return None, d, f"実行用コピーの再ハッシュが一致しない: {info['sha256'][:12]}"
        return str(x), d, ""
    except OSError as e:
        return None, d, f"実行用コピーを書けない({e.__class__.__name__}): {info['sha256'][:12]}"


def remove_exec_copy(d: str | None) -> None:
    """ECO-112 B3: 実行用コピーとそのディレクトリを消す(失敗は無視— OS の一時領域が持つ)。"""
    if d:
        shutil.rmtree(d, ignore_errors=True)


def rollback_brief(info: dict | None, created: bool) -> str | None:
    """ECO-112 B2(r1 IA-01): 起動しなかったとき、この呼び出しが作った保管用の写しだけを取り除く。取り除けなければ OS エラー名。"""
    if not (info and created):
        return None
    try:
        _unlink_stored(info["store_ref"])
    except FileNotFoundError:
        return None
    except OSError as e:
        return e.__class__.__name__
    return None


def committed_copies(root: Path, common: Path | None, eco: str, tree: str | None) -> tuple[dict, str | None, str]:
    """ECO-112 B4: ストアの各ブリーフが束縛された tree の bomdd/reports/ に同じ sha256 で在るか。(結果, entry_code, message)。"""
    out = {"copies": [], "ignored": []}
    if common is None or not tree:
        return out, "BRIEF_STORE_FAILED", "git の共通ディレクトリまたは tree を導出できない"
    d = brief_store_dir(common, eco)
    try:
        entries = sorted(d.iterdir(), key=lambda p: p.name)
    except FileNotFoundError:
        return out, None, ""   # この clone で保存されたブリーフはない(L4)
    except OSError as e:
        return out, "BRIEF_STORE_FAILED", f"ストアを列挙できない({e.__class__.__name__})"
    stored = {}
    for e in entries:
        if not SHA_NAME_RE.match(e.name):
            out["ignored"].append(e.name)
            continue
        try:
            data = e.read_bytes()
        except OSError as x:
            return out, "BRIEF_STORE_FAILED", f"ストアのファイルを読めない({x.__class__.__name__}): {e.name[:12]}"
        if _sha(data) != e.name:
            return out, "BRIEF_STORE_FAILED", f"ストアのファイルが名前と一致しない: {e.name[:12]}"
        stored[e.name] = len(data)
    if not stored:
        return out, None, ""
    try:
        ls = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "-l", tree, "--", REPORTS_PREFIX], capture_output=True)
    except OSError:
        return out, "BRIEF_STORE_FAILED", "git を起動できない"
    if ls.returncode != 0:
        return out, "BRIEF_STORE_FAILED", "git ls-tree が失敗した"
    found = {}
    sizes = set(stored.values())
    for raw in ls.stdout.decode("utf-8", errors="replace").splitlines():
        meta, _, path = raw.partition("\t")
        parts = meta.split()
        if len(parts) != 4 or parts[1] != "blob" or not parts[3].isdigit() or int(parts[3]) not in sizes:
            continue
        blob = subprocess.run(["git", "-C", str(root), "cat-file", "blob", parts[2]], capture_output=True)
        if blob.returncode == 0:
            found.setdefault(_sha(blob.stdout), []).append(path)
    missing = [s for s in stored if s not in found]
    for s in stored:
        for p in found.get(s, []):
            out["copies"].append({"sha256": s, "path": p, "tree": tree})
    if missing:
        return out, "BRIEF_NOT_COMMITTED", "commit 済みの写しがない: " + ",".join(s[:12] for s in missing)
    return out, None, ""


# --- ECO-113: 実行中の起動(X 排他 / W 所有 / J 判定 / R 回復 / A 記録)— 規則の正本は order §1 ---------------------------
RUN_IN_FLIGHT = "RUN_IN_FLIGHT"
# O1: decide() の前の拒否理由(S4 の表の行)→ (判定語, 終了コード)。REPORT_EXISTS は R10 の ARG_ERROR のまま(記録なし)。
IN_FLIGHT_VERDICT = {"ENTRY_ALIVE": ("STOP", 1), "ABNORMAL_END": ("STOP", 1), "CELL_ALIVE": ("STOP", 1),
                     "LOCK_UNAVAILABLE": ("UNMEASURABLE", 2), "JOURNAL_UNREADABLE": ("UNMEASURABLE", 2),
                     "UNKNOWN": ("UNMEASURABLE", 2), "JOURNAL_CORRUPT": ("UNMEASURABLE", 2)}
CLASS_ORDER = ("ABNORMAL_END", "UNKNOWN", "CELL_ALIVE", "JOURNAL_CORRUPT")   # J2: 後ほど厳しい(最も厳しいものを報告)
CLOSING_EVENTS = ("end", "abort", "release")   # J1: これのない start が開いた実行(interrupted は閉じない)
RECOVERY_OPTS = ("--release", "--quarantine-journal")   # R1
END_RETRIES = 3            # S1.6: end の commit の再試行回数
LEDGER_LOCK_SECONDS = 10   # A5
CREATE_SUSPENDED = 0x00000004
_O_LOCAL = (os.O_BINARY | os.O_NOINHERIT) if IS_WIN else os.O_CLOEXEC   # X2/A1: 子へ継承しない・改行を変換しない


def _oserr(e: OSError) -> str:
    return f"{e.__class__.__name__}({e.errno})" if getattr(e, "errno", None) is not None else e.__class__.__name__


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _checkpoint(name: str) -> None:
    """selftest の継ぎ目(V2(g)・V4(i)・V4(m)): 名前つきの地点で例外や競合を差し込む。本番では何もしない。"""
    return None


def _wait(proc) -> int:
    """S1.6 の待機(V4(h) の継ぎ目)。"""
    return proc.wait()


def _jread(path) -> bytes:
    """A2/A3 の読み取り(V4(o) の継ぎ目)。"""
    return Path(path).read_bytes()


_jwrite = os.write   # A1 の 1 回の書き込み(V4(a)(d)(e) の継ぎ目)
_win_branch = IS_WIN  # W6/V2(e): Windows の分岐を切った状態を selftest が作る継ぎ目

if IS_WIN:
    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _adv = ctypes.WinDLL("advapi32", use_last_error=True)
    for _n, _res, _args in (
            ("CreateJobObjectW", _wt.HANDLE, [ctypes.c_void_p, _wt.LPCWSTR]),
            ("SetInformationJobObject", _wt.BOOL, [_wt.HANDLE, ctypes.c_int, ctypes.c_void_p, _wt.DWORD]),
            ("AssignProcessToJobObject", _wt.BOOL, [_wt.HANDLE, _wt.HANDLE]),
            ("OpenJobObjectW", _wt.HANDLE, [_wt.DWORD, _wt.BOOL, _wt.LPCWSTR]),
            ("QueryInformationJobObject", _wt.BOOL, [_wt.HANDLE, ctypes.c_int, ctypes.c_void_p, _wt.DWORD, ctypes.c_void_p]),
            ("IsProcessInJob", _wt.BOOL, [_wt.HANDLE, _wt.HANDLE, ctypes.POINTER(_wt.BOOL)]),
            ("CloseHandle", _wt.BOOL, [_wt.HANDLE]),
            ("CreateToolhelp32Snapshot", _wt.HANDLE, [_wt.DWORD, _wt.DWORD]),
            ("OpenThread", _wt.HANDLE, [_wt.DWORD, _wt.BOOL, _wt.DWORD]),
            ("ResumeThread", _wt.DWORD, [_wt.HANDLE]),
            ("GetCurrentProcess", _wt.HANDLE, []),
            ("ProcessIdToSessionId", _wt.BOOL, [_wt.DWORD, ctypes.POINTER(_wt.DWORD)]),
            ("LocalFree", ctypes.c_void_p, [ctypes.c_void_p])):
        getattr(_k32, _n).restype, getattr(_k32, _n).argtypes = _res, _args
    for _n, _res, _args in (
            ("OpenProcessToken", _wt.BOOL, [_wt.HANDLE, _wt.DWORD, ctypes.POINTER(_wt.HANDLE)]),
            ("GetTokenInformation", _wt.BOOL, [_wt.HANDLE, ctypes.c_int, ctypes.c_void_p, _wt.DWORD, ctypes.POINTER(_wt.DWORD)]),
            ("ConvertSidToStringSidW", _wt.BOOL, [ctypes.c_void_p, ctypes.POINTER(_wt.LPWSTR)])):
        getattr(_adv, _n).restype, getattr(_adv, _n).argtypes = _res, _args

    class _BASIC(ctypes.Structure):   # JOBOBJECT_BASIC_LIMIT_INFORMATION
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64), ("LimitFlags", _wt.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t), ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", _wt.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", _wt.DWORD), ("SchedulingClass", _wt.DWORD)]

    class _EXT(ctypes.Structure):     # JOBOBJECT_EXTENDED_LIMIT_INFORMATION
        _fields_ = [("Basic", _BASIC), ("IoInfo", ctypes.c_uint64 * 6), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    class _ACCT(ctypes.Structure):    # JOBOBJECT_BASIC_ACCOUNTING_INFORMATION
        _fields_ = [("Times", ctypes.c_int64 * 4), ("TotalPageFaultCount", _wt.DWORD), ("TotalProcesses", _wt.DWORD),
                    ("ActiveProcesses", _wt.DWORD), ("TotalTerminatedProcesses", _wt.DWORD)]

    class _THREADENTRY32(ctypes.Structure):
        _fields_ = [("dwSize", _wt.DWORD), ("cntUsage", _wt.DWORD), ("th32ThreadID", _wt.DWORD), ("th32OwnerProcessID", _wt.DWORD),
                    ("tpBasePri", _wt.LONG), ("tpDeltaPri", _wt.LONG), ("dwFlags", _wt.DWORD)]

    _k32.Thread32First.restype = _k32.Thread32Next.restype = _wt.BOOL
    _k32.Thread32First.argtypes = _k32.Thread32Next.argtypes = [_wt.HANDLE, ctypes.POINTER(_THREADENTRY32)]
    _INVALID_HANDLE = ctypes.c_void_p(-1).value


def _winerr(where: str) -> OSError:
    code = ctypes.get_last_error()
    return OSError(errno.EIO, f"{where} failed (winerror {code})")


def _job_create(name: str):
    """W1: 名前つきの job を作る。同名が既にあれば(別の実行のもの)失敗にする。"""
    ctypes.set_last_error(0)
    h = _k32.CreateJobObjectW(None, name)
    if not h:
        raise _winerr("CreateJobObjectW")
    if ctypes.get_last_error() == 183:   # ERROR_ALREADY_EXISTS
        _k32.CloseHandle(h)
        raise OSError(errno.EEXIST, "job name already exists")
    return h


def _job_configure(h) -> None:
    """W1: JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE だけを立てる(breakaway は許さない)。"""
    ext = _EXT()
    ext.Basic.LimitFlags = 0x00002000
    if not _k32.SetInformationJobObject(h, 9, ctypes.byref(ext), ctypes.sizeof(ext)):
        raise _winerr("SetInformationJobObject")


def _job_assign(h, proc) -> None:
    """W2: Popen が持つプロセスのハンドルで job に入れる(pid では入れない)。"""
    if not _k32.AssignProcessToJobObject(h, int(proc._handle)):
        raise _winerr("AssignProcessToJobObject")


def _snapshot_threads(pid: int) -> list:
    """W2 の再開だけが使う: そのプロセスのスレッド ID(入口がハンドルを持つあいだ pid は再利用されない)。判定では使わない。"""
    snap = _k32.CreateToolhelp32Snapshot(0x00000004, 0)   # TH32CS_SNAPTHREAD
    if not snap or snap == _INVALID_HANDLE:
        raise _winerr("CreateToolhelp32Snapshot")
    tids = []
    try:
        te = _THREADENTRY32()
        te.dwSize = ctypes.sizeof(te)
        ok = _k32.Thread32First(snap, ctypes.byref(te))
        while ok:
            if te.th32OwnerProcessID == pid:
                tids.append(te.th32ThreadID)
            ok = _k32.Thread32Next(snap, ctypes.byref(te))
    finally:
        _k32.CloseHandle(snap)
    return tids


def _job_resume(proc) -> None:
    """S1.5: 停止状態で作った cell のスレッドを再開する。1 本も再開できなければ失敗(S2)。"""
    tids = _snapshot_threads(proc.pid)
    if not tids:
        raise OSError(errno.ESRCH, "no thread to resume")
    for tid in tids:
        th = _k32.OpenThread(0x0002, False, tid)   # THREAD_SUSPEND_RESUME
        if not th:
            raise _winerr("OpenThread")
        try:
            if _k32.ResumeThread(th) == 0xFFFFFFFF:
                raise _winerr("ResumeThread")
        finally:
            _k32.CloseHandle(th)


def _job_close(h) -> None:
    """W3: 唯一のハンドルを閉じる — OS が job に残る全プロセスを終わらせ、job は無くなる。"""
    _k32.CloseHandle(h)


def _job_query(name: str) -> tuple[str, int | None]:
    """J2: job の存在だけを見る。("gone", None) / ("active", 稼働プロセス数) / ("error", winerror)。"""
    h = _k32.OpenJobObjectW(0x0004, False, name)   # JOB_OBJECT_QUERY
    if not h:
        code = ctypes.get_last_error()
        return ("gone", None) if code == 2 else ("error", code)   # ERROR_FILE_NOT_FOUND
    try:
        a = _ACCT()
        if not _k32.QueryInformationJobObject(h, 1, ctypes.byref(a), ctypes.sizeof(a), None):
            return "error", ctypes.get_last_error()
        return "active", int(a.ActiveProcesses)
    finally:
        _k32.CloseHandle(h)


def _in_job(name: str) -> bool | None:
    """V2(g): この(呼び出し側の)プロセスがその job に入っているか。開けなければ None。"""
    h = _k32.OpenJobObjectW(0x0004, False, name)
    if not h:
        return None
    try:
        res = _wt.BOOL()
        if not _k32.IsProcessInJob(_k32.GetCurrentProcess(), h, ctypes.byref(res)):
            return None
        return bool(res.value)
    finally:
        _k32.CloseHandle(h)


def _appcontainer() -> str | None:
    """W5: トークンの AppContainer SID(AppContainer でなければ "none")。読めなければ None。"""
    tok = _wt.HANDLE()
    if not _adv.OpenProcessToken(_k32.GetCurrentProcess(), 0x0008, ctypes.byref(tok)):   # TOKEN_QUERY
        return None
    try:
        flag, ret = _wt.DWORD(), _wt.DWORD()
        if not _adv.GetTokenInformation(tok, 29, ctypes.byref(flag), ctypes.sizeof(flag), ctypes.byref(ret)):   # TokenIsAppContainer
            return None
        if not flag.value:
            return "none"
        need = _wt.DWORD()
        _adv.GetTokenInformation(tok, 31, None, 0, ctypes.byref(need))   # TokenAppContainerSid
        buf = ctypes.create_string_buffer(max(need.value, 8))
        if not _adv.GetTokenInformation(tok, 31, buf, need.value, ctypes.byref(need)):
            return None
        psid = ctypes.c_void_p.from_buffer(buf).value
        s = _wt.LPWSTR()
        if not psid or not _adv.ConvertSidToStringSidW(psid, ctypes.byref(s)):
            return None
        try:
            return s.value
        finally:
            _k32.LocalFree(s)
    finally:
        _k32.CloseHandle(tok)


def _identity() -> dict:
    """W5: 名前空間の鍵(host・Windows session・AppContainer)。読めない値は None(判定で UNKNOWN)。"""
    host = platform.node() or None
    if not IS_WIN:
        return {"host": host, "session": None, "appcontainer": None}
    sess = _wt.DWORD()
    session = int(sess.value) if _k32.ProcessIdToSessionId(os.getpid(), ctypes.byref(sess)) else None
    return {"host": host, "session": session, "appcontainer": _appcontainer()}


def run_dir(common: Path) -> Path:
    return common / "bomdd-run"


def lock_file(common: Path, eco: str) -> Path:
    return run_dir(common) / f"{eco}.lock"   # X1: clone ごとに 1 つ(--ledger・worktree に依らない)・消さない


def journal_file(common: Path, eco: str) -> Path:
    return run_dir(common) / f"{eco}.runs.jsonl"   # J1


def acquire_lock(common: Path | None, eco: str) -> tuple[int | None, str | None, str | None]:
    """X2: (fd, cause, error)。ロック呼び出しの衝突だけが ENTRY_ALIVE。os.open・ディレクトリ・その他の失敗は LOCK_UNAVAILABLE。"""
    if common is None:
        return None, "LOCK_UNAVAILABLE", "git"
    p = lock_file(common, eco)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(p), os.O_RDWR | os.O_CREAT | _O_LOCAL, 0o666)
    except OSError as e:
        return None, "LOCK_UNAVAILABLE", _oserr(e)
    try:
        if IS_WIN:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:  # pragma: no cover
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        os.close(fd)
        conflict = (e.errno == errno.EACCES) if IS_WIN else (e.errno in (errno.EWOULDBLOCK, errno.EAGAIN))
        return None, ("ENTRY_ALIVE" if conflict else "LOCK_UNAVAILABLE"), _oserr(e)
    return fd, None, None


def release_lock(fd: int | None) -> None:
    """X3: ハンドルを閉じれば OS が解放する(Windows は先に明示で解く)。"""
    if fd is None:
        return
    try:
        if IS_WIN:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    except OSError:
        pass
    finally:
        os.close(fd)


def _jline(rec: dict) -> bytes:
    return (json.dumps(rec, ensure_ascii=True) + "\n").encode("ascii")   # A1: 1 レコード= 1 行(U+2028 等もエスケープ)


def _write_line(fd: int, line: bytes) -> None:
    n = _jwrite(fd, line)
    if n != len(line):   # A1: 短い書き込みは失敗
        raise OSError(errno.EIO, f"short write {n}/{len(line)}")


def journal_commit(path: Path, rec: dict) -> str | None:
    """A1/A2: 1 回の os.write+fsync(binary・継承しない・追記)。末尾の切れた行は先に切り詰めて repair を記録する。失敗= 理由。ロック下でだけ呼ぶ。"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = _jread(path)
        except FileNotFoundError:
            data = b""
        keep = data.rfind(b"\n") + 1
        torn = data[keep:]
        fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT | _O_LOCAL, 0o666)
        try:
            if torn:
                os.ftruncate(fd, keep)
                _write_line(fd, _jline({"event": "repair", "eco": rec.get("eco"), "truncated_bytes": len(torn), "sha256": _sha(torn), "at": _now()}))
            _write_line(fd, _jline(rec))
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError as e:
        return _oserr(e)
    return None


def journal_read(path: Path) -> tuple[list | None, bytes, list, list, str | None]:
    """A2/A3/A4: (records [(offset, rec)], torn tail, corrupt [(offset, bytes)], excluded [(offset, bytes)], error)。
    b"\\n" だけで分ける。改行のない最後の区間は無いものとする。quarantine の offset より前の壊れた行は以後読まない(R3)。
    存在しない journal はレコードなし。存在して読めない(OSError)は error(JOURNAL_UNREADABLE)。"""
    try:
        data = _jread(path)
    except FileNotFoundError:
        return [], b"", [], [], None
    except OSError as e:
        return None, b"", [], [], _oserr(e)
    parts = data.split(b"\n")
    recs, bad, pos = [], [], 0
    for seg in parts[:-1]:
        try:
            r = json.loads(seg.decode("ascii"))
            if not isinstance(r, dict):
                raise ValueError("not an object")
            recs.append((pos, r))
        except ValueError:   # UnicodeDecodeError と JSONDecodeError を含む
            bad.append((pos, seg + b"\n"))
        pos += len(seg) + 1
    qoff = max((r["offset"] for _, r in recs if r.get("event") == "quarantine" and isinstance(r.get("offset"), int)), default=-1)
    return recs, parts[-1], [b for b in bad if b[0] >= qoff], [b for b in bad if b[0] < qoff], None


def open_runs(recs: list) -> list:
    """J1: start があり、その run_id の end / abort / release がない実行(journal の順)。"""
    starts, closed = {}, set()
    for _, r in recs:
        rid = r.get("run_id")
        if not isinstance(rid, str):
            continue
        if r.get("event") == "start":
            starts.setdefault(rid, r)
        elif r.get("event") in CLOSING_EVENTS:
            closed.add(rid)
    return [r for rid, r in starts.items() if rid not in closed]


def classify_run(start: dict, ident: dict) -> tuple[str, str]:
    """J2: 開いた実行 1 件の分類と理由。入口はもう居ない(居れば X2 が拒否した)— job の存在だけで判定し、pid は使わない。"""
    if not _win_branch:
        return "UNKNOWN", "POSIX"
    for k in ("host", "session", "appcontainer"):
        if start.get(k) is None or ident.get(k) is None or start.get(k) != ident.get(k):
            return "UNKNOWN", k
    name = start.get("job_name")
    if not isinstance(name, str) or not name:
        return "UNKNOWN", "job query error"
    state, n = _job_query(name)
    if state == "gone":
        return "ABNORMAL_END", "job not found"
    if state == "error":
        return "UNKNOWN", "job query error"
    return ("ABNORMAL_END", "job empty") if n == 0 else ("CELL_ALIVE", f"job active {n}")


def judge(recs: list, corrupt: list, ident: dict) -> tuple[str | None, dict, str | None, list]:
    """J2: (報告する理由, S4 の行の追加欄, 行に出す run_id, 分類済みの開いた実行)。開いた実行はすべて分類し、最も厳しいものを報告する。"""
    runs = []
    for s in open_runs(recs):
        cls, because = classify_run(s, ident)
        runs.append({"run_id": s["run_id"], "class": cls, "because": because})
    listed = [{"run_id": r["run_id"], "class": r["class"]} for r in runs]
    if corrupt:
        return "JOURNAL_CORRUPT", {"corrupt_offset": corrupt[0][0], "open_runs": listed}, None, runs
    if not runs:
        return None, {}, None, runs
    cause = max((r["class"] for r in runs), key=CLASS_ORDER.index)
    first = runs[0] if cause == "ABNORMAL_END" else next(r for r in runs if r["class"] == cause)
    extra = {"open_runs": listed}
    if cause == "UNKNOWN":
        extra["unknown_because"] = first["because"]
    return cause, extra, first["run_id"], runs


def in_flight_line(eco: str, cause: str, rid: str | None = None) -> str:
    """S4: `<VERDICT> <ECO> RUN_IN_FLIGHT(<cause>) <run_id or -> → operator`(80 桁以内)。"""
    return _fit(f"{IN_FLIGHT_VERDICT[cause][0]} {eco} {RUN_IN_FLIGHT}({cause}) {rid or '-'} → {DELIVERY[RUN_IN_FLIGHT]}")


def _blank_rec(eco: str, executor: str | None) -> dict:
    """台帳の判定レコードの形(decide() と S4 の拒否で同じ)。"""
    return {"event": "decision", "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"), "eco": eco,
            "receipt": None, "job_state": None, "job_stop_type": None, "verifier_line": None, "verifier_exit": None,
            "code": None, "decision": None, "stop_type": None, "delivery": None, "cell": None, "tree": None,
            "executor": executor, "producer": None, "independence": None, "report": None, "inspection": None,
            "entry_code": None, "entry_detail": None, "required_gates": None, "matched_gates": None, "brief": None,
            "brief_copies": None, "brief_store_ignored": None}


def in_flight_rec(eco: str, executor: str | None, cause: str, extra: dict) -> dict:
    """S4: 拒否の判定レコード — decision(O1)・stop_type RUN_IN_FLIGHT・cause と、その行の追加欄だけ。"""
    rec = _blank_rec(eco, executor)
    rec.update(decision=IN_FLIGHT_VERDICT[cause][0], stop_type=RUN_IN_FLIGHT, delivery=DELIVERY[RUN_IN_FLIGHT], cause=cause)
    rec.update(extra)
    return rec


def decide(root: Path, eco: str, jobmod, witmod, executor: str | None = None) -> tuple[dict, dict | None]:
    """R1〜R3・R6・R9: 判定レコード(台帳 1 行目の元)。起動はしない。"""
    rec = _blank_rec(eco, executor)
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
    if rec["job_state"] == "verified":   # ECO-112 G3: 昇格判定は必須の検査 ID の結果を名前で読む(R11 の後・申告の exit を読む= G4)
        def _unmeasurable(code, detail):
            rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery=DELIVERY["MISSING_INPUT"],
                       entry_code=code, entry_detail=detail)
            return rec, job
        required = _job_value(job, "required_gates")
        rec["required_gates"] = required
        if not required:
            return _unmeasurable("GATES_UNDECLARED", "register に required_gates がない")
        try:
            names = {g.get("name") for g in (json.loads(path.read_text(encoding="utf-8")).get("gates") or []) if isinstance(g, dict)}
        except (OSError, ValueError):
            names = set()
        rec["matched_gates"] = [i for i in required if i in names]
        missing = [i for i in required if i not in names]
        if missing:
            return _unmeasurable("REQUIRED_GATE_MISSING", ",".join(missing))
        common = git_common_dir(root, witmod)   # ECO-112 B4: ストアの各ブリーフが束縛された tree に commit 済みで在る
        res, bcode, bmsg = committed_copies(root, common, eco, rec["tree"])
        rec["brief_copies"], rec["brief_store_ignored"] = res["copies"], res["ignored"]
        if bcode:
            return _unmeasurable(bcode, bmsg)
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


def cell_env(rec: dict, job: dict, root: Path, report: str | None = None, rng: str | None = None,
             exec_brief: str | None = None) -> tuple[dict, str]:
    """R5/R10: cell の環境(job/witness/executor/report/brief)と job ビューの一時ファイル。コマンドは加工しない・承認は起動先。"""
    with tempfile.NamedTemporaryFile("w", suffix=".json", prefix="bomdd-job-", delete=False, encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
        job_json = f.name
    env = dict(os.environ, BOMDD_JOB=rec["eco"], BOMDD_JOB_JSON=job_json, BOMDD_WITNESS=rec["receipt"], BOMDD_EXECUTOR=rec.get("executor") or "",
               BOMDD_REPORT=report or "", BOMDD_RANGE=rng or "",
               BOMDD_BRIEF=exec_brief or "")   # ECO-112 B3(r1 IA-02): 実行用コピー(store_ref は渡さない・none なら空)
    return env, job_json


def cell_record(rec: dict, cell: str) -> dict:
    """台帳 2 行目(event= cell)の形。journal_end は ECO-113 S1.6 で足した 1 欄。"""
    return {"event": "cell", "run_id": rec["run_id"], "eco": rec["eco"], "cell": cell, "executor": rec.get("executor"),
            "started_at": None, "cell_exit": None, "report": None, "journal_end": None}


def _ledger_lock(path: Path) -> int:
    """A5: <台帳>.lock の短い排他(Windows LK_LOCK は 1 秒ごと 10 回で EDEADLK・POSIX は 10 秒まで再試行)。失敗は OSError。"""
    fd = os.open(str(path) + ".lock", os.O_RDWR | os.O_CREAT | _O_LOCAL, 0o666)
    try:
        if IS_WIN:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
        else:  # pragma: no cover
            deadline = time.monotonic() + LEDGER_LOCK_SECONDS
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError as e:
                    if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN) or time.monotonic() > deadline:
                        raise
                    time.sleep(0.05)
    except OSError:
        os.close(fd)
        raise
    return fd


def write_ledger(path: Path, rec: dict) -> str | None:
    """R4: 追記のみ(A5: 追記ごとに台帳の短い OS ロックを持つ)。失敗は理由文字列(exit 2 側)。"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = _ledger_lock(path)
        try:
            with path.open("a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        finally:
            release_lock(fd)
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
    if rec.get("entry_code"):   # ECO-112 O1: 入口自身の理由(witness の OK と読ませない・code 欄は witness のまま)
        tag = rec["entry_code"] + (f"({rec['entry_detail']})" if rec["entry_code"] == "REQUIRED_GATE_MISSING" and rec.get("entry_detail") else "")
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
    """入口本体。emit(line) で標準出力の各行を出す(1 行目= 判定行・R7)。返り値= 終了コード(R8・ECO-113 O1)。
    ECO-113 W3: job ができたら run() のどの出口でも(例外でも)ハンドルを閉じる。O3: 外へ出た想定外の例外は INTERNAL_ERROR・exit 2。"""
    emit = emit or (lambda s: None)
    st = {"job": None, "lock": None, "exec_dir": None, "job_json": None}
    try:
        try:
            return _run(argv, root, emit, st)
        finally:
            _teardown(st)
    except (Exception, KeyboardInterrupt) as e:   # O3: S3 の待機の外。台帳には書かない(台帳が失敗の原因でありうる)
        traceback.print_exc(file=sys.stderr)
        eco = argv[0] if argv and isinstance(argv[0], str) and ECO_RE.match(argv[0]) else "-"
        emit(_fit(f"UNMEASURABLE {eco} INTERNAL_ERROR({e.__class__.__name__}) → operator"))
        return 2


def _close_job(st: dict) -> None:
    """W3: job のハンドルを閉じる(1 回だけ)。"""
    h, st["job"] = st.get("job"), None
    if h is not None:
        _job_close(h)


def _teardown(st: dict) -> None:
    _close_job(st)
    if st.get("job_json"):
        try:
            os.unlink(st["job_json"])
        except OSError:
            pass
        st["job_json"] = None
    remove_exec_copy(st.get("exec_dir"))   # ECO-112 B3: 実行用コピーは出口で必ず消す
    st["exec_dir"] = None
    lk, st["lock"] = st.get("lock"), None
    release_lock(lk)


def _refuse(ledger: Path, eco: str, executor: str | None, cause: str, extra: dict, rid: str | None, emit) -> int:
    """S4: 拒否は判定レコード 1 件と 1 行。レコードが書けなければ既存の台帳失敗の行・exit 2(台帳の失敗が行の判定に勝つ)。"""
    err = write_ledger(ledger, in_flight_rec(eco, executor, cause, extra))
    if err:
        emit(_fit("UNMEASURABLE ARG_ERROR: " + err))
        return 2
    emit(in_flight_line(eco, cause, rid))
    return IN_FLIGHT_VERDICT[cause][1]


def _run(argv: list, root: Path, emit, st: dict) -> int:
    if not argv or argv[0].startswith("--"):
        emit("UNMEASURABLE ARG_ERROR: ECO [--cell --executor --brief --report --range]")
        return 2
    eco = argv[0]
    if not ECO_RE.match(eco):   # r1 IA-01
        emit(_fit(f"UNMEASURABLE ARG_ERROR: ECO の構文不正(ECO-NNN / CAPA-NNN): {eco!r}"))
        return 2
    if any(a in RECOVERY_OPTS for a in argv[1:]):   # ECO-113 R1: 回復は別の経路(decide() を通らない・起動しない)
        return _recover(argv, eco, root, emit, st)
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
    _, git_dir, _ = witmod.worktree_tree(root)
    if report is not None:
        perr = _report_path_error(root, git_dir, report)
        if perr:
            emit(_fit("UNMEASURABLE ARG_ERROR: " + perr))
            return 2
        if (root / report).exists():   # r1 IA-02 / r2 IA-06: 既存物(ファイル・ディレクトリ)を今回の cell の報告と取り違えない(fail-closed)
            emit(_fit(f"UNMEASURABLE ARG_ERROR: --report の宛先が既に存在する: {report}"))
            return 2
    # ECO-113 S1: 台帳パスの導出と R4 の検査はロックの前へ(拒否は従来どおり・記録なし)
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
    # ECO-112 B1: --brief の検査は既存の引数検査のすべての後(欠けた --brief が他の引数の誤りを隠さない)
    brief = opts.get("--brief")
    if brief is not None and not cell:
        emit("UNMEASURABLE ARG_ERROR: --brief は --cell と組で指定する")
        return 2
    if cell and brief is None:
        emit("UNMEASURABLE ARG_ERROR: --cell には --brief PATH|none が必須")
        return 2
    if brief == "none" and report is not None:
        emit("UNMEASURABLE ARG_ERROR: --brief none は --report と組にできない")
        return 2
    # ECO-113 S1: ロック(X2)→ 分類(J2)。拒否は S4。
    _checkpoint("before_lock")
    common = git_common_dir(root, witmod)
    fd, cause, lerr = acquire_lock(common, eco)
    if cause:
        return _refuse(ledger, eco, executor, cause, {} if cause == "ENTRY_ALIVE" else {"lock_error": lerr}, None, emit)
    st["lock"] = fd
    jpath = journal_file(common, eco)
    recs, _torn, corrupt, _excluded, jerr = journal_read(jpath)
    if jerr:
        return _refuse(ledger, eco, executor, "JOURNAL_UNREADABLE", {"journal_error": jerr}, None, emit)
    ident = _identity()
    cause, extra, rid, _runs = judge(recs, corrupt, ident)
    if cause:
        return _refuse(ledger, eco, executor, cause, extra, rid, emit)
    if not cell:   # X3: dry は分類のあいだだけロックを持つ
        lk, st["lock"] = st["lock"], None
        release_lock(lk)
    if report is not None and (root / report).exists():   # S1: R10 の再検査(ロック下)— REPORT_EXISTS は ARG_ERROR のまま・記録なし
        emit(_fit(f"UNMEASURABLE ARG_ERROR: --report の宛先が既に存在する: {report}"))
        return 2
    rec, job = decide(root, eco, jobmod, witmod, executor)
    rec["report"] = report
    launching = rec["decision"] == "ADVANCE" and bool(cell)
    info, created, exec_path = None, False, None
    if launching:   # ECO-112 B2/B3: ADVANCE の後・判定レコードと起動の前にだけストアへ置く(拒否された起動は何も置かない)
        if brief == "none":
            rec["brief"] = "none"
        else:
            info, bcode, bmsg, created = store_brief(root, git_common_dir(root, witmod), eco, brief)
            if not bcode:   # B3(r1 IA-02): cell には実行用コピーを渡す。書けなければ BRIEF_STORE_FAILED(B2 のロールバック)
                exec_path, st["exec_dir"], xmsg = exec_copy(info)
                if exec_path is None:
                    bcode, bmsg = "BRIEF_STORE_FAILED", xmsg
            if bcode:
                rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery=DELIVERY["MISSING_INPUT"],
                           entry_code=bcode, entry_detail=bmsg)
                launching = False
            else:
                rec["brief"] = info
    win = _win_branch
    proc, env = None, None
    if launching:
        env, st["job_json"] = cell_env(rec, job, root, report, rng, exec_path)
        job_name = f"Local\\BomDD-run-{eco}-{rec['run_id']}" if win else None
        if win:   # S1.1: job を作り(W1)、cell を停止状態で起動してハンドルで入れる(W2)。失敗は W4
            try:
                st["job"] = _job_create(job_name)
                _job_configure(st["job"])
                sys.stdout.flush()
                proc = subprocess.Popen(cell, shell=True, cwd=str(root), env=env, creationflags=CREATE_SUSPENDED)
                try:
                    _job_assign(st["job"], proc)
                except OSError:
                    proc.kill()   # W4: 停止状態の cell は何も実行していない — ハンドルで終わらせる
                    proc.wait()
                    raise
            except OSError as e:
                _close_job(st)
                rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery=DELIVERY["MISSING_INPUT"],
                           entry_code="JOB_UNAVAILABLE", entry_detail=_oserr(e))
                launching, proc = False, None
            else:
                _checkpoint("assigned")
        if launching:   # S1.2: start を commit(A1)。失敗は JOURNAL_WRITE_FAILED
            start = {"event": "start", "eco": eco, "run_id": rec["run_id"], "job_name": job_name, "entry_pid": os.getpid(),
                     "host": ident["host"], "session": ident["session"], "appcontainer": ident["appcontainer"], "started_at": _now()}
            jw = journal_commit(jpath, start)
            if jw:
                _close_job(st)   # W3: OS が停止状態の cell を終わらせる
                rec.update(decision="UNMEASURABLE", stop_type="MISSING_INPUT", delivery=DELIVERY["MISSING_INPUT"],
                           entry_code="JOURNAL_WRITE_FAILED", entry_detail=jw)
                launching, proc = False, None
    if launching:
        rec["cell"] = cell
    left = None   # B2(r1 IA-01): 起動しないと決まったら、この呼び出しが作った保管用の写しだけを取り除き、実行用コピーを消す
    if not launching:
        remove_exec_copy(st["exec_dir"])
        st["exec_dir"] = None
        left = rollback_brief(info, created)
    err = write_ledger(ledger, rec)   # R4/r1 IA-02・S1.3: 判定レコードを起動の前に書く。書けなければ起動しない
    if err:
        if launching:   # S1.3 の失敗: job を閉じ(cell は再開前に終わる)、abort を commit
            _close_job(st)
            journal_commit(jpath, {"event": "abort", "eco": eco, "run_id": rec["run_id"], "reason": err, "at": _now()})
            remove_exec_copy(st["exec_dir"])
            st["exec_dir"] = None
            left = rollback_brief(info, created)
        emit(_fit("UNMEASURABLE ARG_ERROR: " + err))
        if left:
            emit(_fit(f"brief left in store: {info['sha256'][:12]} ({left})"))
        return 2
    _checkpoint("first_line")   # V4(m): S1.4 の中の地点
    emit(summary_line(rec, launching))   # R7/r1 IA-03・S1.4: 判定行を起動の前に出す
    if left:
        emit(_fit(f"brief left in store: {info['sha256'][:12]} ({left})"))
    if not launching:
        return {"ADVANCE": 0, "STOP": 1, "UNMEASURABLE": 2}[rec["decision"]]
    ev = cell_record(rec, cell)   # S1.5: ここより前に cell のプロセスは何も実行していない
    ev["started_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if win:
        try:
            _job_resume(proc)
        except OSError:   # S2: 再開の失敗 — job を閉じれば OS が停止状態の cell を終わらせる
            _close_job(st)
            ev["cell_exit"] = "RESUME_FAILED"
            jw = journal_commit(jpath, {"event": "end", "eco": eco, "run_id": rec["run_id"], "cell_exit": "RESUME_FAILED", "at": _now()})
            ev["journal_end"] = "failed" if jw else "committed"
            err2 = write_ledger(ledger, ev)
            emit(_fit("cell not started (RESUME_FAILED)" + (f" · 台帳追記失敗: {err2}" if err2 else "")))
            return 2
    else:   # S1.5(POSIX・W6): ここで Popen(job なし・停止状態なし)
        try:
            sys.stdout.flush()
            proc = subprocess.Popen(cell, shell=True, cwd=str(root), env=env)
        except OSError as e:
            proc, ev["cell_exit"] = None, f"OSError: {e.__class__.__name__}"
    _checkpoint("resumed")
    if proc is not None:
        try:
            ev["cell_exit"] = _wait(proc)
        except (Exception, KeyboardInterrupt):   # S3: 待機の中断 — 閉じない interrupted の記録・exit 2
            journal_commit(jpath, {"event": "interrupted", "eco": eco, "run_id": rec["run_id"], "at": _now()})
            ev.update(cell_exit="interrupted", journal_end="none")
            err2 = write_ledger(ledger, ev)
            emit(_fit("cell interrupted" + (f" · 台帳追記失敗: {err2}" if err2 else "")))
            _close_job(st)   # OS が cell のツリーを終わらせる。次回は ABNORMAL_END(J2)
            return 2
    _checkpoint("after_wait")
    jw = None
    for _attempt in range(1 + END_RETRIES):   # S1.6: end の commit(再試行 3 回)
        jw = journal_commit(jpath, {"event": "end", "eco": eco, "run_id": rec["run_id"], "cell_exit": ev["cell_exit"], "at": _now()})
        if not jw:
            break
    ev["journal_end"] = "failed" if jw else "committed"
    if report:   # R10: cell 終了後に報告を束ねる(cell が書いたものを読むだけ・解釈しない)
        ev["report"] = bind_report(root, report, rng)
    _checkpoint("cell_record")
    err2 = write_ledger(ledger, ev)
    _close_job(st)   # W3
    emit(_fit(f"cell exit {ev['cell_exit']}" + (f" · 台帳追記失敗: {err2}" if err2 else "")))
    if report is not None:   # R10: 判定語の回収を 1 行で(入口の exit は R8 のまま 0・判定で行動しない)
        rp = ev["report"] or {}
        sha = (rp.get("sha256") or "")[:12]
        emit(_fit(f"report {rp.get('verdict')} " + (f"sha256:{sha} " if sha else "(no file) ") + f"({rec.get('executor')})"))
    return 0


def _recover(argv: list, eco: str, root: Path, emit, st: dict) -> int:
    """ECO-113 R1-R5: --release RUN_ID --by EQ-NNN / --quarantine-journal --by EQ-NNN。decide() を通らず、起動せず、何も止めない。
    出口: 0= 閉じた・1= 拒否(ENTRY_ALIVE / CELL_ALIVE)・2= 測定不能・引数不正。台帳(--ledger)は使わない — 記録は journal だけ。"""
    rid, quar, by, other, i = None, False, None, [], 1
    while i < len(argv):
        a = argv[i]
        if a in ("--release", "--by"):
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                emit(f"UNMEASURABLE ARG_ERROR: {a} に値がない")
                return 2
            if (a == "--release" and rid is not None) or (a == "--by" and by is not None):
                emit(f"UNMEASURABLE ARG_ERROR: {a} が重複")
                return 2
            if a == "--release":
                rid = argv[i + 1]
            else:
                by = argv[i + 1]
            i += 2
            continue
        if a == "--quarantine-journal":
            if quar:
                emit("UNMEASURABLE ARG_ERROR: --quarantine-journal が重複")
                return 2
            quar = True
        else:
            other.append(a)
        i += 1
    if other:   # R1: 他のオプションと組めない(--cell・--executor・--report・--range・--ledger・--brief を含む)
        emit(_fit(f"UNMEASURABLE ARG_ERROR: 回復は --by のほかのオプションと組めない: {other[0]}"))
        return 2
    if rid is not None and quar:
        emit("UNMEASURABLE ARG_ERROR: --release と --quarantine-journal は同時に指定できない")
        return 2
    if by is None or not EQ_ID_RE.match(by):
        emit(_fit(f"UNMEASURABLE ARG_ERROR: 回復には --by EQ-NNN が必須(人の行為の記録): {by!r}"))
        return 2
    jobmod, witmod = _load("bomdd-job"), _load("bomdd-witness")
    eq, eq_err = jobmod.load_equipment(root)
    if eq is None:
        emit(_fit(f"UNMEASURABLE ARG_ERROR: 設備台帳を読めない: {eq_err}"))
        return 2
    ent = eq.get(by) or {}
    if ent.get("kind") != "human" or ent.get("status") != "active":   # R4: 自己申告
        emit(_fit(f"UNMEASURABLE ARG_ERROR: --by は kind: human・status: active の設備に限る: {by}"))
        return 2
    common = git_common_dir(root, witmod)
    fd, cause, _lerr = acquire_lock(common, eco)   # R2/R3: ロックを取る
    if cause:
        emit(in_flight_line(eco, cause))
        return IN_FLIGHT_VERDICT[cause][1]
    st["lock"] = fd
    jpath = journal_file(common, eco)
    recs, _torn, corrupt, _excluded, jerr = journal_read(jpath)
    if jerr:
        emit(in_flight_line(eco, "JOURNAL_UNREADABLE"))
        return 2
    _cause, _extra, _rid, runs = judge(recs, [], _identity())   # 解析できた開いた実行を分類し直す(J2)
    if quar:   # R3: 壊れた行を以後の解析から外す。何も動かさず消さない。CELL_ALIVE があるあいだは拒否
        if not corrupt:
            emit("UNMEASURABLE ARG_ERROR: 隔離する壊れた行がない")
            return 2
        alive = next((r for r in runs if r["class"] == "CELL_ALIVE"), None)
        if alive:
            emit(in_flight_line(eco, "CELL_ALIVE", alive["run_id"]))
            return 1
        offset = corrupt[-1][0] + len(corrupt[-1][1])   # この位置より前の壊れた行を外す
        q = {"event": "quarantine", "eco": eco, "offset": offset, "excluded_sha256": _sha(b"".join(b for _, b in corrupt)), "by": by, "at": _now()}
        if journal_commit(jpath, q):
            emit(_fit(f"UNMEASURABLE {eco} MISSING_INPUT(JOURNAL_WRITE_FAILED) → operator"))
            return 2
        emit(_fit(f"QUARANTINED {eco} {offset} (JOURNAL_CORRUPT) by {by}"))
        return 0
    if corrupt:   # 出口は R3(隔離)が先
        emit(in_flight_line(eco, "JOURNAL_CORRUPT"))
        return 2
    run_ = next((r for r in runs if r["run_id"] == rid), None)
    if run_ is None:
        emit(_fit(f"UNMEASURABLE ARG_ERROR: RUN_ID は開いている実行でない: {rid}"))
        return 2
    if run_["class"] == "CELL_ALIVE":   # R2: 拒否
        emit(in_flight_line(eco, "CELL_ALIVE", rid))
        return 1
    rel = {"event": "release", "eco": eco, "run_id": rid, "classified": run_["class"], "cause": run_["because"], "by": by, "at": _now()}
    if run_["class"] == "UNKNOWN":
        rel["cell"] = "unverified"   # 解放する人が、その実行のプロセスが動いていないと表明する
    if journal_commit(jpath, rel):
        emit(_fit(f"UNMEASURABLE {eco} MISSING_INPUT(JOURNAL_WRITE_FAILED) → operator"))
        return 2
    emit(_fit(f"RELEASED {eco} {rid} ({run_['class']}) by {by}"))
    return 0


# --- selftest: 一時 git リポ(実リポ非接触)で known-good は起動し known-bad は起動しない ---------------------
_CLEANUP_FAILS: list = []


class _FixtureDir(tempfile.TemporaryDirectory):
    """ECO-113 W3: 片付けの失敗(cell のプロセスが実行より長く生きてファイルを掴む)を traceback でなく selftest の所見にする。"""

    def __exit__(self, *exc):
        try:
            self.cleanup()
        except OSError as e:
            _CLEANUP_FAILS.append(f"fixture cleanup: {e.__class__.__name__} — cell のプロセスが実行より長く生きた(W3)")


def selftest() -> int:
    # ECO-068: selftest 自身の前提(OS temp・git)不在は traceback でなく UNMEASURABLE の 1 行・exit 2
    try:
        td_cm, wd_cm = _FixtureDir(), _FixtureDir()
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
        (root / "bomdd" / "closed-insp.md").write_text("# Change Order — ECO-904\n\n## 担当設備\n\n- producer: EQ-001\n- inspector: EQ-002\n\nrequired_gates: [g, inspection]\n\n## 6. クローズ(2026-09-12・verified)\n- PASS\n", encoding="utf-8")
        (root / "bomdd" / "nocap.md").write_text("# Change Order — ECO-903\n\n## 3. 受入\n- 検討中\n", encoding="utf-8")
        (root / "bomdd" / "closed.md").write_text("# Change Order — ECO-902\n\nrequired_gates: [g]\n\n## 6. クローズ(2026-09-03・verified)\n- PASS\n", encoding="utf-8")
        # ECO-112 G3/B4: verified の昇格判定の fixture(906= 集合 [V1, V2]・907= 欄なし・908= decided で集合あり・909= inspector なしで inspection を要求)
        (root / "bomdd" / "closed-g.md").write_text("# Change Order — ECO-906\n\nrequired_gates: [V1, V2]\n\n## 6. クローズ(2026-10-18・verified)\n- PASS\n", encoding="utf-8")
        (root / "bomdd" / "closed-nog.md").write_text("# Change Order — ECO-907\n\n## 6. クローズ(2026-10-18・verified)\n- PASS\n", encoding="utf-8")
        (root / "bomdd" / "open-g.md").write_text("# Change Order — ECO-908\n\n## 担当設備\n\n- producer: EQ-001\n\nrequired_gates: [V1, V2]\n\n## 3. 受入\n- 検討中\n", encoding="utf-8")
        (root / "bomdd" / "closed-gi.md").write_text("# Change Order — ECO-909\n\nrequired_gates: [inspection]\n\n## 6. クローズ(2026-10-18・verified)\n- PASS\n", encoding="utf-8")
        eqp = root / "bomdd" / "70-equipment.yaml"
        EQ_TXT = ("equipment:\n"
                  "  - {id: EQ-001, kind: ai-model, model: m1, harness: h1, account_lineage: a1}\n"
                  "  - {id: EQ-002, kind: ai-model, model: m2, harness: h2, account_lineage: a2}\n"
                  "  - {id: EQ-003, kind: ai-model, model: m1, harness: h1, account_lineage: a1}\n"
                  "  - {id: EQ-004, kind: ai-model, model: unknown, harness: h4, account_lineage: a4}\n"
                  "  - {id: EQ-005, kind: ai-model, model: m1, harness: h1, account_lineage: a5}\n"
                  "  - {id: EQ-006, kind: ai-model, model: M1, harness: '  h1  ', account_lineage: A1}\n"
                  "  - {id: EQ-007, kind: human, model: h7, harness: t7, account_lineage: p7, status: active}\n")   # ECO-113 R4: 回復の --by
        eqp.write_text(EQ_TXT, encoding="utf-8")
        reg = root / "bomdd" / "60-change-register.yaml"
        reg.write_text("changes:\n"
                       "  - {id: ECO-900, title: t, status: decided, order_ref: bomdd/open.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
                       "  - {id: ECO-902, title: t2, status: in-progress, order_ref: bomdd/closed.md, required_gates: [g]}\n"
                       "  - {id: ECO-903, title: t3, status: decided, order_ref: bomdd/nocap.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
                       "  - {id: ECO-904, title: t4, status: verified, order_ref: bomdd/closed-insp.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}, required_gates: [g, inspection]}\n"
                       "  - {id: ECO-905, title: t5, status: verified, order_ref: bomdd/closed.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}, required_gates: [g]}\n"
                       "  - {id: ECO-906, title: t6, status: verified, order_ref: bomdd/closed-g.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}, required_gates: [V1, V2]}\n"
                       "  - {id: ECO-907, title: t7, status: verified, order_ref: bomdd/closed-nog.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
                       "  - {id: ECO-908, title: t8, status: decided, order_ref: bomdd/open-g.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}, required_gates: [V1, V2]}\n"
                       "  - {id: ECO-909, title: t9, status: verified, order_ref: bomdd/closed-gi.md, affected_refs: [a.py], diff_audit: {baseline: abc, allowed_paths: [a.py]}, required_gates: [inspection]}\n"
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
        brief_fx = wout / "brief.md"   # ECO-112 T1: 報告する cell(--report)に渡すブリーフの fixture(LF)
        brief_fx.write_bytes(b"factory brief fixture\n")

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
            n_dec = sum(1 for ln in ledger.read_text(encoding="utf-8").splitlines() if '"event": "decision"' in ln) if ledger.exists() else 0
            rc, out = call([eco, "--ledger", str(ledger)] + (["--cell", cell, "--brief", "none"] if use_cell else []) + (["--executor", executor] if executor else []))
            recs = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines()] if ledger.exists() else []
            dec = next((r for r in reversed(recs) if r.get("event") == "decision"), {})
            if sum(1 for r in recs if r.get("event") == "decision") != n_dec + 1:   # ECO-112 T2: この呼び出しの判定レコードが在る(前の行を読まない)
                fails.append(f"{name}: この呼び出しの判定レコードが台帳にない :: {out[:1]}")
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
        rc902, out902 = call(["ECO-902", "--ledger", str(ledger), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
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
            rc_r, out_r = call(["ECO-900", "--ledger", str(ledger), "--cell", c, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "reports/r.md", "--range", "是正確認+回帰"])
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
        rc_st, out_st = call(["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "reports/stale.md", "--range", "境界探索"])
        if rc_st != 2 or not out_st[0].startswith("UNMEASURABLE ARG_ERROR") or "既に存在する" not in out_st[0] or marker.exists() or len(ledger.read_text(encoding="utf-8").splitlines()) != n_st:
            fails.append(f"IA-02 stale: exit {rc_st} / 起動 {marker.exists()} :: {out_st[:1]}")
        (root / "reports" / "stale.md").unlink()
        (root / "reports" / "dirtarget").mkdir()   # r2 IA-06: 同名ディレクトリも起動前拒否
        rc_dt, out_dt = call(["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "reports/dirtarget", "--range", "境界探索"])
        if rc_dt != 2 or not out_dt[0].startswith("UNMEASURABLE ARG_ERROR") or "既に存在する" not in out_dt[0] or marker.exists() or len(ledger.read_text(encoding="utf-8").splitlines()) != n_st:
            fails.append(f"IA-06 dir: exit {rc_dt} / 起動 {marker.exists()} :: {out_dt[:1]}")
        (root / "reports" / "dirtarget").rmdir()
        # r1 IA-01(R8 明確化): cell exit≠0 でも報告は束ねられ、入口 exit は 0(起動した)・3 行の順
        src.write_text("[INFORM / COMPLETE]\n\nREJECT — IA-01\n", encoding="utf-8")
        cell_rep7 = f'"{sys.executable}" -c "import os,shutil,sys; shutil.copy(r\'{src}\', os.environ[\'BOMDD_REPORT\']); sys.exit(7)"'
        rc7, out7 = call(["ECO-900", "--ledger", str(ledger), "--cell", cell_rep7, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "reports/r7.md", "--range", "境界探索"])
        ev7 = last_rec()
        if rc7 != 0 or ev7.get("cell_exit") != 7 or (ev7.get("report") or {}).get("verdict") != "REJECT" or len(out7) != 3 or not out7[1].startswith("cell exit 7") or not out7[2].startswith("report REJECT sha256:"):
            fails.append(f"IA-01: cell exit 7 の扱い: exit {rc7} / {ev7.get('cell_exit')} / {out7}")
        (root / "reports" / "r7.md").unlink(missing_ok=True)   # ECO-112 T3: 拒否された呼び出しは報告を書かない — 自分の検査が報告する(落ちない)
        # --report の構文・所在: 絶対 / `..` / .git 配下 / 前後空白 / 空 / --cell なし → ARG_ERROR・起動しない・台帳不変
        n_before_r = len(ledger.read_text(encoding="utf-8").splitlines())
        # ECO-112 T2: 各要素は自分の理由の文言で照合する(frags は要素と同じ順)
        rep_frags = ("--report には --range", "--range の語彙外", "--range は --report と組", "--report はリポ相対パ", "--report はリポ相対パス",
                     "--report を .git 配下に置けない", "--report はリポ相対パス", "--report はリポ相対パス", "--report はリポ相対パス",
                     "--report は --cell と組", "--report に値がない")
        n_rep = 0
        for bad_rep in (["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "reports/x.md"],   # R11: --range なし
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "reports/x.md", "--range", "探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", "none", "--executor", "EQ-002", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", str(wout / "x.md"), "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "reports/../x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", ".git/x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", " reports/x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "/reports/x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "reports//x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--executor", "EQ-002", "--report", "reports/x.md", "--range", "境界探索"],
                        ["ECO-900", "--ledger", str(ledger), "--cell", cell_norep, "--brief", str(brief_fx), "--executor", "EQ-002", "--report"]):
            if marker.exists():
                marker.unlink()
            frag = rep_frags[n_rep]
            n_rep += 1
            rc_x, out_x = call(bad_rep)
            if rc_x != 2 or not out_x or not out_x[0].startswith("UNMEASURABLE ARG_ERROR") or frag not in out_x[0] or marker.exists():
                fails.append(f"rep-arg {bad_rep[-1]!r}: exit {rc_x}(期待の理由 {frag!r}):: {out_x[:1]}")
        if len(ledger.read_text(encoding="utf-8").splitlines()) != n_before_r:
            fails.append("rep-arg: 不正 --report で台帳に書いた")
        # --report なしの既存経路は不変(cell 行に report=None・出力 2 行)
        d_nr, o_nr = arm("rep-none-regression", good, 0, "ADVANCE", "next", True)
        if last_rec().get("report") is not None or len(o_nr) != 2:
            fails.append(f"rep-none-regression: {last_rec().get('report')} / {o_nr}")
        # --cell に --executor なし / 構文外 → ARG_ERROR・起動しない
        ex_frags = ("--executor EQ-NNN が必須", "--executor の構文不正", "--executor の構文不正")
        n_ex = 0
        for bad_ex in (["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", "none"],
                       ["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", "none", "--executor", "EQ-1"],
                       ["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", "none", "--executor", "eq-002"]):
            if marker.exists():
                marker.unlink()
            frag = ex_frags[n_ex]
            n_ex += 1
            rc_e, out_e = call(bad_ex)
            if rc_e != 2 or not out_e or not out_e[0].startswith("UNMEASURABLE ARG_ERROR") or frag not in out_e[0] or marker.exists():
                fails.append(f"ind-arg {bad_ex[-2:]}: exit {rc_e} / 起動 {marker.exists()} :: {out_e[:1]}")
        # r1 IA-01: ECO の構文(区切り・親参照)は ARG_ERROR・起動しない・台帳も書かない
        wpath.write_text(json.dumps(good), encoding="utf-8")
        if marker.exists():
            marker.unlink()
        n_before = len(ledger.read_text(encoding="utf-8").splitlines())
        for bad_eco in ("ECO-/../../../x", "ECO-900/../x", "..", "ECO-900 x", "ECO_900"):
            rc_t, out_t = call([bad_eco, "--ledger", str(ledger), "--cell", cell, "--brief", "none"])
            if rc_t != 2 or not out_t or not out_t[0].startswith("UNMEASURABLE ARG_ERROR") or "ECO の構文不正" not in out_t[0] or marker.exists():
                fails.append(f"kb-eco-syntax {bad_eco!r}: exit {rc_t} / 起動 {marker.exists()} :: {out_t[:1]}")
        if len(ledger.read_text(encoding="utf-8").splitlines()) != n_before:
            fails.append("kb-eco-syntax: 不正 ECO で台帳に書いた")
        # r1 IA-02: 台帳に書けない(ディレクトリ)→ 起動しない・exit 2
        bad_ledger = wout / "ledger-as-dir"
        bad_ledger.mkdir()
        if marker.exists():
            marker.unlink()
        rc_bl, out_bl = call(["ECO-900", "--ledger", str(bad_ledger), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])   # ECO-112 T3: 自分の理由に届く
        if rc_bl != 2 or marker.exists() or not out_bl[0].startswith("UNMEASURABLE") or "台帳を書けない" not in out_bl[0]:
            fails.append(f"kb-ledger-unwritable: exit {rc_bl} / 起動 {marker.exists()} :: {out_bl[:1]}(起動してはならない)")
        # 台帳を作業木内に置く → 拒否(自己参照)・起動しない
        if marker.exists():
            marker.unlink()
        rc_in, out_in = call(["ECO-900", "--ledger", str(root / "ledger.jsonl"), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])   # ECO-112 T3
        if rc_in != 2 or (root / "ledger.jsonl").exists() or marker.exists() or "作業木内に置けない" not in (out_in[0] if out_in else ""):
            fails.append(f"kb-ledger-inside: exit {rc_in} / 存在 {(root / 'ledger.jsonl').exists()} / 起動 {marker.exists()} :: {out_in[:1]}")
        # 引数不正・未知オプション(r1 IA-01 補足)— 全て ARG_ERROR・起動しない
        # r2 IA-01: オプション値と同じ文字列の余分な位置引数・オプションの重複も ARG_ERROR
        arg_frags = ("ECO [--cell", "ECO [--cell", "--cell に値がない", "--ledger に値がない", "未知の引数", "未知の引数", "未知の引数", "未知の引数",
                     "未知の引数", "--ledger が重複")
        n_arg = 0
        for bad in ([], ["--cell", "x", "--brief", "none"], ["ECO-900", "--brief", "none", "--cell"], ["ECO-900", "--ledger"], ["ECO-900", "--receipt", "x"],
                    ["ECO-900", "extra"], ["ECO-900", "--ledger", str(ledger), "--bogus"],
                    ["ECO-900", "--ledger", str(ledger), "--brief", "none", "--cell", cell, cell],
                    ["ECO-900", "--ledger", str(ledger), str(ledger)], ["ECO-900", "--ledger", str(ledger), "--ledger", str(ledger)]):
            if marker.exists():
                marker.unlink()
            frag = arg_frags[n_arg]
            n_arg += 1
            rc_b, out_b = call(bad)
            if rc_b != 2 or not out_b or not out_b[0].startswith("UNMEASURABLE ARG_ERROR") or frag not in out_b[0] or marker.exists():
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
        # --- ECO-112 G3(R12): verified の昇格判定は必須の検査 ID を名前で読む(V1)---
        g_ok = [{"name": "V1", "exit": 0, "source": "x"}, {"name": "V2", "exit": 0, "source": "x"}]
        d_g, o_g = r11("g3-all-matched", "ECO-906", g_ok, 0, "ADVANCE", "next")
        if d_g.get("required_gates") != ["V1", "V2"] or d_g.get("matched_gates") != ["V1", "V2"] or d_g.get("entry_code") is not None:
            fails.append(f"g3-all-matched: {d_g.get('required_gates')} / {d_g.get('matched_gates')} / {d_g.get('entry_code')}")
        d_g, o_g = r11("g3-missing", "ECO-906", g_ok[:1], 2, "UNMEASURABLE", "operator", "MISSING_INPUT")
        if (d_g.get("entry_code") != "REQUIRED_GATE_MISSING" or d_g.get("matched_gates") != ["V1"] or d_g.get("code") != "OK"
                or not o_g or "REQUIRED_GATE_MISSING(V2)" not in o_g[0]):
            fails.append(f"g3-missing: {d_g.get('entry_code')} / {d_g.get('matched_gates')} / code {d_g.get('code')} :: {o_g[:1]}")
        d_g, o_g = r11("g3-undeclared", "ECO-907", g_ok, 2, "UNMEASURABLE", "operator", "MISSING_INPUT")
        if d_g.get("entry_code") != "GATES_UNDECLARED" or d_g.get("code") != "OK" or not o_g or "GATES_UNDECLARED" not in o_g[0]:
            fails.append(f"g3-undeclared: {d_g.get('entry_code')} / code {d_g.get('code')} :: {o_g[:1]}")
        d_g, _ = r11("g3-case", "ECO-906", [g_ok[0], {"name": "v2", "exit": 0, "source": "x"}], 2, "UNMEASURABLE", "operator", "MISSING_INPUT")
        if d_g.get("entry_code") != "REQUIRED_GATE_MISSING" or d_g.get("entry_detail") != "V2":
            fails.append(f"g3-case: {d_g.get('entry_code')} / {d_g.get('entry_detail')}")
        d_g, _ = r11("g3-no-inspector-inspection", "ECO-909", [{"name": "g", "exit": 0, "source": "x"}], 2, "UNMEASURABLE", "operator", "MISSING_INPUT")
        if d_g.get("entry_code") != "REQUIRED_GATE_MISSING" or d_g.get("entry_detail") != "inspection":
            fails.append(f"g3-no-inspector-inspection: {d_g.get('entry_code')} / {d_g.get('entry_detail')}")
        r11("g3-regression-gate-fail", "ECO-906", [g_ok[0], dict(g_ok[1], exit=1)], 1, "STOP", "factory", "VERIFICATION_FAIL")
        prod("ECO-908", [{"name": "g", "exit": 0, "source": "x"}])   # decided: 集合は照合しない — gate が揃う前に cell が起動する
        if marker.exists():
            marker.unlink()
        rc_g8, out_g8 = call(["ECO-908", "--ledger", str(ledger), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
        if rc_g8 != 0 or not marker.exists() or last_rec().get("event") != "cell":
            fails.append(f"g3-not-verified-launches: exit {rc_g8} / 起動 {marker.exists()} :: {out_g8[:1]}")

        # --- ECO-112 B1-B4(R13): ブリーフの保存・再取得・昇格時の commit 済みの写し(V2)---
        def last_dec(path=ledger):
            rs = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []
            return next((r for r in reversed(rs) if r.get("event") == "decision"), {})
        def n_decs(path=ledger):
            return sum(1 for ln in path.read_text(encoding="utf-8").splitlines() if '"event": "decision"' in ln) if path.exists() else 0
        prod("ECO-900", good["gates"])
        common_fx = git_common_dir(root, witmod)
        store900 = brief_store_dir(common_fx, "ECO-900")
        bseen = wout / "brief-seen.bin"
        cell_b = f'"{sys.executable}" -c "import pathlib,os,shutil; b=os.environ.get(\'BOMDD_BRIEF\',\'\'); pathlib.Path(r\'{marker}\').write_text(b); b and shutil.copyfile(b, r\'{bseen}\')"'
        for f_ in (marker, bseen):
            if f_.exists():
                f_.unlink()
        n0 = n_decs()
        rc_b, out_b = call(["ECO-900", "--ledger", str(ledger), "--cell", cell_b, "--brief", str(brief_fx), "--executor", "EQ-002"])
        db = last_dec() if n_decs() == n0 + 1 else {}   # T2: この呼び出しの判定レコードだけを読む(V3 run 1 の CRASH)
        bi = db.get("brief") if isinstance(db.get("brief"), dict) else {}
        sref = Path(bi.get("store_ref") or "nowhere")
        seen = marker.read_text(encoding="utf-8") if marker.exists() else ""
        if (not db or rc_b != 0 or bi.get("sha256") != hashlib.sha256(brief_fx.read_bytes()).hexdigest() or bi.get("size") != len(brief_fx.read_bytes())
                or not sref.is_file() or sref.read_bytes() != brief_fx.read_bytes() or sref.parent != store900):
            fails.append(f"b-store: exit {rc_b} / record {bool(db)} / {bi} :: {out_b[:1]}")
        if (not seen or Path(seen) == sref or _under(Path(seen), root) or _under(Path(seen), store900)
                or not bseen.exists() or bseen.read_bytes() != brief_fx.read_bytes()):   # V2(i): store_ref でない実行用コピー
            fails.append(f"b-exec-copy: BOMDD_BRIEF {seen!r} / store_ref {sref} / bytes {bseen.exists()} :: {out_b[:1]}")
        if seen and (Path(seen).exists() or Path(seen).parent.exists()):   # V2(j): cell の終了後に消える
            fails.append(f"b-exec-copy-removed: 残っている {seen}")
        if dec_good.get("brief") != "none":
            fails.append(f"b-none-recorded: known-good の brief が none でない: {dec_good.get('brief')}")
        bmm = wout / "brief-mm.md"
        bmm.write_bytes(b"mismatch brief\n")
        mm_store = brief_store_dir(common_fx, "ECO-900") / hashlib.sha256(bmm.read_bytes()).hexdigest()
        mm_store.write_bytes(b"other bytes\n")
        bcr = wout / "brief-crlf.md"
        bcr.write_bytes(b"line one\r\nline two\r\n")
        b_frags = ("BRIEF_STORE_FAILED", "BRIEF_UNREADABLE", "BRIEF_NOT_LF")
        n_b = 0
        for bad_b in (["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", str(bmm), "--executor", "EQ-002"],
                      ["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", str(wout / "no-such-brief.md"), "--executor", "EQ-002"],
                      ["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", str(bcr), "--executor", "EQ-002"]):
            if marker.exists():
                marker.unlink()
            frag = b_frags[n_b]
            n_b += 1
            rc_x, out_x = call(bad_b)
            dx = last_dec()
            if rc_x != 2 or marker.exists() or dx.get("entry_code") != frag or dx.get("decision") != "UNMEASURABLE" or not out_x or frag not in out_x[0]:
                fails.append(f"b-fail {frag}: exit {rc_x} / {dx.get('entry_code')} / 起動 {marker.exists()} :: {out_x[:1]}")
        mm_store.unlink()
        ba_frags = ("--brief PATH|none が必須", "--brief は --cell と組", "--brief none は --report と組にできない", "--report はリポ相対パ")
        n_ba = 0
        for bad_ba in (["ECO-900", "--ledger", str(ledger), "--cell", cell, "--executor", "EQ-002"],
                       ["ECO-900", "--ledger", str(ledger), "--brief", str(brief_fx)],
                       ["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", "none", "--executor", "EQ-002", "--report", "reports/bn.md", "--range", "境界探索"],
                       ["ECO-900", "--ledger", str(ledger), "--cell", cell, "--executor", "EQ-002", "--report", "/abs.md", "--range", "境界探索"]):
            if marker.exists():
                marker.unlink()
            frag = ba_frags[n_ba]
            n_ba += 1
            n_before_ba = len(ledger.read_text(encoding="utf-8").splitlines())
            rc_x, out_x = call(bad_ba)
            if (rc_x != 2 or marker.exists() or not out_x or not out_x[0].startswith("UNMEASURABLE ARG_ERROR") or frag not in out_x[0]
                    or len(ledger.read_text(encoding="utf-8").splitlines()) != n_before_ba):
                fails.append(f"b-arg {frag!r}: exit {rc_x} / 起動 {marker.exists()} :: {out_x[:1]}")
        b2 = wout / "brief-2.md"
        b2.write_bytes(b"second brief\n")
        sha2 = hashlib.sha256(b2.read_bytes()).hexdigest()
        wpath.write_text(json.dumps(dict(good, tree=good["tree"][:-4] + ("0000" if good["tree"][-4:] != "0000" else "1111"))), encoding="utf-8")
        rc_r1, out_r1 = call(["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", str(b2), "--executor", "EQ-002"])
        if rc_r1 != 1 or not out_r1 or not out_r1[0].startswith("STOP ") or (store900 / sha2).exists():   # T2: 呼び出しごとに直後で見る
            fails.append(f"b-refused-stores-nothing (witness STOP): exit {rc_r1} / stored {(store900 / sha2).exists()} :: {out_r1[:1]}")
        prod("ECO-900", good["gates"])
        rc_r2, out_r2 = call(["ECO-902", "--ledger", str(ledger), "--cell", cell, "--brief", str(b2), "--executor", "EQ-002"])
        if rc_r2 != 1 or not out_r2 or not out_r2[0].startswith("STOP ") or (brief_store_dir(common_fx, "ECO-902") / sha2).exists():
            fails.append(f"b-refused-stores-nothing (job STOP): exit {rc_r2} :: {out_r2[:1]}")
        rc_r3, out_r3 = call(["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", str(b2), "--executor", "EQ-001"])
        if rc_r3 != 1 or not out_r3 or "INDEPENDENCE_FAIL" not in out_r3[0] or (store900 / sha2).exists():
            fails.append(f"b-refused-stores-nothing (INDEPENDENCE_FAIL): exit {rc_r3} :: {out_r3[:1]}")
        # --- r1 IA-01 / IA-02(V2(g)-(i)): ロールバックは自分が作った保管用の写しだけ・実行用コピーは残らない・cell が消しても保管用は残る ---
        tmp_root = Path(tempfile.gettempdir())

        def exec_dirs():
            try:
                return {e_.name for e_ in tmp_root.iterdir() if e_.name.startswith("bomdd-brief-")}
            except OSError:
                return set()

        def fresh(name, data):
            f_ = wout / name
            f_.write_bytes(data)
            return f_, hashlib.sha256(data).hexdigest()

        g_ = globals()

        def boom(*a, **k):
            raise PermissionError("patched")
        brb, sha_rb = fresh("brief-rb.md", b"rollback brief\n")
        if marker.exists():
            marker.unlink()
        x0 = exec_dirs()
        rc_g1, out_g1 = call(["ECO-900", "--ledger", str(bad_ledger), "--cell", cell, "--brief", str(brb), "--executor", "EQ-002"])
        if (rc_g1 != 2 or marker.exists() or len(out_g1) != 1 or "台帳を書けない" not in out_g1[0] or (store900 / sha_rb).exists()
                or exec_dirs() - x0):
            fails.append(f"b-rollback-ledger: exit {rc_g1} / stored {(store900 / sha_rb).exists()} / exec {sorted(exec_dirs() - x0)} :: {out_g1[:2]}")
        bex, sha_ex = fresh("brief-ex.md", b"already stored brief\n")
        _i, c_ex, _m, _c = store_brief(root, common_fx, "ECO-900", str(bex))
        x0 = exec_dirs()
        rc_g2, out_g2 = call(["ECO-900", "--ledger", str(bad_ledger), "--cell", cell, "--brief", str(bex), "--executor", "EQ-002"])
        if (c_ex or rc_g2 != 2 or not out_g2 or "台帳を書けない" not in out_g2[0] or not (store900 / sha_ex).is_file()
                or (store900 / sha_ex).read_bytes() != bex.read_bytes() or exec_dirs() - x0):
            fails.append(f"b-rollback-existing: exit {rc_g2} / kept {(store900 / sha_ex).is_file()} :: {out_g2[:2]}")
        bxw, sha_xw = fresh("brief-xw.md", b"execution copy fails\n")
        keep_ = g_["_exec_write"]
        g_["_exec_write"] = boom
        try:
            if marker.exists():
                marker.unlink()
            x0, n0 = exec_dirs(), n_decs()
            rc_g3, out_g3 = call(["ECO-900", "--ledger", str(ledger), "--cell", cell, "--brief", str(bxw), "--executor", "EQ-002"])
        finally:
            g_["_exec_write"] = keep_
        d_g3 = last_dec() if n_decs() == n0 + 1 else {}
        if (not d_g3 or rc_g3 != 2 or marker.exists() or d_g3.get("entry_code") != "BRIEF_STORE_FAILED" or not out_g3
                or "BRIEF_STORE_FAILED" not in out_g3[0] or (store900 / sha_xw).exists() or exec_dirs() - x0):
            fails.append(f"b-rollback-exec-copy: exit {rc_g3} / {d_g3.get('entry_code')} / stored {(store900 / sha_xw).exists()} :: {out_g3[:1]}")
        bfl, sha_fl = fresh("brief-fl.md", b"removal fails\n")
        keep_ = g_["_unlink_stored"]
        g_["_unlink_stored"] = boom
        try:
            if marker.exists():
                marker.unlink()
            rc_h, out_h = call(["ECO-900", "--ledger", str(bad_ledger), "--cell", cell, "--brief", str(bfl), "--executor", "EQ-002"])
        finally:
            g_["_unlink_stored"] = keep_
        if (rc_h != 2 or marker.exists() or len(out_h) != 2 or "台帳を書けない" not in out_h[0]
                or out_h[1] != f"brief left in store: {sha_fl[:12]} (PermissionError)" or not (store900 / sha_fl).is_file()):
            fails.append(f"b-rollback-fails: exit {rc_h} / kept {(store900 / sha_fl).is_file()} :: {out_h[:2]}")
        (store900 / sha_fl).unlink(missing_ok=True)
        bdl, sha_dl = fresh("brief-del.md", b"the cell deletes its brief\n")
        cell_del = f'"{sys.executable}" -c "import pathlib,os; b=os.environ[\'BOMDD_BRIEF\']; pathlib.Path(r\'{marker}\').write_text(b); os.remove(b)"'
        if marker.exists():
            marker.unlink()
        n0 = n_decs()
        rc_i, out_i = call(["ECO-900", "--ledger", str(ledger), "--cell", cell_del, "--brief", str(bdl), "--executor", "EQ-002"])
        d_i = last_dec() if n_decs() == n0 + 1 else {}
        seen_i = marker.read_text(encoding="utf-8") if marker.exists() else ""
        _cc, code_i, msg_i = committed_copies(root, common_fx, "ECO-900", d_i.get("tree"))
        if (not d_i or rc_i != 0 or not seen_i or Path(seen_i) == store900 / sha_dl or not (store900 / sha_dl).is_file()
                or (store900 / sha_dl).read_bytes() != bdl.read_bytes() or code_i != "BRIEF_NOT_COMMITTED" or sha_dl[:12] not in msg_i):
            fails.append(f"b-cell-deletes-brief: exit {rc_i} / kept {(store900 / sha_dl).is_file()} / {code_i} :: {out_i[:1]}")
        ledger2 = wout / "ledger-2.jsonl"
        n0 = n_decs(ledger2)
        rc_l2, _ = call(["ECO-900", "--ledger", str(ledger2), "--cell", cell, "--brief", str(brief_fx), "--executor", "EQ-002"])
        b_l2 = last_dec(ledger2).get("brief") if n_decs(ledger2) == n0 + 1 else None   # T2: この呼び出しの判定レコードだけを読む
        if rc_l2 != 0 or not isinstance(b_l2, dict) or b_l2.get("store_ref") != str(sref):
            fails.append(f"b-other-ledger-same-store: exit {rc_l2} / {b_l2}")
        wt = wout / "wt"
        if witmod._git(root, "worktree", "add", "-q", str(wt), env=env).returncode != 0 or git_common_dir(wt, witmod) != common_fx:
            fails.append(f"b-worktree-same-store: {git_common_dir(wt, witmod)} != {common_fx}")
        # 昇格時(B4): ECO-906 のストアに 1 本 → 束縛された tree に写しがなければ BRIEF_NOT_COMMITTED・在れば通る
        b906 = wout / "brief-906.md"
        b906.write_bytes(b"brief for ECO-906\n")
        info906, code906, _, _ = store_brief(root, common_fx, "ECO-906", str(b906))
        if code906:
            fails.append(f"b-promotion fixture: {code906}")
        d_p, o_p = r11("b-promotion-not-committed", "ECO-906", g_ok, 2, "UNMEASURABLE", "operator", "MISSING_INPUT")
        if d_p.get("entry_code") != "BRIEF_NOT_COMMITTED" or not o_p or "BRIEF_NOT_COMMITTED" not in o_p[0]:
            fails.append(f"b-promotion-not-committed: {d_p.get('entry_code')} :: {o_p[:1]}")
        copy906 = root / "bomdd" / "reports" / "eco-906" / "brief.md"
        copy906.parent.mkdir(parents=True, exist_ok=True)
        copy906.write_bytes(b906.read_bytes())
        (brief_store_dir(common_fx, "ECO-906") / ".tmp-left").write_bytes(b"x")
        d_p, _ = r11("b-promotion-copy", "ECO-906", g_ok, 0, "ADVANCE", "next")
        if (d_p.get("brief_copies") != [{"sha256": info906["sha256"], "path": "bomdd/reports/eco-906/brief.md", "tree": d_p.get("tree")}]
                or d_p.get("brief_store_ignored") != [".tmp-left"]):
            fails.append(f"b-promotion-copy: {d_p.get('brief_copies')} / ignored {d_p.get('brief_store_ignored')}")
        witmod._git(root, "add", "-A", env=env)
        witmod._git(root, "commit", "-q", "-m", "copy", env=env)
        copy906.write_bytes(b"changed after commit\n")
        d_p, _ = r11("b-promotion-head-only", "ECO-906", g_ok, 2, "UNMEASURABLE", "operator", "MISSING_INPUT")
        if d_p.get("entry_code") != "BRIEF_NOT_COMMITTED":
            fails.append(f"b-promotion-head-only: HEAD にだけ在る写しを通した: {d_p.get('entry_code')}")
        copy906.write_bytes(b906.read_bytes())
        (brief_store_dir(common_fx, "ECO-906") / ("f" * 64)).write_bytes(b"not its name\n")
        d_p, _ = r11("b-promotion-store-mismatch", "ECO-906", g_ok, 2, "UNMEASURABLE", "operator", "MISSING_INPUT")
        if d_p.get("entry_code") != "BRIEF_STORE_FAILED":
            fails.append(f"b-promotion-store-mismatch: {d_p.get('entry_code')}")
        (brief_store_dir(common_fx, "ECO-906") / ("f" * 64)).unlink()
        # --- ECO-113(R15): 実行中の起動 — X 排他 / W 所有 / J 判定 / R 回復 / A 記録 / S 順序 / O 出口(order §3 V1-V4)---
        prod("ECO-900", good["gates"])
        jp, lockp = journal_file(common_fx, "ECO-900"), lock_file(common_fx, "ECO-900")
        IDN = _identity()
        lg = wout / "ledger-113.jsonl"   # ECO-113 の腕の台帳(既存の台帳の形の検査に混ぜない)
        BLANK = set(_blank_rec("ECO-900", None))
        RUN_PY = str(TOOLS_DIR / "bomdd-run.py")
        OPEN_CLS = "ABNORMAL_END" if IS_WIN else "UNKNOWN"   # 入口の居ない開いた実行の分類(POSIX は job がない= L1)

        def jrecs():
            r_ = journal_read(jp)[0]
            return [x for _, x in (r_ or [])]

        def jcount(event, rid_=None):
            return sum(1 for x in jrecs() if x.get("event") == event and (rid_ is None or x.get("run_id") == rid_))

        def last_start():
            return next((x for x in reversed(jrecs()) if x.get("event") == "start"), {})

        def recs_of(path):
            return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []

        def row(name, rc_, out_, cause, extra_keys, rid_, n_before, path=lg):
            """V4(n)/(k): S4 の行 — 判定レコードの追加欄はその行のものだけ・行の形・O1 の判定語と exit。"""
            want_v, want_rc = IN_FLIGHT_VERDICT[cause]
            rs_ = recs_of(path)
            d_ = rs_[-1] if len(rs_) == n_before + 1 else {}
            extra_ = set(d_) - BLANK - {"cause"}
            if (rc_ != want_rc or not out_ or out_[0] != in_flight_line("ECO-900", cause, rid_) or d_.get("cause") != cause
                    or d_.get("decision") != want_v or d_.get("stop_type") != "RUN_IN_FLIGHT" or d_.get("delivery") != "operator"
                    or extra_ != set(extra_keys)):
                fails.append(f"{name}: exit {rc_} / cause {d_.get('cause')} / 欄 {sorted(extra_)} :: {out_[:1]}")
            return d_

        def dry(path=lg):
            n_ = len(recs_of(path))
            rc_, out_ = call(["ECO-900", "--ledger", str(path)])
            return rc_, out_, n_

        def craft(**over):
            """J1: journal にだけ在る開いた実行(入口は居ない・job は無い)。"""
            rid_ = f"crafted-{os.urandom(4).hex()}"
            s_ = {"event": "start", "eco": "ECO-900", "run_id": rid_, "job_name": f"Local\\BomDD-run-ECO-900-{rid_}", "entry_pid": 0,
                  "host": IDN["host"], "session": IDN["session"], "appcontainer": IDN["appcontainer"], "started_at": _now()}
            s_.update(over)
            if journal_commit(jp, s_):
                fails.append(f"craft: journal に書けない {rid_}")
            return rid_

        def release(name, rid_, want_cls):
            rc_, out_ = call(["ECO-900", "--release", rid_, "--by", "EQ-007"])
            rel_ = [x for x in jrecs() if x.get("event") == "release" and x.get("run_id") == rid_]
            if (rc_ != 0 or out_[:1] != [f"RELEASED ECO-900 {rid_} ({want_cls}) by EQ-007"] or len(rel_) != 1
                    or rel_[0].get("classified") != want_cls or (rel_[0].get("cell") == "unverified") != (want_cls == "UNKNOWN")):
                fails.append(f"{name}: release exit {rc_} / records {rel_} :: {out_[:1]}")

        n_child = [0]

        def child(args, cwd=root):
            """別プロセスの入口。出力はファイルへ(パイプは cell に継承され、生き残った cell が EOF を止めるため)。"""
            n_child[0] += 1
            out_p = wout / f"child-{n_child[0]}.out"
            with open(out_p, "wb") as f_:
                p_ = subprocess.Popen([sys.executable, RUN_PY] + args, cwd=str(cwd), stdout=f_, stderr=subprocess.STDOUT)
            p_.out_path = out_p
            return p_

        def child_out(p_, secs):
            p_.wait(secs)
            return p_.out_path.read_bytes().decode("utf-8", errors="replace")

        def wait_for(pred, secs=15.0):
            end_ = time.monotonic() + secs
            while time.monotonic() < end_:
                if pred():
                    return True
                time.sleep(0.05)
            return False

        def read_or_none(p_):
            try:
                return p_.read_text(encoding="utf-8")
            except OSError:
                return None

        def advancing(p_):
            a_ = read_or_none(p_)
            time.sleep(0.7)
            b_ = read_or_none(p_)
            return a_ is not None and b_ is not None and a_ != b_

        def lock_free():
            fd_, _c, _e = acquire_lock(common_fx, "ECO-900")
            if fd_ is None:
                return False
            release_lock(fd_)
            return True

        def raise_at(point):
            def f_(name):
                if name == point:
                    raise RuntimeError("patched")
            return f_

        job_names = []
        keep_create = g_["_job_create"]

        def recording_create(name):
            job_names.append(name)
            return keep_create(name)

        loopf, appf, seenf, holdf, ledf = (wout / "loop.py", wout / "append.py", wout / "seen.py", wout / "holdjob.py", wout / "ledger_append.py")
        loopf.write_text("import pathlib, sys, time\np = pathlib.Path(sys.argv[1]); stop = pathlib.Path(sys.argv[2])\n"
                         "for i in range(1200):\n    p.write_text(str(i))\n    if stop.exists():\n        break\n    time.sleep(0.1)\n", encoding="utf-8")
        appf.write_text("import sys, time\nopen(sys.argv[1], 'a').write('x\\n')\ntime.sleep(2.5)\n", encoding="utf-8")
        seenf.write_text("import json, sys\nlg, jp, out = sys.argv[1:4]\nrecs = [json.loads(l) for l in open(lg, encoding='utf-8').read().splitlines()]\n"
                         "d = recs[-1]\nj = open(jp, 'rb').read().decode('ascii', 'replace')\n"
                         "ok = d.get('event') == 'decision' and bool(d.get('cell')) and ('\"run_id\": \"%s\"' % d.get('run_id')) in j\n"
                         "open(out, 'w').write('ok' if ok else 'bad')\n", encoding="utf-8")
        holdf.write_text("import ctypes, sys\nk = ctypes.WinDLL('kernel32', use_last_error=True)\nk.OpenJobObjectW.restype = ctypes.c_void_p\n"
                         "k.OpenJobObjectW.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_wchar_p]\nh = k.OpenJobObjectW(0x0004, 0, sys.argv[1])\n"
                         "print('HELD' if h else 'FAIL %d' % ctypes.get_last_error(), flush=True)\nsys.stdin.read()\n", encoding="utf-8")
        ledf.write_text("import importlib.util, sys\nfrom pathlib import Path\n"
                        "spec = importlib.util.spec_from_file_location('bomdd_run_child', sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
                        "for i in range(int(sys.argv[4])):\n    e = m.write_ledger(Path(sys.argv[2]), {'event': 'x', 'w': sys.argv[3], 'i': i, 'pad': 'y' * 300})\n"
                        "    if e:\n        print(e)\n        sys.exit(1)\n", encoding="utf-8")
        counter, stopf, launches = wout / "counter.txt", wout / "stop.txt", wout / "launches.txt"
        slow = f'"{sys.executable}" "{loopf}" "{counter}" "{stopf}"'
        cell_app = f'"{sys.executable}" "{appf}" "{launches}"'
        lg_a = wout / "ledger-a.jsonl"

        # V1(a)(d)(b) / V2(a) / V3(a)(b): 生きている入口がロックを持つ → 別の起動・dry・解放は ENTRY_ALIVE。入口を殺すと cell も止まり ABNORMAL_END
        for f_ in (counter, stopf):
            f_.unlink(missing_ok=True)
        ch_a = child(["ECO-900", "--ledger", str(lg_a), "--cell", slow, "--brief", "none", "--executor", "EQ-002"])
        if not wait_for(counter.exists):
            fails.append(f"v1 fixture: 子の cell が始まらない :: {ch_a.poll()}")
        else:
            if marker.exists():
                marker.unlink()
            n0 = len(recs_of(lg))
            rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
            row("v1a-entry-alive", rc_x, out_x, "ENTRY_ALIVE", (), None, n0)
            if marker.exists():
                fails.append("v1a-entry-alive: 別の入口がロックを持つあいだに起動した")
            rc_x, out_x, n0 = dry()
            row("v1d-dry-while-running", rc_x, out_x, "ENTRY_ALIVE", (), None, n0)
            rc_x, out_x = call(["ECO-900", "--release", "any-run", "--by", "EQ-007"])
            if rc_x != 1 or out_x[:1] != [in_flight_line("ECO-900", "ENTRY_ALIVE")]:
                fails.append(f"v3b-release-entry-alive: exit {rc_x} :: {out_x[:1]}")
            st_a = last_start()
            rid_a = st_a.get("run_id")
            if IS_WIN:
                ch_a.kill()
                ch_a.wait(30)
                if not wait_for(lock_free, 5.0):
                    fails.append("v1b-lock-after-kill: 入口を殺した後 5 秒以内にロックを取れない")
                if advancing(counter):
                    fails.append("v2a-entry-killed: 入口を殺しても cell の子コマンドが進む")
                if _job_query(st_a.get("job_name") or "x")[0] != "gone":
                    fails.append(f"v2a-entry-killed: job が残る {_job_query(st_a.get('job_name') or 'x')}")
                rc_x, out_x, n0 = dry()
                d_x = row("v2a-abnormal-end", rc_x, out_x, "ABNORMAL_END", ("open_runs",), rid_a, n0)
                if d_x.get("open_runs") != [{"run_id": rid_a, "class": "ABNORMAL_END"}]:
                    fails.append(f"v2a-abnormal-end: open_runs {d_x.get('open_runs')}")
                release("v3a-release-abnormal-end", rid_a, "ABNORMAL_END")
                if marker.exists():
                    marker.unlink()
                rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
                if rc_x != 0 or not marker.exists():
                    fails.append(f"v3a-next-launch: 解放の後の起動が進まない: exit {rc_x} :: {out_x[:1]}")
            else:  # pragma: no cover
                stopf.write_text("x")
                ch_a.wait(60)
        # V1(c): 同時の 2 起動 / 別の --ledger / 2 つの worktree → どれも 1 つだけ起動する
        _t, wt_git, _e = witmod.worktree_tree(wt)
        if wt_git is not None:
            rc_w, m_w, _ = witmod.produce(wt, "ECO-900", good["gates"], "NONE", witmod.default_path(wt_git, "ECO-900"), "selftest")
            if rc_w != 0:
                fails.append(f"v1c fixture: worktree の受領証 {m_w}")
        for name_, a1, a2, cwd2 in (
                ("v1c-same-ledger", ["ECO-900", "--ledger", str(wout / "lc.jsonl"), "--cell", cell_app, "--brief", "none", "--executor", "EQ-002"],
                 ["ECO-900", "--ledger", str(wout / "lc.jsonl"), "--cell", cell_app, "--brief", "none", "--executor", "EQ-002"], root),
                ("v1c-other-ledger", ["ECO-900", "--ledger", str(wout / "lc1.jsonl"), "--cell", cell_app, "--brief", "none", "--executor", "EQ-002"],
                 ["ECO-900", "--ledger", str(wout / "lc2.jsonl"), "--cell", cell_app, "--brief", "none", "--executor", "EQ-002"], root),
                ("v1c-two-worktrees", ["ECO-900", "--cell", cell_app, "--brief", "none", "--executor", "EQ-002"],
                 ["ECO-900", "--cell", cell_app, "--brief", "none", "--executor", "EQ-002"], wt)):
            launches.unlink(missing_ok=True)
            pr_ = [child(a1), child(a2, cwd2)]
            outs_ = [child_out(p_, 120) for p_ in pr_]
            rcs_ = [p_.returncode for p_ in pr_]
            n_l = len(launches.read_text(encoding="utf-8").splitlines()) if launches.exists() else 0
            loser = outs_[rcs_.index(1)] if 1 in rcs_ else ""
            if n_l != 1 or sorted(rcs_) != [0, 1] or "RUN_IN_FLIGHT(ENTRY_ALIVE)" not in loser:
                fails.append(f"{name_}: 起動 {n_l} 回 / exit {rcs_} :: {[o_.splitlines()[:1] for o_ in outs_]}")
        if not lockp.is_file():   # V1(e)
            fails.append("v1e-lock-file-kept: 完了した実行の後にロックファイルがない")
        # V1(f) / V4(n) LOCK_UNAVAILABLE: 読み取り専用のロックファイル・書けないディレクトリは ENTRY_ALIVE でない
        os.chmod(lockp, stat.S_IREAD)
        try:
            rc_x, out_x, n0 = dry()
        finally:
            os.chmod(lockp, stat.S_IREAD | stat.S_IWRITE)
        d_x = row("v1f-readonly-lock", rc_x, out_x, "LOCK_UNAVAILABLE", ("lock_error",), None, n0)
        rd_, moved_ = run_dir(common_fx), run_dir(common_fx).with_name("bomdd-run.moved")
        rd_.rename(moved_)
        rd_.write_text("not a directory\n", encoding="utf-8")
        try:
            rc_x, out_x, n0 = dry()
        finally:
            rd_.unlink()
            moved_.rename(rd_)
        row("v1f-unwritable-dir", rc_x, out_x, "LOCK_UNAVAILABLE", ("lock_error",), None, n0)

        if IS_WIN:
            # V2(b) / V3(b)(e)(f) / V4(n) CELL_ALIVE・JOURNAL_CORRUPT: 別のプロセスが job のハンドルを持つと、入口を殺しても cell は動き続ける
            for f_ in (counter, stopf):
                f_.unlink(missing_ok=True)
            ch_b = child(["ECO-900", "--ledger", str(lg_a), "--cell", slow, "--brief", "none", "--executor", "EQ-002"])
            if not wait_for(counter.exists):
                fails.append("v2b fixture: 子の cell が始まらない")
            st_b = last_start()
            rid_b = st_b.get("run_id")
            hold = subprocess.Popen([sys.executable, str(holdf), st_b.get("job_name") or "x"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            held = hold.stdout.readline().strip()
            ch_b.kill()
            ch_b.wait(30)
            wait_for(lock_free, 5.0)
            if held != "HELD" or not advancing(counter):
                fails.append(f"v2b-cell-alive: 持ち手 {held} / cell が止まった")
            rc_x, out_x, n0 = dry()
            d_x = row("v2b-cell-alive", rc_x, out_x, "CELL_ALIVE", ("open_runs",), rid_b, n0)
            rc_x, out_x = call(["ECO-900", "--release", rid_b, "--by", "EQ-007"])
            if rc_x != 1 or out_x[:1] != [in_flight_line("ECO-900", "CELL_ALIVE", rid_b)] or jcount("release", rid_b):
                fails.append(f"v3b-release-cell-alive: exit {rc_x} :: {out_x[:1]}")
            size_c = jp.stat().st_size
            with open(jp, "ab") as f_:
                f_.write(b"not json\n")
            nq = jcount("quarantine")
            rc_x, out_x = call(["ECO-900", "--quarantine-journal", "--by", "EQ-007"])
            if rc_x != 1 or out_x[:1] != [in_flight_line("ECO-900", "CELL_ALIVE", rid_b)] or jcount("quarantine") != nq:
                fails.append(f"v3e-quarantine-cell-alive: exit {rc_x} :: {out_x[:1]}")
            if not advancing(counter):
                fails.append("v3f-nothing-stopped: 回復の経路が cell を止めた")
            rc_x, out_x, n0 = dry()
            d_x = row("v4n-journal-corrupt-cell-alive", rc_x, out_x, "JOURNAL_CORRUPT", ("corrupt_offset", "open_runs"), None, n0)
            if d_x.get("corrupt_offset") != size_c or d_x.get("open_runs") != [{"run_id": rid_b, "class": "CELL_ALIVE"}]:
                fails.append(f"v4n-journal-corrupt-cell-alive: {d_x.get('corrupt_offset')} != {size_c} / {d_x.get('open_runs')}")
            hold.stdin.close()
            hold.wait(30)
            time.sleep(0.5)
            if advancing(counter):
                fails.append("v2b-holder-closed: 持ち手が閉じても cell が動く")
            size_q = jp.stat().st_size
            rc_x, out_x = call(["ECO-900", "--quarantine-journal", "--by", "EQ-007"])
            q_ = [x for x in jrecs() if x.get("event") == "quarantine"]
            if (rc_x != 0 or not out_x or not out_x[0].startswith("QUARANTINED ECO-900 ") or len(q_) != nq + 1 or jp.stat().st_size <= size_q
                    or q_[-1].get("excluded_sha256") != _sha(b"not json\n") or q_[-1].get("by") != "EQ-007"):
                fails.append(f"v3e-quarantine: exit {rc_x} / {q_[-1:]} :: {out_x[:1]}")
            rc_x, out_x, n0 = dry()
            row("v3e-parsed-run-stays-open", rc_x, out_x, "ABNORMAL_END", ("open_runs",), rid_b, n0)
            release("v3e-release-after-quarantine", rid_b, "ABNORMAL_END")
            # V2(c): job の作成・設定・割り当ての失敗 → JOB_UNAVAILABLE・start なし・job なし・cell は何も実行しない
            for nm in ("_job_create", "_job_configure", "_job_assign"):
                keep_ = g_[nm]
                g_[nm] = boom
                try:
                    if marker.exists():
                        marker.unlink()
                    n0, s0 = n_decs(lg), jcount("start")
                    rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
                finally:
                    g_[nm] = keep_
                d_x = last_dec(lg) if n_decs(lg) == n0 + 1 else {}
                time.sleep(0.3)
                if (rc_x != 2 or d_x.get("entry_code") != "JOB_UNAVAILABLE" or d_x.get("cell") is not None or not out_x
                        or not out_x[0].startswith("UNMEASURABLE ECO-900 JOB_UNAVAILABLE") or jcount("start") != s0 or marker.exists()
                        or _job_query(f"Local\\BomDD-run-ECO-900-{d_x.get('run_id')}")[0] != "gone"):
                    fails.append(f"v2c-{nm}: exit {rc_x} / {d_x.get('entry_code')} / 起動 {marker.exists()} :: {out_x[:1]}")
            # V2(d) / V4(n) UNKNOWN: job の照会が not-found 以外で失敗・session・appcontainer・host が違う
            keep_ = g_["_job_query"]
            g_["_job_query"] = lambda name: ("error", 5)
            try:   # 解放は分類し直す(R2)— 照会の失敗を差し込んだまま解放する
                r_ = craft()
                rc_x, out_x, n0 = dry()
                d_x = row("v2d-job-query-error", rc_x, out_x, "UNKNOWN", ("open_runs", "unknown_because"), r_, n0)
                release("v3a-release-unknown", r_, "UNKNOWN")
            finally:
                g_["_job_query"] = keep_
            if d_x.get("unknown_because") != "job query error":
                fails.append(f"v2d-job-query-error: {d_x.get('unknown_because')}")
            for key_, val_ in (("session", -1), ("appcontainer", "S-1-15-2-0"), ("host", "another-host")):
                r_ = craft(**{key_: val_})
                rc_x, out_x, n0 = dry()
                d_x = row(f"v2d-other-{key_}", rc_x, out_x, "UNKNOWN", ("open_runs", "unknown_because"), r_, n0)
                if d_x.get("unknown_because") != key_:
                    fails.append(f"v2d-other-{key_}: {d_x.get('unknown_because')}")
                release(f"v2d-release-{key_}", r_, "UNKNOWN")
            # V2(g): 入口(selftest)は job の外・ハンドルも残さない / 0 プロセスの job は ABNORMAL_END / 割り当て後・再開前の例外は O3 で job なし
            seen_ = {}

            def probe(name):
                if name == "resumed":
                    s_ = last_start()
                    seen_.update(name=s_.get("job_name"), inside=_in_job(s_.get("job_name") or "x"), q=_job_query(s_.get("job_name") or "x"))
            keep_ = g_["_checkpoint"]
            g_["_checkpoint"] = probe
            try:
                rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
            finally:
                g_["_checkpoint"] = keep_
            if rc_x != 0 or seen_.get("inside") is not False or (seen_.get("q") or ("",))[0] != "active" or _job_query(seen_.get("name") or "x")[0] != "gone":
                fails.append(f"v2g-entry-outside: exit {rc_x} / {seen_}")
            nm0 = f"Local\\BomDD-selftest-empty-{os.urandom(4).hex()}"
            h0 = _job_create(nm0)
            try:
                r_ = craft(job_name=nm0)
                rc_x, out_x, n0 = dry()
            finally:
                _job_close(h0)
            d_x = row("v2g-empty-job", rc_x, out_x, "ABNORMAL_END", ("open_runs",), r_, n0)
            release("v2g-release-empty-job", r_, "ABNORMAL_END")
            err_buf, keep_err = io.StringIO(), sys.stderr
            job_names.clear()
            g_["_checkpoint"], g_["_job_create"], sys.stderr = raise_at("assigned"), recording_create, err_buf
            try:
                if marker.exists():
                    marker.unlink()
                s0 = jcount("start")
                rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
            finally:
                g_["_checkpoint"], g_["_job_create"], sys.stderr = keep_, keep_create, keep_err
            time.sleep(0.3)
            if (rc_x != 2 or out_x[-1:] != ["UNMEASURABLE ECO-900 INTERNAL_ERROR(RuntimeError) → operator"] or "Traceback" not in err_buf.getvalue()
                    or not job_names or _job_query(job_names[-1])[0] != "gone" or marker.exists() or jcount("start") != s0):
                fails.append(f"v2g-exception-before-resume: exit {rc_x} / jobs {job_names} :: {out_x}")
            # V2(h): 再開の失敗 → S2 の 2 行目・cell レコード・end・exit 2・job なし
            job_names.clear()
            keep_ = g_["_job_resume"]
            g_["_job_resume"], g_["_job_create"] = boom, recording_create
            try:
                if marker.exists():
                    marker.unlink()
                rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
            finally:
                g_["_job_resume"], g_["_job_create"] = keep_, keep_create
            ev_ = (recs_of(lg) or [{}])[-1]
            end_ = next((x for x in reversed(jrecs()) if x.get("event") == "end"), {})
            time.sleep(0.3)
            if (rc_x != 2 or out_x[1:] != ["cell not started (RESUME_FAILED)"] or ev_.get("event") != "cell" or ev_.get("cell_exit") != "RESUME_FAILED"
                    or end_.get("cell_exit") != "RESUME_FAILED" or end_.get("run_id") != ev_.get("run_id") or marker.exists()
                    or not job_names or _job_query(job_names[-1])[0] != "gone"):
                fails.append(f"v2h-resume-failed: exit {rc_x} / {ev_.get('cell_exit')} / end {end_.get('cell_exit')} :: {out_x}")

        # V2(e): Windows の分岐を切る(POSIX と同じ)→ 入口の居ない開いた実行は UNKNOWN・cell は 1 行目の後に Popen
        keep_ = g_["_win_branch"]
        g_["_win_branch"] = False
        try:
            r_ = craft(job_name=None)
            rc_x, out_x, n0 = dry()
            d_x = row("v2e-posix-unknown", rc_x, out_x, "UNKNOWN", ("open_runs", "unknown_because"), r_, n0)
            if d_x.get("unknown_because") != "POSIX":
                fails.append(f"v2e-posix-unknown: {d_x.get('unknown_because')}")
            release("v2e-release", r_, "UNKNOWN")
            seen_p = wout / "posix-seen.txt"
            seen_p.unlink(missing_ok=True)
            cell_seen = f'"{sys.executable}" "{seenf}" "{lg}" "{jp}" "{seen_p}"'
            rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell_seen, "--brief", "none", "--executor", "EQ-002"])
            st_p = last_start()
            if rc_x != 0 or read_or_none(seen_p) != "ok" or st_p.get("job_name") is not None or jcount("end", st_p.get("run_id")) != 1:
                fails.append(f"v2e-popen-after-first-line: exit {rc_x} / seen {read_or_none(seen_p)} / job {st_p.get('job_name')} :: {out_x[:1]}")
        finally:
            g_["_win_branch"] = keep_
        # V2(f): 分類は pid による生存確認を呼ばない(os.kill とスナップショットを例外にしても分類できる)
        r_ = craft()
        keep_kill, keep_snap = os.kill, g_["_snapshot_threads"]
        os.kill, g_["_snapshot_threads"] = boom, boom
        try:
            rc_x, out_x, n0 = dry()
        finally:
            os.kill, g_["_snapshot_threads"] = keep_kill, keep_snap
        row("v2f-no-pid", rc_x, out_x, OPEN_CLS, ("open_runs",) if IS_WIN else ("open_runs", "unknown_because"), r_, n0)
        release("v2f-release", r_, OPEN_CLS)
        # V2(i): journal にだけ在る開いた実行は、空の台帳でも分類される(台帳は読まない)
        r_ = craft()
        lg_e = wout / "ledger-empty.jsonl"
        rc_x, out_x, n0 = dry(lg_e)
        row("v2i-journal-only", rc_x, out_x, OPEN_CLS, ("open_runs",) if IS_WIN else ("open_runs", "unknown_because"), r_, n0, lg_e)
        # V3(c): RUN_ID の誤り・人でない --by・他のオプション → ARG_ERROR(それぞれの文言)
        for argv_, frag in ((["ECO-900", "--release", "no-such-run", "--by", "EQ-007"], "開いている実行でない"),
                            (["ECO-900", "--release", r_, "--by", "EQ-002"], "kind: human"),
                            (["ECO-900", "--release", r_, "--by", "EQ-007", "--ledger", str(lg)], "ほかのオプションと組めない"),
                            (["ECO-900", "--quarantine-journal", "--by", "EQ-007", "--executor", "EQ-002"], "ほかのオプションと組めない")):
            n_rel = jcount("release") + jcount("quarantine")
            rc_x, out_x = call(argv_)
            if rc_x != 2 or not out_x or not out_x[0].startswith("UNMEASURABLE ARG_ERROR") or frag not in out_x[0] or jcount("release") + jcount("quarantine") != n_rel:
                fails.append(f"v3c-arg {frag!r}: exit {rc_x} :: {out_x[:1]}")
        release("v2i-release", r_, OPEN_CLS)
        # V3(d): 同時の 2 解放 → 解放レコードは 1 件
        r_ = craft()
        pr_ = [child(["ECO-900", "--release", r_, "--by", "EQ-007"]) for _ in range(2)]
        outs_ = [child_out(p_, 60) for p_ in pr_]
        if jcount("release", r_) != 1 or sum(o_.startswith("RELEASED ") for o_ in outs_) != 1:
            fails.append(f"v3d-concurrent-release: records {jcount('release', r_)} :: {[o_.splitlines()[:1] for o_ in outs_]}")
        # V4(a): start の commit の失敗 → 起動しない・JOURNAL_WRITE_FAILED(判定レコードと 1 行目)
        keep_w = g_["_jwrite"]
        job_names.clear()
        g_["_jwrite"], g_["_job_create"] = boom, recording_create
        try:
            if marker.exists():
                marker.unlink()
            n0, s0 = n_decs(lg), jcount("start")
            rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
        finally:
            g_["_jwrite"], g_["_job_create"] = keep_w, keep_create
        d_x = last_dec(lg) if n_decs(lg) == n0 + 1 else {}
        time.sleep(0.3)
        if (rc_x != 2 or d_x.get("entry_code") != "JOURNAL_WRITE_FAILED" or not out_x or not out_x[0].startswith("UNMEASURABLE ECO-900 JOURNAL_WRITE_FAILED")
                or marker.exists() or jcount("start") != s0 or (IS_WIN and (not job_names or _job_query(job_names[-1])[0] != "gone"))):
            fails.append(f"v4a-start-commit-failed: exit {rc_x} / {d_x.get('entry_code')} / 起動 {marker.exists()} :: {out_x[:1]}")
        # V4(b): start の後に判定レコードが書けない → abort・起動しない・exit 2
        if marker.exists():
            marker.unlink()
        rc_x, out_x = call(["ECO-900", "--ledger", str(bad_ledger), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
        st_x = last_start()
        if rc_x != 2 or marker.exists() or jcount("abort", st_x.get("run_id")) != 1 or not out_x or "台帳を書けない" not in out_x[0]:
            fails.append(f"v4b-ledger-after-start: exit {rc_x} / abort {jcount('abort', st_x.get('run_id'))} :: {out_x[:1]}")
        # V4(c): 改行のない最後の行は無いもの → 次の書き手が切り詰めて repair(sha256)を記録
        torn_b = b'{"event": "start", "run_id": "torn'
        with open(jp, "ab") as f_:
            f_.write(torn_b)
        rc_x, out_x, n0 = dry()
        if rc_x != 0 or not out_x or not out_x[0].startswith("ADVANCE "):
            fails.append(f"v4c-torn-absent: exit {rc_x} :: {out_x[:1]}")
        rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
        data_ = jp.read_bytes()
        rep_ = [x for x in jrecs() if x.get("event") == "repair"]
        if (rc_x != 0 or torn_b in data_ or not data_.endswith(b"\n") or not rep_ or rep_[-1].get("truncated_bytes") != len(torn_b)
                or rep_[-1].get("sha256") != _sha(torn_b)):
            fails.append(f"v4c-torn-repaired: exit {rc_x} / repair {rep_[-1:]}")
        # V4(d): end の commit の失敗 → 再試行・cell レコードに journal_end: failed・実行は開いたまま
        tries = []

        def failing_end(fd, b):
            if b'"event": "end"' in b:
                tries.append(1)
                raise OSError(errno.EIO, "patched")
            return keep_w(fd, b)
        g_["_jwrite"] = failing_end
        try:
            rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
        finally:
            g_["_jwrite"] = keep_w
        ev_, st_x = (recs_of(lg) or [{}])[-1], last_start()
        if rc_x != 0 or ev_.get("event") != "cell" or ev_.get("journal_end") != "failed" or len(tries) != 4:   # S1.6: 1 回+再試行 3 回(order の数で照合する)
            fails.append(f"v4d-end-failed: exit {rc_x} / {ev_.get('journal_end')} / tries {len(tries)}")
        rc_x, out_x, n0 = dry()
        row("v4d-run-open", rc_x, out_x, OPEN_CLS, ("open_runs",) if IS_WIN else ("open_runs", "unknown_because"), st_x.get("run_id"), n0)
        release("v4d-release", st_x.get("run_id"), OPEN_CLS)
        # V4(e): 短い書き込みは失敗(start)→ 残った切れ端は次の書き手が直す
        g_["_jwrite"] = lambda fd, b: keep_w(fd, b[: len(b) // 2])
        try:
            if marker.exists():
                marker.unlink()
            rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
        finally:
            g_["_jwrite"] = keep_w
        short_tail = not jp.read_bytes().endswith(b"\n")
        if rc_x != 2 or not out_x or "JOURNAL_WRITE_FAILED" not in out_x[0] or marker.exists() or not short_tail:
            fails.append(f"v4e-short-write: exit {rc_x} / 切れ端 {short_tail} :: {out_x[:1]}")
        n_rep = jcount("repair")
        rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
        if rc_x != 0 or jcount("repair") != n_rep + 1 or not jp.read_bytes().endswith(b"\n"):
            fails.append(f"v4e-short-write-repaired: exit {rc_x} / repair {jcount('repair') - n_rep}")
        # V4(f) / V4(n) JOURNAL_CORRUPT: 完全な壊れた行 → JOURNAL_CORRUPT(位置)→ 隔離で抜ける / U+2028・U+0085 は 1 レコード
        size_f = jp.stat().st_size
        with open(jp, "ab") as f_:
            f_.write(b"garbage line\n")
        rc_x, out_x, n0 = dry()
        d_x = row("v4f-journal-corrupt", rc_x, out_x, "JOURNAL_CORRUPT", ("corrupt_offset", "open_runs"), None, n0)
        if d_x.get("corrupt_offset") != size_f or d_x.get("open_runs") != []:
            fails.append(f"v4f-journal-corrupt: offset {d_x.get('corrupt_offset')} != {size_f} / {d_x.get('open_runs')}")
        rc_x, out_x = call(["ECO-900", "--release", "any-run", "--by", "EQ-007"])
        if rc_x != 2 or out_x[:1] != [in_flight_line("ECO-900", "JOURNAL_CORRUPT")]:
            fails.append(f"v4f-release-refused-while-corrupt: exit {rc_x} :: {out_x[:1]}")
        rc_x, out_x = call(["ECO-900", "--quarantine-journal", "--by", "EQ-007"])
        rc_y, out_y, n0 = dry()
        if rc_x != 0 or not out_x or not out_x[0].startswith("QUARANTINED ECO-900 ") or rc_y != 0:
            fails.append(f"v4f-quarantined: exit {rc_x}/{rc_y} :: {out_x[:1]} {out_y[:1]}")
        n_before = len(jrecs())
        sep = "a\u2028b\u0085c\u2029d"
        cm_ = journal_commit(jp, {"event": "note", "eco": "ECO-900", "text": sep})
        after_, _t2, cor_, _x2, _e2 = journal_read(jp)
        if cm_ or len(after_) != n_before + 1 or after_[-1][1].get("text") != sep or cor_:
            fails.append(f"v4f-line-separators: {len(after_ or []) - n_before} レコード / corrupt {len(cor_)}")
        if IS_WIN and b"\r" in jp.read_bytes():   # V4(g)
            fails.append("v4g-no-cr: journal に CR がある")
        # V4(h): 待機の中断 → interrupted・cell レコード(interrupted / none)・cell interrupted・exit 2・次回は開いた実行
        def kb(p_):
            raise KeyboardInterrupt
        keep_ = g_["_wait"]
        g_["_wait"] = kb
        try:
            rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
        finally:
            g_["_wait"] = keep_
        ev_, st_x = (recs_of(lg) or [{}])[-1], last_start()
        if (rc_x != 2 or out_x[1:] != ["cell interrupted"] or ev_.get("cell_exit") != "interrupted" or ev_.get("journal_end") != "none"
                or jcount("interrupted", st_x.get("run_id")) != 1):
            fails.append(f"v4h-interrupted: exit {rc_x} / {ev_.get('cell_exit')} / {ev_.get('journal_end')} :: {out_x}")
        time.sleep(0.3)
        rc_x, out_x, n0 = dry()
        row("v4h-run-open", rc_x, out_x, OPEN_CLS, ("open_runs",) if IS_WIN else ("open_runs", "unknown_because"), st_x.get("run_id"), n0)
        release("v4h-release", st_x.get("run_id"), OPEN_CLS)
        # V4(i) / V4(n) REPORT_EXISTS: 最初の検査とロックのあいだに --report ができた → ロック下で ARG_ERROR・記録なし
        rp_i = root / "reports" / "ri.md"

        def make_report(name):
            if name == "before_lock":
                rp_i.write_text("ACCEPT\n", encoding="utf-8")
        keep_ = g_["_checkpoint"]
        g_["_checkpoint"] = make_report
        try:
            if marker.exists():
                marker.unlink()
            n0 = len(recs_of(lg))
            rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", str(brief_fx), "--executor", "EQ-002", "--report", "reports/ri.md", "--range", "境界探索"])
        finally:
            g_["_checkpoint"] = keep_
        if (rc_x != 2 or out_x[:1] != ["UNMEASURABLE ARG_ERROR: --report の宛先が既に存在する: reports/ri.md"] or marker.exists()
                or len(recs_of(lg)) != n0):
            fails.append(f"v4i-report-exists-under-lock: exit {rc_x} / 記録 {len(recs_of(lg)) - n0} :: {out_x[:1]}")
        rp_i.unlink(missing_ok=True)
        # V4(j): 3 プロセスが同じ台帳へ同時に追記 → 全行が在り解析できる
        lg_j = wout / "ledger-concurrent.jsonl"
        pr_ = [subprocess.Popen([sys.executable, str(ledf), RUN_PY, str(lg_j), str(w_), "300"]) for w_ in range(3)]
        rcs_ = [p_.wait(180) for p_ in pr_]
        got_ = set()
        bad_lines = 0
        for ln_ in (lg_j.read_text(encoding="utf-8").split("\n")[:-1] if lg_j.exists() else []):
            try:
                o_ = json.loads(ln_)
                got_.add((o_["w"], o_["i"]))
            except (ValueError, KeyError):
                bad_lines += 1
        if rcs_ != [0, 0, 0] or len(got_) != 900 or bad_lines:
            fails.append(f"v4j-ledger-concurrent: exit {rcs_} / 行 {len(got_)} / 壊れ {bad_lines}")
        # V4(l): RUN_IN_FLIGHT は job の停止語彙と配送先表の両方に在り、片側から外すと照合が落ちる
        vocab_ = set(_load("bomdd-job").STOP_VOCABULARY)
        if ("RUN_IN_FLIGHT" not in vocab_ or DELIVERY.get("RUN_IN_FLIGHT") != "operator" or vocabulary_mismatch(set(DELIVERY), vocab_)
                or not vocabulary_mismatch(set(DELIVERY) - {"RUN_IN_FLIGHT"}, vocab_) or not vocabulary_mismatch(set(DELIVERY), vocab_ - {"RUN_IN_FLIGHT"})):
            fails.append("v4l-vocabulary: RUN_IN_FLIGHT の結線(語彙・配送先・照合の陽性対照)")
        # V4(m): O3 — 3 地点の例外 → INTERNAL_ERROR・exit 2・traceback・job なし。S1.4 と待機の後は開いたまま・end の後は閉じて cell レコードなし
        keep_err0 = sys.stderr
        for point, stays_open in (("first_line", True), ("after_wait", True), ("cell_record", False)):
            err_buf = io.StringIO()
            job_names.clear()
            keep_ = g_["_checkpoint"]
            g_["_checkpoint"], g_["_job_create"], sys.stderr = raise_at(point), recording_create, err_buf
            try:
                n_cell = sum(1 for r in recs_of(lg) if r.get("event") == "cell")
                rc_x, out_x = call(["ECO-900", "--ledger", str(lg), "--cell", cell, "--brief", "none", "--executor", "EQ-002"])
            finally:
                g_["_checkpoint"], g_["_job_create"], sys.stderr = keep_, keep_create, keep_err0
            st_x = last_start()
            time.sleep(0.3)
            if (rc_x != 2 or out_x[-1:] != ["UNMEASURABLE ECO-900 INTERNAL_ERROR(RuntimeError) → operator"] or "Traceback" not in err_buf.getvalue()
                    or (IS_WIN and (not job_names or _job_query(job_names[-1])[0] != "gone"))):
                fails.append(f"v4m-{point}: exit {rc_x} / jobs {job_names} :: {out_x}")
            if stays_open:
                rc_y, out_y, n0 = dry()
                row(f"v4m-{point}-open", rc_y, out_y, OPEN_CLS, ("open_runs",) if IS_WIN else ("open_runs", "unknown_because"), st_x.get("run_id"), n0)
                release(f"v4m-{point}-release", st_x.get("run_id"), OPEN_CLS)
            elif jcount("end", st_x.get("run_id")) != 1 or sum(1 for r in recs_of(lg) if r.get("event") == "cell") != n_cell:
                fails.append(f"v4m-{point}: end {jcount('end', st_x.get('run_id'))} / cell レコードが増えた")
        # V4(o) / V4(n) JOURNAL_UNREADABLE: 在るが読めない journal
        keep_ = g_["_jread"]
        g_["_jread"] = boom
        try:
            rc_x, out_x, n0 = dry()
        finally:
            g_["_jread"] = keep_
        row("v4o-journal-unreadable", rc_x, out_x, "JOURNAL_UNREADABLE", ("journal_error",), None, n0)
        # V4(p): 拒否のレコードが書けない → 既存の台帳失敗の行・exit 2
        r_ = craft()
        rc_x, out_x = call(["ECO-900", "--ledger", str(bad_ledger)])
        if rc_x != 2 or not out_x or not out_x[0].startswith("UNMEASURABLE ARG_ERROR: 台帳を書けない"):
            fails.append(f"v4p-refusal-unwritable: exit {rc_x} :: {out_x[:1]}")
        # V4(q): 分類の違う 2 つの開いた実行 → より厳しい方を報告し、open_runs は両方
        r2_ = craft(host="another-host")
        rc_x, out_x, n0 = dry()
        d_x = row("v4q-precedence", rc_x, out_x, "UNKNOWN", ("open_runs", "unknown_because"), r2_ if IS_WIN else r_, n0)
        if d_x.get("open_runs") != [{"run_id": r_, "class": OPEN_CLS}, {"run_id": r2_, "class": "UNKNOWN"}]:
            fails.append(f"v4q-precedence: {d_x.get('open_runs')}")
        release("v4q-release-1", r_, OPEN_CLS)
        release("v4q-release-2", r2_, "UNKNOWN")
        rc_x, out_x, n0 = dry()
        if rc_x != 0:   # 腕の後始末: 開いた実行が残っていない
            fails.append(f"eco113-cleanup: 開いた実行が残る :: {out_x[:1]}")
        # 台帳の形(全レコードに event・decision 行に verifier_line と decision)
        recs = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines()]
        decs = [r for r in recs if r.get("event") == "decision"]
        if len(decs) < 10 or any("verifier_line" not in r or "decision" not in r or "executor" not in r or "independence" not in r for r in decs) or any("event" not in r for r in recs):
            fails.append(f"ledger: decision 行 {len(decs)} / 形不正")
        # 配送先表の自己整合(job 語彙と 1 対 1)
        jobmod = _load("bomdd-job")
        vocab = set(getattr(jobmod, "STOP_VOCABULARY", ()) or ())
        if vocab and vocabulary_mismatch(set(DELIVERY), vocab):
            fails.append(f"DELIVERY と job の停止語彙が一致しない: {vocabulary_mismatch(set(DELIVERY), vocab)}")
        if set(WITNESS_DELIVERY) != set(witmod.CODES):
            fails.append(f"WITNESS_DELIVERY と witness の CODES が一致しない: {sorted(set(WITNESS_DELIVERY) ^ set(witmod.CODES))}")
        # r1 IA-04: selftest 自身の報告行も 80 桁以内
        for txt in (_report_text([]), _report_text(["x"])):
            if len(txt.splitlines()[0]) > WIDTH:
                fails.append(f"selftest 報告行が {WIDTH} 桁超: {txt.splitlines()[0]}")
    return _report(fails + _CLEANUP_FAILS)


def vocabulary_mismatch(delivery: set, vocab: set) -> list:
    """R6/ECO-113 O2: 配送先表と job の停止語彙の差(1 対 1 なら空)。"""
    return sorted(delivery ^ vocab)


def _report_text(fails) -> str:
    if fails:
        return f"STOP SELFTEST_FAIL: {len(fails)} 件\n  " + "\n  ".join(fails)
    branch = "msvcrt.locking + Job Object (Windows)" if IS_WIN else "fcntl.flock, no job (POSIX, ECO-113 L1)"
    return ("ADVANCE OK: selftest PASS(起動4/dry2/kb5/job1/不能3/独立性9/報告27/gate6/構文5/台帳3/引数13/表)\n"
            f"  ECO-113 V1-V4 PASS · branch: {branch}")   # V1(g): 通った分岐を記録する


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
