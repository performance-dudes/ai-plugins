# LSP-Server — Code-Intelligenz

## Was ist es?
**LSP** (Language Server Protocol) bringt **Code-Intelligenz** für eine
Programmiersprache: „Gehe zur Definition", Fehler-Markierungen, usw. Das Plugin
kann so einen Sprach-Server anbinden.

## Datei & Format
- **Datei:** `.lsp.json` (im example als `.lsp.json.example`)
- **Format:** `.json` → Konfig: welcher Befehl, welche Dateiendungen → welche
  Sprache.

## Wann & wo ausgeführt
**Bei Sitzungsstart automatisch** — der Sprach-Server wird gestartet. Das eigentliche
Server-Programm (z.B. `gopls` für Go) muss **separat installiert** sein. Deshalb
im example entschärft als `.example`.

## Wer löst es aus
**Automatisch**, sobald das Plugin geladen ist.

## Im example-Plugin
`.lsp.json.example` bindet beispielhaft `gopls` (Go) an und sagt: Dateien mit `.go`
→ Sprache „go".
