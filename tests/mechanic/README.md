# tests/mechanic

Einteiliges Plugin (Agent- + Hook-Komponente, kein Build-Subprojekt) → alle
automatisierten Tests liegen hier (Top-Level), eingehängt via Auto-Discovery in
`tests/run-all.sh`.

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
| AC-2-3 | `marketplace.json`-Version == `plugin.json`-Version (Drift = falsche Auslieferung) |
| AC-4-1 | `hooks/hooks.json` valide, `SessionStart` registriert, Pfad über `${CLAUDE_PLUGIN_ROOT}` |
| AC-4-4 | Karte nennt alle vier Routen, Round-up-Regel, Parallelisierung, Disjunktheit |
| AC-4-8 | `routing-card.md` < 1400 Zeichen (Context-Budget) |

Rein statisch, offline, zero-dep (JSON-Parse via `python3`/`node` falls vorhanden,
sonst übersprungen; grep-Checks greifen unabhängig).

## Abdeckung (script-run + hook-behavior-Tier)

| AC | Prüfung |
|----|---------|
| AC-4-6 | Hook ist `bash -n`-sauber **und** zero-dep (kein `jq`/`python`/`node` im Ausführungspfad) |
| AC-4-2 | Hook real ausgeführt → valides JSON, `hookEventName == "SessionStart"`, `additionalContext` nicht leer |
| AC-4-3 | `additionalContext` **byte-identisch** mit `hooks/routing-card.md` — Drift-Schutz |
| AC-4-5 | Fehlende Karte → Exit 0, leere Ausgabe (Session bleibt intakt) |

AC-4-3 ist der wichtigste der vier: er erzwingt, dass der Hook die Karte **injiziert**
statt sie zu duplizieren. Ohne ihn könnte der Hook-Text von der Karte wegdriften und
die Eval-Doktrin („immer das reale Objekt testen") wäre unterlaufen.

AC-4-5 läuft gegen ein temporäres Plugin-Root **ohne** Karte — ein Hook darf eine
Session unter keinen Umständen brechen.

## AC-1-3 — manueller E2E (Modell-ID-Assertion)

Nicht automatisiert (kein E2E-Harness im Repo für Modell-ID-Assertions). Manuell in
einer **frischen** Session verifizieren, nachdem das Plugin installiert/aktualisiert
wurde (die Agent-Registry lädt erst bei Session-Start):

1. `mechanic@ai-plugins` im Workspace enablen, neue Session starten.
2. Agent spawnen mit `subagent_type: "mechanic"`, Prompt: „Gib nur deine exakte
   Modell-ID zurück." → erwartet `claude-sonnet-4-6` (AC-1-3).
3. Agent spawnen mit `subagent_type: "mechanic:errand"`, gleicher Prompt →
   erwartet `claude-haiku-4-5` (AC-1-6).

## AC-4-7 — manueller E2E (Hook-Injektion im echten Context)

Ob ein injizierter `additionalContext` wirklich im Modell-Context landet, ist nur in
einer echten Session beobachtbar (der automatisierte Test prüft die Hook-**Ausgabe**,
nicht die Aufnahme durch den Host).

1. Plugin installieren/aktualisieren, **frische** Session starten.
2. Fragen: „Welche Routing-Regeln für mechanic/errand liegen dir gerade im Context?"
   → erwartet: die vier Routen inkl. `INLINE`, die Round-up-Regel und die
   Parallelisierungs-Regeln aus `hooks/routing-card.md` (AC-4-7).
3. Gegenprobe auf Überleben der Verdichtung: `/compact`, dann dieselbe Frage — der
   Hook feuert auch auf `source: "compact"`, die Karte muss also wieder da sein.
