---
description: Check that the OCR pipeline's dependencies are installed and configured
---

# /ocr-doctor — preflight check

Verify the local environment can run the OCR pipeline. Run the bundled check and
present the result as a checklist, with the exact fix command for anything
missing. **Do not install anything automatically** — show the command.

!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/doctor.sh`

Each line is `OK` or `MISS`/`FAIL` with a hint. Summarize what is ready and what
the user must install, with copy-paste fixes:

- **auge** (Apple Vision OCR) → `brew tap Arthur-Ficial/tap && brew install auge`
- **macOS ≥ 26 (Tahoe)** → auge's Vision baseline; cannot be brew-installed
- **uv** → `brew install uv` (runs the Python scripts)
- **claude CLI** → required for the classification step
- **node ≥ 20** → `brew install node` (the Workflow tool needs it; Bash fallback works without)

Note: the searchable-PDF text layer uses auge + PyMuPDF — PyMuPDF is pulled by
`uv` on first use (PEP-723), so there is no extra system tool to install. auge is
Apple-Silicon + macOS 26 only.
