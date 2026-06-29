# 2026-06-29 — Plugins nach plugins/ bündeln

**What** — Alle Plugins (`context-aware`, `example`, `ocr`, `transcribe`) von
Repo-Top-Level in einen gemeinsamen `plugins/`-Ordner verschoben. Spiegelt den
gleichen Umbau in `ai-plugins-internal`. Top-Level = nur noch `plugins/` + Meta.

**How / decisions**
- Marketplace-`source` → `./plugins/<name>` (Unterordner-Pfad ist unterstützt,
  verifiziert). `enabledPlugins` unberührt (name@marketplace).
- Gates mitgezogen: `tests/structure/check.sh` + `tests/spec-touch-check.sh`
  erkennen Plugins unter `plugins/*/.claude-plugin/`; `plugins/` als erwarteter
  Top-Level-Ordner. Auto-Discovery-Aggregator (`run-all.sh`) brauchte keine
  Änderung. Test-Wrapper `tests/<plugin>/run.sh` → `../../plugins/<plugin>/...`.
- **Bug durch die zusätzliche Ebene gefangen:** `context-aware` und `example`
  haben eine plugin-interne `tests/validate.sh`, die den Marketplace-Root als
  `PLUGIN_DIR/..` berechnete — durch `plugins/<name>` zeigte das auf `plugins/`
  statt Repo-Root (`claude plugin validate` → „marketplace.json invalid"). Auf
  `PLUGIN_DIR/../..` korrigiert.
- repo-conventions §2/§3 + Doku-/Spec-Links nachgezogen (Skill-IDs/Meta-Pfade
  unberührt).

**Tests** — `tests/run-all.sh` PASS (structure + alle 4 Plugins), spec-touch grün.

**Koordination** — `example/` ist nach `plugins/example/` gewandert; das betrifft
Rezas offenen WIP-PR #35 (example-Referenz). Heads-up an Reza, damit er auf die
neue Lage rebasen kann.
