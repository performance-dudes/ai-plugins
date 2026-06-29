# tests/example/

Suite für das **example**-Plugin (Vorlage). **Einteilig** → code-nah
`example/tests/validate.sh`; Wrapper [`run.sh`](run.sh) für die Auto-Discovery.

## Was läuft (offline)
- **config-valid:** Manifest+Marketplace (`claude plugin validate`), alle
  Komponenten-Dateien (`greet`-Command, Workflow, Skill, Agent, Theme,
  Output-Style) vorhanden, Theme-JSON parst (`python3 -m json.tool`),
  Workflow-JS parst (`node --check`), Skill-/Agent-Frontmatter.

## Was übersprungen wird & warum
- **`claude plugin validate`** wenn `claude` fehlt — Skip-Note (neu mit
  `command -v claude` abgesichert, damit `run-all` auf einem Runner ohne CLI grün
  bleibt; vorher hätte das Plugin offline rot gemeldet).

## Nutzung
```bash
bash tests/example/run.sh           # nur dieses Plugin
bash example/tests/validate.sh      # identisch (code-nah)
```
Coverage: [`coverage.md`](coverage.md).
