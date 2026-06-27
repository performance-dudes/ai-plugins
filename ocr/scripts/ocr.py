#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
ocr.py — phase 1+2 of the OCR flow: scans -> raw OCR text, one file per document.

  Phase 1 (OCR):      auge (Apple Vision, macOS 26) per image/PDF — auto-rotates.
  Phase 2 (grouping): scanner files YYYYMMDDHHMMSS_NNN.ext belong to ONE
                      multi-page document (same 14-digit prefix) -> one .txt.

Generic: ships no personal data. Languages default to de-DE,en-US and are
overridable via the OCR_LANGS env var (BCP-47, comma-separated).

Usage:
  uv run ocr.py <input-dir-or-file> [output-dir]
  OCR_LANGS="de-DE,en-US,fr-FR" uv run ocr.py "/path/to/scans" out/scans

Output: <output-dir>/<session>.txt  (one file per document, pages with markers)
Raw text stays here; classification is the next step (klassifiziere.py).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

LANGS = os.environ.get("OCR_LANGS", "de-DE,en-US")  # BCP-47 hints; override via OCR_LANGS
AUGE_FLAGS = os.environ.get("AUGE_FLAGS", "--enhance").split()
EXTS = {".jpg", ".jpeg", ".png", ".pdf", ".tiff", ".tif", ".heic"}
SCANNER_RE = re.compile(r"^(\d{14})_\d{3}$")  # YYYYMMDDHHMMSS_NNN


def session_key(path: Path) -> str:
    m = SCANNER_RE.match(path.stem)
    if m:
        return m.group(1)
    return re.sub(r"[ /]", "_", path.stem)


def auge_ocr(path: Path) -> str:
    cmd = ["auge", "--ocr", str(path), "--langs", LANGS, *AUGE_FLAGS, "-o", "plain", "-q"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return "[auge: timeout]"
    out = (r.stdout or "").strip()
    return out if out else "[auge: no text detected]"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    if subprocess.run(["which", "auge"], capture_output=True).returncode != 0:
        print("auge missing: brew tap Arthur-Ficial/tap && brew install auge", file=sys.stderr)
        return 1

    inp = Path(sys.argv[1]).expanduser()
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("dokumente") / inp.name
    out.mkdir(parents=True, exist_ok=True)

    if inp.is_dir():
        files = sorted(p for p in inp.iterdir()
                       if p.is_file() and p.suffix.lower() in EXTS)
    else:
        files = [inp]
    if not files:
        print(f"no OCR-able files in {inp}", file=sys.stderr)
        return 1

    print(f"{len(files)} files -> OCR (auge, langs={LANGS}, flags={' '.join(AUGE_FLAGS)})")

    # group: key -> [pages]; dict preserves insertion order (Py3.7+)
    groups: dict[str, list[Path]] = {}
    for f in files:
        groups.setdefault(session_key(f), []).append(f)

    n = 0
    for key, pages in groups.items():
        txt = out / f"{key}.txt"
        parts = []
        for p in sorted(pages):
            parts.append(f"--- page: {p.name} ---")
            parts.append(auge_ocr(p))
            parts.append("")
            n += 1
            print(f"\r   {n}/{len(files)}  {key}      ", end="", flush=True)
        txt.write_text("\n".join(parts), encoding="utf-8")
    print()

    docs = len(list(out.glob("*.txt")))
    print(f"{docs} document texts in {out}/")
    print(f"   next step: uv run klassifiziere.py {out} --context-file <your-context>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
