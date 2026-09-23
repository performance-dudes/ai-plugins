---
name: image-toolkit
description: |
  Complete image creation, editing, and processing toolkit combining ImageMagick CLI commands
  with Gemini AI image generation API. Use this skill whenever the user wants to:
  - Create, edit, resize, crop, convert, optimize, or batch-process images with ImageMagick
  - Generate images with AI using Google Gemini API (text-to-image, image editing)
  - Remove or change image backgrounds, add watermarks, create thumbnails or favicons
  - Work with transparency, alpha channels, or compositing
  - Create GIF animations, montages, or image grids
  - Convert between image formats (PNG, JPG, WebP, SVG, PDF)
  Trigger on: image editing, image generation, ImageMagick, magick command, resize image,
  crop image, transparent background, remove background, watermark, favicon, thumbnail,
  batch image processing, Gemini image, AI image generation, text-to-image, image conversion,
  GIF creation, montage, image optimization, SVG to PNG, PDF to image, image comparison.
---

# 🖼️ Image Toolkit

A comprehensive skill for all image work. **For creating and semantically editing
images, Google Gemini is the recommended framework** (text-to-image, "add snow to
this scene", illustrations, art); **ImageMagick** handles fast, deterministic local
processing (resize, crop, convert, watermark, favicon, batch, GIF, montage).

Entry point: the **`/image`** command (this plugin). It bundles
`scripts/generate_image.py`, which runs via `uv` with no manual setup — the
PEP-723 header provisions `google-genai` + Pillow on first run.

## 🧭 When to use what

| Task | Tool | Why |
|------|------|-----|
| Resize, crop, rotate, convert formats | ImageMagick | Fast, local, no API cost |
| Batch processing (hundreds of files) | ImageMagick `mogrify` | Designed for bulk operations |
| Remove/change backgrounds (solid color) | ImageMagick | `-transparent`, `-fuzz`, floodfill |
| Add text, watermarks, shapes | ImageMagick | Full typographic control |
| Create thumbnails, favicons, montages | ImageMagick | Deterministic, repeatable |
| GIF animation from frames | ImageMagick | Frame-level control |
| Generate images from text description | Gemini API | AI understands natural language prompts |
| Edit photos with natural language | Gemini API | "Add snow to this scene" |
| Create illustrations, art, infographics | Gemini API | Creative, context-aware |
| Complex background removal (photos) | Gemini API | AI understands scene semantics |
| Generate + post-process | Gemini → ImageMagick | Best of both worlds |

## 📖 Reference files

This skill has two detailed reference files. Read the one you need:

- **`references/imagemagick.md`** — Complete ImageMagick 7 command reference
  - Read when: user needs local image processing, format conversion, batch operations
  - Covers: resize, crop, rotate, backgrounds, compositing, text, color ops, GIF, montage, optimization

- **`references/gemini-image-api.md`** — Gemini image generation API reference
  - Read when: user wants AI-generated images or AI-powered image editing
  - Covers: GA models + model choice, shut-down model IDs and their successors, Interactions API
    (Python SDK with `uv`, curl), editing, multi-turn, Search grounding, config options, pricing

## ⚡ Quick reference (common tasks)

### ImageMagick basics

```bash
# Convert format
magick input.png output.jpg

# Resize (fit in box, keep aspect ratio)
magick input.jpg -resize 800x600 output.jpg

# Crop from center
magick input.jpg -gravity center -crop 400x400+0+0 +repage output.jpg

# Make white background transparent
magick input.png -fuzz 10% -transparent white output.png

# Remove background (flatten to color)
magick input.png -background white -alpha remove output.jpg

# Add text
magick input.jpg -gravity south -fill white -font Arial -pointsize 36 \
  -annotate +0+10 "Caption" output.jpg

# Batch resize all JPGs
magick mogrify -path thumbnails/ -resize 200x200 *.jpg

# Create favicon from PNG
magick input.png -define icon:auto-resize=256,128,64,48,32,16 favicon.ico
```

### Gemini image generation

```bash
# Bundled script (recommended) — uv reads its PEP-723 header, no manual deps:
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --prompt "A photorealistic fox in a snowy forest at golden hour" --out /tmp/fox.png
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --edit photo.jpg --prompt "Add snow to this scene" --out /tmp/edited.png
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --continue <interaction-id> --prompt "Now make it night" --out /tmp/night.png

# Ad-hoc Python (IMMER --python 3.13 und SDK-Version >= 2.25.0 angeben!)
uv run --python 3.13 --with "google-genai>=2.25.0" --with Pillow python script.py

# curl (Interactions API)
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-flash-image",
    "input": "Your prompt here",
    "response_format": {"type": "image", "aspect_ratio": "16:9", "image_size": "2K"}
  }'
```

**Models (all GA):** `gemini-3.1-flash-image` (default, Nano Banana 2) ·
`gemini-3.1-flash-lite-image` (cheapest, 1K only) · `gemini-3-pro-image` (best text-in-image,
complex layouts). The 2.5 Flash image model, every preview image ID and all Imagen models are
shut down or shutting down — never use them; the successor table is in the reference.

## 🔧 Important conventions

1. **ImageMagick 7**: Always use `magick` command (not legacy `convert`)
2. **Python**: Always use `uv` with `--python 3.13` — never use system Python (3.9 is EOL, causes old SDK caching)
   - `uv run --python 3.13 --with "google-genai>=2.25.0" --with Pillow python script.py`
   - Or create a project: `uv init && uv add "google-genai>=2.25.0" Pillow`
3. **API Key**: Stored as `GEMINI_API_KEY` environment variable (in `~/.zshrc`)
4. **Combine tools**: Generate with Gemini, then post-process with ImageMagick for best results
5. **Interactions API, not `generateContent`**: Google marks `generateContent` as legacy; image
   work goes through `client.interactions.create` (SDK >= 2.25.0). Output is always JPEG —
   re-encode locally for PNG/WebP; transparency comes from ImageMagick, not from Gemini.

## 🎯 Workflow: Generate + Post-process

For complex image tasks, combine both tools:

1. **Generate** the base image with Gemini (creative content, complex scenes)
2. **Post-process** with ImageMagick (exact resize, format conversion, optimization, watermarks)

Example: Create a product hero image
```bash
# Step 1: Generate with Gemini
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --prompt "Professional product photo of sneakers on white background" \
  --aspect 16:9 --size 2K --out raw_hero.png

# Step 2: Post-process with ImageMagick
# social media size, strip metadata, optimize
magick raw_hero.png -resize 1200x630 -strip -quality 85 hero_final.jpg
```
