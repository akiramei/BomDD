#!/usr/bin/env python3
"""process-validator — BomDD process-core 汎用ライフサイクル検査(harness ECO-015)

不変条件(コード固定 — profile で変えられるのはパス・語彙・trailer 名のみ):
  E01 protected-change-without-open-eco : 保護パスの staged 変更は open 状態の ECO を要求
  E02 new-entry-not-initial             : 台帳の新規エントリは initial 状態で始まる
  E03 illegal-transition                : 状態の飛び越し・後退・terminal からの遷移・
                                          エントリ削除・未知の状態
  E04 fix-trailer-missing               : implemented 遷移コミットに fix trailer がない
                                          (states に implemented を含む語彙のときのみ)
  E05 accept-trailer-missing            : applied 遷移コミットに accept trailer がない
  E06 approval-evidence-missing-or-conversational :
                                          applied エントリの履歴に accept trailer commit が
                                          実在しない — 自然文の了承は承認証拠にならない
  E07 trailer-references-unknown-eco    : 履歴の trailer が台帳に実在しない ECO を参照
                                          (ViewPrism2 E18 の移植)

出典: ViewPrism2 validate E14〜E19(ECO-061)/ ViewTube PR-LIFECYCLE-VALIDATOR
(CAPA-VT-002 negative controls)からの共通核抽出。FINDINGS §11.5。

trailer の解釈は本ファイルの parse_trailers() が唯一の実装(commit-msg 検査と履歴証拠
検査が共有 — 検査契約の二重定義は緩い側が必ず緩む: ViewPrism2 ECO-078 の教訓)。

exit: 0=適合 / 1=違反(各行 [Exx]) / 2=測定不能(git・profile・YAML の障害 — hook 文脈では遮断)
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
}

# 状態 → 要求 trailer キー(profile.trailers のキー名)。states に含まれる状態のみ発火。
STATE_TRAILER = {"implemented": "fix", "applied": "accept"}


# --- 厳格 YAML(重複キー=情報損失を遮断。self-conformance ECO-012 と同方式の写し —
#     製品リポ内の強制経路では本 validator が唯一の解釈実装) -------------------------
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


# --- profile -------------------------------------------------------------------------
REQUIRED_KEYS = ["protected_paths", "register", "states", "initial", "open_states", "trailers"]


def load_profile(root: Path) -> dict:
    path = root / "bomdd" / "process-profile.yaml"
    if not path.is_file():
        return {}
    try:
        prof = strict_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        die(f"process-profile.yaml が読めない/情報損失: {e}")
    missing = [k for k in REQUIRED_KEYS if k not in prof]
    if missing:
        die(f"process-profile.yaml に必須キーがない: {missing}")
    if prof["initial"] not in prof["states"]:
        die(f"initial '{prof['initial']}' が states に含まれない")
    prof.setdefault("terminal_extra", [])
    return prof


# --- 台帳 ----------------------------------------------------------------------------
def parse_register(text: str | None, warn: bool = False) -> dict[str, dict]:
    """id → entry。テンプレ placeholder(title が '<' 始まり)は検査対象外(gate ① 裁定 4)"""
    if not text:
        return {}
    data = strict_load(text)  # 呼び出し側で YAMLError を捕捉
    entries: dict[str, dict] = {}
    for e in (data or {}).get("changes") or []:
        if not isinstance(e, dict) or not e.get("id"):
            continue
        title = str(e.get("title", ""))
        if title.startswith("<"):
            if warn:
                print(f"process-validator: [skip] placeholder エントリ {e['id']}(title が '<' 始まり)")
            continue
        entries[str(e["id"])] = e
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


def staged_paths(root: Path) -> list[str]:
    p = run_git(root, "diff", "--cached", "--name-only", "-z")
    if p.returncode != 0:
        die(f"staged ファイルを列挙できない: {p.stderr.strip()}")
    return [x for x in p.stdout.split("\0") if x]


def register_at(root: Path, reg_path: str, ref: str) -> str | None:
    """ref = ':'(index)または 'HEAD'。存在しなければ None(初回 commit 等)"""
    p = run_git(root, "show", f"{ref}:{reg_path}" if ref == "HEAD" else f":{reg_path}")
    return p.stdout if p.returncode == 0 else None


def history_trailer_map(root: Path, keys: list[str]) -> dict[str, set[str]]:
    """履歴全 commit の本文へ parse_trailers を適用(単一解釈)。key → {id, ...}"""
    p = run_git(root, "log", "--format=%H%x01%B%x02")
    out: dict[str, set[str]] = {k: set() for k in keys}
    if p.returncode != 0:  # HEAD なし(履歴ゼロ)は空 — 欠測でなく実際に証拠ゼロ
        return out
    for chunk in p.stdout.split("\x02"):
        if "\x01" not in chunk:
            continue
        _, body = chunk.split("\x01", 1)
        tr = parse_trailers(body)
        for k in keys:
            out[k] |= set(tr.get(k, []))
    return out


# --- trailer(単一解釈関数) ---------------------------------------------------------
_TRAILER_RE = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):\s*(\S.*?)\s*$")


def parse_trailers(msg: str) -> dict[str, list[str]]:
    """メッセージ全行を走査し 'Key: value' 行を収集(commit-msg と履歴証拠の共有実装)"""
    out: dict[str, list[str]] = {}
    for line in msg.splitlines():
        m = _TRAILER_RE.match(line)
        if m:
            out.setdefault(m.group(1), []).append(m.group(2))
    return out


# --- 検査(純関数 — selftest から直接叩く) -----------------------------------------
def check_protected(paths: list[str], entries: dict[str, dict], prof: dict) -> list[str]:
    protected = [p for p in paths
                 if any(p.startswith(pre) for pre in prof["protected_paths"])]
    if not protected:
        return []
    if any(e.get("status") in prof["open_states"] for e in entries.values()):
        return []
    return [f"[E01] {REASONS['E01']}: 保護パス変更 {protected[:3]} に open 状態"
            f"({prof['open_states']})の ECO がない — 起票が先(register: {prof['register']})"]


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
        if old_st == st:
            continue
        if old_st in extra:
            v.append(f"[E03] {REASONS['E03']}: {cid} が terminal '{old_st}' から '{st}' へ遷移")
        elif st in extra:
            pass  # どの状態からも rejected/superseded へは遷移可
        elif old_st in states:
            step = states.index(st) - states.index(old_st)
            if step != 1:
                kind = "飛び越し" if step > 1 else "後退"
                v.append(f"[E03] {REASONS['E03']}: {cid} の {kind} '{old_st}' → '{st}'"
                         f"(順序: {states})")
        else:
            v.append(f"[E03] {REASONS['E03']}: {cid} の旧状態 '{old_st}' が未知")
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
        name = prof["trailers"].get(key)
        if not name:
            continue
        if cid not in trailers.get(name, []):
            code = "E04" if key == "fix" else "E05"
            v.append(f"[{code}] {REASONS[code]}: {cid} の '{st}' 遷移コミットに"
                     f" trailer 「{name}: {cid}」がない")
    return v


def check_trailer_refs(entries: dict[str, dict], prof: dict,
                       trailer_map: dict[str, set[str]]) -> list[str]:
    """履歴 trailer の参照先 ECO が台帳に実在する(E07 — ViewPrism2 E18 の移植)"""
    v: list[str] = []
    for name, ids in trailer_map.items():
        for cid in sorted(ids - set(entries)):
            v.append(f"[E07] {REASONS['E07']}: 履歴の trailer 「{name}: {cid}」が"
                     f"台帳に実在しない ECO を参照")
    return v


def check_history_evidence(entries: dict[str, dict], prof: dict,
                           trailer_map: dict[str, set[str]]) -> list[str]:
    """状態が要求する trailer commit の履歴実在(E06)。自然文の了承は証拠にならない"""
    states = prof["states"]
    v: list[str] = []
    for cid, e in entries.items():
        st = e.get("status")
        if st not in states:
            continue
        for reached in states[: states.index(st) + 1]:
            key = STATE_TRAILER.get(reached)
            if not key:
                continue
            name = prof["trailers"].get(key)
            if name and cid not in trailer_map.get(name, set()):
                v.append(f"[E06] {REASONS['E06']}: {cid}({st})の履歴に"
                         f"「{name}: {cid}」trailer commit が実在しない — "
                         f"自然文の了承・会話記録は承認証拠にならない")
    return v


# --- モード --------------------------------------------------------------------------
def _load_pair(root: Path, prof: dict) -> tuple[dict, dict]:
    reg = prof["register"]
    try:
        old = parse_register(register_at(root, reg, "HEAD"))
        new = parse_register(register_at(root, reg, ":"), warn=True)
    except yaml.YAMLError as e:
        die(f"台帳({reg})がパース不能/情報損失: {e}")
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
    prof = load_profile(root)
    if not prof:
        print("process-validator: profile なし(bomdd/process-profile.yaml)— 管理下でないため素通し")
        return 0

    if a.mode == "pre-commit":
        old, new = _load_pair(root, prof)
        return report(check_protected(staged_paths(root), new, prof)
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

    # validate: 作業ツリーの台帳 + 履歴証拠(E06)
    reg_file = root / prof["register"]
    if not reg_file.is_file():
        die(f"台帳がない: {reg_file}")
    try:
        entries = parse_register(reg_file.read_text(encoding="utf-8"), warn=True)
    except yaml.YAMLError as e:
        die(f"台帳がパース不能/情報損失: {e}")
    tmap = history_trailer_map(root, list(prof["trailers"].values()))
    known = set(prof["states"]) | set(prof["terminal_extra"])
    vio = [f"[E03] {REASONS['E03']}: {cid} が未知の状態 '{e.get('status')}'"
           for cid, e in entries.items() if e.get("status") not in known]
    vio += check_history_evidence(entries, prof, tmap)
    vio += check_trailer_refs(entries, prof, tmap)
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
            msg = f"違反なし(期待どおり)" if good else f"想定外の違反: {codes}"
        else:
            good = codes == [expect]
            msg = f"{expect} 検出" if good else f"期待 {expect} / 実際 {codes or 'なし'}"
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: {msg}")
        ok = ok and good

    e = lambda st: {"status": st}
    # 陽性対照(検出器が壊れたまま全 PASS しない — 変異が発火することを先に確認)
    print("process-validator selftest:")
    t("陽性: 2状態の正常遷移", check_transitions({"ECO-1": e("staged")}, {"ECO-1": e("applied")}, prof2), None)
    t("陽性: 保護パス+open ECO", check_protected(["src/a.py"], {"ECO-1": e("staged")}, prof2), None)
    t("陽性: 非保護パスは ECO 不要", check_protected(["docs/a.md"], {}, prof2), None)
    t("E01: 保護パス・open ECO なし", check_protected(["src/a.py"], {"ECO-1": e("applied")}, prof2), "E01")
    t("E02: 新規が initial でない", check_transitions({}, {"ECO-1": e("applied")}, prof2), "E02")
    t("E03: 飛び越し(3状態)", check_transitions({"ECO-1": e("staged")}, {"ECO-1": e("applied")}, prof3), "E03")
    t("E03: 後退", check_transitions({"ECO-1": e("applied")}, {"ECO-1": e("staged")}, prof2), "E03")
    t("E03: terminal からの遷移", check_transitions({"ECO-1": e("rejected")}, {"ECO-1": e("staged")}, prof2), "E03")
    t("E03: エントリ削除", check_transitions({"ECO-1": e("staged")}, {}, prof2), "E03")
    t("E03: 未知状態", check_transitions({}, {"ECO-1": e("proposed")}, prof2), "E03")
    t("陽性: terminal への遷移は可", check_transitions({"ECO-1": e("staged")}, {"ECO-1": e("rejected")}, prof2), None)
    t("E04: implemented 遷移に fix trailer なし(3状態)",
      check_commit_msg({"ECO-1": e("staged")}, {"ECO-1": e("implemented")}, "eco: fix", prof3), "E04")
    t("陽性: fix trailer あり(3状態)",
      check_commit_msg({"ECO-1": e("staged")}, {"ECO-1": e("implemented")},
                       "eco: fix\n\nBomDD-ECO-Fix: ECO-1", prof3), None)
    t("E05: applied 遷移に accept trailer なし",
      check_commit_msg({"ECO-1": e("staged")}, {"ECO-1": e("applied")}, "eco: accept", prof2), "E05")
    t("陽性: accept trailer あり",
      check_commit_msg({"ECO-1": e("staged")}, {"ECO-1": e("applied")},
                       "eco: accept\n\nBomDD-ECO-Accept: ECO-1", prof2), None)
    t("E06: applied の履歴に accept trailer commit なし(自然文の了承は証拠でない)",
      check_history_evidence({"ECO-1": e("applied")}, prof2, {"BomDD-ECO-Accept": set()}), "E06")
    t("陽性: 履歴に accept trailer commit あり",
      check_history_evidence({"ECO-1": e("applied")}, prof2, {"BomDD-ECO-Accept": {"ECO-1"}}), None)
    t("E06: 3状態 applied は fix 証拠も要求",
      check_history_evidence({"ECO-1": e("applied")}, prof3,
                             {"BomDD-ECO-Fix": set(), "BomDD-ECO-Accept": {"ECO-1"}}), "E06")
    t("E07: trailer が台帳に実在しない ECO を参照",
      check_trailer_refs({}, prof2, {"BomDD-ECO-Accept": {"ECO-9"}}), "E07")
    t("陽性: trailer 参照先が台帳に実在",
      check_trailer_refs({"ECO-9": e("applied")}, prof2, {"BomDD-ECO-Accept": {"ECO-9"}}), None)
    # placeholder skip(gate ① 裁定 4)と厳格ローダーの陽性対照
    ents = parse_register("changes:\n  - id: ECO-001\n    title: <一行要約>\n    status: proposed\n")
    good = ents == {}
    print(f"  [{'PASS' if good else 'FAIL'}] placeholder skip: {'除外された' if good else f'除外されず {ents}'}")
    ok = ok and good
    try:
        strict_load("a: 1\na: 2\n")
        print("  [FAIL] 厳格ローダー陽性対照: 重複キーを検出しない")
        ok = False
    except _DupKeyError:
        print("  [PASS] 厳格ローダー陽性対照: 重複キー検出")
    # trailer 単一解釈の対照(行頭のみ・コメント行は不一致)
    tr = parse_trailers("subject\n\nBomDD-ECO-Accept: ECO-9\n# BomDD-ECO-Fix: ECO-9\n")
    good = tr.get("BomDD-ECO-Accept") == ["ECO-9"] and "BomDD-ECO-Fix" not in tr
    print(f"  [{'PASS' if good else 'FAIL'}] trailer 解釈: {tr}")
    ok = ok and good

    print(f"process-validator selftest: {'all PASS' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
