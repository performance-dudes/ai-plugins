# 2026-07-06 — `mechanic`: cost-tiered Sonnet-4.6 subagent

Neues öffentliches Plugin `mechanic` im Marketplace `ai-plugins`. Liefert einen
Subagent, der per Frontmatter auf `claude-sonnet-4-6` gepinnt ist, für rein
mechanische, vollständig spezifizierte Ausführungsarbeit.

## Motivation

Weekly-Usage-Druck (~80 %). Deterministische Arbeit (Bulk-Edits, Search-and-Replace,
Formatierung, Boilerplate, mechanische Refactors) braucht kein Premium-Modell —
soll aufs günstigere Sonnet 4.6. Der Agent-Tool-`model`-Parameter ist ein Enum
`{sonnet, opus, haiku, fable}` (`sonnet` = Sonnet 5), kann also keine Version pinnen.

## Erkenntnis (recherchiert)

- Sonnet 4.6 existiert (`claude-sonnet-4-6`, Release 17.02.2026, ≈ $3/$15/1M), das
  günstigere Vorgängermodell zu Sonnet 5.
- Frontmatter-`model:` akzeptiert eine **volle Modell-ID** (offiziell dokumentiert,
  gleiche Werte wie `--model`) → versions-genauer Pin nur so möglich.
- Registry lädt neue Agents **nicht** in-session → Verifikation von AC-1-3 braucht
  eine frische Session.

## Geliefert

- `plugins/mechanic/` — plugin.json + agents/mechanic.md (Description trennt
  mechanisch/Urteil, Body: bei Urteilsbedarf zurückgeben statt raten) + README.
- `specs/mechanic/0001_product_mechanic_cost-tiered-subagent.md`
- `docs/mechanic/mechanic.md`, `tests/mechanic/` (config-valid), Marketplace-Eintrag.

## Offen

- AC-1-3 (Modell-ID-Assertion) bleibt manuell — kein E2E-Harness im Repo.
