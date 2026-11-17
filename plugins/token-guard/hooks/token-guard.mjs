#!/usr/bin/env node
// token-guard hook entry point. One process per hook event; the dispatcher lives
// in lib/handler.mjs. Fail-open by design: any internal error exits 0 without a
// decision, so the plugin never blocks because of its own bug.

import { handle } from './lib/handler.mjs'

try {
  let raw = ''
  for await (const c of process.stdin) raw += c
  const out = handle(JSON.parse(raw))
  if (out) process.stdout.write(JSON.stringify(out))
} catch {
  // fail-open
}
process.exit(0)
