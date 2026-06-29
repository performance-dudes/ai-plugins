# Coverage — context-aware

Drei Achsen (SPEC-repo-conventions §6). Handgepflegt. Typen: `config-valid` · `e2e`.

## spec : code
Keine eigene Spec im Repo (Plugin ist `context-aware`-Vorlage). Intent lebt im
`README.md` + Skill `skills/context-aware/`. → spec-frei dokumentiert (AC-1-3).

## spec : test (pro Typ)
| Aspekt | config-valid | e2e |
|---|---|---|
| Manifest/Marketplace gültig | `validate.sh` (claude validate, guarded) | — |
| lean plugin.json (kein gebündelter MCP) | `validate.sh` §2 | — |
| Komponenten vorhanden + JS parst | `validate.sh` §3/§4 | — |
| Agents verdrahten `ctx_*` | `validate.sh` §6 | echte context-mode-Session (manuell) |

## code : tests
| Komponente | config-valid |
|---|---|
| `.claude-plugin/plugin.json` | claude validate |
| `commands/*`, `agents/*`, `skills/context-aware/*` | Präsenz + Frontmatter |
| `workflows/context-aware-demo.js` | `node --check` |
| `scripts/doctor.sh` | Präsenz |

## Lücken (Merge-Gate — schließen oder Issue)
- Kein Laufzeit-/E2E-Test gegen echten `context-mode`-MCP (extern, bewusst offline
  ausgelassen). Bei Bedarf Issue.
