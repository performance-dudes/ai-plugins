# tests/

„Das Plugin ist das Produkt" → getestet wird das **ganze** Plugin (Configs,
Skripte, Skills, Workflows), nicht nur Code. Voll: SPEC-repo-conventions §5/§6.

## Testpyramide

| Tier | Was | Beispiele |
|---|---|---|
| **config-valid** (Basis) | JSON/JS valide, Frontmatter wohlgeformt, Refs auflösbar, `bash -n`/`node --check`, `python3 -m py_compile` | `tests/structure/check.sh`, jede Plugin-`validate.sh` |
| **unit** | Skript-Logik gegen Beispiel-Inputs, ohne Netz/Modelle/Engine | `ocr.py` Session-Grouping, `prepare_chunks.py` Chunker |
| **integration** | Komponenten-Zusammenspiel, Skill-Verhalten | (heute keine; bei Bedarf Issue) |
| **e2e** (Spitze) | echte Claude-Session übt das Plugin | (manuell / on demand) |

## Wo Tests liegen (nach Produktart)

Die ai-plugins-Plugins (`context-aware`, `example`, `ocr`, `transcribe`) sind
**einteilig** (deklarativ + Skripte, kein Build-Subprojekt). Ihre Suite liegt
**code-nah** im Plugin unter `<plugin>/tests/validate.sh`; der Top-Level-Wrapper
`tests/<plugin>/run.sh` ruft sie nur auf, damit `run-all.sh` sie per Auto-Discovery
einsammelt. So bleibt der Test beim Plugin (mit-wandern bei `git mv`), und der
Aggregator findet ihn trotzdem.

- **Einteilig** (hier alle): Suite `<plugin>/tests/validate.sh`, Wrapper
  `tests/<plugin>/run.sh`.
- **Zweiteilig** (Plugin mit Build, z. B. TS-MCP): Unit-Tests code-nah beim Build,
  Plugin-Ebene/Integration/E2E unter `tests/<plugin>/`. (Im internen Marketplace
  `ai-plugins-internal` für `agent-sync` so umgesetzt.)

## Nutzung

```bash
bash tests/run-all.sh           # alle Suiten, offline; Auto-Discovery hängt jede tests/<plugin>/run.sh ein
bash tests/structure/check.sh   # nur die Struktur-Konvention
bash tests/ocr/run.sh           # nur eine Plugin-Suite
```

## Offline-Verhalten

Optionale externe Werkzeuge werden **übersprungen**, nicht erzwungen: fehlt die
`claude`-CLI, entfällt `claude plugin validate` (Skip-Note); fehlt `node`, entfällt
der JS-`--check`. Die Suiten bleiben dadurch grün auf einem Runner ohne diese
Tools (`run-all` darf nie an einer fehlenden externen Abhängigkeit rot werden).
Was genau pro Plugin läuft vs. übersprungen wird, steht in
`tests/<plugin>/README.md`.

## Coverage

Traceability je Plugin in `tests/<plugin>/coverage.md` (spec:code · spec:test/Typ ·
code:tests/Typ). Lücken sind Merge-Gate-relevant — geschlossen oder als Issue.
