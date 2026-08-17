# Product-Spec: `mechanic` — cost-tiered mechanical subagents

Spec-ID: `SPEC-mechanic` · Status: Entwurf · Datum: 2026-07-06 · Autor: Benny (mit Claude)

Gilt für das Plugin `plugins/mechanic` im öffentlichen Marketplace `ai-plugins`.
Methodik: `SPEC-repo-conventions` (Spec-Driven TDD, Struktur, Tests).

---

## 1. Thema

Ein Plugin, das **zwei** Kosten-Tier-Subagents ausliefert, je per Frontmatter fest auf
eine günstigere Modell-Version gepinnt, für **vollständig spezifizierte**, mechanische
Ausführungsarbeit:

- **`mechanic`** → `claude-sonnet-4-6`: mechanische Arbeit, die **Code-/Kontext-Verständnis**
  braucht (spezifizierte Edits, Cross-File-Refactors, passendes Boilerplate).
- **`errand`** → `claude-haiku-4-5`: **triviale, selbst-enthaltene** Transformationen
  **ohne** Codebase-Verständnis (klassifizieren, extrahieren, umformatieren, literales
  Suchen/Ersetzen).

Routing-Regel: Entscheidung nötig → `general-purpose` (Premium); Code-Verständnis nötig
→ `mechanic`; sonst → `errand`.

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
  dieses Pins — für **jede** Person, die das Plugin installiert, identisch.
- **Verhaltens-Leitplanke, nicht nur Modellwahl.** Der Wert entsteht erst durch eine
  **glasklare Description** (wann nutzen / wann NICHT) plus die Anweisung, bei
  Urteilsbedarf **zurückzugeben statt zu raten**. Ein falscher mechanischer Rateschuss
  ist teurer als ein sauberer Hand-back.
- **Die Regel muss im Context liegen, nicht nur im README.** Claude Code lädt von
  einem Agent ausschließlich das Frontmatter-Feld `description:` ins Modell. Die
  eigentliche Routing-Regel — die Kaskade, die `inline`-Route, die
  Asymmetrie („lieber eine Tier zu teuer") und die Parallelisierung — steht im
  README und wird **nie** geladen. Der Orchestrator sieht also zwei Werkzeuge, aber
  nicht die Regel, wann welches. OpenCode-Setups lösen das über `instructions: []`
  (eine immer geladene `AGENTS.md`); in Claude Code ist der **einzige** Plugin-Weg
  dorthin ein `SessionStart`-Hook mit `additionalContext`. Genau dafür — und nur
  dafür — bekommt das Plugin eine Hook-Komponente.

## 3. Nicht-Ziele

- Kein Command, keine Skills, kein MCP — nur die Agent-Komponente plus **genau einen**
  kontext-injizierenden `SessionStart`-Hook.
- **Kein Enforcement.** Der Hook stellt die Regel bereit, er erzwingt sie nicht: kein
  `PreToolUse`-Block, kein Umschreiben von Agent-Aufrufen, kein Veto. Die
  Routing-Entscheidung trifft weiterhin der Aufrufer — jetzt nur informiert statt
  blind.
- Keine automatische Routing-Logik im Orchestrator.

## 4. User Stories & Acceptance Criteria

### US-mech-1 — Agenten laden & pinnen ihre Modell-Version
| AC | Soll | Test |
|----|------|------|
| AC-1-1 | `plugins/mechanic/.claude-plugin/plugin.json` ist valides JSON mit `name: "mechanic"`. | config-valid (`run.sh`) |
| AC-1-2 | `plugins/mechanic/agents/mechanic.md` hat wohlgeformtes Frontmatter mit `name: mechanic` und `model: claude-sonnet-4-6`. | config-valid (`run.sh`) |
| AC-1-3 | In frischer Session meldet ein via `subagent_type: "mechanic"` gespawnter Agent die Modell-ID `claude-sonnet-4-6`. | e2e (manuell, dokumentiert) |
| AC-1-5 | `plugins/mechanic/agents/errand.md` hat wohlgeformtes Frontmatter mit `name: errand` und `model: claude-haiku-4-5`. | config-valid (`run.sh`) |
| AC-1-6 | In frischer Session meldet ein via `subagent_type: "mechanic:errand"` gespawnter Agent die Modell-ID `claude-haiku-4-5`. | e2e (manuell, dokumentiert) |

### US-mech-2 — Marketplace & Struktur
| AC | Soll | Test |
|----|------|------|
| AC-2-1 | `mechanic` ist in `.claude-plugin/marketplace.json` mit `source: "./plugins/mechanic"` registriert. | config-valid (`run.sh`) |
| AC-2-2 | Plugin-Ordner bleibt rein (kein specs/docs/journal/plans darin); Meta liegt Top-Level. | `tests/structure/check.sh` |
| AC-2-3 | Die `version` im Marketplace-Eintrag ist **identisch** mit der in `plugins/mechanic/.claude-plugin/plugin.json`. | config-valid (`run.sh`) |

**Warum AC-2-3 (Versions-Kopplung).** Die Version steht an zwei Orten. Driften sie,
zieht ein Nutzer beim `marketplace update` eine andere Version als die, gegen die hier
getestet wurde — die Suite grün, die Auslieferung falsch. Genau das passierte beim
Bump auf 0.5.0: `plugin.json` wurde gehoben, der Marketplace-Eintrag blieb auf 0.3.0
stehen, und die lokale Suite merkte nichts, weil AC-2-1 nur die **Registrierung**
prüfte, nicht die Version. Gefangen hat es erst die CI (`validate.yml`).

Der Check gehört auf beide Ebenen, damit der Fehler vor dem Push auffällt. Die
Implementierung liegt deshalb **nicht** hier, sondern zentral in
`tests/lib/check-version-sync.sh`: diese Suite ruft sie für `mechanic` auf,
`tests/structure/check.sh` für **alle** Plugins (SPEC-repo-conventions US-conv-4),
und `validate.yml` fährt dieselbe Datei. Eine Implementierung, drei Aufrufer — eine
Zweitfassung würde genau das Auseinanderlaufen wiederholen, das den Fehler erst
möglich gemacht hat.

### US-mech-3 — Description trennt mechanisch von Urteil
| AC | Soll | Test |
|----|------|------|
| AC-3-1 | Die Agent-Description nennt explizit **wann nutzen** (mechanisch/spezifiziert) und **wann NICHT** (Urteil/Design/Debug/Review). | review |
| AC-3-2 | Der Agent-Body weist an, bei Urteilsbedarf zurückzugeben statt zu raten. | review |
| AC-3-3 | Beide Agent-Bodies weisen an, Bulk-Retrieval über `ctx_*` zu routen, **wenn** die Tools vorhanden sind — sonst `Read`/`Grep`. | config-valid (`run.sh`) |

**Warum AC-3-3 im Agent-Body und nicht in der Routing-Karte.** `context-mode` bringt
einen eigenen `SessionStart`-Hook mit, der seinen Context injiziert — aber
`SessionStart` feuert **pro Session, nicht pro Subagent**. Was der Orchestrator über
`ctx_*` weiß, erreicht den Subagenten also nicht. Die Anweisung muss dorthin, wo der
Subagent sie liest: in sein Agent-File. Die Routing-Karte bleibt frei davon — sie
zeigt auf die Agenten, die Agenten kennen ihre Tools selbst (und die Karte hat ein
Zeichenbudget, AC-4-8).

Bedingt formuliert, weil `context-mode` project-scoped installiert sein kann: ohne
die Tools muss der Agent normal weiterarbeiten, nicht nach etwas greifen, das es
nicht gibt.

### US-mech-4 — Die Routing-Regel liegt im System-Context

Als Orchestrator will ich die Routing-Kaskade **im Context haben**, nicht nur zwei
Agent-Descriptions, damit ich `inline` vs. `errand` überhaupt unterscheiden kann und
weiß, wie ein Batch parallelisiert wird.

| AC | Soll | Test |
|----|------|------|
| AC-4-1 | `plugins/mechanic/hooks/hooks.json` ist valides JSON und registriert genau einen `SessionStart`-Hook, der `hooks/sessionstart-routing.sh` über `${CLAUDE_PLUGIN_ROOT}` aufruft. | config-valid (`run.sh`) |
| AC-4-2 | Der Hook gibt auf einem SessionStart-Payload **valides JSON** mit `hookSpecificOutput.hookEventName == "SessionStart"` und nicht-leerem `additionalContext` aus. | hook-behavior (`run.sh`) |
| AC-4-3 | Der `additionalContext` ist **byte-identisch** mit `hooks/routing-card.md` — die Karte ist die einzige Quelle, der Hook dupliziert sie nicht. | hook-behavior (`run.sh`) |
| AC-4-4 | Die Karte nennt alle **vier** Routen (`inline`, `mechanic:errand`, `mechanic`, `general-purpose`), die Asymmetrie-Regel („round up") und einen **Parallelisierungs-Abschnitt** mit der Disjunktheits-Bedingung für schreibende Fan-outs. | config-valid (`run.sh`) |
| AC-4-5 | Fehlt oder ist `routing-card.md` unlesbar, terminiert der Hook mit Exit 0 und leerer Ausgabe — eine Session darf daran nie scheitern. | hook-behavior (`run.sh`) |
| AC-4-6 | Der Hook ist zero-dep (reines `bash`, kein `jq`/`python`/`node`) und `bash -n`-sauber. | script-run (`run.sh`) |
| AC-4-7 | In frischer Session enthält der Context nach Start die Routing-Karte. | e2e (manuell, dokumentiert) |
| AC-4-8 | `routing-card.md` bleibt **unter 1400 Zeichen** (≈ 350 Tokens). | config-valid (`run.sh`) |

**Context-Budget ist ein Erstklass-Constraint (AC-4-8).** Die Karte wird in **jeden**
Session-Abschnitt injiziert, ihre Länge ist also eine Dauerlast auf dem Fenster jedes
Nutzers. Sie ist für ein LLM geschrieben, nicht für Menschen: nur **Delta-Information**
gegenüber dem, was ohnehin im Context steht. Die beiden Agent-Descriptions liefern
bereits „was ist trivial", „was ist mechanisch", „wann hand-back" — das gehört **nicht**
noch einmal in die Karte. Ihr Existenzgrund sind exakt die drei Dinge, die **nirgends**
sonst im Context stehen: die `inline`-Route, die Round-up-Asymmetrie und die
Parallelisierungs-Regeln. Prosa, Begründungen und Beispiele leben im README (nicht
geladen), nicht in der Karte. Wächst die Karte über das Budget, wird gekürzt — nicht
das Budget erhöht.

**Warum `SessionStart` und nicht `UserPromptSubmit`:** der Block wird **einmal je
Session-Abschnitt** berechnet statt in jedem Turn, und `SessionStart` feuert auch bei
`compact` — die Regel überlebt damit die Verdichtung, die sie sonst als Erstes
verlöre.

## 5. Tests

Einteiliges Plugin (Agent- + Hook-Komponente, kein Build-Subprojekt) → alle Tests
unter `tests/mechanic/`, eingehängt via Auto-Discovery in `tests/run-all.sh`.
Test-Typen: `config-valid` (Manifest/Frontmatter/Karte), `script-run` (`bash -n`),
`hook-behavior` (Hook real ausführen, Ausgabe gegen die Karte prüfen). AC-1-3, AC-1-6
und AC-4-7 (e2e) sind manuell in `tests/mechanic/README.md` beschrieben, da sie eine
echte frische Session erfordern.

## 6. Offen / im PR zu begründen

- AC-1-3 bleibt zunächst manuell (kein automatisierter E2E-Harness im Repo für
  Modell-ID-Assertions). Bei Bedarf später als echter E2E-Test nachziehen.
- AC-4-7 bleibt manuell (nur in einer echten Session beobachtbar), ist aber
  **vollständig verifiziert**: 2026-07-25, frische Session nach Installation von 0.5.0 —
  die Karte liegt wörtlich als `SessionStart hook additional context` im Modell-Context.
  Die Gegenprobe nach `/compact` ist ebenfalls bestanden: die Karte ist danach erneut
  vollständig da. Damit ist auch die tragende Begründung für `SessionStart` statt
  `UserPromptSubmit` — Überleben der Verdichtung — empirisch belegt, nicht nur
  konstruktiv.
- Die Routing-Evals (`evals/routing/`) messen die Kaskade bislang **ohne** die Karte
  im Context — der Router-Prompt injiziert nur die Agent-Descriptions. Ob die Karte
  die Trefferquote weiter hebt, ist damit noch nicht gemessen; die Suite steht mit
  pass³ = 1.0 aktuell am Deckeneffekt. Offener Punkt: härtere Near-Misses ergänzen
  (insbesondere Parallelisierungs-Fälle, für die es noch **gar keine** Cases gibt),
  bis die Suite wieder diskriminiert.
