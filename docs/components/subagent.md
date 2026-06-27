# Subagent — `greeter`

## Was ist es?
Ein **Spezial-Helfer** mit eigenen, eng begrenzten Rechten. Claude kann eine
Aufgabe an ihn abgeben (z.B. „begrüße diesen Namen") und bekommt nur das Ergebnis
zurück.

## Datei & Format
- **Datei:** `agents/<name>.md` (hier `agents/greeter.md`)
- **Format:** `.md` mit Frontmatter + Anweisungstext.
- **Frontmatter-Felder:** `name`, `description`, `model` (`inherit`/`haiku`/…),
  `tools` (erlaubte Werkzeuge — nur das Nötigste = „least privilege").

## Wann & von wo gelesen
**Bei Sitzungsstart** entdeckt. Aufgerufen wird er erst, wenn jemand ihn per
`subagent_type: "greeter"` startet.

## Wer löst es aus
**Claude** (oder ein Workflow), per Aufruf — nicht automatisch.

## Im example-Plugin
`agents/greeter.md` ist nur ein **Muster** („so sieht eine Agent-Datei aus"). Der
`/greet`-Ablauf benutzt ihn **nicht** — er ruft direkt ein kleines Modell. Nicht
verwirren lassen: das Muster zeigt nur die Form.

## Warum „least privilege"?
`tools: [Read]` gibt dem Helfer **nur** Lesen — kein Schreiben, kein Ausführen. Je
weniger Rechte, desto weniger kann schiefgehen. Das ist ein Sicherheitsprinzip.
