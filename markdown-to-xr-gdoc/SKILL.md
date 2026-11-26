---
name: markdown-to-xr-gdoc
version: 1.4.8
description: Converts Markdown files into branded HTML documents for XRay.Tech and sends them to a Google Doc conversion endpoint. Use this skill when the user wants to transform a project document (e.g., vision and scope, project plan) into a professional, branded HTML format aligned with XRay.Tech's 2026 design system. It handles Markdown-to-HTML conversion, rendering Mermaid diagrams with local branding, Base64 image embedding, and automated delivery to a Pipedream-hosted conversion service.
---

# XR Markdown to Google Doc Skill

## Purpose in plain English

This skill helps you turn a Markdown document into a branded Google document through the configured conversion service.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


This skill transforms Markdown documentation into high-quality, branded HTML files following XRay.Tech's design language, including branded Mermaid diagrams.

## Prerequisites

This skill requires:
1.  **Python 3** and libraries (we **strongly recommend** using a virtual environment).
2.  **Mermaid CLI (`mmdc`)** for rendering diagrams locally with XRay styling.

### Dependencies

- `markdown`: For converting Markdown to HTML structure.
- `requests`: For sending the final payload to the conversion endpoint.
- `mermaid-cli`: For local rendering of Mermaid blocks to branded SVGs.

### Recommended Setup

```bash
# 1. Setup Python Environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r markdown-to-xr-gdoc/scripts/requirements.txt

# 3. Setup Mermaid CLI (requires Node.js)
npm install -g @mermaid-js/mermaid-cli
```

## Workflow

1.  **Prepare Markdown:** Ensure your Markdown file is ready. The first `# Heading` will be used as the document title.
2.  **Branding Reference:** Reference [branding.md](references/branding.md) for color palettes and typography if manual adjustments are needed.
3.  **Conversion & Upload:** Use the provided script to convert the file and send it to the endpoint.

> [!TIP]
> **Best Display:** Once the Google Doc is generated, switch it to **Pageless** mode (**File > Page setup > Pageless**) for the best visual experience, especially for documents with wide Mermaid diagrams.

### Running the Conversion

To convert a file and send it to XRay.Tech's GDoc conversion service:

```bash
# From the project root
python3 .gemini/skills/xr-md-to-gdoc/scripts/convert_to_gdoc.py <path-to-markdown-file> .gemini/skills/xr-md-to-gdoc/assets/template.html
```

## Technical Details

- **Template:** Uses [template.html](assets/template.html) with XRay.Tech's 2026 styles.
- **Image Handling:** Automatically embeds local images referenced in Markdown as Base64 data URIs.
- **Endpoint:** `https://eo3nite61ktdbkn.m.pipedream.net` (POST).
- **Payload Format:**
    - `documentString`: Full HTML content.
    - `documentName`: Title of the document.
- **Response:** Returns a JSON object with the `gdocURL`.

## Branding Details

| Role | Value |
| :--- | :--- |
| **Page BG** | `floralwhite` |
| **Headings** | `#0e1c2d` (Gray 900) |
| **Body Text** | `#686f76` (Gray 600) |
| **Primary CTA** | `#1566b9` (Blue 500) |
| **Fonts** | `new-order` / `Urbanist` (Headers), `mundial` / `Figtree` (Body) |
