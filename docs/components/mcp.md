# MCP-Server — externe Werkzeuge anbinden

## Was ist es?
**MCP** (Model Context Protocol) ist eine **Steckdose für externe Werkzeuge**: ein
eigener Server, der Claude neue Fähigkeiten gibt (z.B. eine Datenbank abfragen,
eine API ansprechen). Das Plugin kann so einen Server mitliefern und starten.

## Datei & Format
- **Datei:** `.mcp.json` (im example als `.mcp.json.example`)
- **Format:** `.json` → Konfig: welcher Befehl startet den Server, mit welchen
  Umgebungs-Variablen.

## Wann & wo ausgeführt
**Bei Sitzungsstart automatisch** — der Server-Prozess wird **sofort gestartet**.
Genau deshalb ist er im example als `.example` entschärft: Ohne echten Server würde
der Start ins Leere laufen.

## Wer löst es aus
**Automatisch** (das Programm), sobald das Plugin geladen ist.

## Im example-Plugin
`.mcp.json.example` zeigt die Form: ein Server `example-server`, gestartet per
`node ${CLAUDE_PLUGIN_ROOT}/mcp/dist/index.js`. Zum echten Betrieb müsste man erst
einen Server bauen und die Endung `.example` entfernen.
