# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "google-genai>=1.68.0",
#   "Pillow",
# ]
# ///
"""Generate or edit images with the Google Gemini image API.

Bundled so the image-toolkit plugin works out of the box — no manual deps:
`uv` reads the PEP-723 header above and provisions google-genai + Pillow on
first run. Always pins google-genai>=1.68.0 (image_size / thinking_level need
the newer SDK; the system Python 3.9 path caches an old SDK — never use it).

Usage (always via uv):
    uv run scripts/generate_image.py \
        --prompt "A photorealistic fox in a snowy forest at golden hour" \
        --out /tmp/fox.png

    uv run scripts/generate_image.py \
        --edit input.jpg --prompt "Add snow to this scene" --out /tmp/edited.png

Auth: expects GEMINI_API_KEY in the environment (e.g. exported in ~/.zshrc).
Post-process the result with ImageMagick (`magick`) for exact size / format /
optimization — see the image-toolkit skill.
"""
from __future__ import annotations

import argparse
import os
import sys
from io import BytesIO
from pathlib import Path

# ImageMagick covers deterministic local work; this script is only the Gemini
# (cloud) half — the recommended path for *generating* and *semantic editing*.
MIME_BY_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def _client():
    from google import genai

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY not set — export it (see ~/.zshrc) and retry.")
    return genai.Client(api_key=key)


def _save_parts(parts, out_path: str) -> bool:
    from PIL import Image

    saved = False
    for part in parts:
        if getattr(part, "text", None):
            print(f"[gemini] {part.text.strip()}")
        elif getattr(part, "inline_data", None):
            Image.open(BytesIO(part.inline_data.data)).save(out_path)
            print(f"Image saved: {out_path}")
            saved = True
    return saved


def generate(prompt: str, model: str, aspect: str, size: str, out: str) -> bool:
    from google.genai import types

    client = _client()
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect,
                image_size=size,
                person_generation="allow_adult",
            ),
        ),
    )
    return _save_parts(resp.candidates[0].content.parts, out)


def edit(image_path: str, prompt: str, model: str, aspect: str, out: str) -> bool:
    from google.genai import types

    src = Path(image_path)
    if not src.is_file():
        sys.exit(f"--edit source not found: {image_path}")
    mime = MIME_BY_EXT.get(src.suffix.lower(), "image/jpeg")
    client = _client()
    resp = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=src.read_bytes(), mime_type=mime),
            types.Part.from_text(prompt),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect),
        ),
    )
    return _save_parts(resp.candidates[0].content.parts, out)


def main() -> int:
    p = argparse.ArgumentParser(description="Generate or edit images with Gemini.")
    p.add_argument("--prompt", required=True, help="text prompt / edit instruction")
    p.add_argument("--edit", metavar="IMAGE", help="edit an existing image instead of generating")
    p.add_argument("--out", default="/tmp/gemini_image.png", help="output file path")
    p.add_argument("--model", default="gemini-2.5-flash-image", help="image model id")
    p.add_argument("--aspect", default="16:9", help="aspect ratio, e.g. 1:1, 16:9, 4:3")
    p.add_argument("--size", default="2K", help="image size: 1K or 2K (generate only)")
    args = p.parse_args()

    if args.edit:
        ok = edit(args.edit, args.prompt, args.model, args.aspect, args.out)
    else:
        ok = generate(args.prompt, args.model, args.aspect, args.size, args.out)

    if not ok:
        print("No image returned — check the prompt, model, or your quota.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
