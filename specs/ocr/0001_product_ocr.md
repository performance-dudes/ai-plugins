# Spec: the `ocr` plugin

**Theme:** Package the quality-first, on-device OCR + auto-classification flow as a
reusable, **generic** Claude Code plugin, so anyone on the team can digitize and
sort scanned documents — scan images stay on-device, only OCR text reaches the
cloud, all domain knowledge is user-supplied, and nothing is moved without review.

Hierarchy: **theme → user story (US) → acceptance criteria (AC) + test reference.**
Built following the PD plugin house style established by the `example` plugin.

---

## US-OCR-1 — Scans to a reviewable proposal
> As a **team member**, I want to point the plugin at a folder of scans and get a
> rename/sort proposal per document, so that I can file them without wiring the
> pipeline myself.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-OCR-1-1 | `/ocr <folder>` and the `document-ocr` skill both invoke the single bundled `workflows/ocr.js` by `scriptPath`. | review + `tests/validate.sh` (files present) |
| AC-OCR-1-2 | The workflow OCRs on-device (auge), classifies each document with Opus **in parallel**, and writes `_vorschlag.json` + `_vorschlag.md`. | review (workflow structure) |
| AC-OCR-1-3 | The workflow never moves files. | review (no apply call in ocr.js) |

## US-OCR-2 — Generic: no personal data shipped
> As a **maintainer**, I want the plugin to contain no names, taxonomy or personal
> data, so it is safe to publish and works for anyone.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-OCR-2-1 | No person names / personal taxonomy in prompts or scripts; classification uses only a user-provided CONTEXT block. | review (grep for names) |
| AC-OCR-2-2 | The command and skill ask the user for who-is-who, document types, taxonomy, naming convention and languages. | review (`commands/ocr.md`, `SKILL.md`) |
| AC-OCR-2-3 | The classification prompt lives once in `scripts/classify_prompt.md`, shared by the workflow and `klassifiziere.py`. | review |

## US-OCR-3 — Safety: never move without review
> As a **document owner**, I want nothing moved blindly, so official documents stay safe.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-OCR-3-1 | `anwenden.py` is dry-run by default and writes an undo log on `--apply`. | `tests/validate.sh` (dry-run moves nothing) |
| AC-OCR-3-2 | `ist_muell` items are set aside (`--muell-ordner`), never deleted. | review |
| AC-OCR-3-3 | `/ocr-apply` and `/ocr-searchable` run dry-run first and ask before `--apply`. | review (command guardrails) |

## US-OCR-4 — Searchable PDFs (embedding)
> As a **user**, I want scanned PDFs made searchable, so my archive is findable.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-OCR-4-1 | Image-only PDFs (detected via PyMuPDF) get an embedded auge text layer on move and via standalone `durchsuchbar.py`; already-searchable PDFs are left untouched unless `--redo` (AC-OCR-4-5) is given. Embedding is on-device (auge + PyMuPDF, shared `scripts/searchbar.py`) — no ocrmypdf / tesseract / poppler. | review (`searchbar.py`, `anwenden.py`, `durchsuchbar.py`) |
| AC-OCR-4-2 | Embedding applies to documents/PDFs; plain photo images are moved as-is. | review |
| AC-OCR-4-3 | Photo-vs-document by a text threshold (MIN_DOC_CHARS): document scans become searchable PDFs, photo scans/keepsakes (little/no recognized text) stay as images. `--skip-fotos` processes documents only; `--copy` keeps originals. | `tests/validate.sh` (threshold unit test) |
| AC-OCR-4-4 | The text layer round-trips every script auge returns — Latin incl. Umlauts/ß/„, Cyrillic, Greek: an embedded Unicode font (macOS `Helvetica.ttc`, override `OCR_FONT_FILE`), subset on save. Base-14 `helv` (Cyrillic → `·`) is only a fallback and never used by `--redo`. | `tests/validate.sh` §9 |
| AC-OCR-4-5 | `durchsuchbar.py --redo` replaces a text layer that is **entirely invisible** (render mode 3): the old layer is removed by text-only redaction (rotation-aware), links are restored, a fresh auge layer is embedded. Nothing is written if the PDF is signed, a page that had text gets no new lines, or any image's decoded pixel data differs in the saved file. Visible document text is never touched. | `tests/validate.sh` §10 (auge mocked) |

## US-OCR-5 — Every file valid, the safety path provably tested
> As a **developer**, I want every file validated and the dry-run proven to move nothing.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-OCR-5-1 | `plugin.json` valid JSON; `workflows/ocr.js` parses as the Workflow runtime runs it (async-function body); every script compiles. | `tests/validate.sh` |
| AC-OCR-5-2 | `ocr.py` groups scanner pages by prefix; `anwenden.py` dry-run plans a move and changes nothing on disk. | `tests/validate.sh` (unit tests) |
