#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""oracle.py — CLI「worklist」独立受入検査(ブラックボックス oracle)

使い方:
    python oracle.py <被検実装.py へのパス>

規律:
- すべての assert は kit/cli-cad.md(および kit/schema-excerpt.md)へトレースできる
  (対応表= oracle-notes.md)。実装は一切参照していない。
- cli-cad.md §U(U1〜U11)の未規定次元は合否判定に使わない。
- 被検実装は subprocess 経由でのみ実行し (stdout, stderr, exit code) だけを観測する。

exit code: 全 PASS=0 / 1 件でも FAIL=1 / oracle 自身の使用誤り=2
"""

import os
import re
import subprocess
import sys

# ---------------------------------------------------------------- 環境
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(BASE, "kit", "fixtures")
F1 = os.path.join(FIX, "f1-normal.md")
F2 = os.path.join(FIX, "f2-warnings.md")
F3 = os.path.join(FIX, "f3-empty.md")
F4 = os.path.join(FIX, "f4-no-marker.md")
F5 = os.path.join(FIX, "f5-unaudited.md")

# ------------------------------------------------- CAD 規定の正確文字列(§5)
H1 = "== worklist(open / watch)=="
H2 = "== actions due(要処理 — 記帳は正常)=="
H3 = "== validation warnings(記帳不整合)=="
H4 = "== legacy coverage =="
H5 = "== stats =="
HEADINGS = [H1, H2, H3, H4, H5]

ZERO = "(0 件)"
BASIS_MARKER = "境界の根拠: marker"
BASIS_FALLBACK = "境界の根拠: migration-section(fallback)"
UNAUDITED_ZERO = "unaudited: 0 節"


def audited_line(n):
    return "audited(棚卸し済み — 状態の正本は移行残高節): {} 節".format(n)


def count_line(a, b, c, d):
    return ("native(新書式の新規): open {} / watch {} ・ "
            "migrated(期首移行残高): open {} / watch {}".format(a, b, c, d))


STAT_KEYS = [
    "sections_scanned", "structured_sections", "audited_legacy_sections",
    "unaudited_legacy_sections", "open_items", "watch_items", "actions_due",
    "closed_items", "validation_warnings", "elapsed_ms",
]

# ------------------------------------------ fixture ごとの導出期待値(CAD §3-§5)
F1_COUNT = count_line(3, 1, 1, 1)
F1_STATS = [
    "sections_scanned: 4",
    "structured_sections: 3",
    "audited_legacy_sections: 1",
    "unaudited_legacy_sections: 0",
    "open_items: 4(native 3 / migrated 1)",
    "watch_items: 2(native 1 / migrated 1)",
    "actions_due: 1",
    "closed_items: 3(recovered/withdrawn/superseded)",
    "validation_warnings: 0",
]
# (ID, 状態トークン, origin, 節日付(None=無日付), 記帳座標セグメント, 本文全文)
F1_ITEMS = [
    ("EXP-20260601-01", "open", "migrated", "2026-07-01", "20260601", "移行残高の open 項目"),
    ("OBS-20260601-02", "watch 2/3", "migrated", "2026-07-01", "20260601", "移行残高の watch 項目"),
    ("EXP-20260702-04", "open", "native", "2026-07-01", "20260702", "移行節内だが native 上書きの項目"),
    ("EXP-20260702-01", "open", "native", "2026-07-02", "20260702", "新規 open 項目"),
    ("OBS-20260702-02", "watch 3/3", "native", "2026-07-02", "20260702", "閾値到達項目(昇格審査待ち)"),
    ("EXP-20260702-06", "open", "native", None, "20260702", "無日付節の項目"),
]
F1_CLOSED_IDS = ["EXP-20260601-03", "EXP-20260702-03", "OBS-20260702-05"]
F1_EXCLUDED_IDS = ["EXP-99990101-01", "OBS-99990101-02", "EXP-99990101-03"]

F2_COUNT = count_line(1, 0, 0, 0)
F2_STATS_FIXED = [
    "sections_scanned: 1",
    "structured_sections: 1",
    "audited_legacy_sections: 0",
    "unaudited_legacy_sections: 0",
    "open_items: 1(native 1 / migrated 0)",
    "watch_items: 0(native 0 / migrated 0)",
    "actions_due: 0",
    "closed_items: 1(recovered/withdrawn/superseded)",
    None,  # validation_warnings は W1 の多重報告許容のため 6 または 7(下で照合)
]
# W2〜W6 の期待 (行番号, コード) — 行番号は f2-warnings.md の 1 始まり物理行
F2_WARN_FIXED = {(8, "W4"), (9, "W3"), (10, "W2"), (11, "W5"), (12, "W6")}
F2_W1_ALLOWED = {(7, "W1"), (13, "W1")}
F2_NON_ITEMS = ["OBS-20260710-02", "EXP-20260710-03", "EXP-20260710-04",
                "EXP-20260710-05", "EXP-20260710-06"]

F3_STATS = [
    "sections_scanned: 0",
    "structured_sections: 0",
    "audited_legacy_sections: 0",
    "unaudited_legacy_sections: 0",
    "open_items: 0(native 0 / migrated 0)",
    "watch_items: 0(native 0 / migrated 0)",
    "actions_due: 0",
    "closed_items: 0(recovered/withdrawn/superseded)",
    "validation_warnings: 0",
]

F4_COUNT = count_line(0, 0, 1, 1)
F4_STATS = [
    "sections_scanned: 3",
    "structured_sections: 1",
    "audited_legacy_sections: 1",
    "unaudited_legacy_sections: 1",
    "open_items: 1(native 0 / migrated 1)",
    "watch_items: 1(native 0 / migrated 1)",
    "actions_due: 0",
    "closed_items: 0(recovered/withdrawn/superseded)",
    "validation_warnings: 0",
]

F5_COUNT = count_line(1, 0, 0, 0)
F5_STATS = [
    "sections_scanned: 3",
    "structured_sections: 1",
    "audited_legacy_sections: 1",
    "unaudited_legacy_sections: 1",
    "open_items: 1(native 1 / migrated 0)",
    "watch_items: 0(native 0 / migrated 0)",
    "actions_due: 0",
    "closed_items: 0(recovered/withdrawn/superseded)",
    "validation_warnings: 0",
]


# ---------------------------------------------------------------- 基盤
def split_sections(out):
    """5 見出し(正確な文字列)がこの順に現れることを前提にセクションへ分割。
    順序どおりに見つからなければ None(見出し検査の FAIL として扱う)。"""
    lines = out.splitlines()
    pos = []
    start = 0
    for h in HEADINGS:
        found = None
        for i in range(start, len(lines)):
            if lines[i].strip() == h:
                found = i
                break
        if found is None:
            return None
        pos.append(found)
        start = found + 1
    secs = {}
    for k in range(5):
        end = pos[k + 1] if k + 1 < 5 else len(lines)
        secs[k] = lines[pos[k] + 1:end]
    return secs


def first_nonempty(lines):
    for l in lines:
        if l.strip():
            return l.strip()
    return None


def find_line_with(lines, token):
    for l in lines:
        if token in l:
            return l
    return None


class Oracle:
    def __init__(self, impl):
        self.impl = os.path.abspath(impl)
        self.results = []  # (name, ok, detail)
        self._cache = {}

    # ---- 実行(ブラックボックス観測)
    def run(self, *args):
        key = tuple(args)
        if key in self._cache:
            return self._cache[key]
        try:
            p = subprocess.run(
                [sys.executable, self.impl] + list(args),
                capture_output=True, timeout=60, cwd=BASE)
            r = (p.stdout.decode("utf-8", "replace"),
                 p.stderr.decode("utf-8", "replace"), p.returncode)
        except subprocess.TimeoutExpired:
            r = ("", "<TIMEOUT 60s>", -999)
        self._cache[key] = r
        return r

    # ---- 記録
    def add(self, name, ok, expected, got):
        self.results.append((name, bool(ok), expected, got))

    # ---- 共通検査
    def base(self, tag, out, err, rc, with_sections=True):
        self.add(tag + "/exit0", rc == 0, "exit code 0(§6)", "exit code {}".format(rc))
        self.add(tag + "/stderr-empty", err.strip() == "",
                 "stderr は空(§5)", "stderr={!r}".format(err.strip()[:200]))
        if not with_sections:
            return None
        secs = split_sections(out)
        self.add(tag + "/headings-order", secs is not None,
                 "5 見出しが正確な文字列でこの順(§5)",
                 "OK" if secs is not None else "見出し欠落/文字列不一致/順序不正")
        return secs

    def sec(self, secs, i):
        return secs[i] if secs else []

    def check_count_line(self, tag, secs, expected):
        got = first_nonempty(self.sec(secs, 0))
        self.add(tag + "/worklist-count-line", got == expected,
                 "冒頭件数行 {!r}(§5)".format(expected), repr(got))

    def check_zero(self, tag, secs, idx, label):
        lines = [l.strip() for l in self.sec(secs, idx)]
        self.add(tag + "/" + label, ZERO in lines,
                 "セクション内に行 {!r}(§5)".format(ZERO),
                 repr([l for l in lines if l])[:200])

    def check_stats(self, tag, secs, expected9, vw_accept=None):
        lines = [l.strip() for l in self.sec(secs, 4) if l.strip()]
        got = [l for l in lines
               if re.match(r"^(%s):" % "|".join(STAT_KEYS), l)]
        keys = [g.split(":")[0] for g in got]
        problems = []
        if keys != STAT_KEYS:
            problems.append("キー集合/順序が不一致: {}".format(keys))
        else:
            for exp, act in zip(expected9, got[:9]):
                if exp is None:  # validation_warnings 柔軟照合(W1 多重報告許容)
                    m = re.match(r"^validation_warnings: (\d+)$", act)
                    if not m or int(m.group(1)) not in (vw_accept or {0}):
                        problems.append("{!r}(許容 {} )".format(act, sorted(vw_accept or [])))
                elif act != exp:
                    problems.append("{!r} ≠ 期待 {!r}".format(act, exp))
            if not re.match(r"^elapsed_ms: \d+$", got[9]):
                problems.append("elapsed_ms 形式不正: {!r}".format(got[9]))
        self.add(tag + "/stats", not problems,
                 "10 キーをこの順・正確な書式で(§5。elapsed_ms は非負整数のみ検査=U4)",
                 "OK" if not problems else "; ".join(problems)[:400])

    # ------------------------------------------------------------ F1
    def test_f1(self):
        out, err, rc = self.run(F1)
        secs = self.base("f1", out, err, rc)
        wl = self.sec(secs, 0)

        self.check_count_line("f1", secs, F1_COUNT)

        # 出現順
        idxs = []
        for (iid, *_rest) in F1_ITEMS:
            pos = next((n for n, l in enumerate(wl) if iid in l), None)
            idxs.append((iid, pos))
        ok_order = all(p is not None for _, p in idxs) and \
            all(idxs[i][1] < idxs[i + 1][1] for i in range(len(idxs) - 1))
        self.add("f1/worklist-appearance-order", ok_order,
                 "open/watch 6 項目が入力出現順(§5)",
                 str([(i, p) for i, p in idxs]))

        # 各項目行の必須要素(本文全文は --full 側で検査 — 切り詰めは U1)
        for (iid, status, origin, date, _seg, _body) in F1_ITEMS:
            line = find_line_with(wl, iid)
            tokens = [status, origin] + ([date] if date else [])
            missing = [] if line is None else [t for t in tokens if t not in line]
            ok = line is not None and not missing
            self.add("f1/item-{}".format(iid), ok,
                     "行に ID/状態 {!r}/origin {!r}{} を含む(§5)".format(
                         status, origin, "/節日付 {!r}".format(date) if date else ""),
                     "行なし" if line is None else
                     ("OK" if ok else "欠落 {} : {!r}".format(missing, line.strip()[:160])))

        # PROMOTION DUE 項目の ★DUE
        due_line = find_line_with(wl, "OBS-20260702-02")
        self.add("f1/item-due-star", due_line is not None and "★DUE" in due_line,
                 "DUE 項目の worklist 行に ★DUE(§5)",
                 repr(due_line.strip()[:160]) if due_line else "行なし")

        # closed は worklist に列挙されない
        leaked = [i for i in F1_CLOSED_IDS if find_line_with(wl, i)]
        self.add("f1/worklist-excludes-closed", not leaked,
                 "closed 3 件は worklist(open/watch の列挙)に現れない(§5)",
                 "混入 {}".format(leaked) if leaked else "OK")

        # 除外領域(fence/blockquote/HTML コメント)の ID は出力全体に現れない
        found = [i for i in F1_EXCLUDED_IDS if i in out]
        self.add("f1/excluded-regions-not-parsed", not found,
                 "fence/blockquote/HTML コメント内の例示 ID は解析対象外(§3)",
                 "出現 {}".format(found) if found else "OK")

        # actions due: 別セクションに PROMOTION DUE 行
        ad = self.sec(secs, 1)
        line = find_line_with(ad, "OBS-20260702-02")
        ok = line is not None and "PROMOTION DUE" in line and "watch 3/3" in line
        self.add("f1/actions-due-line", ok,
                 "actions due 行に PROMOTION DUE・当該 ID・watch 3/3(§4-§5)",
                 repr(line.strip()[:160]) if line else "行なし")

        # 警告 0(リンク行の非誤検出・DUE を警告に混ぜない、を含む)
        self.check_zero("f1", secs, 2, "warnings-zero")

        # legacy coverage: marker 分岐・audited 1・unaudited 0(正確文字列)
        lg = [l.strip() for l in self.sec(secs, 3)]
        self.add("f1/legacy-basis-marker", first_nonempty(self.sec(secs, 3)) == BASIS_MARKER,
                 "1 行目 {!r}(§3/§5)".format(BASIS_MARKER),
                 repr(first_nonempty(self.sec(secs, 3))))
        self.add("f1/legacy-audited-1", audited_line(1) in lg,
                 repr(audited_line(1)) + "(§5)", repr([l for l in lg if l])[:200])
        enum = [l for l in lg if re.match(r"^- L\d+: ", l)]
        self.add("f1/legacy-unaudited-zero",
                 UNAUDITED_ZERO in lg and not enum,
                 "{!r} の正確文字列・列挙なし(§5)".format(UNAUDITED_ZERO),
                 repr([l for l in lg if l])[:200])

        self.check_stats("f1", secs, F1_STATS)

    # ------------------------------------------------------------ F1 --full
    def test_f1_full(self):
        out, err, rc = self.run(F1, "--full")
        secs = self.base("f1full", out, err, rc)
        wl = self.sec(secs, 0)
        self.check_count_line("f1full", secs, F1_COUNT)
        for (iid, _status, _origin, _date, seg, body) in F1_ITEMS:
            line = find_line_with(wl, iid)
            want = "{} — {}".format(seg, body)
            ok = line is not None and want in line
            self.add("f1full/fulltext-{}".format(iid), ok,
                     "行に {!r} を含む(§5: 記帳座標セグメント — 本文・--full で切り詰めなし)".format(want),
                     "行なし" if line is None else
                     ("OK" if ok else repr(line.strip()[:200])))

    # ------------------------------------------------------------ F2
    def test_f2(self):
        out, err, rc = self.run(F2)
        secs = self.base("f2", out, err, rc)
        wl = self.sec(secs, 0)

        self.check_count_line("f2", secs, F2_COUNT)

        line = find_line_with(wl, "EXP-20260710-01")
        self.add("f2/item-normal-listed", line is not None,
                 "正常 open 項目 EXP-20260710-01 が worklist に列挙(§5)",
                 "OK" if line else "行なし")

        leaked = [i for i in F2_NON_ITEMS if find_line_with(wl, i)]
        self.add("f2/warned-lines-not-counted", not leaked,
                 "W2〜W6 の行は項目として計上しない(§4)",
                 "混入 {}".format(leaked) if leaked else "OK")

        self.check_zero("f2", secs, 1, "actions-due-zero")

        # 警告行の書式・集合・昇順
        wsec = [l.strip() for l in self.sec(secs, 2) if l.strip()]
        parsed = []
        badfmt = []
        for l in wsec:
            m = re.match(r"^- L(\d+) (W[1-6]): ", l)
            if m:
                parsed.append((int(m.group(1)), m.group(2)))
            else:
                badfmt.append(l)
        self.add("f2/warning-line-format", wsec != [] and not badfmt,
                 "各行は '- L{行番号} {Wコード}: ' で始まる(§5)",
                 "OK" if (wsec and not badfmt) else "不一致行 {}".format(
                     [b[:80] for b in badfmt][:5]))

        got_fixed = {p for p in parsed if p[1] != "W1"}
        got_w1 = {p for p in parsed if p[1] == "W1"}
        ok_set = (got_fixed == F2_WARN_FIXED and
                  len(got_w1) >= 1 and got_w1 <= F2_W1_ALLOWED)
        self.add("f2/warning-set", ok_set,
                 "W4@L8 W3@L9 W2@L10 W5@L11 W6@L12 + W1(L7 または L13)(§4・行番号は物理行)",
                 str(sorted(parsed)))

        nums = [n for n, _c in parsed]
        self.add("f2/warning-ascending", nums == sorted(nums) and len(nums) >= 1,
                 "行番号の昇順(§5)", str(nums))

        # legacy coverage(マーカーあり・legacy 節なし)
        lg = [l.strip() for l in self.sec(secs, 3)]
        self.add("f2/legacy-basis-marker",
                 first_nonempty(self.sec(secs, 3)) == BASIS_MARKER,
                 "1 行目 {!r}(§5)".format(BASIS_MARKER),
                 repr(first_nonempty(self.sec(secs, 3))))
        self.add("f2/legacy-audited-0", audited_line(0) in lg,
                 repr(audited_line(0)) + "(§5)", repr([l for l in lg if l])[:200])
        self.add("f2/legacy-unaudited-zero", UNAUDITED_ZERO in lg,
                 repr(UNAUDITED_ZERO) + "(§5)", repr([l for l in lg if l])[:200])

        vw_accept = {len(parsed)} & {6, 7} if parsed else {6, 7}
        self.check_stats("f2", secs, F2_STATS_FIXED, vw_accept=vw_accept)

    # ------------------------------------------------------------ F3(空)
    def test_f3(self):
        out, err, rc = self.run(F3)
        secs = self.base("f3", out, err, rc)
        self.check_zero("f3", secs, 0, "worklist-zero")
        self.check_zero("f3", secs, 1, "actions-due-zero")
        self.check_zero("f3", secs, 2, "warnings-zero")
        lg = "\n".join(self.sec(secs, 3))
        ok = BASIS_MARKER not in lg and BASIS_FALLBACK not in lg
        self.add("f3/legacy-no-boundary", ok,
                 "境界なし — '境界の根拠: marker/migration-section(fallback)' を出さない(§3/§5・文言自体は U6)",
                 "OK" if ok else repr(lg[:200]))
        self.check_stats("f3", secs, F3_STATS)

    # ------------------------------------------------------------ F4(fallback)
    def test_f4(self):
        out, err, rc = self.run(F4)
        secs = self.base("f4", out, err, rc)
        self.check_count_line("f4", secs, F4_COUNT)
        lg = [l.strip() for l in self.sec(secs, 3)]
        self.add("f4/legacy-basis-fallback",
                 first_nonempty(self.sec(secs, 3)) == BASIS_FALLBACK,
                 "1 行目 {!r}(§3/§5)".format(BASIS_FALLBACK),
                 repr(first_nonempty(self.sec(secs, 3))))
        self.add("f4/legacy-audited-1", audited_line(1) in lg,
                 repr(audited_line(1)) + "(§5)", repr([l for l in lg if l])[:200])
        enum = [l for l in lg if re.match(r"^- L\d+: ", l)]
        ok = (len(enum) == 1 and enum[0].startswith("- L12: ")
              and "旧節B" in enum[0] and UNAUDITED_ZERO not in lg)
        self.add("f4/legacy-unaudited-enum", ok,
                 "列挙 1 行 '- L12: …旧節B…'(§5・タイトル切り詰めは U7 のため部分一致)",
                 str([e[:100] for e in enum]) if enum else repr([l for l in lg if l])[:200])
        self.check_stats("f4", secs, F4_STATS)

    # ------------------------------------------------------------ F5(境界後 legacy)
    def test_f5(self):
        out, err, rc = self.run(F5)
        secs = self.base("f5", out, err, rc)
        self.check_count_line("f5", secs, F5_COUNT)
        lg = [l.strip() for l in self.sec(secs, 3)]
        self.add("f5/legacy-basis-marker",
                 first_nonempty(self.sec(secs, 3)) == BASIS_MARKER,
                 "1 行目 {!r}(§5)".format(BASIS_MARKER),
                 repr(first_nonempty(self.sec(secs, 3))))
        self.add("f5/legacy-audited-1", audited_line(1) in lg,
                 repr(audited_line(1)) + "(§5)", repr([l for l in lg if l])[:200])
        enum = [l for l in lg if re.match(r"^- L\d+: ", l)]
        ok = (len(enum) == 1 and enum[0].startswith("- L13: ")
              and "後置" in enum[0] and UNAUDITED_ZERO not in lg)
        self.add("f5/legacy-unaudited-enum", ok,
                 "列挙 1 行 '- L13: …後置…'(§5・U7 のため部分一致)",
                 str([e[:100] for e in enum]) if enum else repr([l for l in lg if l])[:200])
        self.check_stats("f5", secs, F5_STATS)

    # ------------------------------------------------------------ show
    def _show_case(self, tag, ident, path, must_contain):
        out, err, rc = self.run("show", ident, path)
        self.base(tag, out, err, rc, with_sections=False)
        missing = [t for t in must_contain if t not in out]
        self.add(tag + "/content", not missing,
                 "表示に {} を含む(§5 show: ID・状態・origin・本文・source/evidence・節タイトル)".format(
                     [t[:40] for t in must_contain]),
                 "OK" if not missing else "欠落 {}".format([m[:60] for m in missing]))

    def test_show(self):
        # evidence + migrated + 節タイトル
        self._show_case("show-evidence", "EXP-20260601-01", F1,
                        ["EXP-20260601-01", "open", "migrated",
                         "移行残高の open 項目", "2026-06 節・観測1", "移行残高(F1)"])
        # source
        self._show_case("show-source", "OBS-20260601-02", F1,
                        ["OBS-20260601-02", "watch 2/3", "移行残高の watch 項目",
                         "ECO-101", "ECO-102"])
        # origin 上書き(native)+ 節タイトル
        self._show_case("show-origin-override", "EXP-20260702-04", F1,
                        ["EXP-20260702-04", "native", "移行残高(F1)"])
        # not found
        out, err, rc = self.run("show", "EXP-99990101-99", F1)
        self.base("show-notfound", out, err, rc, with_sections=False)
        self.add("show-notfound/content", "EXP-99990101-99" in out and out.strip() != "",
                 "not found の旨に当該 ID を含む(§5)・exit 0(§6)",
                 repr(out.strip()[:160]))
        # ID 引数欠落 → 使用法 1 行
        out, err, rc = self.run("show")
        self.base("show-no-id", out, err, rc, with_sections=False)
        lines = [l for l in out.splitlines() if l.strip()]
        self.add("show-no-id/usage-one-line", len(lines) == 1,
                 "使用法 1 行のみを stdout へ(§2)", repr(lines[:3]))

    # ------------------------------------------------------------ その他の契約
    def test_misc(self):
        # 入力ファイル不在: stdout にパス・exit 0
        missing = os.path.join(BASE, "no-such-input-zz9.md")
        out, err, rc = self.run(missing)
        self.base("missing-file", out, err, rc, with_sections=False)
        self.add("missing-file/path-in-stdout",
                 "no-such-input-zz9.md" in out,
                 "エラーの旨に当該パスを含む(§5。パス区切り正規化を許容しファイル名で照合)",
                 repr(out.strip()[:200]))

        # --selftest
        out, err, rc = self.run("--selftest")
        self.add("selftest/exit0", rc == 0, "exit code 0(§6-§7)", "exit code {}".format(rc))
        self.add("selftest/stderr-empty", err.strip() == "", "stderr は空(§5)",
                 repr(err.strip()[:200]))
        self.add("selftest/pass-line", "selftest: PASS" in out,
                 "'selftest: PASS' を含む行(§7)", repr(out.strip()[:200]))

        # 位置引数解釈: 最初の非フラグ引数が PATH(--full が先でも)
        out, err, rc = self.run("--full", F1)
        secs = split_sections(out)
        ok = rc == 0 and secs is not None and \
            first_nonempty(secs[0]) == F1_COUNT
        self.add("argparse/first-nonflag-is-path", ok,
                 "'--full <PATH>' でも PATH が解釈される(§2)",
                 "OK" if ok else "rc={} 冒頭行={!r}".format(
                     rc, first_nonempty(secs[0]) if secs else None))

        # 相対 PATH(cwd 基準)受け付け(§8)
        rel = os.path.relpath(F1, BASE)
        out, err, rc = self.run(rel)
        secs = split_sections(out)
        ok = rc == 0 and secs is not None and first_nonempty(secs[0]) == F1_COUNT
        self.add("path/relative-accepted", ok,
                 "相対 PATH(cwd 基準)で同一結果(§8)",
                 "OK" if ok else "rc={} 冒頭行={!r}".format(
                     rc, first_nonempty(secs[0]) if secs else None))

    # ------------------------------------------------------------ 実行と報告
    def report(self):
        npass = sum(1 for _n, ok, _e, _g in self.results if ok)
        total = len(self.results)
        for name, ok, expected, got in self.results:
            if ok:
                print("PASS {}".format(name))
            else:
                print("FAIL {}".format(name))
                print("     期待: {}".format(expected))
                print("     実測: {}".format(got))
        verdict = "PASS" if npass == total else "FAIL"
        print("ORACLE: {} ({}/{})".format(verdict, npass, total))
        return 0 if npass == total else 1


def main(argv):
    if len(argv) != 2:
        print("usage: python oracle.py <path-to-implementation.py>")
        return 2
    impl = argv[1]
    if not os.path.isfile(impl):
        print("oracle: implementation not found: {}".format(impl))
        return 2
    for f in (F1, F2, F3, F4, F5):
        if not os.path.isfile(f):
            print("oracle: fixture not found: {}".format(f))
            return 2
    o = Oracle(impl)
    o.test_f1()
    o.test_f1_full()
    o.test_f2()
    o.test_f3()
    o.test_f4()
    o.test_f5()
    o.test_show()
    o.test_misc()
    return o.report()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
