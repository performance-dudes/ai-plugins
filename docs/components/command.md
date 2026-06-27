# Slash-Command — `/greet`

## Was ist es?
Ein **Befehl zum Tippen**. Schreibst du `/greet`, liest Claude die zugehörige
`.md`-Datei und befolgt die Anweisung darin.

## Datei & Format
- **Datei:** `commands/<name>.md` (hier `commands/greet.md`)
- **Format:** `.md` → das **Modell** liest **Anweisungen** in normaler Sprache.
- Oben Frontmatter (`description`, `argument-hint`), darunter der Anweisungstext.

## Wann & von wo gelesen
Commands werden **bei Sitzungsstart** entdeckt (und bei `/reload-plugins` neu
geladen). Ausgeführt wird der Inhalt erst, **wenn du `/greet` tippst**.

## Wer löst es aus
**Du** — bewusst, durch Tippen.

## Im example-Plugin
`commands/greet.md` sagt Claude: „Starte den Workflow `greet.js` per Pfad und gib
ihm den getippten Namen (`$ARGUMENTS`) mit." `$ARGUMENTS` ist der Text hinter dem
Befehl — bei `/greet Felix` also `Felix`.
