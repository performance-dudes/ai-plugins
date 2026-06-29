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

# uv — runs the bundled Gemini script (mandatory for AI generation)
if command -v uv >/dev/null 2>&1; then
  ok "uv ($(uv --version | awk '{print $2}'))"
else
  miss "uv not found — brew install uv  (runs scripts/generate_image.py)"
fi

# GEMINI_API_KEY — recommended AI-generation path
if [ -n "${GEMINI_API_KEY:-}" ]; then
  ok "GEMINI_API_KEY set (AI generation/editing available)"
else
  miss "GEMINI_API_KEY not set — export it in ~/.zshrc for AI generation (get a key at aistudio.google.com). ImageMagick-only work needs no key."
fi

# Optional helpers ImageMagick may delegate to
command -v rsvg-convert >/dev/null 2>&1 && ok "rsvg-convert (crisp SVG->raster)" || miss "rsvg-convert optional, for high-quality SVG rasterization — brew install librsvg"
