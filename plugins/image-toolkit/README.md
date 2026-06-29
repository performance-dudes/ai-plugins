# image-toolkit — image create & edit framework

Create and edit images from Claude Code. **Google Gemini** is the recommended
path for *generating* and *semantically editing* images (text-to-image, "add snow
to this scene", illustrations, art); **ImageMagick 7** does the fast, deterministic
local work (resize, crop, convert, watermark, favicon, batch, GIF, montage).

```
prompt ──▶ Gemini (generate / AI-edit) ──▶ ImageMagick (size · format · optimize) ──▶ asset
           └──── cloud, recommended ────┘   └────────── local, deterministic ──────┘
```

## Generic by design

Ships **no** domain assets — every prompt, image and target spec comes from the
user. The skill and `/image` command carry the *how*; the *what* is yours.

## Use it

```
/image-doctor                              # check deps (ImageMagick, uv, GEMINI_API_KEY)
/image a 16:9 hero photo of sneakers on white      # AI generate (Gemini)
/image make logo.png background transparent        # local (ImageMagick)
```

or just ask — *"generate an image of …"* / *"resize these to 200×200"* — the
`image-toolkit` skill triggers.

Bundled script directly:

```bash
uv run scripts/generate_image.py --prompt "..." --aspect 16:9 --size 2K --out /tmp/out.png
uv run scripts/generate_image.py --edit in.jpg --prompt "..." --out /tmp/edited.png
```

`uv` provisions `google-genai` + Pillow from the script's PEP-723 header — no
manual install. Needs `GEMINI_API_KEY` in the environment (key from
aistudio.google.com). **ImageMagick-only work needs no key.**

## Engines

| Want | Engine | Cost |
|------|--------|------|
| Generate from a description, AI edit, illustration/art | **Gemini** (recommended) | API |
| Resize, crop, convert, transparent/solid bg, watermark, favicon, batch, GIF, montage | **ImageMagick** | local, free |
| Generate then size/optimize exactly | **both** | API + local |

## Components

| Component | Path | Shows |
|-----------|------|-------|
| Command | `commands/image.md` | `/image` → pick engine, run, open result |
| Command | `commands/image-doctor.md` | `/image-doctor` → dependency preflight |
| Skill | `skills/image-toolkit/SKILL.md` | autonomous trigger + full reference (ImageMagick 7, Gemini API) |
| Script | `scripts/generate_image.py` | bundled Gemini generate/edit (uv, PEP-723) |
| Script | `scripts/doctor.sh` | dependency check |

## Setup & testing

- Deps: `brew install imagemagick uv` · export `GEMINI_API_KEY` in `~/.zshrc`
- Smoke test: `bash image-toolkit/tests/validate.sh`
