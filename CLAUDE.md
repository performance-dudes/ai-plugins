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

- 🧬 **Diversität schlägt eine grüne Zahl** — Cases variieren Sprache (de/en),
  Formulierung (explizit / implizit / slash / Paraphrase) und Near-Miss-Familie,
  damit die Eval Intent-Verständnis misst, nicht ein einzelnes Prompt-Template.
- 🎯 **Regime pro Suite wählen** — STRUCTURED Output (welcher Entrypoint feuert: ein
  Label) → **deterministisch matchen** (billig, reproduzierbar, keine
  Judge-Varianz); FREE-TEXT (Wording, Ton, Sprache) → **LLM-as-a-judge**
  (Two-Call, forced `tool_use`, Judge bei temp 0). Genau der Split, den Claude
  Codes plugin-eval-Tooling als `programmatic_first` + LLM-Judgment fährt.
- 🔒 **Locked before run · Clean/Precision-Case Pflicht · N Runs, mean±σ / pass@k** —
  Triggering ist stochastisch; ein einzelner Run ist eine Anekdote.
- 📄 **Cases in YAML** — sie sind human-authored & locked; der `note`/`description`
  IST der Kalibrier-Anker und lebt als Inline-Kommentar am Case. YAML ist die im
  Claude-Code-/promptfoo-Ökosystem übliche Case-/Config-Form; JSONL nur für
  Maschinen-Scale-Datasets. Ab gewisser Komplexität **ein Unterordner je Suite**
  (`evals/<suite>/`).

## Referenz + Tiefe

- **Vorlage zum Kopieren:** [`plugins/example/evals/`](plugins/example/evals/README.md) —
  lauffähige, selbst-enthaltene Mini-Harness (routing = deterministisch,
  greeting = LLM-Judge). `plugins/example/tests/validate.sh` §6 fährt den Scorer in CI.
- **Volle generische Harness:** `plugin-eval@ai-plugins-internal` —
  Confusion-Matrix-Scorer, Cohen's κ (Judge-Validierung), mean±σ-Aggregation.
- **Methodik-Spec:** repo-conventions §4 (Spec-Driven TDD) + §5–§6 (Tests/Coverage).

Ein neues/geändertes Plugin gilt erst als fertig, wenn **Spec + Tests + Evals +
Code + Docs + Context (CLAUDE.md/README)** in sync sind (repo-conventions §4).
