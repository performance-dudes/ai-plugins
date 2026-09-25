# 2026-09-25 — mechanic-Agents unter dem Loader-Limit, repo-weit geprüft

## Was

Die Copilot CLI hat `mechanic` verweigert: die Agent-descriptions von `errand`
(1655 Zeichen) und `mechanic` (1591) lagen über 1024. Claude Code lädt sie
trotzdem — der Fehler war nur in Copilot sichtbar.

- Beide descriptions gekürzt (896 und 986 Zeichen). Jede Routing-Grenze bleibt:
  Batch vs. Einzelfall (inline), Code-Verständnis (mechanic), Entscheidung
  (general-purpose), dazu die Beispiele je Tier.
- `mechanic` 0.5.1 → 0.5.2, damit `plugin update` die Änderung ausliefert.
- Neuer Guard `tests/lib/check_descriptions.py` (plus `skill_desc_len.py`, derselbe
  Extractor wie in `ai-plugins-internal`), gerufen aus `tests/structure/check.sh`:
  jede description ≤ 1024 Zeichen, keine ungequotete Frontmatter-description mit
  `": "`, Negativ-Selbsttest vor dem Scan.
- Spec: US-conv-5 in `specs/repo-conventions/0001_product_repo-conventions.md`.

## Messung

Die descriptions sind das Testobjekt der Routing-Eval, die Cases blieben
unverändert. Drei blinde Trials über `build_router_prompt.py` (isoliert per
`claude -p --setting-sources ""`, Opus 5.5 als Orchestrator): alle drei
20/20, macro-F1 1.000, Under-Routing 0.000 — **pass^3 = 1.0**, wie vor der
Kürzung.

## Learnings

- Der Guard prüft auch `agents/*.md` und `plugin.json`. Ein reiner SKILL.md-Check
  (wie bisher in `ai-plugins-internal`) hätte keinen der Überläufe gefunden.
- Ein Clip-Scalar (`description: >`) trägt für striktes YAML einen Zeilenumbruch
  am Ende, sobald ein weiterer Key folgt. `skill_desc_len.py` zählt ihn jetzt
  konservativ mit; die erste Kürzung von `mechanic` (1023 ohne, 1024 mit) wäre
  sonst durchgerutscht.
