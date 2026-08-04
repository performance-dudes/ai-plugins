---
description: Create or edit an image — Gemini / gpt-image-2 / FLUX.2 for AI generation and semantic edits, ImageMagick for local processing
argument-hint: what you want — e.g. "a hero image of sneakers, 16:9" or "make logo.png background transparent"
---

# /image — create or edit an image

The user wants: **$ARGUMENTS**

Pick the right engine (the `image-toolkit` skill has the full reference — read it
if you need detail):

| Want | Use | How |
|------|-----|-----|
| Generate from a description, AI edit ("add snow", "make it a watercolor"), illustration/art | **an AI provider** | the bundled script below |
| Resize, crop, rotate, convert format, transparent/solid background, watermark, favicon, thumbnail, batch, GIF, montage | **ImageMagick** | `magick …` (local, deterministic, no API cost) |
| Generate then size/optimize exactly | **both** | AI → then `magick` post-process |

## AI generation / editing

Bundled script, runs via `uv` (no manual deps — PEP-723 header provisions the
SDKs on first run). Three providers, all configured purely through env vars:

| `--provider` | Default model | Pick it for | Needs |
|---|---|---|---|
| `gemini` *(default)* | `gemini-3-pro-image` | all-round, character consistency, 4K, transparency | `GEMINI_API_KEY` |
| `azure` | `gpt-image-2` | text *inside* the image, face-preserving edits, arbitrary 4K sizes | `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` |
| `flux` | `FLUX.2-pro` | cinematic photorealism; no person/minor gate | same Azure pair |

```bash
# Generate (default provider)
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --prompt "Professional product photo of sneakers on a white background" \
  --aspect 16:9 --size 2K --out /tmp/hero_raw.png

# Text in the image -> gpt-image-2
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py --provider azure \
  --prompt "Café sign reading 'ROASTED DAILY'" --aspect 16:9 --size 4K --out /tmp/sign.png

# Edit an existing image (natural language, any provider)
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --edit logo.png --prompt "Replace the background with a soft gradient" \
  --out /tmp/logo_edited.png
```

Flags: `--provider`, `--model` (overrides the per-provider default), `--aspect`
(`1:1`, `16:9`, `4:3`, `9:16`, `3:4`), `--size` (`1K`/`2K`/`4K`), `--quality`
(azure: `low`/`medium`/`high`), `--out`.

⚠️ `gpt-image-2` cannot return a **transparent background** — use `gemini`, or
generate on white and strip it: `magick in.png -fuzz 10% -transparent white out.png`.

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
   → the script, picking the provider from the table above. If it's
   **deterministic pixel work** → `magick`. If both → generate, then post-process.
2. If AI generation is needed but no provider credentials are set, say so and
   offer the ImageMagick path where it applies; suggest `/image-doctor`.
   Never print a key or endpoint back to the user.
3. Run the command(s), report the **output path**, and `open` the result so the
   user sees it.
