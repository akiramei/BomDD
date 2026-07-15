# worklist — improvements.md 追跡項目(EXP/OBS)の読み取りビュー(read-only)
#
# lesson-promote 手順 4(期待効果の棚卸し)の走査起点。記帳スキーマ v1
# (.claude/skills/lesson-promote/SKILL.md「追跡項目の記帳スキーマ」)の新書式のみを
# 厳密に解析し、worklist(open/watch)・actions due・validation warnings・
# legacy coverage・stats を表示する。
# 初出: 2026-07-15 レビュー裁定(スキーマ+ビュー+期首移行 — improvements.md 移行残高節)。
#
# 解析原則(v1 で凍結):
#  1. 新書式は厳密に読む(状態語彙 5 種+ID 文法+証拠座標の必須性+watch 現在値)。
#  2. 旧書式(legacy 節)をヒューリスティックに推測して open 扱いしない — 読み落としを
#     スクリプト内部へ移さない。legacy の棚卸し境界は明示マーカー
#     `<!-- worklist-legacy-audit-cutoff: YYYY-MM-DD -->` を正本とする(マーカー以前=
#     audited/以後の legacy 節= unaudited=逸脱。マーカー不在時のみ移行残高節の位置で代替)。
#  3. 解釈できないマーカー行・マーカーなし追跡項目は黙って無視せず warnings に出す。
#     fenced code block・blockquote・HTML コメント内は例示とみなし解析対象外(誤認しない)。
#  4. **要処理事項(actions due)と記帳不整合(validation warnings)は別区分** —
#     watch 3/3 到達(PROMOTION DUE)は不正な記帳ではなく、正しく蓄積された結果の
#     レビュー要求。警告と混ぜると「正常運用でも警告が残る」状態になり真の異常が埋もれる。
#  5. 発生元の区分: 期首移行残高(origin: migrated)と新書式の新規(origin: native)を
#     ビュー上で分ける — 移行残高 43 件に新規 open が埋もれないため。既定=移行残高節内は
#     migrated・それ以外は native。継続行 `origin:` で明示上書き可。
#  6. 終了コードは常に 0(読み取り専用)。validator/CI ゲートへの昇格は運用実測後に
#     二軸(認知コスト/品質リスク)で判断する。--selftest のみ失敗時に exit 1。
#
# 使い方:
#   python worklist.py [path] [--full]      # 既定: ../improvements.md(--full= 本文を切り詰めない)
#   python worklist.py show <ID> [path]     # 1 項目の全文+source/evidence+節を表示
#   python worklist.py --selftest           # 陽性対照(全状態+全警告種+除外領域の恒久 fixture)
#
# validation warnings(記帳不整合):
#   W1 ID 重複(状態遷移は行内書き換え=同一 ID の追跡行は常に 1 本)
#   W2 不明な状態値 / W3 closed 系の日付・via 欠落 / W4 watch の現在値 N/3 欠落
#   W5 状態マーカーのない追跡項目 / W6 本文が「<ID> — <内容>」形式でない
# actions due(要処理事項 — 記帳は正常):
#   PROMOTION DUE = watch N/3 が N>=3(昇格審査の停止点。件数の妥当性も含め判断させる)

import re
import sys
import time
from pathlib import Path

STATES = ("open", "watch", "recovered", "withdrawn", "superseded")
CLOSED = ("recovered", "withdrawn", "superseded")

SECTION_RE = re.compile(r"^##\s+(.*)$")
DATE_IN_TITLE_RE = re.compile(r"(\d{4}-\d{2}(?:-\d{2})?)")
MIGRATION_MARK = "移行残高"
AUDIT_CUTOFF_RE = re.compile(r"worklist-legacy-audit-cutoff:\s*(\d{4}-\d{2}-\d{2})")
BRACKET_LINE_RE = re.compile(r"^\s*-\s*\[([^\]]*)\]\s*(.*)$")
ID_TOKEN = r"(?:EXP|OBS)-[A-Za-z0-9]+-\d{2}"
ID_RE = re.compile(rf"\b({ID_TOKEN})\b")
BODY_RE = re.compile(rf"^({ID_TOKEN})\s+—\s+(.+)$")
BARE_ITEM_RE = re.compile(rf"^\s*-\s+({ID_TOKEN})\b")
WATCH_RE = re.compile(r"^watch\s+(\d)\s*/\s*3$")
CLOSED_RE = re.compile(r"^(recovered|withdrawn|superseded)\s+(\d{4}-\d{2}-\d{2})\s+via\s+(.+\S)$")
CONT_RE = re.compile(r"^\s+(evidence|source|origin):\s*(.+\S)\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
COMMENT_SPAN_RE = re.compile(r"<!--.*?-->")


def parse(text):
    """text -> (items, warnings, dues, sections, cutoff_line)"""
    items, warnings, sections = [], [], []
    cur = None            # 現在の節 index
    attach = None         # 直前に確定した item(継続行の付与先)
    in_fence = False
    in_comment = False
    cutoff_line = None    # 棚卸し境界マーカーの行番号(コメント除去より前に検出)

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw

        cm0 = AUDIT_CUTOFF_RE.search(raw)
        if cm0 and cutoff_line is None:
            cutoff_line = line_no

        # 除外領域: HTML コメント(単一行スパンは除去・複数行は状態で跨ぐ)
        if in_comment:
            if "-->" in line:
                line = line.split("-->", 1)[1]
                in_comment = False
            else:
                continue
        line = COMMENT_SPAN_RE.sub("", line)
        if "<!--" in line:
            line = line.split("<!--", 1)[0]
            in_comment = True

        # 除外領域: fenced code block(例示を追跡項目と誤認しない)
        if FENCE_RE.match(line):
            in_fence = not in_fence
            attach = None
            continue
        if in_fence:
            continue
        # 除外領域: blockquote(過去記録の引用)
        if re.match(r"^\s*>", line):
            attach = None
            continue

        m = SECTION_RE.match(line)
        if m:
            title = m.group(1).strip()
            dm = DATE_IN_TITLE_RE.search(title)
            sections.append({"title": title, "line_no": line_no,
                             "date": dm.group(1) if dm else "-",
                             "structured": False,
                             "migration": MIGRATION_MARK in title})
            cur = len(sections) - 1
            attach = None
            continue

        cm = CONT_RE.match(line)
        if cm and attach is not None:
            attach[cm.group(1)] = cm.group(2)
            continue

        bm = BRACKET_LINE_RE.match(line)
        if bm:
            attach = None
            bracket, rest = bm.group(1).strip(), bm.group(2).strip()
            head = bracket.split()[0] if bracket else ""
            if head in STATES:
                attach = _parse_marker_line(bracket, head, rest, line_no, cur,
                                            items, warnings, sections)
            elif ID_RE.search(rest) or ID_RE.search(bracket):
                warnings.append((line_no, "W2",
                                 f"不明な状態値 [{bracket}](語彙: {'/'.join(STATES)})"))
                if cur is not None:
                    sections[cur]["structured"] = True
            # それ以外(markdown リンク等の通常の [ ] 行)は追跡項目でない — 対象外
            continue

        im = BARE_ITEM_RE.match(line)
        if im:
            attach = None
            warnings.append((line_no, "W5",
                             f"状態マーカーのない追跡項目: {im.group(1)}"))
            if cur is not None:
                sections[cur]["structured"] = True
            continue

        if line.strip():
            attach = None

    # origin の確定(既定: 移行残高節内= migrated / それ以外= native。origin: で上書き)
    for it in items:
        default = "migrated" if (it["section_idx"] is not None
                                 and sections[it["section_idx"]]["migration"]) else "native"
        it["origin"] = it.get("origin", default)

    # W1: ID 重複(追跡行として 2 回以上出現)
    seen = {}
    for it in items:
        seen.setdefault(it["id"], []).append(it["line_no"])
    for id_, lines in seen.items():
        if len(lines) > 1:
            warnings.append((lines[1], "W1",
                             f"ID 重複: {id_}(L{', L'.join(map(str, lines))}"
                             " — 状態遷移は行内書き換え・行の複製禁止)"))

    # actions due: watch 閾値到達(PROMOTION DUE — 記帳不整合ではない)
    dues = []
    for it in items:
        if it["state"] == "watch" and it.get("watch_n", 0) >= 3:
            it["promotion_due"] = True
            dues.append(it)

    warnings.sort(key=lambda w: w[0])
    return items, warnings, dues, sections, cutoff_line


def _parse_marker_line(bracket, head, rest, line_no, cur, items, warnings, sections):
    if cur is not None:
        sections[cur]["structured"] = True

    state, detail, watch_n = None, "", 0
    if head == "open":
        if bracket == "open":
            state = "open"
        else:
            warnings.append((line_no, "W6", f"open に余分な語: [{bracket}]"))
            return None
    elif head == "watch":
        wm = WATCH_RE.match(bracket)
        if wm:
            state, watch_n = "watch", int(wm.group(1))
            detail = f"{watch_n}/3"
        else:
            warnings.append((line_no, "W4",
                             f"watch の現在値 N/3 欠落: [{bracket}]"))
            return None
    else:  # closed 系
        cmm = CLOSED_RE.match(bracket)
        if cmm:
            state, detail = cmm.group(1), f"{cmm.group(2)} via {cmm.group(3)}"
        else:
            warnings.append((line_no, "W3",
                             f"{head} の日付または via <証拠> 欠落: [{bracket}]"))
            return None

    body = BODY_RE.match(rest)
    if not body:
        warnings.append((line_no, "W6",
                         f"本文が「<ID> — <内容>」形式でない: {rest[:60]}"))
        return None
    item = {"id": body.group(1), "state": state, "detail": detail,
            "watch_n": watch_n, "text": body.group(2),
            "section_idx": cur, "line_no": line_no}
    items.append(item)
    return item


def _audit_split(sections, cutoff_line):
    """legacy 節を audited/unaudited に分ける。正本=マーカー行・代替=移行残高節位置。"""
    legacy = [(i, s) for i, s in enumerate(sections) if not s["structured"]]
    if cutoff_line is not None:
        audited = [s for _, s in legacy if s["line_no"] < cutoff_line]
        unaudited = [s for _, s in legacy if s["line_no"] > cutoff_line]
        return audited, unaudited, "marker"
    mig = [i for i, s in enumerate(sections) if s["migration"]]
    if mig:
        m = max(mig)
        audited = [s for i, s in legacy if i < m]
        unaudited = [s for i, s in legacy if i > m]
        return audited, unaudited, "migration-section(fallback)"
    return [], [s for _, s in legacy], None


def render(items, warnings, dues, sections, cutoff_line, elapsed_ms,
           full=False, out=sys.stdout):
    w = out.write
    open_watch = [i for i in items if i["state"] in ("open", "watch")]
    native = [i for i in open_watch if i["origin"] == "native"]
    migrated = [i for i in open_watch if i["origin"] == "migrated"]

    def _count(lst, st):
        return sum(1 for i in lst if i["state"] == st)

    w("== worklist(open / watch)==\n")
    if open_watch:
        w(f"native(新書式の新規): open {_count(native, 'open')} / watch {_count(native, 'watch')}"
          f" ・ migrated(期首移行残高): open {_count(migrated, 'open')} /"
          f" watch {_count(migrated, 'watch')}\n\n")
        w(f"{'ID':<22}{'状態':<14}{'区分':<10}{'発生':<12}根拠 / 内容\n")
        for it in open_watch:
            sec = sections[it["section_idx"]] if it["section_idx"] is not None else None
            date = sec["date"] if sec else "-"
            src = it["id"].split("-")[1]
            state = it["state"] + (f" {it['detail']}" if it["detail"] else "")
            if it.get("promotion_due"):
                state += " ★DUE"
            text = it["text"] if full else \
                it["text"][:70] + ("…" if len(it["text"]) > 70 else "")
            w(f"{it['id']:<22}{state:<14}{it['origin']:<10}{date:<12}{src} — {text}\n")
    else:
        w("(0 件)\n")

    w("\n== actions due(要処理 — 記帳は正常)==\n")
    if dues:
        for it in dues:
            w(f"- PROMOTION DUE  {it['id']}  watch {it['detail']} — 昇格審査へ"
              f"(3 例の独立性も含め判断する停止点)\n")
    else:
        w("(0 件)\n")

    w("\n== validation warnings(記帳不整合)==\n")
    if warnings:
        for line_no, code, msg in warnings:
            w(f"- L{line_no} {code}: {msg}\n")
    else:
        w("(0 件)\n")

    audited, unaudited, basis = _audit_split(sections, cutoff_line)
    w("\n== legacy coverage ==\n")
    if basis:
        w(f"境界の根拠: {basis}\n")
        w(f"audited(棚卸し済み — 状態の正本は移行残高節): {len(audited)} 節\n")
        if unaudited:
            w("unaudited(境界以後に増えた未構造化節 — 逸脱・要棚卸し):\n")
            for s in unaudited:
                w(f"- L{s['line_no']}: {s['title'][:80]}\n")
        else:
            w("unaudited: 0 節\n")
    else:
        w("(棚卸し境界なし — 全 legacy 節が未棚卸し)\n")
        for s in unaudited:
            w(f"- L{s['line_no']}: {s['title'][:80]}\n")

    legacy_n = len(audited) + len(unaudited)
    closed = [i for i in items if i["state"] in CLOSED]
    w("\n== stats ==\n")
    w(f"sections_scanned: {len(sections)}\n")
    w(f"structured_sections: {len(sections) - legacy_n}\n")
    w(f"audited_legacy_sections: {len(audited)}\n")
    w(f"unaudited_legacy_sections: {len(unaudited)}\n")
    w(f"open_items: {sum(1 for i in items if i['state'] == 'open')}"
      f"(native {_count(native, 'open')} / migrated {_count(migrated, 'open')})\n")
    w(f"watch_items: {sum(1 for i in items if i['state'] == 'watch')}"
      f"(native {_count(native, 'watch')} / migrated {_count(migrated, 'watch')})\n")
    w(f"actions_due: {len(dues)}\n")
    w(f"closed_items: {len(closed)}(recovered/withdrawn/superseded)\n")
    w(f"validation_warnings: {len(warnings)}\n")
    w(f"elapsed_ms: {elapsed_ms}\n")


def show(items, sections, id_, out=sys.stdout):
    w = out.write
    hits = [i for i in items if i["id"] == id_]
    if not hits:
        w(f"(not found: {id_})\n")
        return
    for it in hits:
        sec = sections[it["section_idx"]] if it["section_idx"] is not None else None
        w(f"{it['id']}  [{it['state']}{' ' + it['detail'] if it['detail'] else ''}]"
          f"  origin={it['origin']}"
          f"{'  ★PROMOTION DUE' if it.get('promotion_due') else ''}\n")
        w(f"  L{it['line_no']}: {it['text']}\n")
        if it.get("source"):
            w(f"  source: {it['source']}\n")
        if it.get("evidence"):
            w(f"  evidence: {it['evidence']}\n")
        if sec:
            w(f"  節: {sec['title']}(L{sec['line_no']})\n")


# ---- 陽性対照(selftest — 恒久 fixture)-----------------------------------
# 検査器の沈黙対策(FINDINGS §8.3): 空の worklist と壊れた解析器を区別する較正。
# 全 5 状態・全 6 記帳不整合・PROMOTION DUE(3/3 と 4/3)・除外領域(fence/blockquote/
# HTML コメント/リンク行)・継続行(evidence/origin)・棚卸し境界マーカー・
# native/migrated 区分を 1 fixture で踏む。worklist.py 変更時は必ず --selftest を実行(CI 収載済み)。

SELFTEST_FIXTURE = """\
# fixture

## 2026-07-10 fixture 旧節 — legacy(境界マーカー以前=棚卸し済み扱い)

期待する効果: 散文のみ(推測して open 扱いしないこと)。

<!-- worklist-legacy-audit-cutoff: 2026-07-15 -->

## 2026-07-15 method 還元 — 記帳スキーマ v1 移行残高(fixture)

- [open] EXP-20260713-01 — 移行 open 項目
  evidence: 2026-07-13 節・観測1
- [watch 2/3] OBS-20260713-02 — 移行 watch 項目
- [watch 3/3] OBS-20260713-03 — 閾値到達(PROMOTION DUE)
- [watch 4/3] OBS-20260713-04 — 超過も PROMOTION DUE
- [recovered 2026-07-18 via ECO-092] EXP-20260710-01 — 回収済み
- [withdrawn 2026-07-18 via REVIEW-014] EXP-20260710-02 — 実施せず終了
- [superseded 2026-07-18 via OBS-20260713-02] OBS-20260710-03 — 別項目へ吸収
- [open] EXP-20260715-99 — 移行節内だが新規(origin 上書き)
  origin: native

## 2026-07-16 fixture 新節 — 新書式+警告種

- [open] EXP-20260716-01 — 通常 open(native)
- [watch] OBS-20260716-02 — W4: 現在値なし
- [recovered 2026-07-18] EXP-20260716-03 — W3: via なし
- [pending] EXP-20260716-04 — W2: 語彙外の状態
- EXP-20260716-05 — W5: マーカーなしの追跡項目
- [open] EXP-20260716-06 -- W6: 本文区切りが「—」でない
- [recovered 2026-07-19 via ECO-093] EXP-20260716-01 — W1: 重複(行内書き換え違反)
- [改善ログ](improvements.md) — 通常のリンク行は警告対象外

```markdown
- [open] EXP-99999999-01 — fence 内の例示は解析対象外
```

> - [open] EXP-88888888-01 — blockquote 内の過去記録は解析対象外

<!-- - [open] EXP-77777777-01 — HTML コメント内は解析対象外 -->

## 2026-07-17 fixture 後置節 — 境界以後に増えた legacy(unaudited=逸脱)

期待する効果: 散文のみ。
"""

SELFTEST_EXPECT = dict(
    open=3, watch=3, closed=4, dues=2,
    native_active=2, migrated_active=4,
    warn_codes={"W1": 1, "W2": 1, "W3": 1, "W4": 1, "W5": 1, "W6": 1},
    structured=2, audited=1, unaudited=1, basis="marker",
    evidence_attached=True,
)


def selftest():
    items, warnings, dues, sections, cutoff = parse(SELFTEST_FIXTURE)
    audited, unaudited, basis = _audit_split(sections, cutoff)
    active = [i for i in items if i["state"] in ("open", "watch")]
    got = dict(
        open=sum(1 for i in items if i["state"] == "open"),
        watch=sum(1 for i in items if i["state"] == "watch"),
        closed=sum(1 for i in items if i["state"] in CLOSED),
        dues=len(dues),
        native_active=sum(1 for i in active if i["origin"] == "native"),
        migrated_active=sum(1 for i in active if i["origin"] == "migrated"),
        warn_codes={c: sum(1 for _, code, _ in warnings if code == c)
                    for c in ("W1", "W2", "W3", "W4", "W5", "W6")},
        structured=sum(1 for s in sections if s["structured"]),
        audited=len(audited),
        unaudited=len(unaudited),
        basis=basis,
        evidence_attached=any(i.get("evidence") == "2026-07-13 節・観測1"
                              for i in items),
    )
    ok = got == SELFTEST_EXPECT
    print("selftest:", "PASS" if ok else "FAIL")
    if not ok:
        for k in SELFTEST_EXPECT:
            if got[k] != SELFTEST_EXPECT[k]:
                print(f"  {k}: expect {SELFTEST_EXPECT[k]} / got {got[k]}")
        for wline in warnings:
            print("  ", wline)
    return 0 if ok else 1


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if "--selftest" in argv:
        return selftest()

    show_id = None
    if argv and argv[0] == "show":
        if len(argv) < 2:
            print("usage: worklist.py show <ID> [path]")
            return 0
        show_id = argv[1]
        argv = argv[2:]

    full = "--full" in argv
    paths = [a for a in argv if not a.startswith("--")]
    path = Path(paths[0]) if paths else \
        Path(__file__).resolve().parent.parent / "improvements.md"
    if not path.is_file():
        print(f"error: file not found: {path}")
        return 0  # 読み取り専用ツール — ゲートとして使わない(v1 凍結)
    t0 = time.perf_counter()
    items, warnings, dues, sections, cutoff = parse(path.read_text(encoding="utf-8"))
    elapsed_ms = round((time.perf_counter() - t0) * 1000)
    if show_id:
        show(items, sections, show_id)
    else:
        render(items, warnings, dues, sections, cutoff, elapsed_ms, full=full)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
