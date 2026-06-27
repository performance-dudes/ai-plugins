# specs/example-plugin/

Produkt-Specs für das `example`-Plugin — das **Soll** (was es können muss),
nicht der Ist-Zustand (der steht in `docs/`).

**Eine Spec pro Feature:**

- `feature-greet.md` — Begrüßen per Befehl `/greet` und per Skill (gleicher Workflow).
- `feature-component-showcase.md` — von jedem Baustein-Typ eine kopierbare Vorlage.
- `feature-testing.md` — wie man Plugins/Skills testet.

Jede Spec hat: **Thema → User Story (US-…) → Acceptance Criteria (AC-… + Test).**

Faustregel: Würde es *falsch*, sobald eine Änderung gemergt ist → hierher (Spec).
Bleibt es *wahr* nach dem Merge → nach `docs/`.
