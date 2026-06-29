---
description: Apply a reviewed OCR proposal — rename/move scans into the taxonomy (dry-run by default, undo log)
argument-hint: "[ocr-dir] --src <scan-dir> --ziel-root <documents-root>"
---

# /ocr-apply — apply the reviewed proposal (dry-run first)

Carry out a **reviewed** `_vorschlag.json`: rename and move the original scans
into the target taxonomy. This step changes the filesystem — treat it carefully.

## Guardrails (do not skip)

- **Dry-run is the default.** Run it once WITHOUT `--apply` and show the user the
  full plan. Only add `--apply` after they confirm.
- **Review first.** The `_vorschlag.json` must have been reviewed (and corrected
  if needed) by a human. If you are not sure it was, ask before applying.
- **Undo log.** A real run writes `_undo.json` next to the proposal.
- **Documents vs photos.** Image scans with enough recognized text (≥ MIN_DOC_CHARS)
  are combined into one searchable PDF (proportions 1:1, invisible auge text layer);
  **photo scans / keepsakes with little or no text stay as images** (no PDF). A
  single image-only PDF gets an auge text layer on move; PDFs that already have text
  stay unchanged. All on-device (auge + PyMuPDF), no extra tools.
- **Flags.** `--copy` keeps the originals (copy instead of move) — good for a
  staging/review pass. `--skip-fotos` processes documents only and leaves photo
  sessions where they are.

## Run

Dry-run (always first):

!`uv run ${CLAUDE_PLUGIN_ROOT}/scripts/anwenden.py "$1" --src "<scan-dir>" --ziel-root "<documents-root>"`

Show the planned moves (each line says whether it becomes a searchable PDF or stays
an image). After the user confirms, run for real (add `--copy` to keep originals,
`--skip-fotos` to process documents only):

```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/anwenden.py "$1" \
  --src "<scan-dir>" --ziel-root "<documents-root>" --apply [--copy] [--skip-fotos]
```

Report what moved and where the undo log is. To make existing PDFs searchable
separately, use `/ocr-searchable`. Set OCR languages via `OCR_LANGS` (e.g.
`OCR_LANGS=de-DE,en-US`).
