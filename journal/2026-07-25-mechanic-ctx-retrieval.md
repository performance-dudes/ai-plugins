# 2026-07-25 — `mechanic`/`errand`: Bulk-Retrieval über `ctx_*` (0.5.1)

Beide Agent-Bodies weisen jetzt an: sind `ctx_*`-Tools (context-mode) vorhanden, läuft
Bulk-Retrieval darüber — index once, slice many — statt rohe Bytes ins Fenster zu
ziehen. Fehlen sie, normal `Read`/`Grep`.

## Befund davor

Beide Agenten hatten **Zugriff** (kein `tools:`-Frontmatter → volle Session-Tools),
aber keine **Anweisung**. `context-mode` stand nur als Beispiel in einer Aufzählung
("Playwright, context-mode, Gmail, …"). Die vorhandene Formulierung drückte sogar eher
weg von MCP ("not a licence to widen scope"). Ein Agent nahm also `Read`/`Grep`.

## Warum im Agent-Body, nicht in der Routing-Karte

`context-mode` bringt einen eigenen `SessionStart`-Hook mit (`sessionstart.mjs`, plus
`PreToolUse`-Routing auf `Read|Grep|Bash|WebFetch|Agent`). Aber **`SessionStart` feuert
pro Session, nicht pro Subagent** — was der Orchestrator über `ctx_*` weiß, erreicht
den Subagenten nicht. Die Anweisung muss dorthin, wo der Subagent liest.

Die Karte bleibt bewusst frei davon: sie zeigt auf die Agenten, die Agenten kennen ihre
Tools selbst. Ein Test prüft das jetzt als Gegenprobe (Karte darf `ctx_` nicht
erwähnen) — sonst wächst sie gegen ihr Zeichenbudget (AC-4-8).

Bedingt formuliert, weil `context-mode` project-scoped installiert sein kann: hier
z. B. auf `/Users/nante/Developer/performance-dudes` gepinnt, in einer Session
darüber hinaus gar nicht exponiert. Ohne die Tools muss der Agent normal
weiterarbeiten.

`errand` gewinnt am meisten: größte Batches (900-Doc-Scans) auf dem kleinsten Fenster
(Haiku 4.5, 200K) — rohe Reads laufen mitten im Batch voll.

## Geliefert

- Beide Agent-Bodies, je 3 Sätze (token-concise, für ein LLM geschrieben).
- Spec: **AC-3-3** samt Begründung; Test in `tests/mechanic/run.sh` inkl. Gegenprobe
  auf die Karte.
- README-Abschnitt, plugin.json + marketplace.json 0.5.1.

## Verifiziert

- `tests/mechanic/run.sh` PASS, `run-all.sh` grün.
- Routing-Karte **unverändert** (1020 Byte, im Budget).

## Offen

Ob die Agenten der Anweisung real folgen, ist **nicht gemessen** — die Evals haben
keinen Retrieval-Case, und `ctx_*` ist in der Testumgebung nicht exponiert.
