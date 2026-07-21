"""
build_notes.py — render the ECO-LINK study notes from HTML to PDF.

Usage (from project root, with the venv active):
    ./venv/Scripts/python.exe docs/build_notes.py

The single source of truth is docs/notes/ECO-LINK_Development_Notes.html.
We append a new section to that HTML after each task, then re-run this script
to regenerate ECO-LINK_Development_Notes.pdf in the project root.

Requires the dev-only package `xhtml2pdf` (see requirements-dev.txt).
"""

from pathlib import Path

from xhtml2pdf import pisa

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "notes" / "ECO-LINK_Development_Notes.html"
OUTPUT = ROOT / "ECO-LINK_Development_Notes.pdf"


def build():
    html = SOURCE.read_text(encoding="utf-8")
    with open(OUTPUT, "wb") as pdf_file:
        result = pisa.CreatePDF(html, dest=pdf_file, encoding="utf-8")
    if result.err:
        raise SystemExit(f"PDF generation failed with {result.err} error(s).")
    print(f"OK -> {OUTPUT}")


if __name__ == "__main__":
    build()
