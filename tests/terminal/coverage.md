# Coverage — terminal

Traceability nach SPEC-repo-conventions §6, drei Achsen. Spec:
[`specs/terminal/0001_product_terminal_iterm-dynamic-profile.md`](../../specs/terminal/0001_product_terminal_iterm-dynamic-profile.md).

Suite: [`plugins/terminal/tests/validate.sh`](../../plugins/terminal/tests/validate.sh)
(hier eingehängt über [`run.sh`](run.sh)). Test-Typen in Gebrauch: `config-valid` ·
`script-run` · `skill-lint`.

## spec : code

| AC | umsetzende Komponente |
|---|---|
| AC-term-1-1 `Bound Hosts` absolut | `scripts/install-iterm-profile.sh` (Flag-Modus + Template-Pfad), `templates/performance-dudes.json` |
| AC-term-1-2 Badge-Escaping | `templates/performance-dudes.json`, `skills/…/SKILL.md` (Regel) |
| AC-term-1-3 Alpha-Split 0.5/1.0 | `install-iterm-profile.sh` → `srgb()`, Template |
| AC-term-1-4 stabile Guid | `install-iterm-profile.sh` (`<Name>-Dyn`), Template |
| AC-term-2-1 keine Home-Pfade im Template | `templates/*.json` (`{{HOME}}`) |
| AC-term-2-2 `{{HOME}}` überall aufgelöst | `install-iterm-profile.sh` → `subst()` |
| AC-term-2-3 Abbruch bei Rest-Token | `install-iterm-profile.sh` (`sys.exit` auf `{{`) |
| AC-term-3-1 Kandidatenliste | `install-iterm-profile.sh` → `first_existing()`, `_meta.assets` |
| AC-term-3-2 Feld weglassen + Warnung | `install-iterm-profile.sh` (`profile.pop` + `warn`) |
| AC-term-3-3 Begleitfelder mitentfernen | `install-iterm-profile.sh` → `also_remove` |
| AC-term-3-4 trotzdem installieren | `install-iterm-profile.sh` (kein Abbruch bei fehlendem Asset) |
| AC-term-4-1 idempotent | `install-iterm-profile.sh` (Schreiben nach `<Name>.json`) |
| AC-term-4-2 `--dry-run` schreibt nichts | `install-iterm-profile.sh` (`mkdir` erst bei echtem Lauf) |
| AC-term-4-3 valides Profil-JSON | `install-iterm-profile.sh` (`json.dumps`) |
| AC-term-5-1/2 Triggering | `skills/iterm-dynamic-profile/SKILL.md` (`description`) |
| AC-term-5-3 stumme Fehlerbilder benannt | `skills/…/SKILL.md` („Verifying"-Tabelle) |

## spec : test

| AC | Test | Typ |
|---|---|---|
| AC-term-1-1 | §8 `Bound Hosts` beginnt mit `/` | config-valid |
| AC-term-1-2 | §6 Badge endet auf `\(session.name)` | config-valid |
| AC-term-1-3 | §8 Alpha 0.5 vs. 1.0 **und** gleicher RGB-Wert | config-valid |
| AC-term-1-4 | §8 Guid vorhanden, ohne Leerzeichen | config-valid |
| AC-term-2-1 | §5 kein `/Users/`, `/home/` in Templates | config-valid |
| AC-term-2-2 | §8 kein `{{` im erzeugten Profil | script-run |
| AC-term-2-3 | §10 Template löst ohne `--dir` auf | script-run |
| AC-term-3-1 | §9 (HOME auf leeres Verzeichnis gebogen) | script-run |
| AC-term-3-2 | §9 Felder fehlen statt toter Pfade | script-run |
| AC-term-3-3 | §9 `Icon` mit `Custom Icon Path` entfernt | script-run |
| AC-term-3-4 | §9 Profil bleibt installierbar (Badge/Tab da) | script-run |
| AC-term-4-1 | §11 zweiter Lauf → weiterhin genau 1 Datei | script-run |
| AC-term-4-2 | §7 Dry-Run liefert JSON **und** schreibt nichts | script-run |
| AC-term-4-3 | §7/§8 `python3 -m json.tool`, `Profiles`-Array | config-valid |
| AC-term-5-1/2 | `evals/triggering/cases.yaml` (10 positive, 6 near-miss/clean) | eval |
| AC-term-5-3 | — **Lücke**, siehe unten | — |

## code : tests

| Komponente | abgedeckt durch |
|---|---|
| `install-iterm-profile.sh` | §3 (`bash -n`), §7–§12 (Verhalten in beiden Modi, beide Degradationspfade, Farbumrechnung) |
| `templates/performance-dudes.json` | §3, §5, §6, §7–§9 |
| `skills/…/SKILL.md` | §4 (Frontmatter), §14 (wird real in den Eval-Prompt injiziert) |
| `commands/iterm-profile.md` | §2 (Existenz) |
| `.claude-plugin/plugin.json` | §1, §3, §13 (Marketplace-Eintrag) |
| `evals/scripts/score_triggering.py` | §14 (Self-Test: perfekte Vorhersage → F1 1.0, invertierte → 0.0, fehlende werden gemeldet) |

## Bekannte Lücken

Beide sind benannt statt stillschweigend gelassen (§6: „geschlossen oder als Issue
getrackt").

1. **Kein E2E-Test für den automatischen Profilwechsel.** Dass `Bound Hosts` korrekt
   und absolut im Profil steht, ist statisch geprüft (§8). Ob iTerm2 daraufhin
   tatsächlich umschaltet, ließe sich nur in einer echten iTerm2-Sitzung mit
   Shell-Integration messen. Das ist die Spitze der Pyramide und hier bewusst offen —
   der Test bräuchte eine GUI-Sitzung, die CI nicht hat.
2. **AC-term-5-3 ist nicht automatisiert.** Dass der Skill die drei stummen
   Fehlerbilder benennt, prüft derzeit kein Test — ein Grep auf Prosa würde die
   Formulierung einfrieren statt die Aussage zu prüfen. Die Eval misst das
   Triggering, nicht den Inhalt der Antwort.

Beide gehören als Issue getrackt, bevor das Plugin über den Erst-Release hinaus
wächst.
