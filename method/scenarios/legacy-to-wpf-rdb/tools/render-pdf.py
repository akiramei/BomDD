#!/usr/bin/env python3
"""Render the legacy-to-wpf-rdb Markdown runbook to a distribution PDF."""
from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    XPreformatted,
)
from reportlab.platypus.tableofcontents import TableOfContents


SCENARIO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_INPUT = SCENARIO_ROOT / "migration-runbook.md"
DEFAULT_ONBOARDING = SCENARIO_ROOT / "onboarding.md"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "pdf" / "legacy-to-wpf-rdb-migration-runbook.pdf"
FONT_REGULAR = Path("C:/Windows/Fonts/YuGothM.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/YuGothB.ttc")


def register_fonts() -> None:
    if not FONT_REGULAR.is_file() or not FONT_BOLD.is_file():
        raise RuntimeError("Yu Gothic fonts were not found under C:/Windows/Fonts")
    pdfmetrics.registerFont(TTFont("BomDDJP", str(FONT_REGULAR), subfontIndex=0))
    pdfmetrics.registerFont(TTFont("BomDDJP-Bold", str(FONT_BOLD), subfontIndex=0))


class RunbookDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height,
                      id="normal", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        # Draw the footer after all flowables.  Some ReportLab flowables apply a
        # background/clipping region while drawing and can otherwise obscure a
        # footer painted at page start, even though the frame itself does not
        # enter the footer margin.
        self.addPageTemplates(PageTemplate(id="content", frames=[frame], onPageEnd=self._draw_page))

    def _draw_page(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("BomDDJP", 7.5)
        canvas.setFillColor(colors.HexColor("#64748B"))
        if doc.page > 1:
            # A continuation page produced around XPreformatted may obscure
            # left-side footer text in ReportLab.  Keep the footer deliberately
            # minimal and stable: the page number remains visible in every
            # tested continuation pattern, while document identity is carried
            # by the cover and PDF metadata.
            canvas.drawRightString(A4[0] - self.rightMargin, 10 * mm, str(doc.page))
            canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
            canvas.line(self.leftMargin, 14 * mm, A4[0] - self.rightMargin, 14 * mm)
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in {"H1", "H2", "H3", "H4"}:
            level = {"H1": 0, "H2": 0, "H3": 1, "H4": 2}[flowable.style.name]
            text = flowable.getPlainText()
            key = f"heading-{self.seq.nextf('heading')}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level, closed=False)
            if flowable.style.name in {"H1", "H2"}:
                self.notify("TOCEntry", (level, text, self.page, key))


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "Body": ParagraphStyle("Body", parent=base["BodyText"], fontName="BomDDJP",
                               fontSize=9.2, leading=15, textColor=colors.HexColor("#172033"),
                               spaceAfter=4 * mm, wordWrap="CJK"),
        "H1": ParagraphStyle("H1", parent=base["Heading1"], fontName="BomDDJP-Bold",
                             fontSize=20, leading=28, textColor=colors.HexColor("#123B5D"),
                             spaceAfter=8 * mm, wordWrap="CJK"),
        "H2": ParagraphStyle("H2", parent=base["Heading2"], fontName="BomDDJP-Bold",
                             fontSize=15, leading=22, textColor=colors.HexColor("#0F5B78"),
                             spaceBefore=4 * mm, spaceAfter=5 * mm, keepWithNext=True, wordWrap="CJK"),
        "H3": ParagraphStyle("H3", parent=base["Heading3"], fontName="BomDDJP-Bold",
                             fontSize=11.5, leading=17, textColor=colors.HexColor("#176B87"),
                             spaceBefore=3 * mm, spaceAfter=3 * mm, keepWithNext=True, wordWrap="CJK"),
        "H4": ParagraphStyle("H4", parent=base["Heading4"], fontName="BomDDJP-Bold",
                             fontSize=10, leading=15, textColor=colors.HexColor("#315F70"),
                             spaceBefore=2 * mm, spaceAfter=2 * mm, keepWithNext=True, wordWrap="CJK"),
        "Bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontName="BomDDJP",
                                 fontSize=8.8, leading=14, leftIndent=2 * mm, wordWrap="CJK"),
        "Number": ParagraphStyle("Number", parent=base["BodyText"], fontName="BomDDJP",
                                 fontSize=8.8, leading=14, leftIndent=2 * mm, wordWrap="CJK"),
        "Code": ParagraphStyle("Code", parent=base["Code"], fontName="BomDDJP",
                               fontSize=7.7, leading=12, leftIndent=3 * mm, rightIndent=3 * mm,
                               borderPadding=3 * mm, borderColor=colors.HexColor("#CBD5E1"),
                               borderWidth=0.5, backColor=colors.HexColor("#F4F7FA"),
                               textColor=colors.HexColor("#243447")),
        "Quote": ParagraphStyle("Quote", parent=base["BodyText"], fontName="BomDDJP-Bold",
                                fontSize=10, leading=16, leftIndent=7 * mm, rightIndent=7 * mm,
                                borderPadding=3 * mm, borderColor=colors.HexColor("#2D7D9A"),
                                borderWidth=1, backColor=colors.HexColor("#EDF7FA"),
                                textColor=colors.HexColor("#123B5D"), wordWrap="CJK"),
        "Table": ParagraphStyle("Table", parent=base["BodyText"], fontName="BomDDJP",
                                fontSize=7.1, leading=10.5, wordWrap="CJK"),
        "TableHead": ParagraphStyle("TableHead", parent=base["BodyText"], fontName="BomDDJP-Bold",
                                    fontSize=7.2, leading=10.5, textColor=colors.white, wordWrap="CJK"),
        "CoverTitle": ParagraphStyle("CoverTitle", parent=base["Title"], fontName="BomDDJP-Bold",
                                     fontSize=25, leading=35, alignment=TA_LEFT,
                                     textColor=colors.HexColor("#123B5D"), wordWrap="CJK"),
        "CoverSub": ParagraphStyle("CoverSub", parent=base["BodyText"], fontName="BomDDJP",
                                   fontSize=11, leading=18, textColor=colors.HexColor("#476578"),
                                   wordWrap="CJK"),
        "TOCHead": ParagraphStyle("TOCHead", parent=base["Heading1"], fontName="BomDDJP-Bold",
                                  fontSize=18, leading=25, textColor=colors.HexColor("#123B5D")),
        "TOC0": ParagraphStyle("TOC0", fontName="BomDDJP", fontSize=9, leading=14,
                               leftIndent=0, firstLineIndent=0, textColor=colors.HexColor("#123B5D")),
        "TOC1": ParagraphStyle("TOC1", fontName="BomDDJP", fontSize=8, leading=12,
                               leftIndent=7 * mm, firstLineIndent=0, textColor=colors.HexColor("#476578")),
    }


INLINE_CODE = re.compile(r"`([^`]+)`")
STRONG = re.compile(r"\*\*([^*]+)\*\*")


def inline_markup(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = STRONG.sub(r"<b>\1</b>", escaped)
    escaped = INLINE_CODE.sub(r'<font color="#8A3B12">\1</font>', escaped)
    return escaped


def parse_table(lines: list[str], style_map: dict[str, ParagraphStyle], available_width: float) -> Table:
    rows: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in rows[1]):
        rows.pop(1)
    width = max(len(row) for row in rows)
    for row in rows:
        row.extend([""] * (width - len(row)))
    weights = []
    for idx in range(width):
        longest = max(5, min(35, max(len(row[idx]) for row in rows)))
        weights.append(longest)
    total = sum(weights)
    col_widths = [available_width * w / total for w in weights]
    data = []
    for r_idx, row in enumerate(rows):
        cell_style = style_map["TableHead"] if r_idx == 0 else style_map["Table"]
        data.append([Paragraph(inline_markup(cell), cell_style) for cell in row])
    table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B87")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C8D3")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F8FA")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.1 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.1 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.7 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.7 * mm),
    ]))
    return table


def markdown_story(text: str, style_map: dict[str, ParagraphStyle], available_width: float):
    lines = text.splitlines()
    story = []
    i = 0
    first_title_seen = False
    first_h2_seen = False
    in_preamble = False
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if not stripped:
            i += 1
            continue
        if in_preamble:
            if stripped == "---":
                in_preamble = False
            i += 1
            continue
        if stripped.startswith("```"):
            language = stripped[3:].strip()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i].replace("\t", "    "))
                i += 1
            i += 1
            label = f"[{language}]\n" if language else ""
            # XPreformatted draws its border/background as one box.  Letting it
            # start in the last few lines of a frame can paint over the footer
            # even when its text continues on the next page.  The runbook's
            # command examples are deliberately short, so move the complete
            # block to the next page when it does not fit.
            story.append(KeepTogether([
                XPreformatted(html.escape(label + "\n".join(code_lines)), style_map["Code"]),
                Spacer(1, 3 * mm),
            ]))
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2)
            if level == 1 and not first_title_seen:
                first_title_seen = True
                in_preamble = True
                i += 1
                continue
            if level == 2:
                if first_h2_seen:
                    story.append(PageBreak())
                first_h2_seen = True
            story.append(Paragraph(inline_markup(title), style_map[f"H{level}"]))
            i += 1
            continue
        if stripped == "---":
            story.append(Spacer(1, 2 * mm))
            story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#B8C8D3")))
            story.append(Spacer(1, 2 * mm))
            i += 1
            continue
        if stripped.startswith("> "):
            quote = stripped[2:]
            story.append(Paragraph(inline_markup(quote), style_map["Quote"]))
            story.append(Spacer(1, 3 * mm))
            i += 1
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i])
                i += 1
            story.append(KeepTogether([
                parse_table(table_lines, style_map, available_width),
                Spacer(1, 4 * mm),
            ]))
            continue
        if re.match(r"^-\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^-\s+", lines[i].strip()):
                content = re.sub(r"^-\s+", "", lines[i].strip())
                items.append(ListItem(Paragraph(inline_markup(content), style_map["Bullet"]),
                                      leftIndent=4 * mm))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", bulletFontName="BomDDJP",
                                      bulletFontSize=7, leftIndent=6 * mm, bulletOffsetY=1))
            story.append(Spacer(1, 2.5 * mm))
            continue
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                content = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append(ListItem(Paragraph(inline_markup(content), style_map["Number"]),
                                      leftIndent=5 * mm))
                i += 1
            story.append(ListFlowable(items, bulletType="1", start="1", bulletFontName="BomDDJP",
                                      bulletFontSize=7.5, leftIndent=8 * mm, bulletOffsetY=1))
            story.append(Spacer(1, 2.5 * mm))
            continue
        paragraph_lines = [stripped]
        i += 1
        while i < len(lines):
            candidate = lines[i].strip()
            if (not candidate or candidate.startswith(("#", "```", "> ", "|", "- "))
                    or candidate == "---" or re.match(r"^\d+\.\s+", candidate)):
                break
            paragraph_lines.append(candidate)
            i += 1
        story.append(Paragraph(inline_markup(" ".join(paragraph_lines)), style_map["Body"]))
    return story


def build_pdf(input_path: Path, onboarding_path: Path, output_path: Path) -> None:
    register_fonts()
    style_map = styles()
    source_text = input_path.read_text(encoding="utf-8")
    onboarding_text = onboarding_path.read_text(encoding="utf-8")
    version_match = re.search(r"^版:\s*([^\s]+)", source_text, re.MULTILINE)
    if version_match is None:
        raise RuntimeError(f"runbook version line was not found: {input_path}")
    runbook_version = version_match.group(1)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = RunbookDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title="実運用 Java/JavaFX から C#/.NET + WPF への BomDD 標準移行作業手順書",
        author="BomDD",
        subject="legacy-wpf-rdb scenario runbook",
    )
    story = [
        Spacer(1, 28 * mm),
        Paragraph("BomDD SCENARIO RUNBOOK", style_map["CoverSub"]),
        Spacer(1, 8 * mm),
        Paragraph("実運用 Java/JavaFX から<br/>C#/.NET + WPF への<br/>標準移行作業手順書", style_map["CoverTitle"]),
        Spacer(1, 10 * mm),
        HRFlowable(width="42%", thickness=2.2, color=colors.HexColor("#2D7D9A"), hAlign="LEFT"),
        Spacer(1, 10 * mm),
        Paragraph("大規模・複数チーム・既存 RDB 継続利用シナリオ", style_map["CoverSub"]),
        Paragraph("Scenario ID: legacy-wpf-rdb", style_map["CoverSub"]),
        Paragraph(
            f"Version {html.escape(runbook_version)} | PDF generated {date.today().isoformat()}",
            style_map["CoverSub"],
        ),
        Spacer(1, 28 * mm),
        Paragraph("優先順位: 作業者が現在位置を把握し、判断に迷わず手を動かし続けられること。",
                  style_map["Quote"]),
        PageBreak(),
        Paragraph("目次", style_map["TOCHead"]),
        Spacer(1, 4 * mm),
    ]
    toc = TableOfContents()
    toc.levelStyles = [style_map["TOC0"], style_map["TOC1"]]
    story.append(toc)
    story.append(PageBreak())
    story.append(Paragraph("Part 1 初参加者オンボーディング", style_map["H1"]))
    story.extend(markdown_story(onboarding_text, style_map, doc.width))
    story.append(PageBreak())
    # Reset the frame cursor after a preceding list/code flowable.  Without a
    # neutral first flowable ReportLab can retain a transient indentation on
    # this page transition and clip the first characters of the Part 2 title.
    story.append(Spacer(1, 1 * mm))
    story.append(Paragraph("Part 2 標準移行作業手順", style_map["H1"]))
    story.extend(markdown_story(source_text, style_map, doc.width))
    doc.multiBuild(story)
    print(f"[ok] PDF written: {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="render legacy-wpf-rdb runbook PDF")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--onboarding", default=str(DEFAULT_ONBOARDING))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    build_pdf(Path(args.input).resolve(), Path(args.onboarding).resolve(), Path(args.output).resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
