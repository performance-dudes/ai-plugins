# Spec: Workflow component

**Theme:** The plugin bundles a small workflow script that returns a structured
one-line greeting.

## US-WORKFLOW-1 — A bundled greeting workflow

> As a **user**, I want the greet workflow to return a structured one-line
> greeting, so that both the command and the skill can reuse it.

| AC | Criterion | Test reference |
|----|-----------|----------------|
| AC-WORKFLOW-1-1 | The workflow script exists at `example/workflows/greet.js`. | `test.sh` (file presence) |
| AC-WORKFLOW-1-2 | It is syntactically valid JavaScript. | `test.sh` (`node --check`) |
| AC-WORKFLOW-1-3 | It defines `meta` and returns a `greeting`. | `test.sh` (grep) |
