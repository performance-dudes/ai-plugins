# Safety & care rules

Official documents are never moved blindly. The pipeline is built so that a human
always reviews before anything changes on disk.

## Three-stage safety

1. **Propose.** `klassifiziere.py` / the workflow only writes `_vorschlag.json` and
   `_vorschlag.md`. Nothing is moved.
2. **Review.** A human reads `_vorschlag.md` and corrects `_vorschlag.json` if a
   type/person/date/folder is wrong.
3. **Apply.** `anwenden.py` is **dry-run by default** — it prints the plan and
   changes nothing. Only `--apply` moves files, and it writes an undo log
   (`_undo.json`).

## Rules

- **Date = document date, not scan date.** The scanner timestamp in the filename
  (`YYYYMMDDHHMMSS`) is only a grouping key, never the document date.
- **Don't confuse similar people.** If the OCR text doesn't clearly identify the
  person, set `person = "unbekannt"` and `konfidenz = "niedrig"`.
- **Minimal disclosure.** Don't reproduce sensitive content (financial, ID,
  health data) more widely than needed; the reasoning field stays terse.
- **`ist_muell` is set aside, not deleted.** Empty pages / unusable scans go to the
  trash folder (`--muell-ordner`, default `_Aussortiert`) — never removed.
- **"No text detected" is often correct** — a pure photo or drawing. Treat it as a
  private/photo item with low confidence, not an error.
- **Photos stay photos.** Image scans with little or no recognized text (below
  MIN_DOC_CHARS) are kept as images — they are not forced into searchable PDFs.
  Document scans (enough text) become searchable PDFs. `--skip-fotos` leaves photo
  sessions untouched entirely.
- **Searchable text layer affects documents/PDFs.** Document image scans and
  image-only PDFs get an invisible auge text layer (on-device, via PyMuPDF); plain
  photo images are moved as-is.
