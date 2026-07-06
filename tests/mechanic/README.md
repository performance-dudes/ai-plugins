# tests/mechanic

Einteiliges Plugin (nur Agent-Komponente) → alle automatisierten Tests liegen hier
(Top-Level), eingehängt via Auto-Discovery in `tests/run-all.sh`.

## Ausführen

```bash
bash tests/mechanic/run.sh        # nur mechanic
bash tests/run-all.sh             # gesamtes Repo (findet mechanic automatisch)
```

## Abdeckung (config-valid-Tier)

| AC | Prüfung |
|----|---------|
| AC-1-1 | `plugin.json` valides JSON, `name: "mechanic"` |
| AC-1-2 | `agents/mechanic.md` Frontmatter: `name: mechanic`, `model: claude-sonnet-4-6` |
| AC-1-5 | `agents/errand.md` Frontmatter: `name: errand`, `model: claude-haiku-4-5` |
| AC-2-1 | `marketplace.json` registriert `./plugins/mechanic` |

Rein statisch, offline, zero-dep (JSON-Parse via `python3`/`node` falls vorhanden,
sonst übersprungen; grep-Checks greifen unabhängig).

## AC-1-3 — manueller E2E (Modell-ID-Assertion)

Nicht automatisiert (kein E2E-Harness im Repo für Modell-ID-Assertions). Manuell in
einer **frischen** Session verifizieren, nachdem das Plugin installiert/aktualisiert
wurde (die Agent-Registry lädt erst bei Session-Start):

1. `mechanic@ai-plugins` im Workspace enablen, neue Session starten.
2. Agent spawnen mit `subagent_type: "mechanic"`, Prompt: „Gib nur deine exakte
   Modell-ID zurück." → erwartet `claude-sonnet-4-6` (AC-1-3).
3. Agent spawnen mit `subagent_type: "mechanic:errand"`, gleicher Prompt →
   erwartet `claude-haiku-4-5` (AC-1-6).
