# 🤖 Gemini Image API — Referenz (Interactions API)

## Inhaltsverzeichnis

1. [Modelle](#modelle)
2. [Abgeschaltete Modelle — nicht mehr verwenden](#abgeschaltete-modelle--nicht-mehr-verwenden)
3. [API-Route: Interactions statt generateContent](#api-route-interactions-statt-generatecontent)
4. [Konfiguration](#konfiguration)
5. [Python SDK (mit uv)](#python-sdk-mit-uv)
6. [Bildbearbeitung & Multi-Turn](#bildbearbeitung--multi-turn)
7. [Grounding mit Google Search](#grounding-mit-google-search)
8. [curl](#curl)
9. [Preise](#preise)
10. [Best Practices](#best-practices)

---

## Modelle

Alle drei sind **GA** (keine Preview). Der Plugin-Default ist `gemini-3.1-flash-image`.

| Modell-ID | Name | Stärke | Auflösung | Thinking | Search |
|---|---|---|---|---|---|
| `gemini-3.1-flash-lite-image` | Nano Banana 2 Lite | billigste, niedrigste Latenz, Masse | **nur 1K** | `minimal`/`high` | ❌ |
| `gemini-3.1-flash-image` | Nano Banana 2 | **Allrounder (Default)**, Pro-Features bei Flash-Tempo | 512, 1K, 2K, 4K | `minimal`/`high` | Web + Bild |
| `gemini-3-pro-image` | Nano Banana Pro | Profi-Assets, komplexe Layouts, bester Text im Bild | 1K, 2K, 4K | immer an, nicht steuerbar | Web |

### Modellwahl

| Aufgabe | Modell |
|---|---|
| Standard (Illustration, Foto, Edit) | `gemini-3.1-flash-image` |
| Viele Bilder, Entwürfe, Thumbnails | `gemini-3.1-flash-lite-image` |
| Infografik, Menü, Diagramm, viel Text im Bild | `gemini-3-pro-image` |
| Bild braucht aktuelle Fakten (Wetter, Kurse, Ereignisse) | `gemini-3.1-flash-image` + `--search web_search` |
| Stil/Motiv an Web-Bildern ausrichten | `gemini-3.1-flash-image` + `--search image_search` |
| 4K-Druckvorlage | `gemini-3.1-flash-image` oder `gemini-3-pro-image` mit `--size 4K` |

### Referenzbilder (Edit/Komposition)

- Bis zu **14** Eingabebilder je Aufruf.
- `gemini-3-pro-image`: 5 Bilder in hoher Treue, 14 insgesamt.
- `gemini-3.1-flash-image`: Ähnlichkeit für bis zu 4 Figuren, Treue für bis zu 10 Objekte.
- `gemini-3.1-flash-lite-image` ist laut Google **nicht** für mehrere Referenzbilder oder
  Multi-Turn-Editing optimiert — dafür Flash oder Pro.
- Eingabeformate: PNG, JPEG, WebP, HEIC/HEIF (iPhone-Fotos).
- Jedes erzeugte Bild trägt ein **SynthID**-Wasserzeichen.

---

## Abgeschaltete Modelle — nicht mehr verwenden

| Alte ID | Abschaltung | Nachfolger |
|---|---|---|
| `gemini-2.5-flash-image` | 2. Oktober 2026 | `gemini-3.1-flash-image` |
| `gemini-3.1-flash-image-preview` | 25. Juni 2026 | `gemini-3.1-flash-image` |
| `gemini-3-pro-image-preview` | 25. Juni 2026 | `gemini-3-pro-image` |
| `imagen-4.0-generate-001` | 17. August 2026 | `gemini-3.1-flash-image` |
| `imagen-4.0-ultra-generate-001` | 17. August 2026 | `gemini-3.1-flash-image` |
| `imagen-4.0-fast-generate-001` | 17. August 2026 | `gemini-3.1-flash-image` |

Aktueller Stand: <https://ai.google.dev/gemini-api/docs/deprecations>. Taucht eine
dieser IDs in altem Code auf, auf den Nachfolger umstellen — der Imagen-`predict`-Endpoint
existiert für Bilder nicht mehr.

---

## API-Route: Interactions statt generateContent

Google führt Bildgenerierung über die **Interactions API** (`POST /v1beta/interactions`,
im SDK `client.interactions.create`). `generateContent` gilt als **Legacy** und wird
nicht mehr für neue Arbeit verwendet.

| | Interactions (verwenden) | generateContent (Legacy) |
|---|---|---|
| SDK-Aufruf | `client.interactions.create(model=…, input=…)` | `client.models.generate_content(…)` |
| Bild-Optionen | `response_format={"type": "image", …}` | `config.image_config` |
| Thinking | `generation_config={"thinking_level": …}` | `config.thinking_config` |
| Multi-Turn | serverseitig über `previous_interaction_id` | Verlauf selbst mitschicken |
| Ergebnisbild | `interaction.output_image.data` (Base64, **JPEG**) | `part.inline_data.data` (Bytes) |

⚠️ **Interactions liefert Bilder nur als `image/jpeg`.** Für PNG/WebP lokal umkodieren
(Pillow `Image.save("out.png")` oder `magick out.jpg out.png`). Transparenz erzeugt das
Modell nicht — dafür ImageMagick.

---

## Konfiguration

### `response_format` (Bildausgabe)

```python
response_format={
    "type": "image",          # Pflicht
    "aspect_ratio": "16:9",   # optional, Default 1:1 bzw. Seitenverhältnis des Eingabebilds
    "image_size": "2K",       # optional, Default 1K — "512" | "1K" | "2K" | "4K" (großes K)
}
```

**Aspect Ratios (alle Modelle):** `1:1` `2:3` `3:2` `3:4` `4:3` `4:5` `5:4` `9:16` `16:9` `21:9`
**Nur `gemini-3.1-flash-image`:** `1:4` `4:1` `1:8` `8:1`

Ohne `aspect_ratio` übernimmt ein Edit das Seitenverhältnis des Eingabebilds. Das Skript
setzt 16:9 deshalb nur bei neuen Bildern, nicht bei `--edit`/`--continue`.

| Ratio | Einsatz |
|---|---|
| `1:1` | Social-Post, Profilbild |
| `16:9` | YouTube-Thumbnail, Hero, Wallpaper |
| `9:16` | Story, Reel |
| `4:5` | Instagram-Feed hochkant |
| `4:3` / `3:4` | klassisches Foto, Folie |
| `21:9` | Kino-Breitbild, Banner |
| `4:1` / `8:1` | Web-Banner, Header |
| `1:4` / `1:8` | Skyscraper, Seitenleiste |

**Auflösung je Modell:** `512` nur Flash · Lite nur `1K` · Pro `1K`/`2K`/`4K`.
Beispiel 16:9 @ 1K = 1376×768 px.

### `generation_config.thinking_level`

- Flash und Flash Lite: `minimal` (Default) oder `high`.
- Pro: denkt immer, nicht abschaltbar — **kein** `thinking_level` setzen.
- Thinking-Tokens werden immer berechnet (Output-Text-Preis). Das Modell erzeugt bis zu
  zwei Zwischenbilder („thought images", nicht berechnet); das letzte ist das Endbild.

| Aspekt | `minimal` | `high` |
|---|---|---|
| Einfaches Motiv | ✅ | kaum besser |
| Komplexe Szene, Raumbeziehungen | ⚠️ okay | ✅ deutlich besser |
| Text im Bild | ⚠️ | ✅ besser |
| Latenz (Flash, 1K) | ~12 s | 2–3× länger |

`high` nur für komplexe Szenen oder Text im Bild; sonst `minimal`.

---

## Python SDK (mit uv)

Nie `pip install` ins System-Python. Immer `uv`, Python 3.13, SDK **≥ 2.25.0**
(`client.interactions` gibt es erst im 2.x-SDK).

```bash
# Gebündeltes Skript (empfohlen)
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py --prompt "…" --out /tmp/out.png

# Eigenes Skript ad hoc
uv run --python 3.13 --with "google-genai>=2.25.0" --with Pillow python script.py
```

### Text-to-Image

```python
import base64, os
from io import BytesIO
from google import genai
from PIL import Image

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])  # Referenz halten, s. u.
interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="A photorealistic fox in a snowy forest at golden hour",
    response_format={"type": "image", "aspect_ratio": "16:9", "image_size": "2K"},
    generation_config={"thinking_level": "minimal"},
)
if interaction.output_text:
    print(interaction.output_text)
Image.open(BytesIO(base64.b64decode(interaction.output_image.data))).save("fox.png")
print(interaction.id)  # für Folge-Edits
```

⚠️ **`genai.Client` in einer Variable halten.** Das 2.x-SDK schließt den HTTP-Transport,
sobald der Client vom Garbage Collector eingesammelt wird. `genai.Client().interactions.create(…)`
als Einzeiler scheitert deshalb mit `RuntimeError: Cannot send a request, as the client
has been closed.`

### Alle Ausgaben einer Runde durchgehen

`output_image` / `output_text` sind Komfort-Felder (jeweils der **letzte** Block). Für alle
Blöcke:

```python
for step in interaction.steps:
    if step.type == "model_output":
        for block in step.content:
            if block.type == "text":
                print(block.text)
            elif block.type == "image":
                data = base64.b64decode(block.data)
```

---

## Bildbearbeitung & Multi-Turn

### Bild + Anweisung (Edit, Stiltransfer, Inpainting)

```python
def image_block(path: str, mime: str = "image/png") -> dict:
    with open(path, "rb") as f:
        return {"type": "image", "mime_type": mime, "data": base64.b64encode(f.read()).decode()}

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input=[
        image_block("living_room.png"),
        {"type": "text", "text": "Change only the blue sofa to a brown leather chesterfield. "
                                 "Keep everything else unchanged."},
    ],
)
```

Mehrere Bilder kombinieren (Kleid aus Bild 1 an Person aus Bild 2): mehrere `image`-Blöcke
vor den Text-Block setzen, im Prompt per „first image"/„second image" referenzieren.

### Multi-Turn (von Google empfohlen für iteratives Editieren)

Der Verlauf liegt serverseitig; nur die ID der Vorrunde mitgeben:

```python
follow_up = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="Update this infographic to be in German. Do not change any other elements.",
    previous_interaction_id=interaction.id,
    response_format={"type": "image", "aspect_ratio": "16:9", "image_size": "2K"},
)
```

Gebündeltes Skript: `--continue <interaction-id>` (die ID gibt jeder Lauf aus).

---

## Grounding mit Google Search

```python
interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="Weather forecast infographic for Berlin for the next 5 days",
    tools=[{"type": "google_search", "search_types": ["web_search"]}],
    response_format={"type": "image", "aspect_ratio": "16:9"},
)
```

- `web_search`: Flash und Pro. `image_search` (Web-Bilder als visueller Kontext): **nur Flash**.
- Flash Lite unterstützt kein Grounding.
- Web-Suche liefert keine Bilder an das Modell; dafür ist `image_search` da.
- Flash + `image_search` nutzt keine realen Personenbilder aus der Suche.
- Kosten: 5.000 Suchanfragen/Monat frei (über alle Gemini-3.x-Modelle), danach 14 $ je 1.000.

---

## curl

```bash
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-flash-image",
    "input": "Your prompt here",
    "response_format": {"type": "image", "aspect_ratio": "16:9", "image_size": "2K"},
    "generation_config": {"thinking_level": "minimal"}
  }' > /tmp/resp.json
```

Das Bild steckt in `steps[].content[]` mit `type: "image"`:

```bash
jq -r '[.steps[] | select(.type=="model_output") | .content[] | select(.type=="image")][-1].data' \
  /tmp/resp.json | base64 -d > /tmp/out.jpg
```

Edit per curl: `input` als Array aus `{"type":"image","mime_type":"image/png","data":"<BASE64>"}`
und `{"type":"text","text":"…"}`. Base64 unter macOS: `base64 -i in.png`.

---

## Preise

Stand September 2026, Paid Tier, je Bild (Standard; **Batch = halber Preis**). Kein Free Tier
für Bildmodelle über die API.

| Modell | 512 | 1K | 2K | 4K |
|---|---|---|---|---|
| `gemini-3.1-flash-lite-image` | — | 0,034 $ | — | — |
| `gemini-3.1-flash-image` | 0,045 $ | 0,067 $ | 0,101 $ | 0,151 $ |
| `gemini-3-pro-image` | — | 0,134 $ | 0,134 $ | 0,24 $ |

Dazu Thinking-Tokens zum Text-Output-Preis (Flash 3 $, Lite 1,50 $, Pro 12 $ je 1 Mio. Tokens)
und Eingabebilder (vernachlässigbar). Aktuell: <https://ai.google.dev/gemini-api/docs/pricing>.

---

## Best Practices

### Prompting

- Ganze Szenen beschreiben, keine Stichwortlisten.
- Stil explizit: „photorealistic", „oil painting", „flat vector illustration".
- Fotorealismus mit Kamera-Vokabular: „shallow depth of field", „golden hour", „35mm".
- Text im Bild kurz halten; bei viel Text erst den Text festlegen, dann das Bild verlangen.
  Für Text-lastige Motive `gemini-3-pro-image`.
- Beste Sprachen für Prompts: u. a. EN, de-DE, fr-FR, es-MX, ja-JP, zh-CN.
- Die gewünschte Anzahl Bilder hält das Modell nicht zuverlässig ein — je Bild ein Aufruf.

### Kosten

- Default `1K`; `2K`/`4K` nur, wenn das Ziel es braucht.
- Entwürfe mit `gemini-3.1-flash-lite-image`, Endfassung mit Flash oder Pro.
- `thinking_level: "high"` nur bei komplexen Szenen.
- Massenläufe über die Batch API (halber Preis).
- Exakte Zielgröße danach mit ImageMagick schneiden statt teure Auflösung anzufordern.

### Fehler

- Kein Bild in der Antwort (`output_image` ist `None`): Prompt wurde gefiltert oder das Modell
  hat nur Text geliefert — `output_text` lesen, Prompt umformulieren.
- 429: exponentielles Backoff.
- 404 / „model not found": abgeschaltete ID, siehe Tabelle oben.
