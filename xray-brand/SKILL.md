---
name: xray-brand
version: 1.0.4
description: >-
  Apply XRAY's official 2026 brand identity — colors, typography, logo, and component styles — to any document, presentation, web artifact, or design output. Use this skill any time someone asks to create or style something for XRAY, apply XRAY's brand, generate XRAY-branded materials, or produce documents that should follow XRAY's visual identity. Triggers include: "XRAY branded", "make it look like XRAY", "apply the XRAY brand", "XRAY style", "brand this XRAY document", "XRAY presentation", or any request to produce a deliverable for the company XRAY (Workflow Automation Consultancy). This skill should always be used when producing XRAY-branded outputs, even if the user doesn't explicitly say "brand guidelines."
tags:
  - skill
---

# XRAY Brand Skill

## Purpose in plain English

This skill helps you apply XRAY's colors, fonts, logo, and visual standards to a deliverable.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


## Overview

XRAY is a **Workflow Automation Consultancy** with the tagline _"Workflow Automation That Actually Works."_

**Brand personality:** Professional, clear, modern, warm, approachable. Minimal and purposeful decoration — hand-drawn line art, geometric patterns (dots, arcs, circles), subtle background illustrations. Simplicity over complexity.

## Essential Rules

- **Never** use pure black (`#000`) for text, fills, backgrounds, or borders. Use Gray 900 (`#0e1c2d`). The input border in `references/components.md` is Gray 900 for this reason.
- **Light page background** is `floralwhite` (`#FFFAF0`) across the entire canvas, including margins, gutters, and blank space. Use Gray 900 for intentional dark sections and presentation covers.
- **White text** on Blue 500 buttons, and white dropdown or card surfaces, stays allowed. `references/colors.md` lists White for those roles. That is not a page background.
- **All headings** use negative letter-spacing (tight tracking)
- **Logo** is single-color only, never multicolor or gradient, so it stays readable at small sizes. The light logo fill is `#FFFAF0`, not pure white.

## Reference Files

Load these as needed for detailed specifications:

- **[references/colors.md](references/colors.md)** — Full color palette, brand blues, accents
- **[references/typography.md](references/typography.md)** — Font families, type scale, rules
- **[references/components.md](references/components.md)** — Buttons, cards, spacing system
- **[references/logo-inline.md](references/logo-inline.md)** — Copy-paste SVG code and base64 data URIs for all 6 logo variants (use when embedding logos in HTML, CSS, or PDFs). For email, use the PNG wordmarks in `assets/` instead. Many email clients do not render SVG.

## Logo Assets

All official XRAY logos live in `assets/`. Each variant has a dark version (fill `#0E1C2D`, for light backgrounds) and a light version (fill `#FFFAF0`, for dark backgrounds). Use the SVG files for HTML and PDF, and the PNG wordmarks for email. Never recreate or approximate the logo.

### Wordmark (full "XRAY" text)
The most impactful element of the brand identity. The negative space in the "X" conveys the idea of revealing what is hidden — central to XRAY's positioning. Use for document headers, presentation title slides, email headers, and anywhere the brand needs full identification.

- **[assets/wordmark-dark.svg](assets/wordmark-dark.svg)** — Dark fill (`#0E1C2D`), 323x96 — use on `floralwhite` / light backgrounds
- **[assets/wordmark-light.svg](assets/wordmark-light.svg)** — Light fill (`#FFFAF0`), 323x96 — use on Gray 900 / dark backgrounds
- **[assets/wordmark-dark.png](assets/wordmark-dark.png)** — Same dark wordmark as a PNG (400x119, transparent background). Use this in email on light backgrounds.
- **[assets/wordmark-light.png](assets/wordmark-light.png)** — Light wordmark as a PNG (fill `#FFFAF0`, 400x119, transparent background). Use this in email on Gray 900 headers. There is no pure-white wordmark.

### Primary Symbol (the "XR" mark)
The brand in its most minimal and direct form. Emphasizes clarity and a modern aesthetic. Ideal for formal or wide-format applications (presentation covers, website headers, official documents). Best when the brand needs to appear professional, open, and uncluttered.

- **[assets/symbol-dark.svg](assets/symbol-dark.svg)** — Dark fill (`#0E1C2D`), 226x130 — use on light backgrounds
- **[assets/symbol-light.svg](assets/symbol-light.svg)** — Light fill (`#FFFAF0`), 226x130 — use on dark backgrounds

### Secondary Symbol "The Spotlight" (circle mark)
Represents a spotlight — illuminating what is hidden and revealing what others overlook. The circular "XR" provides a strong, contained mark recognizable across different scales and backgrounds. Use for favicons, social media avatars, app icons, stickers, and any context needing a bold presence in limited space. Preferable in small sizes or social/digital contexts. This is the only logo variant that may appear on colored backgrounds.

- **[assets/circle-dark.svg](assets/circle-dark.svg)** — Dark fill (`#0E1C2D`), 260x260 — use on light backgrounds
- **[assets/circle-light.svg](assets/circle-light.svg)** — Light fill (`#FFFAF0`), 260x260 — use on dark or colored backgrounds

### Which logo to use where

| Context | Logo variant | Version |
|---------|-------------|---------|
| Document header / first page | Wordmark | dark on floralwhite |
| Presentation title slide (Gray 900 bg) | Wordmark | light |
| Presentation content slide footer | Primary Symbol | dark on floralwhite |
| PDF header | Wordmark | dark |
| Email header (Gray 900 bg) | Wordmark | light |
| Favicon / avatar / social profile | The Spotlight | dark or light per bg |
| HTML navbar | Wordmark | dark (max-height: 64px) |
| Slide deck footer (every slide) | Primary Symbol | match background |
| Small/social/digital contexts | The Spotlight | match background |
| Colored backgrounds | The Spotlight only | light variant |

### Clearspace (applies to all logo types)
- Minimum clearspace = **half the height of the "X"** (X/2) on ALL four sides
- This zone must be completely free of text, graphics, images, edges, or other elements
- Never place a logo where it overlaps with existing content
- The clearspace rule applies equally to the Wordmark, Primary Symbol, and The Spotlight

### Minimum sizes
- **Wordmark digital minimum:** 135px x 40px — never render smaller than this
- Scale proportionally — never stretch or compress

### Color usage
- **Wordmark and Primary Symbol:** use on light backgrounds (dark fill) or dark backgrounds (light fill) only
- **The Spotlight:** may also appear on colored backgrounds — use the light variant on colored or dark backgrounds
- Always single-color — the fill is either `#0E1C2D` (dark) or `#FFFAF0` (light), never anything else

### Logo don'ts (from official brand guidelines)
The logo is single-color so it reads at small sizes. Recoloring, stretching, rotating, or inventing a sub-brand makes the mark fail at those sizes:

1. **Do not alter the color or add effects** — no shadows, glows, gradients, or custom colors
2. **Do not alter or distort the wordmark** — no stretching, compressing, or modifying letterforms
3. **Do not change the orientation** — no rotating, flipping, or angling the logo
4. **Do not create variations or sub-brands** — no "TechXRAY", "XRAYLabs", etc.
5. **Do not stack or create other versions** — no rearranging the X symbol above "RAY", etc.
6. **Do not add a background to the symbol** — The Spotlight already has its circle; never add boxes, shapes, or colored backgrounds behind any logo variant

### Logo placement in presentations
- Title slides: bottom-left on dark (Gray 900) background, use light wordmark
- Content slides: bottom-left on floralwhite background, use dark Primary Symbol
- Maintain X/2 clearspace padding from slide edges

### Embedding logos in output
Load **[references/logo-inline.md](references/logo-inline.md)** for copy-paste ready SVG code and base64 data URIs for all 6 variants. That file includes usage examples for:
- **Inline SVG** — paste directly into HTML (best quality, scalable)
- **Base64 data URI** — use in `<img>` tags or CSS `background-image` (not email; email uses the PNG wordmarks)
- **ReportLab PDF** — convert via svglib
Always respect the 135x40px minimum size for the wordmark.

## What "Properly Branded" Means

**Important:** Proper branding is NOT just updating colors. A properly XRAY-branded deliverable must include:

1. **The XRAY logo** — wordmark or round logo, appropriately placed
2. **Correct backgrounds** — floralwhite across the full light page, Gray 900 for dark sections
3. **Brand typography** — Urbanist headings, Figtree body
4. **Full color palette** — not just swapping a few colors

If asked to "brand" or "apply XRAY styling" to something, always add the logo and restructure to match brand guidelines — don't just find/replace colors.

## Minimal Intervention Principle

**Do not over-design or rebuild from scratch.** The logo is single-color so it reads at small sizes, and the rest of a branded file should change only as far as the brand requires.

When branding an existing document:

1. **Assess first** — What already exists? What's the minimum change needed?
2. **Keep existing content** — Don't remove graphics, images, or layouts that work
3. **Add, don't replace** — Add the logo, fix colors, adjust backgrounds — don't redesign
4. **Preserve structure** — If the layout is fine, leave it alone
5. **Ask if unsure** — "Should I keep the existing layout or redesign?"

**Before making changes, ask yourself:**
- Am I changing more than necessary?
- Am I removing content the user created?
- Could I achieve proper branding with fewer changes?
- Is this enhancement or reconstruction?

**The goal is to make existing work look XRAY-branded, not to replace it.**

## Application by Document Type

### PowerPoint / Presentations

**Required elements for proper branding:**
- Title slide: Gray 900 (`#0E1C2D`) background with the light XRAY wordmark (fill `#FFFAF0`, bottom-left). This is not a pure-white (`#ffffff`) wordmark.
- Content slides: `floralwhite` background
- XRAY logo in header or footer on every slide
- Urbanist for headings, Figtree for body text
- Gray 900 headings, Gray 600 body text on light backgrounds

### Word Documents / PDFs
- Use the [King Changelog](examples/king-changelog.pdf) as the default layout model for dated project updates. Use [King Decisions Made](examples/king-decisions.pdf) as the default layout model for decision records. Follow their wordmark placement, heading hierarchy, spacing, and floralwhite page treatment. Write each new document from its own sources and omit the King text and links.
- Keep the King examples within authorized private use. Leave these client documents out of public skill releases and public examples.
- Set every page background to `#FFFAF0` from edge to edge, including margins and blank space. In Word, set the page color and enable background colors when exporting. For PDF renderers that do not preserve page backgrounds, paint a full-page `#FFFAF0` fill behind the content.
- Check the final PDF, including the corners and margins of every page. Correct any white bands before delivering it.
- Headings: Gray 900, Urbanist/new-order, bold, tight tracking
- Body: Gray 600, Figtree/mundial
- Logo: top-left header, full wordmark (dark fill on a light page)
- Starting file: [assets/xray-reference.docx](assets/xray-reference.docx) is a blank one-page Word document with a floralwhite (`#FFFAF0`) page background and standard margins. Use it when creating a new branded `.docx`, then add the dark wordmark in the header.

### HTML / Web Artifacts
- Set `html` and `body` to `background: #FFFAF0` so the viewport and space around the content share the same color.
- For HTML-to-PDF export, set `@page { background: #FFFAF0; }` and enable background printing (`printBackground: true` in Chromium PDF APIs, or **Background graphics** in the print dialog). Use a full-page PDF fill if the renderer leaves margins white.
- Import Google Fonts: Urbanist + Figtree
- Use Blue 500 (`#1566b9`) for CTAs and links

### Email Templates
- Header: Gray 900 background with the light wordmark PNG ([assets/wordmark-light.png](assets/wordmark-light.png), fill `#FFFAF0`). Do not use an SVG, including a base64 SVG. Many email clients will not render it.
- Body: floralwhite background
- CTA buttons: Blue 500, white text, 8px radius
- Footer: Gray 900 background, Gray 300 text
- Light email backgrounds: [assets/wordmark-dark.png](assets/wordmark-dark.png)

## Do's and Don'ts

### Do
- Use floralwhite (`#FFFAF0`) across the full light page, including exported margins
- Apply tight negative letter-spacing to all headings
- Keep logo single-color
- Use Gray 900 for all headings on light backgrounds
- Use Blue 500 as the primary interactive/CTA color

### Don't
- Use pure black `#000` for text, fills, backgrounds, or borders
- Use pure white `#ffffff` as a page background
- Make the logo multicolor or add gradients
- Mix font weights arbitrarily — stick to 400, 600, 700
- Use Red 500 or Yellow 500 as primary colors — they are accents only

## Quick Reference

```
BACKGROUNDS:   #FFFAF0 (full light page)  |  #0e1c2d (dark sections)
HEADINGS:      #0e1c2d
BODY TEXT:     #686f76
MUTED TEXT:    #868b8e
BORDERS:       #e1ded8
PRIMARY CTA:   #1566b9  (hover: #0f4185)
ACCENT RED:    #f55647
ACCENT YELLOW: #f5cf45
```
