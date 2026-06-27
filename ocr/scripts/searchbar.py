"""
searchbar.py — searchable PDFs with an auge text layer (shared module).

A single OCR engine: auge (Apple Vision). The recognized text is placed as an
invisible text layer exactly over the image (coordinates from auge --with-boxes).
Image -> PDF keeps the image proportions 1:1 (page = image pixels, no format
coercion).

Imported by the ocr / anwenden / durchsuchbar scripts. Needs PyMuPDF (fitz); the
importing scripts declare it as a PEP-723 dependency. fitz is imported lazily so
this module can be imported (for constants / auge_lines / text_line_count) without
PyMuPDF present.

Generic: ships no personal data. Languages default to de-DE,en-US (OCR_LANGS).
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

LANGS = os.environ.get("OCR_LANGS", "de-DE,en-US")
IMG_EXTS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic"}


def auge_lines(img_path: Path | str) -> list[dict]:
    """auge OCR with bounding boxes -> line_details (normalized coordinates 0..1)."""
    r = subprocess.run(
        ["auge", "--ocr", str(img_path), "--langs", LANGS,
         "--with-boxes", "--enhance", "-o", "json", "-q"],
        capture_output=True, text=True, timeout=180,
    )
    try:
        return json.loads(r.stdout)["results"].get("line_details", []) or []
    except Exception:  # noqa: BLE001
        return []


def _place(page, lines: list[dict], w: float, h: float) -> int:
    """Place invisible text (render_mode=3) per the auge boxes onto the page.
    auge-y is bottom-origin (Vision); PyMuPDF-y is top-origin -> convert."""
    n = 0
    for ln in lines:
        t = (ln.get("text") or "").strip()
        if not t:
            continue
        try:
            x = ln["x"] * w
            fs = max(4.0, ln["height"] * h * 0.9)
            y_top = (1.0 - (ln["y"] + ln["height"])) * h
            page.insert_text((x, y_top + fs * 0.85), t,
                             fontsize=fs, render_mode=3, fontname="helv")
            n += 1
        except Exception:  # noqa: BLE001
            continue
    return n


def ocr_pages(images: list[Path]) -> list[tuple[Path, list[dict]]]:
    """auge OCR per image -> [(image_path, line_details)]. OCR once, then decide."""
    return [(Path(img), auge_lines(img)) for img in images]


def text_line_count(pages: list[tuple[Path, list[dict]]]) -> int:
    """Number of recognized text lines across all pages (photo detection: ~0 = not a document)."""
    return sum(len(lines) for _, lines in pages)


def build_pdf(pages: list[tuple[Path, list[dict]]], dest: Path) -> int:
    """Pre-OCR'd pages -> searchable PDF (1:1 proportions, auge text layer).
    Returns the number of embedded text lines."""
    import fitz  # PyMuPDF (lazy)
    doc = fitz.open()
    total = 0
    for img, lines in pages:
        pix = fitz.Pixmap(str(img))
        w, h = pix.width, pix.height            # page = image pixels -> 1:1 proportion
        page = doc.new_page(width=w, height=h)
        page.insert_image(fitz.Rect(0, 0, w, h), filename=str(img))
        total += _place(page, lines, w, h)
    dest.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(dest), deflate=True, garbage=3)
    doc.close()
    return total


def images_to_pdf(images: list[Path], dest: Path) -> int:
    """Convenience: OCR + PDF in one (no photo threshold)."""
    return build_pdf(ocr_pages(images), dest)


def pdf_is_image_only(pdf_path: Path) -> bool:
    """True if no page carries a text layer (pure image data)."""
    import fitz  # PyMuPDF (lazy)
    try:
        doc = fitz.open(str(pdf_path))
    except Exception:  # noqa: BLE001
        return False
    has_text = any((page.get_text() or "").strip() for page in doc)
    doc.close()
    return not has_text


def add_textlayer(pdf_path: Path, dpi: int = 200) -> int:
    """Make an existing image PDF searchable in place: per page, auge OCR + an
    invisible text layer. Leaves geometry/image untouched. Returns line count."""
    import fitz  # PyMuPDF (lazy)
    doc = fitz.open(str(pdf_path))
    total = 0
    with tempfile.TemporaryDirectory() as td:
        for page in doc:
            w, h = page.rect.width, page.rect.height
            png = os.path.join(td, "page.png")
            page.get_pixmap(dpi=dpi).save(png)     # only for OCR; coords are normalized
            total += _place(page, auge_lines(png), w, h)
    tmp = pdf_path.with_suffix(".tmp.pdf")
    doc.save(str(tmp), deflate=True, garbage=3)
    doc.close()
    tmp.replace(pdf_path)
    return total
