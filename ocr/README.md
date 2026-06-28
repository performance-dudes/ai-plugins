# ocr — quality-first document OCR & auto-classification

Scans in, an organized archive out: OCR every scan on-device (Apple Vision via
`auge`, which auto-rotates), classify each document into a rename/sort proposal,
review it, then apply the moves — with searchable PDF text layers and an undo log.
The scan **images** never leave the machine; only the extracted **text** goes to
Opus for classification.

```
auge ──▶ session group ──▶ claude -p opus ──▶ review ──▶ anwenden
Vision   (timestamp)       + user CONTEXT     _vorschlag   rename + move + PDF layer
└──── on-device ─────┘     └─ cloud (text) ─┘ └── human ──┘ └──── local, dry-run ────┘
```

## Generic by design

Ships **no** domain knowledge — no names, no taxonomy. Every person/type/folder
decision comes from a **CONTEXT block the user supplies per run** (who-is-who,
document types, target taxonomy, naming convention, languages). The command and
skill ask for it; with no context you still get a proposal, just conservative.

## Use it

```
/ocr-doctor                         # check deps
/ocr path/to/scans                  # OCR + classify -> _vorschlag.md (review it!)
/ocr-apply path/to/scans_ocr --src path/to/scans --ziel-root ~/Documents   # dry-run, then --apply
/ocr-searchable ~/Documents --rekursiv     # embed text layers into image-only PDFs (dry-run, then --apply)
```

or just ask: *"OCR and sort these scans"* — the `document-ocr` skill triggers.

## Safety

Official documents are never moved blindly: the pipeline **proposes**, a human
**reviews**, and only then does `anwenden.py` move anything — **dry-run by
default**, with an undo log. `ist_muell` items are set aside, never deleted.

## Searchable PDFs & photo-vs-document

Document image scans become searchable PDFs with an invisible **auge** text layer
placed over the image (via PyMuPDF — one OCR engine, fully on-device, no ocrmypdf /
tesseract / poppler). **Photo scans / keepsakes** (little or no recognized text,
below a threshold) **stay as images** — they are not forced into PDFs. On apply
(`/ocr-apply`): documents → searchable PDF, image-only PDFs get a text layer, photos
stay images; `--skip-fotos` processes documents only, `--copy` keeps originals.
Standalone, `/ocr-searchable` adds a text layer to existing image-only PDFs. PDFs
that already have text are left untouched.

> ⛔ **Agent guardrail — never call `ocrmypdf` / `tesseract` directly.** Use this
> pipeline (`/ocr-searchable` → `durchsuchbar.py`, auge + PyMuPDF). **Never
> `ocrmypdf --force-ocr`**: it **rasterizes the whole page** (vector/text → image) —
> lossy, and bloats archival PDFs (observed: a tax assessment 1.5 MB → 10 MB / 6.4×;
> ID-card scans re-compressed lossily for *zero* text gain). auge lays the text layer
> *over* the existing image without re-rasterizing — that is the entire point.
>
> 🚫 **Vector PDFs — never rasterize, but you *can* make them searchable.** A PDF with
> **0 images and 0 fonts** is vector (e.g. `Microsoft: Print To PDF` forms / payment
> slips) — crisp, small, resolution-independent. Never `--force-ocr` it (that rasterizes
> the vector away). Instead add an invisible text layer via `/ocr-searchable` →
> `durchsuchbar.py` (`searchbar.add_textlayer`): it renders a *temporary* image only to
> run auge, then places the invisible text over the **untouched vector page** — it stays
> vector (lossless) **and** becomes searchable.
>
> ⚠️ **Known limit — junk text layers.** `pdf_is_image_only` treats a PDF as "has
> text" if **any** (even a tiny/junk) text fragment is present, so such a PDF is
> **skipped** (not made searchable). Some scans (e.g. authority/payment forms) carry
> such a fragment. To force them searchable: strip the junk layer first (extract the
> page image via PyMuPDF → rebuild with `searchbar.build_pdf`), then auge — **not**
> `--force-ocr`.

## Components

| Component | Path | Shows |
|-----------|------|-------|
| Workflow | `workflows/ocr.js` | OCR → parallel Opus classification → proposal |
| Command | `commands/ocr.md` | `/ocr` → gather context, invoke the workflow |
| Command | `commands/ocr-apply.md` | `/ocr-apply` → apply reviewed proposal (dry-run + undo) |
| Command | `commands/ocr-searchable.md` | `/ocr-searchable` → embed PDF text layers |
| Command | `commands/ocr-doctor.md` | `/ocr-doctor` → dependency preflight |
| Skill | `skills/document-ocr/SKILL.md` | autonomous trigger → same workflow |
| Scripts | `scripts/` | `ocr.py`, `klassifiziere.py`, `anwenden.py`, `durchsuchbar.py`, `searchbar.py` (auge+PyMuPDF text layer), `classify_prompt.md` |

## Setup & testing

- Setup: [`docs/SETUP.md`](docs/SETUP.md)
- Smoke test: `bash ocr/tests/validate.sh`
