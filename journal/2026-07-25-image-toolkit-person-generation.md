# 2026-07-25 — `image-toolkit`: `person_generation` war hartkodiert (0.1.1)

`generate_image.py` setzte `person_generation="allow_adult"` fest in jede
`ImageConfig`. Das Feld wird nur im **Gemini Enterprise Agent Platform mode**
unterstützt; in der Developer API — dem Standardfall — quittiert die Bibliothek es
mit einem `ValueError`. Jede Generierung schlug damit fehl, unabhängig vom Prompt.

## Fix

Das Feld wird nur noch gesetzt, wenn es angefordert wurde:

```python
img_kwargs = {"aspect_ratio": aspect, "image_size": size}
if person:
    img_kwargs["person_generation"] = person
```

Dazu ein neues Flag `--person-generation` (Default `None`). Wer den Enterprise-Modus
fährt, gibt `--person-generation allow_adult` an; alle anderen bekommen einen Aufruf,
den die Developer API akzeptiert. Der Default ist damit der funktionierende Pfad —
vorher war der Default der kaputte.

Version 0.1.0 → 0.1.1 (an beiden Orten; der neue repo-weite Check hätte einen
einseitigen Bump sofort gefangen).

## Nebenbefund: die Suite lief nie lokal

`image-toolkit` hatte **keinen** `tests/image-toolkit/run.sh`-Wrapper. Die
code-nahe `plugins/image-toolkit/tests/validate.sh` wurde damit nur von
`validate.yml` gefahren (das über `plugins/*/tests/validate.sh` iteriert), aber nicht
von `run-all.sh`, das per Auto-Discovery `tests/<plugin>/run.sh` sucht.

Das ist derselbe Fehlermodus wie beim Versions-Drift: **CI prüft, lokal nicht.** Der
Wrapper ist nachgezogen.

Noch offen, hier nicht angefasst: **`content-craft` hat gar keine
`tests/validate.sh`** — weder in CI noch lokal abgedeckt.

## Verifiziert

- `generate_image.py` kompiliert; `--help` zeigt das neue Flag mit Erklärung.
- `plugins/image-toolkit/tests/validate.sh` → ALL CHECKS PASSED.
- `tests/run-all.sh` grün, jetzt **inklusive** image-toolkit (vorher übersprungen).
- Versionen konsistent (0.1.1 an beiden Orten).

**Nicht** verifiziert: der eigentliche API-Aufruf. Die Suite ist offline und
generiert kein Bild — dass die Developer API den Aufruf ohne `person_generation`
akzeptiert, ist aus dem Fehlerbild geschlossen, nicht hier gemessen.
