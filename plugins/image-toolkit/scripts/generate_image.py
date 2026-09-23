# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "google-genai>=2.25.0",
#   "Pillow",
# ]
# ///
"""Generate or edit images with the Gemini image models (Interactions API).

Bundled so the image-toolkit plugin works out of the box — no manual deps:
`uv` reads the PEP-723 header above and provisions google-genai + Pillow on
first run. Pins google-genai>=2.25.0: `client.interactions` and the typed
image `response_format` need the 2.x SDK.

Usage (always via uv):
    uv run scripts/generate_image.py \
        --prompt "A photorealistic fox in a snowy forest at golden hour" \
        --out /tmp/fox.png

    uv run scripts/generate_image.py \
        --edit input.jpg --prompt "Add snow to this scene" --out /tmp/edited.png

    # follow-up edit on the previous result (id is printed after every run)
    uv run scripts/generate_image.py \
        --continue <interaction-id> --prompt "Make it night" --out /tmp/night.png

Auth: expects GEMINI_API_KEY in the environment (e.g. exported in ~/.zshrc).
Post-process the result with ImageMagick (`magick`) for exact size / format /
optimization — see the image-toolkit skill.
"""
from __future__ import annotations

import argparse
import base64
import mimetypes
import os
import sys
from io import BytesIO
from pathlib import Path

# ImageMagick covers deterministic local work; this script is only the Gemini
# (cloud) half — the recommended path for *generating* and *semantic editing*.
# Input formats the image models accept; iPhone photos are HEIC.
MIME_BY_EXT = {".heic": "image/heic", ".heif": "image/heif"}
# Output formats Pillow writes without extra plugins.
OUT_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}

DEFAULT_MODEL = "gemini-3.1-flash-image"  # Nano Banana 2
STANDARD_ASPECTS = {"1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"}
EXTREME_ASPECTS = {"1:4", "4:1", "1:8", "8:1"}  # Flash only
# What each GA image model accepts (Gemini API image-generation guide).
MODELS = {
    "gemini-3.1-flash-lite-image": {"sizes": {"1K"}, "thinking": True, "search": set(),
                                    "aspects": STANDARD_ASPECTS},
    "gemini-3.1-flash-image": {"sizes": {"512", "1K", "2K", "4K"}, "thinking": True,
                               "search": {"web_search", "image_search"},
                               "aspects": STANDARD_ASPECTS | EXTREME_ASPECTS},
    "gemini-3-pro-image": {"sizes": {"1K", "2K", "4K"}, "thinking": False, "search": {"web_search"},
                           "aspects": STANDARD_ASPECTS},
}
# Shut down (ai.google.dev/gemini-api/docs/deprecations) -> successor.
SHUT_DOWN = {
    "gemini-2.5-flash-image": "gemini-3.1-flash-image",  # dead-id-ok
    "gemini-3.1-flash-image-preview": "gemini-3.1-flash-image",  # dead-id-ok
    "gemini-3-pro-image-preview": "gemini-3-pro-image",  # dead-id-ok
    "imagen-4.0-generate-001": "gemini-3.1-flash-image",  # dead-id-ok
    "imagen-4.0-ultra-generate-001": "gemini-3.1-flash-image",  # dead-id-ok
    "imagen-4.0-fast-generate-001": "gemini-3.1-flash-image",  # dead-id-ok
}
ASPECTS = sorted(STANDARD_ASPECTS | EXTREME_ASPECTS)
MAX_REFERENCE_IMAGES = 14


def _client():
    from google import genai

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY not set — export it (see ~/.zshrc) and retry.")
    return genai.Client(api_key=key)


def _image_block(path: str) -> dict:
    src = Path(path)
    if not src.is_file():
        sys.exit(f"--edit source not found: {path}")
    ext = src.suffix.lower()
    mime = MIME_BY_EXT.get(ext) or mimetypes.guess_type(src.name)[0] or "image/jpeg"
    return {
        "type": "image",
        "mime_type": mime,
        "data": base64.b64encode(src.read_bytes()).decode("ascii"),
    }


def _check(model: str, size: str | None = None, thinking: str | None = None,
           search: list[str] | None = None, aspect: str | None = None) -> None:
    """Reject combinations the model cannot serve — before any paid call."""
    if model in SHUT_DOWN:
        sys.exit(f"{model} is shut down — use {SHUT_DOWN[model]}.")
    caps = MODELS.get(model)
    if caps is None:
        # Unknown id (newer model, alias): pass through, let the API decide.
        print(f"[warn] {model} is not a known GA image model — sending as-is.", file=sys.stderr)
        return
    if size and size not in caps["sizes"]:
        sys.exit(f"--size {size} not supported by {model} (allowed: {', '.join(sorted(caps['sizes']))}).")
    if thinking and not caps["thinking"]:
        sys.exit(f"--thinking is not configurable on {model} (it always thinks).")
    unsupported = set(search or ()) - caps["search"]
    if unsupported:
        sys.exit(f"--search {' '.join(sorted(unsupported))} not supported by {model}.")
    if aspect and aspect not in caps["aspects"]:
        sys.exit(f"--aspect {aspect} not supported by {model} (1:4, 4:1, 1:8, 8:1 are Flash only).")


def _check_out(out: str) -> None:
    """Fail before paying if the result could not be written."""
    path = Path(out)
    if path.suffix.lower() not in OUT_EXTS:
        sys.exit(f"--out {out}: unsupported extension (use one of {', '.join(sorted(OUT_EXTS))}).")
    if not path.parent.is_dir():
        sys.exit(f"--out {out}: directory {path.parent} does not exist.")


def run(args) -> bool:
    from PIL import Image

    # Fresh images default to 16:9; edits and follow-ups keep the input's ratio.
    aspect = args.aspect or (None if args.edit or args.continue_id else "16:9")
    _check(args.model, args.size, args.thinking, args.search, aspect)
    _check_out(args.out)
    if args.edit:
        if len(args.edit) > MAX_REFERENCE_IMAGES:
            sys.exit(f"at most {MAX_REFERENCE_IMAGES} input images, got {len(args.edit)}.")
        user_input = [*(_image_block(p) for p in args.edit), {"type": "text", "text": args.prompt}]
    else:
        user_input = args.prompt

    response_format = {"type": "image"}
    if aspect:
        response_format["aspect_ratio"] = aspect
    if args.size:
        response_format["image_size"] = args.size
    request = {"model": args.model, "input": user_input, "response_format": response_format}
    if args.thinking:
        request["generation_config"] = {"thinking_level": args.thinking}
    if args.continue_id:
        request["previous_interaction_id"] = args.continue_id
    if args.search:
        request["tools"] = [{"type": "google_search", "search_types": args.search}]

    # Keep the Client referenced: SDK 2.x closes its HTTP transport when the
    # Client is garbage-collected, so `_client().interactions.create(...)` fails.
    client = _client()
    interaction = client.interactions.create(**request)

    if interaction.output_text:
        print(f"[gemini] {interaction.output_text.strip()}")
    print(f"Interaction: {interaction.id}  (follow-up: --continue {interaction.id})")
    image = interaction.output_image  # last image of the turn = the final render
    if image is None or not image.data:
        return False
    # The API delivers JPEG; Pillow re-encodes to whatever --out asks for.
    Image.open(BytesIO(base64.b64decode(image.data))).save(args.out)
    print(f"Image saved: {args.out}")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description="Generate or edit images with Gemini (Interactions API).")
    p.add_argument("--prompt", required=True, help="text prompt / edit instruction")
    p.add_argument("--edit", metavar="IMAGE", nargs="+",
                   help=f"edit/combine existing image(s) — up to {MAX_REFERENCE_IMAGES} references")
    p.add_argument("--continue", dest="continue_id", metavar="ID",
                   help="continue a previous interaction (multi-turn editing)")
    p.add_argument("--out", default="/tmp/gemini_image.png", help="output file path (format from extension)")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"image model id (default {DEFAULT_MODEL}; also: {', '.join(m for m in MODELS if m != DEFAULT_MODEL)})")
    p.add_argument("--aspect", choices=ASPECTS,
                   help="aspect ratio (default 16:9; --edit/--continue keep the input's ratio). "
                        "1:4, 4:1, 1:8, 8:1 = Flash only")
    p.add_argument("--size", choices=["512", "1K", "2K", "4K"],
                   help="output resolution (default: model default, 1K). 512 = Flash only, Lite = 1K only")
    p.add_argument("--thinking", choices=["minimal", "high"],
                   help="thinking level for Flash / Flash Lite (API default: minimal). Pro always thinks")
    p.add_argument("--search", nargs="+", choices=["web_search", "image_search"],
                   help="ground on Google Search (image_search: Flash only; not on Flash Lite)")
    args = p.parse_args()

    if not run(args):
        print("No image returned — check the prompt, model, or your quota.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
