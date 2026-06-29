# 2026-06-30 — image-toolkit plugin

Packaging the user-global `image-toolkit` skill (previously `~/.claude/skills/`,
markdown-only knowledge) as a public `ai-plugins` plugin, following the house
style of `ocr`/`transcribe`. Fills the marketplace's image gap.

## What was done

- Vendored the skill: `SKILL.md` + `references/imagemagick.md` (ImageMagick 7) +
  `references/gemini-image-api.md` (Gemini API) into `skills/image-toolkit/`.
- **Bundled `scripts/generate_image.py`** — the skill *referenced* a generation
  script that never existed; the model had to write curl/python ad hoc each time.
  Now a real script ships: generate + edit, run via `uv` with a PEP-723 header
  that provisions `google-genai>=1.68.0` + Pillow on first run. This is the actual
  value-add — it turns loose knowledge into a runnable entry point.
- Commands: `/image` (pick engine, run, open result), `/image-doctor` (preflight).
  `scripts/doctor.sh`, `README.md`, per-plugin `tests/validate.sh` (static-only,
  no network/key needed). Marketplace entry added (5th plugin).

## Decisions & learnings

- **Gemini as the *recommended* create framework, not just optional.** Benny's
  call: lead with the cloud generation/editing path prominently. This is a
  deliberate, softened break from the strict "100 % on-device" identity of
  `transcribe`/`ocr` — accepted for the user value. ImageMagick remains the
  deterministic local half; ImageMagick-only work needs no API key.
- **Engine split is the core of the skill.** Generation / semantic editing →
  Gemini; deterministic pixel work (resize, crop, convert, transparent bg,
  watermark, favicon, batch, GIF, montage) → ImageMagick; combine for
  generate-then-optimize. The `/image` command routes on this.
- **Generic by design.** Like the siblings, ships no domain assets — prompts and
  images come from the user.
- **CI hardening (side fix).** The repo's `validate.yml` still pointed at the
  pre-restructure `example/...` root paths (broken since plugins moved under
  `plugins/`), so it red-failed every PR. Rewrote it to iterate `plugins/*`,
  validate each `plugin.json`, **assert marketplace↔plugin.json version
  consistency**, and run every plugin's `tests/validate.sh`. That version check
  immediately surfaced a stale `ocr` entry (marketplace 0.1.2 vs plugin.json
  0.1.3, from PR #44) — bumped the marketplace entry to 0.1.3.
- **Source skill stays for now.** The global `~/.claude/skills/image-toolkit/`
  remains as the upstream source; whether to retire it in favour of the plugin is
  an open question, deferred.
