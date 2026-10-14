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
- Eval-Kostenmodell (`score_routing.py`): errand 2.0 → 0.2, mechanic 8.0 → 4.0,
  premium 20.0 → 8.0 (Opus 5.5; blended $/1M, 3:1 in:out). Ersparnis laut Scorer 80,9 %. Ground-Truth-Cases unverändert — nur ein Kommentar zur Tier-Version.
- Docs/README: Modellvergleich auf aktuelle Preise; der `errand`-Hinweis „kleinstes
  Fenster, 200K" entfällt — der ctx_*-Rat bleibt, weil Batches auch 1M füllen.

## Mitgezogen: die anderen Plugins

- `context-aware`: `context-scout` → `claude-sonnet-5-5` (0.1.1 → 0.1.2).
- `example`: `judge.py` → `claude-haiku-5-5` (0.2.0 → 0.2.1). Haiku 5.5 lehnt jedes
  `temperature` ≠ 1 mit 400 ab; die locked Cases setzen `temperature: 0.3`. Deshalb
  schickt das Harness Sampling nur noch an 4.x-Modelle — die Cases bleiben unberührt.
  Die Form des Judge-Urteils fixiert das erzwungene Tool-Schema, nicht temp 0;
  Querverweise (Repo-`CLAUDE.md`, READMEs) entsprechend korrigiert.
- `image-toolkit`: Eval-Produktionsstufe → `claude-sonnet-5-5` (0.2.1 → 0.2.2).
  Neu gefahren: Skill 41/41 zertifiziert, aber Baseline 0,83 und nur 7/41 trennscharf —
  Sonnet 5.5 weiß das meiste ohne Skill. Schwerere Cases nötig (#75).

## Learning

Ein stärkeres Modell kann eine Knowledge-Eval entwerten, ohne dass der Skill schlechter
wird: die Baseline steigt. Nach jedem Pin-Wechsel die Baseline-Schranke neu prüfen.

## Offen

- AC-1-3 / AC-1-6 e2e in frischer Session bestätigen (#76).
- `example`-Judge nicht live gefahren — braucht SDK-Key, lokal läuft alles über
  `claude -p` (#77). Judge-Budget auf 2048 angehoben, weil Thinking mitzählt.
