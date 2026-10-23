#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf"]
# ///
"""
durchsuchbar.py — embed an auge text layer into image-only PDFs (make searchable).

Image-only PDFs (scanned, no text layer) are made searchable; PDFs that already
carry text are left untouched. One OCR engine: auge (see searchbar.py). PDFs only —
a plain image has no text layer to carry until it is turned into a PDF.

Generic: ships no personal data. Languages follow searchbar (OCR_LANGS env).

--redo also replaces an existing OCR layer: PDFs whose text is entirely
invisible (render mode 3) get that layer removed and a fresh auge layer
embedded — for layers that lost non-Latin script (Cyrillic as "·") or come from
another OCR engine. Visible document text is never touched; a file is left
unwritten if it is signed, a page loses all its text, or image pixel data changes.

Usage:
  uv run durchsuchbar.py <file.pdf | folder> [--apply] [--rekursiv] [--redo]
  # Default = dry-run (shows only which PDFs would be processed).
"""
from __future__ import annotations

import sys
from pathlib import Path

import searchbar


def main() -> int:
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    rekursiv = "--rekursiv" in sys.argv
    redo = "--redo" in sys.argv
    if not pos:
        print(__doc__)
        return 1

    target = Path(pos[0]).expanduser()
    if not target.exists():
        sys.stderr.write(f"not found: {target}\n")
        return 1
    if target.is_dir():
        pdfs = sorted(target.rglob("*.pdf") if rekursiv else target.glob("*.pdf"))
    else:
        pdfs = [target]

    image_pdfs = [p for p in pdfs if searchbar.pdf_is_image_only(p)]
    ocr_pdfs = [p for p in pdfs if redo and p not in image_pdfs
                and searchbar.pdf_has_only_invisible_text(p)]
    print(f"{len(pdfs)} PDF(s) checked · {len(image_pdfs)} image-only"
          + (f" · {len(ocr_pdfs)} with an OCR layer to replace" if redo else "")
          + f" {'-> embed text layer' if apply else '(dry-run)'}")
    ok = 0
    todo = [(p, False) for p in image_pdfs] + [(p, True) for p in ocr_pdfs]
    for p, replace in todo:
        print(f"  {'.' if apply else 'o'} {'[redo] ' if replace else ''}{p}")
        if apply:
            try:
                n = searchbar.add_textlayer(p, replace=replace)
                ok += 1
                print(f"      {n} lines embedded")
            except Exception as e:  # noqa: BLE001
                sys.stderr.write(f"      failed: {e}\n")
    if apply:
        print(f"\n{ok}/{len(todo)} PDFs made searchable.")
        if ok < len(todo):
            return 1
    else:
        print("\n(dry-run — nothing changed. Use --apply to embed.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
