# skills/

Skills are model-invoked capabilities: each lives in `skills/<name>/SKILL.md`
with `name` + `description` frontmatter. The model reads the `description` to
decide when to apply the skill autonomously.

- **run-greet** — calls the bundled `workflows/greet.js` via the Workflow tool,
  demonstrating skill → workflow composition.
