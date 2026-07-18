#!/usr/bin/env python3
"""Read-only worklist view for the tracking-ledger Markdown schema."""

from __future__ import annotations
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

IDP = r"(?:EXP|OBS)-[A-Za-z0-9]+-\d{2}"
ID_RE = re.compile(IDP)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}|\d{4}-\d{2}")
CUTOFF_RE = re.compile(r"worklist-legacy-audit-cutoff:\s*\d{4}-\d{2}-\d{2}")
BRACKET_RE = re.compile(r"^\s*-\s+\[([^\]]*)\](.*)$")
BULLET_RE = re.compile(r"^\s*-\s+(.+)$")
BODY_RE = re.compile(rf"^\s+({IDP})\s+—\s+(\S(?:.*\S)?)\s*$")
CONT_RE = re.compile(r"^[ \t]+(evidence|source|origin):[ \t]*(.*)$")
FENCE_RE = re.compile(r"^[ \t]{0,3}(\x60{3,}|~{3,})(?:.*)$")
STATUSES = {"open", "watch", "recovered", "withdrawn", "superseded"}
CLOSED = {"recovered", "withdrawn", "superseded"}
USAGE = "usage: worklist.py [PATH] [--full] | worklist.py show <ID> [PATH] | worklist.py --selftest"
SHOW_USAGE = "usage: worklist.py show <ID> [PATH]"


@dataclass
class Section:
    title: str
    line: int
    date: str
    migrated: bool
    structured: bool = False


@dataclass
class Item:
    item_id: str
    status: str
    marker: str
    body: str
    line: int
    section: Section
    watch_n: Optional[int] = None
    origin: str = "native"
    sources: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)


@dataclass(order=True)
class WarningRecord:
    line: int
    code: str
    message: str


@dataclass
class ParseResult:
    sections: list[Section]
    items: list[Item]
    warnings: list[WarningRecord]
    boundary_kind: Optional[str]
    audited: list[Section]
    unaudited: list[Section]


def configure_stdout() -> None:
    method = getattr(sys.stdout, "reconfigure", None)
    if method:
        method(encoding="utf-8", errors="replace", newline="\n")


def strip_comments(line: str, inside: bool) -> tuple[str, bool]:
    visible, at = [], 0
    while at < len(line):
        if inside:
            end = line.find("-->", at)
            if end < 0:
                return "".join(visible), True
            at, inside = end + 3, False
        else:
            start = line.find("<!--", at)
            if start < 0:
                visible.append(line[at:])
                break
            visible.append(line[at:start])
            at, inside = start + 4, True
    return "".join(visible), inside


def parse_marker(marker: str) -> Optional[tuple[str, Optional[int]]]:
    if marker == "open":
        return "open", None
    match = re.fullmatch(r"watch ([0-9])/3", marker)
    if match:
        return "watch", int(match.group(1))
    match = re.fullmatch(
        r"(recovered|withdrawn|superseded) \d{4}-\d{2}-\d{2} via \S(?:.*\S)?",
        marker,
    )
    return (match.group(1), None) if match else None


def marker_warning(marker: str, line: int) -> WarningRecord:
    first = marker.split(maxsplit=1)[0] if marker.strip() else ""
    if first not in STATUSES:
        return WarningRecord(line, "W2", f"unknown state value {(first or '(empty)')!r}")
    if first in CLOSED:
        return WarningRecord(
            line, "W3", "closed state requires YYYY-MM-DD and 'via <evidence>'"
        )
    if first == "watch":
        if re.match(r"watch [0-9]/3\s+", marker):
            return WarningRecord(
                line, "W6", "expected an exact state marker and 'ID — body'"
            )
        return WarningRecord(line, "W4", "watch state requires a one-digit N/3 value")
    return WarningRecord(line, "W6", "expected an exact state marker and 'ID — body'")


def parse_text(text: str) -> ParseResult:
    lines = text.splitlines()
    cutoff_line = next(
        (n for n, raw in enumerate(lines, 1) if CUTOFF_RE.search(raw)), None
    )
    sections: list[Section] = []
    items: list[Item] = []
    warnings: list[WarningRecord] = []
    section: Optional[Section] = None
    item: Optional[Item] = None
    in_comment = False
    fence: Optional[tuple[str, int]] = None

    for number, raw in enumerate(lines, 1):
        if not raw.strip():
            item = None
            continue
        visible, in_comment = strip_comments(raw, in_comment)
        if not visible.strip():
            continue
        fence_match = FENCE_RE.match(visible)
        if fence:
            item = None
            if fence_match:
                token = fence_match.group(1)
                if token[0] == fence[0] and len(token) >= fence[1]:
                    fence = None
            continue
        if fence_match:
            token = fence_match.group(1)
            fence, item = (token[0], len(token)), None
            continue
        if re.match(r"^\s*>", visible):
            item = None
            continue
        if visible.startswith("## "):
            title = visible[3:].strip()
            found_date = DATE_RE.search(title)
            section = Section(
                title, number, found_date.group(0) if found_date else "-", "移行残高" in title
            )
            sections.append(section)
            item = None
            continue
        continuation = CONT_RE.match(visible)
        if continuation and item:
            key, value = continuation.group(1), continuation.group(2).strip()
            if key == "source":
                item.sources.append(value)
            elif key == "evidence":
                item.evidence.append(value)
            elif value in {"native", "migrated"}:
                item.origin = value
            continue

        item = None
        if section is None or ID_RE.search(visible) is None:
            continue
        bracket, bullet = BRACKET_RE.match(visible), BULLET_RE.match(visible)
        if bracket:
            section.structured = True
            marker = bracket.group(1).strip()
            parsed = parse_marker(marker)
            if parsed is None:
                warnings.append(marker_warning(marker, number))
                continue
            body = BODY_RE.fullmatch(bracket.group(2))
            if body is None:
                warnings.append(
                    WarningRecord(number, "W6", "expected an exact '[state] ID — body' line")
                )
                continue
            status, watch_n = parsed
            item = Item(
                body.group(1),
                status,
                marker,
                body.group(2),
                number,
                section,
                watch_n,
                "migrated" if section.migrated else "native",
            )
            items.append(item)
        elif bullet:
            section.structured = True
            warnings.append(WarningRecord(number, "W5", "tracking item lacks a state marker"))

    first_by_id: dict[str, Item] = {}
    for entry in items:
        first = first_by_id.get(entry.item_id)
        if first:
            warnings.append(
                WarningRecord(
                    entry.line,
                    "W1",
                    f"duplicate ID {entry.item_id} (first occurrence L{first.line})",
                )
            )
        else:
            first_by_id[entry.item_id] = entry
    warnings.sort()
    legacy = [value for value in sections if not value.structured]
    if cutoff_line is not None:
        boundary = "marker"
        audited = [value for value in legacy if value.line < cutoff_line]
        unaudited = [value for value in legacy if value.line > cutoff_line]
    else:
        migrations = [value for value in sections if value.migrated]
        if migrations:
            boundary = "migration-section(fallback)"
            fallback_line = migrations[-1].line
            audited = [value for value in legacy if value.line < fallback_line]
            unaudited = [value for value in legacy if value.line > fallback_line]
        else:
            boundary, audited, unaudited = None, [], legacy
    return ParseResult(sections, items, warnings, boundary, audited, unaudited)


def shorten(value: str, width: int) -> str:
    return value if len(value) <= width else value[: width - 1] + "…"


def active(result: ParseResult) -> list[Item]:
    return [item for item in result.items if item.status in {"open", "watch"}]


def due(result: ParseResult) -> list[Item]:
    return [
        item
        for item in result.items
        if item.status == "watch" and item.watch_n is not None and item.watch_n >= 3
    ]


def count(items: list[Item], status: str, origin: str) -> int:
    return sum(item.status == status and item.origin == origin for item in items)


def render_legacy(result: ParseResult) -> list[str]:
    lines = (
        ["境界なし・全 legacy 節が未棚卸し"]
        if result.boundary_kind is None
        else [f"境界の根拠: {result.boundary_kind}"]
    )
    lines.append(
        f"audited(棚卸し済み — 状態の正本は移行残高節): {len(result.audited)} 節"
    )
    if result.unaudited:
        lines.append(f"unaudited(未棚卸し — 要確認): {len(result.unaudited)} 節")
        lines.extend(f"- L{s.line}: {shorten(s.title, 100)}" for s in result.unaudited)
    else:
        lines.append("unaudited: 0 節")
    return lines


def render_report(result: ParseResult, full: bool, elapsed: int) -> str:
    current, action_rows = active(result), due(result)
    lines = ["== worklist(open / watch)=="]
    if not current:
        lines.append("(0 件)")
    else:
        lines.append(
            "native(新書式の新規): open "
            f"{count(current, 'open', 'native')} / watch {count(current, 'watch', 'native')} ・ "
            "migrated(期首移行残高): open "
            f"{count(current, 'open', 'migrated')} / watch {count(current, 'watch', 'migrated')}"
        )
        for item in current:
            state = item.marker + (" ★DUE" if item in action_rows else "")
            body = item.body if full else shorten(item.body, 72)
            coordinate = item.item_id.split("-")[1]
            lines.append(
                f"- {item.item_id} | {state} | {item.origin} | {item.section.date} | "
                f"{coordinate} — {body}"
            )
    lines += ["", "== actions due(要処理 — 記帳は正常)=="]
    lines += (
        [f"- PROMOTION DUE: {item.item_id} (watch {item.watch_n}/3)" for item in action_rows]
        if action_rows
        else ["(0 件)"]
    )
    lines += ["", "== validation warnings(記帳不整合)=="]
    lines += (
        [f"- L{warning.line} {warning.code}: {warning.message}" for warning in result.warnings]
        if result.warnings
        else ["(0 件)"]
    )
    lines += ["", "== legacy coverage =="] + render_legacy(result)
    opens = [item for item in result.items if item.status == "open"]
    watches = [item for item in result.items if item.status == "watch"]
    closed = [item for item in result.items if item.status in CLOSED]
    lines += [
        "",
        "== stats ==",
        f"sections_scanned: {len(result.sections)}",
        f"structured_sections: {sum(s.structured for s in result.sections)}",
        f"audited_legacy_sections: {len(result.audited)}",
        f"unaudited_legacy_sections: {len(result.unaudited)}",
        f"open_items: {len(opens)}(native {count(opens, 'open', 'native')} / migrated {count(opens, 'open', 'migrated')})",
        f"watch_items: {len(watches)}(native {count(watches, 'watch', 'native')} / migrated {count(watches, 'watch', 'migrated')})",
        f"actions_due: {len(action_rows)}",
        f"closed_items: {len(closed)}(recovered/withdrawn/superseded)",
        f"validation_warnings: {len(result.warnings)}",
        f"elapsed_ms: {max(0, elapsed)}",
    ]
    return "\n".join(lines)


def render_show(result: ParseResult, item_id: str) -> str:
    item = next((value for value in result.items if value.item_id == item_id), None)
    if item is None:
        return f"not found: {item_id}"
    is_due = item.status == "watch" and item.watch_n is not None and item.watch_n >= 3
    lines = [
        f"ID: {item.item_id}",
        f"status: {item.marker}{' ★DUE' if is_due else ''}",
        f"origin: {item.origin}",
        f"body: {item.body}",
        f"section: {item.section.title}",
    ]
    lines += [f"source: {value}" for value in item.sources]
    lines += [f"evidence: {value}" for value in item.evidence]
    return "\n".join(lines)


def run_selftest() -> bool:
    fixture = """## 2026-06 legacy
legacy prose
<!-- worklist-legacy-audit-cutoff: 2026-07-01 -->
## 2026-07-01 移行残高
- [open] EXP-202606-01 — migrated open
  source: ECO-1
  evidence: legacy observation
- [watch 1/3] OBS-202606-02 — overridden origin
  origin: native
## 2026-07-02 native
- [watch 3/3] OBS-20260702-01 — due at threshold
- [watch 4/3] OBS-20260702-02 — due over threshold
- [recovered 2026-07-03 via ECO-3] EXP-202606-01 — duplicate recovered
- [withdrawn 2026-07-03 via REVIEW-4] EXP-20260702-03 — withdrawn
- [superseded 2026-07-03 via OBS-20260702-01] OBS-20260702-04 — superseded
- [pending] EXP-20260702-05 — W2
- [recovered 2026-07-03] EXP-20260702-06 — W3
- [watch] OBS-20260702-07 — W4
- EXP-20260702-08 — W5
- [open extra] EXP-20260702-09 — W6
- [documentation](EXP-not-an-id) — ordinary link
~~~markdown
- [open] EXP-9999-01 — fenced
~~~
> - [open] OBS-9999-02 — quoted
<!-- - [open] EXP-9999-03 — commented -->
"""
    result = parse_text(fixture)
    checks = {
        "valid items": len(result.items) == 7,
        "warning codes": {w.code for w in result.warnings} == {"W1", "W2", "W3", "W4", "W5", "W6"},
        "warning count": len(result.warnings) == 6,
        "due threshold and excess": len(due(result)) == 2,
        "all five states": {i.status for i in result.items} == STATUSES,
        "exclusions": not any(i.item_id.startswith(("EXP-9999", "OBS-9999")) for i in result.items),
        "origin override": next(i for i in result.items if i.item_id == "OBS-202606-02").origin == "native",
        "native and migrated": result.items[0].origin == "migrated",
        "source": result.items[0].sources == ["ECO-1"],
        "evidence": result.items[0].evidence == ["legacy observation"],
        "marker": result.boundary_kind == "marker" and len(result.audited) == 1 and not result.unaudited,
    }
    failures = [label for label, passed in checks.items() if not passed]
    print("selftest: PASS" if not failures else "selftest: FAIL")
    for failure in failures:
        print(f"- {failure}")
    return not failures


def parse_cli(argv: list[str]) -> tuple[str, Optional[str], bool]:
    if argv and argv[0] == "show":
        if len(argv) < 2 or argv[1].startswith("--"):
            return "show-usage", None, False
        if len(argv) > 3 or (len(argv) == 3 and argv[2].startswith("--")):
            return "usage", None, False
        return "show", argv[2] if len(argv) == 3 else None, False
    if "--selftest" in argv:
        return ("selftest", None, False) if argv == ["--selftest"] else ("usage", None, False)
    path, full = None, False
    for argument in argv:
        if argument == "--full" and not full:
            full = True
        elif argument.startswith("--"):
            return "usage", None, False
        elif path is None:
            path = argument
        else:
            return "usage", None, False
    return "report", path, full


def read_input(path_text: Optional[str]) -> Optional[str]:
    path = (
        Path(path_text)
        if path_text is not None
        else Path(__file__).resolve().parent.parent / "improvements.md"
    )
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: input file not found: {path}")
    except (OSError, UnicodeError) as error:
        print(f"error: cannot read input file {path}: {error}")
    return None


def main(argv: Optional[list[str]] = None) -> int:
    configure_stdout()
    args = sys.argv[1:] if argv is None else argv
    mode, path_text, full = parse_cli(args)
    if mode == "selftest":
        return 0 if run_selftest() else 1
    if mode == "show-usage":
        print(SHOW_USAGE)
        return 0
    if mode == "usage":
        print(USAGE)
        return 0
    started = time.perf_counter()
    text = read_input(path_text)
    if text is None:
        return 0
    result = parse_text(text)
    elapsed = int((time.perf_counter() - started) * 1000)
    print(render_show(result, args[1]) if mode == "show" else render_report(result, full, elapsed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())