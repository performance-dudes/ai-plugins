# Coverage — example

Drei Achsen (SPEC-repo-conventions §6). Typen: `config-valid`.

## spec : code
Reines Vorlage-/Demo-Plugin, keine eigene Produkt-Spec → spec-frei dokumentiert
(AC-1-3). Es demonstriert die Komponententypen (Command/Workflow/Skill/Agent/
Theme/Output-Style).

## spec : test (pro Typ)
| Aspekt | config-valid |
|---|---|
| Manifest/Marketplace gültig | `validate.sh` §1 (guarded) |
| Komponenten vorhanden | `validate.sh` §2 |
| Theme-JSON gültig | `validate.sh` §3 |
| Workflow-JS parst | `validate.sh` §4 |
| Skill/Agent-Frontmatter | `validate.sh` §5 |

## code : tests
| Komponente | config-valid |
|---|---|
| `commands/greet.md`, `skills/run-greet/*`, `agents/greeter.md` | Präsenz + Frontmatter |
| `workflows/greet.js` | `node --check` |
| `themes/performance-dudes.json` | JSON-Parse |
| `output-styles/terse.md` | Präsenz |

## Lücken
- Keine — die Vorlage hat keinen ausführbaren Laufzeit-Pfad jenseits der Demo.
