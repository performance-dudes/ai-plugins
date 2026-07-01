# 2026-07-01 — content-craft plugin

Packaging two user-global skills (previously `~/.claude/skills/`, markdown-only
knowledge) as one public `ai-plugins` plugin `content-craft`, following the house
style of `ocr`/`transcribe`/`image-toolkit`. Bundles the craft of producing
externally published content — text and UI.

## What was done

- Vendored two skills 1:1 into `skills/`:
  - `blog-article-writing` — SKILL.md + 5 references (writing-frameworks,
    headline-patterns, readability-guide, editing-checklist, practice-drills).
  - `design-skills-2026` — SKILL.md + references/onboarding-ui-patterns.md.
- `plugin.json`, `README.md`, marketplace entry added (6th plugin). JSON validated,
  existing entries untouched (purely additive).

## Decisions & learnings

- **Public, because generic.** Both skills are research-backed, standards-based
  (WCAG 2.1 AA, Core Web Vitals, AIDA/PAS, processing-fluency) — no PD IP. They
  belong in the public marketplace, not internal.
- **MECE against the internal stack.** Delta-checked against `brand:brand-uix`
  and `knowledge`: `blog-article-writing` is disjoint from `knowledge/docs`
  (external articles vs. internal documentation); `design-skills-2026` is the
  generic method layer (responsive, mobile-first, WCAG, motion) *below*
  `brand-uix`'s PD value layer (concrete tokens, voice, named components). Only
  the delta was migrated; overlaps are cross-linked, not duplicated.
- **PLG cleanup — no internal leak into public.** The design skill's
  "Onboarding & Conversion" reference kept only the generic UI execution
  (components, layout, motion, microcopy); the persuasion/PLG substance is *not*
  duplicated here but delegated by cross-link to the `conversion` skill (sales
  plugin, internal). Keeps sales psychology out of the public repo.
- **No private-home cross-links.** Verified the plugin references no skills from
  Benny's private `~/.claude/skills/` (benjamin-linnik, semantic-anchors) — those
  would be dead links for everyone else. semantic-anchors was used only as a
  build-time compaction tool, never linked in the output.

## Review

Independent cold review (PII + plan-conformance): no blockers, no PII, JSON valid,
bestand untouched, PLG cleanup correctly applied. Merge-ready.
