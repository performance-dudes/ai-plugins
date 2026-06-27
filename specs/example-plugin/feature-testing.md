# Spec: Feature „Testen erklärt"

**Thema:** Das Plugin zeigt, **wie** man Plugins und Skills testet — von der
schnellen statischen Prüfung bis zum echten Aufruf.

---

## US-TEST-1 — Nachvollziehbar testen können
> Als **Entwickler** will ich dokumentiert und ausführbar haben, wie ich das
> Plugin teste, damit ich Änderungen absichern kann.

| AC | Kriterium | Test-Referenz |
|----|-----------|---------------|
| AC-TEST-1-1 | `tests/README.md` beschreibt die Test-Schichten (statisch → headless → Verhalten → Hook). | informativ (Doku vorhanden) |
| AC-TEST-1-2 | `tests/validate.sh` läuft fehlerfrei (Exit-Code 0). | `bash example/tests/validate.sh` |
| AC-TEST-1-3 | CI prüft jede PR automatisch statisch. | `.github/workflows/validate.yml` |
