# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "google-genai>=1.68.0",
#   "httpx>=0.27",
#   "Pillow",
# ]
# ///
"""Generate or edit images across three providers: Gemini, Azure FLUX.2, Azure OpenAI.

Bundled so the image-toolkit plugin works out of the box — no manual deps:
`uv` reads the PEP-723 header above and provisions the SDKs on first run.
Always pins google-genai>=1.68.0 (image_size / thinking_level need the newer
SDK; the system Python 3.9 path caches an old SDK — never use it).

Providers
---------
gemini  (default)  Google Gemini image models. Best all-round: prompt adherence,
                   text-in-image, conversational editing, up to 4K.
azure              Azure OpenAI image deployment (gpt-image-2 and relatives).
                   Tops the blind-vote image-editing leaderboards; 4K, arbitrary
                   resolutions, face preservation. No transparent background.
flux               Black Forest Labs FLUX.2 on Azure AI Foundry. Photoreal /
                   cinematic, and — unlike the other two — no person/minor
                   content gate, so it still answers when they refuse.

Configuration — everything environment-specific comes from the environment; this
plugin hardcodes no endpoint, key, or deployment name:

    GEMINI_API_KEY              gemini provider
    AZURE_OPENAI_ENDPOINT       azure + flux providers, e.g. https://<your-resource>.openai.azure.com
    AZURE_OPENAI_API_KEY        azure + flux providers
    AZURE_OPENAI_API_VERSION    optional, defaults to a version serving generations AND edits
    AZURE_IMAGE_DEPLOYMENT      optional, overrides the default azure deployment name
    AZURE_FLUX_DEPLOYMENT       optional, overrides the default flux deployment name

Usage (always via uv):
    uv run scripts/generate_image.py \
        --prompt "A photorealistic fox in a snowy forest at golden hour" \
        --out /tmp/fox.png

    uv run scripts/generate_image.py --provider flux \
        --prompt "Cinematic portrait, 85mm, golden hour" --out /tmp/portrait.png

    uv run scripts/generate_image.py \
        --edit input.jpg --prompt "Add snow to this scene" --out /tmp/edited.png

Post-process the result with ImageMagick (`magick`) for exact size / format /
optimization — see the image-toolkit skill.
"""
from __future__ import annotations

import argparse
import base64
import os
import sys
from io import BytesIO
from pathlib import Path

# ImageMagick covers deterministic local work; this script is only the cloud
# half — the recommended path for *generating* and *semantic editing*.
MIME_BY_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

# Current defaults, verified live against both APIs on 2026-08-04.
DEFAULT_GEMINI_MODEL = "gemini-3-pro-image"  # Nano Banana Pro — GA, up to 4K
DEFAULT_FLUX_MODEL = "FLUX.2-pro"
DEFAULT_AZURE_MODEL = "gpt-image-2"
# 2025-04-01-preview is the oldest version that serves BOTH /images/generations and
# /images/edits — 2025-03-01-preview 404s on edits (verified live).
DEFAULT_AZURE_API_VERSION = "2025-04-01-preview"

# FLUX.2 has no aspect-ratio field — it takes explicit width/height. 1K keeps
# every ratio at or below 1 megapixel, which is also the cheapest Azure billing
# bucket (Azure rounds resolution UP to the next whole megapixel).
FLUX_DIMS = {
    "1K": {
        "1:1": (1024, 1024),
        "4:3": (1024, 768),
        "3:4": (768, 1024),
        "16:9": (1024, 576),
        "9:16": (576, 1024),
    },
    "2K": {
        "1:1": (2048, 2048),
        "4:3": (2048, 1536),
        "3:4": (1536, 2048),
        "16:9": (2048, 1152),
        "9:16": (1152, 2048),
    },
}

# gpt-image-1 / 1.5 / mini accept ONLY this fixed set of three sizes.
AZURE_LEGACY_SIZES = {
    "1:1": "1024x1024",
    "16:9": "1536x1024",
    "4:3": "1536x1024",
    "9:16": "1024x1536",
    "3:4": "1024x1536",
}

# gpt-image-2 takes arbitrary resolutions instead, under four constraints:
# both edges a multiple of 16 · long edge ≤ 3840 px · ratio ≤ 3:1 ·
# total pixels between 655,360 and 8,294,400. These tables stay inside all four.
AZURE_IMAGE2_SIZES = {
    "1K": {"1:1": "1024x1024", "4:3": "1184x896", "3:4": "896x1184", "16:9": "1360x768", "9:16": "768x1360"},
    "2K": {"1:1": "2048x2048", "4:3": "2368x1792", "3:4": "1792x2368", "16:9": "2720x1536", "9:16": "1536x2720"},
    "4K": {"1:1": "2880x2880", "4:3": "3312x2480", "3:4": "2480x3312", "16:9": "3840x2160", "9:16": "2160x3840"},
}


# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------


def _require_env(*names: str) -> list[str]:
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        sys.exit(f"{', '.join(missing)} not set — export it in ~/.zshrc and retry.")
    return [os.environ[n] for n in names]


def _write_bytes(data: bytes, out_path: str) -> bool:
    Path(out_path).write_bytes(data)
    print(f"Image saved: {out_path}")
    return True


def _azure_base() -> tuple[str, str, str]:
    key, endpoint = _require_env("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", DEFAULT_AZURE_API_VERSION)
    return key, endpoint.rstrip("/"), api_version


def _read_image_b64(image_path: str) -> tuple[bytes, str]:
    src = Path(image_path)
    if not src.is_file():
        sys.exit(f"--edit source not found: {image_path}")
    return src.read_bytes(), MIME_BY_EXT.get(src.suffix.lower(), "image/jpeg")


# --------------------------------------------------------------------------
# provider: gemini
# --------------------------------------------------------------------------


def _gemini_client():
    from google import genai

    (key,) = _require_env("GEMINI_API_KEY")
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


def gemini_generate(prompt: str, model: str, aspect: str, size: str, out: str, person: str | None = None) -> bool:
    from google.genai import types

    client = _gemini_client()
    img_kwargs = {"aspect_ratio": aspect, "image_size": size}
    # person_generation wird nur im Gemini Enterprise Agent Platform mode unterstuetzt.
    # In der Developer API (Standard) fuehrt es zu einem ValueError -> nur setzen, wenn angefordert.
    if person:
        img_kwargs["person_generation"] = person
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(**img_kwargs),
        ),
    )
    return _save_parts(resp.candidates[0].content.parts, out)


def gemini_edit(image_path: str, prompt: str, model: str, aspect: str, out: str) -> bool:
    from google.genai import types

    data, mime = _read_image_b64(image_path)
    client = _gemini_client()
    resp = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=data, mime_type=mime),
            types.Part.from_text(text=prompt),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect),
        ),
    )
    return _save_parts(resp.candidates[0].content.parts, out)


# --------------------------------------------------------------------------
# provider: flux (Black Forest Labs on Azure AI Foundry)
# --------------------------------------------------------------------------


def flux_run(prompt: str, model: str, aspect: str, size: str, out: str, edit_path: str | None) -> bool:
    """Call FLUX.2 through Azure's Black Forest Labs *provider* path.

    Note this is NOT the OpenAI-compatible /images endpoint:
        POST {endpoint}/providers/blackforestlabs/v1/{model}?api-version=preview
        Authorization: Bearer {key}   ->   {"data": [{"b64_json": "..."}]}
    The call is synchronous — no polling loop, unlike BFL's own API.
    """
    import httpx

    key, endpoint, _ = _azure_base()
    width, height = FLUX_DIMS.get(size, FLUX_DIMS["1K"]).get(aspect, (1024, 1024))
    payload: dict[str, object] = {
        "model": model,
        "prompt": prompt,
        "width": width,
        "height": height,
        "output_format": "png",
        "num_images": 1,
        "steps": 50,
        # NSFW/moderation knob (0 strict … 6 permissive). 2 is Azure's default.
        # It does NOT gate on people or minors — that is the point of this path.
        "safety_tolerance": 2,
    }
    if edit_path:
        data, _ = _read_image_b64(edit_path)
        payload["input_image"] = base64.b64encode(data).decode()

    # The provider path slug differs from the deployment name: the deployment is
    # "FLUX.2-pro", the BFL route is "flux-2-pro". The payload keeps the deployment name.
    slug = model.lower().replace(".", "-")
    url = f"{endpoint}/providers/blackforestlabs/v1/{slug}?api-version=preview"
    resp = httpx.post(
        url,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        json=payload,
        timeout=180.0,
    )
    if resp.status_code >= 400:
        sys.exit(f"Azure FLUX HTTP {resp.status_code}: {resp.text[:300]}")

    body = resp.json().get("data")
    first = body[0] if isinstance(body, list) and body else body
    b64 = first.get("b64_json") if isinstance(first, dict) else None
    if not b64:
        print("FLUX returned no image payload.", file=sys.stderr)
        return False
    return _write_bytes(base64.b64decode(b64), out)


# --------------------------------------------------------------------------
# provider: azure openai (gpt-image-1 and successors)
# --------------------------------------------------------------------------


def _azure_size(model: str, aspect: str, size: str) -> str:
    """Resolve --aspect/--size to the pixel string this deployment accepts.

    gpt-image-2 takes arbitrary resolutions (so --size actually scales); every
    older gpt-image-* is limited to three fixed sizes and ignores --size.
    """
    if "image-2" in model:
        return AZURE_IMAGE2_SIZES.get(size, AZURE_IMAGE2_SIZES["2K"]).get(aspect, "1024x1024")
    return AZURE_LEGACY_SIZES.get(aspect, "1024x1024")


def azure_run(prompt: str, model: str, aspect: str, size: str, out: str, edit_path: str | None, quality: str) -> bool:
    """Call an Azure OpenAI image deployment (deployment name == --model)."""
    import httpx

    key, endpoint, api_version = _azure_base()
    size = _azure_size(model, aspect, size)
    base = f"{endpoint}/openai/deployments/{model}/images"
    headers = {"api-key": key}

    if edit_path:
        data, mime = _read_image_b64(edit_path)
        resp = httpx.post(
            f"{base}/edits?api-version={api_version}",
            headers=headers,
            files={"image": (Path(edit_path).name, data, mime)},
            data={"prompt": prompt, "size": size, "quality": quality, "n": "1"},
            timeout=180.0,
        )
    else:
        resp = httpx.post(
            f"{base}/generations?api-version={api_version}",
            headers={**headers, "Content-Type": "application/json"},
            json={"prompt": prompt, "size": size, "quality": quality, "n": 1},
            timeout=180.0,
        )

    if resp.status_code >= 400:
        sys.exit(f"Azure OpenAI HTTP {resp.status_code}: {resp.text[:300]}")

    items = resp.json().get("data") or []
    if not items or not items[0].get("b64_json"):
        print("Azure OpenAI returned no image payload.", file=sys.stderr)
        return False
    if items[0].get("revised_prompt"):
        print(f"[azure] revised prompt: {items[0]['revised_prompt'][:200]}")
    return _write_bytes(base64.b64decode(items[0]["b64_json"]), out)


# --------------------------------------------------------------------------


def _resolve_provider(requested: str) -> str:
    if requested != "auto":
        return requested
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("AZURE_OPENAI_API_KEY"):
        return "flux"
    sys.exit("No provider credentials found — set GEMINI_API_KEY or AZURE_OPENAI_API_KEY in ~/.zshrc.")


def _resolve_model(provider: str, requested: str | None) -> str:
    """--model wins, then the deployment-name env override, then the built-in default.

    Azure deployment names are chosen per resource and need not match the model
    name, so they are overridable without touching the plugin.
    """
    if requested:
        return requested
    env_override = {"azure": "AZURE_IMAGE_DEPLOYMENT", "flux": "AZURE_FLUX_DEPLOYMENT"}.get(provider)
    if env_override and os.environ.get(env_override):
        return os.environ[env_override]
    return {"gemini": DEFAULT_GEMINI_MODEL, "flux": DEFAULT_FLUX_MODEL, "azure": DEFAULT_AZURE_MODEL}[provider]


def main() -> int:
    p = argparse.ArgumentParser(description="Generate or edit images (Gemini / Azure FLUX.2 / Azure OpenAI).")
    p.add_argument("--prompt", required=True, help="text prompt / edit instruction")
    p.add_argument("--edit", metavar="IMAGE", help="edit an existing image instead of generating")
    p.add_argument("--out", default="/tmp/generated_image.png", help="output file path")
    p.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "gemini", "flux", "azure"],
        help="gemini (default, best all-round) | flux (photoreal, no person gate) | azure (gpt-image-*)",
    )
    p.add_argument("--model", default=None, help="model / deployment id — defaults per provider")
    p.add_argument("--aspect", default="16:9", help="aspect ratio: 1:1, 16:9, 4:3, 9:16, 3:4")
    p.add_argument("--size", default="2K", help="1K/2K/4K — gemini and gpt-image-2 honour all three; flux 1K/2K")
    p.add_argument("--quality", default="high", help="azure only: high | medium | low")
    p.add_argument(
        "--person-generation",
        dest="person",
        default=None,
        help="gemini only, z.B. allow_adult — NUR im Enterprise Agent Platform mode; in der Developer API weglassen",
    )
    args = p.parse_args()

    provider = _resolve_provider(args.provider)
    model = _resolve_model(provider, args.model)
    print(f"[{provider}] model={model} aspect={args.aspect} mode={'edit' if args.edit else 'generate'}")

    if provider == "gemini":
        ok = (
            gemini_edit(args.edit, args.prompt, model, args.aspect, args.out)
            if args.edit
            else gemini_generate(args.prompt, model, args.aspect, args.size, args.out, args.person)
        )
    elif provider == "flux":
        ok = flux_run(args.prompt, model, args.aspect, args.size, args.out, args.edit)
    else:
        ok = azure_run(args.prompt, model, args.aspect, args.size, args.out, args.edit, args.quality)

    if not ok:
        print("No image returned — check the prompt, model, or your quota.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
