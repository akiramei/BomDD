# bomdd-job — register + ECO order から job ビューを生成する read-only 射影(ECO-062 第 1 弾)
#
# 目的: 運転員(人・Bot・スクリプトを問わない)が BomDD を理解せずに工程を運ぶための
# 機械可読ビュー。**正本ではない**(register / order が正本・本ツールは導出のみ・書き戻さない)。
# 由来: ECO-062 §1-1(job は生成される射影・手書きしない)・§5 Phase 2 手動リハーサル
# (導出可 4 欄 / 出所なし 6 欄 F1〜F6 / 状態不整合 F0)。
#
# 原則(v0 で凍結):
#  1. 全欄が `source` 座標を持つ — register のキー / order の見出し / "none"(出所なし)。
#     散文からの手写し(転写値)はしない: 出所のない欄は null + source "none" で出す(F1/F3/F4/F6)。
#  2. 状態の正本は register。order のクローズ節と register.status が矛盾したら修復せず
#     停止種別 LEDGER_INCONSISTENT を出す(F0・ECO-055 の実測)。
#  3. 停止語彙は job 側の固定値(F5・ECO-062 §0.5 の 5 種+⑥台帳不整合)。台帳から導出できるのは
#     NONE / LEDGER_INCONSISTENT / MISSING_INPUT のみ — 他は receipt 由来で本ツールの被覆外と明示する。
#  4. 終了コードは常に 0(読み取り専用・判定器ではない)。--selftest のみ失敗時に exit 1。
#  5. 報告経路は明示 UTF-8(実行環境の既定符号化に依存させない — §13)。
#
# 使い方:
#   python bomdd-job.py ECO-062 [--register PATH] [--json]
#   python bomdd-job.py --all [--register PATH]      # verified 以外の全 ECO
#   python bomdd-job.py --dwell [--register PATH] [--stale-days N] [--json] [--no-cache]   # 滞留の測定(ECO-120・キャッシュ ECO-122)
#   python bomdd-job.py --selftest
#
# 検出力の限界(宣言):
#   (1) クローズ節の検出は見出し形状(「## N. クローズ」+ verified 語)のみ — 本文の意味は読まない。
#   (2) forbidden / expected_outputs / independent_inspection / required_capability は register/order に
#       構造欄がないため常に null(F2/F3/F4/F6)。
#   (3) 受入の PASS/FAIL は導出しない(witness の担当・bomdd-witness.py)。
#   (4) ECO-064(F1): required_skills は activation-map(templates/product-profile/skills/activation-map.yaml・
#       参照付き対応表)から台帳側の機械アンカーだけで導出し、skills_observed は order の receipt 見出し
#       (C16/C17 の正規表現を import・preflight は job 側)から導出、skills_missing= 差(**情報欄**・停止語彙
#       不変・gate 化しない)。map 不在 / import 不能 / order 不在は unknown(合格ではない)。契約の**意味**は
#       測らない — map の source は所在参照のみで、契約が変われば所在が腐る(selftest は実在まで)。
#       認識依存のトリガー(calibrate ②④)は機械化しない。
#   (5) ECO-072(F2): required_capability は order の配員欄(`- producer: EQ-NNN` / `- inspector: EQ-NNN`・fence 外)から
#       読み、設備台帳 bomdd/70-equipment.yaml で実在確認する。欄なし= null(従来どおり・停止しない)。値が EQ-NNN 構文外・
#       同一 role に異なる id・台帳に無い id は LEDGER_INCONSISTENT、台帳が読めないのに宣言がある場合は MISSING_INPUT(fail-closed)。
#       独立性の判定(producer vs executor)は job の責務外(入口 bomdd-run.py --executor)。停止語彙に INDEPENDENCE_FAIL を
#       追加するが job は導出しない(被覆宣言のとおり)。
#   (6) ECO-077(F7): 役割 → 使用可能スキル集合の結線。activation-map の各 class は `roles`(語彙= producer / inspector・
#       配員欄と同じ)を持ち、required_skills_by_role= 該当 class の required_skills を roles ごとに集めたもの(**情報欄**・
#       停止語彙不変・gate 化しない)。receipt_author_role は register の同名欄(任意・観測欄: 受入時の較正 receipt を書いた役割)
#       をそのまま射影する— 欄なし= null(停止しない)。役割の**禁止**は導出しない(禁止はリポ面で観測できる項目
#       〔allowed_paths・commit・register 遷移・receipt 著者〕にのみ置く— playbook §8.5)。roles 欠落・語彙外・重複は MAP_INVALID。
#   (7) ECO-112(G2): required_gates は register の同名欄(機械の写し)と order の `required_gates:` 行(行頭・fence/HTML コメント外に
#       1 本・裁定の記録)を集合として照合して射影する。両方なし= null(停止しない)。片方だけ・行が 2 本以上・形状不正(非空文字列の重複なし
#       list でない)・集合の不一致は LEDGER_INCONSISTENT。起票後に両方を同時に変えても検出しない(ECO-112 L2)。読むのは入口(bomdd-run R12)。
#   (8) ECO-120(--dwell): 滞留の**測定**ビュー(gate ではない・job レコードと stop_type に触れない・exit 0)。register の git 履歴の
#       全コミットを読み(cat-file --batch・大きい履歴は並列)、open の各エントリが現在の status に入ったコミットを導出する
#       (手書きの since は持たない — §13)。waiting_on(語彙 WAITING_VOCAB)と top-level paused も同じく履歴から開始を導出する。
#       読めないコミットは警告で名指しし黙って捨てない。未コミットの作業は dirty パス数と最古 mtime(下限)と register の HEAD 差で示す。
#       測らないもの: status や理由が正しいか・誰も走らせなければ何も出ない・終端 status(applied 等)での滞留。
#       ECO-122: コマンド行では blob ごとの解析結果をキャッシュ(dwell_cache_dir_default()・どのリポジトリの外)に置いて使い回す。
#       キャッシュは履歴からの導出で、消してよい(次の実行が全部読み直す)。標準出力は変わらず、数は標準エラーへ。--no-cache で使わない。
#       形の正しい誤ったエントリは信じる(内容アドレスのキャッシュは見分けられない)— 疑わしければ --no-cache。

import io
import json
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

STOP_VOCABULARY = (
    "NONE",                  # 進行可
    "NORMATIVE_RULING",      # ① 規範判断が要る(gate ①・converge 裁定点)→ 人
    "VERIFICATION_FAIL",     # ② 検査赤(stop/report)→ 工場へ差し戻し
    "BOM_CONTRADICTION",     # ③ BOM 自己矛盾(blocked)→ 設計者
    "CONVERGENCE_LIMIT",     # ④ 未収束の上限到達 → 裁定点(再実行ではない)
    "PREFLIGHT_HOLD",        # ⑤ 開始条件不成立 → 工程判定
    "LEDGER_INCONSISTENT",   # ⑥ 台帳不整合(register と order の状態矛盾)→ 台帳の所有者
    "MISSING_INPUT",         # 欠測(order 不在・register 不能)— 測定不能は合格ではない
    "INDEPENDENCE_FAIL",     # ⑦ 独立性不成立(producer と executor が同一 id / 3 軸一致 / 軸 unknown)→ 運転員(配員のやり直し)。入口が導出・ECO-072
    "INSPECTION_MISSING",    # ⑧ verified かつ inspector 宣言なのに witness に inspection gate がない → 運転員(独立検査の結果回収)。入口が導出・ECO-074
    "RUN_IN_FLIGHT",         # ⑨ 同じ変更の別の起動が実行中・終わりを記録しない実行が残る・run journal の欠陥 → 運転員。入口が導出(台帳から導出しない)・ECO-113
)
DERIVABLE_FROM_LEDGER = ("NONE", "LEDGER_INCONSISTENT", "MISSING_INPUT")

EQUIPMENT_REL = "bomdd/70-equipment.yaml"
EQ_ID_RE = re.compile(r"^EQ-\d{3}$")
ASSIGN_RE = re.compile(r"^[ \t]{0,3}-[ \t]*(producer|inspector)[ \t]*:[ \t]*(\S+)", re.M)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
HEAD_RE = re.compile(r"^[ \t]{0,3}(#{1,6})[ \t]+([^\n]*)$", re.M)
EQUIP_HEAD_RE = re.compile(r"担当設備|equipment", re.I)
INDEPENDENCE_AXES = ("model", "harness", "account_lineage")
CLOSE_HEAD_RE = re.compile(r"^[ \t]{0,3}#{2,6}[ \t]+\d+\.[ \t]*クローズ[^\n]*verified", re.M)
FENCE_RE = re.compile(r"^[ \t]{0,3}(```|~~~)[^\n]*\n.*?(?:^[ \t]{0,3}\1[ \t]*$|\Z)", re.S | re.M)
REQ_GATES_LINE_RE = re.compile(r"^required_gates:([^\n]*)$", re.M)   # ECO-112 G1: column 0・fence と HTML コメントの外

# --- ECO-064(F1): activation-map と receipt 突合 -------------------------------------------
# 対応表の正本= method/templates/product-profile/skills/activation-map.yaml(契約の所在参照のみ・転写しない)。
# converge 要否(C16 hard-positive)と receipt 見出しの正規表現は self-conformance.py から import(正本 1 つ)。
# preflight receipt の見出し(ECO-042 様式)は C 検査が未整備のため job 側で検出する。
TOOLS_DIR = Path(__file__).resolve().parent
MAP_PATH = TOOLS_DIR.parent / "templates" / "product-profile" / "skills" / "activation-map.yaml"
PREFLIGHT_RECEIPT_RE = re.compile(r"^[ \t]{0,3}#{2,6}[ \t]+[^\n]*?/?preflight\s*receipt\b", re.I | re.M)


def _load_selfconf():
    """self-conformance.py の正規表現を import する(失敗= None・呼び側は unknown にする)。"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("bomdd_selfconf", TOOLS_DIR / "self-conformance.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {"hard": mod.CONVERGE_HARD_POSITIVES, "converge": mod.CONVERGE_RECEIPT_HEAD_RE,
                "calibrate": mod.C17_RECEIPT_RE, "strip": mod._strip_fences_all}
    except Exception:  # noqa: BLE001 — import 不能は測定不能として上位で unknown にする
        return None


ANCHOR_KINDS = ("always", "ledger-status", "affected-refs-glob", "order-hard-positive")
# ECO-077(F7): roles の語彙= order 配員欄(ASSIGN_RE)と同じ 2 語。役割の追加は配員欄・設備台帳と同時に(ここだけ増やさない)。
ROLE_VOCAB = ("producer", "inspector")
SKILL_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]*")   # IA-09(r3): canonical な skill ID 文法(bomdd-init の SKILLS と同じ命名)
# IA-11(r4): statuses は register の状態語彙(60-change-register.yaml テンプレ冒頭の宣言+実運用の filed / in-progress)に限定
REGISTER_STATUSES = ("proposed", "filed", "decided", "in-progress", "implemented", "applied", "verified", "rejected", "superseded")
# IA-10(r4): instrument_paths の正規形 — リポ相対(先頭 `/`・ドライブ・`..` 禁止)・前後空白なし・`\` 不可・`**` 単独(全一致)禁止
INSTRUMENT_PATH_RE = re.compile(r"(?!.*(?:^|/)\.\.(?:/|$))[A-Za-z0-9_.*?\-]+(?:/[A-Za-z0-9_.*?\-]+)*")


def _is_str_list(v) -> bool:
    return isinstance(v, list) and all(isinstance(s, str) and s.strip() for s in v)


def validate_map(classes, base: Path) -> list:
    """IA-01/IA-04(r1): class の形状(型)と source の参照実在(ファイル+`#` 以降の literal 断片)を検査し、問題を列挙する。
    .md の断片は見出し行(# で始まる行)に含まれること・.py その他は本文に含まれることを要求する。意味の一致は測らない。"""
    problems = []
    if not isinstance(classes, list) or not classes:
        return ["classes 配列なし"]
    seen = set()
    for i, cls in enumerate(classes):
        if not isinstance(cls, dict):
            problems.append(f"class[{i}] が object でない")
            continue
        cid = cls.get("id")
        tag = f"class {cid!r}" if isinstance(cid, str) else f"class[{i}]"
        if not isinstance(cid, str) or not cid.strip():
            problems.append(f"{tag}: id が文字列でないか空")  # IA-07(r2): unhashable な id を seen に入れない
        elif cid in seen:
            problems.append(f"{tag}: id 重複")
        else:
            seen.add(cid)
        if not _is_str_list(cls.get("required_skills")) or not cls.get("required_skills"):
            problems.append(f"{tag}: required_skills が非空の文字列配列でない")
        else:
            # IA-09(r3): canonical な skill ID 文法(小文字英数と `-`)+ skills/ 直下の実ファイル名との大小文字込みの完全一致
            # (Windows の大小文字非区別 FS と `..` の逸脱を排除)+ 重複拒否。
            skills_dir = base / "method" / "templates" / "product-profile" / "skills"
            try:
                canonical = {p.stem for p in skills_dir.iterdir() if p.suffix == ".md"}
            except OSError:
                canonical = set()
            seen_skills = set()
            for s in cls["required_skills"]:
                if not SKILL_ID_RE.fullmatch(s):
                    problems.append(f"{tag}: スキル ID {s!r} が文法外(小文字英数と - のみ)")
                elif s not in canonical:
                    problems.append(f"{tag}: スキル {s} が skills/ 直下に実在しない(大小文字込みの完全一致)")
                if s in seen_skills:
                    problems.append(f"{tag}: required_skills に重複 {s!r}")
                seen_skills.add(s)
        # ECO-077(F7): roles は非空の文字列配列・語彙内(ROLE_VOCAB)・重複なし。欠落は無言の「全役割」にせず不正(fail-closed)
        roles = cls.get("roles")
        if not _is_str_list(roles) or not roles:
            problems.append(f"{tag}: roles が非空の文字列配列でない")
        else:
            seen_roles = set()
            for r in roles:
                if r not in ROLE_VOCAB:
                    problems.append(f"{tag}: roles の値 {r!r} が語彙 {ROLE_VOCAB} にない")
                if r in seen_roles:
                    problems.append(f"{tag}: roles に重複 {r!r}")
                seen_roles.add(r)
        kind = cls.get("anchor_kind")
        if kind not in ANCHOR_KINDS:
            problems.append(f"{tag}: anchor_kind 不正 {kind!r}")
        if kind == "ledger-status":
            sts = cls.get("statuses")
            if not _is_str_list(sts) or not sts:
                problems.append(f"{tag}: statuses が非空の文字列配列でない")  # IA-08(r2): 空配列は class を無言で無効化するため不正
            else:
                for s in sts:  # IA-11(r4): 語彙外(大小文字・前後空白違いを含む)は無言の非該当になるため不正
                    if s not in REGISTER_STATUSES:
                        problems.append(f"{tag}: statuses の値 {s!r} が register の状態語彙にない")
        if kind == "affected-refs-glob":
            ips = cls.get("instrument_paths")
            if not _is_str_list(ips) or not ips:
                problems.append(f"{tag}: instrument_paths が非空の文字列配列でない")
            else:
                for pth in ips:  # IA-10(r4): 非正規パス(絶対・前後空白・`\`・`..`・`**` 単独)は無言の非該当/全一致になるため不正
                    if pth != pth.strip() or "\\" in pth or not INSTRUMENT_PATH_RE.fullmatch(pth):
                        problems.append(f"{tag}: instrument_paths の値 {pth!r} が正規形でない(リポ相対・前後空白なし・`/` 区切り)")
                    elif pth.replace("*", "").replace("/", "") == "":
                        problems.append(f"{tag}: instrument_paths の値 {pth!r} は全一致(literal 区間なし)のため不正")
        if not isinstance(cls.get("anchor"), str) or not cls["anchor"].strip():
            problems.append(f"{tag}: anchor が空")
        src = cls.get("source")
        if not isinstance(src, str) or not src.strip():
            problems.append(f"{tag}: source が空")
            continue
        for part in src.split(";"):
            part = part.strip()
            if not part:
                problems.append(f"{tag}: source に空要素(; 区切り)がある")  # IA-06(r2): 空要素は不正
                continue
            fp, _, frag = part.partition("#")
            fpath = base / fp.strip()
            if not fpath.is_file():
                problems.append(f"{tag}: source {fp.strip()} が実在しない")
                continue
            frag = frag.strip()
            if not frag:
                problems.append(f"{tag}: source {fp.strip()} に # 断片がない")
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                problems.append(f"{tag}: source {fp.strip()} を読めない")
                continue
            if fpath.suffix == ".md":
                ok = any(line.lstrip().startswith("#") and frag in line for line in text.splitlines())
            else:
                ok = frag in text
            if not ok:
                problems.append(f"{tag}: source 断片 '{frag}' が {fp.strip()} に実在しない")
    return problems


def load_map(path: Path = MAP_PATH, base: Path | None = None):
    """activation-map を読み validate する。(classes, None) / (None, 理由)。不正な map は使わない(fail-closed・unknown 側)。"""
    if yaml is None:
        return None, "PyYAML 不在"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        return None, f"activation-map 読取不能: {e}"
    classes = (data or {}).get("classes") if isinstance(data, dict) else None
    if not isinstance(classes, list) or not classes:
        return None, "activation-map 形状不正(classes 配列なし)"
    if base is None:
        base = path.resolve().parents[4] if len(path.resolve().parents) > 4 else path.resolve().parent
    try:
        problems = validate_map(classes, base)
    except Exception as e:  # noqa: BLE001 — IA-07(r2): validator 自身の例外も MAP_INVALID(exit 0 契約の最終防御)
        problems = [f"validate_map が例外終了: {type(e).__name__}"]
    if problems:
        return None, "activation-map 不正(MAP_INVALID): " + " / ".join(problems[:5]) + (" …" if len(problems) > 5 else "")
    return classes, None


def _glob_match(ref: str, pattern: str) -> bool:
    """IA-02(r1): 区切りを跨がない glob。`*` は 1 階層内・`**` は複数階層。`\\` は `/` へ正規化(OS 非依存)。"""
    r = ref.replace("\\", "/")
    p = pattern.replace("\\", "/")
    out = ""
    i = 0
    while i < len(p):
        c = p[i]
        if c == "*":
            if i + 1 < len(p) and p[i + 1] == "*":
                out += ".*"
                i += 2
                continue
            out += "[^/]*"
        elif c == "?":
            out += "[^/]"
        else:
            out += re.escape(c)
        i += 1
    return re.fullmatch(out, r) is not None


def _class_matches(cls: dict, entry: dict, order_text: str | None, sc) -> bool | None:
    """anchor_kind ごとの機械判定。None= 判定不能(unknown)。"""
    kind = cls.get("anchor_kind")
    if kind == "always":
        return True
    if kind == "ledger-status":
        statuses = cls.get("statuses")
        if not _is_str_list(statuses) or not statuses:  # IA-01/IA-08: 型不正・空配列は判定不能(validate_map が先に弾くが防御的に)
            return None
        return str(entry.get("status")) in statuses
    if kind == "affected-refs-glob":
        pats = cls.get("instrument_paths")
        if not _is_str_list(pats) or not pats:
            return None
        refs_raw = entry.get("affected_refs")
        refs = [str(r) for r in refs_raw] if isinstance(refs_raw, list) else []
        return any(_glob_match(r, p) for r in refs for p in pats)  # IA-02: 区切りを跨がない
    if kind == "order-hard-positive":
        if order_text is None or sc is None:
            return None
        text = sc["strip"](order_text)
        return any(rx.search(text) for _, rx in sc["hard"])
    return None


def observed_skills(order_text: str | None, sc) -> list | None:
    """order の receipt 見出しから起動済みスキルを導出(fence 除去後)。None= 判定不能。"""
    if order_text is None or sc is None:
        return None
    text = sc["strip"](order_text)
    out = []
    if PREFLIGHT_RECEIPT_RE.search(text):
        out.append("preflight")
    if sc["converge"].search(text):
        out.append("converge")
    if sc["calibrate"].search(text):
        out.append("calibrate")
    return out


def _field(value, source):
    return {"value": value, "source": source}


def load_equipment(root: Path, rel: str = EQUIPMENT_REL):
    """設備台帳を読み {id: entry} を返す。(dict, None) / (None, 理由)。形状不正・id 構文外・重複は不正(fail-closed)。"""
    if yaml is None:
        return None, "PyYAML 不在"
    try:
        data = yaml.safe_load((root / rel).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        return None, f"設備台帳 読取不能: {e.__class__.__name__}"
    items = (data or {}).get("equipment") if isinstance(data, dict) else None
    if not isinstance(items, list) or not items:
        return None, "設備台帳 形状不正(equipment 配列なし)"
    out = {}
    for i, e in enumerate(items):
        if not isinstance(e, dict) or not isinstance(e.get("id"), str) or not EQ_ID_RE.match(e["id"]):
            return None, f"設備台帳 entry[{i}] の id が EQ-NNN でない"
        for ax in INDEPENDENCE_AXES:   # r1 IA-01: 未選択 entry でも 3 軸は「文字列か欠落」以外を台帳不正として弾く(台帳全体の形状)
            if ax in e and e[ax] is not None and not isinstance(e[ax], str):
                return None, f"設備台帳 {e['id']} の {ax} が文字列でない({type(e[ax]).__name__})"
        if e["id"] in out:
            return None, f"設備台帳 id 重複: {e['id']}"
        out[e["id"]] = e
    return out, None


def equipment_sections(text: str) -> str:
    """r1 IA-03: 見出しに「担当設備」/「equipment」を含む節(次の同位以上の見出しまで)だけを連結して返す。節がなければ空文字。"""
    heads = list(HEAD_RE.finditer(text))
    out = []
    for i, h in enumerate(heads):
        if not EQUIP_HEAD_RE.search(h.group(2)):
            continue
        level = len(h.group(1))
        end = len(text)
        for nxt in heads[i + 1:]:
            if len(nxt.group(1)) <= level:
                end = nxt.start()
                break
        out.append(text[h.end():end])
    return "\n".join(out)


def assignments(order_text: str) -> dict:
    """order の配員欄を role → [値…] で返す(出現順・重複込み)。fence と HTML コメントを除去し、担当設備節の中だけを読む(use/mention の区別・r1 IA-03)。"""
    text = HTML_COMMENT_RE.sub("", FENCE_RE.sub("", order_text))
    text = equipment_sections(text)
    found = {"producer": [], "inspector": []}
    for m in ASSIGN_RE.finditer(text):
        found[m.group(1)].append(m.group(2))
    return found


def resolve_capability(order_text: str, root: Path):
    """ECO-072(F2): (value, source, stop, reason)。value は {producer, inspector}(未宣言は None)。欄なしは (None, none…, None, None)。"""
    found = assignments(order_text)
    if not found["producer"] and not found["inspector"]:
        return None, "none(F2: order の担当設備節に配員欄〔- producer: EQ-NNN / - inspector: EQ-NNN〕なし)", None, None
    value = {}
    for role in ("producer", "inspector"):
        vals = found[role]
        if not vals:
            value[role] = None
            continue
        bad = [v for v in vals if not EQ_ID_RE.match(v)]
        if bad:
            return None, "order 配員欄", "LEDGER_INCONSISTENT", f"order の {role} 値が EQ-NNN 構文でない: {bad[0]!r}"
        if len(set(vals)) > 1:
            return None, "order 配員欄", "LEDGER_INCONSISTENT", f"order の {role} に異なる id: {sorted(set(vals))}"
        value[role] = vals[0]
    eq, err = load_equipment(root)
    if eq is None:
        return None, "order 配員欄", "MISSING_INPUT", f"配員欄があるが設備台帳を読めない: {err}"
    for role, eid in value.items():
        if eid is not None and eid not in eq:
            return None, "order 配員欄", "LEDGER_INCONSISTENT", f"order の {role} {eid} が設備台帳 {EQUIPMENT_REL} にない"
    src = f"order 担当設備節の配員欄(- producer/inspector: EQ-NNN・fence/HTML コメント外)+{EQUIPMENT_REL} で実在確認(独立性の判定は入口 bomdd-run --executor)"
    return value, src, None, None


def _gate_list(v):
    """G2: 非空文字列の list で重複なし → list。それ以外 → None。"""
    if not isinstance(v, list) or not v or not all(isinstance(x, str) and x.strip() and x == x.strip() for x in v):
        return None
    return v if len(set(v)) == len(v) else None


def resolve_required_gates(entry: dict, order_text: str | None):
    """ECO-112 G1/G2: (value, source, stop, reason)。register の required_gates(機械の写し)と order の `required_gates:` 行(裁定の記録)が
    集合として一致することを要求する。両方なし= (None, none…, None, None)。不一致・形状不正・行の重複 → LEDGER_INCONSISTENT。"""
    has_field = "required_gates" in entry
    lines = []
    if order_text is not None:
        lines = REQ_GATES_LINE_RE.findall(HTML_COMMENT_RE.sub("", FENCE_RE.sub("", order_text)))
    if not has_field and not lines:
        return None, "none(G1: register に required_gates なし・order に required_gates: 行なし)", None, None
    src = "register の required_gates(機械の写し)= order の required_gates: 行(裁定の記録・column 0・fence/HTML コメント外)"
    if len(lines) > 1:
        return None, src, "LEDGER_INCONSISTENT", f"order に required_gates: 行が {len(lines)} 本ある(1 本に限る)"
    if not has_field:
        return None, src, "LEDGER_INCONSISTENT", "order に required_gates: 行があるが register に required_gates がない"
    if not lines:
        return None, src, "LEDGER_INCONSISTENT", "register に required_gates があるが order に required_gates: 行がない"
    reg = _gate_list(entry.get("required_gates"))
    if reg is None:
        return None, src, "LEDGER_INCONSISTENT", f"register の required_gates が非空文字列の重複なし list でない: {entry.get('required_gates')!r}"
    try:
        parsed = yaml.safe_load(lines[0]) if yaml is not None else None
    except yaml.YAMLError:
        parsed = None
    ordl = _gate_list(parsed)
    if ordl is None:
        return None, src, "LEDGER_INCONSISTENT", f"order の required_gates: 行を非空文字列の重複なし list として読めない: {lines[0].strip()!r}"
    if set(reg) != set(ordl):
        return None, src, "LEDGER_INCONSISTENT", f"register {sorted(reg)} と order {sorted(ordl)} の required_gates が一致しない"
    return list(reg), src, None, None


def load_register(path: Path):
    if yaml is None:
        return None, "PyYAML 不在"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        return None, f"register 読取不能: {e}"
    if not isinstance(data, dict) or not isinstance(data.get("changes"), list):
        return None, "register 形状不正(changes 配列なし)"
    return data["changes"], None


def project(entry: dict, root: Path, register_rel: str, amap=None, map_err: str | None = None, sc=None) -> dict:
    """amap= activation-map の classes(None= 不在/不能・map_err に理由)/ sc= self-conformance の正規表現(None= import 不能)。"""
    eco = str(entry.get("id"))
    da = entry.get("diff_audit") or {}
    order_ref = entry.get("order_ref")
    job = {
        "job": _field(f"JOB-{eco}", f"{register_rel}:{eco}.id(導出)"),
        "eco": _field(eco, f"{register_rel}:{eco}.id"),
        "objective": _field(entry.get("title"), f"{register_rel}:{eco}.title"),
        "state": _field(entry.get("status"), f"{register_rel}:{eco}.status(状態の正本)"),
        "inputs": _field({"order_ref": order_ref, "affected_refs": entry.get("affected_refs")},
                         f"{register_rel}:{eco}.order_ref/affected_refs"),
        "write_scope": _field(da.get("allowed_paths"), f"{register_rel}:{eco}.diff_audit.allowed_paths"),
        "diff_baseline": _field(da.get("baseline"), f"{register_rel}:{eco}.diff_audit.baseline"),
        "required_skills": _field(None, "〔後段で導出〕"),
        "required_skills_by_role": _field(None, "〔後段で導出〕"),
        "receipt_author_role": _field(entry.get("receipt_author_role") if isinstance(entry.get("receipt_author_role"), str) else None,
                                      f"{register_rel}:{eco}.receipt_author_role(F7 観測欄・ECO-077: 受入時の較正 receipt を書いた役割。欄なし= null・停止しない)"),
        "required_capability": _field(None, "none(F2: 設備認定 ID の欄なし — 第 1 弾対象外)"),
        "forbidden": _field(None, "none(F3: order「採らない」は散文 — 転写しない)"),
        "expected_outputs": _field(None, "none(F4: order §1 は散文 — 転写しない)"),
        "independent_inspection": _field(None, "none(F6: 配員欄に inspector なし — verification 散文は転写しない)"),
        "required_gates": _field(None, "none(G1: order 不在のため未照合)" if "required_gates" in entry else "none(G1: register に required_gates なし)"),
        "stop_vocabulary": _field(list(STOP_VOCABULARY), "bomdd-job.py 固定値(F5)"),
        "stop_derivable_from_ledger": _field(list(DERIVABLE_FROM_LEDGER), "bomdd-job.py 固定値(被覆宣言)"),
    }
    # 停止種別の導出(台帳のみから)
    stop, reason = "NONE", "register と order の状態に矛盾なし"
    order_text = None
    if not order_ref:
        stop, reason = "MISSING_INPUT", "order_ref なし(検査対象が特定不能)"
    else:
        op = root / order_ref
        if not op.exists():
            stop, reason = "MISSING_INPUT", f"order 不在: {order_ref}"
        else:
            order_text = op.read_text(encoding="utf-8", errors="replace")
            text = FENCE_RE.sub("", order_text)
            closed = bool(CLOSE_HEAD_RE.search(text))
            status = str(entry.get("status"))
            if closed and status != "verified":
                stop, reason = "LEDGER_INCONSISTENT", f"order にクローズ節(verified)があるが register.status={status}"
            elif status == "verified" and not closed:
                stop, reason = "LEDGER_INCONSISTENT", "register.status=verified だが order にクローズ節(verified)がない"
            # ECO-072(F2): 配員欄 → required_capability(設備台帳で実在確認)。台帳由来の停止が先(既存の停止を上書きしない)
            cap, cap_src, cap_stop, cap_reason = resolve_capability(order_text, root)
            job["required_capability"] = _field(cap, cap_src)
            if isinstance(cap, dict) and cap.get("inspector"):   # ECO-074(F6): inspector 宣言 → 独立検査が要る(verified 昇格は witness の inspection gate を要求)
                job["independent_inspection"] = _field({"required": True, "inspector": cap["inspector"]},
                                                        "order 配員欄 inspector(ECO-074: verified 昇格には witness の inspection gate〔台帳から導出〕が要る)")
            if stop == "NONE" and cap_stop:
                stop, reason = cap_stop, cap_reason
            # ECO-112 G2: required_gates(register と order の一致)。台帳由来の停止が先(既存の停止を上書きしない)
            rg, rg_src, rg_stop, rg_reason = resolve_required_gates(entry, order_text)
            job["required_gates"] = _field(rg, rg_src)
            if stop == "NONE" and rg_stop:
                stop, reason = rg_stop, rg_reason
    job["stop_type"] = _field(stop, f"導出: {reason}")

    # ECO-064(F1): required_skills(activation-map)・skills_observed(order の receipt 見出し)・skills_missing(差・情報欄)
    if amap is None:
        job["required_skills"] = _field(None, f"unknown(理由コード MAP_MISSING: {map_err or 'activation-map 不在'})")
        job["required_skills_by_role"] = _field(None, "unknown(required が判定不能)")
    else:
        req, matched, undecidable, by_role = [], [], [], {}
        for cls in amap:
            m = _class_matches(cls, entry, order_text, sc)
            if m is None:
                undecidable.append(str(cls.get("id")))
            elif m:
                matched.append(str(cls.get("id")))
                for s in cls.get("required_skills") or []:
                    if s not in req:
                        req.append(str(s))
                    for r in cls.get("roles") or []:   # ECO-077(F7): 役割 → スキル集合(validate 済み map では roles は非空・語彙内)
                        by_role.setdefault(str(r), [])
                        if s not in by_role[str(r)]:
                            by_role[str(r)].append(str(s))
        # IA-12(r4): required は集合 — 配列順は class の宣言順に依存させず辞書順で固定(class 列挙も同様)
        req = sorted(req)
        matched = sorted(matched)
        undecidable = sorted(undecidable)
        by_role = {r: sorted(v) for r, v in sorted(by_role.items())}
        src = f"activation-map.yaml: {', '.join(matched) or '(該当 class なし)'}"
        if undecidable:
            src += f" / 判定不能 class= {', '.join(undecidable)}(order 不在または self-conformance import 不能)"
        job["required_skills"] = _field(req, src)
        job["required_skills_by_role"] = _field(by_role, "導出: 該当 class の required_skills を roles ごとに集合化(F7 情報欄・役割パッケージの入力・gate 化しない)")
    obs = observed_skills(order_text, sc)
    if obs is None:
        job["skills_observed"] = _field(None, "unknown(order 不在または self-conformance import 不能)")
        job["skills_missing"] = _field(None, "unknown(observed が判定不能)")
    else:
        job["skills_observed"] = _field(obs, "order の receipt 見出し(fence 除去後・C16/C17 の正規表現を import・preflight は job 側の見出し検出)")
        req_v = job["required_skills"]["value"]
        if req_v is None:
            job["skills_missing"] = _field(None, "unknown(required が判定不能)")
        else:
            job["skills_missing"] = _field([s for s in req_v if s not in obs],
                                           "導出: required − observed(情報欄・停止語彙不変・gate 化しない — playbook §8.5)")
    return job


def render(job: dict) -> str:
    out = []
    for k, f in job.items():
        v = f["value"]
        vs = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
        out.append(f"{k}: {vs}\n  source: {f['source']}")
    return "\n".join(out) + "\n"


# --- selftest(陽性対照: 整合 / 不整合 2 方向 / order 不在 / 出所なし欄が null) ---------------
def selftest() -> int:
    # ECO-068: selftest 自身の前提(OS temp)不在は traceback でなく UNMEASURABLE の 1 行・exit 2(job は git を使わない)
    try:
        td_cm = tempfile.TemporaryDirectory()
    except OSError as e:
        print(f"UNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE): selftest の前提不在 — {e.__class__.__name__}: {str(e)[:120]}")
        return 2
    rc = _selftest_body(td_cm)
    return max(rc, _dwell_selftest())   # ECO-120: --dwell の腕(git を使う — 既存の腕は git を使わないので分ける)


def _set_times_back(path: Path, epoch: float) -> bool:
    """fixture 用: mtime と(Windows では)作成日時を epoch に戻す。作成日時を戻せたら True(ctime は他の OS では設定できない)。"""
    import os
    os.utime(path, (epoch, epoch))
    if os.name != "nt":
        return False
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
                                wintypes.DWORD, wintypes.HANDLE)
    h = k32.CreateFileW(str(path), 0x100, 0x7, None, 3, 0x02000000, None)   # FILE_WRITE_ATTRIBUTES・共有全部・OPEN_EXISTING
    if h in (None, wintypes.HANDLE(-1).value):
        return False
    try:
        t = int((epoch + 11644473600) * 10**7)
        ft = wintypes.FILETIME(t & 0xFFFFFFFF, t >> 32)
        return bool(k32.SetFileTime(h, ctypes.byref(ft), None, ctypes.byref(ft)))
    finally:
        k32.CloseHandle(h)


def _dwell_cache_arms(root: Path, reg: Path, now, cdir: Path, commit, fails: list) -> list:
    """ECO-122 P3 の腕。root は読めないコミットを 1 つ含む fixture。走った腕の名前を返す。"""
    ran = []

    def run(cache_dir):
        st = {}
        return json.dumps(dwell(reg, 14, now, cache_dir=cache_dir, stats=st), ensure_ascii=False, sort_keys=True), st

    def check(arm, got, want, st, **expect):
        ran.append(arm)
        if got != want:
            fails.append(f"cache {arm}: 結果が --no-cache と違う")
        for k, v in expect.items():
            if st.get(k) != v:
                fails.append(f"cache {arm}: {k}={st.get(k)!r} != {v!r}")

    base, _ = run(None)
    n = json.loads(base)["commits_read"]   # fixture の全コミットが register の blob を持つ(hits はコミットで数える)
    rel = reg.relative_to(root).as_posix()
    shas = _dwell_git(root, "log", "--format=%H", "--", rel).split()
    d = len({_dwell_git(root, "rev-parse", f"{s}:{rel}").strip() for s in shas})   # 解析は異なる blob ごとに 1 回(A→B→A は 2 度目を読まない)
    if d >= n:
        fails.append(f"cache: fixture に同じ内容の版がない({d} blob / {n} コミット)— 重複の腕が効かない")
    got, st = run(cdir)
    check("cold", got, base, st, hits=0, parsed=d, read_miss="absent", write="ok")
    path = Path(st["file"])
    got, st = run(cdir)
    check("warm", got, base, st, hits=n, parsed=0, read_miss=None, write=None)
    if not any("読めないコミット" in w for w in json.loads(got)["warnings"]):
        fails.append("cache warm: 読めないコミットの警告が温かい実行で消えた")
    raw = path.read_text(encoding="utf-8")
    path.write_text(raw[: len(raw) // 2], encoding="utf-8")   # 途中で切れたファイル
    got, st = run(cdir)
    check("truncated", got, base, st, hits=0, parsed=d, read_miss="not JSON", write="ok")
    data = json.loads(path.read_text(encoding="utf-8"))
    data["key"] = "0" * 64
    path.write_text(json.dumps(data), encoding="utf-8")
    got, st = run(cdir)
    check("version-key", got, base, st, hits=0, parsed=d, read_miss="version key differs", write="ok")
    blocked = cdir.parent / "not-a-dir"
    blocked.write_text("x", encoding="utf-8")   # キャッシュの置き場がファイル = 書けない
    got, st = run(blocked)
    check("unwritable", got, base, st, hits=0, parsed=d)
    if not str(st.get("write", "")).startswith(("FileExistsError", "NotADirectoryError", "FileNotFoundError", "PermissionError", "OSError")):
        fails.append(f"cache unwritable: 書けない理由が出ない: {st.get('write')!r}")
    text = reg.read_text(encoding="utf-8")
    commit(root, reg, text.replace("ECO-002", "ECO-009", 1) if "ECO-002" in text else text + "#\n", 4)   # 新しいコミット 1 つ
    base2, _ = run(None)
    got, st = run(cdir)
    check("one-new-commit", got, base2, st, hits=n, parsed=1, read_miss=None, write="ok")
    return ran


def _dwell_selftest() -> int:
    """ECO-120 V2-V4 の腕: 改変した履歴・理由と一時停止・未コミットの作業・直列と並列の一致・引数。"""
    import contextlib
    import datetime as dt
    import os
    import subprocess
    if yaml is None:
        print("bomdd-job dwell selftest UNMEASURABLE: PyYAML 不在")
        return 2
    now = dt.datetime(2026, 11, 4, 12, 0, tzinfo=dt.timezone.utc)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@x", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    fails = []
    v4_note = ["30 日の腕は未到達"]

    def git(root, *a, days_ago=None):
        e = dict(env)
        if days_ago is not None:
            e["GIT_AUTHOR_DATE"] = e["GIT_COMMITTER_DATE"] = (now - dt.timedelta(days=days_ago)).isoformat()
        r = subprocess.run(["git", "-C", str(root), *a], capture_output=True, env=e)
        if r.returncode != 0:
            raise RuntimeError(f"fixture git {a[:2]}: {r.stderr.decode(errors='replace')[:120]}")
        return r.stdout.decode(errors="replace").strip()

    def repo(root):
        root.mkdir()
        git(root, "init", "-q")
        git(root, "config", "core.autocrlf", "false")
        (root / "bomdd").mkdir()
        return root / "bomdd" / "60-change-register.yaml"

    def commit(root, reg, text, days_ago):
        reg.write_text(text, encoding="utf-8", newline="\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", f"d-{days_ago}", days_ago=days_ago)
        return git(root, "rev-parse", "HEAD")

    def by_id(r):
        return {o["id"]: o for o in r["open"]}

    def blk(entries, ind="  "):   # ブロック形式の register(ind= リストの字下げ)
        out = "changes:\n"
        for eid, st, extra in entries:
            out += f"{ind}- id: {eid}\n{ind}  title: t\n{ind}  status: {st}\n" + "".join(f"{ind}  {k}: {v}\n" for k, v in extra)
        return out

    try:
        with tempfile.TemporaryDirectory() as td:
            # --- V2: 改変した履歴(各腕が 1 つの近道の known-bad) ---
            ra = Path(td) / "a"
            reg = repo(ra)
            e3 = ("ECO-003", "filed", [])   # 3 件目: (c) で ECO-002 の行が「動いた側」になるように(2 件だと diff は相手を動かす)
            c1 = commit(ra, reg, blk([("ECO-002", "implemented", []), ("ECO-001", "filed", []), e3]), 60)
            commit(ra, reg, blk([("ECO-002", "implemented", []), ("ECO-001", "implemented", []), e3]), 50)
            c3 = commit(ra, reg, blk([("ECO-002", "implemented", []), ("ECO-001", "filed", []), e3]), 40)
            c4 = commit(ra, reg, blk([("ECO-002", "implemented", []), ("ECO-001", "filed", []), e3], ind="    "), 30)   # (b) 字下げだけ
            c5 = commit(ra, reg, blk([("ECO-001", "filed", []), e3, ("ECO-002", "implemented", [])], ind="    "), 20)   # (c) 並べ替えだけ
            c6 = commit(ra, reg, "changes: [ {id: ECO-001, status: filed\n", 10)                                        # (d) 読めない
            commit(ra, reg, blk([("ECO-001", "filed", []), e3, ("ECO-002", "implemented", [])], ind="    "), 5)
            reg.write_text(blk([("ECO-001", "filed", []), e3, ("ECO-002", "verified", [])], ind="    "), encoding="utf-8", newline="\n")  # (e)
            r = dwell(reg, 14, now)
            o = by_id(r)
            if o.get("ECO-001", {}).get("since_commit") != c3:
                fails.append(f"V2(a) A→B→A: ECO-001 の開始 {o.get('ECO-001', {}).get('since_commit', '')[:10]} != 2 度目の A {c3[:10]}")
            if o.get("ECO-002", {}).get("since_commit") != c1:
                fails.append(f"V2(b)(c)(e) ECO-002 の開始 {o.get('ECO-002', {}).get('since_commit', '')[:10]} != {c1[:10]}(字下げ・並べ替え・作業木で動いた)")
            if r["parse_failures"] != 1 or not any(c6[:10] in w for w in r["warnings"]):
                fails.append(f"V2(d) 読めないコミット {c6[:10]} が警告で名指しされない: {r['warnings']}")
            if not r["uncommitted"]["register_differs_from_head"]:
                fails.append("V2(e) 作業木だけの変更で register の HEAD 差が出ない")
            # known-bad: 「status 行に最後に触ったコミット」の近道は (b)(c) で開始を動かす — 腕が区別することを示す
            for rev, want_bad, arm in ((c4, c4, "b"), (c5, c5, "c")):
                text = git(ra, "show", f"{rev}:bomdd/60-change-register.yaml").splitlines()
                n = next(i for i, l in enumerate(text, 1)
                         if l.strip() == "status: implemented" and "ECO-002" in "\n".join(text[max(0, i - 4):i]))
                blamed = git(ra, "blame", "--porcelain", "-L", f"{n},{n}", rev, "--", "bomdd/60-change-register.yaml").split()[0]
                if blamed != want_bad or blamed == c1:
                    fails.append(f"V2 known-bad({arm}): 近道が {blamed[:10]} を返した(期待 {want_bad[:10]}・腕が区別しない)")
            # 直列と並列は同じ結果
            r1, r2 = dwell(reg, 14, now, workers=1), dwell(reg, 14, now, workers=2)
            if (r1["open"], r1["warnings"]) != (r2["open"], r2["warnings"]):
                fails.append("直列と並列で結果が違う")

            # --- ECO-122 P3: blob ごとのキャッシュ(冷・温・なしで同じ結果・新しいコミットだけ読む・壊れたキャッシュは外れ) ---
            cache_n = len(_dwell_cache_arms(ra, reg, now, Path(td) / "cache", commit, fails))

            # --- V3: 理由・閾値・一時停止 ---
            rb = Path(td) / "b"
            regb = repo(rb)
            ents = [("ECO-079", "implemented", []), ("ECO-010", "filed", [("waiting_on", "start-instruction")]),
                    ("ECO-011", "implemented", [("waiting_on", "human-acceptance")]),
                    ("ECO-012", "implemented", [("waiting_on", "independent-inspection")]),
                    ("ECO-013", "filed", [("waiting_on", "human-ruling")]), ("ECO-014", "filed", [("waiting_on", "eco:ECO-VT-163")]),
                    ("ECO-015", "filed", [("waiting_on", "external")]), ("ECO-016", "filed", [("waiting_on", "bogus")]),
                    ("ECO-017", "verified", [("waiting_on", "external")])]
            commit(rb, regb, blk(ents), 49)
            commit(rb, regb, blk(ents + [("ECO-020", "filed", [])]), 3)
            r = dwell(regb, 14, now)
            o = by_id(r)
            groups = {e["group"] for e in r["open"] if e["over_threshold"]}
            want = {"none", "start-instruction", "human-acceptance", "independent-inspection", "human-ruling", "eco:ECO-VT-163",
                    "external", "bogus"}
            if groups != want:
                fails.append(f"V3 理由の群: {sorted(groups)} != {sorted(want)}")
            if not any("ECO-016" in w and "語彙外" in w for w in r["warnings"]):
                fails.append("V3 語彙外の waiting_on が警告にならない")
            if not any("ECO-017" in w and "終端" in w for w in r["warnings"]):
                fails.append("V3 終端 status の waiting_on が警告にならない")
            unexplained = [e["id"] for e in r["open"] if e["over_threshold"] and e["group"] == "none"]
            if unexplained != ["ECO-079"] or o["ECO-079"]["days"] != 49.0:
                fails.append(f"V3 ECO-079 形(49 日・理由なし)が unexplained に出ない: {unexplained} / {o.get('ECO-079')}")
            if o["ECO-020"]["over_threshold"] or not by_id(dwell(regb, 2, now))["ECO-020"]["over_threshold"]:
                fails.append("V3 閾値: 3 日の ECO-020 が 14 日で出る / 2 日で出ない")
            if "unexplained(閾値超・理由なし) 1:" not in render_dwell(r):
                fails.append("V3 render に unexplained 1 件が出ない")
            # job レコードと stop_type は waiting_on で変わらない
            (rb / "bomdd" / "o.md").write_text("# Change Order — ECO-016\n", encoding="utf-8")
            base = {"id": "ECO-016", "title": "t", "status": "filed", "order_ref": "bomdd/o.md"}
            j0 = project(dict(base), rb, "bomdd/60-change-register.yaml")
            j1 = project(dict(base, waiting_on="bogus"), rb, "bomdd/60-change-register.yaml")
            if j0 != j1:
                fails.append("V3 waiting_on で job レコードが変わった")
            p_ok = blk(ents + [("ECO-020", "filed", [])]) + "paused:\n  reason: r\n  resume_when: w\n"
            cp = commit(rb, regb, p_ok, 1)
            r = dwell(regb, 14, now)
            if not r["paused"] or r["paused"]["since_commit"] != cp or {e["group"] for e in r["open"]} != {"paused"}:
                fails.append(f"V3 paused: 群が paused だけにならない / 開始が違う: {r['paused']}")
            if any("paused" in w for w in r["warnings"]):
                fails.append("V3 両欄ある paused に警告が出た")
            commit(rb, regb, blk(ents + [("ECO-020", "filed", [])]) + "paused:\n  reason: r\n", 0.5)
            if not any("resume_when" in w for w in dwell(regb, 14, now)["warnings"]):
                fails.append("V3 resume_when のない paused が警告にならない")

            # --- V4: 未コミットの作業(年齢は下限) ---
            rc_ = Path(td) / "c"
            regc = repo(rc_)
            (rc_ / "a.txt").write_text("a\n", encoding="utf-8")
            commit(rc_, regc, blk([("ECO-001", "filed", [])]), 2)
            real_now = dt.datetime.now(dt.timezone.utc)
            (rc_ / "a.txt").write_text("a2\n", encoding="utf-8")
            (rc_ / "b.txt").write_text("b\n", encoding="utf-8")
            (rc_ / "c.txt").write_text("c\n", encoding="utf-8")
            win = _set_times_back(rc_ / "a.txt", real_now.timestamp() - 30 * 86400)
            _set_times_back(rc_ / "b.txt", real_now.timestamp() - 10 * 86400)
            os.utime(rc_ / "c.txt", (real_now.timestamp() - 3000 * 86400,) * 2)   # 古い mtime を保って今置かれたファイル
            u = dwell(regc, 14, real_now)["uncommitted"]
            if u["dirty_paths"] != 3 or u["register_differs_from_head"]:
                fails.append(f"V4 dirty 3・HEAD 差なし になっていない: {u}")
            if (u["oldest_days_lower_bound"] or 0) > 31:
                fails.append(f"V4 古い mtime だけのファイルで年齢が過大(作成日時を見ていない): {u}")
            v4_note[0] = "30 日の腕は実行(作成日時も戻した)" if win else "30 日の腕は未実行(作成日時を戻せない OS)"
            if win and abs((u["oldest_days_lower_bound"] or 0) - 30) > 1:
                fails.append(f"V4 最古 30 日(作成日時も 30 日前)になっていない: {u}")
            git(rc_, "checkout", "--", "a.txt")
            (rc_ / "b.txt").unlink()
            (rc_ / "c.txt").unlink()
            u = dwell(regc, 14, real_now)["uncommitted"]
            if u != {"dirty_paths": 0, "oldest_days_lower_bound": None, "register_differs_from_head": False}:
                fails.append(f"V4 clean で dirty 0・年齢なし にならない: {u}")
            regc.write_text(blk([("ECO-001", "implemented", [])]), encoding="utf-8", newline="\n")
            if not dwell(regc, 14, real_now)["uncommitted"]["register_differs_from_head"]:
                fails.append("V4 register の未コミット変更で HEAD 差が出ない")

            # --- 引数(exit 0・1 行で返す) ---
            for argv, frag in ((["--dwell", "--stale-days", "0"], "--stale-days"), (["--dwell", "--bogus"], "未知のオプション"),
                               (["--dwell", "--register"], "値がない"),
                               (["--dwell", "--register", str(Path(td) / "nope.yaml")], "測定不能")):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = dwell_main(argv)
                if rc != 0 or not buf.getvalue().startswith("MISSING_INPUT") or frag not in buf.getvalue():
                    fails.append(f"引数 {argv}: rc={rc} 出力={buf.getvalue()[:80]!r}")
    except Exception as e:  # noqa: BLE001 — fixture の構築失敗は測定不能
        print(f"bomdd-job dwell selftest UNMEASURABLE: {type(e).__name__}: {str(e)[:160]}")
        return 2
    if fails:
        print("bomdd-job dwell selftest FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("bomdd-job dwell selftest PASS(ECO-120: V2 A→B→A・字下げ・並べ替え・読めないコミット・作業木だけの変更・近道の known-bad 2 腕・"
          "直列=並列 / V3 理由 7 群+語彙外・終端の警告・ECO-079 形・閾値 14/2・job 不変・paused 群/警告 / V4 dirty 年齢・古い mtime だけの"
          f"ファイル・clean・register の HEAD 差・{v4_note[0]} / 引数 4 種 / ECO-122 キャッシュ {cache_n} 腕: 冷・温(警告は残る)・途中で切れた"
          "ファイル・別の版キー・書けない置き場・新しいコミット 1 つ)")
    return 0


def _selftest_body(td_cm) -> int:
    fails = []
    with td_cm as td:
        root = Path(td)
        (root / "bomdd").mkdir()
        reg = root / "bomdd" / "60-change-register.yaml"
        (root / "bomdd" / "open.md").write_text("# Change Order — ECO-901\n\n## 3. 受入\n- 検討中\n", encoding="utf-8")
        (root / "bomdd" / "closed.md").write_text(
            "# Change Order — ECO-902\n\n## 6. クローズ(2026-09-03・verified)\n- 受入 PASS\n"
            "```\n## 9. クローズ(fence 内・verified)\n```\n", encoding="utf-8")
        (root / "bomdd" / "fenced.md").write_text(
            "# Change Order — ECO-904\n\n```\n## 6. クローズ(2026-09-03・verified)\n```\n", encoding="utf-8")
        reg.write_text(
            "changes:\n"
            "  - {id: ECO-901, title: t1, status: decided, order_ref: bomdd/open.md, affected_refs: [a.py],\n"
            "     diff_audit: {baseline: abc, allowed_paths: [a.py]}}\n"
            "  - {id: ECO-902, title: t2, status: in-progress, order_ref: bomdd/closed.md}\n"
            "  - {id: ECO-903, title: t3, status: verified, order_ref: bomdd/missing.md}\n"
            "  - {id: ECO-904, title: t4, status: verified, order_ref: bomdd/fenced.md}\n"
            "  - {id: ECO-905, title: t5, status: verified, order_ref: bomdd/closed.md}\n",
            encoding="utf-8")
        entries, err = load_register(reg)
        if err:
            return _report([f"fixture register 読取: {err}"])
        jobs = {e["id"]: project(e, root, "bomdd/60-change-register.yaml") for e in entries}
        exp = {"ECO-901": "NONE", "ECO-902": "LEDGER_INCONSISTENT", "ECO-903": "MISSING_INPUT",
               "ECO-904": "LEDGER_INCONSISTENT", "ECO-905": "NONE"}
        for k, want in exp.items():
            got = jobs[k]["stop_type"]["value"]
            if got != want:
                fails.append(f"{k}: stop_type {got} != {want}")
        j = jobs["ECO-901"]
        if j["write_scope"]["value"] != ["a.py"] or j["job"]["value"] != "JOB-ECO-901":
            fails.append("ECO-901: 導出欄が不正")
        for k in ("forbidden", "expected_outputs", "independent_inspection", "required_capability"):
            if j[k]["value"] is not None or not j[k]["source"].startswith("none"):
                fails.append(f"ECO-901: {k} は null + source none であるべき")
        # ECO-064: 上記 jobs は map/sc なしで project したため required は unknown(理由コード)であるべき
        if j["required_skills"]["value"] is not None or "MAP_MISSING" not in j["required_skills"]["source"]:
            fails.append(f"ECO-901: map なし project の required が unknown(MAP_MISSING)でない: {j['required_skills']}")
        if any("source" not in f for f in j.values()):
            fails.append("全欄 source 必須")
        # --- ECO-072(F2): 配員欄 → required_capability(設備台帳で実在確認)---
        (root / "bomdd" / "70-equipment.yaml").write_text(
            "equipment:\n  - {id: EQ-001, kind: ai-model, model: m1, harness: h1, account_lineage: a1}\n"
            "  - {id: EQ-002, kind: ai-model, model: m2, harness: h2, account_lineage: a2}\n", encoding="utf-8")
        (root / "bomdd" / "cap.md").write_text("# ECO-911\n\n## 担当設備\n\n- producer: EQ-001\n- inspector: EQ-002\n\n```\n- producer: EQ-999\n```\n\n<!-- - inspector: EQ-999 -->\n", encoding="utf-8")
        (root / "bomdd" / "cap-unknown.md").write_text("# ECO-912\n\n## 担当設備\n\n- producer: EQ-999\n", encoding="utf-8")
        (root / "bomdd" / "cap-syntax.md").write_text("# ECO-913\n\n## 担当設備\n\n- producer: <EQ-NNN>\n", encoding="utf-8")
        (root / "bomdd" / "cap-dup.md").write_text("# ECO-914\n\n## 担当設備\n\n- producer: EQ-001\n- producer: EQ-002\n", encoding="utf-8")
        # r1 IA-03: HTML コメント内・担当設備節の外(他節・節なし)の言及は配員でない
        (root / "bomdd" / "cap-mention.md").write_text(
            "# ECO-915\n\n<!--\n- producer: EQ-001\n-->\n\n## 説明\n\n- producer: EQ-001\n\n## 担当設備\n\n<!-- - producer: EQ-002 -->\n\n## 3. 受入\n\n- producer: EQ-002\n",
            encoding="utf-8")
        (root / "bomdd" / "cap-nosec.md").write_text("# ECO-916\n\n- producer: EQ-001\n", encoding="utf-8")
        (root / "bomdd" / "cap-sub.md").write_text("# ECO-917\n\n## 担当設備(equipment)\n\n### 製造\n\n- producer: EQ-001\n\n## 次\n\n- inspector: EQ-002\n", encoding="utf-8")
        mk = lambda i, o: {"id": i, "title": "t", "status": "decided", "order_ref": o}  # noqa: E731
        jc = project(mk("ECO-911", "bomdd/cap.md"), root, "bomdd/60-change-register.yaml")
        if jc["required_capability"]["value"] != {"producer": "EQ-001", "inspector": "EQ-002"} or jc["stop_type"]["value"] != "NONE":
            fails.append(f"F2: 配員欄の解決が不正(fence 内は無視): {jc['required_capability']} / {jc['stop_type']}")
        if jc["independent_inspection"]["value"] != {"required": True, "inspector": "EQ-002"}:   # ECO-074 F6
            fails.append(f"F6: inspector 宣言から independent_inspection が導出されない: {jc['independent_inspection']}")
        for i, o, want in (("ECO-912", "bomdd/cap-unknown.md", "LEDGER_INCONSISTENT"), ("ECO-913", "bomdd/cap-syntax.md", "LEDGER_INCONSISTENT"),
                           ("ECO-914", "bomdd/cap-dup.md", "LEDGER_INCONSISTENT")):
            jx = project(mk(i, o), root, "bomdd/60-change-register.yaml")
            if jx["stop_type"]["value"] != want or jx["required_capability"]["value"] is not None:
                fails.append(f"F2: {o} が {want} でない: {jx['stop_type']} / {jx['required_capability']}")
        for i, o in (("ECO-915", "bomdd/cap-mention.md"), ("ECO-916", "bomdd/cap-nosec.md")):
            jm2 = project(mk(i, o), root, "bomdd/60-change-register.yaml")
            if jm2["required_capability"]["value"] is not None or jm2["stop_type"]["value"] != "NONE":
                fails.append(f"IA-03: {o} の言及が配員として解決された: {jm2['required_capability']} / {jm2['stop_type']}")
        js2 = project(mk("ECO-917", "bomdd/cap-sub.md"), root, "bomdd/60-change-register.yaml")
        if js2["required_capability"]["value"] != {"producer": "EQ-001", "inspector": None}:
            fails.append(f"IA-03: 担当設備節の下位見出しは節内・次の同位見出し以降は節外 であるべき: {js2['required_capability']}")
        if js2["independent_inspection"]["value"] is not None:   # ECO-074 F6: inspector なしは null のまま
            fails.append(f"F6: inspector なしで independent_inspection が null でない: {js2['independent_inspection']}")
        # --- ECO-112 G2: required_gates(register の写し = order の required_gates: 行)---
        gdir = root / "bomdd"
        (gdir / "g-ok.md").write_text("# ECO-920\n\nrequired_gates: [V1, V2]\n\n```\nrequired_gates: [X]\n```\n<!--\nrequired_gates: [Y]\n-->\n"
                                      "prose `required_gates: [Z]` mid-line\n", encoding="utf-8")
        (gdir / "g-two.md").write_text("# ECO-921\n\nrequired_gates: [V1]\nrequired_gates: [V1]\n", encoding="utf-8")
        (gdir / "g-bad.md").write_text("# ECO-922\n\nrequired_gates: V1 and V2\n", encoding="utf-8")
        (gdir / "g-none.md").write_text("# ECO-923\n\nno line here\n", encoding="utf-8")
        mg = lambda i, o, **kw: dict({"id": i, "title": "t", "status": "decided", "order_ref": o}, **kw)  # noqa: E731
        g_cases = (("g-equal", mg("ECO-920", "bomdd/g-ok.md", required_gates=["V2", "V1"]), "NONE", ["V2", "V1"]),
                   ("g-differ", mg("ECO-920", "bomdd/g-ok.md", required_gates=["V1"]), "LEDGER_INCONSISTENT", None),
                   ("g-field-missing", mg("ECO-920", "bomdd/g-ok.md"), "LEDGER_INCONSISTENT", None),
                   ("g-line-missing", mg("ECO-923", "bomdd/g-none.md", required_gates=["V1"]), "LEDGER_INCONSISTENT", None),
                   ("g-two-lines", mg("ECO-921", "bomdd/g-two.md", required_gates=["V1"]), "LEDGER_INCONSISTENT", None),
                   ("g-unparsable", mg("ECO-922", "bomdd/g-bad.md", required_gates=["V1", "V2"]), "LEDGER_INCONSISTENT", None),
                   ("g-dup", mg("ECO-920", "bomdd/g-ok.md", required_gates=["V1", "V1", "V2"]), "LEDGER_INCONSISTENT", None),
                   ("g-not-strings", mg("ECO-920", "bomdd/g-ok.md", required_gates=["V1", 2]), "LEDGER_INCONSISTENT", None),
                   ("g-both-absent", mg("ECO-923", "bomdd/g-none.md"), "NONE", None))
        for gname, gentry, gwant, gval in g_cases:
            gj = project(gentry, root, "bomdd/60-change-register.yaml")
            if gj["stop_type"]["value"] != gwant or gj["required_gates"]["value"] != gval:
                fails.append(f"G2 {gname}: stop {gj['stop_type']['value']} / gates {gj['required_gates']['value']}(期待 {gwant} / {gval})")
            if gwant == "LEDGER_INCONSISTENT" and "required_gates" not in gj["stop_type"]["source"]:
                fails.append(f"G2 {gname}: 停止の理由が required_gates を名指ししない: {gj['stop_type']['source']}")
        # r1 IA-01: 未選択 entry の 3 軸が非文字列 → 台帳不正(MISSING_INPUT)
        (root / "bomdd" / "70-equipment.yaml").write_text(
            "equipment:\n  - {id: EQ-001, model: m1, harness: h1, account_lineage: a1}\n  - {id: EQ-002, model: m2, harness: h2, account_lineage: a2}\n"
            "  - {id: EQ-003, model: [bad], harness: h3, account_lineage: a3}\n", encoding="utf-8")
        if load_equipment(root)[0] is not None:
            fails.append("IA-01: 未選択 entry の list 軸を load_equipment が通した")
        jb = project(mk("ECO-911", "bomdd/cap.md"), root, "bomdd/60-change-register.yaml")
        if jb["stop_type"]["value"] != "MISSING_INPUT":
            fails.append(f"IA-01: 軸が非文字列の台帳+宣言ありが MISSING_INPUT でない: {jb['stop_type']}")
        (root / "bomdd" / "70-equipment.yaml").write_text("equipment:\n  - {id: EQ-001, model: ~, harness: h1, account_lineage: 7}\n", encoding="utf-8")
        if load_equipment(root)[0] is not None:
            fails.append("IA-01: 数値の軸を load_equipment が通した")
        (root / "bomdd" / "70-equipment.yaml").write_text("equipment:\n  - {id: EQ-001, model: ~, harness: h1}\n", encoding="utf-8")
        if load_equipment(root)[0] is None:
            fails.append("IA-01: null/欠落の軸(unknown 扱い)を load_equipment が弾いた")
        (root / "bomdd" / "70-equipment.yaml").unlink()
        jl = project(mk("ECO-911", "bomdd/cap.md"), root, "bomdd/60-change-register.yaml")
        if jl["stop_type"]["value"] != "MISSING_INPUT":
            fails.append(f"F2: 台帳不在+宣言ありが MISSING_INPUT でない: {jl['stop_type']}")
        (root / "bomdd" / "70-equipment.yaml").write_text("equipment:\n  - {id: EQ-001, model: m1}\n  - {id: EQ-001, model: m1}\n", encoding="utf-8")
        if load_equipment(root)[0] is not None:
            fails.append("F2: id 重複の設備台帳を load_equipment が通した")
        (root / "bomdd" / "70-equipment.yaml").write_text("equipment:\n  - {id: EQ-1, model: m1}\n", encoding="utf-8")
        if load_equipment(root)[0] is not None:
            fails.append("F2: id 構文外の設備台帳を load_equipment が通した")
        (root / "bomdd" / "70-equipment.yaml").unlink()
        if j["required_capability"]["value"] is not None or "F2" not in j["required_capability"]["source"]:
            fails.append("F2: 配員欄なしの order で required_capability が null+F2 でない")
        # --- r2 追加腕(独立検査 IA-04 / IA-05 の陽性対照)---
        rel = "bomdd/60-change-register.yaml"
        jobs, _ = select(["ECO-901", "ECO-902", "--json", "--register", rel], root)
        doc = json.loads(json.dumps({"register": rel, "jobs": jobs}, ensure_ascii=False))
        if len(doc["jobs"]) != 2 or {j["eco"]["value"] for j in doc["jobs"]} != {"ECO-901", "ECO-902"}:
            fails.append("IA-04: 複数 job が単一 JSON 文書に 2 件で入るべき")
        jobs, _ = select(["--register"], root)
        if jobs[0]["stop_type"]["value"] != "MISSING_INPUT":
            fails.append("IA-05: --register 値なしが MISSING_INPUT でない")
        jobs, _ = select(["ECO-999", "--register", rel], root)
        if jobs[0]["stop_type"]["value"] != "MISSING_INPUT" or jobs[0]["eco"]["value"] != "ECO-999":
            fails.append("IA-05: 不在 ECO が MISSING_INPUT レコードでない")
        reg2 = root / "bomdd" / "null.yaml"
        reg2.write_text("changes:\n  - ~\n  - {id: ECO-906, title: t6, status: decided, order_ref: bomdd/open.md}\n", encoding="utf-8")
        jobs, _ = select(["--all", "--register", "bomdd/null.yaml"], root)
        kinds = sorted(j["stop_type"]["value"] for j in jobs)
        if kinds != ["MISSING_INPUT", "NONE"]:
            fails.append(f"IA-05: null エントリの扱いが不正: {kinds}")
        # IA-07(r2): 対象指定なし・未知オプションは空 jobs でなく MISSING_INPUT レコード
        for argv_bad in (["--json", "--register", rel], ["--bogus", "ECO-901", "--register", rel]):
            jobs, _ = select(argv_bad, root)
            if len(jobs) != 1 or jobs[0]["stop_type"]["value"] != "MISSING_INPUT":
                fails.append(f"IA-07: {argv_bad} が MISSING_INPUT レコードでない: {jobs}")
        # --- ECO-064(F1): activation-map と receipt 突合 ---
        amap, map_err = load_map()
        sc = _load_selfconf()
        if amap is None:
            fails.append(f"F1: 実 activation-map が読めない: {map_err}")
        if sc is None:
            fails.append("F1: self-conformance の正規表現を import できない")
        if amap is not None:
            skills_dir = MAP_PATH.parent
            for cls in amap:
                for k in ("id", "required_skills", "roles", "anchor_kind", "anchor", "source"):   # ECO-077: roles を必須キーに
                    if k not in cls:
                        fails.append(f"F1 V3: class {cls.get('id')} に {k} がない")
                for s in cls.get("required_skills") or []:
                    if not (skills_dir / f"{s}.md").exists():
                        fails.append(f"F1 V3: class {cls.get('id')} のスキル {s} が skills/ に実在しない")
                for src in str(cls.get("source", "")).split(";"):
                    fp = src.strip().split("#")[0].strip()
                    if fp and not (TOOLS_DIR.parent.parent / fp).exists():
                        fails.append(f"F1 V3: class {cls.get('id')} の source {fp} が実在しない")
        if amap is not None and sc is not None:
            # 陽性対照: design-synthesis(残ゲート= hard-positive)/ instrument-change(method/tools/x.py)/ verified / receipt 検出(fence 内は無視)
            (root / "bomdd" / "f1-pos.md").write_text(
                "# ECO-907\n\n## 6. 残ゲート\n- gate ① 裁定\n\n## /preflight receipt(起動経路: 自発)\n- ok\n\n"
                "## /converge receipt(起動経路: 自発)\n- 判定: 収束\n\n### 較正 receipt\n- 査定した主張\n", encoding="utf-8")
            (root / "bomdd" / "f1-neg.md").write_text(
                "# ECO-908\n\n## 1. 変更\n- 事実の記録のみ\n\n```\n## /converge receipt(fence 内)\n### 較正 receipt(fence 内)\n## /preflight receipt(fence 内)\n```\n",
                encoding="utf-8")
            pos = {"id": "ECO-907", "status": "verified", "order_ref": "bomdd/f1-pos.md", "affected_refs": ["method/tools/x.py"]}
            neg = {"id": "ECO-908", "status": "decided", "order_ref": "bomdd/f1-neg.md", "affected_refs": ["docs/a.md"]}
            jp = project(pos, root, rel, amap, None, sc)
            jn = project(neg, root, rel, amap, None, sc)
            if sorted(jp["required_skills"]["value"]) != ["calibrate", "converge", "preflight"]:
                fails.append(f"F1: 陽性 required が不正: {jp['required_skills']}")
            if jp["skills_observed"]["value"] != ["preflight", "converge", "calibrate"] or jp["skills_missing"]["value"] != []:
                fails.append(f"F1: 陽性 observed/missing が不正: {jp['skills_observed']} / {jp['skills_missing']}")
            if jn["required_skills"]["value"] != ["preflight"] or jn["skills_observed"]["value"] != [] or jn["skills_missing"]["value"] != ["preflight"]:
                fails.append(f"F1: 陰性(fence 内 receipt 無視・start のみ)が不正: {jn['required_skills']} / {jn['skills_observed']} / {jn['skills_missing']}")
            # --- ECO-077(F7): 役割 → スキル集合(情報欄)・receipt_author_role の射影 ---
            if jp["required_skills_by_role"]["value"] != {"inspector": ["calibrate"], "producer": ["calibrate", "converge", "preflight"]}:
                fails.append(f"F7: 陽性 by_role が不正: {jp['required_skills_by_role']}")
            if jn["required_skills_by_role"]["value"] != {"producer": ["preflight"]}:
                fails.append(f"F7: 陰性 by_role が不正: {jn['required_skills_by_role']}")
            if jp["receipt_author_role"]["value"] is not None:
                fails.append(f"F7: register 欄なしの receipt_author_role が null でない: {jp['receipt_author_role']}")
            jr = project(dict(pos, receipt_author_role="producer"), root, rel, amap, None, sc)
            if jr["receipt_author_role"]["value"] != "producer" or "観測欄" not in jr["receipt_author_role"]["source"]:
                fails.append(f"F7: receipt_author_role の射影が不正: {jr['receipt_author_role']}")
            jr2 = project(dict(pos, receipt_author_role=["producer"]), root, rel, amap, None, sc)
            if jr2["receipt_author_role"]["value"] is not None:
                fails.append(f"F7: 文字列でない receipt_author_role が null にならない: {jr2['receipt_author_role']}")
            if jr["stop_type"]["value"] != jp["stop_type"]["value"] or jr["required_skills"] != jp["required_skills"]:
                fails.append("F7: receipt_author_role の有無で stop_type / required_skills が変わる(gate 化している)")
            st_ = next(c for c in amap if c.get("id") == "start")
            for badroles in (None, [], ["promoter"], ["producer", "producer"], "producer", ["Producer"]):
                bc = dict(st_, roles=badroles)
                if badroles is None:
                    bc.pop("roles", None)   # 欠落(キーなし)も不正
                if not validate_map([bc], MAP_PATH.resolve().parents[4]):
                    fails.append(f"F7: roles={badroles!r} を validate_map が通した")
            if validate_map([dict(st_, roles=["inspector", "producer"])], MAP_PATH.resolve().parents[4]):
                fails.append("F7: 語彙内の roles を validate_map が弾いた")
            # map 不在 → required unknown(missing も unknown)/ sc 不能 → observed unknown・design-synthesis 判定不能
            ju = project(pos, root, rel, None, "activation-map 不在", sc)
            if ju["required_skills"]["value"] is not None or not ju["required_skills"]["source"].startswith("unknown"):
                fails.append("F1: map 不在で required が unknown でない")
            if ju["skills_missing"]["value"] is not None:
                fails.append("F1: map 不在で missing が unknown でない")
            if ju["required_skills_by_role"]["value"] is not None or not ju["required_skills_by_role"]["source"].startswith("unknown"):
                fails.append("F7: map 不在で by_role が unknown でない")
            js = project(pos, root, rel, amap, None, None)
            if js["skills_observed"]["value"] is not None or "判定不能 class= design-synthesis" not in js["required_skills"]["source"]:
                fails.append(f"F1: sc 不能で observed unknown / design-synthesis 判定不能 でない: {js['required_skills']['source']}")
            # order 不在 → observed unknown・required は台帳アンカー分のみ+design 判定不能
            jm = project({"id": "ECO-909", "status": "filed", "order_ref": "bomdd/none.md"}, root, rel, amap, None, sc)
            if jm["skills_observed"]["value"] is not None or jm["required_skills"]["value"] != ["preflight"]:
                fails.append(f"F1: order 不在の扱いが不正: {jm['required_skills']} / {jm['skills_observed']}")
            # --- 独立検査 r1(ECO-064)の陽性対照 ---
            base = MAP_PATH.resolve().parents[4]
            # IA-04: source 断片の陰性対照 — 断片を「不存在」にした map は validate_map が弾く / 実 map は 0 件
            if validate_map(amap, base):
                fails.append(f"IA-04: 実 map に validate 問題: {validate_map(amap, base)}")
            tampered = [dict(c, source=str(c.get("source")).split("#")[0] + "#不存在") for c in amap]
            if not validate_map(tampered, base):
                fails.append("IA-04: 断片不存在の map を validate_map が通した")
            # IA-01: statuses の型不正(int / str / dict)は traceback でなく MAP_INVALID(unknown)・判定関数は None
            vp = next(c for c in amap if c.get("id") == "verified-promotion")
            for badv in (7, "verified", {"verified": 1}):
                badc = dict(vp, statuses=badv)
                if _class_matches(badc, {"status": "verified"}, None, sc) is not None:
                    fails.append(f"IA-01: statuses={badv!r} が判定不能(None)でない")
                mp = root / "bomdd" / "bad-map.yaml"
                mp.write_text("classes:\n  - {id: verified-promotion, required_skills: [calibrate], anchor_kind: ledger-status,\n"
                              f"     statuses: {json.dumps(badv)}, anchor: a, source: 'method/templates/product-profile/skills/calibrate.md#自発起動契約'}}\n",
                              encoding="utf-8")
                cl, er = load_map(mp, base)
                if cl is not None or "MAP_INVALID" not in (er or ""):
                    fails.append(f"IA-01: statuses={badv!r} の map が MAP_INVALID にならない: {er}")
            # IA-02: glob は区切りを跨がない・`\\` は `/` に正規化・`**` は複数階層
            ic = next(c for c in amap if c.get("id") == "instrument-change")
            for ref, want in (("method/tools/x.py", True), ("method/tools/sub/x.py", False), ("method" + chr(92) + "tools" + chr(92) + "x.py", True),
                              ("docs/x.py", False), ("bomdd/hooks/pre-push", True)):
                got = _class_matches(ic, {"affected_refs": [ref]}, None, sc)
                if got is not want:
                    fails.append(f"IA-02: glob {ref!r} -> {got}(期待 {want})")
            if not _glob_match("a/b/c/x.py", "a/**/x.py") or _glob_match("a/b/x.py", "a/*/*/x.py"):
                fails.append("IA-02: ** / * の階層意味が不正")
            # anchor_kind 不正・required_skills のスキル不在も MAP_INVALID
            mp = root / "bomdd" / "bad-map2.yaml"
            mp.write_text("classes:\n  - {id: x, required_skills: [nosuchskill], anchor_kind: bogus, anchor: a, source: 'method/tools/self-conformance.py#C17_SCOPE_MIN'}\n",
                          encoding="utf-8")
            cl, er = load_map(mp, base)
            if cl is not None or "MAP_INVALID" not in (er or ""):
                fails.append(f"validate: anchor_kind 不正/スキル不在の map が MAP_INVALID にならない: {er}")
            # --- 独立検査 r2(ECO-064)の陽性対照 ---
            st = next(c for c in amap if c.get("id") == "start")
            # IA-06: source の ; 区切り空要素は不正
            if not validate_map([dict(st, source=st["source"] + " ; ; " + st["source"])], base):
                fails.append("IA-06: source の空要素を validate_map が通した")
            if not validate_map([dict(st, source="; " + st["source"])], base):
                fails.append("IA-06: 先頭の空要素を validate_map が通した")
            # IA-07: unhashable な id(list / dict)は traceback でなく問題として列挙・load_map は MAP_INVALID
            for badid in (["start"], {"a": 1}, None, 3):
                try:
                    if not validate_map([dict(st, id=badid)], base):
                        fails.append(f"IA-07: id={badid!r} を validate_map が通した")
                except Exception as e:  # noqa: BLE001
                    fails.append(f"IA-07: id={badid!r} で validate_map が例外 {type(e).__name__}")
            mp = root / "bomdd" / "bad-map3.yaml"
            mp.write_text("classes:\n  - {id: [start], required_skills: [preflight], anchor_kind: always, anchor: a, source: 'method/templates/product-profile/skills/preflight.md#自発起動契約'}\n",
                          encoding="utf-8")
            cl, er = load_map(mp, base)
            if cl is not None or "MAP_INVALID" not in (er or ""):
                fails.append(f"IA-07: id=[start] の map が MAP_INVALID にならない: {er}")
            # IA-08: 空配列の statuses / instrument_paths は不正・判定関数は None
            vp2 = next(c for c in amap if c.get("id") == "verified-promotion")
            ic2 = next(c for c in amap if c.get("id") == "instrument-change")
            if not validate_map([dict(vp2, statuses=[])], base) or not validate_map([dict(ic2, instrument_paths=[])], base):
                fails.append("IA-08: 空配列の statuses/instrument_paths を validate_map が通した")
            if _class_matches(dict(vp2, statuses=[]), {"status": "verified"}, None, sc) is not None or \
               _class_matches(dict(ic2, instrument_paths=[]), {"affected_refs": ["method/tools/x.py"]}, None, sc) is not None:
                fails.append("IA-08: 空配列で _class_matches が None でない")
            # --- 独立検査 r3(ECO-064)の陽性対照: IA-09 canonical な skill ID ---
            for rs in (["Preflight"], ["../README"], ["../x"], ["preflight", "preflight"], ["pre flight"], ["preflight.md"], [""]):
                if not validate_map([dict(st, required_skills=rs)], base):
                    fails.append(f"IA-09: required_skills={rs!r} を validate_map が通した")
            if validate_map([dict(st, required_skills=["preflight"])], base) or validate_map([dict(st, required_skills=["factory-delegate"])], base):
                fails.append("IA-09: canonical な skill ID を validate_map が弾いた")
            # --- 独立検査 r4(ECO-064)の陽性対照: IA-10 instrument_paths の正規形 / IA-11 statuses の語彙 / IA-12 順序安定 ---
            for ip in (["C:/absolute/*.py"], [" method/tools/*.py"], ["method/tools/*.py "], ["**"], ["*/*"], ["/method/tools/*.py"],
                       ["method/../tools/*.py"], ["method\\tools\\*.py"]):
                if not validate_map([dict(ic2, instrument_paths=ip)], base):
                    fails.append(f"IA-10: instrument_paths={ip!r} を validate_map が通した")
            for ip in (["method/tools/*.py"], ["bomdd/hooks/*"], [".github/workflows/*"], ["a/**/x.py"]):
                if validate_map([dict(ic2, instrument_paths=ip)], base):
                    fails.append(f"IA-10: 正規形 {ip!r} を validate_map が弾いた: {validate_map([dict(ic2, instrument_paths=ip)], base)}")
            for sts in (["Verified"], [" verified"], ["verified "], ["done"]):
                if not validate_map([dict(vp2, statuses=sts)], base):
                    fails.append(f"IA-11: statuses={sts!r} を validate_map が通した")
            if validate_map([dict(vp2, statuses=["verified", "implemented"])], base):
                fails.append("IA-11: 語彙内の statuses を validate_map が弾いた")
            pos_rev = {"id": "ECO-910", "status": "verified", "order_ref": "bomdd/f1-pos.md", "affected_refs": ["method/tools/x.py"]}
            a = project(pos_rev, root, rel, amap, None, sc)["required_skills"]
            b2 = project(pos_rev, root, rel, list(reversed(amap)), None, sc)["required_skills"]
            if a != b2 or a["value"] != sorted(a["value"]):
                fails.append(f"IA-12: class 順序で required が変わる/辞書順でない: {a} vs {b2}")
    return _report(fails)


def _report(fails) -> int:
    if fails:
        print("bomdd-job selftest FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("bomdd-job selftest PASS(整合 NONE / 不整合 2 方向 / order 不在 / fence 内見出し無視 / 出所なし欄 null / 全欄 source / r2: 複数 --json 単一文書・引数不正 MISSING_INPUT・null エントリ・r2b: 対象なし/未知オプション MISSING_INPUT / F1: map 実在+source 実在・陽性/陰性 class・fence 内 receipt 無視・map 不在/sc 不能/order 不在= unknown・r1: 型不正 MAP_INVALID・source 断片の陰性対照・区切りを跨がない glob・r2: 空 source 要素・unhashable id・空配列= MAP_INVALID・r3: canonical skill ID〔文法+大小文字込み実在+重複拒否〕・r4: instrument_paths 正規形・statuses 語彙・required 辞書順 / F2〔ECO-072〕: 配員欄→台帳実在・fence 内無視・未知 id/構文外/重複= LEDGER_INCONSISTENT・台帳不在= MISSING_INPUT・台帳 id 重複/構文外= 不正 / r1: IA-01 未選択 entry の非文字列軸= 台帳不正・IA-03 HTML コメント/他節/節なしの言及は配員でない・下位見出しは節内 / F6〔ECO-074〕: inspector 宣言→ required / F7〔ECO-077〕: roles 必須キー・by_role 陽性/陰性・map 不在= unknown・receipt_author_role 射影〔文字列のみ・欄なし null・stop/required 不変〕・roles 欠落/空/語彙外/重複/非配列/大文字= MAP_INVALID・語彙内 2 語= 通過)")
    return 0


# --- ECO-120: --dwell(滞留の測定ビュー) -----------------------------------------------------------
DWELL_TERMINAL = ("verified", "applied", "rejected", "superseded", "withdrawn", "cancelled", "closed")
WAITING_VOCAB = ("start-instruction", "human-ruling", "human-acceptance", "independent-inspection", "external")
WAITING_ECO_RE = re.compile(r"eco:[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*-\d+")
DWELL_BUCKETS = ((7, "<=7d"), (30, "8-30d"), (90, "31-90d"), (None, ">90d"))
DWELL_PARALLEL_MIN = 64   # これ未満のコミット数は直列で読む(並列の起動費が勝つ)


def _dwell_loader():
    return getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def _dwell_items(data):
    """エントリの list と、それが `changes` 以外の古い形から取ったか。古い形(ViewPrism2 初期の change_orders 等)は
    「最初の list で先頭が id を持つ dict」を取る(section 0 の全件読みと同じ規則)。見つからなければ (None, False)。"""
    if isinstance(data, dict) and isinstance(data.get("changes"), list):
        return data["changes"], False
    if isinstance(data, list):
        return data, True
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "id" in v[0]:
                return v, True
    return None, False


def _dwell_snapshot(blob: bytes):
    """1 コミットの register → ({id: (status, waiting_on)}, paused の正規化文字列 or None, 古い形か)。形状不正は例外。"""
    data = yaml.load(blob, Loader=_dwell_loader())
    items, legacy = _dwell_items(data)
    if items is None:
        raise ValueError("エントリの list がない")
    snap = {}
    for e in items:
        if isinstance(e, dict) and "id" in e:
            w = e.get("waiting_on")
            snap[str(e["id"])] = (str(e.get("status")), None if w is None else str(w))
    has_p = isinstance(data, dict) and "paused" in data
    paused = json.dumps(data["paused"], ensure_ascii=False, sort_keys=True, default=str) if has_p else None
    return snap, paused, legacy


def _dwell_chunk(args):
    """(top, rel, [(idx, sha)]) → [(idx, snap|None, paused, err|None)]。自分の cat-file --batch を 1 本持つ(並列の単位)。
    rel が None なら sha は blob id そのもの(ECO-122: キャッシュに無い blob だけを読む)。"""
    import subprocess
    top, rel, items = args
    out = []
    p = subprocess.Popen(["git", "-C", top, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for idx, sha in items:
            p.stdin.write((f"{sha}:{rel}\n" if rel is not None else f"{sha}\n").encode())
            p.stdin.flush()
            head = p.stdout.readline().decode(errors="replace").split()
            if len(head) != 3 or head[1] != "blob":
                out.append((idx, None, None, "register なし(" + " ".join(head[1:])[:40] + ")"))
                continue
            size = int(head[2])
            blob = p.stdout.read(size)
            p.stdout.read(1)
            try:
                snap, paused, legacy = _dwell_snapshot(blob)
                out.append((idx, snap, paused, "legacy" if legacy else None))
            except Exception as e:  # noqa: BLE001 — 読めないコミットは名指しで返す(黙って捨てない)
                out.append((idx, None, None, type(e).__name__))
    finally:
        p.stdin.close()
        p.wait()
    return out


def _dwell_git(top, *args):
    import subprocess
    r = subprocess.run(["git", "-C", str(top), *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:2])} exit {r.returncode}: {r.stderr.decode(errors='replace').strip()[:120]}")
    return r.stdout.decode("utf-8", errors="replace")


def _dwell_parse(top: Path, rel, items, workers):
    """items[(idx, spec)] を読む → [(idx, snap, paused, err)](idx 順)。workers は解析が要る件数から決める(ECO-122: 全部ヒットなら起動しない)。"""
    import os
    if not items:
        return []
    k = workers if workers is not None else (min(os.cpu_count() or 1, 8) if len(items) >= DWELL_PARALLEL_MIN else 1)
    rows = []
    if k <= 1:
        rows = _dwell_chunk((str(top), rel, items))
    else:
        from concurrent.futures import ProcessPoolExecutor
        chunks = [items[i::k] for i in range(k)]   # 交互に配る: 後のコミットほど register が大きく、連続の塊だと最後の担当に偏る
        with ProcessPoolExecutor(max_workers=k) as ex:
            for part in ex.map(_dwell_chunk, [(str(top), rel, c) for c in chunks if c]):
                rows.extend(part)
    rows.sort(key=lambda r: r[0])
    return rows


def _dwell_cache_key():
    """ECO-122 P1: 版キーは導出する(手で上げる番号を持たない)— 解析規則の source・loader・PyYAML の版のハッシュ。
    source が読めなければ None(キャッシュを使わない)。"""
    import hashlib
    import inspect
    try:
        src = inspect.getsource(_dwell_snapshot) + "\0" + inspect.getsource(_dwell_items)
    except (OSError, TypeError):
        return None
    ld = _dwell_loader()
    return hashlib.sha256(f"{ld.__module__}.{ld.__name__}\0{getattr(yaml, '__version__', '?')}\0{src}".encode("utf-8")).hexdigest()


def dwell_cache_dir_default() -> Path:
    """ECO-122 P2: どのリポジトリの外にも置く — BOMDD_DWELL_CACHE_DIR > %LOCALAPPDATA% > $XDG_CACHE_HOME > ~/.cache。"""
    import os
    if os.environ.get("BOMDD_DWELL_CACHE_DIR"):
        return Path(os.environ["BOMDD_DWELL_CACHE_DIR"])
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "bomdd" / "dwell-cache"
    return Path(os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")) / "bomdd" / "dwell-cache"


def _dwell_cache_path(cache_dir: Path, top: Path, rel: str) -> Path:
    """1 register 1 ファイル: git common dir と register のパスのハッシュで名づける(worktree は共有・別リポは別ファイル)。"""
    import hashlib
    common = (top / _dwell_git(top, "rev-parse", "--git-common-dir").strip()).resolve()
    return Path(cache_dir) / (hashlib.sha256(f"{common.as_posix()}\0{rel}".encode("utf-8")).hexdigest()[:24] + ".json")


def _dwell_cache_load(path: Path, key: str):
    """→ ({blob: (snap|None, paused, err)}, None) か ({}, 外れの理由)。どんな不具合も外れ(判定にしない)。"""
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return {}, "absent"
    except OSError as e:
        return {}, f"unreadable: {type(e).__name__}"
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return {}, "not JSON"
    if not isinstance(data, dict) or not isinstance(data.get("blobs"), dict):
        return {}, "shape"
    if data.get("key") != key:
        return {}, "version key differs"
    out = {}
    for b, v in data["blobs"].items():
        if not (isinstance(v, list) and len(v) == 3 and (v[0] is None or isinstance(v[0], dict))
                and (v[1] is None or isinstance(v[1], str)) and (v[2] is None or isinstance(v[2], str))):
            return {}, "shape"
        snap = None
        if v[0] is not None:
            snap = {}
            for eid, sw in v[0].items():
                if not (isinstance(sw, list) and len(sw) == 2 and isinstance(sw[0], str) and (sw[1] is None or isinstance(sw[1], str))):
                    return {}, "shape"
                snap[eid] = (sw[0], sw[1])
        out[b] = (snap, v[1], v[2])
    return out, None


def _dwell_cache_save(path: Path, key: str, rel: str, blobs: dict):
    """この実行で使った blob だけを書く(書き換えられた履歴の blob は落ちる)。一時ファイル → rename。失敗は理由を返す(例外にしない)。"""
    import os
    tmp = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
        body = {"key": key, "register": rel,
                "blobs": {b: [None if s is None else {k: list(v) for k, v in s.items()}, p, e] for b, (s, p, e) in blobs.items()}}
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(body, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, path)
        tmp = None
        return None
    except OSError as e:
        return f"{type(e).__name__}: {str(e)[:120]}"
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _dwell_read_history(top: Path, rel: str, workers: int | None = None, cache_dir=None, stats=None):
    """register の履歴を古い順に読む → (commits[(sha, iso)], results[(snap|None, paused, err)])。workers=1 で直列。
    cache_dir が None ならキャッシュを使わない(ECO-120 と同じ読み方)。stats(dict)にはキャッシュの数を入れる(結果には入れない)。"""
    import subprocess
    stats = stats if stats is not None else {}
    log = _dwell_git(top, "log", "--reverse", "--format=%H %cI", "--", rel)
    commits = [tuple(l.split(" ", 1)) for l in log.splitlines() if l.strip()]
    key = _dwell_cache_key() if cache_dir is not None else None
    if key is None:
        stats.update(cache="off" if cache_dir is None else "off (source unavailable)")
        rows = _dwell_parse(top, rel, list(enumerate(sha for sha, _ in commits)), workers)
        return commits, [(snap, paused, err) for _, snap, paused, err in rows]
    # ECO-122 P1: 各コミットの register の blob id を取り、キャッシュに無い blob だけを読む
    chk = subprocess.run(["git", "-C", str(top), "cat-file", "--batch-check"], capture_output=True,
                         input="".join(f"{sha}:{rel}\n" for sha, _ in commits).encode())
    if chk.returncode != 0:
        raise RuntimeError(f"git cat-file --batch-check exit {chk.returncode}")
    heads = [l.split() for l in chk.stdout.decode(errors="replace").splitlines()]
    if len(heads) != len(commits):
        raise RuntimeError(f"git cat-file --batch-check: {len(heads)} 行 != {len(commits)} コミット")
    path = _dwell_cache_path(Path(cache_dir), top, rel)
    cached, miss = _dwell_cache_load(path, key)
    results, used, todo, hits = [None] * len(commits), {}, {}, 0
    for i, head in enumerate(heads):
        if len(head) != 3 or head[1] != "blob":   # _dwell_chunk と同じ文言(blob が無いコミットは読む費用がないのでキャッシュしない)
            results[i] = (None, None, "register なし(" + " ".join(head[1:])[:40] + ")")
        elif head[0] in cached:
            results[i] = used[head[0]] = cached[head[0]]
            hits += 1
        else:
            todo.setdefault(head[0], []).append(i)
    blobs = list(todo)
    for idx, snap, paused, err in _dwell_parse(top, None, list(enumerate(blobs)), workers):
        used[blobs[idx]] = (snap, paused, err)
        for i in todo[blobs[idx]]:
            results[i] = used[blobs[idx]]
    stats.update(cache="on", file=str(path), hits=hits, parsed=len(todo), read_miss=miss, write=None)
    if todo or miss is not None or set(cached) != set(used):
        stats["write"] = _dwell_cache_save(path, key, rel, used) or "ok"
    return commits, results


def _dwell_runs(commits, results):
    """各 id の変化点(dwell.py と同じ規則: 読めたコミットだけを順に見て、直前に見た値と違えば変化点)。"""
    st_hist, wt_hist, paused_hist = {}, {}, []
    for (sha, iso), (snap, paused, err) in zip(commits, results):
        if snap is None:
            continue
        for eid, (st, w) in snap.items():
            h = st_hist.setdefault(eid, [])
            if not h or h[-1][1] != st:
                h.append((iso, st, sha))
            hw = wt_hist.setdefault(eid, [])
            if not hw or hw[-1][1] != w:
                hw.append((iso, w, sha))
        if not paused_hist or paused_hist[-1][1] != paused:
            paused_hist.append((iso, paused, sha))
    return st_hist, wt_hist, paused_hist


def _days(now, iso):
    import datetime as dt
    return round((now - dt.datetime.fromisoformat(iso)).total_seconds() / 86400, 1)


def _bucket(d):
    for lim, name in DWELL_BUCKETS:
        if lim is None or d <= lim:
            return name


def _dwell_uncommitted(top: Path, rel: str, now) -> dict:
    """P4: dirty パス数・最古 mtime(下限)・register の HEAD 差。ignored は除く。"""
    import datetime as dt
    raw = _dwell_git(top, "status", "--porcelain=v1", "-z", "-uall")
    parts = raw.split("\0")
    paths, i = [], 0
    while i < len(parts):
        ent = parts[i]
        if len(ent) > 3:
            paths.append(ent[3:])
            if ent[0] in "RC":   # rename/copy は次の要素が元パス(数えない)
                i += 1
        i += 1
    oldest = None
    for p in paths:
        try:
            s = (top / p).stat()
        except OSError:   # 削除されたパス: 数えるが年齢は測れない
            continue
        # 更新日時と作成日時(無ければ ctime)の新しいほう: 古い mtime を保ったまま置かれたファイル(TimetableAdv の NuGet DLL・
        # mtime 2018 年・作成 2026-09-02)で年齢を過大に出さない — 書き込みか到着のどちらかが更新する限り、年齢は下限になる(ECO-120 V7)
        m = max(s.st_mtime, getattr(s, "st_birthtime", None) or s.st_ctime)
        age = (now - dt.datetime.fromtimestamp(m, dt.timezone.utc)).total_seconds() / 86400
        oldest = age if oldest is None else max(oldest, age)
    differs = rel in paths
    return {"dirty_paths": len(paths), "oldest_days_lower_bound": None if oldest is None else round(oldest, 1),
            "register_differs_from_head": differs}


def dwell(register: Path, stale_days: int = 14, now=None, workers: int | None = None, cache_dir=None, stats=None) -> dict:
    """ECO-120 P1-P4。例外は呼び側で MISSING_INPUT 相当の 1 行にする。
    ECO-122: cache_dir を渡したときだけ blob ごとの解析結果を使い回す(結果は同じ・数は stats に入れる)。"""
    import datetime as dt
    import statistics
    now = now or dt.datetime.now(dt.timezone.utc)
    register = register.resolve()
    top = Path(_dwell_git(register.parent, "rev-parse", "--show-toplevel").strip())
    rel = register.relative_to(top.resolve()).as_posix()
    commits, results = _dwell_read_history(top, rel, workers, cache_dir, stats)
    if not commits:
        raise RuntimeError(f"{rel} に履歴がない(未コミット)")
    warnings = [f"読めないコミット {sha[:10]} ({iso[:10]}): {err}" for (sha, iso), (s, _, err) in zip(commits, results) if s is None]
    last = next(((snap, paused) for snap, paused, _ in reversed(results) if snap is not None), None)
    if last is None:
        raise RuntimeError("どのコミットの register も読めない")
    head_snap, head_paused = last
    st_hist, wt_hist, paused_hist = _dwell_runs(commits, results)

    paused = None
    if head_paused is not None:
        pv = json.loads(head_paused)
        iso, _, sha = paused_hist[-1]
        reason = pv.get("reason") if isinstance(pv, dict) else None
        resume = pv.get("resume_when") if isinstance(pv, dict) else None
        paused = {"since_commit": sha, "since_date": iso, "days": _days(now, iso), "reason": reason, "resume_when": resume}
        if not (isinstance(reason, str) and reason.strip()):
            warnings.append("paused に reason がない")
        if not (isinstance(resume, str) and resume.strip()):
            warnings.append("paused に resume_when がない")

    open_, summary = [], {}
    for eid, (st, w) in head_snap.items():
        if w is not None and not (w in WAITING_VOCAB or WAITING_ECO_RE.fullmatch(w)):
            warnings.append(f"{eid}: waiting_on の値が語彙外: {w!r}")
        if st in DWELL_TERMINAL:
            if w is not None:
                warnings.append(f"{eid}: 終端 status ({st}) に waiting_on が残っている: {w!r}")
            continue
        iso, _, sha = st_hist[eid][-1]
        rec = {"id": eid, "status": st, "since_commit": sha, "since_date": iso, "days": _days(now, iso),
               "waiting_on": w, "waiting_since_commit": None, "waiting_days": None}
        if w is not None:
            wiso, _, wsha = wt_hist[eid][-1]
            rec["waiting_since_commit"], rec["waiting_days"] = wsha, _days(now, wiso)
        rec["over_threshold"] = rec["days"] > stale_days
        reason = "paused" if paused else (w or "none")
        rec["group"] = reason
        summary.setdefault(reason, {n: 0 for _, n in DWELL_BUCKETS})[_bucket(rec["days"])] += 1
        open_.append(rec)
    open_.sort(key=lambda r: -r["days"])

    spans = {}
    for h in st_hist.values():
        for (a_iso, a_st, _), (b_iso, _, _) in zip(h, h[1:]):
            d = (dt.datetime.fromisoformat(b_iso) - dt.datetime.fromisoformat(a_iso)).total_seconds() / 86400
            spans.setdefault(a_st, []).append(d)
    past = {s: {"n": len(x), "median": round(statistics.median(x), 1), "max": round(max(x), 1)} for s, x in sorted(spans.items())}
    return {"register": rel, "repo": str(top), "head_commit": commits[-1][0], "commits_read": len(commits),
            "parse_failures": sum(1 for s, _, _ in results if s is None),
            "legacy_shape_commits": sum(1 for s, _, e in results if s is not None and e == "legacy"), "stale_days": stale_days,
            "now": now.isoformat(timespec="seconds"), "paused": paused, "summary": summary,
            "open": open_, "past_dwell": past, "uncommitted": _dwell_uncommitted(top, rel, now), "warnings": warnings}


def render_dwell(r: dict) -> str:
    out = [f"dwell: {r['register']} @ {r['head_commit'][:10]} — commits {r['commits_read']}・読めない {r['parse_failures']}・"
           f"古い形 {r['legacy_shape_commits']}・"
           f"open {len(r['open'])}・閾値 {r['stale_days']} 日(測定ビュー・gate ではない)"]
    if r["paused"]:
        p = r["paused"]
        out.append(f"PAUSED {p['days']} 日(since {p['since_commit'][:10]}): reason={p['reason']!r} resume_when={p['resume_when']!r}")
    out.append("summary(理由 × 経過): " + " / ".join(
        f"{g}: " + " ".join(f"{b} {n}" for b, n in cnt.items()) for g, cnt in sorted(r["summary"].items())) if r["summary"] else "summary: open なし")
    unexplained = [o for o in r["open"] if o["over_threshold"] and o["group"] == "none"]
    out.append(f"unexplained(閾値超・理由なし) {len(unexplained)}:")
    out += [f"  {o['id']} {o['status']} {o['days']} 日(since {o['since_commit'][:10]})" for o in unexplained]
    for g in sorted({o["group"] for o in r["open"] if o["over_threshold"] and o["group"] != "none"}):
        rows = [o for o in r["open"] if o["over_threshold"] and o["group"] == g]
        out.append(f"{g} {len(rows)}:")
        out += [f"  {o['id']} {o['status']} {o['days']} 日" + (f"(理由 {o['waiting_days']} 日)" if o["waiting_days"] is not None else "")
                for o in rows]
    out.append("past dwell(閉じた区間): " + " / ".join(f"{s} n={v['n']} median={v['median']} max={v['max']}" for s, v in r["past_dwell"].items()))
    u = r["uncommitted"]
    out.append(f"uncommitted: dirty {u['dirty_paths']}・最古 {u['oldest_days_lower_bound']} 日(下限)・register の HEAD 差 "
               f"{'あり' if u['register_differs_from_head'] else 'なし'}")
    out += [f"WARNING {w}" for w in r["warnings"]]
    return "\n".join(out) + "\n"


def _dwell_cache_lines(stats: dict) -> list:
    """ECO-122: キャッシュの数(標準エラーへ — 標準出力はキャッシュの有無で変えない)。"""
    if stats.get("cache") != "on":
        return [f"dwell cache: {stats.get('cache', 'off')}"]
    out = []
    if stats.get("read_miss"):
        out.append(f"dwell cache: read: miss ({stats['read_miss']})")
    if stats.get("write") not in (None, "ok"):
        out.append(f"dwell cache: write failed: {stats['write']}")
    out.append(f"dwell cache: hits {stats['hits']}, parsed {stats['parsed']}, file {stats['file']}")
    return out


def _dwell_cache_report(stats: dict):
    data = ("\n".join(_dwell_cache_lines(stats)) + "\n").encode("utf-8", errors="replace")
    try:
        sys.stderr.flush()
        sys.stderr.buffer.write(data)
        sys.stderr.buffer.flush()
    except (AttributeError, ValueError, OSError):   # buffer の無い stderr(テストの差し替え等)
        sys.stderr.write(data.decode("utf-8"))


def dwell_main(argv) -> int:
    """--dwell の入口。引数不正・測定不能は 1 行(--json は {"error"})で返し、exit 0(原則 4)。"""
    known = {"--dwell", "--register", "--json", "--stale-days", "--no-cache"}
    err, reg_rel, stale = None, "bomdd/60-change-register.yaml", 14
    unknown = [a for a in argv if a.startswith("--") and a not in known]
    if unknown:
        err = f"未知のオプション(引数不正): {' '.join(unknown)}"
    for opt in ("--register", "--stale-days"):
        if not err and opt in argv:
            i = argv.index(opt)
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                err = f"{opt} に値がない(引数不正)"
            elif opt == "--register":
                reg_rel = argv[i + 1]
            elif not re.fullmatch(r"[1-9]\d{0,3}", argv[i + 1]):
                err = f"--stale-days は 1〜9999 の整数: {argv[i + 1]!r}"
            else:
                stale = int(argv[i + 1])
    res = None
    if not err:
        if yaml is None:
            err = "PyYAML 不在"
        else:
            stats = {}
            try:
                res = dwell(Path.cwd() / reg_rel, stale, cache_dir=None if "--no-cache" in argv else dwell_cache_dir_default(),
                            stats=stats)
            except Exception as e:  # noqa: BLE001 — 測定不能は合格ではない: 理由を出して止まる
                err = f"測定不能: {type(e).__name__}: {str(e)[:160]}"
            if not err:
                _dwell_cache_report(stats)
    if "--json" in argv:
        print(json.dumps({"error": err} if err else res, ensure_ascii=False, indent=2))
    else:
        print(f"MISSING_INPUT {err}" if err else render_dwell(res), end="" if not err else "\n")
    return 0


def _missing(reason: str, eco: str | None = None) -> dict:
    """欠測(MISSING_INPUT)を job と同形の 1 レコードで表す — 消費側が同じ parser で読める。"""
    rec = {"stop_type": _field("MISSING_INPUT", f"導出: {reason}")}
    if eco:
        rec = {"eco": _field(eco, "引数"), **rec}
    return rec


def select(argv: list, root: Path):
    """引数と register から (jobs, reg_rel) を返す。引数不正・register 不能・null エントリは
    MISSING_INPUT レコードにして返す(IA-05: traceback を出さない・終了コードは常に 0)。"""
    reg_rel = "bomdd/60-change-register.yaml"
    if "--register" in argv:
        i = argv.index("--register")
        if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
            return [_missing("--register に値がない(引数不正)")], reg_rel
        reg_rel = argv[i + 1]
    # IA-07(r2): 未知オプション・対象指定なしを「対象なし」と区別する(空 jobs を黙って返さない)
    known = {"--register", "--json", "--all", "--selftest"}
    unknown = [a for a in argv if a.startswith("--") and a not in known]
    if unknown:
        return [_missing(f"未知のオプション(引数不正): {' '.join(unknown)}")], reg_rel
    if "--all" not in argv and not any(a.startswith(("ECO-", "CAPA-")) for a in argv):
        return [_missing("対象指定なし(引数不正): ECO-NNN か --all を指定")], reg_rel
    entries, err = load_register(root / reg_rel)
    if err:
        return [_missing(err)], reg_rel
    jobs = []
    valid = [e for e in entries if isinstance(e, dict)]
    for bad in (e for e in entries if not isinstance(e, dict)):
        jobs.append(_missing(f"register エントリが object でない: {bad!r}"))
    want = [a for a in argv if a.startswith("ECO-") or a.startswith("CAPA-")]
    if "--all" in argv:
        sel = [e for e in valid if e.get("status") != "verified"]
    else:
        sel = [e for e in valid if str(e.get("id")) in want]
        for w in want:
            if not any(str(e.get("id")) == w for e in valid):
                jobs.append(_missing(f"register に {w} なし", w))
    amap, map_err = load_map()
    sc = _load_selfconf()
    jobs.extend(project(e, root, reg_rel, amap, map_err, sc) for e in sel)
    return jobs, reg_rel


def main(argv) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", newline="\n")
    if "--selftest" in argv:
        return selftest()
    if "--dwell" in argv:   # ECO-120: 既存の経路(select)に入る前に分ける — 既存モードの出力を変えない
        return dwell_main(argv)
    jobs, reg_rel = select(argv, Path.cwd())
    if "--json" in argv:
        # IA-04: 複数 job でも単一 JSON 文書(object)にする — 標準 parser で閉じる
        print(json.dumps({"register": reg_rel, "jobs": jobs}, ensure_ascii=False, indent=2))
    else:
        for job in jobs:
            print(render(job))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
