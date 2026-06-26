export const meta = {
  name: 'greet',
  description: 'Minimal demo workflow shipped inside a plugin: one agent returns a one-line greeting',
  phases: [{ title: 'Greet' }],
}

// args comes from the slash command: Workflow({ scriptPath, args })
const who = typeof args === 'string' && args.trim() ? args.trim() : 'world'

phase('Greet')
const line = await agent(
  `Return ONLY a short, friendly one-line greeting addressed to "${who}". No preamble, no quotes.`,
  { label: `greet:${who}`, model: 'haiku' }
)

log(`greeted ${who}`)
return { who, greeting: line }
