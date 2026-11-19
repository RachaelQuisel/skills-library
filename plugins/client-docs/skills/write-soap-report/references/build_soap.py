"""
Build an XRAY-branded SOAP report .docx from a content dict.

Generalizes Rachael's THFH SOAP generators into one reusable, data-driven builder.
Fill the CONTENT dict (or pass your own to build()) and run:

    python3 build_soap.py

Requires: python-docx  (pip install python-docx)

Content-dict schema — see references/soap-format-and-voice.md for the full spec.
Each section renders an H1 (Subjective / Objective / Assessment / Plan) with a blue
accent rule, then its ordered list of blocks. Block types:
    {"body": str}                          body paragraph
    {"bold_body": str}                     bold lead-in paragraph (mini sub-label)
    {"bullet": str, "bold": str?}          bullet; optional bold prefix
    {"numbered": str, "bold": str?}        numbered item; optional bold prefix
    {"h2": str} / {"h3": str}              subheading inside a section
    {"table": {"headers": [...], "rows": [[...], ...]}}   branded table
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
import os

# ── XRAY Brand Tokens ──
GRAY_900 = RGBColor(0x0E, 0x1C, 0x2D)
GRAY_600 = RGBColor(0x68, 0x6F, 0x76)
GRAY_500 = RGBColor(0x86, 0x8B, 0x8E)
BLUE_500 = RGBColor(0x15, 0x66, 0xB9)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)

HEADING_FONT = "Urbanist"
BODY_FONT    = "Figtree"

# Correct tagline — NEVER "That Actually Works".
FOOTER_TEXT  = "XRAY  ·  Workflow Automation That Works"

# XRAY wordmark (PNG, for header). Tries known locations; doc still builds without it.
LOGO_CANDIDATES = [
    os.path.expanduser("~/Claude-Work/CLIENTS/The_HOPE_for_Health_Teri_Hall/Code/xray-wordmark-dark.png"),
    os.path.expanduser("~/Downloads/xray-wordmark-dark.png"),
    os.path.expanduser("~/Claude-Work/CLIENTS/Coding_Clarified_Janine_Mothershed/Project Documentation/xray-wordmark.png"),
]
LOGO_PATH = next((p for p in LOGO_CANDIDATES if os.path.exists(p)), None)
OUT_DIR   = os.path.dirname(os.path.abspath(__file__))


# ── low-level helpers ──
def set_cell_shading(cell, hex_color):
    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'))


def set_char_spacing(run, spacing_pt):
    run._r.get_or_add_rPr().append(
        parse_xml(f'<w:spacing {nsdecls("w")} w:val="{int(spacing_pt * 20)}"/>'))


def _bottom_border(p, sz, color):
    p._p.get_or_add_pPr().append(parse_xml(
        f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="{sz}" w:space="1" w:color="{color}"/></w:pBdr>'))


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.style = doc.styles[f"Heading {level}"]
    run = p.add_run(text)
    run.font.name = HEADING_FONT
    run.font.color.rgb = GRAY_900
    run.font.bold = True
    sizes = {1: (20, -1), 2: (14, -0.5), 3: (12, -0.5)}
    size, spacing = sizes.get(level, (12, -0.5))
    run.font.size = Pt(size)
    set_char_spacing(run, spacing)
    if level == 1:
        rule = doc.add_paragraph()
        rule.paragraph_format.space_before = Pt(2)
        rule.paragraph_format.space_after = Pt(12)
        _bottom_border(rule, 6, "1566B9")
    return p


def add_body(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = BODY_FONT
    run.font.size = Pt(10)
    run.font.color.rgb = GRAY_600
    p.paragraph_format.space_after = Pt(6)
    return p


def add_bold_body(doc, bold_text, normal_text=""):
    p = doc.add_paragraph()
    b = p.add_run(bold_text)
    b.font.name, b.font.size, b.font.color.rgb, b.bold = BODY_FONT, Pt(10), GRAY_900, True
    if normal_text:
        r = p.add_run(normal_text)
        r.font.name, r.font.size, r.font.color.rgb = BODY_FONT, Pt(10), GRAY_600
    p.paragraph_format.space_after = Pt(4)
    return p


def _list_item(doc, style, text, bold_prefix=""):
    p = doc.add_paragraph(style=style)
    if bold_prefix:
        b = p.add_run(bold_prefix)
        b.font.name, b.font.size, b.font.color.rgb, b.bold = BODY_FONT, Pt(10), GRAY_900, True
    run = p.add_run(text)
    run.font.name, run.font.size, run.font.color.rgb = BODY_FONT, Pt(10), GRAY_600
    p.paragraph_format.space_after = Pt(3)
    return p


def add_bullet(doc, text, bold_prefix=""):
    return _list_item(doc, "List Bullet", text, bold_prefix)


def add_numbered(doc, text, bold_prefix=""):
    return _list_item(doc, "List Number", text, bold_prefix)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(header)
        run.font.name, run.font.size, run.font.color.rgb, run.bold = HEADING_FONT, Pt(9), WHITE, True
        set_cell_shading(cell, "0E1C2D")
    for r_idx, row_data in enumerate(rows):
        for c_idx, cell_text in enumerate(row_data):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(cell_text))
            run.font.name, run.font.size, run.font.color.rgb = BODY_FONT, Pt(9), GRAY_600
            if r_idx % 2 == 0:
                set_cell_shading(cell, "F5F0E8")  # warm tint
    tblPr = table._tbl.tblPr
    tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        + "".join(f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="E1DED8"/>'
                  for e in ("top", "left", "bottom", "right", "insideH", "insideV"))
        + '</w:tblBorders>'))
    doc.add_paragraph()
    return table


# ── document scaffold ──
def setup_doc():
    doc = Document()
    for section in doc.sections:
        section.top_margin = section.bottom_margin = Cm(2.5)
        section.left_margin = section.right_margin = Cm(2.5)
    normal = doc.styles["Normal"].font
    normal.name, normal.size, normal.color.rgb = BODY_FONT, Pt(10), GRAY_600
    for level, size in ((1, 20), (2, 14), (3, 12)):
        f = doc.styles[f"Heading {level}"].font
        f.name, f.color.rgb, f.bold, f.size = HEADING_FONT, GRAY_900, True, Pt(size)
    return doc


def add_logo_header(doc):
    for section in doc.sections:
        header = section.header
        header.is_linked_to_previous = False
        p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        if LOGO_PATH:
            p.add_run().add_picture(LOGO_PATH, width=Inches(1.5))
        p.paragraph_format.space_after = Pt(8)


def add_branded_footer(doc):
    for section in doc.sections:
        footer = section.footer
        footer.is_linked_to_previous = False
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p._p.get_or_add_pPr().append(parse_xml(
            f'<w:pBdr {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="4" w:color="E1DED8"/></w:pBdr>'))
        run = p.add_run(FOOTER_TEXT)
        run.font.name, run.font.size, run.font.color.rgb = BODY_FONT, Pt(8), GRAY_500
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_title_block(doc, content):
    title = doc.add_paragraph()
    r = title.add_run("SOAP Report")
    r.font.name, r.font.size, r.font.color.rgb, r.bold = HEADING_FONT, Pt(28), GRAY_900, True
    set_char_spacing(r, -1.5)

    if content.get("client"):
        sub = doc.add_paragraph()
        r = sub.add_run(content["client"])
        r.font.name, r.font.size, r.font.color.rgb = HEADING_FONT, Pt(16), GRAY_600
        set_char_spacing(r, -0.5)

    rule = doc.add_paragraph()
    rule.paragraph_format.space_before = Pt(4)
    rule.paragraph_format.space_after = Pt(12)
    _bottom_border(rule, 8, "1566B9")

    for label, key in (("Date: ", "date"), ("Duration: ", "duration"), ("Consultant: ", "consultant")):
        if not content.get(key):
            continue
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        b = p.add_run(label)
        b.font.name, b.font.size, b.font.color.rgb, b.bold = BODY_FONT, Pt(10), GRAY_900, True
        r = p.add_run(content[key])
        r.font.name, r.font.size, r.font.color.rgb = BODY_FONT, Pt(10), GRAY_600

    # Subject line + description block (every SOAP carries both)
    for label, key in (("Subject: ", "subject"), ("Description: ", "description")):
        if not content.get(key):
            continue
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4) if key == "subject" else Pt(0)
        p.paragraph_format.space_after = Pt(2)
        b = p.add_run(label)
        b.font.name, b.font.size, b.font.color.rgb, b.bold = BODY_FONT, Pt(9), GRAY_500, True
        r = p.add_run(content[key])
        r.font.name, r.font.size, r.font.color.rgb = BODY_FONT, Pt(9), GRAY_500


def render_block(doc, block):
    if "h2" in block:
        add_heading(doc, block["h2"], level=2)
    elif "h3" in block:
        add_heading(doc, block["h3"], level=3)
    elif "body" in block:
        add_body(doc, block["body"])
    elif "bold_body" in block:
        add_bold_body(doc, block["bold_body"])
    elif "bullet" in block:
        add_bullet(doc, block["bullet"], block.get("bold", ""))
    elif "numbered" in block:
        add_numbered(doc, block["numbered"], block.get("bold", ""))
    elif "table" in block:
        add_table(doc, block["table"]["headers"], block["table"]["rows"])
    else:
        raise ValueError(f"Unknown block type: {block}")


def build(content, out_path=None):
    doc = setup_doc()
    add_logo_header(doc)
    add_branded_footer(doc)
    add_title_block(doc, content)
    for section in content["sections"]:
        add_heading(doc, section["heading"], level=1)
        for block in section["blocks"]:
            render_block(doc, block)
    # Word-native metadata: Subject + Description (Comments)
    cp = doc.core_properties
    if content.get("subject"):
        cp.subject = content["subject"]
    if content.get("description"):
        # Word's core "description" (comments) property caps at 255 chars
        desc = content["description"]
        cp.comments = desc if len(desc) <= 255 else desc[:252].rstrip() + "..."
    cp.title = f"SOAP Report — {content.get('client', '')} — {content.get('date', '')}".strip(" —")
    cp.author = content.get("consultant", "Rachael Quisel, XRAY")
    if out_path is None:
        out_path = os.path.join(OUT_DIR, "SOAP-Report.docx")
    doc.save(out_path)
    print(f"Saved: {out_path}")
    if not LOGO_PATH:
        print("Note: XRAY wordmark PNG not found — header rendered without logo.")
    return out_path


# ── Example content (replace with the drafted session) ──
CONTENT = {
    "client": "Example Client (Contact Name)",
    "date": "Month D, YYYY",
    "duration": "X hours",
    "consultant": "Rachael Quisel, XRAY",
    "subject": "Contact Name | Rachael Quisel | Company Name | Month D, YYYY | Project",
    "description": "One or two sentences on what the session covered (keep under 255 chars).",
    "sections": [
        {"heading": "Subjective", "blocks": [
            {"body": "One-to-two sentence framing of the client's presenting problem, in plain language."},
        ]},
        {"heading": "Objective", "blocks": [
            {"h2": "1. First work item or topic"},
            {"body": "What was done or discussed, with specifics."},
            {"bullet": "concrete detail", "bold": "Bold subject "},
            {"h2": "Deliverables Produced"},
            {"table": {"headers": ["File", "Location"],
                       "rows": [["Deliverable.docx", "~/Claude-Work/CLIENTS/.../soap-reports/"]]}},
        ]},
        {"heading": "Assessment", "blocks": [
            {"body": "What it means and why it matters."},
            {"numbered": "— the insight.", "bold": "Value-add "},
        ]},
        {"heading": "Plan", "blocks": [
            {"h2": "Immediate Next Steps"},
            {"numbered": "— near-term action.", "bold": "Action "},
            {"h2": "Upcoming Build Items (prioritized)"},
            {"numbered": "— with brief rationale.", "bold": "Build item "},
        ]},
    ],
}


if __name__ == "__main__":
    build(CONTENT)
