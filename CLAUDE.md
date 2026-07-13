# ai-plugins — Repo-Kontext für Claude

Öffentliche Performance-Dudes-Claude-Code-Plugins. Die **verbindlichen**
Struktur-, Test- und Methodik-Regeln stehen in
[`specs/repo-conventions/0001_product_repo-conventions.md`](specs/repo-conventions/0001_product_repo-conventions.md) —
lies die zuerst. Diese Datei hält nur den Kontext, den ein Agent sofort im Kopf
haben muss.

## Das Plugin ist das Produkt — also wird das Plugin getestet, nicht der Code

Zwei Ebenen, nicht verwechseln:

- **`tests/`** — lädt/läuft das Plugin (Manifest, Komponenten, Syntax, Smoke). „Ist
  es korrekt verdrahtet?" Läuft in CI auf jedem PR. Regeln: repo-conventions §5–§6.
- **`evals/`** — misst die **Qualität** auf bekannten Inputs mit festgezurrter
  Ground-Truth. „Tut es das Richtige?" Das ist der **Measure-Schritt** der
  write→measure→optimize-Schleife.

## Eval-Logik (die eine Regel)

> **Die Eval testet das PLUGIN. Gefixt wird das Plugin (Skill-Description,
> Agent-Prompt, Workflow) — die Cases werden NIE angepasst.**

Ist ein Case einmal festgezurrt und bildet die Erwartungshaltung korrekt ab, ist er
**eingefroren**. Ein Fehlschlag ist ein **Plugin-Bug**, kein Anlass, den Case
aufzuweichen, umzuformulieren oder zu löschen, damit der Run grün wird — das wäre
Overfitting des Tests auf den Code und zerstört den einzigen Zweck der Eval.

Ergänzende Prinzipien:

- 🎯 **Immer das *object under test* testen — injecten, nicht duplizieren.** Die Eval
  fährt gegen das **reale** Objekt: die echten Prompts, Skill-`SKILL.md`s, Agent-Files,
  Workflows — zur Laufzeit **injiziert/gelesen**, nie gegen eine ins Harness kopierte
  Paraphrase. Eine Kopie driftet vom Original weg und misst dann sich selbst statt das
  Plugin. Der Router-/Judge-Harness liest also `agents/<name>.md` (bzw. die reale
  Skill/Workflow-Datei) direkt; ändert sich das Plugin, ändert sich automatisch, was
  getestet wird. Ein Test gegen eine dritte, gepflegte Kopie ist per Definition kein
  Test des Plugins.

- 🧬 **Diversität schlägt eine grüne Zahl** — Cases variieren Sprache (de/en),
  Formulierung (explizit / implizit / slash / Paraphrase) und Near-Miss-Familie,
  damit die Eval Intent-Verständnis misst, nicht ein einzelnes Prompt-Template.
- 🎯 **Regime pro Suite wählen** — STRUCTURED Output (welcher Entrypoint feuert: ein
  Label) → **deterministisch matchen** (billig, reproduzierbar, keine
  Judge-Varianz); FREE-TEXT (Wording, Ton, Sprache) → **LLM-as-a-judge**
  (Two-Call, forced `tool_use`, Judge bei temp 0). Genau der Split, den Claude
  Codes plugin-eval-Tooling als `programmatic_first` + LLM-Judgment fährt.
- 🔒 **Locked before run · Clean/Precision-Case Pflicht · N Trials, pass^k / mean±σ** —
  Triggering ist stochastisch; ein einzelner Trial ist eine Anekdote. Anthropic macht
  Non-Determinismus erstklassig: **pass@k** (≥1 Erfolg in k) fürs Explorative,
  **pass^k** (alle k bestehen) für kundenkritische Verlässlichkeit — Letzteres ist
  unsere Messlatte, wenn eine Suite grün heißen soll.
- 🧭 **Anthropics Vokabular sprechen** — eine Suite ist eine *evaluation suite* aus
  *tasks*; ein Lauf ist ein *trial*; Scorer/Judge sind *graders*; der eingefangene
  Output ist ein *transcript*; PASS/FAIL ist das *outcome*; die Skripte sind das
  *evaluation harness*, das reale Plugin das *agent harness/scaffold*. Zwei Regeln aus
  „Demystifying evals" direkt übernehmen: (a) **Tasks aus realen Failures** — mit 20–50
  einfachen, echten Fällen starten, nicht mit hübschen Synthetik-Cases; jeder bestätigte
  Miss wird ein neuer locked Case. (b) **Grade the output, not the tool-call path** —
  das beobachtbare Ergebnis prüfen (welcher Entrypoint/welche Tier/welche Antwort),
  nie eine erzwungene Multi-Step-Trajektorie (das overfittet).
- 🧪 **Task-Klarheit als Lock-Bar** — ein Case ist erst festzurr-reif, wenn **zwei
  Domänen-Expert:innen zum selben Pass/Fail-Urteil** kämen. Ist er das nicht, ist die
  Erwartung noch unscharf — schärfen, nicht einfrieren.
- 📄 **Cases in YAML** — sie sind human-authored & locked; der `note`/`description`
  IST der Kalibrier-Anker und lebt als Inline-Kommentar am Case. YAML ist die im
  Claude-Code-/promptfoo-Ökosystem übliche Case-/Config-Form; JSONL nur für
  Maschinen-Scale-Datasets. Ab gewisser Komplexität **ein Unterordner je Suite**
  (`evals/<suite>/`).

## Referenz + Tiefe

- **Vorlage zum Kopieren:** [`plugins/example/evals/`](plugins/example/evals/README.md) —
  lauffähige, selbst-enthaltene Mini-Harness (routing = deterministisch,
  greeting = LLM-Judge). `plugins/example/tests/validate.sh` §6 fährt den Scorer in CI.
- **Angewandtes Beispiel (Routing):** [`plugins/mechanic/evals/`](plugins/mechanic/evals/README.md) —
  misst die Kern-Promise des mechanic-Plugins (routet ein Task in die richtige Tier:
  inline · errand · mechanic · general-purpose). Zeigt den asymmetrischen Fall:
  **Under-Routing-Rate** als eigene Metrik neben F1 und ein Kostenmodell mit
  Retry-Strafe (zu-billig-geroutet scheitert → Retry auf premium). Grundsatz: lieber
  eine Tier zu teuer als eine zu billig.
- **Volle generische Harness:** `plugin-eval@ai-plugins-internal` —
  Confusion-Matrix-Scorer, Cohen's κ (Judge-Validierung), mean±σ-Aggregation.
- **Methodik-Spec:** repo-conventions §4 (Spec-Driven TDD) + §5–§6 (Tests/Coverage).
- **Kanonische Grounding (First-Hand):** Anthropic, „Demystifying evals for AI agents"
  (9. Jan 2026, das Vokabular + der Grader-Hierarchie-Rat oben) und der Docs-Guide
  „Define success criteria and build evaluations" (`develop-tests`, code-based →
  LLM-based → human) plus der Anthropic-Course `prompt_evaluations`. Wichtig zu wissen:
  **ein natives Plugin-Eval-Framework gibt es NICHT** (auch nicht als Preview) — offiziell
  nur `plugin validate` (Hygiene) + headless `claude -p` + eigene Assertions; das einzige
  First-Party-Eval-Tool ist `skill-creator` (nur Skills, assertion-basiert). Unsere
  Harness füllt genau diese Lücke, methodisch deckungsgleich mit der Doktrin. Verwandte
  Community-Tools: `cc-plugin-eval` (Triggering), `skill-eval-action` (YAML-Skill-Cases).

Ein neues/geändertes Plugin gilt erst als fertig, wenn **Spec + Tests + Evals +
Code + Docs + Context (CLAUDE.md/README)** in sync sind (repo-conventions §4).
