# workspace-context tests

This suite covers the public `workspace-context` plugin as a one-piece,
declarative plugin:

- manifest and marketplace validation when the Claude CLI is available;
- required component presence;
- JSON and Bash syntax;
- skill frontmatter and explicit-invocation safeguards;
- the session-start hook contract; and
- a source/private-identifier hygiene scan.

Run it from the marketplace root:

```bash
bash tests/workspace-context/run.sh
```

The suite is also auto-discovered by `bash tests/run-all.sh`.
