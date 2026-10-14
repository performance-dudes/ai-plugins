# 2026-10-14 — `mechanic`: Pins auf Sonnet 5.5 / Haiku 5.5

Beide Kosten-Tier-Subagenten auf die aktuelle Modellgeneration gehoben:
`mechanic` → `claude-sonnet-5-5`, `errand` → `claude-haiku-5-5`. Version 0.5.2 → 0.6.0.

## Motivation

Beide neuen Modelle sind gleichzeitig **billiger und stärker** als ihre Vorgänger —
kein Trade-off, den die Tier-Logik abwägen müsste:

| Tier | alt | neu | $/1M in/out | Kontext |
|---|---|---|---|---|
| `errand` | Haiku 4.5 | Haiku 5.5 | $1/$5 → $0.10/$0.50 | 200K → 1M |
| `mechanic` | Sonnet 4.6 | Sonnet 5.5 | $3/$15 → $2/$10 | 1M → 1M |

Die Premium-Tier (Opus 5.5, $4/$20) bleibt klar teurer; die Kaskade
errand < mechanic < premium hält, die Abstände werden größer.

## Geliefert

- Agent-Frontmatter (`model:`) und Descriptions beider Agents.
- Spec AC-1-2/1-3/1-5/1-6 und die Kosten-Begründung (§2); die alte Begründung
  „Sonnet 4.6 ist billiger als Sonnet 5" war ohnehin falsch (Sonnet 5 kostet $2/$10).
- `tests/mechanic/run.sh` prüft die neuen Pins.
- Eval-Kostenmodell (`score_routing.py`): errand 2.0 → 0.2, mechanic 8.0 → 4.0
  (blended $/1M). Ground-Truth-Cases unverändert — nur ein Kommentar zur Tier-Version.
- Docs/README: Modellvergleich auf aktuelle Preise; der `errand`-Hinweis „kleinstes
  Fenster, 200K" entfällt — der ctx_*-Rat bleibt, weil Batches auch 1M füllen.

## Offen

- AC-1-3 / AC-1-6 (e2e: gespawnter Agent meldet die neue Modell-ID) nach dem Update
  in frischer Session manuell bestätigen.
- Routing-Eval mit dem neuen Kostenmodell nicht neu gefahren — die Labels hängen nicht
  am Preis, nur die illustrative Ersparnis-Zahl.
