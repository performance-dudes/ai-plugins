# Setup — ocr plugin

One-time setup per machine. Run `/ocr-doctor` any time to check status.

## Requirements

- **Apple Silicon Mac on macOS ≥ 26 (Tahoe)** — `auge` builds on the macOS 26
  Apple Vision baseline (Document Parsing, auto-orientation).
- **auge** (Apple Vision OCR) — `brew tap Arthur-Ficial/tap && brew install auge`
- **uv** — `brew install uv` (runs the Python scripts)
- **claude CLI** — Claude Code, for the classification step
- **node ≥ 20** — `brew install node` (the Workflow tool needs it; without it the
  `/ocr` command falls back to a Bash-driven run)

```bash
brew tap Arthur-Ficial/tap && brew install auge
brew install uv
auge --release    # verify
```

## Searchable PDFs — no extra system tools

The searchable-PDF text layer is produced with **auge + PyMuPDF** (one OCR engine,
fully on-device). PyMuPDF (`pymupdf`) is declared in the scripts' PEP-723 headers
and pulled by `uv` on first use — nothing to `brew install`.

> Note: PyMuPDF is licensed AGPL-3.0. It is not bundled or redistributed by this
> plugin — `uv` fetches it onto your machine at runtime — so the plugin's own
> license is unaffected. Mentioned for AGPL-aware users.

## What goes where

- OCR text and the proposal (`_vorschlag.json` / `_vorschlag.md`) go into the
  output dir you pass (default `<scanDir>_ocr`).
- `anwenden.py` moves the **original** scans into your documents root; a real run
  writes `_undo.json`.
- Nothing is uploaded except the OCR **text** sent to Opus for classification —
  never the scan images.

## On-device vs cloud

OCR (auge / Apple Vision), the searchable-PDF embedding (auge + PyMuPDF), and the
apply step run entirely on the machine. Only the extracted text is sent to Opus to
classify each document.
