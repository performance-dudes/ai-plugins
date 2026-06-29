# 🤖 Gemini Image Generation API — Vollständige Referenz

## Inhaltsverzeichnis
1. [Verfügbare Modelle](#verfügbare-modelle)
2. [API Endpoints](#api-endpoints)
3. [Konfigurationsoptionen](#konfigurationsoptionen)
4. [Python SDK (mit uv)](#python-sdk-mit-uv)
5. [Bash/curl API](#bashcurl-api)
6. [Bildbearbeitung](#bildbearbeitung)
7. [Streaming](#streaming)
8. [ThinkingConfig](#thinkingconfig)
9. [Google Search Tool](#google-search-tool)
10. [Best Practices](#best-practices)

---

## Verfügbare Modelle

### Gemini Native Image Models (generateContent endpoint)

| Model ID | Status | Notes |
|----------|--------|-------|
| `gemini-2.5-flash-image` | **GA (Stable)** | Recommended for production |
| `gemini-3.1-flash-image-preview` | Preview | Fast, up to 4K, thinkingLevel support |
| `gemini-3-pro-image-preview` | Preview | Studio quality, 4K, complex layouts |

### Imagen Models (predict endpoint)

| Model ID | Status | Notes |
|----------|--------|-------|
| `imagen-4.0-generate-001` | GA | Standard, up to 2K |
| `imagen-4.0-ultra-generate-001` | GA | Highest quality |
| `imagen-4.0-fast-generate-001` | GA | Lowest latency |

### Model selection guide

| Use case | Recommended model |
|----------|-------------------|
| Standard production | `gemini-2.5-flash-image` |
| Interactive editing (multi-turn) | `gemini-2.5-flash-image` |
| Best text-in-image quality | `gemini-3-pro-image-preview` |
| Lowest latency | `imagen-4.0-fast-generate-001` |
| Highest image quality | `imagen-4.0-ultra-generate-001` |
| High volume, fast | `gemini-3.1-flash-image-preview` |

---

## API Endpoints

```
# Gemini models
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:streamGenerateContent

# Imagen models
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:predict
```

Auth: `x-goog-api-key: $GEMINI_API_KEY` header

---

## Konfigurationsoptionen

### imageConfig

#### REST API (camelCase)

| Parameter | Values | Default |
|-----------|--------|---------|
| `aspectRatio` | `"1:1"`, `"2:3"`, `"3:2"`, `"3:4"`, `"4:3"`, `"4:5"`, `"5:4"`, `"9:16"`, `"16:9"`, `"21:9"`, `"1:4"`, `"4:1"`, `"1:8"`, `"8:1"` | `"1:1"` |
| `imageSize` | `"512"` (3.1-flash only), `"1K"`, `"2K"`, `"4K"` | `"1K"` |
| `personGeneration` | `"dont_allow"`, `"allow_adult"`, `"allow_all"` | `"allow_adult"` |
| `imageOutputOptions.mimeType` | `"image/jpeg"`, `"image/png"`, `"image/webp"` | `"image/png"` |
| `imageOutputOptions.compressionQuality` | 1-100 | — |

#### Python SDK (snake_case) — types.ImageConfig()

> **SDK >= 1.65.0 erforderlich.** Immer `--python 3.13` und `--with "google-genai>=1.68.0"` bei `uv run` verwenden, sonst werden alte cached Pakete genutzt, die `image_size` und `thinking_level` nicht kennen.

| Parameter (Python) | Values | Unterstützt |
|---------------------|--------|-------------|
| `aspect_ratio` | `"1:1"`, `"16:9"`, `"9:16"`, etc. | ✅ Alle Modelle |
| `image_size` | `"512"`, `"1K"`, `"2K"`, `"4K"` | ✅ Ab SDK 1.65.0 |
| `person_generation` | `"ALLOW_ALL"`, `"ALLOW_ADULT"`, `"ALLOW_NONE"` | ✅ Alle Modelle |
| `output_mime_type` | — | ❌ Nur Vertex AI, nicht Gemini API |
| `output_compression_quality` | — | ❌ Nur Vertex AI, nicht Gemini API |

### ThinkingConfig — types.ThinkingConfig()

> Nur für Gemini 3.x Modelle. Nicht mit `gemini-2.5-flash-image` verwenden!
> `thinking_level` und `thinking_budget` **nie gleichzeitig** setzen.

| Parameter (Python) | Values | Modelle |
|---------------------|--------|---------|
| `thinking_level` | `"minimal"`, `"low"`, `"medium"`, `"high"` | gemini-3.1-flash-image: nur `"minimal"` (Default), `"high"` / gemini-3-pro-image: nur `"low"`, `"high"` / Gemini 3 Flash (Text): alle 4 |
| `thinking_budget` | `0`–`32768` (int) | Nur Gemini 2.5 Modelle |
| `include_thoughts` | `True` / `False` | Gemini 3.x (Tokens werden immer abgerechnet) |

### Imagen aspect ratios (more limited)
`"1:1"`, `"3:4"`, `"4:3"`, `"9:16"`, `"16:9"`

### Common aspect ratio uses

| Ratio | Use case |
|-------|----------|
| `1:1` | Social media posts, profile pics |
| `16:9` | YouTube thumbnails, desktop wallpapers |
| `9:16` | Instagram/TikTok stories, reels |
| `4:3` | Classic photos, presentations |
| `3:4` | Portrait photos |
| `21:9` | Ultra-wide cinematic |

---

## Python SDK (mit uv)

> **Wichtig:** Niemals `pip install` in die System-Python-Umgebung. Immer `uv` verwenden.
> **Wichtig:** Immer `--python 3.13` angeben, da das System-Python (3.9) zu alt ist und alte SDK-Versionen cached werden, die `image_size` und `thinking_level` nicht unterstützen. SDK >= 1.65.0 ist erforderlich.

### Einmalig ausführen (kein Projekt nötig)

```bash
uv run --python 3.13 --with "google-genai>=1.68.0" --with Pillow python script.py
```

### Als Projekt

```bash
uv init image-gen && cd image-gen
uv add "google-genai>=1.68.0" Pillow
uv run python script.py
```

### Text-to-Image (non-streaming)

```python
import os
from io import BytesIO
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def generate_image(
    prompt: str,
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: str = "16:9",
    image_size: str = "2K",
    output_path: str = "output.png",
) -> None:
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=image_size,
                person_generation="allow_adult",
            ),
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.text:
            print(f"Description: {part.text.strip()}")
        elif part.inline_data:
            img = Image.open(BytesIO(part.inline_data.data))
            img.save(output_path)
            print(f"Image saved: {output_path}")


generate_image(
    prompt="A photorealistic fox in a snowy forest at golden hour",
    output_path="/tmp/fox.png",
)
```

### Imagen 4

```python
def generate_imagen(
    prompt: str,
    model: str = "imagen-4.0-generate-001",
    num_images: int = 1,
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
    output_dir: str = "/tmp",
) -> list[str]:
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=num_images,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            person_generation="allow_adult",
            output_mime_type="image/jpeg",
        ),
    )

    paths = []
    for i, img in enumerate(response.generated_images):
        path = f"{output_dir}/imagen_{i}.jpg"
        img.image.save(path)
        paths.append(path)
        print(f"Saved: {path}")
    return paths
```

---

## Bildbearbeitung

### Edit existing image with prompt

```python
def edit_image(
    image_path: str,
    edit_prompt: str,
    model: str = "gemini-2.5-flash-image",
    output_path: str = "/tmp/edited.png",
) -> None:
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ext = Path(image_path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    response = client.models.generate_content(
        model=model,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            types.Part.from_text(edit_prompt),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="1:1"),
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.text:
            print(f"Response: {part.text}")
        elif part.inline_data:
            img = Image.open(BytesIO(part.inline_data.data))
            img.save(output_path)
            print(f"Edited image: {output_path}")
```

### Multi-turn editing (conversation)

```python
def multi_turn_edit(image_path: str) -> None:
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                types.Part.from_text("Add sunflowers to this vase"),
            ],
        )
    ]

    # Round 1
    r1 = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"]
        ),
    )
    contents.append(r1.candidates[0].content)

    # Round 2 — builds on previous result
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text("Replace sunflowers with tulips")],
        )
    )

    r2 = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"]
        ),
    )

    for part in r2.candidates[0].content.parts:
        if part.inline_data:
            img = Image.open(BytesIO(part.inline_data.data))
            img.save("/tmp/multi_turn_result.png")
```

---

## Bash/curl API

### Text-to-Image

```bash
#!/usr/bin/env bash
GEMINI_API_KEY="${GEMINI_API_KEY:?GEMINI_API_KEY not set}"
MODEL="gemini-2.5-flash-image"
OUTPUT="/tmp/generated.png"

RESPONSE=$(curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "A fox in a snowy forest"}]}],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {
        "aspectRatio": "16:9",
        "imageSize": "2K",
        "personGeneration": "allow_adult"
      }
    }
  }')

# Extract and save image
echo "$RESPONSE" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
for part in data['candidates'][0]['content']['parts']:
    if 'text' in part:
        print(part['text'])
    elif 'inlineData' in part:
        with open('${OUTPUT}', 'wb') as f:
            f.write(base64.b64decode(part['inlineData']['data']))
        print('Saved: ${OUTPUT}')
"
```

### Edit image (curl)

```bash
#!/usr/bin/env bash
GEMINI_API_KEY="${GEMINI_API_KEY:?GEMINI_API_KEY not set}"
INPUT_IMAGE="$1"
EDIT_PROMPT="${2:-Add snow to this scene}"
OUTPUT="/tmp/edited.png"
MODEL="gemini-2.5-flash-image"

# Base64 encode (macOS)
IMAGE_B64=$(base64 -i "$INPUT_IMAGE")

# Determine MIME type
case "${INPUT_IMAGE##*.}" in
    jpg|jpeg) MIME="image/jpeg" ;;
    png)      MIME="image/png" ;;
    webp)     MIME="image/webp" ;;
    *)        MIME="image/jpeg" ;;
esac

cat > /tmp/edit_request.json << EOF
{
  "contents": [{"parts": [
    {"inline_data": {"mime_type": "${MIME}", "data": "${IMAGE_B64}"}},
    {"text": "${EDIT_PROMPT}"}
  ]}],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {"aspectRatio": "1:1", "imageSize": "1K"}
  }
}
EOF

RESPONSE=$(curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @/tmp/edit_request.json)

echo "$RESPONSE" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
for part in data['candidates'][0]['content']['parts']:
    if 'text' in part:
        print(part['text'])
    elif 'inlineData' in part:
        with open('${OUTPUT}', 'wb') as f:
            f.write(base64.b64decode(part['inlineData']['data']))
        print('Saved: ${OUTPUT}')
"
```

### Imagen 4 (predict endpoint)

```bash
#!/usr/bin/env bash
GEMINI_API_KEY="${GEMINI_API_KEY:?GEMINI_API_KEY not set}"
MODEL="imagen-4.0-generate-001"

RESPONSE=$(curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:predict" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [{"prompt": "Product photo of vintage leather briefcase"}],
    "parameters": {
      "sampleCount": 4,
      "aspectRatio": "4:3",
      "imageSize": "2K",
      "personGeneration": "allow_adult"
    }
  }')

echo "$RESPONSE" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
for i, pred in enumerate(data.get('predictions', [])):
    if 'bytesBase64Encoded' in pred:
        with open(f'/tmp/imagen_{i}.png', 'wb') as f:
            f.write(base64.b64decode(pred['bytesBase64Encoded']))
        print(f'Saved: /tmp/imagen_{i}.png')
    elif 'raiFilteredReason' in pred:
        print(f'Image {i} filtered: {pred[\"raiFilteredReason\"]}')
"
```

---

## Streaming

### Python

```python
def generate_streaming(prompt: str, output_path: str = "/tmp/streamed.png"):
    image_data = b""

    for chunk in client.models.generate_content_stream(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="16:9"),
        ),
    ):
        for part in chunk.candidates[0].content.parts:
            if part.text:
                print(part.text, end="", flush=True)
            elif part.inline_data:
                image_data += part.inline_data.data

    if image_data:
        img = Image.open(BytesIO(image_data))
        img.save(output_path)
        print(f"\nSaved: {output_path}")
```

### Bash (SSE)

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:streamGenerateContent?alt=sse" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "Cyberpunk city at night"}]}],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}
    }
  }' | python3 -c "
import sys, json, base64
chunks = []
for line in sys.stdin:
    line = line.strip()
    if line.startswith('data: ') and line[6:] != '[DONE]':
        try:
            chunk = json.loads(line[6:])
            for part in chunk.get('candidates', [{}])[0].get('content', {}).get('parts', []):
                if 'text' in part:
                    print(part['text'], end='', flush=True)
                elif 'inlineData' in part:
                    chunks.append(part['inlineData']['data'])
        except json.JSONDecodeError:
            pass
print()
if chunks:
    with open('/tmp/streamed.png', 'wb') as f:
        f.write(base64.b64decode(''.join(chunks)))
    print('Saved: /tmp/streamed.png')
"
```

---

## ThinkingConfig

Only for Gemini 3.x models (`gemini-3.1-flash-image-preview`, `gemini-3-pro-image-preview`).

| Parameter | Values | Description |
|-----------|--------|-------------|
| `thinkingLevel` | `"minimal"`, `"low"`, `"medium"`, `"high"` | Reasoning depth |
| `includeThoughts` | `true` / `false` | Show thinking in response |

> Thinking tokens are always billed regardless of `includeThoughts`.

```python
config=types.GenerateContentConfig(
    response_modalities=["TEXT", "IMAGE"],
    thinking_config=types.ThinkingConfig(
        thinking_level="high",
        include_thoughts=True,
    ),
)
```

```json
"generationConfig": {
  "responseModalities": ["TEXT", "IMAGE"],
  "thinkingConfig": {
    "thinkingLevel": "high",
    "includeThoughts": false
  }
}
```

---

## Google Search Tool

Enables grounding with current web information.

### Python

```python
config=types.GenerateContentConfig(
    response_modalities=["TEXT", "IMAGE"],
    tools=[types.Tool(google_search=types.GoogleSearch())],
)
```

### JSON (curl)

```json
"tools": [{"googleSearch": {}}]
```

Grounding metadata in response:
```python
metadata = response.candidates[0].grounding_metadata
if metadata:
    print("Queries:", metadata.web_search_queries)
    for chunk in metadata.grounding_chunks or []:
        print(f"Source: {chunk.web.title} - {chunk.web.uri}")
```

---

## Gemini 3.1 Flash Image Preview — Vollständige Beispiele

Das neueste Modell `gemini-3.1-flash-image-preview` unterstützt ThinkingConfig, Google Search Grounding und Streaming. Hier die vollständigen Beispiele:

### Bash/curl (streamGenerateContent)

```bash
#!/bin/bash
set -e -E

GEMINI_API_KEY="${GEMINI_API_KEY:?GEMINI_API_KEY not set}"
MODEL_ID="gemini-3.1-flash-image-preview"
GENERATE_CONTENT_API="streamGenerateContent"

cat << EOF > /tmp/request.json
{
    "contents": [
      {
        "role": "user",
        "parts": [
          {
            "text": "INSERT_INPUT_HERE"
          }
        ]
      }
    ],
    "generationConfig": {
      "responseModalities": ["IMAGE", "TEXT"],
      "thinkingConfig": {
        "thinkingLevel": "MINIMAL"
      },
      "imageConfig": {
        "aspectRatio": "",
        "imageSize": "1K",
        "personGeneration": ""
      }
    },
    "tools": [
      {
        "googleSearch": {
          "searchTypes": {
            "webSearch": {}
          }
        }
      }
    ]
}
EOF

curl \
  -X POST \
  -H "Content-Type: application/json" \
  "https://generativelanguage.googleapis.com/v1beta/models/${MODEL_ID}:${GENERATE_CONTENT_API}?key=${GEMINI_API_KEY}" \
  -d '@/tmp/request.json'
```

**imageConfig parameters for this model:**

| Parameter | Values | Notes |
|-----------|--------|-------|
| `aspectRatio` | `""` (auto), `"1:1"`, `"16:9"`, `"9:16"`, `"4:3"`, `"3:4"`, `"21:9"`, etc. | Empty string = auto |
| `imageSize` | `"512"`, `"1K"`, `"2K"`, `"4K"` | 512 is exclusive to this model |
| `personGeneration` | `""` (default), `"dont_allow"`, `"allow_adult"`, `"allow_all"` | Empty = default |
| `thinkingLevel` | `"MINIMAL"`, `"LOW"`, `"MEDIUM"`, `"HIGH"` | Controls reasoning depth |

### Python (mit uv, streaming)

```bash
uv run --with google-genai --with Pillow python gemini_image.py
```

```python
import mimetypes
import os
from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-3.1-flash-image-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
            search_types=types.SearchTypes(
                web_search=types.WebSearch(),
            ),
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="MINIMAL",
        ),
        image_config=types.ImageConfig(
            aspect_ratio="",
            image_size="1K",
            person_generation="",
        ),
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
        tools=tools,
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.parts is None:
            continue
        if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
            file_name = f"generated_image_{file_index}"
            file_index += 1
            inline_data = chunk.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            save_binary_file(f"{file_name}{file_extension}", data_buffer)
        else:
            print(chunk.text)


if __name__ == "__main__":
    generate()
```

### Image editing with gemini-3.1-flash (Python)

```python
def edit_with_flash31(image_path: str, prompt: str, output_prefix: str = "edited"):
    """Edit an existing image using gemini-3.1-flash-image-preview."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
        image_config=types.ImageConfig(image_size="2K"),
        response_modalities=["IMAGE", "TEXT"],
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model="gemini-3.1-flash-image-preview",
        contents=contents,
        config=config,
    ):
        if chunk.parts is None:
            continue
        if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
            inline_data = chunk.parts[0].inline_data
            ext = mimetypes.guess_extension(inline_data.mime_type)
            save_binary_file(f"{output_prefix}_{file_index}{ext}", inline_data.data)
            file_index += 1
        else:
            print(chunk.text)
```

---

## Preise & Kosten (Stand März 2026)

### gemini-3.1-flash-image-preview

| Typ | Standard | Batch/Flex |
|-----|----------|------------|
| Input (Text/Bild) | $0.50 / 1M Tokens | $0.25 / 1M |
| Output Text (inkl. Thinking) | $3.00 / 1M Tokens | $1.50 / 1M |
| **Output Bild** | **$60.00 / 1M Tokens** | $30.00 / 1M |

**Bild-Kosten nach Auflösung:**

| Auflösung | Tokens | Kosten/Bild |
|-----------|--------|-------------|
| 512px | 747 | ~$0.045 |
| 1K | 1.120 | ~$0.067 |
| 2K | 1.680 | ~$0.101 |
| 4K | 2.520 | ~$0.151 |

### gemini-3-pro-image-preview

| Typ | Standard | Batch/Flex |
|-----|----------|------------|
| Input (Text/Bild) | $2.00 / 1M Tokens | $1.00 / 1M |
| Output Text (inkl. Thinking) | $12.00 / 1M Tokens | $6.00 / 1M |
| **Output Bild** | **$120.00 / 1M Tokens** | $60.00 / 1M |

### Thinking-Kosten

- **Thinking-Tokens = Output-Text-Preis** (kein Aufschlag, kein Rabatt)
- **Immer berechnet**, auch bei `include_thoughts: false`
- `minimal`: ~0–100 Thinking-Tokens → vernachlässigbare Zusatzkosten
- `high`: ~5.000–20.000 Thinking-Tokens → ca. 30–45% Mehrkosten pro Bild

### Thinking-Level Einfluss auf Qualität

| Aspekt | `minimal` | `high` |
|--------|-----------|--------|
| Einfache Motive (1 Objekt) | ✅ Gut | ✅ Kaum besser |
| Komplexe Szenen (mehrere Objekte, Raumbeziehungen) | ⚠️ Okay | ✅ Deutlich besser |
| Text im Bild | ⚠️ Standard | ✅ Leicht besser |
| Prompt-Treue | ⚠️ Standard | ✅ Besser (interne Kompositions-Prüfung) |
| Latenz | 4–6 Sek. | 2–3x länger |

**Empfehlung:** `minimal` für einfache Motive, `high` nur bei komplexen Szenen mit mehreren Elementen oder Text im Bild.

---

## Best Practices

### Prompting
- Describe complete scenes, not just keywords
- Specify style explicitly: `"photorealistic"`, `"oil painting"`, `"vector illustration"`
- Use camera terminology for photo-realistic: `"shallow depth of field"`, `"golden hour"`
- Keep text-in-image under 25 characters

### Model selection
- Fast + cheap: `imagen-4.0-fast-generate-001`
- Best text rendering: `gemini-3-pro-image-preview`
- Standard production: `gemini-2.5-flash-image`
- Interactive editing: `gemini-2.5-flash-image` (supports multi-turn)

### Error handling
- Always check for both `inlineData` and `text` in response parts
- Handle `raiFilteredReason` in Imagen responses
- Implement exponential backoff for 429 errors

### Cost optimization
- Use `thinkingLevel: "minimal"` for high-volume workloads and simple prompts
- Use `thinkingLevel: "high"` only for complex scenes with spatial relationships or text-in-image
- Use streaming for better UX (perceived latency)
- Batch API for mass generation (no rate limit issues, 50% cost reduction)
