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

Usage:
  uv run durchsuchbar.py <file.pdf | folder> [--apply] [--rekursiv]
  # Default = dry-run (shows only which PDFs are image-only).
"""
from __future__ import annotations

import sys
from pathlib import Path

import searchbar


def main() -> int:
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    rekursiv = "--rekursiv" in sys.argv
    if not pos:
        print(__doc__)
        return 1

    target = Path(pos[0]).expanduser()
    if target.is_dir():
        pdfs = sorted(target.rglob("*.pdf") if rekursiv else target.glob("*.pdf"))
    else:
        pdfs = [target]

    image_pdfs = [p for p in pdfs if searchbar.pdf_is_image_only(p)]
    print(f"{len(pdfs)} PDF(s) checked · {len(image_pdfs)} image-only "
          f"{'-> embed text layer' if apply else '(dry-run)'}")
    ok = 0
    for p in image_pdfs:
        print(f"  {'.' if apply else 'o'} {p}")
        if apply:
            try:
                n = searchbar.add_textlayer(p)
                ok += 1
                print(f"      {n} lines embedded")
            except Exception as e:  # noqa: BLE001
                sys.stderr.write(f"      failed: {e}\n")
    if apply:
        print(f"\n{ok}/{len(image_pdfs)} PDFs made searchable.")
    else:
        print("\n(dry-run — nothing changed. Use --apply to embed.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
