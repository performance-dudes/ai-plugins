---
description: OCR a folder of scanned documents and classify each into a reviewable rename/sort proposal
argument-hint: "[scan-folder]"
---

# /ocr — OCR + classify scanned documents into a proposal

Run the plugin's bundled OCR workflow for `$ARGUMENTS`. This produces only a
**proposal** — nothing is moved. Applying is a separate, human-gated step
(`/ocr-apply`).

## Step 1 — gather CONTEXT (the biggest quality lever)

This plugin ships **no** domain knowledge. Classification quality comes entirely
from context **you** provide. Before running, make sure you have, and **ask the
user** for anything missing:

- **Scan folder** — the directory of scans (jpg/png/pdf/heic/…), first argument.
- **Who is who** — the people whose documents these are, with any easy mix-ups
  (so a name is assigned correctly or left "unbekannt").
- **Document types** that typically occur.
- **Target taxonomy** — the folders under the documents root to sort into.
- **Naming convention** for the speaking filename (default if none:
  `YYYY-MM-DD_Type_Person_Detail`).
- **Languages** of the documents (BCP-47, e.g. `de-DE,en-US`).

Assemble these into a single CONTEXT block (plain text). With no context it still
classifies, just more conservatively (person/date → "unbekannt"). A template is
in `${CLAUDE_PLUGIN_ROOT}/skills/document-ocr/references/context-and-taxonomy.md`.

## Step 2 — run the workflow

**Preferred — Workflow orchestration.** If the **Workflow tool** is available:

```
Workflow({
  scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/ocr.js",
  args: {
    pluginRoot: "${CLAUDE_PLUGIN_ROOT}",
    scanDir: "<scan folder>",
    context: "<the CONTEXT block you assembled>",
    langs: "<e.g. de-DE,en-US>"
  }
})
```

It OCRs every scan on-device (auge / Apple Vision, auto-rotating), classifies each
document with **Opus in parallel**, and writes `_vorschlag.json` + `_vorschlag.md`
into the output dir. When the task-notification arrives, report:
- the output dir and the **proposal** (point the user at `_vorschlag.md` to review),
- the count and how many are low-confidence,
- that **applying is separate**: review/fix `_vorschlag.json`, then `/ocr-apply`.

**Fallback (no Workflow tool).** Run the scripts via Bash: `ocr.py <scanDir> <outDir>`
→ write the CONTEXT to a file → `klassifiziere.py <outDir> --context-file <ctx>`.
See `${CLAUDE_PLUGIN_ROOT}/skills/document-ocr/references/pipeline.md`.

## Safety

Never move documents without review. `/ocr` only proposes; `/ocr-apply` is dry-run
by default and writes an undo log. If a step fails, see `/ocr-doctor`.
