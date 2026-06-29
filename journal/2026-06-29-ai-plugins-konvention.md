# 2026-06-29 — ai-plugins auf die PD-Repo-Konvention angeglichen

## Was

Den im internen Marketplace `ai-plugins-internal` etablierten Konventions-Standard
(SPEC-repo-conventions) auf den **öffentlichen** Marketplace `ai-plugins` portiert:

- **Konventions-Spec + Meta-READMEs:** `specs/repo-conventions/0001_product_repo-conventions.md`
  (Spec-ID `SPEC-repo-conventions` beibehalten), plus `specs/README.md`,
  `docs/README.md`, `journal/README.md`, `plans/README.md`, `tests/README.md`
  (an ai-plugins-Beispiele angepasst, interne Verweise wie agent-sync/MCP entfernt).
- **Mechanik:** `tests/structure/check.sh` (verbatim — erzwingt AC-1-1/1-2/1-4 inkl.
  Spec-Naming-Token und Plugin-Reinheit), `tests/run-all.sh` (Auto-Discovery von
  `tests/<plugin>/run.sh`), `tests/spec-touch-check.sh`, CI
  `.github/workflows/conventions.yml`.
- **Plugin-Suiten verdrahtet:** je Plugin ein Wrapper `tests/<plugin>/run.sh`, der
  die **code-nahe** `<plugin>/tests/validate.sh` aufruft, plus
  `tests/<plugin>/README.md` (läuft/übersprungen + warum) und `coverage.md`.
- **Konventionsverstoß behoben:** `ocr/docs/SETUP.md` und `transcribe/docs/SETUP.md`
  lagen **im** Plugin → per `git mv` nach `docs/ocr/SETUP.md` bzw.
  `docs/transcribe/SETUP.md` (Top-Level). Verweise nachgezogen.
- **Specs umbenannt** auf das Schema `<NNNN>_<type>_<plugin>`:
  `specs/ocr/reference.md` → `0001_product_ocr.md`,
  `specs/transcribe/reference.md` → `0001_product_transcribe.md`. Verweise in
  `docs/` und `journal/` nachgezogen.

## Entscheidungen

- **Tests bleiben code-nah** (`<plugin>/tests/validate.sh`), der Top-Level-Wrapper
  ruft sie nur. So wandern Tests mit dem Plugin (`git mv`), und der Aggregator
  findet sie trotzdem per Auto-Discovery — kein zentraler Edit pro Plugin-PR.
- **`plugins/example/tests/validate.sh` offline-robust gemacht:** der `claude plugin
  validate`-Aufruf war ungeschützt (anders als bei den drei anderen Validatoren) →
  auf einem CI-Runner ohne `claude`-CLI wäre `run-all` rot geworden. Jetzt per
  `command -v claude` geschützt mit Skip-Note — konsistent zu context-aware/ocr/
  transcribe. Berührt damit bereits gemergte Plugin-Arbeit (bewusst, minimal).
- **SETUP-Verweise aus dem Plugin** (`${CLAUDE_PLUGIN_ROOT}/docs/SETUP.md` im
  transcribe-Doctor, `doctor.sh`) zeigen jetzt auf die GitHub-URL im Marketplace-
  Repo — das installierte Plugin liefert die Datei nicht mehr mit, also ist der
  Repo-Pfad der ehrliche Ort. Trade-off der Konvention (Doku außerhalb des Plugins).

## Verifikation

`bash tests/run-all.sh` grün: Struktur (AC-1-1/1-2/1-4 + Reinheit) + alle vier
Plugin-Suiten. In dieser Umgebung laufen alle Validatoren **voll** (claude-CLI,
node, python3, uv vorhanden). Die deterministischen Unit-Tests (ocr-Session-Grouping,
anwenden-Dry-Run, transcribe-Chunker) sind reine python3-Stdlib — kein OCR-Engine,
kein Audio, kein Netz, keine Modelle.

## Follow-ups

- E2E-Pfade (echtes OCR/PyMuPDF, echte Whisper/pyannote-Pipeline, context-mode-MCP)
  bleiben bewusst außerhalb des Offline-Aggregats — bei Bedarf als Issue.
- `context-aware` und `example` sind als **spec-frei** dokumentiert (AC-1-3 in den
  jeweiligen `coverage.md`); falls sie eine Produkt-Spec bekommen, unter
  `specs/<plugin>/<NNNN>_product_<plugin>.md` anlegen.
