---
name: document-ocr
description: OCR scanned documents on-device (auge / Apple Vision, auto-rotating) and classify each into a reviewable rename/sort proposal, then optionally apply it (move + searchable PDF text layer, dry-run + undo). Use when the user wants to digitize, OCR, read, sort, rename or file scanned documents/receipts/letters/IDs, make scanned PDFs searchable, or turn a folder of scans into an organized archive. Trigger phrases — "OCR these scans", "digitize documents", "sort my scans", "read this scan", "make this PDF searchable", "classify documents", "Scan einsortieren", "Dokumente digitalisieren", "durchsuchbares PDF".
argument-hint: "[scan-folder]"
---

# document-ocr — call the bundled OCR workflow

This skill lets the model start the OCR pipeline autonomously when a request
matches, without the user remembering `/ocr`. It funnels into the same
`workflows/ocr.js` — single source of truth. It produces a **proposal only**;
moving files is a separate, human-gated step.

## This plugin is generic — context comes from the user

It ships **no** domain knowledge — no names, no taxonomy. Classification quality
comes from context the user gives. Before running, gather and (if missing) **ask
for**:

1. **Scan folder** — the directory of scans.
2. **Who is who** — people whose documents these are, with easy mix-ups noted.
3. **Document types** that typically occur.
4. **Target taxonomy** — folders under the documents root to sort into.
5. **Naming convention** (default: `YYYY-MM-DD_Type_Person_Detail`).
6. **Languages** of the documents (BCP-47).

Assemble these into one CONTEXT block. Empty context is allowed (more
conservative classification). Template:
`references/context-and-taxonomy.md`.

## What to do

1. Resolve the scan folder and the CONTEXT above.

2. If the **Workflow tool is available**, run the bundled script:

   ```
   Workflow({
     scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/ocr.js",
     args: {
       pluginRoot: "${CLAUDE_PLUGIN_ROOT}",
       scanDir: "<scan folder>",
       context: "<the CONTEXT block>",
       langs: "<e.g. de-DE,en-US>"
     }
   })
   ```

   It OCRs on-device, classifies each document with Opus in parallel, and writes
   `_vorschlag.json` + `_vorschlag.md`. Report the proposal and point the user at
   `_vorschlag.md` to review. Then stop — do **not** move anything.

3. If the **Workflow tool is NOT available**, fall back to the bundled scripts via
   Bash — see `references/pipeline.md`.

## Applying and searchable PDFs

- To move the reviewed proposal into the taxonomy: `/ocr-apply` (dry-run by
  default, undo log). Image-only PDFs get a searchable text layer on move.
- To embed text layers into existing PDFs standalone: `/ocr-searchable`.

## Safety-first principles

- **On-device for OCR.** auge / Apple Vision runs locally; only the OCR **text**
  goes to Opus for classification — never the images.
- **Never move without review.** The pipeline proposes; a human reviews; only then
  is anything moved, with a dry-run and an undo log.
- **Date = document date, not scan date.** Don't confuse similar people; when
  unsure, "unbekannt".

References: `references/pipeline.md`, `references/context-and-taxonomy.md`,
`references/safety.md`.
