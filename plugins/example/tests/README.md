# Testing plugins and skills

There is no single "test runner" for plugins — you combine static validation,
headless invocation, and behavioural checks. This folder shows each layer.

## 1. Static validation (fast, no model)

Validate the manifest and component syntax before anything else:

```bash
claude plugin validate ./example          # plugin.json + components
claude plugin validate .                  # the marketplace.json
claude plugin details example             # component inventory + token cost
```

`tests/validate.sh` bundles this with file-presence, JSON-parse, `node --check`
on the workflow, and frontmatter checks:

```bash
bash example/tests/validate.sh
```

This is what CI should run on every PR (see `.github/workflows/` at the repo root).

## 2. Test a skill / command / workflow headlessly

Run Claude Code non-interactively and assert on the output. Point it at a
throwaway marketplace so you test the *installed* form, not loose files:

```bash
# add this repo as a local marketplace, enable the plugin, then invoke
claude plugin marketplace add /path/to/ai-plugins
claude plugin install example@ai-plugins

# drive the command headlessly and check the result
claude -p "/greet Felix" --output-format json | jq -r '.result'
```

For a **workflow** specifically, the most direct test is to run the script by
path and assert on its structured return — no install needed:

```bash
# (inside a Claude Code session or SDK harness)
Workflow({ scriptPath: "./example/workflows/greet.js", args: "Felix" })
# => { who: "Felix", greeting: "..." }
```

Give the workflow a `schema` in real tests so the return is validated for you.

## 3. Test a skill's *triggering* (does the model pick it?)

A skill is only useful if its `description` makes the model invoke it at the
right time. Test that behaviourally:

```bash
claude -p "say hi to the Performance Dudes" --output-format json \
  | jq -e '.result | test("Performance Dudes"; "i")'
```

If the model should NOT trigger it, assert the negative too. Keep these prompts
in a table and run them as a matrix.

## 4. Test a hook

Hooks are plain programs that read JSON on stdin. Test them in isolation —
no Claude Code needed:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' \
  | bash example/hooks/scripts/example-pretooluse.sh ; echo "exit=$?"
```

Assert on exit code (0 allow / 2 block) and any JSON it prints.

## Layering

| Layer | Speed | Catches |
|-------|-------|---------|
| `claude plugin validate` | instant | broken manifest/components |
| `validate.sh` | seconds | missing files, bad JSON/JS, frontmatter |
| `claude -p "/cmd"` | model call | command/workflow actually runs |
| trigger-matrix prompts | model calls | skill fires (and doesn't over-fire) |
| hook-in-isolation | instant | hook logic + exit codes |

Run layers 1–2 in CI on every PR; run 3–4 on a schedule or before release.
