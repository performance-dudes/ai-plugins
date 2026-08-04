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
  the SDKs via its PEP-723 header).
- **GEMINI_API_KEY** → export in `~/.zshrc` (key from aistudio.google.com).
  Unlocks the `gemini` provider (the default).
- **AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY** → export in `~/.zshrc`.
  One pair unlocks *two* providers: `azure` (gpt-image-2 — best text-in-image
  and face-preserving edits) and `flux` (FLUX.2 — cinematic, no person gate).
  Optional: `AZURE_OPENAI_API_VERSION`, `AZURE_IMAGE_DEPLOYMENT`,
  `AZURE_FLUX_DEPLOYMENT` when your deployment names differ from the model names.
- **rsvg-convert** (optional) → `brew install librsvg` for crisp SVG→raster.

Make clear the split: ImageMagick + uv cover local work; each provider credential
unlocks one AI path. At least one provider is needed for AI generation;
ImageMagick-only work needs none.

**Never echo a key or endpoint value** — report only whether each is set.
