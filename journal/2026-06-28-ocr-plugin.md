# 2026-06-28 — ocr plugin

A reusable, generic packaging of the on-device OCR + auto-classification flow
(previously a local-only personal pipeline) as a public `ai-plugins` plugin,
following the `example` plugin's house style and the sibling `transcribe` plugin.

## What was done

- Vendored the pipeline: `ocr.py` (auge / Apple Vision, session grouping),
  `anwenden.py` (apply + undo + PDF text-layer embedding), `durchsuchbar.py`
  (standalone embedding of a searchable text layer into image-only PDFs). Rewrote
  `klassifiziere.py` to be context-driven, and extracted the classification prompt
  into a shared `scripts/classify_prompt.md`.
- Wrote `workflows/ocr.js`: OCR → parallel Opus classification (one agent per
  document, shared prompt) → assemble the proposal. The command and skill both
  invoke it by `scriptPath`; a Bash fallback exists.
- Commands: `/ocr` (propose), `/ocr-apply` (apply, dry-run + undo), `/ocr-searchable`
  (embed PDF text layers), `/ocr-doctor` (preflight). Full PD structure: specs/,
  docs/, journal/, a per-plugin `tests/validate.sh` with deterministic unit tests.

## Decisions & learnings

- **Generic, no personal data.** The original classifier carried a household
  KONTEXT block (real family names, Cyrillic spellings, a personal taxonomy) and a
  hardcoded person enum. All of it was removed; who-is-who, document types, target
  taxonomy and naming convention now come from a user-supplied CONTEXT block. A
  template ships in `references/context-and-taxonomy.md`.
- **Single source of truth for the prompt.** `scripts/classify_prompt.md` is read
  by both the workflow's parallel agents and the standalone `klassifiziere.py`, so
  there is no drift between the two paths.
- **Apply stays out of the workflow.** Moving files is state-changing, so the
  workflow only proposes; `anwenden.py` is a separate, human-gated command,
  dry-run by default with an undo log. This mirrors the pipeline's own safety model
  and the repo's merge policy.
- **OCR text embedding via auge + PyMuPDF.** Tracking the upstream pipeline, the
  searchable-PDF layer is produced by a single engine — auge places an invisible
  text layer (from its bounding boxes) over the image via PyMuPDF (shared
  `scripts/searchbar.py`). This replaced the earlier ocrmypdf/tesseract/poppler
  path: fully on-device, one engine, and only one `uv`-pulled dependency
  (`pymupdf`) instead of three brew tools. Embedding is PDF-only by nature — a
  plain image has no text layer until it is combined into a PDF (which apply does
  automatically). PyMuPDF is AGPL-3.0 but not bundled (uv fetches it at runtime),
  so the plugin's license is unaffected.
- **Photo-vs-document threshold.** Tracking upstream: `anwenden.py` decides per
  session whether an image scan is a document (recognized text ≥ MIN_DOC_CHARS = 20,
  via `meaningful_chars` over the already-produced OCR .txt — no re-OCR) or a photo
  /keepsake (below threshold). Documents become searchable PDFs; photos stay images.
  Added `--skip-fotos` (documents only) and `--copy` (keep originals for staging).
  `meaningful_chars` matches this plugin's English OCR markers (`--- page`,
  `[auge: no text detected]`), kept in sync with `ocr.py`.
- **Languages genericized.** OCR hints default to `de-DE,en-US` (OCR_LANGS), no
  baked-in locale.
- **Tracking policy.** Per request, the plugin tracks the upstream pipeline's
  architectural changes live; this entry reflects the auge+PyMuPDF state.
