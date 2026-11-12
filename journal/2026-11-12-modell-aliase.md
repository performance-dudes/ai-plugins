# 2026-11-12 — Modell-Aliase statt Modell-IDs

## Anlass

Agent-Frontmatter und Eval-Skripte trugen volle Modell-IDs (`claude-sonnet-5-5`,
`claude-haiku-5-5`). Jede ID veraltet mit dem nächsten Modell-Release, und auf
Gateways mit eigenen IDs (Foundry-Modus auf einer Kunden-VM) bricht sie. Dort löst
Claude Code die Aliase über `ANTHROPIC_DEFAULT_<FAMILIE>_MODEL` auf.

## Entscheidungen

- **Frontmatter trägt den Alias** (`sonnet`, `haiku`): `mechanic` 0.7.0,
  `context-aware` 0.1.3. Spec AC-1-2/1-3/1-5/1-6 und `tests/mechanic/run.sh`
  prüfen jetzt den Alias statt der ID.
- **`claude -p`-Skripte** (`image-toolkit/evals/run.sh`, 0.2.4) übergeben den Alias direkt.
- **SDK-Skripte** (`example/evals/scripts/judge.py`, 0.2.2): Die Messages-API kennt keine
  Aliase. `resolve_model()` nimmt zuerst `ANTHROPIC_DEFAULT_<ALIAS>_MODEL`, sonst das
  neueste Modell der Familie aus der Models-API. Eine volle ID wird durchgereicht.
- **Feste Version nur per Umgebungsvariable**, nie im Plugin.

## Nicht geändert

Messprotokolle (`image-toolkit/evals/README.md`, Abschnitt Ergebnisse) nennen
weiter das Modell, mit dem gemessen wurde.
