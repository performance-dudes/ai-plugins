# Testing the mechanic plugin

Two layers, same split the repo uses everywhere: **`tests/`** proves the plugin
*loads and wires*; **`evals/`** proves it *does the right thing*.

## `tests/` — does it load & wire? (fast, mostly no model)

```bash
bash mechanic/tests/validate.sh
```

Checks the manifest + marketplace validate, the two agent files exist with
`name` / `description` / `model` frontmatter, `plugin.json` parses, and — as a
bridge to the eval — that the routing scorer still PASSes on the committed sample.
This is what CI runs on every PR.

## `evals/` — is the routing sharp? (the real quality bar)

The plugin's whole value is the routing decision, so that is scored separately with
locked ground truth and a confusion matrix. See **[`../evals/README.md`](../evals/README.md)**.

```bash
uv run mechanic/evals/scripts/score_routing.py          # score the committed sample
```

> Use `tests/` for "does it load and run", `evals/` for "does it route correctly".
> A routing miss is a **plugin bug** — fix the agent description, never the case.
