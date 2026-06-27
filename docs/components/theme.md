# Theme — Farbschema  *(experimentell)*

## Was ist es?
Ein **Farbschema** für die Oberfläche von Claude Code.

## Datei & Format
- **Datei:** `themes/<name>.json` (hier `themes/performance-dudes.json`)
- **Format:** `.json` → ein Programm liest **exakte Farbwerte** (deshalb kein `.md`).

## Wann & wo aktiv
Wird **bei Sitzungsstart** entdeckt, aber erst **aktiv, wenn du es einschaltest**:
`/theme`. Es ist also „opt-in" (freiwillig) — nichts ändert sich ungefragt.

## Wer löst es aus
**Du** — mit `/theme`.

## Status
**Experimentell.** Für ein öffentliches Plugin, das ein breites Publikum nutzt,
lieber vorsichtig einsetzen; intern unproblematisch.

## Im example-Plugin
`themes/performance-dudes.json` zeigt die Form eines Themes (Basis-Schema +
einzelne überschriebene Farben).
