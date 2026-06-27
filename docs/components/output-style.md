# Output-Style — `Terse`

## Was ist es?
Ändert **wie** Claude antwortet (nicht *was*). Beispiel hier: „so knapp wie möglich,
kein Fülltext".

## Datei & Format
- **Datei:** `output-styles/<name>.md` (hier `output-styles/terse.md`)
- **Format:** `.md` mit Frontmatter (`name`, `description`) + Anweisungstext.
- Der Anweisungstext wird **an die System-Anweisung von Claude angehängt**, solange
  der Stil aktiv ist.

## Wann & wo aktiv
Bei Sitzungsstart entdeckt, aktiv erst nach `/output-style Terse`. Freiwillig.

## Wer löst es aus
**Du** — mit `/output-style`.

## Im example-Plugin
`output-styles/terse.md` ist ein knapper Antwort-Stil. Zum Ausprobieren:
`/output-style Terse`.
