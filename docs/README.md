# docs/ — So ist das `example`-Plugin aufgebaut

Hier steht der **Ist-Zustand**: wie das Plugin jetzt aussieht und wie man es
benutzt. (Was es können *soll*, steht in `specs/` — das ist die Wunschliste.)

## Was liegt hier?

- `getting-started.md` — der kürzeste Weg: Plugin nehmen und `/greet` ausführen.
- `file-formats.md` — warum `.json` / `.md` / `.sh` / `.yml` (Schlüssel zur Architektur).
- `architecture/example-plugin.md` — wie die Teile zusammenarbeiten (mit Bild).
- `components/` — **vollständige Referenz: eine Seite pro Baustein** (Manifest,
  Command, Skill, Subagent, Workflow, Theme, Output-Style, Hooks, MCP, LSP, Monitors).
- `development/components.md` — Kurz-Übersicht aller Bausteine in einer Tabelle.

Faustregel: Wird ein Text *falsch*, sobald sich etwas ändert → er gehört in
`specs/`. Bleibt er *wahr* → er gehört hierher in `docs/`.
