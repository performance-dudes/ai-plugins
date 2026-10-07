# Coverage — plugin-guard

Traceability nach SPEC-repo-conventions §6. Spec:
[`specs/plugin-guard/0001_product_plugin-guard.md`](../../specs/plugin-guard/0001_product_plugin-guard.md).
Suite: [`validate.sh`](../../plugins/plugin-guard/tests/validate.sh) (§n) und
[`guard.test.ts`](../../plugins/plugin-guard/tests/guard.test.ts) (#n, Reihenfolge im File).

## spec : code

| AC | umsetzende Komponente |
|---|---|
| AC-pg-1-1 Gate bei Laden + Reload | `register.ts` → `on('plugin.register')`, `judge`, `summary` |
| AC-pg-1-2 saubere Module laden | `register.ts` (`next(e)`) |
| AC-pg-1-3 Fähigkeiten + Kombinationen | `register.ts` → `judgeUses`; `rules.json` `capabilityRules` |
| AC-pg-1-4 nur Tier `user` | `register.ts` (`e.tier !== 'user'`) |
| AC-pg-1-5 `blockAt` | `plugin.json` `userConfig`, `register.ts` → `judge` |
| AC-pg-1-6 fail-closed | `register.ts` `.catch(…)` |
| AC-pg-1-7 kein Versteck | `register.ts` → `listCode`; `scan.py` → `code_files`; `rules.json` `skipPaths`/`skipFiles` |
| AC-pg-2-1 Freigabe pinnt Hash | `register.ts` → `sha256`, `scanSource`, `command.run approve` |
| AC-pg-2-2 Update invalidiert | `register.ts` → `judge` (`seen`, `changed`) |
| AC-pg-2-3 Engine-Dateien neutral | `rules.json` `skipPaths`/`skipFiles` |
| AC-pg-2-4 nur Person darf freigeben | `register.ts` (`e.origin.kind`) |
| AC-pg-2-5 Status, Sitzungsbezug | `register.ts` → `report`, `current` |
| AC-pg-3-1 eine Regeldatei | `rules/rules.json` |
| AC-pg-3-2/3 Treffer/Near-Misses | `rules.json` `sourceRules`, `scan.py` → `scan_plugin` |
| AC-pg-3-4 SessionStart-Audit | `audit.sh`, `scan.py --hook` → `diff_state`, `render` |
| AC-pg-3-5 eigenes Plugin überspringen | `scan.py` → `discover` |
| AC-pg-3-6 `--fail-at` | `scan.py` → `main` |

## spec : test

| AC | Test | Typ |
|---|---|---|
| AC-pg-1-1 | #1 Ablehnung nennt `[critical]`, Regel, `hooks/register.ts:2`; E2E | hook-behavior · e2e |
| AC-pg-1-2 | #2 | hook-behavior |
| AC-pg-1-3 | #7 Token + fetch, #8 `NODE_OPTIONS`; E2E `evil-helper` | hook-behavior · e2e |
| AC-pg-1-4 | #9 | hook-behavior |
| AC-pg-1-5 | #10, #11 | hook-behavior |
| AC-pg-1-6 | #14 | hook-behavior |
| AC-pg-1-7 | #12 (Mod), §4 „no hiding place" (scan.py) | hook-behavior · script-run |
| AC-pg-2-1 | #3, #5 (Hash == SHA-256 des Codes) | hook-behavior |
| AC-pg-2-2 | #4 | hook-behavior |
| AC-pg-2-3 | #13; E2E zweiter Lauf ohne „geändert" | hook-behavior · e2e |
| AC-pg-2-4 | #6 | hook-behavior |
| AC-pg-2-5 | #5 Status-Text; E2E (veraltete Urteile) | hook-behavior · e2e |
| AC-pg-3-1 | §3 | config-valid |
| AC-pg-3-2 | §4 alle Regeln, fehlendes Fixture = rot | script-run |
| AC-pg-3-3 | §4 Near-Misses | script-run |
| AC-pg-3-4 | §5 zwei Läufe, ohne python3, kaputter stdin | script-run |
| AC-pg-3-5 | §5 | script-run |
| AC-pg-3-6 | §5 | script-run |

## code : tests

| Komponente | config-valid | script-run | hook-behavior | e2e |
|---|---|---|---|---|
| `hooks/hooks.json` | §2 | — | — | manuell |
| `hooks/register.ts` | §6 validate | — | #1–#14 | manuell |
| `hooks/scripts/audit.sh` | §2 | §5 | — | manuell |
| `hooks/scripts/scan.py` | §2 | §4, §5 | — | manuell |
| `rules/rules.json` | §2, §3 | §4 | #1, #12 (Mechanik mit Test-Regelsatz) | manuell |

## Lücken

- **Mod-Tests nutzen einen Test-Regelsatz**, nicht `rules.json`: die Test-Engine hat kein
  Dateisystem. Die echte `rules.json` ist über `scan.py` (§4) und den E2E-Lauf belegt.
- **Mod-Tests und `claude plugin validate` laufen nicht in CI** (keine `claude`-CLI dort).
- **Reihenfolge** (Gate sieht nur später ladende Module) ist dokumentiert und per E2E
  belegt, aber nicht automatisch getestet.
- **E2E** manuell (Rezept in `docs/plugin-guard.md`).
