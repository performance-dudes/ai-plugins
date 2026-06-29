---
description: Create or edit an image — Gemini for AI generation/semantic edits, ImageMagick for local processing
argument-hint: [what you want — e.g. "a hero image of sneakers, 16:9" or "make logo.png background transparent"]
---

# /image — create or edit an image

The user wants: **$ARGUMENTS**

Pick the right engine (the `image-toolkit` skill has the full reference — read it
if you need detail):

| Want | Use | How |
|------|-----|-----|
| Generate from a description, AI edit ("add snow", "make it a watercolor"), illustration/art | **Gemini** (recommended) | the bundled script below |
| Resize, crop, rotate, convert format, transparent/solid background, watermark, favicon, thumbnail, batch, GIF, montage | **ImageMagick** | `magick …` (local, deterministic, no API cost) |
| Generate then size/optimize exactly | **both** | Gemini → then `magick` post-process |

## AI generation / editing (Gemini)

Bundled script, runs via `uv` (no manual deps — PEP-723 header provisions
`google-genai` + Pillow on first run). Needs `GEMINI_API_KEY` in the env.

```bash
# Generate
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --prompt "Professional product photo of sneakers on a white background" \
  --aspect 16:9 --size 2K --out /tmp/hero_raw.png

# Edit an existing image (natural language)
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --edit logo.png --prompt "Replace the background with a soft gradient" \
  --out /tmp/logo_edited.png
```

Flags: `--model` (default `gemini-2.5-flash-image`), `--aspect` (`1:1`, `16:9`,
`4:3`, …), `--size` (`1K`/`2K`, generate only), `--out`.

## Local processing (ImageMagick)

Use `magick` directly — common recipes:

```bash
magick input.png output.jpg                                   # convert format
magick input.jpg -resize 1200x630 -strip -quality 85 out.jpg  # social size + optimize
magick input.png -fuzz 10% -transparent white out.png         # white -> transparent
magick in.png -define icon:auto-resize=256,128,64,48,32,16 favicon.ico
magick mogrify -path thumbs/ -resize 200x200 *.jpg            # batch
```

## How to respond

1. Decide engine from the request. If it needs **generation or semantic editing**
   → Gemini script. If it's **deterministic pixel work** → `magick`. If both →
   generate, then post-process.
2. If Gemini is needed but `GEMINI_API_KEY` is unset, say so and offer the
   ImageMagick path where it applies; suggest `/image-doctor`.
3. Run the command(s), report the **output path**, and `open` the result so the
   user sees it.
