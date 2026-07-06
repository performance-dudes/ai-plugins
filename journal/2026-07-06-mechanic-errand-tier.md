# 2026-07-06 — `mechanic`: Haiku-Tier `errand` + geschärfte `mechanic`-Description

Zweiter Kosten-Tier-Subagent `errand` (gepinnt auf `claude-haiku-4-5`) ins bestehende
`mechanic`-Plugin, plus geschärfte `mechanic`-Description. Version 0.1.0 → 0.2.0.

## Motivation

Haiku 4.5 (≈ $1/$5 pro 1M) ist nochmal 3× billiger als Sonnet 4.6. Triviale,
selbst-enthaltene Transformationen (klassifizieren, extrahieren, umformatieren,
literales Suchen/Ersetzen) brauchen kein Sonnet — sollen aufs Haiku-Tier.

## Kern-Entscheidung: die Trennachse

Das Overlap-Risiko zwischen den beiden billigen Tiers wird über **eine** Achse gelöst:
**braucht die Ausführung Code-/Kontext-Verständnis?**
- Ja → `mechanic` (Sonnet 4.6): spezifizierter Edit der passen muss, Cross-File-Refactor.
- Nein → `errand` (Haiku 4.5): isolierte Transformation, ~pattern-substitution.

Beide Descriptions verweisen explizit auf Up-/Down-Routing; Gesamtregel: Entscheidung
nötig → general-purpose; Code-Verständnis nötig → mechanic; sonst → errand.

## Geliefert

- `plugins/mechanic/agents/errand.md` — Haiku-Pin, Description trennt trivial/Code-Kontext.
- `plugins/mechanic/agents/mechanic.md` — Description geschärft (Code-Kontext-Achse +
  Verweis nach unten auf errand, nach oben auf general-purpose).
- plugin.json (0.2.0), README, docs, Spec (AC-1-5/1-6), Test (errand-Frontmatter),
  Marketplace-Description aktualisiert.

## Verifiziert

- `subagent_type: "mechanic:errand"` → Modell-ID `claude-haiku-4-5` (nach reload, s.u.).
