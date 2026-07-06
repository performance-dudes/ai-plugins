# Product-Spec: `mechanic` — cost-tiered mechanical subagent

Spec-ID: `SPEC-mechanic` · Status: Entwurf · Datum: 2026-07-06 · Autor: Benny (mit Claude)

Gilt für das Plugin `plugins/mechanic` im öffentlichen Marketplace `ai-plugins`.
Methodik: `SPEC-repo-conventions` (Spec-Driven TDD, Struktur, Tests).

---

## 1. Thema

Ein Plugin, das **einen** Subagent (`mechanic`) ausliefert, der per Frontmatter fest
auf **Sonnet 4.6** (`claude-sonnet-4-6`) gepinnt ist und ausschließlich
**mechanische, vollständig spezifizierte** Ausführungsarbeit übernimmt.

## 2. Warum (Begründung)

- **Kosten-Tiering.** Sonnet 4.6 ist die günstigere Vorgänger-Generation (≈ $3/$15
  pro 1M vs. das teurere Sonnet 5). Deterministische Arbeit — Aufgaben mit **einem**
  korrekten Output — braucht kein Premium-Modell. Diese Arbeit auf 4.6 auszulagern
  ist ein reiner Budget-Gewinn **ohne** Qualitätsverlust, weil kein Urteilsvermögen
  im Spiel ist. Premium-Tier (Opus / Sonnet 5) bleibt für Denkarbeit frei.
- **Der Alias reicht nicht.** Der Agent-Tool-`model`-Parameter ist ein Enum
  `{sonnet, opus, haiku, fable}`; `sonnet` löst auf das aktuelle Default (Sonnet 5)
  auf. Ein versions-genauer Pin ist **nur** über das Frontmatter-Feld `model:` mit
  voller Modell-ID möglich (offiziell dokumentiert, akzeptiert dieselben Werte wie
  `--model`). Ein ausgeliefertes Plugin ist der reproduzierbare, teilbare Träger
  dieses Pins — für Benny **und** Tsveti identisch.
- **Verhaltens-Leitplanke, nicht nur Modellwahl.** Der Wert entsteht erst durch eine
  **glasklare Description** (wann nutzen / wann NICHT) plus die Anweisung, bei
  Urteilsbedarf **zurückzugeben statt zu raten**. Ein falscher mechanischer Rateschuss
  ist teurer als ein sauberer Hand-back.

## 3. Nicht-Ziele

- Kein Command, keine Skills, kein MCP, keine Hooks — nur die Agent-Komponente.
- Keine automatische Routing-Logik im Orchestrator; die Auswahl trifft der Aufrufer
  anhand der Description.

## 4. User Stories & Acceptance Criteria

### US-mech-1 — Agent lädt & pinnt 4.6
| AC | Soll | Test |
|----|------|------|
| AC-1-1 | `plugins/mechanic/.claude-plugin/plugin.json` ist valides JSON mit `name: "mechanic"`. | config-valid (`run.sh`) |
| AC-1-2 | `plugins/mechanic/agents/mechanic.md` hat wohlgeformtes Frontmatter mit `name: mechanic` und `model: claude-sonnet-4-6`. | config-valid (`run.sh`) |
| AC-1-3 | In frischer Session meldet ein via `subagent_type: "mechanic"` gespawnter Agent die Modell-ID `claude-sonnet-4-6`. | e2e (manuell, dokumentiert) |

### US-mech-2 — Marketplace & Struktur
| AC | Soll | Test |
|----|------|------|
| AC-2-1 | `mechanic` ist in `.claude-plugin/marketplace.json` mit `source: "./plugins/mechanic"` registriert. | config-valid (`run.sh`) |
| AC-2-2 | Plugin-Ordner bleibt rein (kein specs/docs/journal/plans darin); Meta liegt Top-Level. | `tests/structure/check.sh` |

### US-mech-3 — Description trennt mechanisch von Urteil
| AC | Soll | Test |
|----|------|------|
| AC-3-1 | Die Agent-Description nennt explizit **wann nutzen** (mechanisch/spezifiziert) und **wann NICHT** (Urteil/Design/Debug/Review). | review |
| AC-3-2 | Der Agent-Body weist an, bei Urteilsbedarf zurückzugeben statt zu raten. | review |

## 5. Tests

Einteiliges Plugin (nur Agent-Komponente) → alle Tests unter `tests/mechanic/`
(config-valid), eingehängt via Auto-Discovery in `tests/run-all.sh`. AC-1-3 (e2e)
ist manuell in `tests/mechanic/README.md` beschrieben, da es eine echte frische
Session erfordert.

## 6. Offen / im PR zu begründen

- AC-1-3 bleibt zunächst manuell (kein automatisierter E2E-Harness im Repo für
  Modell-ID-Assertions). Bei Bedarf später als echter E2E-Test nachziehen.
