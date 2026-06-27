# Manifest — `plugin.json`

## Was ist es?
Die **Visitenkarte** des Plugins: Name, Version, Beschreibung. Ohne sie (an
Standard-Pfaden) ist ein Ordner kein richtiges Plugin.

## Datei & Format
- **Datei:** `.claude-plugin/plugin.json`
- **Format:** `.json` → ein Programm (Claude Code) liest **Daten**.

## Wann & von wo gelesen
**Beim Laden des Plugins** (Sitzungsstart). Claude Code liest die Felder, um das
Plugin zu kennen und seine Bausteine zu finden.

## Felder
- **Pflicht:** `name` (kleinbuchstaben-mit-bindestrich).
- **Optional:** `description`, `version`, `author`, `homepage`, `repository`,
  `license`, `keywords`, `displayName`.
- **Tipp:** `version` weglassen → es wird der Git-Commit benutzt.

## Im example-Plugin
`example/.claude-plugin/plugin.json` — minimal: `name`, `description`, `version`,
`author`, `keywords`. Genau so sieht das kleinste sinnvolle Manifest aus.

## Profi-Kniff
`"$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json"` oben
hinzufügen → dein Editor zeigt Auto-Vervollständigung und meckert bei Fehlern, noch
während du tippst.
