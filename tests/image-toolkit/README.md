# tests/image-toolkit

Einteiliges Plugin → die Suite liegt **code-nah** unter
`plugins/image-toolkit/tests/validate.sh`. `run.sh` hier ist nur der Wrapper, damit
`tests/run-all.sh` sie per Auto-Discovery einsammelt.

## Ausführen

```bash
bash tests/image-toolkit/run.sh   # nur image-toolkit
bash tests/run-all.sh             # gesamtes Repo
```

## Abdeckung (config-valid-Tier)

| Prüfung | Was |
|---|---|
| Manifest | `plugin.json` valides JSON |
| Skripte | `generate_image.py` kompiliert, hat PEP-723-Header |
| Frontmatter | `commands/image.md`, `commands/image-doctor.md` (`description`), `SKILL.md` (`name`+`description`) |
| Version | via `tests/lib/check-version-sync.sh` im repo-weiten `structure`-Lauf |
| Modelle | keine abgeschalteten Gemini/Imagen-IDs außerhalb der Nachfolger-Tabelle; Default GA; SDK-Pin 2.x; Interactions API |

Rein statisch und offline — es wird **kein** Bild generiert und kein API-Key
gebraucht. Die Gemini-Aufrufe selbst sind damit nicht abgedeckt; was live geprüft
wurde, steht im jeweiligen Journal-Eintrag
(`journal/2026-09-23-image-toolkit-gemini-ga-interactions.md`).

Neue abgeschaltete IDs (Deprecations-Seite der Gemini API) in `DEAD` in
`plugins/image-toolkit/tests/validate.sh` §6 nachtragen.
