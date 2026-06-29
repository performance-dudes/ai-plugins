# tests/context-aware/

Suite für das **context-aware**-Plugin. **Einteilig** (deklarativ + ein
Bash-Doctor, kein Build) → eine Suite, code-nah: `context-aware/tests/validate.sh`.
Der Wrapper [`run.sh`](run.sh) ruft sie nur, damit `tests/run-all.sh` sie per
Auto-Discovery einsammelt.

## Was läuft (offline, zero externe Modelle)
- **config-valid:** Manifest- und Marketplace-Validierung (`claude plugin validate`),
  „kein gebündelter MCP-Server" (`plugin.json` ist lean), alle Komponenten-Dateien
  vorhanden, Workflow-JS parst (`node --check`), Skill-/Agent-Frontmatter
  (name+description), Agents listen den `ctx_*`-Namespace.

## Was übersprungen wird & warum
- **`claude plugin validate`** wenn die `claude`-CLI fehlt — mit Skip-Note
  (durch `command -v claude` geschützt).
- **`node --check`** wenn `node` fehlt — Skip-Note.
- **context-mode (ctx_*) Laufzeit:** das Plugin setzt den Workspace-MCP
  `context-mode` voraus; die Suite prüft nur die **Verdrahtung** (Allowlist im
  Agent-Frontmatter), startet keinen MCP. E2E mit echtem context-mode ist
  bewusst nicht im Offline-Aggregat.

## Nutzung
```bash
bash tests/context-aware/run.sh        # nur dieses Plugin
bash context-aware/tests/validate.sh   # identisch (code-nah)
```
Coverage: [`coverage.md`](coverage.md).
