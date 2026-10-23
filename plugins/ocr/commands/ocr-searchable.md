---
description: Embed a searchable OCR text layer into image-only PDFs (dry-run by default)
argument-hint: "[file.pdf | folder] (path only — add --redo / --rekursiv to the run line)"
---

# /ocr-searchable — make image-only PDFs searchable

Embed an invisible OCR text layer (from auge) into PDFs that are pure scanned
images, so they become searchable/findable. PDFs that already have a text layer
are left untouched. **PDFs only** — a plain image file (jpg/png) has no text layer
to embed unless it is first turned into a PDF. Fully on-device (auge + PyMuPDF).

## Guardrails

- **Dry-run is the default.** Run without `--apply` first to list which PDFs are
  image-only; show that to the user, then add `--apply` to embed.
- **In place.** A real run rewrites each image-only PDF with an added text layer
  (the visible image is unchanged).
- **Paths with spaces / `(...)` / non-ASCII.** The path is passed via `"$ARGUMENTS"`
  (the full argument string, quoted), so spaces, parentheses and Umlauts work
  without manual quoting. Do **not** use `$1` here — it is shell-word-split and
  silently truncates such paths (e.g. `…/Mietvertrag_(unterschrieben).pdf` → `.pdf`).

## Run

Dry-run (always first):

!`uv run ${CLAUDE_PLUGIN_ROOT}/scripts/durchsuchbar.py "$ARGUMENTS"`

After the user confirms, embed for real (add `--rekursiv` for a whole folder tree):

```
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/durchsuchbar.py "$ARGUMENTS" --apply [--rekursiv]
```

The argument is **only the path** — `"$ARGUMENTS"` is one quoted word, so flags
typed after the path would become part of it and silently match nothing. Add
`--rekursiv` / `--redo` / `--apply` yourself after the quoted path, e.g.
`uv run ${CLAUDE_PLUGIN_ROOT}/scripts/durchsuchbar.py "$ARGUMENTS" --rekursiv --redo`
(dry-run), then the same with `--apply`.

`--redo` also **replaces** an existing invisible OCR layer (e.g. one where
Cyrillic came out as `·`, or another engine's gibberish). Only PDFs whose text is
entirely invisible qualify; visible document text is never touched, links are kept,
and a file is not written if it is signed, a page loses all its text, or any image's
pixel data would change. Dry-run first, as above.

Set OCR languages via `OCR_LANGS` (e.g. `OCR_LANGS=de-DE,en-US`). Needs `auge`
(see `/ocr-doctor`).
