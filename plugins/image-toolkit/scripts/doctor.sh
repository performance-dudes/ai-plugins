#!/usr/bin/env bash
# Preflight for the image-toolkit plugin. Prints OK / MISS lines with a hint.
# Mutates nothing, installs nothing — the command shows the fix.
set -uo pipefail

ok()   { printf 'OK    %s\n' "$1"; }
miss() { printf 'MISS  %s\n' "$1"; }

# ImageMagick 7 — local processing half (mandatory)
if command -v magick >/dev/null 2>&1; then
  ok "ImageMagick 7 ($(magick -version | head -1 | awk '{print $3}'))"
elif command -v convert >/dev/null 2>&1; then
  miss "ImageMagick is v6 (legacy 'convert') — install v7 for the 'magick' command: brew install imagemagick"
else
  miss "ImageMagick not found — brew install imagemagick"
fi

# uv — runs the bundled generation script (mandatory for AI generation)
if command -v uv >/dev/null 2>&1; then
  ok "uv ($(uv --version | awk '{print $2}'))"
else
  miss "uv not found — brew install uv  (runs scripts/generate_image.py)"
fi

# Provider credentials. All three are optional on their own — you need at least
# one for AI generation; ImageMagick-only work needs none. Never print a value.
providers=0

if [ -n "${GEMINI_API_KEY:-}" ]; then
  ok "GEMINI_API_KEY set — provider 'gemini' available (default)"
  providers=$((providers + 1))
else
  miss "GEMINI_API_KEY not set — export it in ~/.zshrc for the 'gemini' provider (key at aistudio.google.com)"
fi

if [ -n "${AZURE_OPENAI_API_KEY:-}" ] && [ -n "${AZURE_OPENAI_ENDPOINT:-}" ]; then
  ok "AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT set — providers 'azure' and 'flux' available"
  providers=$((providers + 1))
  [ -n "${AZURE_OPENAI_API_VERSION:-}" ] \
    && ok "AZURE_OPENAI_API_VERSION set (overrides the built-in default)" \
    || ok "AZURE_OPENAI_API_VERSION unset — using the built-in default (fine)"
  [ -n "${AZURE_IMAGE_DEPLOYMENT:-}" ] && ok "AZURE_IMAGE_DEPLOYMENT set (custom azure deployment name)"
  [ -n "${AZURE_FLUX_DEPLOYMENT:-}" ] && ok "AZURE_FLUX_DEPLOYMENT set (custom flux deployment name)"
else
  miss "AZURE_OPENAI_API_KEY / AZURE_OPENAI_ENDPOINT not both set — export them in ~/.zshrc for the 'azure' and 'flux' providers"
fi

[ "$providers" -eq 0 ] && miss "No AI provider configured — only the ImageMagick half will work"

# Optional helpers ImageMagick may delegate to
command -v rsvg-convert >/dev/null 2>&1 && ok "rsvg-convert (crisp SVG->raster)" || miss "rsvg-convert optional, for high-quality SVG rasterization — brew install librsvg"
