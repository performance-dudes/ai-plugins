# content-craft

Two generic, research-backed **user-space skills** for content and design craft. No PD IP —
everything here rests on public, evidence-based practice (WCAG, Core Web Vitals, AIDA/PAS,
processing-fluency). Register the marketplace once, enable the plugin per project.

## Skills

| Skill | What it does |
|---|---|
| `blog-article-writing` | Draft, structure, edit and review blog posts using research-backed techniques — AIDA/PAS frameworks, headline patterns, readability guide, editing checklist, practice drills. |
| `design-skills-2026` | Modern responsive mobile-first UI/UX — WCAG 2.1 AA, Core Web Vitals, color/typography, buttons, layout, motion, plus onboarding UI patterns (components, layout, motion). |

Each skill carries its own `SKILL.md` plus `references/` with paste-ready detail.

## Scope (MECE)

- **`blog-article-writing`** is external/reader-facing writing — disjoint from any internal
  knowledge/docs skills.
- **`design-skills-2026`** is the UI **execution** layer (components, layout, motion). The
  conversion-/PLG-**psychology** (aha-moment framework, paywall placement, persuasion,
  decision matrices) deliberately lives in the **conversion skill (sales plugin)**, not here —
  no duplication, no persuasion substance leaked into public.

## Install

```bash
claude plugin marketplace add performance-dudes/ai-plugins
```

Then enable per project in `<project>/.claude/settings.json`:

```json
{ "enabledPlugins": { "content-craft@ai-plugins": true } }
```

`/reload-plugins` to activate. The skills trigger automatically on relevant phrases (see each
`SKILL.md` frontmatter) or can be invoked directly.
