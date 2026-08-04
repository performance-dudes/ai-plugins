# 🔷 Azure Image Generation — gpt-image-* und FLUX.2

Reference for the two Azure-hosted providers this plugin ships: **Azure OpenAI**
(`gpt-image-2` and relatives) and **Black Forest Labs FLUX.2** on Azure AI Foundry.
Both are served by the *same* resource, key, and endpoint — but on **two different
URL shapes**, which is the single most common source of 404s.

> ⚠️ **No credentials in this repo.** Endpoint, key, api-version, and deployment
> names come from the environment. Every example below uses `${AZURE_OPENAI_*}`
> placeholders — never paste a real endpoint or key into a file.

## Inhaltsverzeichnis

1. [Konfiguration](#konfiguration)
2. [Azure OpenAI — gpt-image-*](#azure-openai--gpt-image-)
3. [gpt-image-2 vs gpt-image-1](#gpt-image-2-vs-gpt-image-1)
4. [Azure FLUX.2](#azure-flux2)
5. [Modellwahl](#modellwahl)
6. [Troubleshooting](#troubleshooting)

---

## Konfiguration

```bash
# in ~/.zshrc — values are yours, none of them belong in this plugin
export AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
export AZURE_OPENAI_API_KEY=<your-key>
export AZURE_OPENAI_API_VERSION=2025-04-01-preview   # optional
export AZURE_IMAGE_DEPLOYMENT=gpt-image-2            # optional, if name ≠ model
export AZURE_FLUX_DEPLOYMENT=FLUX.2-pro              # optional, ditto
```

List what is actually deployed on your resource:

```bash
curl -s -H "api-key: ${AZURE_OPENAI_API_KEY}" \
  "${AZURE_OPENAI_ENDPOINT}/openai/deployments?api-version=2023-03-15-preview" \
  | python3 -c 'import json,sys; [print(x["id"], x.get("status")) for x in json.load(sys.stdin)["data"]]'
```

`--model` on the bundled script is the **deployment name**, not the catalog name.

---

## Azure OpenAI — gpt-image-*

The OpenAI-compatible images path. Two operations, same auth header (`api-key`):

```
POST {endpoint}/openai/deployments/{deployment}/images/generations?api-version={ver}
POST {endpoint}/openai/deployments/{deployment}/images/edits?api-version={ver}
```

**api-version matters.** `2025-04-01-preview` serves *both* generations and edits.
Older versions (e.g. `2025-03-01-preview`) 404 on `/images/edits` — verified live.
`preview` as a bare value also 404s here; that alias belongs to the FLUX path.

### Generate

```bash
curl -s -X POST \
  "${AZURE_OPENAI_ENDPOINT}/openai/deployments/gpt-image-2/images/generations?api-version=2025-04-01-preview" \
  -H "api-key: ${AZURE_OPENAI_API_KEY}" -H "Content-Type: application/json" \
  -d '{"prompt": "Your prompt here", "size": "2720x1536", "quality": "high", "n": 1}'
```

### Edit (multipart, not JSON)

```bash
curl -s -X POST \
  "${AZURE_OPENAI_ENDPOINT}/openai/deployments/gpt-image-2/images/edits?api-version=2025-04-01-preview" \
  -H "api-key: ${AZURE_OPENAI_API_KEY}" \
  -F "image=@input.png" -F "prompt=Add warm string lights" -F "size=2720x1536" -F "n=1"
```

Both return `{"data": [{"b64_json": "...", "revised_prompt": "..."}]}` — **always
base64, never a URL**, unlike the old DALL·E deployments.

### Options

| Parameter | Values | Note |
|---|---|---|
| `size` | see below | `auto` lets the model choose |
| `quality` | `low`, `medium`, `high` | controls image *tokens*, not resolution |
| `output_format` | `png`, `jpeg` | |
| `output_compression` | 0–100 | JPEG only |
| `background` | `auto`, `transparent` | **not supported by gpt-image-2** |
| `n` | integer | images per request |

---

## gpt-image-2 vs gpt-image-1

| | `gpt-image-1` | `gpt-image-2` |
|---|---|---|
| Resolution | 3 fixed: `1024x1024`, `1024x1536`, `1536x1024` | arbitrary, under 4 constraints (below) |
| Max edge | 1536 px | 3840 px (4K) |
| Transparent background | ✅ | ❌ **not supported** |
| Input fidelity on edits | `input_fidelity` parameter | always high, parameter not accepted |
| Face preservation | — | ✅ |
| Blind-vote editing Elo | ~1139 | ~1463 (**#1**) |
| Price 1024², low / med / high | $0.011 / $0.042 / $0.167 | $0.006 / $0.053 / $0.211 |

**Verdict:** gpt-image-2 is the better default by a wide margin — the editing-arena
gap is not incremental, and `low` quality alone is both cheaper and roughly
gpt-image-1-mini class. Keep `gpt-image-1` only for **transparent backgrounds**,
which gpt-image-2 cannot produce.

### gpt-image-2 size constraints

All four must hold when you pass an explicit `size`:

1. both edges a multiple of **16**
2. long edge ≤ **3840** px
3. aspect ratio ≤ **3:1**
4. total pixels between **655,360** and **8,294,400**

Ready-made sets used by the bundled script:

| | 1:1 | 4:3 | 3:4 | 16:9 | 9:16 |
|---|---|---|---|---|---|
| 1K | 1024x1024 | 1184x896 | 896x1184 | 1360x768 | 768x1360 |
| 2K | 2048x2048 | 2368x1792 | 1792x2368 | 2720x1536 | 1536x2720 |
| 4K | 2880x2880 | 3312x2480 | 2480x3312 | 3840x2160 | 2160x3840 |

---

## Azure FLUX.2

FLUX is **not** on the OpenAI-compatible images path. It uses the Black Forest Labs
*provider* route, with **`Authorization: Bearer`** instead of `api-key`:

```
POST {endpoint}/providers/blackforestlabs/v1/{slug}?api-version=preview
```

The slug is lower-case with dots turned into hyphens: deployment `FLUX.2-pro` →
slug `flux-2-pro`. The payload keeps the **deployment name**.

```bash
curl -s -X POST \
  "${AZURE_OPENAI_ENDPOINT}/providers/blackforestlabs/v1/flux-2-pro?api-version=preview" \
  -H "Authorization: Bearer ${AZURE_OPENAI_API_KEY}" -H "Content-Type: application/json" \
  -d '{"model": "FLUX.2-pro", "prompt": "Cinematic portrait, 85mm, golden hour",
       "width": 1024, "height": 576, "output_format": "png", "num_images": 1,
       "steps": 50, "safety_tolerance": 2}'
```

Synchronous — no polling loop, unlike BFL's own API. Response is
`{"data": [{"b64_json": "..."}]}` (a **list**; some docs show a dict).

| Parameter | Note |
|---|---|
| `width` / `height` | explicit pixels — FLUX has no aspect-ratio field |
| `steps` | 28 for drafts, 50 for full quality |
| `safety_tolerance` | 0 strict … 6 permissive; 2 is the default. An NSFW knob — it does **not** gate on people or minors |
| `input_image` | raw base64 (no `data:` prefix) turns generation into an edit |

**Billing:** Azure rounds resolution **up to the next whole megapixel**, so
1024×1024 (exactly 1 MP) bills the minimum tier while 1032×1032 bills as 2 MP.
Every 1K preset in this plugin stays at or below 1 MP for that reason.
Indicative: `FLUX.2-pro` ≈ $0.03/image ≤1 MP, `FLUX.2-flex` ≈ $0.05, plus ≈ $0.015
per reference image.

**Why keep FLUX at all:** it has no person/minor content gate. When Gemini or
gpt-image refuse a perfectly benign prompt involving people, FLUX still answers.

---

## Modellwahl

| Job | Provider / model |
|---|---|
| Text inside the image (signs, posters, UI, infographics) | `gpt-image-2` |
| Edit that must preserve faces and fine detail | `gpt-image-2` |
| 4K hero image, arbitrary aspect | `gpt-image-2` (`--size 4K`) |
| Transparent background from the model | `gpt-image-1`, or Gemini |
| Cinematic photorealism | `FLUX.2-pro` |
| Prompt the others refuse (benign, people) | `FLUX.2-pro` |
| Cheapest acceptable draft | `gpt-image-2 --quality low` |

---

## Troubleshooting

| Symptom | Cause |
|---|---|
| `404` on `/images/edits` | api-version too old — use `2025-04-01-preview` or newer |
| `404` on the FLUX path | slug not normalized (`FLUX.2-pro` → `flux-2-pro`), or wrong auth header |
| `401` on FLUX, `200` on gpt-image | FLUX needs `Authorization: Bearer`, not `api-key` |
| `Resource not found` on generations | deployment name ≠ model name — list deployments, set `AZURE_IMAGE_DEPLOYMENT` |
| `background: transparent` rejected | gpt-image-2 does not support transparency |
| Image costs double what you expected | FLUX megapixel rounding — drop below the next whole MP |
| SDK returns a URL, not bytes | old DALL·E code path; gpt-image-* always returns `b64_json` |
