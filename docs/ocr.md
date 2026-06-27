# ocr — plugin state

Current-state documentation for the `ocr` plugin (intent lives in
`specs/ocr/reference.md`; the running log is in `journal/`).

## What it is

A quality-first OCR + auto-classification plugin for Apple Silicon (macOS 26).
Scan images are processed entirely on-device (Apple Vision via `auge`); only the
extracted text is sent to Opus to classify. All domain knowledge is supplied by
the user per run (the CONTEXT block) — the plugin ships none. Nothing is moved
without human review.

## Architecture (when read / who triggers / where it runs)

| Component | File | Triggered by | Runs |
|-----------|------|--------------|------|
| Workflow | `ocr/workflows/ocr.js` | command or skill, by `scriptPath` | Workflow tool (orchestrates agents) |
| Command `/ocr` | `ocr/commands/ocr.md` | user types it | main session |
| Command `/ocr-apply` | `ocr/commands/ocr-apply.md` | user types it | main session (Bash) |
| Command `/ocr-searchable` | `ocr/commands/ocr-searchable.md` | user types it | main session (Bash) |
| Command `/ocr-doctor` | `ocr/commands/ocr-doctor.md` | user types it | main session (Bash) |
| Skill `document-ocr` | `ocr/skills/document-ocr/SKILL.md` | model, on matching request | main session |
| Pipeline scripts | `ocr/scripts/*` | the workflow / commands, via Bash | on-device |

## Flow

```
/ocr ──┐
       ├─▶ workflows/ocr.js
skill ─┘      ├─ OCR        ocr.py (auge / Apple Vision, auto-rotate, session grouping)  [on-device]
              ├─ Classify   parallel Opus, one per document, shared classify_prompt.md + user CONTEXT
              └─ Proposal   assemble _vorschlag.json + _vorschlag.md   (NO moves)
                 │
   review by human ─▶ /ocr-apply  anwenden.py (dry-run default, --apply, undo log, PDF text layer)
                      /ocr-searchable  durchsuchbar.py (embed text layer into image-only PDFs)
```

## Quality & safety contract

- **On-device for OCR**; cloud only for the extracted text.
- **Propose → review → apply.** Nothing moves without a human; apply is dry-run by
  default with an undo log.
- **Generic.** Person/type/folder come only from the user CONTEXT; the classify
  prompt is shared (`scripts/classify_prompt.md`) by workflow and fallback script.
- **Searchable PDFs & photo-vs-document.** Document scans (recognized text ≥
  MIN_DOC_CHARS) become searchable PDFs with an invisible auge text layer (PyMuPDF,
  on-device); photo scans / keepsakes (little/no text) stay as images. Image-only
  PDFs get a text layer; `--skip-fotos`/`--copy` adjust apply behavior.

## Known limitations

- auge is Apple Silicon + macOS 26 only.
- Classification of very large batches is parallel but still cloud-bound (one Opus
  call per document).

## Tests

`bash ocr/tests/validate.sh` — structure + syntax of every file, plus deterministic
unit tests (ocr.py session grouping; anwenden.py dry-run moves nothing).
