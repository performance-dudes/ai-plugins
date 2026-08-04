# image-toolkit — image create & edit framework

Create and edit images from Claude Code. **Three AI providers** cover *generating*
and *semantically editing* images (text-to-image, "add snow to this scene",
illustrations, art); **ImageMagick 7** does the fast, deterministic local work
(resize, crop, convert, watermark, favicon, batch, GIF, montage).

```
prompt ──▶ Gemini · gpt-image-2 · FLUX.2 ──▶ ImageMagick (size · format · optimize) ──▶ asset
           └────── cloud, pick per job ─────┘  └────────── local, deterministic ──────┘
```

## Generic by design

Ships **no** domain assets and **no** credentials — every prompt, image and target
spec comes from the user; every endpoint, key and deployment name comes from the
environment. The skill and `/image` command carry the *how*; the *what* is yours.

## Providers

| `--provider` | Default model | Pick it for | Env |
|---|---|---|---|
| `gemini` *(default)* | `gemini-3-pro-image` | all-round, character consistency, 4K, transparency | `GEMINI_API_KEY` |
| `azure` | `gpt-image-2` | text *inside* the image, face-preserving edits, arbitrary sizes to 4K | `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` |
| `flux` | `FLUX.2-pro` | cinematic photorealism; no person/minor content gate | same Azure pair |

Optional overrides: `AZURE_OPENAI_API_VERSION`, `AZURE_IMAGE_DEPLOYMENT`,
`AZURE_FLUX_DEPLOYMENT`. `--provider auto` picks whatever is configured.

⚠️ `gpt-image-2` cannot return a transparent background — use `gemini`, or strip
it locally with `magick in.png -fuzz 10% -transparent white out.png`.

## Use it

```
/image-doctor                                      # check deps + which providers are configured
/image a 16:9 hero photo of sneakers on white      # AI generate
/image make logo.png background transparent        # local (ImageMagick)
```

or just ask — *"generate an image of …"* / *"resize these to 200×200"* — the
`image-toolkit` skill triggers.

Bundled script directly:

```bash
uv run scripts/generate_image.py --prompt "..." --aspect 16:9 --size 2K --out /tmp/out.png
uv run scripts/generate_image.py --provider azure --prompt "..." --size 4K --out /tmp/sign.png
uv run scripts/generate_image.py --edit in.jpg --prompt "..." --out /tmp/edited.png
```

`uv` provisions the SDKs from the script's PEP-723 header — no manual install.
**ImageMagick-only work needs no key.**

## Engines

| Want | Engine | Cost |
|------|--------|------|
| Generate from a description, AI edit, illustration/art | **Gemini / gpt-image-2 / FLUX.2** | API |
| Resize, crop, convert, transparent/solid bg, watermark, favicon, batch, GIF, montage | **ImageMagick** | local, free |
| Generate then size/optimize exactly | **both** | API + local |

## Components

| Component | Path | Shows |
|-----------|------|-------|
| Command | `commands/image.md` | `/image` → pick provider/engine, run, open result |
| Command | `commands/image-doctor.md` | `/image-doctor` → dependency + credential preflight |
| Skill | `skills/image-toolkit/SKILL.md` | autonomous trigger + provider routing |
| Reference | `skills/image-toolkit/references/imagemagick.md` | ImageMagick 7 command reference |
| Reference | `skills/image-toolkit/references/gemini-image-api.md` | Gemini image API |
| Reference | `skills/image-toolkit/references/azure-image-api.md` | Azure gpt-image-* and FLUX.2 |
| Script | `scripts/generate_image.py` | bundled multi-provider generate/edit (uv, PEP-723) |
| Script | `scripts/doctor.sh` | dependency + credential check |

## Setup & testing

- Deps: `brew install imagemagick uv`
- Credentials: export at least one provider's variables in `~/.zshrc` (see table)
- Smoke test: `bash image-toolkit/tests/validate.sh`
