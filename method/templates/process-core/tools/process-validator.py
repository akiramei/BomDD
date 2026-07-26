#!/usr/bin/env python3
"""process-validator — BomDD process-core 汎用ライフサイクル検査(harness ECO-015・ECO-016)

不変条件(コード固定 — profile で変えられるのはパス・語彙・trailer 名のみ):
  E01 protected-change-without-open-eco : 保護パスの staged 変更は **HEAD 時点で** open 状態の
                                          ECO を要求(起票 commit の先行を強制 — ECO-016 REV-10)
  E02 new-entry-not-initial             : 台帳の新規エントリは initial 状態で始まる
  E03 illegal-transition                : 状態の飛び越し・後退・terminal からの遷移・
                                          エントリ削除・未知の状態(旧状態の未知も遮断 — REV-09)
  E04 fix-trailer-missing               : implemented 遷移コミットに fix trailer がない
  E05 accept-trailer-missing            : applied 遷移コミットに accept trailer がない
  E06 approval-evidence-missing-or-conversational :
                                          状態が要求する trailer commit が履歴に実在し、かつ
                                          **その commit で当該遷移が実際に発生した**こと(SHA・
                                          遷移紐付け — 事前植込み trailer は証拠にならない。REV-03)。
                                          自然文の了承は承認証拠にならない
  E07 trailer-references-unknown-eco    : 履歴の trailer が台帳に実在しない ECO を参照
  E08 equipment-change-without-open-eco : 設備自身(profile・hooks・validator 等)の変更・削除は
                                          open ECO を要求(自己保護。HEAD に profile が実在する
                                          場合のみ発火 — 設置の初回 commit は対象外。REV-01/案a:
                                          profile の撤去も ECO 経由 — 武装解除も変更管理の対象)
  E09 evidence-state-divergence         : 遷移証拠と現在状態の乖離(applied 証拠があるのに
                                          staged 等)+ fix→accept の祖先順序違反
                                          (ViewPrism2 E17 相当の移植。REV-03)

台帳解析は fail-closed(REV-04): 非 mapping エントリ・id/status 欠落・**id 重複**(後勝ち情報
損失= ECO-011/012 の 1 段上の同型)・changes 非 list は測定不能 exit 2。placeholder は明示
sentinel(`<一行要約>` 完全一致)のみ skip。git 障害と履歴ゼロを区別し、障害は exit 2(REV-08)。
merge 中は HEAD と MERGE_HEAD の台帳を合算して比較元にする(REV-13)。

trailer の解釈は git 意味論に整合する**最終 trailer ブロックのみ**(REV-02 — 中間段落・件名・
本文後続は不成立)。parse_trailers() が唯一の実装(commit-msg 検査と履歴証拠検査が共有)。

出典: ViewPrism2 validate_bom E14〜E19 / ViewTube PR-LIFECYCLE-VALIDATOR / ECO-015 独立受入検査
(bomdd/reports/independent-inspection-eco-015.md・13/13 CONFIRMED)。

exit: 0=適合 / 1=違反(各行 [Exx]) / 2=測定不能(git・profile・台帳構造の障害 — hook 文脈では遮断)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("process-validator: 測定不能 — PyYAML が必要です(pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REASONS = {
    "E01": "protected-change-without-open-eco",
    "E02": "new-entry-not-initial",
    "E03": "illegal-transition",
    "E04": "fix-trailer-missing",
    "E05": "accept-trailer-missing",
    "E06": "approval-evidence-missing-or-conversational",
    "E07": "trailer-references-unknown-eco",
    "E08": "equipment-change-without-open-eco",
    "E09": "evidence-state-divergence",
}

# 状態 → 要求 trailer キー。states に含まれる状態のみ発火。
STATE_TRAILER = {"implemented": "fix", "applied": "accept"}
TRAILER_STATE = {"fix": "implemented", "accept": "applied"}

# 設備の自己保護パス(コード固定 — profile の protected_paths に依存しない。ECO-016 REV-01)
CORE_PROTECTED = ["bomdd/process-profile.yaml", "bomdd/hooks/",
                  "bomdd/tools/process-validator.py", "bomdd/tools/process-qualification.py"]

# placeholder sentinel(完全一致のみ skip — 先頭文字判定の廃止。ECO-016 REV-04)
PLACEHOLDER_TITLES = {"<一行要約>"}

PROFILE_REL = "bomdd/process-profile.yaml"


# --- 厳格 YAML(重複キー=情報損失を遮断) -------------------------------------------
class _DupKeyError(yaml.YAMLError):
    pass


class _StrictLoader(yaml.SafeLoader):
    pass


def _strict_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in seen:
            raise _DupKeyError(f"重複キー '{key}'(line {key_node.start_mark.line + 1})")
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _strict_mapping)


def strict_load(text: str):
    return yaml.load(text, Loader=_StrictLoader)


def die(msg: str) -> "NoReturn":
    print(f"process-validator: 測定不能 — {msg}", file=sys.stderr)
    sys.exit(2)


# --- profile(REV-01: nested schema の厳格検証) --------------------------------------
REQUIRED_KEYS = ["protected_paths", "register", "states", "initial", "open_states", "trailers"]


def validate_profile(prof) -> list[str]:
    """profile の構造検証(純関数)。エラー列挙 — 空リスト=妥当"""
    errs: list[str] = []
    if not isinstance(prof, dict):
        return ["profile が mapping でない"]
    missing = [k for k in REQUIRED_KEYS if k not in prof]
    if missing:
        errs.append(f"必須キーがない: {missing}")
        return errs
    def is_strlist(x):
        return isinstance(x, list) and all(isinstance(s, str) and s for s in x)
    if not is_strlist(prof["protected_paths"]):
        errs.append("protected_paths は非空文字列の list")
    if not (isinstance(prof["register"], str) and prof["register"]):
        errs.append("register は非空文字列")
    states = prof["states"]
    if not (is_strlist(states) and states):
        errs.append("states は非空文字列の非空 list")
    elif len(set(states)) != len(states):
        errs.append("states に重複がある")
    else:
        if prof["initial"] not in states:
            errs.append(f"initial '{prof['initial']}' が states に含まれない")
        if not is_strlist(prof["open_states"]) or not set(prof["open_states"]) <= set(states):
            errs.append("open_states は states の部分集合")
        extra = prof.get("terminal_extra", [])
        if not isinstance(extra, list) or not all(isinstance(s, str) and s for s in extra):
            errs.append("terminal_extra は文字列 list")
        elif set(extra) & set(states) or len(set(extra)) != len(extra):
            errs.append("terminal_extra は states と非重複・自身も重複なし")
    tr = prof["trailers"]
    if not (isinstance(tr, dict) and isinstance(tr.get("fix"), str) and tr.get("fix")
            and isinstance(tr.get("accept"), str) and tr.get("accept")):
        errs.append("trailers は fix/accept 両キーを非空文字列で持つ(部分削除は無音無効化になるため遮断)")
    elif tr["fix"] == tr["accept"]:
        errs.append("trailers.fix と trailers.accept は別名")
    return errs


def load_profile(root: Path, head_fallback: bool = False) -> dict:
    """profile を読む。head_fallback= 作業ツリーに無ければ HEAD 版を使う(案a: 削除中も検査を継続)"""
    path = root / PROFILE_REL
    text: str | None = None
    if path.is_file():
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            die(f"process-profile.yaml が読めない: {e}")
    elif head_fallback:
        p = run_git(root, "show", f"HEAD:{PROFILE_REL}")
        if p.returncode == 0:
            text = p.stdout
            print("process-validator: [note] profile は作業ツリーに無いが HEAD に実在 — HEAD 版で検査継続(撤去は ECO 経由・案a)")
    if text is None:
        return {}
    try:
        prof = strict_load(text)
    except yaml.YAMLError as e:
        die(f"process-profile.yaml がパース不能/情報損失: {e}")
    errs = validate_profile(prof)
    if errs:
        die("process-profile.yaml が不正(部分変異の無音無効化を遮断): " + "・".join(errs))
    prof.setdefault("terminal_extra", [])
    return prof


# --- 台帳(REV-04: fail-closed 解析) -------------------------------------------------
def parse_register(text: str | None, warn: bool = False) -> dict[str, dict]:
    """id → entry。構造不正(非 mapping・id/status 欠落・id 重複・changes 非 list)は ValueError。
    placeholder は sentinel 完全一致のみ skip。"""
    if not text:
        return {}
    data = strict_load(text)  # yaml.YAMLError は呼び出し側で die
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("台帳の top-level が mapping でない")
    changes = data.get("changes")
    if changes is None:
        changes = []
    if not isinstance(changes, list):
        raise ValueError("changes が list でない")
    entries: dict[str, dict] = {}
    for i, e in enumerate(changes):
        if not isinstance(e, dict):
            raise ValueError(f"changes[{i}] が mapping でない: {e!r}")
        cid = e.get("id")
        if not isinstance(cid, str) or not cid:
            raise ValueError(f"changes[{i}] に id がない/不正")
        if str(e.get("title", "")) in PLACEHOLDER_TITLES:
            if warn:
                print(f"process-validator: [skip] placeholder エントリ {cid}(sentinel 一致)")
            continue
        if not isinstance(e.get("status"), str) or not e.get("status"):
            raise ValueError(f"{cid} に status がない/不正")
        if cid in entries:
            raise ValueError(f"id 重複: {cid}(後勝ち情報損失の遮断 — ECO-011/012 同型)")
        entries[cid] = e
    return entries


# --- git -----------------------------------------------------------------------------
def run_git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
    except OSError as e:
        die(f"git を実行できない: {e}")


def repo_root() -> Path:
    p = run_git(Path.cwd(), "rev-parse", "--show-toplevel")
    if p.returncode != 0:
        die("git リポジトリではない")
    return Path(p.stdout.strip())


def ensure_git_repo(root: Path) -> None:
    if run_git(root, "rev-parse", "--git-dir").returncode != 0:
        die(f"{root} は git リポジトリではない(git 障害は証拠ゼロと区別する — REV-08)")


def head_exists(root: Path) -> bool:
    return run_git(root, "rev-parse", "--verify", "-q", "HEAD").returncode == 0


def head_has_profile(root: Path) -> bool:
    return head_exists(root) and run_git(root, "cat-file", "-e", f"HEAD:{PROFILE_REL}").returncode == 0


def staged_paths(root: Path) -> list[str]:
    p = run_git(root, "diff", "--cached", "--name-only", "-z")
    if p.returncode != 0:
        die(f"staged ファイルを列挙できない: {p.stderr.strip()}")
    return [x for x in p.stdout.split("\0") if x]


def register_text_at(root: Path, reg_path: str, ref: str) -> str | None:
    """ref= ':'(index)/ commit-ish。存在しなければ None"""
    spec = f":{reg_path}" if ref == ":" else f"{ref}:{reg_path}"
    p = run_git(root, "show", spec)
    return p.stdout if p.returncode == 0 else None


def parent_registers(root: Path, prof: dict) -> list[dict[str, dict]]:
    """比較元= HEAD(+merge 中は MERGE_HEAD — REV-13)。HEAD なし(初回 commit)は空。"""
    if not head_exists(root):
        return [{}]
    refs = ["HEAD"]
    if run_git(root, "rev-parse", "--verify", "-q", "MERGE_HEAD").returncode == 0:
        refs.append("MERGE_HEAD")
    out = []
    for ref in refs:
        try:
            out.append(parse_register(register_text_at(root, prof["register"], ref)))
        except (yaml.YAMLError, ValueError) as e:
            die(f"台帳({ref})がパース不能/構造不正: {e}")
    return out


def combine_parents(parents: list[dict[str, dict]], prof: dict) -> dict[str, dict]:
    """複数親の合算 — id ごとに最も進んだ状態を比較元にする(純関数・REV-13)"""
    states, extra = prof["states"], set(prof["terminal_extra"])

    def rank(st):
        if st in extra:
            return (2, 0)
        if st in states:
            return (1, states.index(st))
        return (0, 0)

    out: dict[str, dict] = {}
    for p in parents:
        for cid, e in p.items():
            if cid not in out or rank(e.get("status")) > rank(out[cid].get("status")):
                out[cid] = e
    return out


# --- trailer(単一解釈・git 意味論= 最終 trailer ブロックのみ — REV-02) --------------
_TRAILER_RE = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):\s*(\S.*?)\s*$")


def parse_trailers(msg: str) -> dict[str, list[str]]:
    """最終段落が全行 trailer 形式のときだけ、その段落を trailer として解釈する
    (中間段落・件名のみ・本文後続・混在段落は不成立 — git/ViewPrism2 と同意味論)。
    commit-msg 検査と履歴証拠検査の共有実装(唯一の解釈)。"""
    blocks: list[list[str]] = []
    cur: list[str] = []
    for line in msg.splitlines():
        if line.strip() == "":
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append(cur)
    if len(blocks) < 2:  # 件名のみ/単一段落は trailer を持たない
        return {}
    last = blocks[-1]
    matches = [_TRAILER_RE.match(l) for l in last]
    if not all(matches):
        return {}
    out: dict[str, list[str]] = {}
    for m in matches:
        out.setdefault(m.group(1), []).append(m.group(2))
    return out


# --- 履歴証拠(REV-03: SHA・遷移紐付け) ----------------------------------------------
def gather_history(root: Path, prof: dict) -> tuple[dict, dict]:
    """履歴を走査し (linked, raw) を返す。
    linked: {(key,id): [sha,...]} — trailer を持つ commit で当該遷移が実際に発生したもののみ。
    raw:    {trailer_name: {id,...}} — 出現した全 trailer(E07 用)。
    git 障害は die(履歴ゼロ= HEAD なしは空 — REV-08)。歴史上の台帳が不正な commit は
    証拠として不採用(warn のみ — 履歴は不変のため die しない・fail-closed 方向)。"""
    ensure_git_repo(root)
    raw: dict[str, set[str]] = {n: set() for n in prof["trailers"].values()}
    linked: dict[tuple[str, str], list[str]] = {}
    if not head_exists(root):
        return linked, raw
    p = run_git(root, "log", "--format=%H%x01%B%x02")
    if p.returncode != 0:
        die(f"git log が失敗(証拠ゼロと区別する — REV-08): {p.stderr.strip()}")
    name_key = {prof["trailers"]["fix"]: "fix", prof["trailers"]["accept"]: "accept"}
    reg = prof["register"]
    for chunk in p.stdout.split("\x02"):
        if "\x01" not in chunk:
            continue
        sha, body = chunk.split("\x01", 1)
        sha = sha.strip()
        tr = parse_trailers(body)
        hit = {name_key[n]: ids for n, ids in tr.items() if n in name_key}
        if not hit:
            continue
        for n, ids in tr.items():
            if n in raw:
                raw[n] |= set(ids)
        try:
            new_e = parse_register(register_text_at(root, reg, sha))
            old_e = parse_register(register_text_at(root, reg, f"{sha}^"))
        except (yaml.YAMLError, ValueError):
            print(f"process-validator: [warn] {sha[:9]} の台帳が解析不能 — この commit は証拠に採用しない")
            continue
        for key, ids in hit.items():
            st = TRAILER_STATE[key]
            for cid in ids:
                if (new_e.get(cid, {}).get("status") == st
                        and old_e.get(cid, {}).get("status") != st):
                    linked.setdefault((key, cid), []).append(sha)
    return linked, raw


# --- 検査(純関数 — selftest から直接叩く) -----------------------------------------
def check_protected(paths: list[str], head_entries: dict[str, dict], prof: dict) -> list[str]:
    """E01 — 判定は HEAD 側 open ECO(起票 commit の先行を強制。REV-10)"""
    protected = [p for p in paths
                 if any(p.startswith(pre) for pre in prof["protected_paths"])]
    if not protected:
        return []
    if any(e.get("status") in prof["open_states"] for e in head_entries.values()):
        return []
    return [f"[E01] {REASONS['E01']}: 保護パス変更 {protected[:3]} — HEAD 時点で open 状態"
            f"({prof['open_states']})の ECO がない(起票 commit が先・同一 commit 起票は不可)"]


def check_equipment(paths: list[str], head_entries: dict[str, dict], prof: dict,
                    equipped: bool) -> list[str]:
    """E08 — 設備自身の変更・削除の自己保護(HEAD に profile 実在時のみ。REV-01/案a)"""
    if not equipped:
        return []
    touched = [p for p in paths
               if any(p == cp or p.startswith(cp) for cp in CORE_PROTECTED)]
    if not touched:
        return []
    if any(e.get("status") in prof["open_states"] for e in head_entries.values()):
        return []
    return [f"[E08] {REASONS['E08']}: 工程設備の変更/削除 {touched[:3]} に open ECO がない"
            f" — 設備(profile/hooks/validator)の武装解除・改変も変更管理の対象(案a)"]


def check_transitions(old: dict[str, dict], new: dict[str, dict], prof: dict) -> list[str]:
    states, extra = prof["states"], prof["terminal_extra"]
    known = set(states) | set(extra)
    v: list[str] = []
    for cid, e in new.items():
        st = e.get("status")
        if st not in known:
            v.append(f"[E03] {REASONS['E03']}: {cid} が未知の状態 '{st}'(語彙: {states}+{extra})")
            continue
        if cid not in old:
            if st != prof["initial"]:
                v.append(f"[E02] {REASONS['E02']}: 新規 {cid} が '{st}' で登録"
                         f"(新規は '{prof['initial']}' で始まる)")
            continue
        old_st = old[cid].get("status")
        if old_st not in known:  # REV-09: 旧状態の未知検証を terminal 判定より先に
            v.append(f"[E03] {REASONS['E03']}: {cid} の旧状態 '{old_st}' が未知(terminal への遷移でも洗浄しない)")
            continue
        if old_st == st:
            continue
        if old_st in extra:
            v.append(f"[E03] {REASONS['E03']}: {cid} が terminal '{old_st}' から '{st}' へ遷移")
        elif st in extra:
            pass  # known な状態からの rejected/superseded は可
        else:
            step = states.index(st) - states.index(old_st)
            if step != 1:
                kind = "飛び越し" if step > 1 else "後退"
                v.append(f"[E03] {REASONS['E03']}: {cid} の {kind} '{old_st}' → '{st}'"
                         f"(順序: {states})")
    for cid in old:
        if cid not in new:
            v.append(f"[E03] {REASONS['E03']}: {cid} が台帳から削除された(ID は再利用・削除しない)")
    return v


def check_commit_msg(old: dict[str, dict], new: dict[str, dict], msg: str, prof: dict) -> list[str]:
    trailers = parse_trailers(msg)
    v: list[str] = []
    for cid, e in new.items():
        st = e.get("status")
        old_st = old.get(cid, {}).get("status")
        if st == old_st or st not in prof["states"]:
            continue
        key = STATE_TRAILER.get(st)
        if not key:
            continue
        name = prof["trailers"][key]
        if cid not in trailers.get(name, []):
            code = "E04" if key == "fix" else "E05"
            v.append(f"[{code}] {REASONS[code]}: {cid} の '{st}' 遷移コミットの最終 trailer ブロックに"
                     f"「{name}: {cid}」がない(中間段落は trailer と認めない)")
    return v


def check_history_evidence(entries: dict[str, dict], prof: dict,
                           linked: dict[tuple[str, str], list[str]]) -> list[str]:
    """E06 — 状態が要求する遷移紐付き証拠の実在(事前植込みは linked に入らない)"""
    states = prof["states"]
    v: list[str] = []
    for cid, e in entries.items():
        st = e.get("status")
        if st not in states:
            continue
        for reached in states[: states.index(st) + 1]:
            key = STATE_TRAILER.get(reached)
            if key and not linked.get((key, cid)):
                v.append(f"[E06] {REASONS['E06']}: {cid}({st})— 「{prof['trailers'][key]}: {cid}」"
                         f"trailer を持ち、かつその commit で '{reached}' 遷移が発生した証拠が履歴にない"
                         f" — 自然文の了承・事前植込み trailer は承認証拠にならない")
    return v


def check_divergence(entries: dict[str, dict], prof: dict,
                     linked: dict[tuple[str, str], list[str]],
                     is_ancestor=None) -> list[str]:
    """E09 — 遷移証拠と現在状態の乖離+fix→accept 順序(ViewPrism2 E17 相当。REV-03)"""
    states, extra = prof["states"], set(prof["terminal_extra"])
    v: list[str] = []
    for (key, cid), shas in sorted(linked.items()):
        req = TRAILER_STATE[key]
        if req not in states:
            continue
        e = entries.get(cid)
        if e is None:
            continue  # 台帳不在は E07 が担う
        st = e.get("status")
        if st in states and states.index(st) < states.index(req) and st not in extra:
            v.append(f"[E09] {REASONS['E09']}: {cid} は '{req}' 遷移証拠({shas[0][:9]})を持つのに"
                     f"現在状態が '{st}' — 逆行乖離(再着手は新 ECO で行う)")
    if is_ancestor is not None and "implemented" in states:
        for cid in {c for (k, c) in linked if k == "accept"}:
            fixes = linked.get(("fix", cid), [])
            accepts = linked.get(("accept", cid), [])
            if fixes and accepts and not any(is_ancestor(f, a) for f in fixes for a in accepts):
                v.append(f"[E09] {REASONS['E09']}: {cid} の fix 証拠が accept 証拠の祖先でない(順序違反)")
    return v


# --- モード --------------------------------------------------------------------------
def _load_pair(root: Path, prof: dict) -> tuple[dict, dict]:
    old = combine_parents(parent_registers(root, prof), prof)
    try:
        new = parse_register(register_text_at(root, prof["register"], ":"), warn=True)
    except (yaml.YAMLError, ValueError) as e:
        die(f"台帳(index)がパース不能/構造不正: {e}")
    return old, new


def report(violations: list[str]) -> int:
    for line in violations:
        print(line, file=sys.stderr)
    if violations:
        print(f"process-validator: {len(violations)} 件の違反 — commit を遮断しました", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="BomDD process-core lifecycle validator")
    ap.add_argument("--mode", required=True,
                    choices=["pre-commit", "commit-msg", "validate", "selftest"])
    ap.add_argument("--msg-file", help="commit-msg モードのメッセージファイル")
    ap.add_argument("--root", help="対象リポ(既定: cwd の git root)")
    a = ap.parse_args()

    if a.mode == "selftest":
        return selftest()

    root = Path(a.root).resolve() if a.root else repo_root()
    ensure_git_repo(root)
    prof = load_profile(root, head_fallback=(a.mode in ("pre-commit", "commit-msg")))
    if not prof:
        print("process-validator: profile なし(bomdd/process-profile.yaml)— 管理下でないため素通し")
        return 0

    if a.mode == "pre-commit":
        old, new = _load_pair(root, prof)
        paths = staged_paths(root)
        return report(check_protected(paths, old, prof)
                      + check_equipment(paths, old, prof, head_has_profile(root))
                      + check_transitions(old, new, prof))

    if a.mode == "commit-msg":
        if not a.msg_file:
            die("--msg-file が必要")
        try:
            msg = Path(a.msg_file).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            die(f"メッセージファイルが読めない: {e}")
        old, new = _load_pair(root, prof)
        return report(check_transitions(old, new, prof)
                      + check_commit_msg(old, new, msg, prof))

    # validate: 作業ツリーの台帳 + 履歴証拠(E06/E07/E09)
    reg_file = root / prof["register"]
    if not reg_file.is_file():
        die(f"台帳がない: {reg_file}")
    try:
        entries = parse_register(reg_file.read_text(encoding="utf-8"), warn=True)
    except (yaml.YAMLError, ValueError) as e:
        die(f"台帳がパース不能/構造不正: {e}")
    linked, raw = gather_history(root, prof)
    known = set(prof["states"]) | set(prof["terminal_extra"])
    vio = [f"[E03] {REASONS['E03']}: {cid} が未知の状態 '{e.get('status')}'"
           for cid, e in entries.items() if e.get("status") not in known]
    vio += check_history_evidence(entries, prof, linked)
    for name, ids in raw.items():
        for cid in sorted(ids - set(entries)):
            vio.append(f"[E07] {REASONS['E07']}: 履歴の trailer 「{name}: {cid}」が台帳に実在しない ECO を参照")
    def is_ancestor(a_sha: str, b_sha: str) -> bool:
        return run_git(root, "merge-base", "--is-ancestor", a_sha, b_sha).returncode == 0
    vio += check_divergence(entries, prof, linked, is_ancestor)
    rc = report(vio)
    if rc == 0:
        print(f"process-validator: validate OK({len(entries)} entries)")
    return rc


# --- selftest(純関数の対検査 — 陽性対照+変異。git 不要・決定的) -------------------
def selftest() -> int:
    prof2 = {"protected_paths": ["src/"], "register": "bomdd/60-change-register.yaml",
             "states": ["staged", "applied"], "initial": "staged", "open_states": ["staged"],
             "terminal_extra": ["rejected", "superseded"],
             "trailers": {"fix": "BomDD-ECO-Fix", "accept": "BomDD-ECO-Accept"}}
    prof3 = dict(prof2, states=["staged", "implemented", "applied"],
                 open_states=["staged", "implemented"])
    ok = True

    def t(name: str, got: list[str], expect: str | None) -> None:
        nonlocal ok
        codes = sorted({m.group(1) for m in (re.match(r"\[(E\d\d)\]", g) for g in got) if m})
        if expect is None:
            good = not got
            msg = "違反なし(期待どおり)" if good else f"想定外の違反: {codes}"
        else:
            good = codes == [expect]
            msg = f"{expect} 検出" if good else f"期待 {expect} / 実際 {codes or 'なし'}"
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: {msg}")
        ok = ok and good

    def tb(name: str, good: bool, detail: str = "") -> None:
        nonlocal ok
        print(f"  [{'PASS' if good else 'FAIL'}] {name}{': ' + detail if detail else ''}")
        ok = ok and good

    def raises(fn) -> bool:
        try:
            fn()
            return False
        except (ValueError, yaml.YAMLError):
            return True

    e = lambda st: {"status": st}
    print("process-validator selftest:")

    # profile 検証(REV-01)
    tb("profile 陽性対照(既定 2 状態)", validate_profile(prof2) == [])
    tb("REV-01: trailers.accept 削除を遮断",
       any("trailers" in x for x in validate_profile(dict(prof2, trailers={"fix": "BomDD-ECO-Fix"}))))
    tb("REV-01: trailers.accept 空文字列を遮断",
       any("trailers" in x for x in validate_profile(dict(prof2, trailers={"fix": "F", "accept": ""}))))
    tb("REV-01: states 重複を遮断",
       any("重複" in x for x in validate_profile(dict(prof2, states=["staged", "staged"]))))
    tb("REV-01: open_states ⊄ states を遮断",
       any("open_states" in x for x in validate_profile(dict(prof2, open_states=["ghost"]))))
    tb("REV-01: initial ∉ states を遮断",
       any("initial" in x for x in validate_profile(dict(prof2, initial="ghost"))))

    # trailer 意味論(REV-02)
    tb("REV-02: 中間段落 trailer は不成立",
       parse_trailers("subject\n\nBomDD-ECO-Accept: ECO-1\n\nordinary final paragraph\n") == {})
    tb("REV-02: 単一段落(件名のみ)は不成立", parse_trailers("BomDD-ECO-Accept: ECO-1\n") == {})
    tb("REV-02: 混在最終段落(コメント行)は不成立",
       parse_trailers("subject\n\nBomDD-ECO-Accept: ECO-9\n# comment\n") == {})
    tb("陽性: 最終 trailer ブロックは成立",
       parse_trailers("subject\n\nbody\n\nBomDD-ECO-Fix: ECO-9\nBomDD-ECO-Accept: ECO-9\n")
       == {"BomDD-ECO-Fix": ["ECO-9"], "BomDD-ECO-Accept": ["ECO-9"]})

    # 台帳解析(REV-04)
    tb("REV-04: id 重複を遮断",
       raises(lambda: parse_register("changes:\n  - {id: ECO-1, title: a, status: applied}\n  - {id: ECO-1, title: b, status: staged}\n")))
    tb("REV-04: 非 mapping entry を遮断", raises(lambda: parse_register("changes: [42]\n")))
    tb("REV-04: status 欠落を遮断", raises(lambda: parse_register("changes:\n  - {id: ECO-1, title: a}\n")))
    tb("REV-04: changes 非 list を遮断", raises(lambda: parse_register("changes: {id: x}\n")))
    tb("REV-04: sentinel 完全一致のみ skip",
       parse_register("changes:\n  - {id: ECO-001, title: <一行要約>, status: proposed}\n") == {}
       and raises(lambda: parse_register("changes:\n  - {id: ECO-1, title: <別の何か>, status: proposed}\n")) is False
       and "ECO-1" in parse_register("changes:\n  - {id: ECO-1, title: <別の何か>, status: proposed}\n"))
    try:
        strict_load("a: 1\na: 2\n")
        tb("厳格ローダー陽性対照", False, "重複キーを検出しない")
    except _DupKeyError:
        tb("厳格ローダー陽性対照", True, "重複キー検出")

    # 遷移(REV-09 含む)
    t("陽性: 2状態の正常遷移", check_transitions({"ECO-1": e("staged")}, {"ECO-1": e("applied")}, prof2), None)
    t("E02: 新規が initial でない", check_transitions({}, {"ECO-1": e("applied")}, prof2), "E02")
    t("E03: 飛び越し(3状態)", check_transitions({"ECO-1": e("staged")}, {"ECO-1": e("applied")}, prof3), "E03")
    t("E03: 後退", check_transitions({"ECO-1": e("applied")}, {"ECO-1": e("staged")}, prof2), "E03")
    t("E03: terminal からの遷移", check_transitions({"ECO-1": e("rejected")}, {"ECO-1": e("staged")}, prof2), "E03")
    t("E03: エントリ削除", check_transitions({"ECO-1": e("staged")}, {}, prof2), "E03")
    t("E03: 未知状態(新)", check_transitions({}, {"ECO-1": e("proposed")}, prof2), "E03")
    t("REV-09: 未知旧状態 → terminal は洗浄しない",
      check_transitions({"ECO-1": e("mystery")}, {"ECO-1": e("rejected")}, prof2), "E03")
    t("陽性: known → terminal は可", check_transitions({"ECO-1": e("staged")}, {"ECO-1": e("rejected")}, prof2), None)

    # E01(REV-10: HEAD 側判定)/ E08(REV-01)
    t("陽性: 保護パス+HEAD に open ECO", check_protected(["src/a.py"], {"ECO-1": e("staged")}, prof2), None)
    t("E01: 保護パス・HEAD に open なし", check_protected(["src/a.py"], {"ECO-1": e("applied")}, prof2), "E01")
    t("REV-10: 同一 commit 起票(HEAD 空)は E01", check_protected(["src/a.py"], {}, prof2), "E01")
    t("E08: 設備変更・open なし(設置済み)",
      check_equipment(["bomdd/process-profile.yaml"], {}, prof2, True), "E08")
    t("E08: profile 削除も対象(案a)",
      check_equipment(["bomdd/hooks/pre-commit"], {"ECO-1": e("applied")}, prof2, True), "E08")
    t("陽性: 設備変更+open ECO は可(監査つき撤去)",
      check_equipment(["bomdd/process-profile.yaml"], {"ECO-1": e("staged")}, prof2, True), None)
    t("陽性: 未設置(初回 commit)の設備 staged は対象外",
      check_equipment(["bomdd/process-profile.yaml"], {}, prof2, False), None)

    # commit-msg(E04/E05)
    t("E04: implemented 遷移に fix trailer なし(3状態)",
      check_commit_msg({"ECO-1": e("staged")}, {"ECO-1": e("implemented")}, "eco: fix", prof3), "E04")
    t("陽性: fix trailer(最終ブロック)",
      check_commit_msg({"ECO-1": e("staged")}, {"ECO-1": e("implemented")},
                       "eco: fix\n\nBomDD-ECO-Fix: ECO-1", prof3), None)
    t("E05: accept trailer なし",
      check_commit_msg({"ECO-1": e("staged")}, {"ECO-1": e("applied")}, "eco: accept", prof2), "E05")
    t("REV-02: 中間段落 trailer では E05",
      check_commit_msg({"ECO-1": e("staged")}, {"ECO-1": e("applied")},
                       "subject\n\nBomDD-ECO-Accept: ECO-1\n\ntrailing body", prof2), "E05")

    # 履歴証拠(E06 遷移紐付け)/ E09
    t("E06: 遷移紐付き証拠なし(事前植込みは linked に入らない)",
      check_history_evidence({"ECO-1": e("applied")}, prof2, {}), "E06")
    t("陽性: 遷移紐付き accept 証拠あり",
      check_history_evidence({"ECO-1": e("applied")}, prof2, {("accept", "ECO-1"): ["abc"]}), None)
    t("E06: 3状態 applied は fix 証拠も要求",
      check_history_evidence({"ECO-1": e("applied")}, prof3, {("accept", "ECO-1"): ["abc"]}), "E06")
    t("E09: accept 証拠があるのに staged(逆行乖離)",
      check_divergence({"ECO-1": e("staged")}, prof2, {("accept", "ECO-1"): ["abc"]}), "E09")
    t("陽性: terminal なら乖離でない",
      check_divergence({"ECO-1": e("rejected")}, prof2, {("accept", "ECO-1"): ["abc"]}), None)
    t("E09: fix→accept 順序違反(3状態)",
      check_divergence({"ECO-1": e("applied")}, prof3,
                       {("fix", "ECO-1"): ["f1"], ("accept", "ECO-1"): ["a1"]},
                       is_ancestor=lambda a, b: False), "E09")
    t("陽性: fix が accept の祖先",
      check_divergence({"ECO-1": e("applied")}, prof3,
                       {("fix", "ECO-1"): ["f1"], ("accept", "ECO-1"): ["a1"]},
                       is_ancestor=lambda a, b: True), None)

    # merge 合算(REV-13)
    combined = combine_parents([{"ECO-1": e("staged")}, {"ECO-1": e("applied")}], prof2)
    tb("REV-13: 複数親は最も進んだ状態を採用", combined["ECO-1"]["status"] == "applied")
    t("REV-13: merge 陽性対照(親 B で applied 済み → index applied は非違反)",
      check_transitions(combined, {"ECO-1": e("applied")}, prof2), None)

    print(f"process-validator selftest: {'all PASS' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
