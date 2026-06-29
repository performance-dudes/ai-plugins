---
description: Check that the image-toolkit dependencies are installed and configured
---

# /image-doctor — preflight check

Verify the local environment can run image-toolkit. Run the bundled check and
present the result as a checklist, with the exact fix for anything missing.
**Do not install anything automatically** — show the command.

!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/doctor.sh`

Each line is `OK` or `MISS` with a hint. Summarize what is ready and what the
user must install:

- **ImageMagick 7** → `brew install imagemagick` (the `magick` command; v6
  `convert` is legacy). Powers all local processing — mandatory.
- **uv** → `brew install uv`. Runs the bundled `generate_image.py` (provisions
  `google-genai` + Pillow via its PEP-723 header).
- **GEMINI_API_KEY** → export in `~/.zshrc` (key from aistudio.google.com).
  Needed only for **AI generation/editing**; ImageMagick-only work needs no key.
- **rsvg-convert** (optional) → `brew install librsvg` for crisp SVG→raster.

Make clear the split: ImageMagick + uv cover local work; the Gemini key unlocks
the recommended AI generation/editing path.
