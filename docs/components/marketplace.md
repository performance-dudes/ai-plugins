# Marketplace — `marketplace.json`

## Was ist es?
Der **App-Store** des Repos: die Liste, aus der man Plugins installiert. Ein
Marketplace kann mehrere Plugins anbieten.

## Datei & Format
- **Datei:** `.claude-plugin/marketplace.json` (im Repo-Wurzel)
- **Format:** `.json` → Daten für ein Programm.

## Wann & von wo gelesen
Wenn du den Marketplace hinzufügst (`claude plugin marketplace add <repo>`), liest
Claude Code diese Datei, um zu wissen **welche Plugins es gibt und wo sie liegen**.

## Felder
- **Pflicht:** `name`, `owner` (`{name}`), `plugins` (Liste).
- **Pro Plugin-Eintrag:** `name` + `source` (wo es liegt, z.B. `"./example"`),
  optional `description`, `version`.

## Im example-Plugin
`.claude-plugin/marketplace.json` bietet ein Plugin an: `example`, Quelle
`./example`. Das `source: "./example"` heißt: „das Plugin liegt im Unterordner
`example/`".
