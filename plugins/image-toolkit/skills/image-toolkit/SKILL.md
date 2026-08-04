---
name: image-toolkit
description: |
  Complete image creation, editing, and processing toolkit combining ImageMagick CLI commands
  with three AI image providers (Google Gemini, Azure OpenAI gpt-image, Azure FLUX.2).
  Use this skill whenever the user wants to:
  - Create, edit, resize, crop, convert, optimize, or batch-process images with ImageMagick
  - Generate images with AI (text-to-image, image editing) via Gemini, gpt-image-2, or FLUX.2
  - Remove or change image backgrounds, add watermarks, create thumbnails or favicons
  - Work with transparency, alpha channels, or compositing
  - Create GIF animations, montages, or image grids
  - Convert between image formats (PNG, JPG, WebP, SVG, PDF)
  Trigger on: image editing, image generation, ImageMagick, magick command, resize image,
  crop image, transparent background, remove background, watermark, favicon, thumbnail,
  batch image processing, Gemini image, gpt-image, nano banana, FLUX, AI image generation,
  text-to-image, image conversion, GIF creation, montage, image optimization, SVG to PNG,
  PDF to image, image comparison.
---

# 🖼️ Image Toolkit

A comprehensive skill for all image work. **AI providers** create and semantically
edit images (text-to-image, "add snow to this scene", illustrations, art);
**ImageMagick** handles fast, deterministic local processing (resize, crop,
convert, watermark, favicon, batch, GIF, montage).

Entry point: the **`/image`** command (this plugin). It bundles
`scripts/generate_image.py`, which runs via `uv` with no manual setup — the
PEP-723 header provisions the SDKs on first run.

## 🔑 Configuration — environment only

The plugin hardcodes **no** endpoint, key, or deployment name. Everything
environment-specific is read from the environment (export in `~/.zshrc`):

| Variable | Needed for | Note |
|---|---|---|
| `GEMINI_API_KEY` | `gemini` | key at aistudio.google.com |
| `AZURE_OPENAI_ENDPOINT` | `azure`, `flux` | `https://<your-resource>.openai.azure.com` |
| `AZURE_OPENAI_API_KEY` | `azure`, `flux` | same key serves both paths |
| `AZURE_OPENAI_API_VERSION` | optional | overrides the built-in default |
| `AZURE_IMAGE_DEPLOYMENT` | optional | if your deployment name ≠ model name |
| `AZURE_FLUX_DEPLOYMENT` | optional | ditto for FLUX |

Run **`/image-doctor`** to see which providers are configured. Never write a key
or endpoint into a file — they belong in the environment.

## 🧭 Which provider

| Need | Provider | Why |
|------|----------|-----|
| Text *inside* the image (posters, signs, UI, infographics) | `azure` (gpt-image-2) | tops the blind-vote leaderboards on text + prompt adherence |
| Precise edits that must preserve faces / fine detail | `azure` (gpt-image-2) | always processes inputs at high fidelity; face preservation |
| Character consistency across a series, 4K, conversational multi-turn edits | `gemini` (Nano Banana Pro) | leads the editing arenas, strong reference handling |
| High-volume, cost-sensitive work | `gemini` (`gemini-3.1-flash-image`) | cheap generalist |
| Cinematic photorealism | `flux` (FLUX.2-pro) | BFL's strength |
| Subject the others refuse (people, minors in benign scenes) | `flux` | no person/minor content gate |
| Transparent background straight from the model | `gemini`, or `azure` with gpt-image-1 | **gpt-image-2 cannot do transparency** — else strip it in ImageMagick |

| Task | Tool | Why |
|------|------|-----|
| Resize, crop, rotate, convert formats | ImageMagick | Fast, local, no API cost |
| Batch processing (hundreds of files) | ImageMagick `mogrify` | Designed for bulk operations |
| Remove/change backgrounds (solid color) | ImageMagick | `-transparent`, `-fuzz`, floodfill |
| Add text, watermarks, shapes | ImageMagick | Full typographic control |
| Create thumbnails, favicons, montages | ImageMagick | Deterministic, repeatable |
| GIF animation from frames | ImageMagick | Frame-level control |
| Generate + post-process | AI → ImageMagick | Best of both worlds |

## 🤖 Current models (verified 2026-08-04)

| Provider | Model id | Status | Max | Notes |
|---|---|---|---|---|
| gemini | `gemini-3-pro-image` *(default)* | GA | 4K | "Nano Banana Pro" — top-tier editing, ~94 % text accuracy |
| gemini | `gemini-3.1-flash-image` | GA | 4K | "Nano Banana 2" — cheap high-volume generalist |
| gemini | `gemini-3.1-flash-lite-image` | GA | — | cheapest tier |
| gemini | `gemini-2.5-flash-image` | GA (legacy) | 2K | original Nano Banana — superseded, keep only for reproducibility |
| gemini | `imagen-4.0-*` | ⚠️ deprecated | 2K | shuts down **2026-08-17** — do not build on it |
| azure | `gpt-image-2` *(default)* | GA | 4K | arbitrary resolutions, face preservation, **no transparency** |
| azure | `gpt-image-1` | GA (legacy) | 1536 px | three fixed sizes; the only gpt-image with transparent background |
| azure | `gpt-image-1.5`, `gpt-image-1-mini` | GA | 1536 px | intermediate tiers |
| flux | `FLUX.2-pro` *(default)* | GA | ~4 MP | photoreal, cheapest FLUX tier |
| flux | `FLUX.2-flex` | GA | ~4 MP | more control knobs, pricier |

`azure` and `flux` model ids are **deployment names** on your own Azure resource —
what exists depends on what you deployed. `/image-doctor` and `--model` cover the rest.

## 📖 Reference files

This skill has three detailed reference files. Read the one you need:

- **`references/imagemagick.md`** — Complete ImageMagick 7 command reference
  - Read when: user needs local image processing, format conversion, batch operations
  - Covers: resize, crop, rotate, backgrounds, compositing, text, color ops, GIF, montage, optimization

- **`references/gemini-image-api.md`** — Gemini image generation API reference
  - Read when: user wants AI-generated images or AI-powered image editing via Gemini
  - Covers: models, REST API (curl), Python SDK (with `uv`), image editing, streaming, config options

- **`references/azure-image-api.md`** — Azure OpenAI (gpt-image-*) and Azure FLUX.2 reference
  - Read when: the job needs text-in-image, high-fidelity edits, or a provider without a person gate
  - Covers: both endpoint shapes, size/quality constraints, pricing, gpt-image-2 vs gpt-image-1

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

### AI image generation

```bash
# Bundled script (recommended) — uv reads its PEP-723 header, no manual deps.
# --provider defaults to gemini; falls back to flux if only Azure creds exist.
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --prompt "A photorealistic fox in a snowy forest at golden hour" --out /tmp/fox.png

# Text inside the image / high-fidelity edit -> gpt-image-2
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py --provider azure \
  --prompt "Shop sign reading 'OPEN DAILY 9-6'" --aspect 16:9 --size 4K --out /tmp/sign.png

# Cinematic photorealism, or a subject the others refuse -> FLUX.2
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py --provider flux \
  --prompt "Cinematic portrait, 85mm, golden hour" --out /tmp/portrait.png

# Edit an existing image (any provider)
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --edit photo.jpg --prompt "Add snow to this scene" --out /tmp/edited.png

# Ad-hoc Python (IMMER --python 3.13 und SDK-Version >= 1.68.0 angeben!)
uv run --python 3.13 --with "google-genai>=1.68.0" --with Pillow python script.py
```

Flags: `--provider` (`gemini`|`azure`|`flux`|`auto`), `--model`, `--aspect`
(`1:1`,`16:9`,`4:3`,`9:16`,`3:4`), `--size` (`1K`|`2K`|`4K`), `--quality`
(azure: `low`|`medium`|`high`), `--out`.

## 🔧 Important conventions

1. **ImageMagick 7**: Always use `magick` command (not legacy `convert`)
2. **Python**: Always use `uv` with `--python 3.13` — never use system Python (3.9 is EOL, causes old SDK caching)
   - `uv run --python 3.13 --with "google-genai>=1.68.0" --with Pillow python script.py`
   - Or create a project: `uv init && uv add "google-genai>=1.68.0" Pillow`
3. **Credentials live in the environment only** — never in a file, never in a prompt,
   never echoed into output. See the configuration table above.
4. **Combine tools**: Generate with an AI provider, then post-process with ImageMagick
5. **SDK-Version**: `image_size` und `thinking_level` benötigen SDK >= 1.65.0. Immer `"google-genai>=1.68.0"` pinnen!
6. **Transparency**: `gpt-image-2` cannot return a transparent background. Either use
   `gemini` / `gpt-image-1`, or generate on flat white and strip it with
   `magick in.png -fuzz 10% -transparent white out.png`.

## 🎯 Workflow: Generate + Post-process

For complex image tasks, combine both tools:

1. **Generate** the base image with an AI provider (creative content, complex scenes)
2. **Post-process** with ImageMagick (exact resize, format conversion, optimization, watermarks)

Example: Create a product hero image
```bash
# Step 1: Generate
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --prompt "Professional product photo of sneakers on white background" \
  --aspect 16:9 --out raw_hero.png

# Step 2: Post-process with ImageMagick
magick raw_hero.png \
  -resize 1200x630 \            # Social media size
  -strip \                       # Remove metadata
  -quality 85 \                  # Optimize
  hero_final.jpg
```
