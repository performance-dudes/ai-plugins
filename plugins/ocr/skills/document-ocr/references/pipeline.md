# Pipeline reference — phases & script interfaces

Four phases. Phases 1–2 are on-device; phase 3 (classification) is the only cloud
step and sends only the OCR **text** to Opus; phase 4 (apply) is local and
human-gated.

```
auge ──▶ session group ──▶ claude -p opus ──▶ review ──▶ anwenden
Vision   (timestamp)       + user CONTEXT     _vorschlag   rename + move + PDF layer
└──── on-device ─────┘     └─ cloud (text) ─┘ └── human ──┘ └──── local, dry-run ────┘
```

Scripts live in `${CLAUDE_PLUGIN_ROOT}/scripts/`; run Python with `uv run`.

## Phase 1–2 — `ocr.py`

```bash
OCR_LANGS="de-DE,en-US" uv run ocr.py "<scan-dir>" "<out-dir>"
```

Runs `auge` (Apple Vision) per image/PDF — it **auto-rotates** scans and returns
"no text detected" for pure photos. Scanner files `YYYYMMDDHHMMSS_NNN.ext` with
the same 14-digit prefix are grouped as one multi-page document → one
`<session>.txt`. Languages via the `OCR_LANGS` env var.

## Phase 3 — `klassifiziere.py`

```bash
uv run klassifiziere.py "<out-dir>" --context-file "<ctx.txt>" [--model opus] [--limit N]
```

Sends each `<session>.txt` with your CONTEXT block and the generic prompt
(`scripts/classify_prompt.md`) through `claude -p` and writes:
- `_vorschlag.json` — machine-readable, input for `anwenden.py`
- `_vorschlag.md` — human review table

Fields per document: `dokumenttyp`, `person`, `datum`, `sprechender_name`,
`zielordner`, `konfidenz`, `ist_muell`, `begruendung`. The CONTEXT is the quality
lever — see `context-and-taxonomy.md`. `--limit N` is a cheap test run.

## Phase 4 — `anwenden.py` (human-gated, dry-run default)

```bash
uv run anwenden.py "<out-dir>" --src "<scan-dir>" --ziel-root "<documents-root>"          # dry-run
uv run anwenden.py "<out-dir>" --src "<scan-dir>" --ziel-root "<documents-root>" --apply
```

Renames/moves the original scans into `<ziel-root>/<zielordner>/<sprechender_name>`.
Dry-run by default; `--apply` writes an undo log (`_undo.json`). **Document** image
scans (recognized text ≥ MIN_DOC_CHARS) are combined into one **searchable PDF**
(proportions 1:1, invisible auge text layer); **photo** scans / keepsakes (little
or no text) **stay as images**. A single image-only PDF gets an auge text layer on
move; PDFs that already have text stay unchanged. Flags: `--copy` (keep originals),
`--skip-fotos` (documents only). OCR languages via `OCR_LANGS`.

## Searchable PDFs — `durchsuchbar.py` (standalone)

```bash
uv run durchsuchbar.py "<file.pdf | folder>" [--rekursiv]          # dry-run
uv run durchsuchbar.py "<folder>" --rekursiv --apply
```

Embeds an invisible auge text layer into image-only PDFs (detected via PyMuPDF),
leaving already-searchable PDFs untouched. PDFs only. The embedding lives in the
shared `scripts/searchbar.py` module (auge + PyMuPDF, fully on-device — no
ocrmypdf / tesseract / poppler).

> ⛔ **Even in this Bash fallback: never reach for `ocrmypdf`/`tesseract`.** Always
> use `durchsuchbar.py` (auge). **Never `ocrmypdf --force-ocr`** — it rasterizes the
> page (lossy, bloats PDFs ~6×, ID scans degraded for zero text gain). auge adds the
> layer *over* the image, non-lossily.
>
> 🚫 **Vector PDFs** (0 images + 0 fonts, e.g. `Print To PDF` forms): never
> `--force-ocr` (rasterizes the vector away). `add_textlayer` is safe — it renders a
> *temporary* image only for auge, then lays the invisible text over the untouched
> vector page → stays vector (lossless) **and** searchable.
>
> ⚠️ **Junk text layer:** a PDF with any minimal/junk text fragment is detected as
> "has text" and **skipped**. To make it searchable, first strip the junk layer
> (extract the page image via PyMuPDF → `searchbar.build_pdf`), then auge.

## The Workflow

`workflows/ocr.js` wires phases 1–3 (OCR → parallel Opus classification →
proposal). It never moves files — apply (phase 4) is always a separate command.
