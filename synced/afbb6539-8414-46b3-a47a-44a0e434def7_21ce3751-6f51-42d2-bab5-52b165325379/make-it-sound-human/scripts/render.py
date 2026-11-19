"""Render an HTML page to a branded PDF and save small page previews to look at.

Usage: python render.py <page.html> <output.pdf>
The HTML may reference logo-xray.svg; this script copies the logo next to the page if it is missing.
"""
import shutil
import subprocess
import sys
from pathlib import Path


def ensure(pkg, mod=None):
    try:
        __import__(mod or pkg)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", pkg], check=True)


def main():
    html_path = Path(sys.argv[1]).resolve()
    pdf_path = Path(sys.argv[2]).resolve()
    logo = html_path.parent / "logo-xray.svg"
    if not logo.exists():
        shutil.copy(Path(__file__).resolve().parent.parent / "assets" / "logo-xray.svg", logo)

    ensure("weasyprint")
    import weasyprint
    weasyprint.HTML(str(html_path)).write_pdf(str(pdf_path))

    ensure("pdf2image")
    from pdf2image import convert_from_path
    pages = convert_from_path(str(pdf_path), dpi=70)
    for i, page in enumerate(pages, 1):
        page.save(pdf_path.parent / f"preview-page-{i}.png")
    print(f"{len(pages)} pages. Previews: {pdf_path.parent}/preview-page-N.png")


if __name__ == "__main__":
    main()
