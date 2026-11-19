---
name: pdf-builder
description: >
  Build production-quality multi-page PDF documents using ReportLab and pypdf.
  Use this skill whenever the user asks to create, design, or generate a PDF —
  especially business documents like agreements, contracts, invoices, forms,
  reports, or templates. Trigger on: "create a PDF", "make a PDF", "build a
  PDF template", "generate a PDF form", "design a document", "make this into a
  PDF", or any request where the output is a polished .pdf file. Also trigger
  when converting an existing document (Word, image, sketch) into a designed PDF.
  This skill encodes hard-won lessons about spacing, overlap prevention,
  typography hierarchy, color systems, and verification — always use it rather
  than winging a ReportLab build from scratch.
---

# PDF Builder Skill

Production-quality PDFs with ReportLab. This skill encodes the design system,
spacing rules, and verification discipline that prevent the most common PDF
generation mistakes.

---

## 0. Before Writing Any Code

1. **Read the full brief.** Identify: page count, sections, field types, tables,
   signatures, branding assets.
2. **Run the height model** (see §3) for every page before writing build functions.
   If a page overflows on paper, it will overflow in code.
3. **Decide on a clean rewrite vs. patch.** If the user asks for a holistic
   redesign (color, spacing, typography), start fresh. Patching accumulated
   constants causes invisible conflicts.

---

## 1. Design System

Encode ALL design tokens as named constants at the top of the script.
Never hardcode a number twice.

### 1.1 Typography — 5-level hierarchy

```python
# T1  Page/doc title:     14pt Bold,  accent color
# T2  Section headers:    12pt Bold,  accent color
# T3  Key entity name:    13pt Bold,  DARK  (e.g. company name)
# T4  Body / address:     10pt Reg,   MED
# T5  Field labels:        9pt Reg,   MID   (readable but subordinate)
# T6  Legal / italic:      9pt Italic, DARK
# T7  Table col headers:   8pt Bold,  WHITE on accent
# T8  Footer / notes:      8pt Reg,   MGRAY
```

Rule: **each level must be visually distinct from its neighbors.** If T4 and
T5 look the same, bump the size delta.

### 1.2 Color palette

```python
DARK    = colors.HexColor('#111111')   # primary text — headings, body
MED     = colors.HexColor('#333333')   # secondary text (addresses, sub-body)
MID     = colors.HexColor('#555555')   # field labels — readable, subordinate
MGRAY   = colors.HexColor('#888888')   # footnotes, row numbers, footer
BLUE    = colors.HexColor('#1a5276')   # section headers, rules, table headers
BLUE_LT = colors.HexColor('#EDF4FB')   # panel tint (publisher block, etc.)
FWHITE  = colors.HexColor('#F9F9F9')   # input box fill (near-white)
LGRAY   = colors.HexColor('#F3F3F3')   # alternating table row tint
BORDER  = colors.HexColor('#C8C8C8')   # box strokes, rule lines
WHITE   = colors.white
BLACK   = colors.black
```

Adapt accent color to brand, keep the rest of the scale intact.

### 1.3 Spacing — 8pt grid

```python
ML = MR = 36       # left / right margin
MB      = 36       # bottom margin
UW      = W - ML - MR   # usable width (letter = 540pt)

GAP_SM  = 8        # label-to-box gap
GAP_MD  = 18       # between stacked fields in a column
GAP_LG  = 30       # between major sections
BOX_H   = 28       # input box height (generous for handwriting)
LBL_SZ  = 9        # field label font size

FIELD_UNIT = GAP_SM + BOX_H + GAP_MD   # 54pt per stacked field row

HDR_H   = 22       # table column header height
ROW_H   = 24       # table data row height

GUTTER  = 24       # gap between 2-col layout columns
COL_W   = (UW - GUTTER) / 2   # 258pt for letter-size with ML=MR=36
```

**8pt grid rule:** all vertical gaps should be multiples of 8 (8, 16, 24, 30, 36…).
Eyeballed values like 13, 17, 22 cause subtle misalignment.

---

## 2. Core Primitive Functions

Always build these primitives first. They encode the spacing rules so page
layout code stays clean and readable.

### 2.1 `draw_field(c, x, y, w, label) → bottom_y`

```python
def draw_field(c, x, y, w, label):
    """Label immediately above its input box.
    y = label baseline. Returns bottom of box (not including GAP_MD)."""
    c.setFillColor(MID)
    c.setFont("Helvetica", LBL_SZ)
    c.drawString(x, y, label)
    by = y - GAP_SM - BOX_H
    c.setFillColor(FWHITE)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.rect(x, by, w, BOX_H, fill=1, stroke=1)
    return by   # caller subtracts GAP_MD before next label
```

**Critical:** the caller is responsible for subtracting GAP_MD after calling
`draw_field`. This keeps the gap accounting explicit and auditable.

### 2.2 `two_col(c, y, left_lbls, right_lbls) → bottom_y`

```python
def two_col(c, y, left_lbls, right_lbls):
    """Perfectly symmetric 2-column stacked fields.
    Both columns start at the same y. Returns y at bottom of taller column."""
    lx = ML
    rx = ML + COL_W + GUTTER
    ly = ry = y
    for lbl in left_lbls:
        ly = draw_field(c, lx, ly, COL_W, lbl) - GAP_MD
    for lbl in right_lbls:
        ry = draw_field(c, rx, ry, COL_W, lbl) - GAP_MD
    return min(ly, ry)
```

**Symmetry rule:** both columns must use the same `COL_W`. Never use different
widths for left vs. right unless deliberately asymmetric (e.g., 60/40 split).

### 2.3 `sec_head(c, label, y, size=12) → content_y`

```python
def sec_head(c, label, y, size=12):
    """Bold accent heading + full-width rule.
    Returns y ready for first content item (below rule + breathing room)."""
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", size)
    c.drawString(ML, y, label)
    c.setStrokeColor(BLUE)
    c.setLineWidth(0.8)
    c.line(ML, y - 4, W - MR, y - 4)
    return y - size - 16   # size + rule gap + breathing room
```

### 2.4 `wrap_text(c, text, x, y, max_w, ...) → bottom_y`

```python
def wrap_text(c, text, x, y, max_w,
              font="Helvetica", size=9, leading=14, color=DARK):
    c.setFillColor(color)
    c.setFont(font, size)
    line = ""
    for word in text.split():
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            if line:
                c.drawString(x, y, line)
                y -= leading
            line = word
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y
```

### 2.5 `pg_footer(c, left, right)`

```python
def pg_footer(c, left, right):
    """Only draws the rule line if there is text to show.
    NEVER call this unconditionally — an empty footer still draws its line."""
    if left or right:
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.4)
        c.line(ML, MB + 10, W - MR, MB + 10)
    c.setFillColor(MGRAY)
    c.setFont("Helvetica", 8)
    if left:
        c.drawString(ML, MB, left)
    if right:
        c.drawRightString(W - MR, MB, right)
```

**Footer trap:** calling `pg_footer(c, "", "")` with a naive implementation
still draws the horizontal rule, creating a mysterious line across the bottom
of every page even when you think you've removed it. Always guard on content.

---

## 3. Page Height Modeling (Do This Before Coding)

For every page, model the vertical space in plain Python BEFORE writing the
build function. This catches overflow before it happens.

```python
# Example model for a form page
H, MB = 792, 36
GAP_LG, GAP_SM, BOX_H, GAP_MD = 30, 8, 28, 18
FIELD_UNIT = GAP_SM + BOX_H + GAP_MD  # 54

y = H - 48                     # start below top margin

# Section header
y -= 12 + 16                   # heading size + breathing room = 28

# Two stacked fields side by side (3 rows)
y -= 3 * FIELD_UNIT            # 162

y -= GAP_LG                    # section gap

# Another section (2 rows)
y -= 12 + 16                   # header
y -= 2 * FIELD_UNIT            # 108
y -= GAP_LG

print(f"y remaining: {y}, margin clearance: {y - MB}pt")
# Must be positive. If < 0, content overflows. If < 20, dangerously tight.
```

**Rule:** margin clearance must be ≥ 20pt. If 10–20pt, acceptable but verify.
If < 10pt, restructure — move a section to the next page.

---

## 4. Table Layout

### 4.1 Column width assertion (non-negotiable)

```python
TABLE_COLS = [
    (ML,       22, "#"),
    (ML + 22, 112, "Product"),
    # ... more columns ...
]
assert sum(w for _, w, _ in TABLE_COLS) == UW, \
    f"Cols sum to {sum(w for _,w,_ in TABLE_COLS)}, need {UW}"
```

**Always assert.** Off-by-one column math silently clips the rightmost column
or leaves a gap at the edge.

### 4.2 Column header text clipping

```python
def col_headers(c, y, cols):
    for x, w, lbl in cols:
        c.setFillColor(BLUE)
        c.rect(x, y - HDR_H, w, HDR_H, fill=1, stroke=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        # Clip label text to fit column — never let it overflow
        txt = lbl
        while txt and c.stringWidth(txt, "Helvetica-Bold", 8) > w - 4:
            txt = txt[:-1]
        c.drawCentredString(x + w / 2, y - HDR_H + 7, txt)
    return y - HDR_H
```

### 4.3 Alternating row tints

```python
def data_row(c, y, cols, n):
    fill = LGRAY if n % 2 == 0 else FWHITE
    for i, (x, w, _) in enumerate(cols):
        c.setFillColor(fill)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.4)
        c.rect(x, y - ROW_H, w, ROW_H, fill=1, stroke=1)
        if i == 0:  # row number in first cell
            c.setFillColor(MGRAY)
            c.setFont("Helvetica", 7.5)
            c.drawCentredString(x + w / 2, y - ROW_H + 8, str(n))
    return y - ROW_H
```

---

## 5. Centering Elements

### Horizontal centering within a column

```python
# Center text within a column of width col_w starting at x
text_w = c.stringWidth(text, font, size)
text_x = x + (col_w - text_w) / 2
c.drawString(text_x, y, text)
```

**Never use `drawCentredString` with left-edge x.** It expects the CENTER
point, not the left edge. Mixing these up shifts text off-center by col_w/2.

---

## 6. Multi-Page Assembly

Each page is a separate function returning a `BytesIO` buffer. Assembly uses
pypdf to merge.

```python
def build_page1():
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=letter)
    # ... draw everything ...
    c.save()
    buf.seek(0)
    return buf

if __name__ == "__main__":
    pages = [build_page1(), build_page2(), build_page3(), build_page4()]
    writer = PdfWriter()
    for buf in pages:
        for page in PdfReader(buf).pages:
            writer.add_page(page)
    with open("output.pdf", "wb") as f:
        writer.write(f)
```

**Why separate functions?** Each page has its own coordinate system. Mixing
pages in one canvas requires `c.showPage()` which resets state unexpectedly.
Separate buffers are explicit and debuggable.

---

## 7. Verification (Required Before Delivering)

Run ALL of these checks after every build. Never skip.

### 7.1 Content verification

```python
import pdfplumber

required = {
    0: ["Expected text on page 1", "Another required string"],
    1: ["Expected text on page 2"],
}
with pdfplumber.open("output.pdf") as pdf:
    for pg_i, items in required.items():
        text = pdf.pages[pg_i].extract_text() or ""
        missing = [i for i in items if i not in text]
        if missing:
            print(f"Page {pg_i+1} MISSING: {missing}")
        else:
            print(f"Page {pg_i+1}: OK")
```

### 7.2 Zero-overlap check

```python
with pdfplumber.open("output.pdf") as pdf:
    for pg_i in range(len(pdf.pages)):
        words = pdf.pages[pg_i].extract_words()
        overlaps = []
        for i, a in enumerate(words):
            for b in words[i+1:]:
                v = a['bottom'] > b['top'] + 2 and b['bottom'] > a['top'] + 2
                h = a['x1'] > b['x0'] + 2 and b['x1'] > a['x0'] + 2
                if v and h:
                    overlaps.append((a['text'], b['text']))
        if overlaps:
            print(f"Page {pg_i+1} OVERLAPS: {overlaps}")
        else:
            print(f"Page {pg_i+1}: zero overlaps ✓")
```

**pdfplumber coordinate system:** y increases DOWNWARD (0 = top of page,
792 = bottom). ReportLab coordinates are OPPOSITE (0 = bottom, 792 = top).
Always convert when reasoning about overlap: `rl_y = H - pdfplumber_top`.

### 7.3 Footer line check

```python
with pdfplumber.open("output.pdf") as pdf:
    for pg_i in range(len(pdf.pages)):
        footer_lines = [l for l in pdf.pages[pg_i].lines if l['top'] > H - MB - 20]
        if footer_lines:
            print(f"Page {pg_i+1} has {len(footer_lines)} footer line(s) — intentional?")
```

### 7.4 Spacing sanity — boxes vs. adjacent elements

When a new section or label immediately follows a box, measure the gap:

```python
# SB box bottom=660, Notes label top=665 → gap = 5pt ✓ (must be > 0)
# SB box bottom=660, Notes label top=659 → gap = -1pt ✗ OVERLAP
```

If gap < 4pt, increase the inter-element spacing constant.

---

## 8. Common Bugs and Fixes

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| Footer rule appears on pages with no footer text | `pg_footer` draws line unconditionally | Guard: `if left or right:` before drawing rule |
| Element overlaps the one below it | Section box bottom ≈ next label top | Add 4–8pt between box bottom and next label baseline |
| "Missing" text despite being in the code | Content cut off by `if y < MB + N: break` threshold too high | Lower threshold to MB+36; verify all expected headings present |
| Table right edge clips or leaves gap | Column widths don't sum to UW | `assert sum(w for _,w,_ in cols) == UW` |
| Company name/text not truly centered | `drawCentredString` called with left-edge x | Use `x + col_w/2` as center point, or calculate `x + (col_w - text_w)/2` |
| Design looks muddy after many iterations | Accumulated constant patches conflict | Ground-up rewrite with clean design system |
| Page overflows (content below footer) | No height model before building | Run §3 height model first; clearance must be ≥ 20pt |
| Address/text bleeds outside column | `wrap_text` max_w not set to column width | Pass `COL_W` (not `UW`) when wrapping inside a column |
| Two-col fields misalign | Right column x calculated wrong | `rx = ML + COL_W + GUTTER` — not `ML + UW/2` |
| Signature line too short for real signature | Line spans column minus small padding | Use full `COL_W` for signature lines |

---

## 9. Design Rules for Business Documents

These apply beyond code — pure design discipline:

1. **Nothing should overlap.** Verify programmatically, not visually.
2. **Every text element has exactly one role.** Label ≠ body ≠ heading.
3. **Symmetric columns use identical widths.** Not "approximately equal."
4. **Company names and headings should be visually dominant.** If the company
   name looks the same weight as address text, it's too small.
5. **Input boxes need breathing room.** BOX_H = 28pt minimum for handwriting.
   Labels sit immediately above their own box (GAP_SM = 8pt), not floating.
6. **Section gaps are larger than field gaps.** GAP_LG > GAP_MD > GAP_SM.
7. **Footer rules only appear when there is footer content.** A line with no
   text is visual noise.
8. **Don't bury white space at the bottom of a page.** If a section fits,
   spread it to use the space. Signatures especially benefit from breathing room.
9. **Centered text uses the center of its container**, not the center of the
   whole page (unless that's the intent).
10. **Color contrast:** body text #111111 on white. Labels #555555. Footnotes
    #888888. Never use colors lighter than #888888 for any readable text.

---

## 10. Quick-Start Template

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas as rl_canvas
from pypdf import PdfWriter, PdfReader
import io

W, H    = letter           # 612 × 792
ML = MR = 36
MB      = 36
UW      = W - ML - MR     # 540

# Colors
DARK    = colors.HexColor('#111111')
MED     = colors.HexColor('#333333')
MID     = colors.HexColor('#555555')
MGRAY   = colors.HexColor('#888888')
BLUE    = colors.HexColor('#1a5276')
BLUE_LT = colors.HexColor('#EDF4FB')
FWHITE  = colors.HexColor('#F9F9F9')
LGRAY   = colors.HexColor('#F3F3F3')
BORDER  = colors.HexColor('#C8C8C8')
WHITE   = colors.white
BLACK   = colors.black

# Spacing
GAP_SM     = 8
GAP_MD     = 18
GAP_LG     = 30
BOX_H      = 28
LBL_SZ     = 9
FIELD_UNIT = GAP_SM + BOX_H + GAP_MD  # 54
HDR_H, ROW_H = 22, 24
GUTTER     = 24
COL_W      = (UW - GUTTER) / 2        # 258

# Install primitives: draw_field, two_col, sec_head, wrap_text, pg_footer
# (copy from §2 above)

def build_page1():
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=letter)
    y = H - 48
    # ... your content here ...
    pg_footer(c, "", "")
    c.save()
    buf.seek(0)
    return buf

if __name__ == "__main__":
    # 1. Run height model (§3) first
    # 2. Build pages
    pages = [build_page1()]
    writer = PdfWriter()
    for buf in pages:
        for page in PdfReader(buf).pages:
            writer.add_page(page)
    out = "/mnt/user-data/outputs/output.pdf"
    with open(out, "wb") as f:
        writer.write(f)
    # 3. Verify (§7)
    print(f"Written: {out}")
```

---

## 11. Install Dependencies

```bash
pip install reportlab pypdf pdfplumber --break-system-packages
```

---

## Reference

- **§3** — height modeling before coding
- **§7** — full verification suite (content + overlaps + footer + spacing)
- **§8** — bug lookup table
- **§9** — design rules
