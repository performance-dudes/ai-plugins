# 2026-09-23 — `image-toolkit`: GA-Bildmodelle und Interactions API (0.2.0)

## Anlass

Der Default `gemini-2.5-flash-image` wird am **2. Oktober 2026** abgeschaltet. Alle anderen
Modelle, die Referenz und Skript nannten, waren schon weg:
`gemini-3.1-flash-image-preview` und `gemini-3-pro-image-preview` seit 25. Juni 2026,
alle `imagen-4.0-*` seit 17. August 2026. Quelle: die Deprecations-Seite der Gemini API,
gegengeprüft mit `client.models.list()` — Imagen taucht dort nicht mehr auf.

## Upgrade-Pfade

Nach Googles Nachfolger-Angaben. Für `gemini-2.5-flash-image` nennt die
Deprecations-Seite noch `gemini-3.1-flash-image-preview`, das selbst auf
`gemini-3.1-flash-image` verweist. Die Pricing-Seite nennt „3.1 Flash Image oder
3.1 Flash Lite Image". Default wird Flash; das kostet je 1K-Bild ca. 0,067 $ statt
0,039 $ (+70 %). Wer den alten Preispunkt will, nimmt Flash Lite (0,034 $).

| Alt | Neu |
|---|---|
| `gemini-2.5-flash-image` (Default) | `gemini-3.1-flash-image` (Nano Banana 2, Default) |
| `gemini-3.1-flash-image-preview` | `gemini-3.1-flash-image` |
| `gemini-3-pro-image-preview` | `gemini-3-pro-image` |
| `imagen-4.0-*` | `gemini-3.1-flash-image` |
| — | neu: `gemini-3.1-flash-lite-image` (Nano Banana 2 Lite, GA seit 30. Juni 2026) |

## API-Route

Google führt `generateContent` inzwischen als **Legacy** und dokumentiert Bildgenerierung über
die **Interactions API**. Entscheidung (Benny): gleich mitziehen statt nur IDs tauschen.
`generate_image.py` ruft jetzt `client.interactions.create` (SDK-Pin `google-genai>=2.25.0`).

Dazugekommen, weil die Route es hergibt: `--continue <id>` (Multi-Turn serverseitig über
`previous_interaction_id`), `--edit` mit bis zu 14 Bildern, `--thinking`, `--search`,
`--size 512|1K|2K|4K`. Das Skript prüft Größe/Thinking/Search gegen das Modell, bevor ein
bezahlter Aufruf rausgeht.

`--person-generation` ist entfallen: Das Feld gehörte zur `ImageConfig` von
`generateContent` und galt ohnehin nur im Enterprise-Modus.

## Fallstricke, die jetzt im Skript/der Referenz stehen

- **`genai.Client` in einer Variable halten.** Das 2.x-SDK schließt den HTTP-Transport beim
  Garbage Collect; `_client().interactions.create(...)` scheiterte mit
  `RuntimeError: Cannot send a request, as the client has been closed.` — ohne dass ein
  Request rausging.
- **Interactions liefert nur JPEG.** Pillow kodiert in das Format der `--out`-Endung um.
- **Default-Größe ist jetzt 1K** (API-Default), nicht mehr 2K — günstiger, und Flash Lite
  kann nur 1K.

## Nebenbefund: der Edit-Pfad war in 0.1.1 kaputt

`types.Part.from_text(prompt)` positional — im SDK ist `text` keyword-only. Jeder `--edit`-Lauf
warf `TypeError`. Mit dem Umbau erledigt (Edit baut jetzt Interactions-Blöcke).

## Cold-Review-Befunde (umgesetzt)

- Seitenverhältnisse je Modell geprüft: `1:4`/`4:1`/`1:8`/`8:1` nur Flash.
- `--aspect` ohne Default bei `--edit`/`--continue` — das Modell behält das
  Eingabe-Seitenverhältnis; neue Bilder weiter 16:9.
- Ausgabe-Endung und Zielordner werden **vor** dem bezahlten Aufruf geprüft.
- Abgeschaltete IDs brechen mit Nachfolger-Hinweis ab statt nur zu warnen.
- Eingabe-MIME über `mimetypes`, plus HEIC/HEIF.
- Thinking-Preis Flash korrigiert (3 $, nicht 1,50 $); Lite-Einschränkung bei
  Multi-Turn/mehreren Referenzen dokumentiert.

## Tests

`validate.sh` §6 neu: keine abgeschalteten IDs in `scripts/`, `commands/`, `README.md`; in der
Referenz nur in der Nachfolger-Tabelle; Default = `gemini-3.1-flash-image`; SDK-Pin 2.x;
Skript ruft `client.interactions.create` (nicht nur im Kommentar), kein `generateContent` mehr.
SKILL.md ist mit im Scan; die Nachfolger-Map im Skript ist per `# dead-id-ok` ausgenommen.
Gegenprobe gegen den Stand von `origin/main`: alle Prüfungen rot.

`validate.sh` §7 neu: Unit-Test der Guards mit reinem `python3` (kein uv, kein Key) —
elf Ablehnungen, vier Annahmen.

## Verifiziert

- `bash tests/run-all.sh` → PASS.
- Offline-Guards: Lite + `--size 2K`, Pro + `--thinking`, Lite + `--search` brechen jeweils
  vor dem API-Aufruf mit Klartext ab.
- **Ein** Live-Durchstich (Budget-Vorgabe 1 $): Default-Pfad, `gemini-3.1-flash-image`, 16:9 @ 1K
  → 1376×768 PNG in 12 s, ca. 0,07 $.

**Nicht** live verifiziert: `--edit`, `--continue`, `--search`, `--thinking high`, Flash Lite,
Pro. Die Aufrufformen folgen Googles Doku (Context7 + ai.google.dev) und den SDK-2.25-Typen.
